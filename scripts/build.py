#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0
"""Build profile-driven resume PDFs from LaTeX source."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
OUTPUTS_DIR = REPOSITORY_ROOT / "outputs"
CACHE_DIR = REPOSITORY_ROOT / ".cache"
OUT_DIR = CACHE_DIR / "out"
AUX_DIR = CACHE_DIR / "aux"
LATEXMKRC = REPOSITORY_ROOT / ".latexmkrc"
PROFILES_DIR = REPOSITORY_ROOT / "profiles"
RESUME_TEX = REPOSITORY_ROOT / "resume.tex"

SUPPORTED_SECTIONS = {
    "header",
    "summary",
    "experience",
    "publications",
    "education",
    "skills",
}


class Color:
    BLUE = "\033[34m"
    GREEN = "\033[32m"
    RED = "\033[31m"
    YELLOW = "\033[33m"
    BOLD = "\033[1m"
    RESET = "\033[0m"


@dataclass(frozen=True)
class ProfileConfig:
    profile: str
    name: str
    section_order: tuple[str, ...]
    included_sections: tuple[str, ...]
    keyword_emphasis: tuple[str, ...]


def main() -> None:
    args = parse_args()

    try:
        ensure_paths()
        profiles = load_profiles()
        selected_profiles = select_profiles(profiles, args.profile)
        built_pdfs = [build_profile(profile) for profile in selected_profiles]

        if args.open and built_pdfs:
            open_pdf(built_pdfs[0])

    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        print_error(str(exc))
        sys.exit(1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build resume PDF variants.")
    parser.add_argument(
        "--profile",
        metavar="PROFILE",
        default=None,
        help="Profile variant to build. Builds all profiles when omitted.",
    )
    parser.add_argument(
        "--open",
        action="store_true",
        help="Open the first generated PDF after building.",
    )
    return parser.parse_args()


def ensure_paths() -> None:
    for path in (RESUME_TEX, LATEXMKRC, PROFILES_DIR):
        if not path.exists():
            raise FileNotFoundError(f"Required path not found: {path}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    AUX_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)


def load_profiles() -> dict[str, ProfileConfig]:
    profiles: dict[str, ProfileConfig] = {}

    for profile_path in sorted(PROFILES_DIR.glob("*.yaml")):
        profile = load_profile(profile_path)

        if profile.profile in profiles:
            raise ValueError(f"Duplicate profile found: {profile.profile}")

        profiles[profile.profile] = profile

    if not profiles:
        raise ValueError(f"No profiles found in {PROFILES_DIR}")

    return profiles


def load_profile(profile_path: Path) -> ProfileConfig:
    data = load_yaml(profile_path)

    profile = require_scalar(data, "profile", profile_path)
    name = first_scalar(data, ("name", "label"), profile_path)
    section_order = first_sequence(data, ("section_order", "sections"), profile_path)
    included_sections = first_sequence(data, ("included_sections", "sections"), profile_path)
    keyword_emphasis = first_sequence(data, ("keyword_emphasis", "emphasis"), profile_path)

    validate_sections(section_order, included_sections, profile_path)

    return ProfileConfig(
        profile=profile,
        name=name,
        section_order=tuple(section_order),
        included_sections=tuple(included_sections),
        keyword_emphasis=tuple(keyword_emphasis),
    )


def select_profiles(
    profiles: dict[str, ProfileConfig],
    requested_profile: str | None,
) -> list[ProfileConfig]:
    if requested_profile is None:
        return [profiles[name] for name in sorted(profiles)]

    if requested_profile not in profiles:
        available = ", ".join(sorted(profiles))
        raise ValueError(
            f"Unknown profile '{requested_profile}'. Available profiles: {available}"
        )

    return [profiles[requested_profile]]


def build_profile(profile: ProfileConfig) -> Path:
    generated_source = REPOSITORY_ROOT / f"resume-{profile.profile}.generated.tex"
    source_pdf = OUT_DIR / f"{generated_source.stem}.pdf"
    final_pdf = OUTPUTS_DIR / f"resume-{profile.profile}.pdf"
    log_file = AUX_DIR / f"{generated_source.stem}.log"

    generated_source.write_text(render_resume(profile), encoding="utf-8")

    cmd = [
        "latexmk",
        "-pdf",
        "-halt-on-error",
        "-interaction=nonstopmode",
        "-recorder",
        "-synctex=1",
        "-file-line-error",
        "-f",
        "-gg",
        "-cd",
        str(generated_source),
    ]

    print_build_header(profile, generated_source, final_pdf, log_file)

    try:
        try:
            result = subprocess.run(cmd, cwd=REPOSITORY_ROOT, check=False)
        except FileNotFoundError as exc:
            raise FileNotFoundError("latexmk is not installed or not available on PATH.") from exc

        if result.returncode != 0:
            print_log_tail(log_file)
            raise RuntimeError(
                f"LaTeX build failed for profile '{profile.profile}'.\n"
                f"Log file: {log_file}\n"
                f"Open log: open {log_file}\n"
                f"Tail log: tail --lines=100 {log_file}"
            )

        if not source_pdf.exists():
            print_log_tail(log_file)
            raise FileNotFoundError(f"Expected PDF not found: {source_pdf}")

        shutil.copy2(source_pdf, final_pdf)
        print_success(profile, final_pdf)
        return final_pdf

    finally:
        generated_source.unlink(missing_ok=True)


def render_resume(profile: ProfileConfig) -> str:
    source = RESUME_TEX.read_text(encoding="utf-8")
    document_start = "\\begin{document}"
    document_end = "\\end{document}"

    try:
        preamble, remainder = source.split(document_start, maxsplit=1)
        _, _ = remainder.split(document_end, maxsplit=1)
    except ValueError as exc:
        raise ValueError(f"Unable to locate document markers in {RESUME_TEX}") from exc

    included_sections = set(profile.included_sections)
    rendered_sections: list[str] = ["\\pagestyle{fancy}"]

    for section in profile.section_order:
        if section not in included_sections:
            continue

        rendered_sections.append(f"\\input{{sections/{section}}}")

        if section == "header":
            rendered_sections.append("\\vspace{0.5em}")

    body = "\n\n".join(rendered_sections)
    return f"{preamble}{document_start}\n\n{body}\n\n{document_end}\n"


def validate_sections(
    section_order: list[str],
    included_sections: list[str],
    profile_path: Path,
) -> None:
    unknown_sections = sorted(
        (set(section_order) | set(included_sections)) - SUPPORTED_SECTIONS
    )

    if unknown_sections:
        raise ValueError(
            f"Unsupported sections in {profile_path.name}: {', '.join(unknown_sections)}"
        )

    missing_order = [
        section for section in included_sections if section not in section_order
    ]

    if missing_order:
        raise ValueError(
            f"Included sections missing from section_order in {profile_path.name}: "
            f"{', '.join(missing_order)}"
        )


def load_yaml(profile_path: Path) -> dict[str, Any]:
    contents = profile_path.read_text(encoding="utf-8")

    try:
        import yaml
    except ImportError:
        data = load_simple_yaml(contents)
    else:
        data = yaml.safe_load(contents) or {}

    if not isinstance(data, dict):
        raise ValueError(f"Profile must be a YAML mapping: {profile_path.name}")

    return data


def first_scalar(data: dict[str, Any], keys: tuple[str, ...], profile_path: Path) -> str:
    for key in keys:
        value = data.get(key)

        if value is not None:
            return scalar(value).strip()

    raise ValueError(f"Missing required field {' or '.join(keys)} in {profile_path.name}")


def require_scalar(data: dict[str, Any], key: str, profile_path: Path) -> str:
    value = data.get(key)

    if value is None:
        raise ValueError(f"Missing required field {key} in {profile_path.name}")

    return scalar(value).strip()


def first_sequence(data: dict[str, Any], keys: tuple[str, ...], profile_path: Path) -> list[str]:
    for key in keys:
        value = data.get(key)

        if value is not None:
            return [scalar(item).strip() for item in sequence(value)]

    raise ValueError(f"Missing required field {' or '.join(keys)} in {profile_path.name}")


def scalar(value: Any) -> str:
    if not isinstance(value, str):
        raise ValueError(f"Expected string, found {type(value).__name__}")

    return value


def sequence(value: Any) -> list[Any]:
    if not isinstance(value, list):
        raise ValueError(f"Expected list, found {type(value).__name__}")

    return value


def load_simple_yaml(contents: str) -> dict[str, Any]:
    data: dict[str, Any] = {}
    lines = contents.splitlines()
    index = 0

    while index < len(lines):
        raw_line = lines[index]
        stripped = raw_line.strip()

        if not stripped or stripped.startswith("#"):
            index += 1
            continue

        indent = len(raw_line) - len(raw_line.lstrip(" "))
        key, separator, value = stripped.partition(":")

        if not separator:
            raise ValueError(f"Unable to parse YAML line: {raw_line}")

        value = value.strip()

        if value == "":
            items: list[str] = []
            index += 1

            while index < len(lines):
                item_line = lines[index]
                item_stripped = item_line.strip()
                item_indent = len(item_line) - len(item_line.lstrip(" "))

                if not item_stripped or item_stripped.startswith("#"):
                    index += 1
                    continue

                if item_indent <= indent:
                    break

                if not item_stripped.startswith("- "):
                    raise ValueError(f"Unable to parse YAML list item: {item_line}")

                items.append(strip_quotes(item_stripped[2:].strip()))
                index += 1

            data[key] = items
            continue

        data[key] = strip_quotes(value)
        index += 1

    return data


def strip_quotes(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]

    return value


def print_build_header(
    profile: ProfileConfig,
    generated_source: Path,
    final_pdf: Path,
    log_file: Path,
) -> None:
    print()
    print(f"{Color.BOLD}{Color.BLUE}──────────────────────────────────────────────{Color.RESET}")
    print(f"{Color.BOLD}{Color.BLUE}Resume Build{Color.RESET}")
    print(f"{Color.BOLD}{Color.BLUE}──────────────────────────────────────────────{Color.RESET}")
    print(f"{Color.BOLD}Profile:{Color.RESET} {profile.profile} ({profile.name})")
    print(f"{Color.BOLD}Source:{Color.RESET}  {generated_source}")
    print(f"{Color.BOLD}Output:{Color.RESET}  {final_pdf}")
    print(f"{Color.BOLD}Log:{Color.RESET}     {log_file}")
    print()


def print_success(profile: ProfileConfig, final_pdf: Path) -> None:
    print()
    print(f"{Color.GREEN}✅ Build complete{Color.RESET}")
    print(f"{Color.BOLD}Profile:{Color.RESET} {profile.profile}")
    print(f"{Color.BOLD}PDF:{Color.RESET}     {final_pdf}")
    print()


def print_error(message: str) -> None:
    print()
    print(f"{Color.RED}❌ Error{Color.RESET}", file=sys.stderr)
    print(message, file=sys.stderr)
    print()


def print_log_tail(log_file: Path, lines: int = 80) -> None:
    if not log_file.exists():
        print(f"{Color.YELLOW}No LaTeX log file found: {log_file}{Color.RESET}")
        return

    print()
    print(f"{Color.YELLOW}Last {lines} lines from LaTeX log:{Color.RESET}")
    print(f"{Color.YELLOW}{'─' * 80}{Color.RESET}")

    contents = log_file.read_text(encoding="utf-8", errors="ignore").splitlines()

    for line in contents[-lines:]:
        print(line)

    print(f"{Color.YELLOW}{'─' * 80}{Color.RESET}")
    print()


def open_pdf(pdf_path: Path) -> None:
    if not pdf_path.exists():
        return

    if sys.platform == "darwin":
        subprocess.run(["open", str(pdf_path)], check=False)
    elif sys.platform.startswith("linux") and shutil.which("xdg-open"):
        subprocess.run(["xdg-open", str(pdf_path)], check=False)
    elif sys.platform == "win32":
        os.startfile(str(pdf_path))  # type: ignore[attr-defined]


if __name__ == "__main__":
    main()
