#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from collections.abc import Iterable
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
AUDIT_OUTPUT = REPO_ROOT / "audits" / "publication-readiness.md"

SUPPORTED_IMAGE_EXTENSIONS = {".png", ".pdf", ".jpg", ".jpeg", ".eps"}
# Empty suffix is allowed for directories declared as include sources (e.g. `sections/`).
SUPPORTED_SOURCE_EXTENSIONS = {".tex", ".bib", ".sty", ".png", ".pdf", ".jpg", ".jpeg", ".eps", ""}
ALLOWED_SOURCE_USAGES = {"toplevel", "include", "ignore"}
HERO_DIMENSIONS = (1920, 1080)
FIGURE_DIMENSIONS = (1600, 900)
REQUIRED_PROMPT_HEADINGS = {
    # Keep headings lowercase; parse_markdown_headings normalizes observed headings to lowercase.
    "prompt history",
    "generation context",
    "synchronization notes",
    "rendering rationale",
    "recursive checkpoints",
}


def add_check(checks: list[Check], area: str, name: str, condition: bool, pass_details: str, fail_details: str) -> None:
    checks.append(
        Check(
            area=area,
            name=name,
            status="PASS" if condition else "FAIL",
            details=pass_details if condition else fail_details,
        )
    )


def run_cmd(command: list[str], cwd: Path) -> tuple[int, str]:
    proc = subprocess.run(command, cwd=cwd, capture_output=True, text=True, check=False)
    output = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode, output.strip()


def parse_bib_keys(bib_text: str) -> set[str]:
    return set(re.findall(r"@\w+\{([^,]+),", bib_text))


def parse_bib_entries(bib_text: str) -> tuple[list[tuple[str, dict[str, str]]], list[str]]:
    entries: list[tuple[str, dict[str, str]]] = []
    parse_errors: list[str] = []
    current_key: str | None = None
    current_fields: dict[str, str] = {}
    in_entry = False
    current_field_name: str | None = None
    current_field_parts: list[str] = []
    current_field_brace_depth = 0

    for line in bib_text.splitlines():
        start_match = re.match(r"^@\w+\{([^,]+),\s*$", line.strip())
        if start_match:
            current_key = start_match.group(1).strip()
            current_fields = {}
            in_entry = True
            continue

        if in_entry and current_field_name is not None:
            current_field_parts.append(line.strip())
            current_field_brace_depth += line.count("{") - line.count("}")
            if current_field_brace_depth == 0:
                raw_value = " ".join(part for part in current_field_parts if part).strip()
                value = re.sub(r"\}\s*,?\s*$", "", raw_value).strip()
                current_fields[current_field_name] = value
                current_field_name = None
                current_field_parts = []
                current_field_brace_depth = 0
            elif current_field_brace_depth < 0:
                if current_key:
                    parse_errors.append(current_key)
                current_field_name = None
                current_field_parts = []
                current_field_brace_depth = 0
            continue

        if in_entry and line.strip() == "}":
            if current_key:
                entries.append((current_key, current_fields))
            current_key = None
            current_fields = {}
            in_entry = False
            continue

        if not in_entry:
            continue

        field_match = re.match(r"^\s*([a-zA-Z][\w-]*)\s*=\s*\{(.*)$", line)
        if not field_match:
            continue
        field_name = field_match.group(1).strip().lower()
        remainder = field_match.group(2).strip()
        brace_depth = 1 + remainder.count("{") - remainder.count("}")
        if brace_depth == 0:
            current_fields[field_name] = re.sub(r"\}\s*,?\s*$", "", remainder).strip()
            continue
        if brace_depth < 0:
            if current_key:
                parse_errors.append(current_key)
            continue
        current_field_name = field_name
        current_field_parts = [remainder]
        current_field_brace_depth = brace_depth

    if current_field_name is not None and current_key:
        parse_errors.append(current_key)

    return entries, sorted(set(parse_errors))


def parse_citation_keys(tex_text: str) -> set[str]:
    pattern = re.compile(r"\\(?:auto|text|paren)?cite\*?(?:\[[^\]]*\])?\{([^}]+)\}")
    keys: set[str] = set()
    for block in pattern.findall(tex_text):
        for key in block.split(","):
            clean = key.strip()
            if clean:
                keys.add(clean)
    return keys


def find_graphics_paths(tex_text: str) -> list[str]:
    pattern = re.compile(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}")
    return [match.strip() for match in pattern.findall(tex_text)]


def resolve_figure_path(raw: str) -> Path | None:
    search_roots = [PAPER_DIR, PAPER_DIR / "figures"]
    for root in search_roots:
        candidate = root / raw
        if candidate.suffix and candidate.exists():
            return candidate
        for ext in SUPPORTED_IMAGE_EXTENSIONS:
            with_ext = candidate.with_suffix(ext)
            if with_ext.exists():
                return with_ext
    return None


def parse_figure_manifest_entries(path: Path) -> set[str]:
    if not path.exists():
        return set()
    names: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        for entry in re.findall(r"`([^`]+\.(?:png|pdf|jpg|jpeg|eps))`", line, flags=re.IGNORECASE):
            names.add(Path(entry).name)
    return names


def expected_png_dimensions(filename: str) -> tuple[int, int] | None:
    if filename == "hero.png":
        return HERO_DIMENSIONS
    if re.fullmatch(r"figure\d+\.png", filename):
        return FIGURE_DIMENSIONS
    return None


def read_png_dimensions(path: Path) -> tuple[int, int] | None:
    try:
        with path.open("rb") as handle:
            # PNG file signature: 8 fixed bytes.
            signature = handle.read(8)
            if signature != b"\x89PNG\r\n\x1a\n":
                return None
            # First chunk header: 4-byte length + 4-byte chunk type.
            ihdr_length = handle.read(4)
            ihdr_type = handle.read(4)
            if len(ihdr_length) != 4 or ihdr_type != b"IHDR":
                return None
            if int.from_bytes(ihdr_length, byteorder="big") != 13:
                return None
            # IHDR data payload is always 13 bytes in PNG.
            ihdr_data = handle.read(13)
            if len(ihdr_data) != 13:
                return None
            width = int.from_bytes(ihdr_data[0:4], byteorder="big")
            height = int.from_bytes(ihdr_data[4:8], byteorder="big")
            return (width, height)
    except OSError:
        return None


def parse_markdown_headings(path: Path) -> set[str]:
    if not path.exists():
        return set()
    headings: set[str] = set()
    try:
        content = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return set()
    for line in content.splitlines():
        match = re.match(r"^##\s+(.+)$", line)
        if match:
            headings.add(match.group(1).strip().lower())
    return headings


def build_prompt_path(filename: str) -> Path:
    return PAPER_DIR / "figures" / "prompts" / f"{Path(filename).stem}.prompt.md"


def sorted_unique(values: Iterable[str]) -> list[str]:
    return sorted(set(values))


def extract_figure_blocks(tex_text: str) -> list[str]:
    return re.findall(r"\\begin\{figure\*?\}.*?\\end\{figure\*?\}", tex_text, flags=re.DOTALL)


def gather_checks() -> list[Check]:
    checks: list[Check] = []

    # Publication structure / repository coherence
    required_paths = [
        REPO_ROOT / "paper" / "paper.tex",
        REPO_ROOT / "paper" / "references.bib",
        REPO_ROOT / "paper" / "00README.json",
        REPO_ROOT / "paper" / "figures" / "manifest.md",
        REPO_ROOT / "paper" / "figures" / "prompts" / "README.md",
        REPO_ROOT / "scripts" / "build-paper.sh",
        REPO_ROOT / "scripts" / "validate-metadata.py",
        REPO_ROOT / ".latexmkrc",
        REPO_ROOT / ".github" / "workflows" / "pages.yml",
        REPO_ROOT / "docs" / "index.html",
        REPO_ROOT / "specs" / "publication" / "publication-manifest.spec.md",
        REPO_ROOT / "specs" / "publication" / "arxiv-publication.spec.md",
        REPO_ROOT / "specs" / "publication" / "publication-workflow.spec.md",
        REPO_ROOT / "publication.json",
        REPO_ROOT / "CITATION.cff",
        # Canonical metadata layer
        REPO_ROOT / "metadata" / "publication.yaml",
        REPO_ROOT / "metadata" / "repository.yaml",
        REPO_ROOT / "metadata" / "authors.yaml",
        REPO_ROOT / "metadata" / "citations.yaml",
        REPO_ROOT / "metadata" / "renderers.yaml",
    ]
    missing = [str(path.relative_to(REPO_ROOT)) for path in required_paths if not path.exists()]
    add_check(
        checks,
        "Publication structure",
        "Required publication files",
        not missing,
        "All required publication and workflow files are present.",
        "Missing required files: " + ", ".join(missing),
    )

    # arXiv compatibility
    readme_json_path = PAPER_DIR / "00README.json"
    try:
        readme_json = json.loads(readme_json_path.read_text(encoding="utf-8"))
        readme_json_ok = True
    except (FileNotFoundError, json.JSONDecodeError):
        readme_json = {}
        readme_json_ok = False

    add_check(
        checks,
        "arXiv compatibility",
        "00README.json is parseable JSON",
        readme_json_ok,
        "paper/00README.json is valid JSON.",
        "paper/00README.json is missing or invalid JSON.",
    )

    schema_ok = str(readme_json.get("$schema", "")).startswith("https://arxiv.org/schemas/00readme/")
    add_check(
        checks,
        "arXiv compatibility",
        "00README schema points to arXiv",
        schema_ok,
        "00README schema matches arXiv 00readme schema URL.",
        "00README schema does not point to an arXiv 00readme schema URL.",
    )

    required_readme_keys = {"manifest_version", "publication", "process", "sources", "build"}
    missing_readme_keys = sorted(required_readme_keys - set(readme_json.keys()))
    add_check(
        checks,
        "arXiv compatibility",
        "00README required root keys",
        not missing_readme_keys,
        "00README includes required manifest root keys.",
        "00README is missing keys: " + ", ".join(missing_readme_keys),
    )

    sources = readme_json.get("sources", []) if isinstance(readme_json.get("sources", []), list) else []
    invalid_source_usages: list[str] = []
    missing_sources: list[str] = []
    unsupported_source_types: list[str] = []
    toplevel_sources = 0

    for source in sources:
        if not isinstance(source, dict):
            continue
        path_value = str(source.get("path", "")).strip()
        usage = str(source.get("usage", "")).strip()
        if usage not in ALLOWED_SOURCE_USAGES:
            invalid_source_usages.append(f"{path_value} ({usage})")
        full_path = PAPER_DIR / path_value
        if not full_path.exists():
            missing_sources.append(path_value)
        if full_path.suffix.lower() not in SUPPORTED_SOURCE_EXTENSIONS:
            unsupported_source_types.append(path_value)
        if usage == "toplevel":
            toplevel_sources += 1

    add_check(
        checks,
        "arXiv compatibility",
        "Source usage values are supported",
        not invalid_source_usages,
        "All declared source usage values are supported.",
        "Unsupported source usage values: " + ", ".join(invalid_source_usages),
    )
    add_check(
        checks,
        "arXiv compatibility",
        "Declared sources exist",
        not missing_sources,
        "All sources listed in 00README exist under paper/.",
        "Missing 00README sources: " + ", ".join(missing_sources),
    )
    add_check(
        checks,
        "arXiv compatibility",
        "Declared source file types are upload-safe",
        not unsupported_source_types,
        "Declared source file extensions are arXiv-safe.",
        "Unsupported source file types in 00README: " + ", ".join(unsupported_source_types),
    )
    add_check(
        checks,
        "arXiv compatibility",
        "Single toplevel source declared",
        toplevel_sources == 1,
        "Exactly one toplevel source is declared in 00README.",
        f"Expected 1 toplevel source, found {toplevel_sources}.",
    )

    # Bibliography integrity
    section_tex_files = sorted((PAPER_DIR / "sections").glob("*.tex"))
    add_check(
        checks,
        "Publication structure",
        "Section source files exist",
        bool(section_tex_files),
        f"Found {len(section_tex_files)} section .tex files under paper/sections.",
        "No .tex files found under paper/sections.",
    )

    tex_text = "\n".join(path.read_text(encoding="utf-8") for path in section_tex_files)
    tex_text += "\n" + (PAPER_DIR / "paper.tex").read_text(encoding="utf-8")
    bib_text = (PAPER_DIR / "references.bib").read_text(encoding="utf-8")

    citation_keys = parse_citation_keys(tex_text)
    bibliography_keys = parse_bib_keys(bib_text)
    bibliography_entries, bib_parse_errors = parse_bib_entries(bib_text)
    missing_bib_entries = sorted(citation_keys - bibliography_keys)
    duplicate_bib_entries = sorted(
        key
        for key in bibliography_keys
        if len(re.findall(rf"@\w+\{{{re.escape(key)},", bib_text)) > 1
    )
    entries_missing_core_fields = sorted(
        key for key, fields in bibliography_entries if "author" not in fields or "title" not in fields
    )
    malformed_doi_entries: list[str] = []
    noncanonical_doi_url_entries: list[str] = []
    noncanonical_arxiv_entries: list[str] = []

    for key, fields in bibliography_entries:
        doi = fields.get("doi")
        url = fields.get("url") or ""
        if doi:
            if doi.lower().startswith(("http://", "https://", "doi:")):
                malformed_doi_entries.append(key)
            expected_url = f"https://doi.org/{doi}"
            if url and url != expected_url:
                noncanonical_doi_url_entries.append(key)

        eprinttype = fields.get("eprinttype", "")
        eprint = fields.get("eprint", "")
        if eprinttype or "arxiv.org/abs/" in url:
            if eprinttype != "arxiv":
                noncanonical_arxiv_entries.append(key)
            elif not eprint or (url and url != f"https://arxiv.org/abs/{eprint}"):
                noncanonical_arxiv_entries.append(key)

    add_check(
        checks,
        "Bibliography integrity",
        "All citation keys resolve to bibliography entries",
        not missing_bib_entries,
        f"All {len(citation_keys)} citation keys resolve in references.bib.",
        "Missing bibliography entries for citation keys: " + ", ".join(missing_bib_entries),
    )
    add_check(
        checks,
        "Bibliography integrity",
        "Bibliography keys are unique",
        not duplicate_bib_entries,
        f"All {len(bibliography_keys)} bibliography keys are unique.",
        "Duplicate bibliography keys found: " + ", ".join(duplicate_bib_entries),
    )
    add_check(
        checks,
        "Bibliography integrity",
        "Bibliography entries include core metadata",
        not entries_missing_core_fields,
        "All bibliography entries contain at least author and title fields.",
        "Bibliography entries missing core fields: " + ", ".join(entries_missing_core_fields),
    )
    add_check(
        checks,
        "Bibliography integrity",
        "Bibliography entry structure is parseable",
        not bib_parse_errors,
        "All bibliography entries have parseable field structure.",
        "Malformed bibliography field structure found in entries: " + ", ".join(bib_parse_errors),
    )
    add_check(
        checks,
        "Bibliography integrity",
        "DOI fields use canonical BibLaTeX value format",
        not malformed_doi_entries,
        "All DOI fields use canonical DOI values (no URL/doi: prefixes).",
        "Malformed DOI values (URL/doi: prefix) found in entries: " + ", ".join(malformed_doi_entries),
    )
    add_check(
        checks,
        "Bibliography integrity",
        "DOI URLs match DOI field values",
        not noncanonical_doi_url_entries,
        "All DOI URLs resolve to the canonical https://doi.org/<doi> form.",
        "DOI URL mismatch detected in entries: " + ", ".join(noncanonical_doi_url_entries),
    )
    add_check(
        checks,
        "Bibliography integrity",
        "arXiv metadata is canonical",
        not noncanonical_arxiv_entries,
        "All arXiv entries use canonical eprinttype/eprint/url metadata.",
        "Non-canonical arXiv metadata found in entries: " + ", ".join(noncanonical_arxiv_entries),
    )

    # Figure integrity
    graphics_paths = find_graphics_paths(tex_text)
    missing_graphics: list[str] = []
    unsupported_graphics: list[str] = []
    referenced_figure_filenames: set[str] = set()

    for raw_path in graphics_paths:
        resolved = resolve_figure_path(raw_path)
        if resolved is None:
            missing_graphics.append(raw_path)
            continue
        referenced_figure_filenames.add(resolved.name)
        if resolved.suffix.lower() not in SUPPORTED_IMAGE_EXTENSIONS:
            unsupported_graphics.append(raw_path)

    add_check(
        checks,
        "Figure integrity",
        "All referenced figure files exist",
        not missing_graphics,
        f"All {len(graphics_paths)} figure references resolve to files.",
        "Missing figure files for references: " + ", ".join(missing_graphics),
    )
    add_check(
        checks,
        "Figure integrity",
        "Figure file formats are render-safe",
        not unsupported_graphics,
        "All figure files use supported render-safe image formats.",
        "Unsupported figure formats: " + ", ".join(unsupported_graphics),
    )

    missing_prompt_files: list[str] = []
    for filename in referenced_figure_filenames:
        prompt_path = build_prompt_path(filename)
        if not prompt_path.exists():
            missing_prompt_files.append(str(prompt_path.relative_to(REPO_ROOT)))
    add_check(
        checks,
        "Figure integrity",
        "Referenced figures have prompt-preservation files",
        not missing_prompt_files,
        "All referenced figures have prompt files in paper/figures/prompts/.",
        "Missing figure prompt files: " + ", ".join(sorted_unique(missing_prompt_files)),
    )

    incomplete_prompt_files: list[str] = []
    for filename in referenced_figure_filenames:
        prompt_path = build_prompt_path(filename)
        if not prompt_path.exists():
            continue
        headings = parse_markdown_headings(prompt_path)
        if not REQUIRED_PROMPT_HEADINGS.issubset(headings):
            missing_headings = sorted(REQUIRED_PROMPT_HEADINGS - headings)
            incomplete_prompt_files.append(
                f"{prompt_path.relative_to(REPO_ROOT)} (missing: {', '.join(missing_headings)})"
            )

    add_check(
        checks,
        "Figure integrity",
        "Prompt files include recursive metadata headings",
        not incomplete_prompt_files,
        "All figure prompt files contain required recursive-metadata headings.",
        "Prompt files with missing headings: " + ", ".join(sorted_unique(incomplete_prompt_files)),
    )

    noncanonical_png_dimensions: list[str] = []
    for raw_path in graphics_paths:
        resolved = resolve_figure_path(raw_path)
        if resolved is None or resolved.suffix.lower() != ".png":
            continue
        expected_dimensions = expected_png_dimensions(resolved.name)
        if expected_dimensions is None:
            continue
        actual_dimensions = read_png_dimensions(resolved)
        if actual_dimensions is None:
            noncanonical_png_dimensions.append(f"{resolved.name} (unreadable PNG header)")
            continue
        if actual_dimensions != expected_dimensions:
            noncanonical_png_dimensions.append(
                f"{resolved.name} ({actual_dimensions[0]}x{actual_dimensions[1]} != {expected_dimensions[0]}x{expected_dimensions[1]})"
            )

    add_check(
        checks,
        "Figure integrity",
        "Referenced PNG dimensions are canonical",
        not noncanonical_png_dimensions,
        "All referenced PNG figures match canonical dimensions.",
        "Referenced PNGs with non-canonical dimensions: " + ", ".join(sorted_unique(noncanonical_png_dimensions)),
    )

    figure_blocks = extract_figure_blocks(tex_text)
    figure_blocks_missing_caption = [idx + 1 for idx, block in enumerate(figure_blocks) if "\\caption{" not in block]
    figure_blocks_missing_label = [idx + 1 for idx, block in enumerate(figure_blocks) if "\\label{fig:" not in block]

    add_check(
        checks,
        "Figure integrity",
        "Figure blocks include captions",
        not figure_blocks_missing_caption,
        f"All {len(figure_blocks)} figure blocks include captions.",
        "Figure blocks missing captions: " + ", ".join(str(value) for value in figure_blocks_missing_caption),
    )
    add_check(
        checks,
        "Figure integrity",
        "Figure blocks include fig: labels",
        not figure_blocks_missing_label,
        f"All {len(figure_blocks)} figure blocks include fig: labels.",
        "Figure blocks missing fig: labels: " + ", ".join(str(value) for value in figure_blocks_missing_label),
    )

    manifest_entries = parse_figure_manifest_entries(PAPER_DIR / "figures" / "manifest.md")
    missing_manifest_entries = sorted(referenced_figure_filenames - manifest_entries)
    add_check(
        checks,
        "Figure integrity",
        "Referenced figures are listed in figures/manifest.md",
        not missing_manifest_entries,
        "All referenced figures are represented in figures/manifest.md.",
        "Referenced figures missing from manifest: " + ", ".join(missing_manifest_entries),
    )

    # GitHub Pages deployment integrity
    pages_workflow_path = REPO_ROOT / ".github" / "workflows" / "pages.yml"
    pages_workflow_text = pages_workflow_path.read_text(encoding="utf-8")
    docs_index_text = (REPO_ROOT / "docs" / "index.html").read_text(encoding="utf-8")

    add_check(
        checks,
        "GitHub Pages deployment",
        "Pages workflow deploys publication artifacts",
        all(
            token in pages_workflow_text
            for token in (
                "Build reflector PDF",
                "Synchronize publication assets into docs",
                "Verify publication synchronization",
                "Deploy GitHub Pages",
                "docs/publication.json",
                "docs/reflector.pdf",
            )
        ),
        "Pages workflow includes build, synchronization, verification, and deploy steps.",
        "Pages workflow is missing one or more expected publication deployment steps.",
    )

    add_check(
        checks,
        "GitHub Pages deployment",
        "docs landing page links publication artifacts",
        all(
            token in docs_index_text
            for token in (
                "./reflector.pdf",
                "./publication.json",
                "./figures/hero.png",
                "Abstract preview",
                "Read online",
            )
        ),
        "docs/index.html links canonical publication artifacts.",
        "docs/index.html is missing one or more publication artifact links.",
    )

    # Metadata consistency
    metadata_exit, metadata_output = run_cmd([sys.executable, "scripts/validate-metadata.py"], REPO_ROOT)
    add_check(
        checks,
        "Metadata consistency",
        "Cross-file metadata validation",
        metadata_exit == 0,
        "scripts/validate-metadata.py passed.",
        "scripts/validate-metadata.py failed: " + (metadata_output or "(no output)"),
    )

    # Deterministic builds / LaTeX structure
    latexmkrc_text = (REPO_ROOT / ".latexmkrc").read_text(encoding="utf-8")
    build_script_text = (REPO_ROOT / "scripts" / "build-paper.sh").read_text(encoding="utf-8")

    add_check(
        checks,
        "Deterministic builds",
        "Build configuration declares deterministic controls",
        all(token in latexmkrc_text for token in ("$max_repeat = 10", "$force_mode = 1", "$out_dir = \".cache/out\"", "$aux_dir = \".cache/aux\"")),
        ".latexmkrc declares deterministic max repeat and fixed output/aux directories.",
        ".latexmkrc is missing one or more deterministic build controls.",
    )
    add_check(
        checks,
        "Deterministic builds",
        "Build script uses repository orchestration",
        "latexmkrc_file" in build_script_text and "-r \"${latexmkrc_file}\"" in build_script_text,
        "scripts/build-paper.sh invokes the root .latexmkrc orchestration config.",
        "scripts/build-paper.sh does not appear to invoke the configured latexmkrc_file.",
    )

    if shutil.which("latexmk"):
        code, output = run_cmd(["./scripts/build-paper.sh", "paper"], REPO_ROOT)
        add_check(
            checks,
            "LaTeX and build validation",
            "Paper compiles cleanly",
            code == 0,
            "./scripts/build-paper.sh paper succeeded.",
            "./scripts/build-paper.sh paper failed: " + (output or "(no output)"),
        )
    else:
        checks.append(
            Check(
                area="LaTeX and build validation",
                name="Paper compiles cleanly",
                status="WARN",
                details="latexmk is not installed in this environment; local compile check is blocked.",
            )
        )

    return checks


def write_report(checks: list[Check]) -> None:
    timestamp = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    pass_count = sum(1 for check in checks if check.status == "PASS")
    warn_count = sum(1 for check in checks if check.status == "WARN")
    fail_count = sum(1 for check in checks if check.status == "FAIL")

    by_area: dict[str, list[Check]] = {}
    for check in checks:
        by_area.setdefault(check.area, []).append(check)

    def area_ok(area: str) -> bool:
        return all(item.status == "PASS" for item in by_area.get(area, [])) and bool(by_area.get(area))

    def mark(value: bool) -> str:
        return "x" if value else " "

    unresolved = [check for check in checks if check.status in {"WARN", "FAIL"}]

    lines: list[str] = []
    lines.append("# Publication Readiness Audit Report")
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
        lines.append("Overall result: ✅ **Publication-ready**")
    elif fail_count == 0:
        lines.append("Overall result: ⚠️ **Conditionally ready** (non-failing blockers remain)")
    else:
        lines.append("Overall result: ❌ **Not publication-ready**")
    lines.append("")

    lines.append("## Goal Checklist")
    lines.append("")
    lines.append(f"- [{mark(area_ok('arXiv compatibility'))}] Validate arXiv compatibility")
    lines.append(f"- [{mark(area_ok('Publication structure'))}] Validate publication structure")
    lines.append(f"- [{mark(area_ok('Bibliography integrity'))}] Validate bibliography integrity")
    lines.append(f"- [{mark(area_ok('Figure integrity'))}] Validate figure references")
    lines.append(f"- [{mark(area_ok('GitHub Pages deployment'))}] Validate GitHub Pages deployment")
    lines.append(f"- [{mark(area_ok('Metadata consistency'))}] Validate metadata consistency")
    lines.append(f"- [{mark(area_ok('Deterministic builds') and area_ok('LaTeX and build validation'))}] Validate deterministic builds")
    lines.append("- [x] Generate publication readiness report")
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

    lines.append("## arXiv Compatibility Report")
    lines.append("")
    arxiv_checks = by_area.get("arXiv compatibility", [])
    if arxiv_checks:
        for check in arxiv_checks:
            icon = "✅" if check.status == "PASS" else "⚠️" if check.status == "WARN" else "❌"
            lines.append(f"- {icon} **{check.name}** — {check.details}")
    else:
        lines.append("- ⚠️ No arXiv checks were executed.")
    lines.append("")

    lines.append("## Unresolved Issues")
    lines.append("")
    if unresolved:
        for check in unresolved:
            lines.append(f"- {check.status}: {check.area} — {check.name}: {check.details}")
    else:
        lines.append("- None.")
    lines.append("")

    lines.append("## Recommended Fixes")
    lines.append("")
    if unresolved:
        for check in unresolved:
            if "latexmk is not installed" in check.details:
                lines.append("- Install `latexmk` + TeX Live toolchain locally/CI and rerun `./scripts/build-paper.sh paper` to close build reproducibility confidence.")
            else:
                lines.append(f"- Resolve: **{check.area} / {check.name}**.")
    else:
        lines.append("- No fixes required.")
    lines.append("")

    lines.append("## Final Publication Checklist")
    lines.append("")
    lines.append(f"- [{mark(fail_count == 0 and warn_count == 0)}] Paper deemed structurally publication-ready")
    lines.append(f"- [{mark(area_ok('arXiv compatibility'))}] arXiv compatibility verified")
    lines.append("- [x] unresolved publication blockers identified")
    lines.append(f"- [{mark(area_ok('Deterministic builds') and area_ok('LaTeX and build validation'))}] deterministic build confidence improved")
    lines.append(f"- [{mark(area_ok('Publication structure'))}] repository publication architecture validated")
    lines.append("")

    AUDIT_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    AUDIT_OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    checks = gather_checks()
    write_report(checks)
    print(f"[audit] publication readiness report written to {AUDIT_OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
