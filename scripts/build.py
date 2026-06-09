#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0
"""build.py — Build profile-driven resume PDFs from LaTeX source.

Usage:
    python scripts/build.py [--profile PROFILE] [--open]

Options:
    --profile PROFILE   Profile variant to build (default: all configured profiles)
    --open              Open the generated PDF after building
    --help              Show this help message
"""

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
    "education",
    "skills",
    "publications",
}


@dataclass(frozen=True)
class ProfileConfig:
    profile: str
    name: str
    description: str
    summary: str
    section_order: tuple[str, ...]
    included_sections: tuple[str, ...]
    keyword_emphasis: tuple[str, ...]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build resume PDF from LaTeX source.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--profile",
        metavar="PROFILE",
        default=None,
        help="Profile variant to build (e.g. ai-infra, platform, research, general).",
    )
    parser.add_argument(
        "--open",
        action="store_true",
        help="Open the generated PDF after building.",
    )
    return parser.parse_args()


def build() -> None:
    args = parse_args()

    if not RESUME_TEX.exists():
        print(f"Error: resume.tex not found at '{RESUME_TEX}'.", file=sys.stderr)
        sys.exit(1)

    if not LATEXMKRC.exists():
        print(f"Error: .latexmkrc not found at '{LATEXMKRC}'.", file=sys.stderr)
        sys.exit(1)

    if not PROFILES_DIR.exists():
        print(f"Error: profiles directory not found at '{PROFILES_DIR}'.", file=sys.stderr)
        sys.exit(1)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    AUX_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    try:
        profiles = load_profiles()
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.profile:
        try:
            selected_profiles = [profiles[args.profile]]
        except KeyError:
            available = ", ".join(sorted(profiles))
            print(
                f"Error: Unknown profile '{args.profile}'. Available profiles: {available}.",
                file=sys.stderr,
            )
            sys.exit(1)
    else:
        selected_profiles = [profiles[name] for name in sorted(profiles)]

    try:
        built_pdfs = [build_profile(profile) for profile in selected_profiles]
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    if args.open and built_pdfs:
        _open_pdf(built_pdfs[0])


def load_profiles() -> dict[str, ProfileConfig]:
    profiles: dict[str, ProfileConfig] = {}

    for profile_path in sorted(PROFILES_DIR.glob("*.yaml")):
        profile = load_profile(profile_path)
        if profile.profile in profiles:
            raise ValueError(
                f"Duplicate profile '{profile.profile}' found in '{profile_path.name}'."
            )
        profiles[profile.profile] = profile

    if not profiles:
        raise ValueError(f"No profile definitions found in '{PROFILES_DIR}'.")

    return profiles


def load_profile(profile_path: Path) -> ProfileConfig:
    data = _load_yaml(profile_path)

    profile = _require_scalar(data, "profile", profile_path)
    name = _first_scalar(data, ("name", "label"), profile_path)
    description = _scalar(data.get("description", "")).strip()
    summary = _first_scalar(data, ("summary", "summary_variant"), profile_path)
    section_order = _first_sequence(data, ("section_order", "sections"), profile_path)
    included_sections = _first_sequence(
        data,
        ("included_sections", "sections"),
        profile_path,
    )
    keyword_emphasis = _first_sequence(
        data,
        ("keyword_emphasis", "emphasis"),
        profile_path,
    )

    _validate_sections(section_order, included_sections, profile_path)

    return ProfileConfig(
        profile=profile,
        name=name,
        description=description,
        summary=summary,
        section_order=tuple(section_order),
        included_sections=tuple(included_sections),
        keyword_emphasis=tuple(keyword_emphasis),
    )


def build_profile(profile: ProfileConfig) -> Path:
    generated_source = REPOSITORY_ROOT / f"resume-{profile.profile}.generated.tex"
    source_pdf = OUT_DIR / f"{generated_source.stem}.pdf"
    final_pdf = OUTPUTS_DIR / f"resume-{profile.profile}.pdf"

    if source_pdf.exists():
        source_pdf.unlink()

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
        f"-r={LATEXMKRC}",
        str(generated_source),
    ]

    print(f"Building resume [{profile.profile}]...")
    print(f"  Source:  {generated_source}")
    print(f"  Output:  {final_pdf}")

    try:
        try:
            result = subprocess.run(cmd, cwd=REPOSITORY_ROOT)
        except FileNotFoundError as exc:
            raise FileNotFoundError(
                "latexmk is not installed or not available on PATH."
            ) from exc

        if result.returncode != 0:
            raise RuntimeError(f"LaTeX build failed for profile '{profile.profile}'.")

        if not source_pdf.exists():
            raise FileNotFoundError(f"Expected PDF not found at '{source_pdf}'.")

        shutil.copy2(source_pdf, final_pdf)
        print(f"Build complete: {final_pdf}")
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
        raise ValueError(
            f"Unable to locate document markers in '{RESUME_TEX.name}'."
        ) from exc

    rendered_sections: list[str] = []
    included_sections = set(profile.included_sections)

    for section in profile.section_order:
        if section not in included_sections:
            continue

        if section == "summary":
            rendered_sections.append(render_summary(profile))
        else:
            rendered_sections.append(f"\\input{{sections/{section}}}")

        if section == "header":
            rendered_sections.append("\\vspace{0.5em}")

    body = "\n\n".join(["\\pagestyle{fancy}", *rendered_sections])
    return f"{preamble}{document_start}\n\n{body}\n\n{document_end}\n"


def render_summary(profile: ProfileConfig) -> str:
    keywords = ", ".join(
        f"\\textbf{{{escape_latex(keyword)}}}" for keyword in profile.keyword_emphasis
    )
    lines = [
        "\\section{Summary}",
        "",
        f"{escape_latex(profile.summary)}",
    ]

    if keywords:
        lines.extend(["", f"\\textbf{{Keyword Emphasis:}} {keywords}."])

    return "\n".join(lines)


def escape_latex(value: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(char, char) for char in value)


def _validate_sections(
    section_order: list[str], included_sections: list[str], profile_path: Path
) -> None:
    unknown_sections = sorted(
        (set(section_order) | set(included_sections)) - SUPPORTED_SECTIONS
    )
    if unknown_sections:
        names = ", ".join(unknown_sections)
        raise ValueError(
            f"Unsupported sections in '{profile_path.name}': {names}."
        )

    missing_order = [section for section in included_sections if section not in section_order]
    if missing_order:
        names = ", ".join(missing_order)
        raise ValueError(
            f"Included sections missing from section_order in '{profile_path.name}': {names}."
        )


def _first_scalar(data: dict[str, Any], keys: tuple[str, ...], profile_path: Path) -> str:
    for key in keys:
        value = data.get(key)
        if value is not None:
            return _scalar(value).strip()
    expected = " or ".join(keys)
    raise ValueError(f"Missing required field '{expected}' in '{profile_path.name}'.")


def _require_scalar(data: dict[str, Any], key: str, profile_path: Path) -> str:
    value = data.get(key)
    if value is None:
        raise ValueError(f"Missing required field '{key}' in '{profile_path.name}'.")
    return _scalar(value).strip()


def _first_sequence(
    data: dict[str, Any], keys: tuple[str, ...], profile_path: Path
) -> list[str]:
    for key in keys:
        value = data.get(key)
        if value is not None:
            return [_scalar(item).strip() for item in _sequence(value)]
    expected = " or ".join(keys)
    raise ValueError(f"Missing required field '{expected}' in '{profile_path.name}'.")


def _scalar(value: Any) -> str:
    if isinstance(value, str):
        return value
    raise ValueError(f"Expected a string value, found '{type(value).__name__}'.")


def _sequence(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    raise ValueError(f"Expected a list value, found '{type(value).__name__}'.")


def _load_yaml(profile_path: Path) -> dict[str, Any]:
    contents = profile_path.read_text(encoding="utf-8")

    try:
        import yaml  # type: ignore[import-not-found]
    except ImportError:
        data = _load_simple_yaml(contents)
    else:
        data = yaml.safe_load(contents) or {}

    if not isinstance(data, dict):
        raise ValueError(f"Profile definition '{profile_path.name}' must be a YAML mapping.")

    return data


def _load_simple_yaml(contents: str) -> dict[str, Any]:
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
            raise ValueError(f"Unable to parse YAML line: '{raw_line}'.")

        value = value.strip()
        if value == ">":
            block_lines: list[str] = []
            index += 1
            while index < len(lines):
                block_line = lines[index]
                block_stripped = block_line.strip()
                block_indent = len(block_line) - len(block_line.lstrip(" "))

                if block_stripped and not block_stripped.startswith("#") and block_indent <= indent:
                    break

                if block_stripped and not block_stripped.startswith("#"):
                    block_lines.append(block_stripped)

                index += 1

            data[key] = " ".join(block_lines)
            continue

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
                    raise ValueError(f"Unable to parse YAML list item: '{item_line}'.")

                items.append(_strip_quotes(item_stripped[2:].strip()))
                index += 1

            data[key] = items
            continue

        data[key] = _strip_quotes(value)
        index += 1

    return data


def _strip_quotes(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def _open_pdf(pdf_path: Path) -> None:
    if not pdf_path.exists():
        return

    if sys.platform == "darwin":
        subprocess.run(["open", str(pdf_path)], check=False)
    elif sys.platform.startswith("linux"):
        if shutil.which("xdg-open"):
            subprocess.run(["xdg-open", str(pdf_path)], check=False)
    elif sys.platform == "win32":
        os.startfile(str(pdf_path))  # type: ignore[attr-defined]


if __name__ == "__main__":
    build()
