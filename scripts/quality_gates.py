#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0
"""quality_gates.py — Repository quality validation helpers."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

import build


REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_PLACEHOLDER_PATHS = (
    "resume.tex",
    "sections/*.tex",
    "profiles/*.yaml",
)
PLACEHOLDER_PATTERNS = (
    re.compile(r"\bTODO\b", flags=re.IGNORECASE),
    re.compile(r"\bFIXME\b", flags=re.IGNORECASE),
    re.compile(r"\bplaceholder\b", flags=re.IGNORECASE),
    re.compile(r"\bTBD\b", flags=re.IGNORECASE),
)
DEFAULT_REQUIRED_HEADINGS = ("Summary", "Experience", "Education", "Skills")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run repository quality gate checks.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("validate-profiles", help="Validate profile YAML definitions.")

    placeholders = subparsers.add_parser(
        "check-placeholders",
        help="Fail when unresolved placeholder content is present.",
    )
    placeholders.add_argument(
        "--path",
        action="append",
        default=[],
        help="Glob path (relative to repository root) to scan. Repeatable.",
    )

    ats = subparsers.add_parser(
        "validate-ats",
        help="Validate machine-readable ATS text extraction from a generated PDF.",
    )
    ats.add_argument("--pdf", required=True, help="Path to PDF file to validate.")
    ats.add_argument(
        "--require-heading",
        action="append",
        default=[],
        help="Required heading in extracted text. Repeatable.",
    )
    ats.add_argument(
        "--summary-file",
        default=None,
        help="Optional markdown summary output file path.",
    )
    return parser.parse_args()


def validate_profiles() -> int:
    try:
        profiles = build.load_profiles()
    except ValueError as exc:
        print(f"Profile validation failed: {exc}", file=sys.stderr)
        return 1

    errors: list[str] = []
    for profile_path in sorted(build.PROFILES_DIR.glob("*.yaml")):
        profile = build.load_profile(profile_path)
        if profile.profile != profile_path.stem:
            errors.append(
                f"{profile_path}: expected profile id '{profile_path.stem}' "
                f"to match filename, found '{profile.profile}'."
            )
        if not profile.keyword_emphasis:
            errors.append(f"{profile_path}: keyword_emphasis must include at least one value.")

    if errors:
        print("Profile validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print(f"Validated {len(profiles)} profile definition(s).")
    return 0


def check_placeholders(paths: list[str]) -> int:
    scan_paths = paths or list(DEFAULT_PLACEHOLDER_PATHS)
    findings: list[str] = []

    for relative in scan_paths:
        for candidate in sorted(REPOSITORY_ROOT.glob(relative)):
            if not candidate.is_file():
                continue

            for line_number, line in enumerate(candidate.read_text(encoding="utf-8").splitlines(), 1):
                stripped = line.strip()
                if not stripped:
                    continue
                if stripped.startswith(("#", "%")):
                    continue

                for pattern in PLACEHOLDER_PATTERNS:
                    if pattern.search(line):
                        findings.append(
                            f"{candidate.relative_to(REPOSITORY_ROOT)}:{line_number}: {stripped}"
                        )
                        break

    if findings:
        print("Placeholder content detected:")
        for finding in findings:
            print(f"  - {finding}")
        return 1

    print("No placeholder content detected.")
    return 0


def validate_ats(pdf: Path, required_headings: list[str], summary_file: str | None) -> int:
    if not pdf.exists():
        print(f"ATS validation failed: PDF not found at '{pdf}'.", file=sys.stderr)
        return 1

    if shutil.which("pdftotext") is None:
        print("ATS validation failed: 'pdftotext' is not installed or not on PATH.", file=sys.stderr)
        return 1

    extracted = subprocess.run(
        ["pdftotext", str(pdf), "-"],
        check=False,
        capture_output=True,
        text=True,
    )
    if extracted.returncode != 0:
        print(
            f"ATS validation failed: pdftotext exited with code {extracted.returncode}.",
            file=sys.stderr,
        )
        if extracted.stderr:
            print(extracted.stderr.strip(), file=sys.stderr)
        return 1

    text = extracted.stdout
    normalized = text.casefold()
    headings = required_headings or list(DEFAULT_REQUIRED_HEADINGS)
    missing = [
        heading
        for heading in headings
        if re.search(rf"\b{re.escape(heading.casefold())}\b", normalized) is None
    ]

    errors: list[str] = []
    if not text.strip():
        errors.append("Extracted text is empty.")
    if len(text.strip()) < 200:
        errors.append("Extracted text is unexpectedly short (< 200 characters).")
    if missing:
        errors.append(f"Missing required headings: {', '.join(missing)}.")

    if summary_file:
        write_summary(Path(summary_file), pdf, text, missing, errors)

    if errors:
        print("ATS validation failed:")
        for error in errors:
            print(f"  - {error}")
        return 1

    print(f"ATS validation passed for '{pdf}' ({len(text.strip())} extracted characters).")
    return 0


def write_summary(
    summary_path: Path,
    pdf: Path,
    text: str,
    missing_headings: list[str],
    errors: list[str],
) -> None:
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    status = "✅ PASS" if not errors else "❌ FAIL"
    missing = ", ".join(missing_headings) if missing_headings else "None"
    character_count = len(text.strip())
    with summary_path.open("a", encoding="utf-8") as handle:
        handle.write("## ATS Extraction Validation\n\n")
        handle.write(f"- Status: {status}\n")
        handle.write(f"- PDF: `{pdf}`\n")
        handle.write(f"- Extracted characters: `{character_count}`\n")
        handle.write(f"- Missing required headings: `{missing}`\n")
        if errors:
            handle.write("- Errors:\n")
            for error in errors:
                handle.write(f"  - {error}\n")
        handle.write("\n")


def main() -> int:
    args = parse_args()
    if args.command == "validate-profiles":
        return validate_profiles()
    if args.command == "check-placeholders":
        return check_placeholders(args.path)
    if args.command == "validate-ats":
        return validate_ats(
            pdf=Path(args.pdf),
            required_headings=args.require_heading,
            summary_file=args.summary_file,
        )
    raise ValueError(f"Unsupported command '{args.command}'.")


if __name__ == "__main__":
    sys.exit(main())
