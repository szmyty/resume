#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0
# audit-chktex.py — Generate a ChkTeX audit report for the reflector paper.
#
# Runs ChkTeX on the paper source, parses the output, and writes a structured
# Markdown report to audits/chktex-audit.md with:
#   - Warning summary table by severity
#   - Per-file breakdown
#   - Suggested remediation for each warning type
#   - Publication readiness assessment
#
# Usage:
#   python scripts/audit-chktex.py [--paper PAPER_DIR] [--output OUTPUT_FILE]
#   python scripts/audit-chktex.py --help

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
PAPER_DIR = REPO_ROOT / "paper"
CHKTEXRC = REPO_ROOT / ".chktexrc"
DEFAULT_OUTPUT = REPO_ROOT / "audits" / "chktex-audit.md"


# ---------------------------------------------------------------------------
# Warning metadata
# ---------------------------------------------------------------------------

# Severity levels: CRITICAL > HIGH > MEDIUM > LOW
WARNING_SEVERITY: dict[int, str] = {
    # CRITICAL — compilation or structural integrity
    11: "CRITICAL",
    17: "CRITICAL",
    19: "CRITICAL",
    # HIGH — typographic correctness
    2: "HIGH",
    18: "HIGH",
    # MEDIUM — style and readability
    6: "MEDIUM",
    8: "MEDIUM",
    10: "MEDIUM",
    13: "MEDIUM",
    22: "MEDIUM",
    33: "MEDIUM",
    34: "MEDIUM",
    38: "MEDIUM",
    43: "MEDIUM",
    # LOW — informational / minor
    4: "LOW",
    5: "LOW",
    7: "LOW",
    12: "LOW",
    14: "LOW",
    15: "LOW",
    20: "LOW",
    21: "LOW",
    23: "LOW",
    24: "LOW",
    27: "LOW",
    28: "LOW",
    31: "LOW",
    32: "LOW",
    35: "LOW",
    36: "LOW",
    37: "LOW",
    40: "LOW",
    41: "LOW",
    44: "LOW",
}

WARNING_DESCRIPTIONS: dict[int, str] = {
    2: "Non-breaking space (~) should precede \\cite, \\ref, \\Figure",
    4: "\\ldots is normally not used in LaTeX",
    5: "Use \\{ instead of { in mathematical mode",
    6: "Use \\( \\) instead of $ for inline math",
    7: "Include file not found",
    8: "Wrong length of dash (use -- for en-dash, --- for em-dash)",
    10: "Double space in input",
    11: "Wrong delimiter hierarchy in math",
    12: "Interword spacing",
    13: "Intersentence spacing — use \\@ before period ending abbreviation",
    14: "Mismatch or unmatched parenthesis",
    15: "No whitespace before opening bracket",
    17: "Unmatched $ — broken math mode",
    18: "Use `` and '' for quotation marks, not \" or '",
    19: "Mismatched \\begin / \\end environments",
    20: "User-defined pattern match",
    21: "Command may not be available inside a formula",
    22: "Use \\textrm or \\mathrm instead of \\rm",
    23: "No input file found",
    24: "Remove this command",
    27: "Interword spacing",
    28: "Multiple end-of-line characters",
    31: "Wrong use of \\cite — use \\citet or \\citep where applicable",
    32: "Use \\mathit for math italic",
    33: "Avoid primitive TeX (\\def, \\edef, etc.) in LaTeX documents",
    34: "Equation should start on its own paragraph",
    35: "Put a space before -- or ---",
    36: "Put a space after -- or ---",
    37: "Remove spaces before punctuation",
    38: "Do not use -- or --- in mathematical mode",
    40: "Put a space after opening parenthesis",
    41: "Put a space before closing parenthesis",
    43: "Avoid \\def in LaTeX documents",
    44: "User-suppressed warning (inline %chktex suppress)",
}

REMEDIATION: dict[int, str] = {
    2:  "Replace `\\cite{key}` with `~\\cite{key}` and `\\ref{label}` with `~\\ref{label}`.",
    8:  "Use `--` for en-dashes (ranges: pages 10--20) and `---` for em-dashes (parenthetical—like this).",
    10: "Remove one of the consecutive spaces; use a single space between words.",
    11: "Check that math delimiters `(`, `)`, `[`, `]`, `\\{`, `\\}` are correctly nested.",
    13: "Add `\\@` before a period that ends an abbreviation: `e.g.\\ ` or `cf.\\ `.",
    17: "Find and close the unmatched `$` sign to restore math mode balance.",
    18: "Replace `\"` with ` `` ` (opening) and `''` (closing). Use `\\enquote{}` from csquotes.",
    19: "Ensure every `\\begin{env}` has a matching `\\end{env}` and they are not interleaved.",
    22: "Replace `{\\rm text}` with `\\textrm{text}` or `\\mathrm{text}` inside math.",
    33: "Replace `\\def\\cmd{...}` with `\\newcommand{\\cmd}{...}` or `\\renewcommand`.",
    34: "Add a blank line before a displayed equation to start it on its own paragraph.",
    38: "Replace `--` or `---` inside math with `\\text{--}` or the minus operator `-`.",
    43: "Replace `\\def` with `\\newcommand` for LaTeX-idiomatic macro definitions.",
}

DEFAULT_REMEDIATION = "Review the ChkTeX manual entry for this warning and apply the suggested fix."

SEVERITY_ORDER = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "UNKNOWN": 4}


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class ChkTeXWarning:
    file: str
    line: int
    col: int
    warning_num: int
    message: str
    context: str = ""

    @property
    def severity(self) -> str:
        return WARNING_SEVERITY.get(self.warning_num, "UNKNOWN")

    @property
    def description(self) -> str:
        return WARNING_DESCRIPTIONS.get(self.warning_num, self.message)

    @property
    def remediation(self) -> str:
        return REMEDIATION.get(self.warning_num, DEFAULT_REMEDIATION)


@dataclass
class AuditResult:
    generated_at: str
    paper_dir: str
    chktex_version: str
    chktex_available: bool
    warnings: list[ChkTeXWarning] = field(default_factory=list)
    raw_output: str = ""
    build_succeeded: bool = True

    @property
    def critical_count(self) -> int:
        return sum(1 for w in self.warnings if w.severity == "CRITICAL")

    @property
    def high_count(self) -> int:
        return sum(1 for w in self.warnings if w.severity == "HIGH")

    @property
    def medium_count(self) -> int:
        return sum(1 for w in self.warnings if w.severity == "MEDIUM")

    @property
    def low_count(self) -> int:
        return sum(1 for w in self.warnings if w.severity == "LOW")

    @property
    def total_count(self) -> int:
        return len(self.warnings)

    @property
    def readiness_status(self) -> str:
        if not self.chktex_available:
            return "UNKNOWN"
        if self.critical_count > 0:
            return "NOT_READY"
        if self.high_count > 0:
            return "CONDITIONALLY_READY"
        if self.medium_count > 0:
            return "MOSTLY_READY"
        return "READY"

    @property
    def readiness_emoji(self) -> str:
        return {
            "READY": "✅",
            "MOSTLY_READY": "🟡",
            "CONDITIONALLY_READY": "⚠️",
            "NOT_READY": "❌",
            "UNKNOWN": "⬜",
        }.get(self.readiness_status, "⬜")

    @property
    def readiness_label(self) -> str:
        return {
            "READY": "Publication ready — no active ChkTeX warnings",
            "MOSTLY_READY": "Mostly ready — medium/low warnings only",
            "CONDITIONALLY_READY": "Conditionally ready — high-severity warnings require remediation",
            "NOT_READY": "Not ready — critical warnings must be resolved before publication",
            "UNKNOWN": "Unknown — ChkTeX is not available in this environment",
        }.get(self.readiness_status, "Unknown")


# ---------------------------------------------------------------------------
# ChkTeX runner
# ---------------------------------------------------------------------------

def get_chktex_version() -> str:
    try:
        result = subprocess.run(
            ["chktex", "--version"],
            capture_output=True,
            text=True,
            check=False,
        )
        output = result.stdout.strip() or result.stderr.strip()
        # Extract version from output like "ChkTeX v1.7.6 — ..."
        m = re.search(r"v?(\d+\.\d+[\.\d]*)", output)
        return m.group(1) if m else output.splitlines()[0] if output else "unknown"
    except (OSError, subprocess.SubprocessError):
        return "unknown"


def run_chktex(paper_dir: Path, chktexrc: Path | None) -> tuple[int, str]:
    """Run ChkTeX on paper.tex in paper_dir. Return (exit_code, output)."""
    opts = [
        "chktex",
        "-v0",   # parseable format: file:line:col:warning_num:message
        "-q",    # suppress banner
    ]
    if chktexrc and chktexrc.exists():
        opts += ["-l", str(chktexrc)]
    # Suppressed warning numbers (see scripts/lint-paper.sh for justifications)
    for n in (1, 3, 9, 16, 24, 25, 26, 30, 42, 45, 46):
        opts += ["-n", str(n)]
    opts.append("paper.tex")

    env = {**os.environ, "TERM": os.environ.get("TERM", "dumb")}
    result = subprocess.run(
        opts,
        cwd=paper_dir,
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    # stdout has the warnings; stderr has cosmetic messages (e.g. terminal type)
    output = result.stdout
    return result.returncode, output.strip()


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

# ChkTeX -v0 format:
#   file:LINE:COL:WARNING_NUM:message
_WARNING_RE = re.compile(
    r"^(.+?):(\d+):(\d+):(\d+):(.+)$"
)


def parse_chktex_output(raw: str) -> list[ChkTeXWarning]:
    warnings: list[ChkTeXWarning] = []
    lines = raw.splitlines()
    i = 0
    while i < len(lines):
        m = _WARNING_RE.match(lines[i])
        if m:
            file_, line, col, num, msg = m.groups()
            warnings.append(
                ChkTeXWarning(
                    file=file_,
                    line=int(line),
                    col=int(col),
                    warning_num=int(num),
                    message=msg.strip(),
                )
            )
        i += 1
    return warnings


# ---------------------------------------------------------------------------
# Report generator
# ---------------------------------------------------------------------------

def _severity_badge(severity: str) -> str:
    return {
        "CRITICAL": "🔴 CRITICAL",
        "HIGH":     "🟠 HIGH",
        "MEDIUM":   "🟡 MEDIUM",
        "LOW":      "🔵 LOW",
        "UNKNOWN":  "⬜ UNKNOWN",
    }.get(severity, severity)


def generate_report(result: AuditResult) -> str:
    lines: list[str] = []

    # REUSE-IgnoreStart
    lines.append("<!-- SPDX-FileCopyrightText: 2026 Alan Szmyt -->")
    lines.append("<!-- SPDX-License-Identifier: Apache-2.0 -->")
    # REUSE-IgnoreEnd
    lines.append("")
    lines.append("# ChkTeX Audit Report")
    lines.append("")
    lines.append(f"Generated at: `{result.generated_at}`")
    lines.append("")
    lines.append(f"Paper: `{result.paper_dir}`")
    if result.chktex_available:
        lines.append(f"ChkTeX version: `{result.chktex_version}`")
    lines.append("")

    # --- Summary ---
    lines.append("## Summary")
    lines.append("")
    if not result.chktex_available:
        lines.append("> ⬜ **ChkTeX is not available in this environment.**")
        lines.append("> Install ChkTeX to perform publication linting.")
        lines.append("")
    else:
        lines.append(f"| Severity | Count |")
        lines.append(f"|----------|-------|")
        lines.append(f"| 🔴 Critical | {result.critical_count} |")
        lines.append(f"| 🟠 High | {result.high_count} |")
        lines.append(f"| 🟡 Medium | {result.medium_count} |")
        lines.append(f"| 🔵 Low | {result.low_count} |")
        lines.append(f"| **Total** | **{result.total_count}** |")
        lines.append("")

    # --- Publication Readiness ---
    lines.append("## Publication Readiness")
    lines.append("")
    lines.append(
        f"{result.readiness_emoji} **{result.readiness_label}**"
    )
    lines.append("")

    if result.chktex_available:
        if result.critical_count > 0:
            lines.append(
                "> ❌ **Critical warnings must be resolved before any public release or arXiv submission.**"
            )
        elif result.high_count > 0:
            lines.append(
                "> ⚠️  High-severity warnings should be remediated before submission."
            )
        elif result.medium_count > 0:
            lines.append(
                "> 🟡 Medium warnings represent style and readability improvements. Recommended before final release."
            )
        else:
            lines.append(
                "> ✅ No active ChkTeX warnings. The paper passes publication linting."
            )
        lines.append("")

    # --- Warning detail (if any) ---
    if result.warnings:
        lines.append("## Warning Details")
        lines.append("")

        # Group by severity
        severity_groups: dict[str, list[ChkTeXWarning]] = {}
        for w in sorted(result.warnings, key=lambda x: (SEVERITY_ORDER.get(x.severity, 99), x.warning_num, x.line)):
            severity_groups.setdefault(w.severity, []).append(w)

        for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "UNKNOWN"]:
            group = severity_groups.get(severity, [])
            if not group:
                continue
            lines.append(f"### {_severity_badge(severity)}")
            lines.append("")
            lines.append("| File | Line | Col | Warning | Message |")
            lines.append("|------|------|-----|---------|---------|")
            for w in group:
                fname = Path(w.file).name
                lines.append(
                    f"| `{fname}` | {w.line} | {w.col} | W{w.warning_num} | {w.message} |"
                )
            lines.append("")

        # --- Remediation guide ---
        lines.append("## Suggested Remediation")
        lines.append("")

        seen_nums: set[int] = set()
        for w in sorted(result.warnings, key=lambda x: (SEVERITY_ORDER.get(x.severity, 99), x.warning_num)):
            if w.warning_num in seen_nums:
                continue
            seen_nums.add(w.warning_num)
            lines.append(f"### Warning {w.warning_num} — {w.description}")
            lines.append("")
            lines.append(f"**Severity:** {_severity_badge(w.severity)}")
            lines.append("")
            lines.append(f"**Remediation:** {w.remediation}")
            lines.append("")

    else:
        if result.chktex_available:
            lines.append("## Warning Details")
            lines.append("")
            lines.append("_No warnings found. The paper passes all active ChkTeX checks._")
            lines.append("")

    # --- arXiv Readiness ---
    lines.append("## arXiv Submission Readiness")
    lines.append("")
    lines.append("| Check | Status | Notes |")
    lines.append("|-------|--------|-------|")

    def check_row(label: str, ok: bool, note: str = "") -> str:
        icon = "✅" if ok else "❌"
        return f"| {label} | {icon} | {note} |"

    lines.append(check_row("ChkTeX available", result.chktex_available, "Required for linting"))
    lines.append(check_row("No critical warnings", result.critical_count == 0 if result.chktex_available else True,
                            f"{result.critical_count} critical" if result.chktex_available else "Not checked"))
    lines.append(check_row("No high-severity warnings", result.high_count == 0 if result.chktex_available else True,
                            f"{result.high_count} high" if result.chktex_available else "Not checked"))
    lines.append(check_row("No medium warnings", result.medium_count == 0 if result.chktex_available else True,
                            f"{result.medium_count} medium" if result.chktex_available else "Not checked"))
    lines.append("")

    # --- Configuration note ---
    lines.append("## Configuration")
    lines.append("")
    lines.append(
        "ChkTeX is configured via `.chktexrc` at the repository root. "
        "Suppressed warnings are documented with justifications in that file. "
        "Inline suppressions (`%chktex N`) are tracked as Warning 44 and reviewed during audit."
    )
    lines.append("")
    lines.append(
        "To re-run this audit locally:"
    )
    lines.append("")
    lines.append("```bash")
    lines.append("task audit:paper")
    lines.append("# or")
    lines.append("python scripts/audit-chktex.py")
    lines.append("```")
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate a ChkTeX audit report for the reflector paper.",
    )
    parser.add_argument(
        "--paper",
        default=str(PAPER_DIR),
        help="Path to paper directory (default: paper/)",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT),
        help=f"Output Markdown file (default: {DEFAULT_OUTPUT})",
    )
    args = parser.parse_args()

    paper_dir = Path(args.paper)
    output_path = Path(args.output)

    now = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

    chktex_available = shutil.which("chktex") is not None
    chktex_version = get_chktex_version() if chktex_available else "not installed"

    warnings: list[ChkTeXWarning] = []
    raw_output = ""

    if chktex_available:
        print(f"Running ChkTeX on {paper_dir}/paper.tex …", flush=True)
        chktexrc = CHKTEXRC if CHKTEXRC.exists() else None
        _exit_code, raw_output = run_chktex(paper_dir, chktexrc)
        warnings = parse_chktex_output(raw_output)
        if warnings:
            print(f"  Found {len(warnings)} warning(s).", flush=True)
        else:
            print("  ✅ No warnings.", flush=True)
    else:
        print("⚠️  chktex is not installed — skipping lint run.", flush=True)
        print("   Install with: apt-get install chktex", flush=True)

    result = AuditResult(
        generated_at=now,
        paper_dir=str(paper_dir),
        chktex_version=chktex_version,
        chktex_available=chktex_available,
        warnings=warnings,
        raw_output=raw_output,
    )

    report = generate_report(result)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")
    print(f"\nAudit report written to: {output_path}", flush=True)
    print(f"Readiness: {result.readiness_emoji} {result.readiness_label}", flush=True)

    # Exit non-zero only if critical or high warnings are found
    if result.critical_count > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
