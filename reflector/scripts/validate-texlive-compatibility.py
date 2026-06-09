#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0
# validate-texlive-compatibility.py — Validate TeXLive compatibility for the paper.

from __future__ import annotations

import json
import re
import shutil
import subprocess
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
PUBLICATION_DIR = REPO_ROOT / "publication"
REPORT_OUTPUT = PUBLICATION_DIR / "compatibility-report.md"

# Packages known to be present in TeXLive 2025 base/recommended/full
# This list covers packages in reflector.sty
TEXLIVE_2025_PACKAGES: dict[str, str] = {
    "inputenc": "base",
    "fontenc": "base",
    "babel": "required",
    "lmodern": "recommended",
    "microtype": "recommended",
    "geometry": "recommended",
    "setspace": "recommended",
    "parskip": "recommended",
    "xcolor": "recommended",
    "hyperref": "recommended",
    "bookmark": "recommended",
    "biblatex": "recommended",
    "graphicx": "base",
    "float": "recommended",
    "caption": "recommended",
    "subcaption": "recommended",
    "booktabs": "recommended",
    "array": "base",
    "longtable": "recommended",
    "tabularx": "recommended",
    "listings": "recommended",
    "amsmath": "required",
    "amssymb": "required",
    "amsthm": "required",
    "mathtools": "recommended",
    "bm": "required",
    "enumitem": "recommended",
    "csquotes": "recommended",
    "multirow": "recommended",
    "makecell": "recommended",
    "cleveref": "recommended",
    "tcolorbox": "full",
    "fancyhdr": "recommended",
    "titlesec": "recommended",
}

# Packages with known pdflatex compatibility issues
PDFLATEX_INCOMPATIBLE: set[str] = {
    # These require lualatex or xelatex
    "fontspec",
    "unicode-math",
    "luatexja",
    "luacode",
}

# Packages deprecated or removed in recent TeXLive versions
DEPRECATED_PACKAGES: set[str] = {
    "epsfig",      # deprecated: use graphicx
    "subfig",      # superseded by subcaption
    "subfigure",   # superseded by subcaption
    "natbib",      # use biblatex instead (coexistence issues)
    "cite",        # incompatible with biblatex
    "ucs",         # deprecated unicode input extension
    "ae",          # use lmodern instead
    "isolatin",    # deprecated encoding
    "pslatex",     # deprecated font package
    "times",       # deprecated: use lmodern or newtxtext
    "palatino",    # deprecated: use mathpazo or newpxtext
    "mathpple",    # obsolete
}

# Packages with known conflicts with biblatex
BIBLATEX_CONFLICTS: set[str] = {
    "natbib",
    "cite",
    "chapterbib",
    "mcite",
}


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


def extract_packages(sty_text: str) -> list[tuple[str, str]]:
    """Extract (package_name, options) from \\RequirePackage and \\usepackage calls."""
    results: list[tuple[str, str]] = []
    pattern = re.compile(r"\\(?:RequirePackage|usepackage)\s*(?:\[([^\]]*)\])?\s*\{([^}]+)\}")
    for match in pattern.finditer(sty_text):
        options = (match.group(1) or "").strip()
        pkgs = match.group(2).strip()
        for pkg in pkgs.split(","):
            pkg = pkg.strip()
            if pkg:
                results.append((pkg, options))
    return results


def run_cmd(command: list[str], cwd: Path) -> tuple[int, str]:
    proc = subprocess.run(command, cwd=cwd, capture_output=True, text=True, check=False)
    output = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode, output.strip()


def gather_checks() -> list[Check]:
    checks: list[Check] = []

    # -------------------------------------------------------------------------
    # 1. TeXLive version declarations
    # -------------------------------------------------------------------------
    readme_json_path = PAPER_DIR / "00README.json"
    texlive_declared: str = ""
    compiler_declared: str = ""
    bibliography_declared: str = ""

    if readme_json_path.exists():
        try:
            readme_json = json.loads(readme_json_path.read_text(encoding="utf-8"))
            process = readme_json.get("process", {})
            texlive_declared = str(process.get("texlive", "")).strip()
            compiler_declared = str(process.get("compiler", "")).strip()
            bibliography_declared = str(process.get("bibliography", "")).strip()
        except (json.JSONDecodeError, AttributeError):
            readme_json = {}

    add_check(
        checks,
        "TeXLive declarations",
        "TeXLive version declared in 00README.json",
        bool(texlive_declared),
        f"TeXLive version declared: {texlive_declared!r}.",
        "process.texlive is not declared in paper/00README.json.",
    )

    # Validate the declared version is current
    try:
        texlive_year = int(texlive_declared)
        is_current = texlive_year >= 2025
    except ValueError:
        texlive_year = 0
        is_current = False

    add_check(
        checks,
        "TeXLive declarations",
        "Declared TeXLive version is current (2025+)",
        is_current,
        f"Declared TeXLive {texlive_year} is a current release (2025 or later).",
        f"Declared TeXLive version {texlive_declared!r} is older than 2025 or not a valid year.",
        warn=True,
    )

    add_check(
        checks,
        "TeXLive declarations",
        "Compiler is declared in 00README.json",
        bool(compiler_declared),
        f"Compiler declared: {compiler_declared!r}.",
        "process.compiler is not declared in paper/00README.json.",
    )

    add_check(
        checks,
        "TeXLive declarations",
        "Bibliography backend declared in 00README.json",
        bool(bibliography_declared),
        f"Bibliography backend declared: {bibliography_declared!r}.",
        "process.bibliography is not declared in paper/00README.json.",
    )

    # -------------------------------------------------------------------------
    # 2. Package compatibility with TeXLive 2025
    # -------------------------------------------------------------------------
    sty_path = PAPER_DIR / "styles" / "reflector.sty"
    if sty_path.exists():
        sty_text = sty_path.read_text(encoding="utf-8")
        packages = extract_packages(sty_text)
        package_names = [name for name, _ in packages]

        # Check all packages are known in TeXLive 2025
        unknown_packages = [
            pkg for pkg in package_names
            if pkg not in TEXLIVE_2025_PACKAGES
        ]
        add_check(
            checks,
            "Package compatibility",
            "All packages are known in TeXLive 2025",
            not unknown_packages,
            f"All {len(package_names)} packages in reflector.sty are listed in the TeXLive 2025 package set.",
            "Packages not verified in TeXLive 2025 package set: " + ", ".join(unknown_packages),
            warn=True,  # WARN since our list may be incomplete
        )

        # Deprecated packages
        deprecated_used = [pkg for pkg in package_names if pkg in DEPRECATED_PACKAGES]
        add_check(
            checks,
            "Package compatibility",
            "No deprecated packages used",
            not deprecated_used,
            "No deprecated or superseded packages found in reflector.sty.",
            "Deprecated packages found: " + ", ".join(deprecated_used),
        )

        # pdflatex compatibility
        if compiler_declared == "pdflatex":
            incompatible_with_pdflatex = [pkg for pkg in package_names if pkg in PDFLATEX_INCOMPATIBLE]
            add_check(
                checks,
                "Package compatibility",
                "All packages are pdflatex-compatible",
                not incompatible_with_pdflatex,
                "All packages in reflector.sty are compatible with pdflatex.",
                "Packages incompatible with pdflatex: " + ", ".join(incompatible_with_pdflatex),
            )

        # biblatex conflict check
        biblatex_conflicting = [pkg for pkg in package_names if pkg in BIBLATEX_CONFLICTS]
        add_check(
            checks,
            "Package compatibility",
            "No biblatex-incompatible packages used",
            not biblatex_conflicting,
            "No packages conflicting with biblatex are used.",
            "Packages conflicting with biblatex: " + ", ".join(biblatex_conflicting),
        )
    else:
        checks.append(Check(
            area="Package compatibility",
            name="Style file exists",
            status="FAIL",
            details="paper/styles/reflector.sty not found.",
        ))

    # -------------------------------------------------------------------------
    # 3. Compiler compatibility
    # -------------------------------------------------------------------------
    if sty_path.exists():
        sty_text = sty_path.read_text(encoding="utf-8")

        # inputenc — required for pdflatex, not needed for lualatex/xelatex
        uses_inputenc = "inputenc" in sty_text
        if compiler_declared in ("pdflatex", "latex", ""):
            add_check(
                checks,
                "Compiler compatibility",
                "inputenc is declared for pdflatex",
                uses_inputenc,
                "inputenc is declared — required for pdflatex UTF-8 input handling.",
                "inputenc is not declared; pdflatex may mishandle UTF-8 input.",
            )

        # fontenc T1 — standard for pdflatex
        uses_fontenc_t1 = "[T1]{fontenc}" in sty_text or "T1" in sty_text and "fontenc" in sty_text
        add_check(
            checks,
            "Compiler compatibility",
            "fontenc with T1 encoding declared",
            uses_fontenc_t1,
            "fontenc with T1 encoding is declared for proper glyph support.",
            "fontenc with T1 encoding is not declared.",
        )

        # babel
        uses_babel = "babel" in sty_text
        add_check(
            checks,
            "Compiler compatibility",
            "babel language support declared",
            uses_babel,
            "babel language package is declared.",
            "babel is not declared; language-specific hyphenation may not function correctly.",
        )

        # biblatex backend
        uses_biblatex = "biblatex" in sty_text
        if uses_biblatex:
            biblatex_backend_biber = "backend=biber" in sty_text
            add_check(
                checks,
                "Compiler compatibility",
                "biblatex uses biber backend",
                biblatex_backend_biber,
                "biblatex is configured with backend=biber.",
                "biblatex is used but backend=biber is not declared; defaulting to bibtex may cause issues.",
            )

        # lmodern (preferred over obsolete font packages)
        uses_lmodern = "lmodern" in sty_text
        add_check(
            checks,
            "Compiler compatibility",
            "lmodern font package used",
            uses_lmodern,
            "lmodern is used for modern T1-encoded Latin Modern fonts.",
            "lmodern is not used; font rendering may be suboptimal on some TeXLive installations.",
            warn=True,
        )

        # microtype (pdflatex compatible)
        uses_microtype = "microtype" in sty_text
        if compiler_declared in ("pdflatex", "lualatex", ""):
            add_check(
                checks,
                "Compiler compatibility",
                "microtype is declared for typography",
                uses_microtype,
                "microtype is declared for pdflatex/lualatex micro-typography.",
                "microtype is not declared.",
                warn=True,
            )

    # -------------------------------------------------------------------------
    # 4. Encoding compatibility
    # -------------------------------------------------------------------------
    paper_tex_path = PAPER_DIR / "paper.tex"
    if paper_tex_path.exists():
        paper_text = paper_tex_path.read_text(encoding="utf-8")
        # Confirm UTF-8 encoding of the file itself
        try:
            paper_tex_path.read_text(encoding="utf-8")
            utf8_ok = True
        except UnicodeDecodeError:
            utf8_ok = False
        add_check(
            checks,
            "Encoding compatibility",
            "paper.tex is valid UTF-8",
            utf8_ok,
            "paper.tex is encoded as valid UTF-8.",
            "paper.tex contains non-UTF-8 byte sequences.",
        )

    if sty_path.exists():
        sty_text = sty_path.read_text(encoding="utf-8")
        uses_utf8_inputenc = "[utf8]{inputenc}" in sty_text or "utf8" in sty_text
        add_check(
            checks,
            "Encoding compatibility",
            "UTF-8 input encoding declared",
            uses_utf8_inputenc,
            "inputenc[utf8] is declared for UTF-8 source file support.",
            "UTF-8 input encoding is not explicitly declared in the style.",
        )

    # Check all .tex files are valid UTF-8
    tex_encoding_failures: list[str] = []
    for tex_file in sorted(PAPER_DIR.rglob("*.tex")):
        try:
            tex_file.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            tex_encoding_failures.append(str(tex_file.relative_to(PAPER_DIR)))
    add_check(
        checks,
        "Encoding compatibility",
        "All .tex files are valid UTF-8",
        not tex_encoding_failures,
        f"All .tex files under paper/ are valid UTF-8.",
        "Non-UTF-8 .tex files found: " + ", ".join(tex_encoding_failures),
    )

    # -------------------------------------------------------------------------
    # 5. TeXLive toolchain availability (runtime check)
    # -------------------------------------------------------------------------
    for tool in ("latexmk", "pdflatex", "biber"):
        found = shutil.which(tool) is not None
        add_check(
            checks,
            "Toolchain availability",
            f"{tool} is available",
            found,
            f"{tool} is available in PATH.",
            f"{tool} is not available in PATH — install TeXLive to enable local builds.",
            warn=True,  # WARN: environment may not have TeXLive; CI will
        )

    if shutil.which("pdflatex"):
        code, output = run_cmd(["pdflatex", "--version"], REPO_ROOT)
        version_line = output.splitlines()[0] if output else "(no output)"
        add_check(
            checks,
            "Toolchain availability",
            "pdflatex version reported",
            code == 0,
            f"pdflatex version: {version_line}",
            "pdflatex --version failed.",
        )

    if shutil.which("biber"):
        code, output = run_cmd(["biber", "--version"], REPO_ROOT)
        version_line = output.splitlines()[0] if output else "(no output)"
        add_check(
            checks,
            "Toolchain availability",
            "biber version reported",
            code == 0,
            f"biber version: {version_line}",
            "biber --version failed.",
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
    lines.append("# TeXLive Compatibility Report")
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
        lines.append("Overall result: ✅ **Fully TeXLive-compatible**")
    elif fail_count == 0:
        lines.append("Overall result: ⚠️ **Conditionally compatible** (non-failing issues remain)")
    else:
        lines.append("Overall result: ❌ **Compatibility concerns detected**")
    lines.append("")

    lines.append("## Goal Checklist")
    lines.append("")
    lines.append(f"- [{mark(area_ok('TeXLive declarations'))}] TeXLive version and toolchain declared")
    lines.append(f"- [{mark(area_ok('Package compatibility'))}] All packages compatible with TeXLive 2025")
    lines.append(f"- [{mark(area_ok('Compiler compatibility'))}] Compiler-specific package configuration validated")
    lines.append(f"- [{mark(area_ok('Encoding compatibility'))}] UTF-8 encoding declared and consistent")
    lines.append(f"- [{mark(area_ok('Toolchain availability'))}] TeXLive toolchain available in environment")
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

    # Package matrix section
    sty_path = PAPER_DIR / "styles" / "reflector.sty"
    if sty_path.exists():
        sty_text = sty_path.read_text(encoding="utf-8")
        packages = extract_packages(sty_text)
        if packages:
            lines.append("## Package Compatibility Matrix")
            lines.append("")
            lines.append("Packages declared in `paper/styles/reflector.sty` against TeXLive 2025:")
            lines.append("")
            lines.append("| Package | TeXLive 2025 Collection | pdflatex Compatible | Notes |")
            lines.append("| --- | --- | --- | --- |")
            for pkg, opts in packages:
                collection = TEXLIVE_2025_PACKAGES.get(pkg, "⚠️ unverified")
                pdflatex_ok = "✅" if pkg not in PDFLATEX_INCOMPATIBLE else "❌"
                deprecated = " *(deprecated)*" if pkg in DEPRECATED_PACKAGES else ""
                biblatex_conflict = " *(biblatex conflict)*" if pkg in BIBLATEX_CONFLICTS else ""
                notes = deprecated + biblatex_conflict if (deprecated or biblatex_conflict) else "—"
                lines.append(f"| `{pkg}` | {collection} | {pdflatex_ok} | {notes} |")
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
            if "not available in PATH" in check.details:
                tool = check.name.split()[0]
                lines.append(f"- Install `{tool}` via TeXLive (`tlmgr install {tool}`) or install full TeXLive 2025.")
            elif "TeXLive version" in check.name and "older" in check.details:
                lines.append(
                    "- Update the declared TeXLive version in `paper/00README.json` `process.texlive` "
                    "to match the current TeXLive release year."
                )
            elif "unverified" in check.details:
                lines.append(
                    f"- Verify `{check.name}` package compatibility with TeXLive 2025 "
                    "using `tlmgr info <package>`."
                )
            else:
                lines.append(f"- Resolve: **{check.area} / {check.name}**.")
        lines.append("")

    lines.append("## TeXLive 2025 Compatibility Assessment")
    lines.append("")
    if fail_count == 0:
        confidence = "High" if warn_count == 0 else "Medium"
        lines.append(f"**Compatibility confidence: {confidence}**")
        lines.append("")
        lines.append(
            "The reflector paper style (`reflector.sty`) uses well-established LaTeX packages "
            "that have been part of TeXLive for many years and are compatible with TeXLive 2025. "
            "The pdflatex + biber + biblatex combination is the recommended arXiv compilation stack."
        )
    else:
        lines.append("**Compatibility confidence: Low**")
        lines.append("")
        lines.append("One or more compatibility-critical checks failed. Review and resolve failing checks above.")
    lines.append("")

    PUBLICATION_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    checks = gather_checks()
    write_report(checks)
    fail_count = sum(1 for c in checks if c.status == "FAIL")
    warn_count = sum(1 for c in checks if c.status == "WARN")
    print(f"[validate-texlive-compatibility] report written to {REPORT_OUTPUT}")
    print(f"[validate-texlive-compatibility] pass={sum(1 for c in checks if c.status == 'PASS')} warn={warn_count} fail={fail_count}")
    return 1 if fail_count > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
