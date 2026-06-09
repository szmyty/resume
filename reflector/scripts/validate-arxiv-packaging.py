#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0
# validate-arxiv-packaging.py — Validate arXiv upload packaging and structure.

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path


@dataclass(frozen=True)
class Check:
    area: str
    name: str
    status: str  # PASS | WARN | FAIL
    details: str


REPO_ROOT = Path(__file__).resolve().parent.parent
PAPER_DIR = REPO_ROOT / "paper"
AUDIT_OUTPUT = REPO_ROOT / "audits" / "arxiv-validation.md"

# arXiv-safe image formats
ARXIV_SAFE_IMAGE_EXTENSIONS = {".png", ".pdf", ".jpg", ".jpeg", ".eps"}
# arXiv-safe source file extensions (empty for directories)
ARXIV_SAFE_SOURCE_EXTENSIONS = {".tex", ".bib", ".sty", ".png", ".pdf", ".jpg", ".jpeg", ".eps", ""}
# Supported usage values in 00README
ALLOWED_SOURCE_USAGES = {"toplevel", "include", "ignore"}
# Supported compilers for arXiv
ARXIV_SUPPORTED_COMPILERS = {"pdflatex", "latex", "xelatex", "lualatex"}
# Supported bibliography tools for arXiv
ARXIV_SUPPORTED_BIBLIOGRAPHY = {"biber", "bibtex", "bibtex8"}
# arXiv per-file size limit (10 MB)
ARXIV_FILE_SIZE_LIMIT_BYTES = 10 * 1024 * 1024
# arXiv total upload size limit (50 MB)
ARXIV_TOTAL_SIZE_LIMIT_BYTES = 50 * 1024 * 1024
# System files that must not be present in the upload bundle
BANNED_FILENAMES = {".DS_Store", "Thumbs.db", "desktop.ini"}
# Placeholder / repository support files that are intentionally non-image and should be excluded from image format checks
NON_FIGURE_SUPPORT_NAMES = {".gitkeep", ".gitignore", ".keep", ".nojekyll"}


def add_check(
    checks: list[Check],
    area: str,
    name: str,
    condition: bool,
    pass_details: str,
    fail_details: str,
    warn: bool = False,
) -> None:
    if condition:
        status = "PASS"
        details = pass_details
    else:
        status = "WARN" if warn else "FAIL"
        details = fail_details
    checks.append(Check(area=area, name=name, status=status, details=details))


def gather_checks() -> list[Check]:
    checks: list[Check] = []

    # -------------------------------------------------------------------------
    # 1. 00README.json manifest validation
    # -------------------------------------------------------------------------
    readme_json_path = PAPER_DIR / "00README.json"
    try:
        readme_text = readme_json_path.read_text(encoding="utf-8")
        readme_json: dict = json.loads(readme_text)
        readme_json_ok = True
    except FileNotFoundError:
        readme_json = {}
        readme_json_ok = False
    except json.JSONDecodeError:
        readme_json = {}
        readme_json_ok = False

    add_check(
        checks,
        "Manifest",
        "00README.json is parseable JSON",
        readme_json_ok,
        "paper/00README.json is valid JSON.",
        "paper/00README.json is missing or invalid JSON.",
    )

    schema_val = str(readme_json.get("$schema", ""))
    add_check(
        checks,
        "Manifest",
        "00README schema references arXiv",
        schema_val.startswith("https://arxiv.org/schemas/00readme/"),
        "00README $schema references the arXiv 00readme schema.",
        f"00README $schema does not reference an arXiv 00readme schema URL (found: {schema_val!r}).",
    )

    required_root_keys = {"manifest_version", "publication", "process", "sources", "build"}
    missing_root_keys = sorted(required_root_keys - set(readme_json.keys()))
    add_check(
        checks,
        "Manifest",
        "00README required root keys present",
        not missing_root_keys,
        "00README includes all required root keys.",
        "00README is missing required root keys: " + ", ".join(missing_root_keys),
    )

    # process block
    process = readme_json.get("process", {}) if isinstance(readme_json.get("process"), dict) else {}
    compiler = str(process.get("compiler", "")).strip()
    bibliography = str(process.get("bibliography", "")).strip()
    deterministic = process.get("deterministic", False)
    texlive_declared = str(process.get("texlive", "")).strip()
    max_repeat = process.get("max_repeat")

    add_check(
        checks,
        "Manifest",
        "Compiler is declared",
        bool(compiler),
        f"Compiler declared in process block: {compiler!r}.",
        "process.compiler is not declared in 00README.",
    )
    add_check(
        checks,
        "Manifest",
        "Compiler is arXiv-supported",
        compiler in ARXIV_SUPPORTED_COMPILERS,
        f"Declared compiler {compiler!r} is supported by arXiv.",
        f"Declared compiler {compiler!r} is not in the arXiv-supported set: {sorted(ARXIV_SUPPORTED_COMPILERS)}.",
    )
    add_check(
        checks,
        "Manifest",
        "Bibliography tool is declared",
        bool(bibliography),
        f"Bibliography tool declared: {bibliography!r}.",
        "process.bibliography is not declared in 00README.",
    )
    add_check(
        checks,
        "Manifest",
        "Bibliography tool is supported",
        bibliography in ARXIV_SUPPORTED_BIBLIOGRAPHY,
        f"Declared bibliography tool {bibliography!r} is supported.",
        f"Declared bibliography tool {bibliography!r} is not in the supported set: {sorted(ARXIV_SUPPORTED_BIBLIOGRAPHY)}.",
    )
    add_check(
        checks,
        "Manifest",
        "Deterministic flag is set",
        deterministic is True,
        "process.deterministic is true in 00README.",
        "process.deterministic is not set to true in 00README.",
    )
    add_check(
        checks,
        "Manifest",
        "TeXLive version declared",
        bool(texlive_declared),
        f"TeXLive version declared in process block: {texlive_declared!r}.",
        "process.texlive is not declared in 00README.",
    )
    add_check(
        checks,
        "Manifest",
        "max_repeat declared",
        isinstance(max_repeat, int) and max_repeat > 0,
        f"process.max_repeat declared as {max_repeat}.",
        "process.max_repeat is not declared or not a positive integer in 00README.",
    )

    # build block
    build = readme_json.get("build", {}) if isinstance(readme_json.get("build"), dict) else {}
    build_script = str(build.get("script", "")).strip()
    orchestration = str(build.get("orchestration", "")).strip()

    add_check(
        checks,
        "Manifest",
        "Build script declared",
        bool(build_script),
        f"build.script declared: {build_script!r}.",
        "build.script is not declared in 00README.",
    )
    add_check(
        checks,
        "Manifest",
        "Orchestration config declared",
        bool(orchestration),
        f"build.orchestration declared: {orchestration!r}.",
        "build.orchestration is not declared in 00README.",
    )

    # -------------------------------------------------------------------------
    # 2. Source declarations
    # -------------------------------------------------------------------------
    sources = readme_json.get("sources", [])
    if not isinstance(sources, list):
        sources = []

    invalid_usages: list[str] = []
    missing_sources: list[str] = []
    unsupported_types: list[str] = []
    absolute_paths: list[str] = []
    escaping_paths: list[str] = []
    toplevel_count = 0

    for source in sources:
        if not isinstance(source, dict):
            continue
        path_val = str(source.get("path", "")).strip()
        usage = str(source.get("usage", "")).strip()

        if usage not in ALLOWED_SOURCE_USAGES:
            invalid_usages.append(f"{path_val} ({usage!r})")
        if Path(path_val).is_absolute():
            absolute_paths.append(path_val)
        # Check path doesn't escape the paper directory
        try:
            (PAPER_DIR / path_val).resolve().relative_to(PAPER_DIR.resolve())
        except ValueError:
            escaping_paths.append(path_val)

        full_path = PAPER_DIR / path_val
        if not full_path.exists():
            missing_sources.append(path_val)
        ext = full_path.suffix.lower()
        if ext not in ARXIV_SAFE_SOURCE_EXTENSIONS:
            unsupported_types.append(path_val)
        if usage == "toplevel":
            toplevel_count += 1

    add_check(
        checks,
        "Source declarations",
        "All source usage values are valid",
        not invalid_usages,
        "All declared source usage values are valid.",
        "Invalid source usage values: " + ", ".join(invalid_usages),
    )
    add_check(
        checks,
        "Source declarations",
        "No absolute source paths",
        not absolute_paths,
        "All source paths are relative.",
        "Absolute paths found in sources: " + ", ".join(absolute_paths),
    )
    add_check(
        checks,
        "Source declarations",
        "No path-escaping source declarations",
        not escaping_paths,
        "No source paths escape the paper/ bundle directory.",
        "Source paths escaping paper/ found: " + ", ".join(escaping_paths),
    )
    add_check(
        checks,
        "Source declarations",
        "All declared sources exist on disk",
        not missing_sources,
        "All declared sources exist under paper/.",
        "Missing declared sources: " + ", ".join(missing_sources),
    )
    add_check(
        checks,
        "Source declarations",
        "All source file types are arXiv-safe",
        not unsupported_types,
        "All declared source file extensions are arXiv-safe.",
        "Unsupported file types in source declarations: " + ", ".join(unsupported_types),
    )
    add_check(
        checks,
        "Source declarations",
        "Exactly one toplevel source declared",
        toplevel_count == 1,
        "Exactly one toplevel source is declared.",
        f"Expected exactly 1 toplevel source; found {toplevel_count}.",
    )

    # bibliography declared in sources
    bib_in_sources = any(
        str(s.get("path", "")).endswith(".bib")
        for s in sources
        if isinstance(s, dict)
    )
    add_check(
        checks,
        "Source declarations",
        "Bibliography file declared in sources",
        bib_in_sources,
        "A .bib bibliography file is declared in sources.",
        "No .bib bibliography file is declared in sources.",
    )

    # style file declared in sources
    sty_in_sources = any(
        str(s.get("path", "")).endswith(".sty")
        for s in sources
        if isinstance(s, dict)
    )
    add_check(
        checks,
        "Source declarations",
        "Style file declared in sources",
        sty_in_sources,
        "A .sty publication style file is declared in sources.",
        "No .sty publication style file is declared in sources.",
    )

    # -------------------------------------------------------------------------
    # 3. Upload structure / filesystem sanity
    # -------------------------------------------------------------------------
    symlinks: list[str] = []
    for item in PAPER_DIR.rglob("*"):
        if item.is_symlink():
            symlinks.append(str(item.relative_to(PAPER_DIR)))

    add_check(
        checks,
        "Upload structure",
        "No symlinks in paper bundle",
        not symlinks,
        "No symlinks found under paper/.",
        "Symlinks found under paper/ (not supported by arXiv): " + ", ".join(symlinks),
    )

    # banned system files
    banned_found: list[str] = []
    for item in PAPER_DIR.rglob("*"):
        if item.name in BANNED_FILENAMES:
            banned_found.append(str(item.relative_to(PAPER_DIR)))

    add_check(
        checks,
        "Upload structure",
        "No system files in paper bundle",
        not banned_found,
        "No banned system files found under paper/.",
        "Banned system files found: " + ", ".join(banned_found),
    )

    # build artifacts must not bleed into declared sources
    cache_in_sources = [
        str(s.get("path", ""))
        for s in sources
        if isinstance(s, dict) and (
            str(s.get("path", "")).startswith(".cache/")
            or str(s.get("path", "")).endswith(".aux")
            or str(s.get("path", "")).endswith(".log")
            or str(s.get("path", "")).endswith(".fls")
            or str(s.get("path", "")).endswith(".fdb_latexmk")
        )
    ]
    add_check(
        checks,
        "Upload structure",
        "No build artifacts declared as sources",
        not cache_in_sources,
        "No build artifact paths (.cache/, .aux, .log, .fls) appear in source declarations.",
        "Build artifact paths found in source declarations: " + ", ".join(cache_in_sources),
    )

    # paper.tex exists as entrypoint
    add_check(
        checks,
        "Upload structure",
        "Toplevel paper.tex exists",
        (PAPER_DIR / "paper.tex").exists(),
        "paper/paper.tex exists as the toplevel LaTeX entrypoint.",
        "paper/paper.tex is missing.",
    )

    # references.bib exists
    add_check(
        checks,
        "Upload structure",
        "references.bib exists",
        (PAPER_DIR / "references.bib").exists(),
        "paper/references.bib exists.",
        "paper/references.bib is missing.",
    )

    # -------------------------------------------------------------------------
    # 4. Figure format compatibility
    # -------------------------------------------------------------------------
    figure_dir = PAPER_DIR / "figures"
    if figure_dir.is_dir():
        # Only consider actual image/asset files; skip .md docs, placeholders, and support files
        figure_files = [
            f for f in figure_dir.iterdir()
            if f.is_file()
            and not f.name.endswith(".md")
            and f.name not in NON_FIGURE_SUPPORT_NAMES
        ]
        unsupported_figs = [f.name for f in figure_files if f.suffix.lower() not in ARXIV_SAFE_IMAGE_EXTENSIONS]
        oversized_figs = [f.name for f in figure_files if f.stat().st_size > ARXIV_FILE_SIZE_LIMIT_BYTES]

        add_check(
            checks,
            "Figure compatibility",
            "All figure formats are arXiv-safe",
            not unsupported_figs,
            f"All {len(figure_files)} figure files use arXiv-safe image formats.",
            "Figures with unsupported formats: " + ", ".join(unsupported_figs),
        )
        add_check(
            checks,
            "Figure compatibility",
            "All figure files are within arXiv size limits",
            not oversized_figs,
            f"All figure files are within the {ARXIV_FILE_SIZE_LIMIT_BYTES // (1024 * 1024)} MB per-file size limit.",
            "Oversized figure files (> 10 MB): " + ", ".join(oversized_figs),
        )
    else:
        checks.append(Check(
            area="Figure compatibility",
            name="Figure directory exists",
            status="FAIL",
            details="paper/figures/ directory not found.",
        ))

    # total bundle size estimate
    total_bytes = sum(f.stat().st_size for f in PAPER_DIR.rglob("*") if f.is_file() and ".cache" not in f.parts)
    add_check(
        checks,
        "Figure compatibility",
        "Total paper bundle within arXiv upload limit",
        total_bytes < ARXIV_TOTAL_SIZE_LIMIT_BYTES,
        f"Total paper bundle size is {total_bytes // 1024} KB, within the 50 MB arXiv upload limit.",
        f"Total paper bundle size {total_bytes // (1024 * 1024)} MB exceeds the arXiv 50 MB upload limit.",
    )

    # -------------------------------------------------------------------------
    # 5. Bibliography / compilation path compatibility
    # -------------------------------------------------------------------------
    bib_path = PAPER_DIR / "references.bib"
    if bib_path.exists():
        bib_text = bib_path.read_text(encoding="utf-8")
        bib_entry_count = len(re.findall(r"^@\w+\{", bib_text, flags=re.MULTILINE))
        add_check(
            checks,
            "Bibliography",
            "Bibliography file is non-empty",
            bib_entry_count > 0,
            f"references.bib contains {bib_entry_count} bibliography entries.",
            "references.bib appears to be empty or contains no valid entries.",
        )

    # Check compiler/bibliography combination compatibility
    compatible_combinations = {
        ("pdflatex", "biber"),
        ("pdflatex", "bibtex"),
        ("pdflatex", "bibtex8"),
        ("lualatex", "biber"),
        ("xelatex", "biber"),
        ("latex", "bibtex"),
        ("latex", "bibtex8"),
    }
    combo = (compiler, bibliography)
    add_check(
        checks,
        "Bibliography",
        "Compiler/bibliography combination is compatible",
        combo in compatible_combinations or not (compiler and bibliography),
        f"Compiler {compiler!r} + bibliography {bibliography!r} is a known-compatible combination.",
        f"Compiler {compiler!r} + bibliography {bibliography!r} is not a standard arXiv-compatible combination.",
    )

    # Validate biblatex is used with biber (not bibtex)
    sty_path = PAPER_DIR / "styles" / "reflector.sty"
    if sty_path.exists():
        sty_text = sty_path.read_text(encoding="utf-8")
        uses_biblatex = "biblatex" in sty_text
        biblatex_backend_biber = "backend=biber" in sty_text
        add_check(
            checks,
            "Bibliography",
            "biblatex uses biber backend",
            not uses_biblatex or biblatex_backend_biber,
            "biblatex is configured with backend=biber.",
            "biblatex is used but backend=biber is not explicitly declared in the style.",
        )

    return checks


def write_report(checks: list[Check]) -> None:
    timestamp = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    pass_count = sum(1 for c in checks if c.status == "PASS")
    warn_count = sum(1 for c in checks if c.status == "WARN")
    fail_count = sum(1 for c in checks if c.status == "FAIL")

    by_area: dict[str, list[Check]] = {}
    for check in checks:
        by_area.setdefault(check.area, []).append(check)

    def area_ok(area: str) -> bool:
        return all(c.status == "PASS" for c in by_area.get(area, [])) and bool(by_area.get(area))

    def mark(value: bool) -> str:
        return "x" if value else " "

    unresolved = [c for c in checks if c.status in {"WARN", "FAIL"}]

    lines: list[str] = []
    lines.append("# arXiv Packaging Validation Report")
    lines.append("")
    lines.append(f"Generated at: `{timestamp}`")
    lines.append("")
    lines.append("## Executive Summary")
    lines.append("")
    lines.append(f"- Total checks: **{len(checks)}**")
    lines.append(f"- Pass: **{pass_count}**")
    lines.append(f"- Warn: **{warn_count}**")
    lines.append(f"- Fail: **{fail_count}**")
    lines.append("")
    if fail_count == 0 and warn_count == 0:
        lines.append("Overall result: ✅ **arXiv upload-ready**")
    elif fail_count == 0:
        lines.append("Overall result: ⚠️ **Conditionally ready** (non-failing issues remain)")
    else:
        lines.append("Overall result: ❌ **Not arXiv upload-ready**")
    lines.append("")

    lines.append("## Goal Checklist")
    lines.append("")
    lines.append(f"- [{mark(area_ok('Manifest'))}] Validate arXiv manifest (00README.json)")
    lines.append(f"- [{mark(area_ok('Source declarations'))}] Validate source declarations")
    lines.append(f"- [{mark(area_ok('Upload structure'))}] Validate upload structure")
    lines.append(f"- [{mark(area_ok('Figure compatibility'))}] Validate figure format compatibility")
    lines.append(f"- [{mark(area_ok('Bibliography'))}] Validate bibliography compatibility")
    lines.append("")

    lines.append("## Detailed Checks")
    lines.append("")
    for area in sorted(by_area):
        lines.append(f"### {area}")
        lines.append("")
        lines.append("| Check | Result | Details |")
        lines.append("| --- | --- | --- |")
        for check in by_area[area]:
            icon = "✅" if check.status == "PASS" else "⚠️" if check.status == "WARN" else "❌"
            lines.append(f"| {check.name} | {icon} {check.status} | {check.details} |")
        lines.append("")

    lines.append("## arXiv Upload Checklist")
    lines.append("")
    lines.append(f"- [{mark(area_ok('Manifest'))}] 00README.json is valid and complete")
    lines.append(f"- [{mark(area_ok('Source declarations'))}] All sources declared, present, and arXiv-safe")
    lines.append(f"- [{mark(area_ok('Upload structure'))}] Upload bundle is clean (no symlinks, no artifacts, no system files)")
    lines.append(f"- [{mark(area_ok('Figure compatibility'))}] All figures are in arXiv-compatible formats and within size limits")
    lines.append(f"- [{mark(area_ok('Bibliography'))}] Bibliography compilation path is arXiv-compatible")
    lines.append("")

    if unresolved:
        lines.append("## Unresolved Issues")
        lines.append("")
        for check in unresolved:
            icon = "⚠️" if check.status == "WARN" else "❌"
            lines.append(f"- {icon} **{check.area} / {check.name}**: {check.details}")
        lines.append("")

    AUDIT_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    AUDIT_OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    checks = gather_checks()
    write_report(checks)
    fail_count = sum(1 for c in checks if c.status == "FAIL")
    warn_count = sum(1 for c in checks if c.status == "WARN")
    print(f"[validate-arxiv-packaging] report written to {AUDIT_OUTPUT}")
    print(f"[validate-arxiv-packaging] pass={sum(1 for c in checks if c.status == 'PASS')} warn={warn_count} fail={fail_count}")
    return 1 if fail_count > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
