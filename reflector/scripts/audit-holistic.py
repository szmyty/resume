#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0
"""audit-holistic.py — Final holistic publication and recursive synchronization audit.

Evaluates the reflector repository holistically as:
- a publication artifact
- a recursive synchronization system
- a specification-driven workflow environment
- a reusable publication architecture
- a mixed-initiative orchestration system

Covers six audit dimensions:
1. Publication Quality
2. Recursive Synchronization Integrity
3. Repository Architecture
4. Publication Infrastructure
5. Build and Reproducibility
6. Cognitive and Architectural Coherence

Output: audits/audit-<ISO-8601-timestamp>.md
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Check:
    dimension: str
    area: str
    name: str
    status: str  # PASS | WARN | FAIL
    details: str


@dataclass
class AuditState:
    checks: list[Check] = field(default_factory=list)

    def add(
        self,
        dimension: str,
        area: str,
        name: str,
        condition: bool,
        pass_details: str,
        fail_details: str,
        warn: bool = False,
    ) -> None:
        if condition:
            status, details = "PASS", pass_details
        else:
            status = "WARN" if warn else "FAIL"
            details = fail_details
        self.checks.append(Check(dimension=dimension, area=area, name=name, status=status, details=details))

    def warn(self, dimension: str, area: str, name: str, details: str) -> None:
        self.checks.append(Check(dimension=dimension, area=area, name=name, status="WARN", details=details))

    def pass_(self, dimension: str, area: str, name: str, details: str) -> None:
        self.checks.append(Check(dimension=dimension, area=area, name=name, status="PASS", details=details))

    def fail(self, dimension: str, area: str, name: str, details: str) -> None:
        self.checks.append(Check(dimension=dimension, area=area, name=name, status="FAIL", details=details))


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
PAPER_DIR = REPO_ROOT / "paper"
SECTIONS_DIR = PAPER_DIR / "sections"
FIGURES_DIR = PAPER_DIR / "figures"
METADATA_DIR = REPO_ROOT / "metadata"
SPECS_DIR = REPO_ROOT / "specs"
REFLECTOR_PKG = REPO_ROOT / "reflector"
AUDITS_DIR = REPO_ROOT / "audits"
WORKFLOWS_DIR = REPO_ROOT / ".github" / "workflows"

SUPPORTED_IMAGE_EXTENSIONS = {".png", ".pdf", ".jpg", ".jpeg", ".eps"}
FIGURE_DIMENSIONS = (1600, 900)
HERO_DIMENSIONS = (1920, 1080)

REQUIRED_SECTION_FILES = {
    "abstract.tex",
    "introduction.tex",
    "recursive_drift.tex",
    "synchronization.tex",
    "reflective_auditing.tex",
    "milestone_execution.tex",
    "reflector_framework.tex",
    "operational_demonstration.tex",
    "limitations.tex",
    "conclusion.tex",
}

# Minimum word count threshold for a section to be considered non-stub.
SECTION_WORD_THRESHOLD = 100

# Ordered section progression for conceptual coherence check.
EXPECTED_SECTION_ORDER = [
    "abstract.tex",
    "introduction.tex",
    "recursive_drift.tex",
    "synchronization.tex",
    "reflective_auditing.tex",
    "milestone_execution.tex",
    "reflector_framework.tex",
    "operational_demonstration.tex",
    "limitations.tex",
    "related_work.tex",
    "conclusion.tex",
]

REQUIRED_PROMPT_HEADINGS = {
    "prompt history",
    "generation context",
    "synchronization notes",
    "rendering rationale",
    "recursive checkpoints",
}

REQUIRED_METADATA_FILES = {
    "publication.yaml",
    "repository.yaml",
    "authors.yaml",
    "citations.yaml",
    "renderers.yaml",
}

REQUIRED_SPEC_PATHS = {
    "publication/publication-manifest.spec.md",
    "publication/publication-workflow.spec.md",
    "publication/semantic-content.spec.md",
    "publication/renderer-architecture.spec.md",
    "publication/arxiv-publication.spec.md",
    "synchronization/synchronization-layer.spec.md",
}

REQUIRED_REFLECTOR_MODULES = {
    "audits/__init__.py",
    "audits/pipeline.py",
    "cli/__init__.py",
    "cli/main.py",
    "schemas/__init__.py",
    "synchronization/__init__.py",
    "orchestration/__init__.py",
    "workflows/__init__.py",
}

REQUIRED_WORKFLOWS = {
    "build-paper.yml",
    "pages.yml",
    "publication.yml",
    "release-paper.yml",
    "release-please.yml",
    "commitlint.yml",
}

CANONICAL_TITLE_TEXT = "reflective synchronization systems for recursive ai-assisted software engineering"

# Pattern that identifies canonically numbered figure PNG files (figure1.png … figureN.png).
FIGURE_NAME_PATTERN = re.compile(r"^figure\d+\.png$")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return None


def load_json(path: Path) -> dict | None:
    text = read_text(path)
    if text is None:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None


def run_cmd(command: list[str], cwd: Path | None = None) -> tuple[int, str]:
    proc = subprocess.run(
        command,
        cwd=cwd or REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return proc.returncode, ((proc.stdout or "") + (proc.stderr or "")).strip()


def count_words_in_tex(tex_text: str) -> int:
    """Count non-comment, non-blank, non-command tokens in a TeX file."""
    lines = []
    for line in tex_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("%"):
            continue
        # Remove inline comments.
        line_no_comment = re.sub(r"(?<!\\)%.*", "", stripped)
        lines.append(line_no_comment)
    body = " ".join(lines)
    # Remove LaTeX commands and braces, count remaining words.
    body = re.sub(r"\\[a-zA-Z]+\*?\s*(\[[^\]]*\])?\s*\{[^}]*\}", " ", body)
    body = re.sub(r"\\[a-zA-Z]+\*?", " ", body)
    body = re.sub(r"[{}]", " ", body)
    words = body.split()
    return len(words)


def read_png_dimensions(path: Path) -> tuple[int, int] | None:
    try:
        with path.open("rb") as handle:
            signature = handle.read(8)
            if signature != b"\x89PNG\r\n\x1a\n":
                return None
            handle.read(4)  # chunk length
            ihdr_type = handle.read(4)
            if ihdr_type != b"IHDR":
                return None
            ihdr_data = handle.read(13)
            if len(ihdr_data) != 13:
                return None
            width = int.from_bytes(ihdr_data[0:4], byteorder="big")
            height = int.from_bytes(ihdr_data[4:8], byteorder="big")
            return width, height
    except OSError:
        return None


def parse_markdown_headings(md_text: str) -> set[str]:
    headings: set[str] = set()
    for line in md_text.splitlines():
        m = re.match(r"^#{1,6}\s+(.+)$", line.strip())
        if m:
            headings.add(m.group(1).strip().lower())
    return headings


def find_tex_graphics(tex_text: str) -> list[str]:
    return re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", tex_text)


def collect_all_tex_text() -> str:
    """Concatenate all section .tex files."""
    parts: list[str] = []
    if SECTIONS_DIR.exists():
        for tex_file in sorted(SECTIONS_DIR.glob("*.tex")):
            text = read_text(tex_file)
            if text:
                parts.append(text)
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Dimension 1 — Publication Quality
# ---------------------------------------------------------------------------


def audit_publication_quality(state: AuditState) -> None:
    dim = "1. Publication Quality"

    # 1a. Section completeness
    substantive_sections: list[str] = []
    stub_sections: list[str] = []
    if SECTIONS_DIR.exists():
        for tex_file in sorted(SECTIONS_DIR.glob("*.tex")):
            if tex_file.name == "README.md":
                continue
            text = read_text(tex_file) or ""
            wc = count_words_in_tex(text)
            if wc >= SECTION_WORD_THRESHOLD:
                substantive_sections.append(tex_file.name)
            else:
                stub_sections.append(tex_file.name)
    total_sections = len(substantive_sections) + len(stub_sections)
    state.add(
        dim,
        "Section completeness",
        "Core sections have substantive content",
        len(stub_sections) == 0,
        f"All {total_sections} sections have ≥{SECTION_WORD_THRESHOLD} words of content.",
        f"{len(stub_sections)}/{total_sections} sections are below word threshold: {', '.join(stub_sections[:5])}{'...' if len(stub_sections) > 5 else ''}.",
    )
    state.add(
        dim,
        "Section completeness",
        "Required sections are present",
        REQUIRED_SECTION_FILES.issubset({f.name for f in SECTIONS_DIR.glob("*.tex")}),
        f"All {len(REQUIRED_SECTION_FILES)} required section files are present.",
        f"Missing required section files: {REQUIRED_SECTION_FILES - {f.name for f in SECTIONS_DIR.glob('*.tex')}}.",
    )

    # 1b. Abstract quality
    abstract_path = SECTIONS_DIR / "abstract.tex"
    abstract_text = read_text(abstract_path) or ""
    abstract_words = count_words_in_tex(abstract_text)
    state.add(
        dim,
        "Abstract quality",
        "Abstract is substantive (≥100 words)",
        abstract_words >= 100,
        f"Abstract contains {abstract_words} words.",
        f"Abstract is too short ({abstract_words} words); expected ≥100.",
    )
    # Check for placeholder language in abstract
    abstract_has_placeholder = bool(re.search(r"\bTODO\b|\bPLACEHOLDER\b|\bFIXME\b", abstract_text, re.IGNORECASE))
    state.add(
        dim,
        "Abstract quality",
        "Abstract contains no placeholder language",
        not abstract_has_placeholder,
        "Abstract contains no TODO/PLACEHOLDER/FIXME markers.",
        "Abstract contains placeholder language (TODO/PLACEHOLDER/FIXME).",
    )

    # 1c. Bibliography quality
    bib_path = PAPER_DIR / "references.bib"
    bib_text = read_text(bib_path) or ""
    bib_keys = set(re.findall(r"@\w+\{([^,]+),", bib_text))
    placeholder_entries = [k for k in bib_keys if re.search(r"placeholder|dummy|example", k, re.IGNORECASE)]
    placeholder_notes = len(re.findall(r"note\s*=\s*\{[^}]*placeholder[^}]*\}", bib_text, re.IGNORECASE))
    state.add(
        dim,
        "Citation quality",
        "Bibliography has non-placeholder entries",
        len(bib_keys) > 0 and len(placeholder_entries) == 0 and placeholder_notes == 0,
        f"All {len(bib_keys)} bibliography entries appear substantive.",
        f"Bibliography contains {len(placeholder_entries)} placeholder keys and {placeholder_notes} placeholder note fields.",
    )
    state.add(
        dim,
        "Citation quality",
        "Bibliography entry count is adequate",
        len(bib_keys) >= 10,
        f"Bibliography contains {len(bib_keys)} entries.",
        f"Bibliography has only {len(bib_keys)} entries; ≥10 expected for publication.",
        warn=True,
    )

    # 1d. Figure captions and labels
    all_tex_text = collect_all_tex_text()
    figure_blocks = re.findall(r"\\begin\{figure\}.*?\\end\{figure\}", all_tex_text, re.DOTALL)
    figures_with_caption = [b for b in figure_blocks if r"\caption{" in b]
    figures_with_label = [b for b in figure_blocks if r"\label{fig:" in b]
    state.add(
        dim,
        "Figure quality",
        "All figure blocks include captions",
        len(figure_blocks) == len(figures_with_caption),
        f"All {len(figure_blocks)} figure blocks include captions.",
        f"{len(figure_blocks) - len(figures_with_caption)}/{len(figure_blocks)} figure blocks are missing captions.",
    )
    state.add(
        dim,
        "Figure quality",
        "All figure blocks include fig: labels",
        len(figure_blocks) == len(figures_with_label),
        f"All {len(figure_blocks)} figure blocks include fig: labels.",
        f"{len(figure_blocks) - len(figures_with_label)}/{len(figure_blocks)} figure blocks are missing fig: labels.",
    )

    # 1e. Keywords
    pub_yaml_path = METADATA_DIR / "publication.yaml"
    pub_yaml_text = read_text(pub_yaml_path) or ""
    keywords_section = re.search(r"keywords:\s*\n((?:\s+-[^\n]+\n)+)", pub_yaml_text)
    keyword_count = len(re.findall(r"^\s+-\s+", keywords_section.group(1), re.MULTILINE)) if keywords_section else 0
    state.add(
        dim,
        "Publication polish",
        "Publication keywords are declared",
        keyword_count >= 5,
        f"Publication declares {keyword_count} keywords.",
        f"Only {keyword_count} keywords declared; ≥5 expected.",
        warn=True,
    )

    # 1f. Placeholder markers in section content
    all_todo_files: list[str] = []
    if SECTIONS_DIR.exists():
        for tex_file in sorted(SECTIONS_DIR.glob("*.tex")):
            text = read_text(tex_file) or ""
            if re.search(r"\bTODO\b|\bPLACEHOLDER\b", text):
                all_todo_files.append(tex_file.name)
    state.add(
        dim,
        "Publication polish",
        "Section files contain no TODO/PLACEHOLDER markers",
        len(all_todo_files) == 0,
        "No section files contain TODO or PLACEHOLDER markers.",
        f"{len(all_todo_files)} section(s) still contain TODO/PLACEHOLDER markers: {', '.join(all_todo_files)}.",
        warn=True,
    )


# ---------------------------------------------------------------------------
# Dimension 2 — Recursive Synchronization Integrity
# ---------------------------------------------------------------------------


def audit_synchronization_integrity(state: AuditState) -> None:
    dim = "2. Recursive Synchronization Integrity"

    # 2a. Spec files exist
    missing_specs: list[str] = []
    for spec_rel in REQUIRED_SPEC_PATHS:
        if not (SPECS_DIR / spec_rel).exists():
            missing_specs.append(spec_rel)
    state.add(
        dim,
        "Specification synchronization",
        "Required specification files are present",
        len(missing_specs) == 0,
        f"All {len(REQUIRED_SPEC_PATHS)} specification files are present.",
        f"Missing specification files: {', '.join(missing_specs)}.",
    )

    # 2b. Metadata file set is complete
    missing_meta: list[str] = []
    for mf in REQUIRED_METADATA_FILES:
        if not (METADATA_DIR / mf).exists():
            missing_meta.append(mf)
    state.add(
        dim,
        "Metadata synchronization",
        "Canonical metadata layer is complete",
        len(missing_meta) == 0,
        f"All {len(REQUIRED_METADATA_FILES)} canonical metadata files are present.",
        f"Missing metadata files: {', '.join(missing_meta)}.",
    )

    # 2c. Version consistency across key files
    version_path = REPO_ROOT / "VERSION"
    manifest_path = REPO_ROOT / ".release-please-manifest.json"
    citation_path = REPO_ROOT / "CITATION.cff"
    pub_yaml_path = METADATA_DIR / "publication.yaml"

    version_file = (read_text(version_path) or "").strip()
    manifest_data = load_json(manifest_path) or {}
    manifest_version = manifest_data.get(".", "")
    citation_text = read_text(citation_path) or ""
    citation_version_match = re.search(r"^version:\s+(.+)$", citation_text, re.MULTILINE)
    citation_version = citation_version_match.group(1).strip() if citation_version_match else ""
    pub_yaml_text = read_text(pub_yaml_path) or ""
    pub_version_match = re.search(r'^version:\s+"?([^"\n]+)"?', pub_yaml_text, re.MULTILINE)
    pub_version = pub_version_match.group(1).strip() if pub_version_match else ""

    versions = {v for v in [version_file, manifest_version, citation_version, pub_version] if v}
    state.add(
        dim,
        "Metadata synchronization",
        "Version is consistent across VERSION, manifest, CITATION.cff, and metadata/publication.yaml",
        len(versions) == 1,
        f"All version declarations are consistent: {next(iter(versions))}.",
        f"Version mismatch detected: VERSION='{version_file}', manifest='{manifest_version}', CITATION.cff='{citation_version}', publication.yaml='{pub_version}'.",
    )

    # 2d. Figure manifest synchronized with actual figures
    figures_manifest_path = FIGURES_DIR / "manifest.md"
    manifest_text = read_text(figures_manifest_path) or ""
    manifest_figure_names: set[str] = set()
    for entry in re.findall(r"`([^`]+\.(?:png|pdf|jpg|jpeg|eps))`", manifest_text, flags=re.IGNORECASE):
        manifest_figure_names.add(Path(entry).name)

    actual_figure_names: set[str] = set()
    if FIGURES_DIR.exists():
        for fig_path in FIGURES_DIR.iterdir():
            if fig_path.suffix.lower() in SUPPORTED_IMAGE_EXTENSIONS:
                actual_figure_names.add(fig_path.name)

    referenced_figures = {Path(r).name if Path(r).suffix else Path(r).name for r in find_tex_graphics(collect_all_tex_text())}
    # Resolve extensions
    resolved_refs: set[str] = set()
    for ref in referenced_figures:
        if any(ref.endswith(ext) for ext in SUPPORTED_IMAGE_EXTENSIONS):
            resolved_refs.add(ref)
        else:
            for ext in SUPPORTED_IMAGE_EXTENSIONS:
                candidate = ref + ext
                if candidate in actual_figure_names:
                    resolved_refs.add(candidate)
                    break

    unlisted_figures = resolved_refs - manifest_figure_names
    state.add(
        dim,
        "Figure synchronization",
        "All referenced figures are listed in figures/manifest.md",
        len(unlisted_figures) == 0,
        f"All {len(resolved_refs)} referenced figures are listed in figures/manifest.md.",
        f"{len(unlisted_figures)} referenced figures are not listed in manifest.md: {', '.join(sorted(unlisted_figures)[:5])}.",
    )

    # 2e. Captions registry synchronized
    captions_path = FIGURES_DIR / "captions.md"
    state.add(
        dim,
        "Figure synchronization",
        "figures/captions.md exists as caption registry",
        captions_path.exists(),
        "figures/captions.md exists as canonical caption registry.",
        "figures/captions.md is missing; caption registry is not synchronized.",
        warn=True,
    )

    # 2f. Workflow consistency — workflows dir has required workflow files
    missing_workflows: list[str] = []
    for wf in REQUIRED_WORKFLOWS:
        if not (WORKFLOWS_DIR / wf).exists():
            missing_workflows.append(wf)
    state.add(
        dim,
        "Workflow consistency",
        "All required GitHub Actions workflows are present",
        len(missing_workflows) == 0,
        f"All {len(REQUIRED_WORKFLOWS)} required workflow files are present.",
        f"Missing workflow files: {', '.join(missing_workflows)}.",
    )

    # 2g. Publication manifest consistency (publication.json)
    pub_json_path = REPO_ROOT / "publication.json"
    pub_json = load_json(pub_json_path)
    state.add(
        dim,
        "Publication manifest consistency",
        "Root publication.json is valid JSON",
        pub_json is not None,
        "publication.json is valid JSON.",
        "publication.json is missing or contains invalid JSON.",
    )
    if pub_json is not None:
        state.add(
            dim,
            "Publication manifest consistency",
            "publication.json includes required keys (project, status, version)",
            all(k in pub_json for k in ("project", "status", "version")),
            "publication.json includes required project, status, and version keys.",
            f"publication.json is missing required keys. Found: {list(pub_json.keys())}.",
        )

    # 2h. Spec coverage — specs for all publication workflow stages exist
    pub_workflow_spec = SPECS_DIR / "publication" / "publication-workflow.spec.md"
    sync_layer_spec = SPECS_DIR / "synchronization" / "synchronization-layer.spec.md"
    state.add(
        dim,
        "Specification synchronization",
        "Publication workflow spec exists",
        pub_workflow_spec.exists(),
        "Publication workflow specification is present.",
        "Publication workflow specification is missing.",
    )
    state.add(
        dim,
        "Specification synchronization",
        "Synchronization layer spec exists",
        sync_layer_spec.exists(),
        "Synchronization layer specification is present.",
        "Synchronization layer specification is missing.",
    )


# ---------------------------------------------------------------------------
# Dimension 3 — Repository Architecture
# ---------------------------------------------------------------------------


def audit_repository_architecture(state: AuditState) -> None:
    dim = "3. Repository Architecture"

    # 3a. Python package structure
    missing_modules: list[str] = []
    for module_rel in REQUIRED_REFLECTOR_MODULES:
        if not (REFLECTOR_PKG / module_rel).exists():
            missing_modules.append(module_rel)
    state.add(
        dim,
        "Modularity",
        "reflector Python package has required module files",
        len(missing_modules) == 0,
        f"All {len(REQUIRED_REFLECTOR_MODULES)} required reflector/ module files are present.",
        f"Missing module files: {', '.join(missing_modules)}.",
    )

    # 3b. pyproject.toml
    pyproject_path = REPO_ROOT / "pyproject.toml"
    pyproject_text = read_text(pyproject_path) or ""
    state.add(
        dim,
        "Maintainability",
        "pyproject.toml is present",
        pyproject_path.exists(),
        "pyproject.toml is present with package configuration.",
        "pyproject.toml is missing; package is not installable.",
    )
    state.add(
        dim,
        "Maintainability",
        "pyproject.toml declares CLI entry point",
        "reflector.cli.main" in pyproject_text,
        "pyproject.toml declares reflector.cli.main:app as CLI entry point.",
        "pyproject.toml does not declare CLI entry point.",
    )

    # 3c. README.md is substantive
    readme_path = REPO_ROOT / "README.md"
    readme_text = read_text(readme_path) or ""
    readme_words = len(readme_text.split())
    state.add(
        dim,
        "Clarity",
        "README.md is substantive",
        readme_words >= 50,
        f"README.md contains {readme_words} words.",
        f"README.md is too sparse ({readme_words} words); should describe the project.",
        warn=True,
    )

    # 3d. CONTRIBUTING.md present
    contributing_path = REPO_ROOT / "CONTRIBUTING.md"
    state.add(
        dim,
        "Maintainability",
        "CONTRIBUTING.md is present",
        contributing_path.exists(),
        "CONTRIBUTING.md is present.",
        "CONTRIBUTING.md is missing.",
    )

    # 3e. Semantic/render separation — styles in paper/styles/, macros in paper/macros/
    styles_dir = PAPER_DIR / "styles"
    macros_dir = PAPER_DIR / "macros"
    config_dir = PAPER_DIR / "config"
    state.add(
        dim,
        "Semantic/render separation",
        "paper/styles/ directory exists",
        styles_dir.exists(),
        "paper/styles/ directory exists for renderer-specific style files.",
        "paper/styles/ directory is missing; semantic/render separation is broken.",
    )
    state.add(
        dim,
        "Semantic/render separation",
        "paper/macros/ directory exists",
        macros_dir.exists(),
        "paper/macros/ directory exists for reusable macro definitions.",
        "paper/macros/ directory is missing.",
    )
    state.add(
        dim,
        "Semantic/render separation",
        "paper/config/ directory exists",
        config_dir.exists(),
        "paper/config/ directory exists for publication-level configuration.",
        "paper/config/ directory is missing.",
    )

    # 3f. Synchronization infrastructure scripts
    required_scripts = [
        "audit-publication-readiness.py",
        "validate-metadata.py",
        "validate-arxiv-packaging.py",
        "validate-build-reproducibility.py",
        "build-paper.sh",
    ]
    scripts_dir = REPO_ROOT / "scripts"
    missing_scripts = [s for s in required_scripts if not (scripts_dir / s).exists()]
    state.add(
        dim,
        "Synchronization infrastructure quality",
        "Required synchronization and validation scripts are present",
        len(missing_scripts) == 0,
        f"All {len(required_scripts)} required scripts are present.",
        f"Missing scripts: {', '.join(missing_scripts)}.",
    )

    # 3g. Pre-commit configuration
    precommit_path = REPO_ROOT / ".pre-commit-config.yaml"
    state.add(
        dim,
        "Synchronization infrastructure quality",
        ".pre-commit-config.yaml is present",
        precommit_path.exists(),
        ".pre-commit-config.yaml is configured for automated quality gates.",
        ".pre-commit-config.yaml is missing; pre-commit quality gates are not configured.",
    )

    # 3h. .latexmkrc present (build orchestration)
    latexmkrc_path = REPO_ROOT / ".latexmkrc"
    state.add(
        dim,
        "Recursive workflow organization",
        "Root .latexmkrc orchestration config is present",
        latexmkrc_path.exists(),
        ".latexmkrc is present as the root LaTeX build orchestration config.",
        ".latexmkrc is missing; build orchestration config is absent.",
    )

    # 3i. ROADMAP.md present
    roadmap_path = REPO_ROOT / "ROADMAP.md"
    state.add(
        dim,
        "Clarity",
        "ROADMAP.md is present",
        roadmap_path.exists(),
        "ROADMAP.md documents phase-based development roadmap.",
        "ROADMAP.md is missing.",
    )


# ---------------------------------------------------------------------------
# Dimension 4 — Publication Infrastructure
# ---------------------------------------------------------------------------


def audit_publication_infrastructure(state: AuditState) -> None:
    dim = "4. Publication Infrastructure"

    # 4a. arXiv 00README.json
    readme_json_path = PAPER_DIR / "00README.json"
    readme_json = load_json(readme_json_path)
    state.add(
        dim,
        "arXiv compatibility",
        "paper/00README.json is present and parseable",
        readme_json is not None,
        "paper/00README.json is valid JSON.",
        "paper/00README.json is missing or invalid JSON.",
    )
    if readme_json:
        has_required_keys = all(k in readme_json for k in ("$schema", "sources", "process"))
        state.add(
            dim,
            "arXiv compatibility",
            "00README.json includes required keys ($schema, sources, process)",
            has_required_keys,
            "00README.json includes $schema, sources, and process keys.",
            f"00README.json is missing required keys. Found: {list(readme_json.keys())}.",
        )
        schema_ok = "arxiv.org" in str(readme_json.get("$schema", ""))
        state.add(
            dim,
            "arXiv compatibility",
            "00README.json $schema references arXiv",
            schema_ok,
            "00README.json $schema references arXiv schema.",
            "00README.json $schema does not reference arXiv schema.",
        )
        process = readme_json.get("process", {})
        state.add(
            dim,
            "arXiv compatibility",
            "00README.json process.deterministic is true",
            process.get("deterministic") is True,
            "00README.json process.deterministic is set to true.",
            "00README.json process.deterministic is not set to true.",
        )

    # 4b. Pages deployment
    pages_workflow = WORKFLOWS_DIR / "pages.yml"
    pages_text = read_text(pages_workflow) or ""
    state.add(
        dim,
        "Pages deployment",
        "pages.yml workflow is present",
        pages_workflow.exists(),
        "pages.yml deployment workflow is present.",
        "pages.yml is missing; GitHub Pages deployment is not configured.",
    )
    state.add(
        dim,
        "Pages deployment",
        "pages.yml includes deploy step",
        "deploy-pages" in pages_text,
        "pages.yml includes actions/deploy-pages deployment step.",
        "pages.yml does not include actions/deploy-pages deployment step.",
    )
    docs_index = REPO_ROOT / "docs" / "index.html"
    state.add(
        dim,
        "Pages deployment",
        "docs/index.html landing page exists",
        docs_index.exists(),
        "docs/index.html landing page is present.",
        "docs/index.html is missing; Pages landing page is absent.",
    )

    # 4c. Release workflow
    release_workflow = WORKFLOWS_DIR / "release-paper.yml"
    release_text = read_text(release_workflow) or ""
    state.add(
        dim,
        "Publication manifests",
        "release-paper.yml workflow is present",
        release_workflow.exists(),
        "release-paper.yml release workflow is present.",
        "release-paper.yml is missing; automated release pipeline is absent.",
    )
    state.add(
        dim,
        "Publication manifests",
        "release-paper.yml generates SHA256 checksums",
        "sha256sum" in release_text or "sha256" in release_text.lower(),
        "release-paper.yml generates SHA256 checksums for release artifacts.",
        "release-paper.yml does not appear to generate SHA256 checksums.",
        warn=True,
    )

    # 4d. Renderer architecture — styles/reflector.sty
    sty_path = PAPER_DIR / "styles" / "reflector.sty"
    state.add(
        dim,
        "Renderer architecture",
        "paper/styles/reflector.sty publication style file exists",
        sty_path.exists(),
        "paper/styles/reflector.sty renderer style file is present.",
        "paper/styles/reflector.sty is missing; renderer architecture is incomplete.",
    )

    # 4e. Metadata consistency — validate-metadata.py passes
    rc, output = run_cmd([sys.executable, "scripts/validate-metadata.py"])
    state.add(
        dim,
        "Metadata consistency",
        "scripts/validate-metadata.py passes",
        rc == 0,
        "scripts/validate-metadata.py passed with no errors.",
        f"scripts/validate-metadata.py failed: {output[:200]}.",
    )

    # 4f. CITATION.cff present with ORCID
    citation_path = REPO_ROOT / "CITATION.cff"
    citation_text = read_text(citation_path) or ""
    state.add(
        dim,
        "Metadata consistency",
        "CITATION.cff is present",
        citation_path.exists(),
        "CITATION.cff is present with publication citation metadata.",
        "CITATION.cff is missing.",
    )
    state.add(
        dim,
        "Metadata consistency",
        "CITATION.cff includes ORCID identifier",
        "orcid:" in citation_text,
        "CITATION.cff includes ORCID identifier.",
        "CITATION.cff does not include an ORCID identifier.",
        warn=True,
    )

    # 4g. release-manifest.json present
    release_manifest_path = REPO_ROOT / "release-manifest.json"
    state.add(
        dim,
        "Publication manifests",
        "release-manifest.json is present",
        release_manifest_path.exists(),
        "release-manifest.json is present.",
        "release-manifest.json is missing.",
    )


# ---------------------------------------------------------------------------
# Dimension 5 — Build and Reproducibility
# ---------------------------------------------------------------------------


def audit_build_reproducibility(state: AuditState) -> None:
    dim = "5. Build and Reproducibility"

    latexmkrc_path = REPO_ROOT / ".latexmkrc"
    latexmkrc_text = read_text(latexmkrc_path) or ""

    # 5a. Deterministic compilation controls
    determinism_checks = [
        ("$max_repeat = 10", "max_repeat capped at 10"),
        ("$force_mode = 1", "force_mode enabled"),
        ("$out_dir", "output directory fixed"),
        ("$aux_dir", "aux directory fixed"),
        ("$pdf_mode = 1", "pdf_mode declared"),
    ]
    for pattern, description in determinism_checks:
        state.add(
            dim,
            "Deterministic compilation",
            f".latexmkrc declares {description}",
            pattern in latexmkrc_text,
            f".latexmkrc correctly declares {description}.",
            f".latexmkrc is missing {description} ({pattern!r}).",
        )

    # 5b. Bibliography stability
    state.add(
        dim,
        "Bibliography stability",
        ".latexmkrc configures biber with fixed directories",
        "--input-directory" in latexmkrc_text and "--output-directory" in latexmkrc_text,
        ".latexmkrc configures biber with fixed --input-directory and --output-directory.",
        ".latexmkrc does not configure biber with fixed directory arguments.",
    )
    sty_path = PAPER_DIR / "styles" / "reflector.sty"
    sty_text = read_text(sty_path) or ""
    state.add(
        dim,
        "Bibliography stability",
        "biblatex uses deterministic sorting mode",
        "sorting=" in sty_text or "sorting=" in latexmkrc_text,
        "biblatex is configured with deterministic sorting.",
        "biblatex sorting mode is not explicitly configured.",
        warn=True,
    )

    # 5c. Build script flags
    build_script_path = REPO_ROOT / "scripts" / "build-paper.sh"
    build_text = read_text(build_script_path) or ""
    script_checks = [
        ("-gg", "full-rebuild flag -gg"),
        ("-halt-on-error", "halt-on-error flag"),
        ("-interaction=nonstopmode", "non-interactive flag"),
        ("-recorder", "recorder flag for dep tracking"),
        ("set -euo pipefail", "strict error handling"),
    ]
    for pattern, description in script_checks:
        state.add(
            dim,
            "Workflow reproducibility",
            f"build-paper.sh uses {description}",
            pattern in build_text,
            f"scripts/build-paper.sh uses {description}.",
            f"scripts/build-paper.sh is missing {description}.",
        )

    # 5d. Figure reproducibility — PNG dimensions canonical
    canonical_ok = True
    dimension_issues: list[str] = []
    if FIGURES_DIR.exists():
        for png_file in FIGURES_DIR.glob("*.png"):
            dims = read_png_dimensions(png_file)
            if dims is None:
                continue
            if png_file.name == "hero.png":
                expected = HERO_DIMENSIONS
            elif FIGURE_NAME_PATTERN.fullmatch(png_file.name):
                expected = FIGURE_DIMENSIONS
            else:
                continue
            if dims != expected:
                canonical_ok = False
                dimension_issues.append(f"{png_file.name}: got {dims}, expected {expected}")
    state.add(
        dim,
        "Figure reproducibility",
        "All PNG figures have canonical dimensions",
        canonical_ok,
        "All PNG figures match canonical dimensions (1600×900 for figures, 1920×1080 for hero).",
        f"PNG dimension mismatches: {'; '.join(dimension_issues)}.",
    )

    # 5e. Prompt files for figures
    prompts_dir = FIGURES_DIR / "prompts"
    all_tex_text = collect_all_tex_text()
    ref_figs = {Path(r).stem for r in find_tex_graphics(all_tex_text) if r}
    prompt_stems = {f.stem.replace(".prompt", "") for f in prompts_dir.glob("*.prompt.md")} if prompts_dir.exists() else set()
    figs_without_prompts = [s for s in ref_figs if s not in prompt_stems]
    state.add(
        dim,
        "Figure reproducibility",
        "All referenced figures have prompt-preservation files",
        len(figs_without_prompts) == 0,
        f"All {len(ref_figs)} referenced figures have prompt files in paper/figures/prompts/.",
        f"{len(figs_without_prompts)} referenced figures lack prompt files: {', '.join(sorted(figs_without_prompts)[:5])}.",
    )

    # 5f. CI/CD workflow toolchain
    build_wf = WORKFLOWS_DIR / "build-paper.yml"
    build_wf_text = read_text(build_wf) or ""
    state.add(
        dim,
        "CI/CD synchronization",
        "build-paper.yml CI workflow is present",
        build_wf.exists(),
        "build-paper.yml CI workflow is present.",
        "build-paper.yml is missing; CI PDF build pipeline is absent.",
    )
    state.add(
        dim,
        "CI/CD synchronization",
        "CI workflow invokes build-paper.sh",
        "build-paper.sh" in build_wf_text,
        "CI workflow invokes scripts/build-paper.sh.",
        "CI workflow does not invoke scripts/build-paper.sh.",
    )
    state.add(
        dim,
        "CI/CD synchronization",
        "CI workflow provides LaTeX toolchain",
        "latex-action" in build_wf_text or "texlive" in build_wf_text.lower(),
        "CI workflow provides a LaTeX toolchain (latex-action or texlive).",
        "CI workflow does not configure a LaTeX toolchain.",
    )

    # 5g. Timestamp independence
    metadata_tex = read_text(PAPER_DIR / "macros" / "metadata.tex") or ""
    uses_today = r"\today" in metadata_tex
    state.add(
        dim,
        "Deterministic compilation",
        "Paper date does not use \\today (timestamp independence)",
        not uses_today,
        "Paper date macro does not use \\today — build is timestamp-independent.",
        "Paper date uses \\today in macros/metadata.tex — builds are not timestamp-independent.",
        warn=True,
    )


# ---------------------------------------------------------------------------
# Dimension 6 — Cognitive and Architectural Coherence
# ---------------------------------------------------------------------------


def audit_cognitive_coherence(state: AuditState) -> None:
    dim = "6. Cognitive and Architectural Coherence"

    # 6a. Conceptual flow — expected sections present and in paper.tex order
    paper_tex_text = read_text(PAPER_DIR / "paper.tex") or ""
    input_lines = [
        re.search(r"\\input\{([^}]+)\}", line)
        for line in paper_tex_text.splitlines()
    ]
    input_order = [m.group(1).replace("sections/", "") for m in input_lines if m]
    # Add .tex suffix if missing
    input_order = [s if s.endswith(".tex") else s + ".tex" for s in input_order]

    expected_in_paper = all(sec in input_order for sec in EXPECTED_SECTION_ORDER[:6])
    state.add(
        dim,
        "Conceptual flow",
        "Core sections are included in paper.tex",
        expected_in_paper,
        "Core sections (abstract through reflector_framework) are included in paper.tex.",
        f"Some core sections are not included in paper.tex. Found: {input_order[:8]}.",
    )

    # 6b. Terminology consistency — key terms appear in both paper sections and specs
    key_terms = ["recursive drift", "synchronization", "milestone", "governance", "reflector"]
    all_tex_text = collect_all_tex_text().lower()
    spec_text = ""
    if SPECS_DIR.exists():
        for spec_file in SPECS_DIR.rglob("*.spec.md"):
            spec_text += (read_text(spec_file) or "").lower()
    missing_from_tex = [t for t in key_terms if t not in all_tex_text]
    missing_from_specs = [t for t in key_terms if t not in spec_text]
    state.add(
        dim,
        "Terminology consistency",
        "Key domain terms appear in paper sections",
        len(missing_from_tex) == 0,
        f"All {len(key_terms)} key domain terms appear in paper sections.",
        f"Key terms missing from paper sections: {', '.join(missing_from_tex)}.",
    )
    state.add(
        dim,
        "Terminology consistency",
        "Key domain terms appear in specification files",
        len(missing_from_specs) == 0,
        f"All {len(key_terms)} key domain terms appear in specification files.",
        f"Key terms missing from specifications: {', '.join(missing_from_specs)}.",
        warn=True,
    )

    # 6c. Recursive systems coherence — Python package aligns with paper sections
    paper_section_topics = {
        "audits": SECTIONS_DIR / "reflective_auditing.tex",
        "synchronization": SECTIONS_DIR / "synchronization.tex",
        "orchestration": SECTIONS_DIR / "milestone_execution.tex",
        "schemas": SECTIONS_DIR / "reflector_framework.tex",
        "workflows": SECTIONS_DIR / "operational_demonstration.tex",
    }
    aligned_modules: list[str] = []
    misaligned_modules: list[str] = []
    for module_name, section_path in paper_section_topics.items():
        module_exists = (REFLECTOR_PKG / module_name).exists()
        section_exists = section_path.exists()
        if module_exists and section_exists:
            aligned_modules.append(module_name)
        else:
            misaligned_modules.append(module_name)
    state.add(
        dim,
        "Recursive systems coherence",
        "Python module topology aligns with paper section topics",
        len(misaligned_modules) == 0,
        f"All {len(aligned_modules)} key modules have corresponding paper sections.",
        f"{len(misaligned_modules)} module/section alignments are missing: {', '.join(misaligned_modules)}.",
    )

    # 6d. Synchronization philosophy — audit scripts reference recursive/synchronization concepts
    audit_script_path = REPO_ROOT / "scripts" / "audit-publication-readiness.py"
    audit_text = read_text(audit_script_path) or ""
    state.add(
        dim,
        "Synchronization philosophy consistency",
        "Audit infrastructure reflects synchronization philosophy",
        "synchronization" in audit_text.lower() or "recursive" in audit_text.lower(),
        "Audit scripts reference synchronization/recursive concepts, aligning with publication philosophy.",
        "Audit scripts do not reference synchronization/recursive concepts.",
    )

    # 6e. Architecture documented — CONTRIBUTING.md mentions publication workflow
    contributing_text = read_text(REPO_ROOT / "CONTRIBUTING.md") or ""
    state.add(
        dim,
        "Conceptual flow",
        "CONTRIBUTING.md documents contribution workflow",
        len(contributing_text.split()) >= 100,
        "CONTRIBUTING.md provides substantive contribution guidance.",
        "CONTRIBUTING.md is missing or too sparse to guide contributors.",
        warn=True,
    )

    # 6f. Title consistency across surfaces
    title_tex_path = PAPER_DIR / "config" / "title.tex"
    title_tex_text = read_text(title_tex_path) or ""
    pub_yaml_text = read_text(METADATA_DIR / "publication.yaml") or ""
    title_in_tex = CANONICAL_TITLE_TEXT in title_tex_text.lower()
    title_in_yaml = CANONICAL_TITLE_TEXT in pub_yaml_text.lower()
    state.add(
        dim,
        "Terminology consistency",
        "Canonical title is consistent across paper/config/title.tex and metadata/publication.yaml",
        title_in_tex and title_in_yaml,
        "Canonical title appears consistently in paper/config/title.tex and metadata/publication.yaml.",
        f"Title inconsistency: in title.tex={title_in_tex}, in publication.yaml={title_in_yaml}.",
    )


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

DIMENSION_GOALS = {
    "1. Publication Quality": [
        ("Section completeness", "All paper sections have substantive content"),
        ("Abstract quality", "Abstract is publication-ready"),
        ("Citation quality", "Bibliography is complete and non-placeholder"),
        ("Figure quality", "All figures have captions, labels, and canonical dimensions"),
        ("Publication polish", "No placeholder markers; keywords declared"),
    ],
    "2. Recursive Synchronization Integrity": [
        ("Specification synchronization", "All specification files are present"),
        ("Metadata synchronization", "Version is consistent across all metadata surfaces"),
        ("Figure synchronization", "Figure manifest is synchronized"),
        ("Workflow consistency", "All required workflows are present"),
        ("Publication manifest consistency", "publication.json is valid and complete"),
    ],
    "3. Repository Architecture": [
        ("Modularity", "reflector Python package is structurally complete"),
        ("Maintainability", "pyproject.toml, CONTRIBUTING.md, README.md are present"),
        ("Semantic/render separation", "Styles, macros, and config directories are present"),
        ("Synchronization infrastructure quality", "All validation scripts are present"),
        ("Recursive workflow organization", ".latexmkrc orchestration is in place"),
    ],
    "4. Publication Infrastructure": [
        ("arXiv compatibility", "00README.json is valid and arXiv-compliant"),
        ("Pages deployment", "Pages workflow and landing page are configured"),
        ("Metadata consistency", "validate-metadata.py passes; CITATION.cff is complete"),
        ("Publication manifests", "Release workflow and manifests are present"),
        ("Renderer architecture", "reflector.sty renderer style file is present"),
    ],
    "5. Build and Reproducibility": [
        ("Deterministic compilation", "All .latexmkrc determinism controls are declared"),
        ("Bibliography stability", "biber is configured with fixed directories"),
        ("Workflow reproducibility", "build-paper.sh uses all determinism flags"),
        ("Figure reproducibility", "PNG dimensions are canonical; prompts are preserved"),
        ("CI/CD synchronization", "CI workflow invokes build-paper.sh with LaTeX toolchain"),
    ],
    "6. Cognitive and Architectural Coherence": [
        ("Conceptual flow", "Core sections are included in paper.tex"),
        ("Terminology consistency", "Key terms appear consistently across paper and specs"),
        ("Recursive systems coherence", "Python modules align with paper section topics"),
        ("Synchronization philosophy consistency", "Audit scripts reflect synchronization philosophy"),
    ],
}


def generate_report(state: AuditState) -> str:
    timestamp = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    checks = state.checks
    pass_count = sum(1 for c in checks if c.status == "PASS")
    warn_count = sum(1 for c in checks if c.status == "WARN")
    fail_count = sum(1 for c in checks if c.status == "FAIL")
    total = len(checks)

    by_dim: dict[str, list[Check]] = {}
    for c in checks:
        by_dim.setdefault(c.dimension, []).append(c)

    def dim_ok(dim: str) -> bool:
        return all(c.status == "PASS" for c in by_dim.get(dim, [])) and bool(by_dim.get(dim))

    def area_ok_in_dim(dim: str, area: str) -> bool:
        return all(c.status == "PASS" for c in by_dim.get(dim, []) if c.area == area) and any(
            c.area == area for c in by_dim.get(dim, [])
        )

    def mark(v: bool) -> str:
        return "x" if v else " "

    def icon(status: str) -> str:
        return {"PASS": "✅", "WARN": "⚠️", "FAIL": "❌"}.get(status, "❓")

    if fail_count == 0 and warn_count == 0:
        overall = "✅ **Publication-ready** — all checks passed."
    elif fail_count == 0:
        overall = "⚠️ **Conditionally ready** — no hard failures; non-critical warnings remain."
    else:
        overall = f"❌ **Not publication-ready** — {fail_count} hard failure(s) must be resolved."

    lines: list[str] = []
    lines += [
        "# 🔎 Holistic Publication and Recursive Synchronization Audit Report",
        "",
        f"Generated at: `{timestamp}`",
        "",
        "**Repository:** egohygiene/reflector  ",
        "**Audit type:** Final holistic publication and recursive synchronization checkpoint  ",
        "**Scope:** Six dimensions — publication quality, recursive synchronization integrity,",
        "repository architecture, publication infrastructure, build and reproducibility,",
        "and cognitive and architectural coherence.",
        "",
    ]

    # Executive summary
    lines += [
        "## Executive Summary",
        "",
        f"- Total checks: **{total}**",
        f"- Pass: **{pass_count}**",
        f"- Warn: **{warn_count}**",
        f"- Fail: **{fail_count}**",
        "",
        f"Overall result: {overall}",
        "",
    ]

    # Dimension overview table
    lines += [
        "## Audit Dimensions Overview",
        "",
        "| Dimension | Checks | Pass | Warn | Fail | Status |",
        "| --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for dim in sorted(by_dim):
        dim_checks = by_dim[dim]
        dp = sum(1 for c in dim_checks if c.status == "PASS")
        dw = sum(1 for c in dim_checks if c.status == "WARN")
        df = sum(1 for c in dim_checks if c.status == "FAIL")
        if df > 0:
            dim_status = "❌ Fail"
        elif dw > 0:
            dim_status = "⚠️ Warn"
        else:
            dim_status = "✅ Pass"
        lines.append(f"| {dim} | {len(dim_checks)} | {dp} | {dw} | {df} | {dim_status} |")
    lines.append("")

    # Issue goals checklist
    lines += [
        "## Issue Goals",
        "",
        f"- [x] Perform final holistic repository audit",
        f"- [{mark(fail_count == 0)}] Validate publication readiness",
        f"- [{mark(dim_ok('2. Recursive Synchronization Integrity'))}] Validate recursive synchronization integrity",
        f"- [{mark(dim_ok('3. Repository Architecture') and dim_ok('6. Cognitive and Architectural Coherence'))}] Validate repository coherence",
        f"- [{mark(dim_ok('5. Build and Reproducibility'))}] Validate deterministic publication workflows",
        "- [x] Generate final audit report",
        f"- [x] Identify remaining high-signal improvements",
        "",
    ]

    # Detailed dimension analyses
    lines += ["## Detailed Analyses", ""]
    for dim in sorted(by_dim):
        dim_checks = by_dim[dim]
        lines += [f"### {dim}", ""]

        # Goal sub-checklist for this dimension
        goals = DIMENSION_GOALS.get(dim, [])
        if goals:
            lines.append("**Goals:**")
            lines.append("")
            for area, goal_text in goals:
                ok = area_ok_in_dim(dim, area)
                lines.append(f"- [{mark(ok)}] {goal_text}")
            lines.append("")

        # Check table grouped by area
        by_area: dict[str, list[Check]] = {}
        for c in dim_checks:
            by_area.setdefault(c.area, []).append(c)

        lines += [
            "| Area | Check | Result | Details |",
            "| --- | --- | --- | --- |",
        ]
        for area in sorted(by_area):
            for check in by_area[area]:
                lines.append(f"| {area} | {check.name} | {icon(check.status)} {check.status} | {check.details} |")
        lines.append("")

    # Unresolved issues
    unresolved = [c for c in checks if c.status in {"WARN", "FAIL"}]
    lines += ["## Unresolved Issues", ""]
    if unresolved:
        for c in unresolved:
            lines.append(f"- {icon(c.status)} **{c.dimension} / {c.area} / {c.name}**: {c.details}")
    else:
        lines.append("- None — all checks passed.")
    lines.append("")

    # Synthesis and high-signal improvements
    lines += [
        "## Synthesis",
        "",
        "The reflector repository has reached a strong architectural and publication foundation.",
        "The six-dimension audit reveals:",
        "",
    ]
    for dim in sorted(by_dim):
        dim_checks = by_dim[dim]
        dp = sum(1 for c in dim_checks if c.status == "PASS")
        dw = sum(1 for c in dim_checks if c.status == "WARN")
        df = sum(1 for c in dim_checks if c.status == "FAIL")
        if df == 0 and dw == 0:
            verdict = "fully compliant"
        elif df == 0:
            verdict = "conditionally compliant (warnings only)"
        else:
            verdict = f"non-compliant ({df} failure(s))"
        lines.append(f"- **{dim}**: {verdict} ({dp} pass, {dw} warn, {df} fail).")
    lines.append("")

    # High-signal improvements
    lines += ["## High-Signal Improvements", ""]
    fail_items = [c for c in checks if c.status == "FAIL"]
    warn_items = [c for c in checks if c.status == "WARN"]
    if fail_items:
        lines.append("### Critical (must resolve before publication)")
        lines.append("")
        for c in fail_items:
            lines.append(f"- **{c.area} / {c.name}**: {c.details}")
        lines.append("")
    if warn_items:
        lines.append("### Advisory (address to raise quality)")
        lines.append("")
        for c in warn_items:
            lines.append(f"- **{c.area} / {c.name}**: {c.details}")
        lines.append("")
    if not fail_items and not warn_items:
        lines.append("- No improvements required — all checks passed.")
        lines.append("")

    # Final readiness checklist
    lines += [
        "## Final Publication Readiness Checklist",
        "",
        f"- [{mark(dim_ok('1. Publication Quality'))}] Publication quality validated",
        f"- [{mark(dim_ok('2. Recursive Synchronization Integrity'))}] Recursive synchronization integrity confirmed",
        f"- [{mark(dim_ok('3. Repository Architecture'))}] Repository architecture validated",
        f"- [{mark(dim_ok('4. Publication Infrastructure'))}] Publication infrastructure validated",
        f"- [{mark(dim_ok('5. Build and Reproducibility'))}] Build determinism and reproducibility confirmed",
        f"- [{mark(dim_ok('6. Cognitive and Architectural Coherence'))}] Cognitive and architectural coherence confirmed",
        f"- [{mark(fail_count == 0)}] No hard failures — publication-ready",
        "- [x] Final holistic audit report generated",
        "",
    ]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> int:
    state = AuditState()

    audit_publication_quality(state)
    audit_synchronization_integrity(state)
    audit_repository_architecture(state)
    audit_publication_infrastructure(state)
    audit_build_reproducibility(state)
    audit_cognitive_coherence(state)

    report = generate_report(state)

    timestamp = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    # Replace colons with dashes for filesystem compatibility (colons are invalid in filenames on Windows).
    safe_ts = timestamp.replace(":", "-")
    output_path = AUDITS_DIR / f"audit-{safe_ts}.md"
    AUDITS_DIR.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")

    pass_count = sum(1 for c in state.checks if c.status == "PASS")
    warn_count = sum(1 for c in state.checks if c.status == "WARN")
    fail_count = sum(1 for c in state.checks if c.status == "FAIL")
    print(f"[audit-holistic] report written to {output_path}")
    print(f"[audit-holistic] pass={pass_count} warn={warn_count} fail={fail_count}")
    return 1 if fail_count > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
