#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0
# watch-paper.sh — Watch a LaTeX paper directory and rebuild on changes.
#
# Usage:
#   ./scripts/watch-paper.sh <paper-path|paper-slug>
#
# Examples:
#   ./scripts/watch-paper.sh paper
#   ./scripts/watch-paper.sh reflector
#
# Requirements:
#   - latexmk (with -pvc flag for continuous preview)
#   - pdflatex or xelatex
#   - biber (for biblatex)

set -euo pipefail

TARGET="${1:-}"

if [[ -z "${TARGET}" ]]; then
  echo "Usage: $0 <paper-path|paper-slug>" >&2
  echo "Examples: $0 paper | $0 reflector" >&2
  exit 1
fi

PAPER_DIR="${TARGET}"

if [[ ( "${TARGET}" == "paper" || "${TARGET}" == "reflector" ) && -d "paper" ]]; then
  PAPER_DIR="paper"
fi

if [[ ! -d "${PAPER_DIR}" ]]; then
  echo "Error: Directory '${PAPER_DIR}' not found." >&2
  exit 1
fi

PAPER_TEX="${PAPER_DIR}/paper.tex"

if [[ ! -f "${PAPER_TEX}" ]]; then
  echo "Error: '${PAPER_TEX}' not found." >&2
  exit 1
fi

mkdir -p "${PAPER_DIR}/.cache/aux" "${PAPER_DIR}/.cache/out"

echo "Watching: ${PAPER_DIR}/"
echo "Output:   ${PAPER_DIR}/.cache/out/"
echo "Press Ctrl+C to stop."
echo ""

(
  cd "${PAPER_DIR}"

  latexmk \
    -pdf \
    -interaction=nonstopmode \
    -synctex=1 \
    -file-line-error \
    -shell-escape \
    -f \
    -gg \
    -cd \
    -r "../.latexmkrc" \
    -pvc \
    "paper.tex"
)
