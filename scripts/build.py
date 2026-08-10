#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0
"""Build profile-driven résumé and CV PDFs from LaTeX source.

Architecture
------------
Five concepts are kept distinct during build resolution:

  1. content/evidence  — canonical career facts in sections/*.tex
  2. document type     — resume | cv  (documents/*.yaml)
  3. profile           — broad role-family emphasis  (profiles/*.yaml)
  4. target            — optional application-specific overlay (targets/*.yaml)
  5. template/theme    — LaTeX style (templates/<type>/template.tex)

Resolution merge order:
  document manifest defaults
    -> profile
    -> optional target overlay
    -> explicit CLI overrides (--page-size)

Output paths
------------
  dist/<document_type>/<profile>/alan-szmyt-<document_type>-<profile>.pdf
  dist/<document_type>/<profile>/<target>/alan-szmyt-<document_type>-<profile>-<target>.pdf

Backward compatibility
----------------------
``--document`` defaults to ``resume``, so existing ``--profile`` invocations
continue to work. The output directory has changed from ``outputs/`` to
``dist/``; a compatibility copy is written to ``outputs/`` for any workflow
that still expects the old path.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
OUTPUTS_DIR = REPOSITORY_ROOT / "outputs"
DIST_DIR = REPOSITORY_ROOT / "dist"
CACHE_DIR = REPOSITORY_ROOT / ".cache"
OUT_DIR = CACHE_DIR / "out"
AUX_DIR = CACHE_DIR / "aux"
LATEXMKRC = REPOSITORY_ROOT / ".latexmkrc"
PROFILES_DIR = REPOSITORY_ROOT / "profiles"
DOCUMENTS_DIR = REPOSITORY_ROOT / "documents"
TARGETS_DIR = REPOSITORY_ROOT / "targets"
TEMPLATES_DIR = REPOSITORY_ROOT / "templates"
RESUME_TEX = REPOSITORY_ROOT / "resume.tex"

SUPPORTED_DOCUMENT_TYPES = {"resume", "cv"}
SUPPORTED_PAGE_SIZES = {"letter", "a4"}
PAGE_CLASS_MAP = {"letter": "letterpaper", "a4": "a4paper"}

# Sections available per document type. The CV superset includes extension
# points that are empty until populated in follow-up content work.
RESUME_SECTIONS: frozenset[str] = frozenset({
    "header",
    "summary",
    "experience",
    "publications",
    "education",
    "skills",
})
CV_SECTIONS: frozenset[str] = RESUME_SECTIONS | frozenset({
    "projects",
    "talks",
    "awards",
    "service",
})
DOCUMENT_SECTION_POOLS: dict[str, frozenset[str]] = {
    "resume": RESUME_SECTIONS,
    "cv": CV_SECTIONS,
}

# Legacy alias kept so quality_gates.py continues to work unchanged.
SUPPORTED_SECTIONS = RESUME_SECTIONS


class Color:
    BLUE = "\033[34m"
    GREEN = "\033[32m"
    RED = "\033[31m"
    YELLOW = "\033[33m"
    BOLD = "\033[1m"
    RESET = "\033[0m"


@dataclass(frozen=True)
class DocumentManifest:
    """Parsed document manifest from documents/<type>.yaml."""

    document_type: str
    default_template: str
    default_page_size: str
    section_pool: tuple[str, ...]
    default_section_order: tuple[str, ...]


@dataclass(frozen=True)
class ProfileConfig:
    """Parsed profile variant from profiles/<name>.yaml."""

    profile: str
    name: str
    section_order: tuple[str, ...]
    included_sections: tuple[str, ...]
    keyword_emphasis: tuple[str, ...]
    description: str = ""


@dataclass(frozen=True)
class TargetConfig:
    """Parsed application-specific overlay from targets/<name>.yaml."""

    target: str
    description: str
    document_type: str | None = None
    profile: str | None = None
    page_size: str | None = None
    section_order: tuple[str, ...] | None = None
    output_basename: str | None = None


@dataclass(frozen=True)
class BuildConfig:
    """Fully resolved build configuration after merging all layers."""

    document_type: str
    profile: str
    template: str
    page_size: str
    section_order: tuple[str, ...]
    included_sections: tuple[str, ...]
    output_basename: str
    target: str | None = None


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    args = parse_args()

    try:
        if args.list:
            print_available()
            return

        ensure_paths()
        documents = load_document_manifests()
        profiles = load_profiles()

        document_type = args.document or "resume"
        if document_type not in documents:
            available = ", ".join(sorted(documents))
            raise ValueError(
                f"Unknown document type '{document_type}'. Available: {available}"
            )

        document = documents[document_type]
        selected_profiles = select_profiles(profiles, args.profile)
        target: TargetConfig | None = None
        if args.target:
            target = load_target(TARGETS_DIR / f"{args.target}.yaml")

        built_pdfs: list[Path] = []
        for prof in selected_profiles:
            config = resolve_config(
                document=document,
                profile=prof,
                target=target,
                page_size_override=args.page_size,
            )
            pdf = build_document(config)
            built_pdfs.append(pdf)

        if args.open and built_pdfs:
            open_pdf(built_pdfs[0])

    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        print_error(str(exc))
        sys.exit(1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build résumé and CV PDFs from canonical LaTeX content.\n\n"
            "Examples:\n"
            "  python scripts/build.py --document resume --profile general\n"
            "  python scripts/build.py --document cv --profile research\n"
            "  python scripts/build.py --document cv --profile research --page-size a4\n"
            "  python scripts/build.py --document resume --profile general --target example\n"
            "  python scripts/build.py --list\n"
            "  python scripts/build.py --profile general  # backward-compatible (resume)"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--document",
        metavar="DOCUMENT",
        default=None,
        help=(
            "Document type to build: resume | cv. "
            "Defaults to 'resume' when omitted (backward-compatible)."
        ),
    )
    parser.add_argument(
        "--profile",
        metavar="PROFILE",
        default=None,
        help="Profile variant to build. Builds all profiles when omitted.",
    )
    parser.add_argument(
        "--target",
        metavar="TARGET",
        default=None,
        help="Optional application-specific overlay (targets/<name>.yaml).",
    )
    parser.add_argument(
        "--page-size",
        metavar="SIZE",
        default=None,
        choices=sorted(SUPPORTED_PAGE_SIZES),
        help="Override page size: letter | a4. Inherits from document/target otherwise.",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available documents, profiles, and targets, then exit.",
    )
    parser.add_argument(
        "--open",
        action="store_true",
        help="Open the first generated PDF after building.",
    )
    return parser.parse_args()


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------


def print_available() -> None:
    documents = load_document_manifests()
    profiles = load_profiles()
    targets = load_all_targets()

    print(f"\n{Color.BOLD}Available document types:{Color.RESET}")
    for name, doc in sorted(documents.items()):
        print(f"  {name:12}  template={doc.default_template}, page-size={doc.default_page_size}")

    print(f"\n{Color.BOLD}Available profiles:{Color.RESET}")
    for name, prof in sorted(profiles.items()):
        print(f"  {name:12}  {prof.name}")

    print(f"\n{Color.BOLD}Available targets:{Color.RESET}")
    if targets:
        for name, t in sorted(targets.items()):
            print(f"  {name:12}  {t.description.strip()[:60]}")
    else:
        print("  (none)")

    print()


def load_all_targets() -> dict[str, TargetConfig]:
    targets: dict[str, TargetConfig] = {}
    if not TARGETS_DIR.exists():
        return targets
    for path in sorted(TARGETS_DIR.glob("*.yaml")):
        t = load_target(path)
        targets[t.target] = t
    return targets


# ---------------------------------------------------------------------------
# Document manifests
# ---------------------------------------------------------------------------


def load_document_manifests() -> dict[str, DocumentManifest]:
    manifests: dict[str, DocumentManifest] = {}
    if not DOCUMENTS_DIR.exists():
        raise FileNotFoundError(f"Documents directory not found: {DOCUMENTS_DIR}")

    for path in sorted(DOCUMENTS_DIR.glob("*.yaml")):
        doc = load_document_manifest(path)
        if doc.document_type in manifests:
            raise ValueError(f"Duplicate document type '{doc.document_type}' in {path.name}")
        manifests[doc.document_type] = doc

    if not manifests:
        raise ValueError(f"No document manifests found in {DOCUMENTS_DIR}")

    return manifests


def load_document_manifest(path: Path) -> DocumentManifest:
    data = load_yaml(path)

    document_type = require_scalar(data, "document_type", path)
    if document_type not in SUPPORTED_DOCUMENT_TYPES:
        raise ValueError(
            f"Unsupported document_type '{document_type}' in {path.name}. "
            f"Supported: {', '.join(sorted(SUPPORTED_DOCUMENT_TYPES))}"
        )

    default_template = require_scalar(data, "default_template", path)
    default_page_size = first_scalar(data, ("default_page_size",), path)
    if default_page_size not in SUPPORTED_PAGE_SIZES:
        raise ValueError(
            f"Unsupported page size '{default_page_size}' in {path.name}. "
            f"Supported: {', '.join(sorted(SUPPORTED_PAGE_SIZES))}"
        )

    section_pool = first_sequence(data, ("section_pool",), path)
    default_section_order = first_sequence(data, ("default_section_order",), path)

    return DocumentManifest(
        document_type=document_type,
        default_template=default_template,
        default_page_size=default_page_size,
        section_pool=tuple(section_pool),
        default_section_order=tuple(default_section_order),
    )


# ---------------------------------------------------------------------------
# Profiles
# ---------------------------------------------------------------------------


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
    description = data.get("description", "")
    if description and not isinstance(description, str):
        description = str(description)

    return ProfileConfig(
        profile=profile,
        name=name,
        section_order=tuple(section_order),
        included_sections=tuple(included_sections),
        keyword_emphasis=tuple(keyword_emphasis),
        description=description.strip() if description else "",
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


# ---------------------------------------------------------------------------
# Targets
# ---------------------------------------------------------------------------


def load_target(path: Path) -> TargetConfig:
    if not path.exists():
        raise FileNotFoundError(f"Target file not found: {path}")

    data = load_yaml(path)
    target = require_scalar(data, "target", path)
    description = data.get("description", "")
    if description and not isinstance(description, str):
        description = str(description)

    document_type = data.get("document_type")
    profile = data.get("profile")
    page_size = data.get("page_size")
    output_basename = data.get("output_basename")

    if document_type is not None:
        document_type = scalar(document_type).strip()
        if document_type not in SUPPORTED_DOCUMENT_TYPES:
            raise ValueError(
                f"Unknown document_type '{document_type}' in target {path.name}."
            )

    if page_size is not None:
        page_size = scalar(page_size).strip()
        if page_size not in SUPPORTED_PAGE_SIZES:
            raise ValueError(
                f"Unknown page_size '{page_size}' in target {path.name}. "
                f"Supported: {', '.join(sorted(SUPPORTED_PAGE_SIZES))}"
            )

    raw_order = data.get("section_order")
    section_order: tuple[str, ...] | None = None
    if raw_order is not None:
        section_order = tuple(scalar(s).strip() for s in sequence(raw_order))

    if output_basename is not None:
        output_basename = scalar(output_basename).strip()

    return TargetConfig(
        target=target,
        description=description.strip() if description else "",
        document_type=document_type or None,
        profile=scalar(profile).strip() if profile else None,
        page_size=page_size or None,
        section_order=section_order,
        output_basename=output_basename,
    )


# ---------------------------------------------------------------------------
# Config resolution
# ---------------------------------------------------------------------------


def resolve_config(
    document: DocumentManifest,
    profile: ProfileConfig,
    target: TargetConfig | None,
    page_size_override: str | None,
) -> BuildConfig:
    """Merge document → profile → target → CLI into a final BuildConfig.

    Resolution rules:
    - section_order:    target > profile > document default
    - included_sections: profile (intersected with section_pool)
    - page_size:        CLI > target > document default
    - template:         document default (not overridable in this release)
    """
    section_pool = set(document.section_pool)

    # Section ordering: target can override, else use profile, else document default.
    if target is not None and target.section_order is not None:
        section_order = target.section_order
    else:
        section_order = profile.section_order

    # Included sections always come from the profile, restricted to the pool.
    included_sections = tuple(
        s for s in profile.included_sections if s in section_pool
    )

    # Validate sections against pool.
    unknown_in_order = sorted(set(section_order) - section_pool)
    if unknown_in_order:
        raise ValueError(
            f"Section(s) not in pool for document '{document.document_type}': "
            f"{', '.join(unknown_in_order)}. "
            f"Pool: {', '.join(sorted(section_pool))}"
        )

    unknown_included = sorted(set(included_sections) - section_pool)
    if unknown_included:
        raise ValueError(
            f"Included section(s) not in pool for document '{document.document_type}': "
            f"{', '.join(unknown_included)}"
        )

    # Ensure every included section appears in section_order.
    included_set = set(included_sections)
    missing_from_order = [s for s in included_sections if s not in section_order]
    if missing_from_order:
        raise ValueError(
            f"Included sections missing from section_order: "
            f"{', '.join(missing_from_order)}"
        )

    # Duplicate check in section_order.
    seen: set[str] = set()
    for s in section_order:
        if s in seen:
            raise ValueError(f"Duplicate section in section_order: '{s}'")
        seen.add(s)

    # Page size: CLI > target > document default.
    if page_size_override:
        page_size = page_size_override
    elif target is not None and target.page_size:
        page_size = target.page_size
    else:
        page_size = document.default_page_size

    # Output basename.
    if target is not None and target.output_basename:
        basename = target.output_basename
    elif target is not None:
        basename = f"alan-szmyt-{document.document_type}-{profile.profile}-{target.target}"
    else:
        basename = f"alan-szmyt-{document.document_type}-{profile.profile}"

    return BuildConfig(
        document_type=document.document_type,
        profile=profile.profile,
        template=document.default_template,
        page_size=page_size,
        section_order=tuple(section_order),
        included_sections=included_sections,
        output_basename=basename,
        target=target.target if target else None,
    )


# ---------------------------------------------------------------------------
# Build execution
# ---------------------------------------------------------------------------


def ensure_paths() -> None:
    for path in (LATEXMKRC, PROFILES_DIR, DOCUMENTS_DIR):
        if not path.exists():
            raise FileNotFoundError(f"Required path not found: {path}")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    AUX_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    DIST_DIR.mkdir(parents=True, exist_ok=True)


def build_document(config: BuildConfig) -> Path:
    stem = config.output_basename
    generated_source = REPOSITORY_ROOT / f"{stem}.generated.tex"
    source_pdf = OUT_DIR / f"{stem}.pdf"

    # Deterministic dist output path.
    if config.target:
        final_pdf_dir = DIST_DIR / config.document_type / config.profile / config.target
    else:
        final_pdf_dir = DIST_DIR / config.document_type / config.profile
    final_pdf = final_pdf_dir / f"{stem}.pdf"
    final_pdf_dir.mkdir(parents=True, exist_ok=True)

    log_file = AUX_DIR / f"{stem}.log"

    generated_source.write_text(render_document(config), encoding="utf-8")

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

    print_build_header(config, generated_source, final_pdf, log_file)

    try:
        try:
            result = subprocess.run(cmd, cwd=REPOSITORY_ROOT, check=False)
        except FileNotFoundError as exc:
            raise FileNotFoundError("latexmk is not installed or not available on PATH.") from exc

        if result.returncode != 0:
            print_log_tail(log_file)
            raise RuntimeError(
                f"LaTeX build failed for '{config.output_basename}'.\n"
                f"Log file: {log_file}\n"
                f"Tail log: tail --lines=100 {log_file}"
            )

        if not source_pdf.exists():
            print_log_tail(log_file)
            raise FileNotFoundError(f"Expected PDF not found: {source_pdf}")

        shutil.copy2(source_pdf, final_pdf)

        # Backward-compatible copy for tooling that still reads outputs/.
        compat_pdf = OUTPUTS_DIR / f"{stem}.pdf"
        shutil.copy2(source_pdf, compat_pdf)

        print_success(config, final_pdf)
        return final_pdf

    finally:
        generated_source.unlink(missing_ok=True)


def render_document(config: BuildConfig) -> str:
    """Render the generated .tex source for a given BuildConfig.

    Reads the preamble from ``templates/<document_type>/template.tex`` if
    present, otherwise falls back to reading the preamble from ``resume.tex``
    (backward-compatible path for résumé builds).
    """
    template_path = TEMPLATES_DIR / config.document_type / "template.tex"
    if template_path.exists():
        preamble = _render_preamble_from_template(template_path, config)
    else:
        preamble = _render_preamble_from_resume_tex(config)

    included_sections = set(config.included_sections)
    rendered_sections: list[str] = ["\\pagestyle{fancy}"]

    for section in config.section_order:
        if section not in included_sections:
            continue

        rendered_sections.append(f"\\input{{sections/{section}}}")

        if section == "header":
            rendered_sections.append("\\vspace{0.5em}")

    body = "\n\n".join(rendered_sections)
    return f"{preamble}\\begin{{document}}\n\n{body}\n\n\\end{{document}}\n"


def _render_preamble_from_template(template_path: Path, config: BuildConfig) -> str:
    """Read a structured template.tex and substitute build-time placeholders."""
    doc_type_label = config.document_type.capitalize()
    page_class = PAGE_CLASS_MAP.get(config.page_size, "letterpaper")
    keywords = ", ".join([
        "Software Engineering",
        "Systems Engineering",
        "Platform Engineering",
        f"{doc_type_label}",
    ])

    text = template_path.read_text(encoding="utf-8")
    text = text.replace("{{PAGE_CLASS}}", page_class)
    text = text.replace("{{DOCUMENT_TITLE}}", f"Alan Szmyt {doc_type_label}")
    text = text.replace(
        "{{DOCUMENT_SUBJECT}}",
        f"Software Engineer, Systems Architect, and Research Engineer {doc_type_label}",
    )
    text = text.replace("{{PDF_KEYWORDS}}", keywords)
    return text + "\n"


def _render_preamble_from_resume_tex(config: BuildConfig) -> str:
    """Extract the preamble from resume.tex (legacy résumé path)."""
    source = RESUME_TEX.read_text(encoding="utf-8")
    document_start = "\\begin{document}"
    try:
        preamble, _ = source.split(document_start, maxsplit=1)
    except ValueError as exc:
        raise ValueError(f"Unable to locate document markers in {RESUME_TEX}") from exc
    return preamble


# ---------------------------------------------------------------------------
# Legacy helpers kept for validate_sections in quality_gates.py
# ---------------------------------------------------------------------------


def validate_sections(
    section_order: list[str],
    included_sections: list[str],
    profile_path: Path,
    section_pool: frozenset[str] | None = None,
) -> None:
    pool = section_pool if section_pool is not None else SUPPORTED_SECTIONS

    unknown_sections = sorted(
        (set(section_order) | set(included_sections)) - pool
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

        if value in {">", "|", ">-", "|-"}:
            block_lines: list[str] = []
            block_indent: int | None = None
            index += 1

            while index < len(lines):
                block_line = lines[index]
                block_stripped = block_line.strip()
                current_indent = len(block_line) - len(block_line.lstrip(" "))

                if not block_stripped:
                    block_lines.append("")
                    index += 1
                    continue

                if current_indent <= indent:
                    break

                if block_indent is None:
                    block_indent = current_indent

                normalized = block_line[block_indent:] if len(block_line) >= block_indent else block_stripped
                block_lines.append(normalized.rstrip())
                index += 1

            if value.startswith(">"):
                folded = " ".join(part for part in block_lines if part)
                data[key] = strip_quotes(folded.strip())
            else:
                literal = "\n".join(block_lines).strip()
                data[key] = strip_quotes(literal)
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
    config: BuildConfig,
    generated_source: Path,
    final_pdf: Path,
    log_file: Path,
) -> None:
    doc_label = config.document_type.capitalize()
    print()
    print(f"{Color.BOLD}{Color.BLUE}──────────────────────────────────────────────{Color.RESET}")
    print(f"{Color.BOLD}{Color.BLUE}{doc_label} Build{Color.RESET}")
    print(f"{Color.BOLD}{Color.BLUE}──────────────────────────────────────────────{Color.RESET}")
    print(f"{Color.BOLD}Document:{Color.RESET} {config.document_type}")
    print(f"{Color.BOLD}Profile:{Color.RESET}  {config.profile}")
    if config.target:
        print(f"{Color.BOLD}Target:{Color.RESET}   {config.target}")
    print(f"{Color.BOLD}Page:{Color.RESET}     {config.page_size}")
    print(f"{Color.BOLD}Source:{Color.RESET}   {generated_source}")
    print(f"{Color.BOLD}Output:{Color.RESET}   {final_pdf}")
    print(f"{Color.BOLD}Log:{Color.RESET}      {log_file}")
    print()


def print_success(config: BuildConfig, final_pdf: Path) -> None:
    print()
    print(f"{Color.GREEN}✅ Build complete{Color.RESET}")
    print(f"{Color.BOLD}Document:{Color.RESET} {config.document_type}")
    print(f"{Color.BOLD}Profile:{Color.RESET}  {config.profile}")
    print(f"{Color.BOLD}PDF:{Color.RESET}      {final_pdf}")
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
