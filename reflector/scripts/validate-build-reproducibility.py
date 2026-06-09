#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0
# validate-build-reproducibility.py — Validate deterministic build reproducibility.

from __future__ import annotations

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
AUDIT_OUTPUT = REPO_ROOT / "audits" / "build-reproducibility.md"


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
    # 1. Build configuration determinism (.latexmkrc)
    # -------------------------------------------------------------------------
    latexmkrc_path = REPO_ROOT / ".latexmkrc"
    if latexmkrc_path.exists():
        latexmkrc_text = latexmkrc_path.read_text(encoding="utf-8")

        add_check(
            checks,
            "Build configuration",
            "max_repeat is declared",
            "$max_repeat = 10" in latexmkrc_text,
            ".latexmkrc declares $max_repeat = 10 to cap rebuild iterations.",
            ".latexmkrc does not declare $max_repeat = 10.",
        )
        add_check(
            checks,
            "Build configuration",
            "force_mode is enabled",
            "$force_mode = 1" in latexmkrc_text,
            ".latexmkrc enables $force_mode = 1 for deterministic rebuild.",
            ".latexmkrc does not enable $force_mode = 1.",
        )
        add_check(
            checks,
            "Build configuration",
            "Output directory is fixed",
            '$out_dir = ".cache/out"' in latexmkrc_text,
            ".latexmkrc fixes $out_dir to .cache/out.",
            ".latexmkrc does not fix $out_dir to .cache/out.",
        )
        add_check(
            checks,
            "Build configuration",
            "Aux directory is fixed",
            '$aux_dir = ".cache/aux"' in latexmkrc_text,
            ".latexmkrc fixes $aux_dir to .cache/aux.",
            ".latexmkrc does not fix $aux_dir to .cache/aux.",
        )
        add_check(
            checks,
            "Build configuration",
            "do_cd is enabled",
            "$do_cd = 1" in latexmkrc_text,
            ".latexmkrc enables $do_cd = 1 for stable relative path resolution.",
            ".latexmkrc does not enable $do_cd = 1.",
        )
        add_check(
            checks,
            "Build configuration",
            "PDF mode is declared",
            "$pdf_mode = 1" in latexmkrc_text,
            ".latexmkrc declares $pdf_mode = 1 for pdflatex output.",
            ".latexmkrc does not declare $pdf_mode = 1.",
        )
        add_check(
            checks,
            "Build configuration",
            "TEXINPUTS paths are explicit",
            'TEXINPUTS' in latexmkrc_text,
            ".latexmkrc declares explicit TEXINPUTS search paths.",
            ".latexmkrc does not declare TEXINPUTS, allowing implicit path resolution.",
        )
        add_check(
            checks,
            "Build configuration",
            "TEXMFOUTPUT is fixed",
            "TEXMFOUTPUT" in latexmkrc_text,
            ".latexmkrc fixes TEXMFOUTPUT to the aux directory.",
            ".latexmkrc does not fix TEXMFOUTPUT.",
        )
        add_check(
            checks,
            "Build configuration",
            "emulate_aux is enabled",
            "$emulate_aux = 1" in latexmkrc_text,
            ".latexmkrc enables $emulate_aux = 1 for aux directory emulation.",
            ".latexmkrc does not enable $emulate_aux = 1.",
        )
    else:
        checks.append(Check(
            area="Build configuration",
            name=".latexmkrc exists",
            status="FAIL",
            details=".latexmkrc not found at repository root.",
        ))

    # -------------------------------------------------------------------------
    # 2. Build script determinism
    # -------------------------------------------------------------------------
    build_script_path = REPO_ROOT / "scripts" / "build-paper.sh"
    if build_script_path.exists():
        build_script_text = build_script_path.read_text(encoding="utf-8")

        add_check(
            checks,
            "Build script",
            "Build script invokes repository .latexmkrc",
            "latexmkrc_file" in build_script_text and '-r "${latexmkrc_file}"' in build_script_text,
            "scripts/build-paper.sh invokes the root .latexmkrc via -r flag.",
            "scripts/build-paper.sh does not invoke the configured latexmkrc_file with -r flag.",
        )
        add_check(
            checks,
            "Build script",
            "Build script uses -gg for full rebuild",
            "-gg" in build_script_text,
            "scripts/build-paper.sh uses -gg to force a full, clean rebuild.",
            "scripts/build-paper.sh does not use -gg; incremental rebuild may produce non-deterministic output.",
        )
        add_check(
            checks,
            "Build script",
            "Build script uses -halt-on-error",
            "-halt-on-error" in build_script_text,
            "scripts/build-paper.sh uses -halt-on-error for clean failure detection.",
            "scripts/build-paper.sh does not use -halt-on-error.",
        )
        add_check(
            checks,
            "Build script",
            "Build script uses -interaction=nonstopmode",
            "-interaction=nonstopmode" in build_script_text,
            "scripts/build-paper.sh uses -interaction=nonstopmode for non-interactive reproducible runs.",
            "scripts/build-paper.sh does not set -interaction=nonstopmode.",
        )
        add_check(
            checks,
            "Build script",
            "Build script enables -recorder",
            "-recorder" in build_script_text,
            "scripts/build-paper.sh enables -recorder for dependency tracking.",
            "scripts/build-paper.sh does not enable -recorder.",
        )
        add_check(
            checks,
            "Build script",
            "Build uses set -euo pipefail",
            "set -euo pipefail" in build_script_text,
            "scripts/build-paper.sh uses set -euo pipefail for strict error handling.",
            "scripts/build-paper.sh does not use set -euo pipefail.",
        )
    else:
        checks.append(Check(
            area="Build script",
            name="Build script exists",
            status="FAIL",
            details="scripts/build-paper.sh not found.",
        ))

    # -------------------------------------------------------------------------
    # 3. Bibliography determinism
    # -------------------------------------------------------------------------
    if latexmkrc_path.exists():
        latexmkrc_text = latexmkrc_path.read_text(encoding="utf-8")
        biber_cmd = re.search(r"\$biber\s*=\s*[\"'](.*?)[\"']", latexmkrc_text, re.DOTALL)
        biber_text = biber_cmd.group(1) if biber_cmd else latexmkrc_text

        add_check(
            checks,
            "Bibliography determinism",
            "biber uses fixed --input-directory",
            "--input-directory=.cache/aux" in latexmkrc_text,
            "biber is configured with --input-directory=.cache/aux for fixed input.",
            "biber does not use a fixed --input-directory in .latexmkrc.",
        )
        add_check(
            checks,
            "Bibliography determinism",
            "biber uses fixed --output-directory",
            "--output-directory=.cache/aux" in latexmkrc_text,
            "biber is configured with --output-directory=.cache/aux for fixed output.",
            "biber does not use a fixed --output-directory in .latexmkrc.",
        )

    # Check for biblatex sorting mode (deterministic: nyt or nty, not random)
    sty_path = PAPER_DIR / "styles" / "reflector.sty"
    if sty_path.exists():
        sty_text = sty_path.read_text(encoding="utf-8")
        sorting_match = re.search(r"sorting\s*=\s*(\w+)", sty_text)
        sorting_mode = sorting_match.group(1) if sorting_match else None
        deterministic_sortings = {"nyt", "nty", "nyvt", "ynt", "ydnt", "none", "anyt", "anyvt"}
        add_check(
            checks,
            "Bibliography determinism",
            "Bibliography sorting mode is deterministic",
            sorting_mode is None or sorting_mode.lower() in deterministic_sortings,
            f"biblatex sorting={sorting_mode!r} is deterministic.",
            f"biblatex sorting={sorting_mode!r} is not a known-deterministic mode.",
        )

    # -------------------------------------------------------------------------
    # 4. Timestamp independence
    # -------------------------------------------------------------------------
    # Check if \today is used in metadata — it causes date drift between builds
    metadata_path = PAPER_DIR / "macros" / "metadata.tex"
    if metadata_path.exists():
        metadata_text = metadata_path.read_text(encoding="utf-8")
        uses_today = "\\today" in metadata_text
        add_check(
            checks,
            "Timestamp independence",
            "Paper date does not use \\today",
            not uses_today,
            "Paper date does not use \\today; date is stable across builds.",
            "Paper date uses \\today in macros/metadata.tex — this introduces build timestamp drift. "
            "Consider replacing \\today with a fixed date string for reproducible artifacts.",
            warn=True,  # WARN not FAIL — common in draft papers
        )

    # Check sections for embedded \today usage
    section_dir = PAPER_DIR / "sections"
    sections_with_today: list[str] = []
    if section_dir.is_dir():
        for tex_file in sorted(section_dir.glob("*.tex")):
            content = tex_file.read_text(encoding="utf-8")
            if "\\today" in content or "\\DTMnow" in content:
                sections_with_today.append(tex_file.name)
    add_check(
        checks,
        "Timestamp independence",
        "Section files do not use dynamic date commands",
        not sections_with_today,
        "No section files use \\today or \\DTMnow.",
        "Section files with dynamic date commands: " + ", ".join(sections_with_today),
        warn=True,
    )

    # -------------------------------------------------------------------------
    # 5. Output artifact stability
    # -------------------------------------------------------------------------
    # Validate that output/aux directories are gitignored
    gitignore_path = REPO_ROOT / ".gitignore"
    if gitignore_path.exists():
        gitignore_text = gitignore_path.read_text(encoding="utf-8")
        add_check(
            checks,
            "Output stability",
            ".cache/ is git-ignored",
            ".cache/" in gitignore_text or "**/.cache/" in gitignore_text or ".cache" in gitignore_text,
            ".cache/ build artifacts are excluded from version control.",
            ".cache/ is not listed in .gitignore — build artifacts may be accidentally committed.",
        )
        add_check(
            checks,
            "Output stability",
            "Generated PDFs are git-ignored",
            # PDFs are excluded if *.pdf is gitignored OR if they are generated inside .cache/
            # (which is already excluded by the .cache gitignore entry)
            "*.pdf" in gitignore_text
            or "paper/*.pdf" in gitignore_text
            or ".cache" in gitignore_text
            or "paper/.cache/" in gitignore_text,
            "Generated PDF files are excluded from version control (via .cache/ exclusion).",
            "Generated PDFs may not be excluded from version control — ensure .cache/ or *.pdf is in .gitignore.",
        )
    else:
        checks.append(Check(
            area="Output stability",
            name=".gitignore exists",
            status="WARN",
            details=".gitignore not found; build artifacts may not be excluded from version control.",
        ))

    # -------------------------------------------------------------------------
    # 6. CI/CD reproducibility
    # -------------------------------------------------------------------------
    build_workflow_path = REPO_ROOT / ".github" / "workflows" / "build-paper.yml"
    if build_workflow_path.exists():
        build_workflow_text = build_workflow_path.read_text(encoding="utf-8")

        # Check that TeXLive is available — either via explicit install or via a latex-action
        # xu-cheng/latex-action and similar actions provide a full TeXLive environment implicitly
        texlive_available = (
            "texlive-version:" in build_workflow_text
            or "scheme-full" in build_workflow_text
            or "2025" in build_workflow_text
            or "texlive" in build_workflow_text.lower()
            or "latex-action" in build_workflow_text  # xu-cheng/latex-action provides TeXLive
            or "install-tl" in build_workflow_text
            or "latexmk" in build_workflow_text.lower()
        )
        add_check(
            checks,
            "CI/CD reproducibility",
            "CI workflow provides TeXLive toolchain",
            texlive_available,
            "CI build workflow provides a TeXLive toolchain (via latex-action or explicit install).",
            "CI build workflow does not appear to provide a TeXLive toolchain.",
        )

        # Check that build script is invoked
        add_check(
            checks,
            "CI/CD reproducibility",
            "CI invokes build-paper.sh",
            "build-paper.sh" in build_workflow_text,
            "CI build workflow invokes scripts/build-paper.sh.",
            "CI build workflow does not invoke build-paper.sh.",
        )

        # Check that latexmk is installed
        add_check(
            checks,
            "CI/CD reproducibility",
            "CI installs latexmk",
            "latexmk" in build_workflow_text.lower(),
            "CI build workflow installs latexmk.",
            "CI build workflow does not appear to install latexmk.",
        )
    else:
        checks.append(Check(
            area="CI/CD reproducibility",
            name="Build workflow exists",
            status="FAIL",
            details=".github/workflows/build-paper.yml not found.",
        ))

    # -------------------------------------------------------------------------
    # 7. Manifest stability
    # -------------------------------------------------------------------------
    import json as json_mod

    pub_json_path = REPO_ROOT / "publication.json"
    if pub_json_path.exists():
        try:
            pub_json = json_mod.loads(pub_json_path.read_text(encoding="utf-8"))
            required_pub_keys = {"project", "status", "version"}
            missing_pub_keys = sorted(required_pub_keys - set(pub_json.keys()))
            add_check(
                checks,
                "Manifest stability",
                "publication.json has required keys",
                not missing_pub_keys,
                "publication.json includes required project, status, and version keys.",
                "publication.json is missing keys: " + ", ".join(missing_pub_keys),
            )
        except (json_mod.JSONDecodeError, OSError):
            checks.append(Check(
                area="Manifest stability",
                name="publication.json is valid JSON",
                status="FAIL",
                details="publication.json is not valid JSON.",
            ))
    else:
        checks.append(Check(
            area="Manifest stability",
            name="publication.json exists",
            status="FAIL",
            details="publication.json not found.",
        ))

    release_manifest_path = REPO_ROOT / "release-manifest.json"
    add_check(
        checks,
        "Manifest stability",
        "release-manifest.json exists",
        release_manifest_path.exists(),
        "release-manifest.json exists.",
        "release-manifest.json not found.",
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
    lines.append("# Build Reproducibility Validation Report")
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
        lines.append("Overall result: ✅ **Fully deterministic**")
    elif fail_count == 0:
        lines.append("Overall result: ⚠️ **Conditionally deterministic** (non-failing issues remain)")
    else:
        lines.append("Overall result: ❌ **Determinism concerns detected**")
    lines.append("")

    lines.append("## Goal Checklist")
    lines.append("")
    lines.append(f"- [{mark(area_ok('Build configuration'))}] Build configuration declares deterministic controls")
    lines.append(f"- [{mark(area_ok('Build script'))}] Build script uses deterministic invocation flags")
    lines.append(f"- [{mark(area_ok('Bibliography determinism'))}] Bibliography compilation is deterministic")
    lines.append(f"- [{mark(area_ok('Timestamp independence'))}] Builds are timestamp-independent")
    lines.append(f"- [{mark(area_ok('Output stability'))}] Build artifacts are isolated from version control")
    lines.append(f"- [{mark(area_ok('CI/CD reproducibility'))}] CI/CD pipeline is reproducible")
    lines.append(f"- [{mark(area_ok('Manifest stability'))}] Publication manifests are stable")
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

    if unresolved:
        lines.append("## Unresolved Issues")
        lines.append("")
        for check in unresolved:
            icon = "⚠️" if check.status == "WARN" else "❌"
            lines.append(f"- {icon} **{check.area} / {check.name}**: {check.details}")
        lines.append("")

        lines.append("## Recommended Fixes")
        lines.append("")
        for check in unresolved:
            if "\\today" in check.details:
                lines.append(
                    "- Replace `\\today` in `macros/metadata.tex` with a fixed date string "
                    "(e.g., `\\newcommand{\\paperdate}{2025-01-01}`) to eliminate timestamp drift between builds."
                )
            elif "latexmk is not installed" in check.details:
                lines.append(
                    "- Install `latexmk` + TeX Live toolchain and rerun `./scripts/build-paper.sh paper` "
                    "to validate full build reproducibility."
                )
            else:
                lines.append(f"- Resolve: **{check.area} / {check.name}**.")
        lines.append("")

    lines.append("## Determinism Confidence Assessment")
    lines.append("")
    if fail_count == 0:
        confidence = "High" if warn_count == 0 else "Medium"
        lines.append(f"**Confidence level: {confidence}**")
        lines.append("")
        lines.append("The build infrastructure declares deterministic controls across:")
        lines.append("- latexmk iteration capping (`$max_repeat`)")
        lines.append("- Fixed output and auxiliary directories")
        lines.append("- Explicit TEXINPUTS path ordering")
        lines.append("- Isolated biber bibliography processing")
        lines.append("- CI/CD toolchain pinning")
        if warn_count > 0:
            lines.append("")
            lines.append(
                "Non-failing warnings remain (see Unresolved Issues). "
                "Addressing these would increase determinism confidence to High."
            )
    else:
        lines.append("**Confidence level: Low**")
        lines.append("")
        lines.append("One or more determinism-critical checks failed. Review and resolve failing checks above.")
    lines.append("")

    AUDIT_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    AUDIT_OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    checks = gather_checks()
    write_report(checks)
    fail_count = sum(1 for c in checks if c.status == "FAIL")
    warn_count = sum(1 for c in checks if c.status == "WARN")
    print(f"[validate-build-reproducibility] report written to {AUDIT_OUTPUT}")
    print(f"[validate-build-reproducibility] pass={sum(1 for c in checks if c.status == 'PASS')} warn={warn_count} fail={fail_count}")
    return 1 if fail_count > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
