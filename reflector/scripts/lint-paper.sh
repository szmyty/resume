#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0
# lint-paper.sh — Run ChkTeX on the reflector paper and report findings.
#
# Usage:
#   ./scripts/lint-paper.sh [paper-dir] [--output FILE] [--format FORMAT]
#
# Arguments:
#   paper-dir       Path to paper directory (default: paper)
#   --output FILE   Write ChkTeX output to FILE in addition to stdout
#   --format FORMAT Output format: full (default) or counts
#
# Exit codes:
#   0   No active ChkTeX warnings found
#   1   One or more ChkTeX warnings found
#   2   chktex is not installed
#   3   Paper source file not found
#
# SUPPRESSED WARNINGS
# -------------------
# The following warnings are suppressed via -n flags because they produce
# systematic false positives for this document class and writing style.
# Each suppression is documented with its justification below.
#
# Warning  1 — "Command terminated with space."
#              Justification: Macros in metadata.tex use \cmd\ for explicit
#              spacing. Suppressed globally; controlled instead by .chktexrc
#              Silent list which adds reflector macros to chktex's allowed set.
#
# Warning  3 — "You should enclose the previous parenthesis with {}."
#              Justification: False positive when parentheses appear inside
#              displaymath or align environments. Math delimiters are intentional.
#
# Warning  9 — "Could not find included file."
#              Justification: ChkTeX resolves \input paths relative to the CWD
#              and does not honour TEXINPUTS. reflector uses .latexmkrc TEXINPUTS
#              which adds ./sections//, ./macros//, etc. File existence is
#              validated by the build step and audit-publication-readiness.py.
#
# Warning 16 — "Protect \footnote, \thanks, \label, \ref, etc."
#              Justification: reflector.sty loads hyperref which makes these
#              commands robust. False positives dominate in section headings.
#
# Warning 25 — "You should remove spaces before punctuation."
#              Justification: False positives from display-math endings before
#              external punctuation. The compiled output is typographically correct.
#
# Warning 26 — "You should remove spaces before this char."
#              Justification: Overlaps with Warning 25; same class of false
#              positives from spacing around math environments.
#
# Warning 30 — "Multiple space character in input."
#              Justification: Visual alignment whitespace in tabular and
#              listings environments for source readability; not a typographic error.
#
# Warning 42 — "You should avoid starting a paragraph with a formula."
#              Justification: Technical writing conventions permit this in
#              theorems, definitions, and numbered equations.
#
# Warning 45 — "Use \( \) instead of $ $."
#              Justification: reflector.sty uses $ $ for inline math throughout;
#              the style is internally consistent and common in academic papers.
#
# Warning 46 — "Use \[ \] instead of $$ $$."
#              Justification: The manuscript does not use $$; if encountered it
#              is caught at compilation as a higher-priority error.

set -euo pipefail

REPOSITORY_ROOT="$(git rev-parse --show-toplevel)"

PAPER_DIR_ARG="paper"
OUTPUT_FILE=""
FORMAT="full"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --output)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        --format)
            FORMAT="$2"
            shift 2
            ;;
        --help)
            head -25 "$0" | grep "^#" | sed 's/^# \?//'
            exit 0
            ;;
        *)
            PAPER_DIR_ARG="$1"
            shift
            ;;
    esac
done

# Resolve paper directory (absolute or relative to repo root)
if [[ "${PAPER_DIR_ARG}" = /* ]]; then
    PAPER_DIR="${PAPER_DIR_ARG}"
else
    PAPER_DIR="${REPOSITORY_ROOT}/${PAPER_DIR_ARG}"
fi

PAPER_TEX="${PAPER_DIR}/paper.tex"
CHKTEXRC="${REPOSITORY_ROOT}/.chktexrc"

# ---------------------------------------------------------------------------
# Preflight checks
# ---------------------------------------------------------------------------

if ! command -v chktex >/dev/null 2>&1; then
    echo "❌ chktex is not installed." >&2
    echo "   Install it with: apt-get install chktex" >&2
    echo "   Or via TeX Live: tlmgr install chktex" >&2
    exit 2
fi

if [[ ! -f "${PAPER_TEX}" ]]; then
    echo "❌ Paper source not found: ${PAPER_TEX}" >&2
    exit 3
fi

# ---------------------------------------------------------------------------
# Banner
# ---------------------------------------------------------------------------

if [[ -n "${GITHUB_ACTIONS:-}" ]]; then
    echo "::group::ChkTeX — ${PAPER_DIR_ARG}"
fi

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo " ChkTeX — Publication Lint"
echo " Paper:   ${PAPER_TEX}"
if [[ -f "${CHKTEXRC}" ]]; then
    echo " Config:  ${CHKTEXRC}"
else
    echo " Config:  (none — using chktex defaults)"
fi
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# ---------------------------------------------------------------------------
# Build ChkTeX options
# ---------------------------------------------------------------------------

CHKTEX_OPTS=(
    -v0               # Parseable format: file:line:col:warning_num:message
    -q                # Suppress banner
)

# Ensure TERM is set to avoid cosmetic "terminal type is null" message from chktex
export TERM="${TERM:-dumb}"

# Load repository config if present
if [[ -f "${CHKTEXRC}" ]]; then
    CHKTEX_OPTS+=( -l "${CHKTEXRC}" )
fi

# Suppressed warnings (see justifications in the header comment above)
# W1  — command terminated with space (handled by .chktexrc Silent list instead)
# W3  — parenthesis enclosure in math (false positives)
# W9  — included file not found (TEXINPUTS not honoured by chktex)
# W16 — protect commands (hyperref makes them robust)
# W24 — "delete this space" before \label (false positive: paper places \label on
#         its own line after \section{...}, which is a standard formatting convention)
# W25 — space before punctuation (math-mode false positives)
# W26 — space before char (overlaps with W25)
# W30 — multiple spaces (alignment whitespace)
# W42 — paragraph starting with formula (technical writing style)
# W45 — use \( \) instead of $ $ (consistent style choice)
# W46 — use \[ \] instead of $$ $$ (manuscript does not use $$)
for warn_num in 1 3 9 16 24 25 26 30 42 45 46; do
    CHKTEX_OPTS+=( -n "${warn_num}" )
done

# ---------------------------------------------------------------------------
# Run ChkTeX
# ---------------------------------------------------------------------------

# Change to paper directory so \input paths resolve correctly
cd "${PAPER_DIR}"

set +e
CHKTEX_OUTPUT="$(chktex "${CHKTEX_OPTS[@]}" paper.tex 2>&1)"
CHKTEX_EXIT=$?
set -e

cd "${REPOSITORY_ROOT}"

# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

WARNING_COUNT="$(echo "${CHKTEX_OUTPUT}" | grep -c "^.*:[0-9]*:[0-9]*:" 2>/dev/null || true)"

if [[ "${FORMAT}" == "counts" ]]; then
    echo "Warnings found: ${WARNING_COUNT}"
else
    if [[ -z "${CHKTEX_OUTPUT}" ]]; then
        echo ""
        echo "✅ No ChkTeX warnings found."
    else
        echo ""
        echo "${CHKTEX_OUTPUT}"
        echo ""
        echo "─────────────────────────────────────────────────────────"
        if [[ "${WARNING_COUNT}" -gt 0 ]]; then
            echo "⚠️  Total warnings: ${WARNING_COUNT}"
        else
            echo "✅ No warnings."
        fi
    fi
fi

# Write output to file if requested
if [[ -n "${OUTPUT_FILE}" ]]; then
    mkdir -p "$(dirname "${OUTPUT_FILE}")"
    printf '%s\n' "${CHKTEX_OUTPUT}" > "${OUTPUT_FILE}"
    echo "Output written to: ${OUTPUT_FILE}"
fi

if [[ -n "${GITHUB_ACTIONS:-}" ]]; then
    echo "::endgroup::"
fi

exit "${CHKTEX_EXIT}"
