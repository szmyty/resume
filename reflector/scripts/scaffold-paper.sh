#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0
# scaffold-paper.sh — Scaffold a new paper from the shared template.
#
# Usage:
#   ./scripts/scaffold-paper.sh [paper|reflector]

set -euo pipefail

PAPER_SLUG="${1:-paper}"

if [[ "${PAPER_SLUG}" != "reflector" && "${PAPER_SLUG}" != "paper" ]]; then
  echo "Usage: $0 [paper|reflector]" >&2
  exit 1
fi

PAPER_DIR="paper"

if [[ -d "${PAPER_DIR}" ]]; then
  echo "Error: '${PAPER_DIR}' already exists." >&2
  exit 1
fi

TEMPLATE_DIR="templates/paper"

if [[ ! -d "${TEMPLATE_DIR}" ]]; then
  echo "Error: Template directory '${TEMPLATE_DIR}' not found." >&2
  exit 1
fi

echo "Scaffolding: ${PAPER_DIR}"

cp -r "${TEMPLATE_DIR}" "${PAPER_DIR}"

# Remove .gitkeep files (real files will fill these directories)
find "${PAPER_DIR}" -name ".gitkeep" -delete

echo ""
echo "Done! Paper scaffolded at: ${PAPER_DIR}/"
echo ""
echo "Next steps:"
echo "  1. Update ${PAPER_DIR}/README.md with paper metadata"
echo "  2. Update ${PAPER_DIR}/paper.tex with paper title and author"
echo "  3. Add sections to ${PAPER_DIR}/sections/"
echo "  4. Build with: ./scripts/build-paper.sh ${PAPER_DIR}"
