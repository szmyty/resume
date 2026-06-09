#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0
"""build.py — Build resume PDF from LaTeX source.

Usage:
    python scripts/build.py [--profile PROFILE] [--open]

Options:
    --profile PROFILE   Profile variant to build (default: none, builds base resume)
    --open              Open the generated PDF after building
    --help              Show this help message
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
OUTPUTS_DIR = REPOSITORY_ROOT / "outputs"
CACHE_DIR = REPOSITORY_ROOT / ".cache"
OUT_DIR = CACHE_DIR / "out"
AUX_DIR = CACHE_DIR / "aux"
LATEXMKRC = REPOSITORY_ROOT / ".latexmkrc"
RESUME_TEX = REPOSITORY_ROOT / "resume.tex"
OUTPUT_PDF = OUT_DIR / "resume.pdf"
FINAL_PDF = OUTPUTS_DIR / "resume.pdf"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build resume PDF from LaTeX source.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--profile",
        metavar="PROFILE",
        default=None,
        help="Profile variant to build (e.g. ai-infra, platform, research, fullstack).",
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

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    AUX_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

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
        str(RESUME_TEX),
    ]

    profile_label = f" [{args.profile}]" if args.profile else ""
    print(f"Building resume{profile_label}...")
    print(f"  Source:  {RESUME_TEX}")
    print(f"  Output:  {OUT_DIR}/")

    result = subprocess.run(cmd, cwd=REPOSITORY_ROOT)

    if result.returncode != 0:
        print("LaTeX build failed.", file=sys.stderr)
        sys.exit(1)

    if not OUTPUT_PDF.exists():
        print(f"Error: Expected PDF not found at '{OUTPUT_PDF}'.", file=sys.stderr)
        sys.exit(1)

    shutil.copy2(OUTPUT_PDF, FINAL_PDF)
    print(f"Build complete: {FINAL_PDF}")

    if args.open:
        _open_pdf(FINAL_PDF)


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
