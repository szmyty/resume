#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0
# print-latex-diagnostics.sh — Emit focused LaTeX diagnostics from cached build logs.

set -euo pipefail

PAPER_DIR="${1:-paper}"
LOG_TAIL_LINES="${LATEX_LOG_TAIL_LINES:-120}"
AUX_DIR="${PAPER_DIR}/.cache/aux"
OUT_DIR="${PAPER_DIR}/.cache/out"
LOG_FILE="${AUX_DIR}/paper.log"
BLG_FILE="${AUX_DIR}/paper.blg"
PDF_FILE="${OUT_DIR}/paper.pdf"

begin_group() {
    local title="$1"

    if [[ -n "${GITHUB_ACTIONS:-}" ]]; then
        echo "::group::${title}"
    else
        echo "=== ${title} ==="
    fi
}

end_group() {
    if [[ -n "${GITHUB_ACTIONS:-}" ]]; then
        echo "::endgroup::"
    else
        echo
    fi
}

print_section() {
    local title="$1"
    shift

    begin_group "${title}"
    "$@"
    end_group
}

print_tail() {
    local file_path="$1"

    if [[ -f "${file_path}" ]]; then
        tail -n "${LOG_TAIL_LINES}" "${file_path}"
    else
        echo "Not found: ${file_path}"
    fi
}

print_matches() {
    local file_path="$1"
    local pattern="$2"

    if [[ ! -f "${file_path}" ]]; then
        echo "Not found: ${file_path}"
        return
    fi

    local matches
    matches="$(grep -nE "${pattern}" "${file_path}" || true)"

    if [[ -n "${matches}" ]]; then
        printf '%s\n' "${matches}"
    else
        echo "No matches found."
    fi
}

print_status() {
    echo "Paper directory: ${PAPER_DIR}"
    echo "Aux directory:   ${AUX_DIR}"
    echo "Output directory: ${OUT_DIR}"
    echo "LaTeX log:       ${LOG_FILE}"
    echo "Biber log:       ${BLG_FILE}"
    echo "Partial PDF:     ${PDF_FILE}"

    if [[ -f "${PDF_FILE}" ]]; then
        ls -lh "${PDF_FILE}"
    else
        echo "Partial PDF not found."
    fi
}

print_section "LaTeX diagnostics summary" print_status
print_section "LATEX LOG TAIL" print_tail "${LOG_FILE}"
print_section "LIKELY LATEX FAILURES" print_matches "${LOG_FILE}" "^(\\! )|(LaTeX Error:)|(Emergency stop)|(Fatal error)|(Runaway argument\\?)|(Undefined control sequence)|(Package [^:]+ Error:)"
print_section "MISSING FILES OR INCLUDES" print_matches "${LOG_FILE}" "(LaTeX Error: File .+ not found)|(I can't find file)|(Unable to load picture or PDF file)|(Cannot determine size of graphic)|(Package pdftex\\.def Error:)"
print_section "REFERENCE WARNINGS" print_matches "${LOG_FILE}" "(undefined references)|(undefined citations)|(Citation .+ undefined)|(Reference .+ undefined)|(Please \\(re\\)run Biber)"
print_section "BIBER OUTPUT" print_tail "${BLG_FILE}"
print_section "BIBER WARNINGS" print_matches "${BLG_FILE}" "^(WARN|ERROR) -"
