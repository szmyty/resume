#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0
# build-magazine.sh — Build and validate magazine PDF artifacts.
#
# Usage:
#   ./scripts/build-magazine.sh [doctor|build|build-print|build-all|clean]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPOSITORY_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
MAGAZINE_DIR="${REPOSITORY_ROOT}/magazine"
TEX_DIR="${MAGAZINE_DIR}/tex"
PAGES_DIR="${MAGAZINE_DIR}/pages"
PROMPTS_DIR="${MAGAZINE_DIR}/prompts"
DIST_DIR="${MAGAZINE_DIR}/dist"
CACHE_AUX_DIR="${MAGAZINE_DIR}/.cache/aux"
CACHE_OUT_DIR="${MAGAZINE_DIR}/.cache/out"
LATEXMKRC_FILE="${TEX_DIR}/.latexmkrc"

readonly -a PAGE_FILES=(
  "page01-cover.png"
  "page02-what-is-reflector.png"
  "page03-recursive-drift.png"
  "page04-synchronization.png"
  "page05-recursive-loop.png"
  "page06-mixed-initiative-systems.png"
  "page07-distributed-cognition.png"
  "page08-governance-is-infrastructure.png"
  "page09-reflector-framework.png"
  "page10-reflector-in-ten-ideas.png"
  "page11-standing-on-the-shoulders-of-giants.png"
  "page12-future-directions.png"
  "page13-the-future-is-synchronized.png"
  "page14-back-cover.png"
)

readonly -a PROMPT_FILES=(
  "page01-cover.prompt.md"
  "page02-inside-cover.prompt.md"
  "page03-recursive-drift.prompt.md"
  "page04-synchronization.prompt.md"
  "page05-recursive-loop.prompt.md"
  "page06-mixed-initiative.prompt.md"
  "page07-distributed-cognition.prompt.md"
  "page08-governance.prompt.md"
  "page09-reflector-framework.prompt.md"
  "page10-key-insights.prompt.md"
  "page11-inspirations.prompt.md"
  "page12-future-directions.prompt.md"
  "page13-closing-reflection.prompt.md"
  "page14-back-cover.prompt.md"
)

usage() {
  head -7 "$0" | grep "^#" | sed 's/^# \?//'
}

validate_assets() {
  local expected_count="${#PAGE_FILES[@]}"
  local index page_file prompt_file page_prefix prompt_prefix expected_prefix

  if [[ "${#PROMPT_FILES[@]}" -ne "${expected_count}" ]]; then
    echo "Error: Internal configuration mismatch: PAGE_FILES and PROMPT_FILES differ in length." >&2
    exit 1
  fi

  if [[ ! -d "${PAGES_DIR}" ]]; then
    echo "Error: Missing pages directory at '${PAGES_DIR}'." >&2
    exit 1
  fi

  if [[ ! -d "${PROMPTS_DIR}" ]]; then
    echo "Error: Missing prompts directory at '${PROMPTS_DIR}'." >&2
    exit 1
  fi

  local page_count
  page_count="$(find "${PAGES_DIR}" -maxdepth 1 -type f -name 'page*.png' | wc -l | tr -d ' ')"
  if [[ "${page_count}" -ne "${expected_count}" ]]; then
    echo "Error: Expected ${expected_count} page images, found ${page_count}." >&2
    exit 1
  fi

  local prompt_count
  prompt_count="$(find "${PROMPTS_DIR}" -maxdepth 1 -type f -name 'page*.prompt.md' | wc -l | tr -d ' ')"
  if [[ "${prompt_count}" -ne "${expected_count}" ]]; then
    echo "Error: Expected ${expected_count} prompt files, found ${prompt_count}." >&2
    exit 1
  fi

  if [[ "${page_count}" -ne "${prompt_count}" ]]; then
    echo "Error: Page and prompt file counts do not match (${page_count} vs ${prompt_count})." >&2
    exit 1
  fi

  for ((index = 0; index < expected_count; index++)); do
    page_file="${PAGE_FILES[index]}"
    prompt_file="${PROMPT_FILES[index]}"
    expected_prefix="$(printf 'page%02d-' "$((index + 1))")"

    if [[ ! -f "${PAGES_DIR}/${page_file}" ]]; then
      echo "Error: Missing sequential page file '${PAGES_DIR}/${page_file}'." >&2
      exit 1
    fi

    if [[ ! -f "${PROMPTS_DIR}/${prompt_file}" ]]; then
      echo "Error: Missing matching prompt file '${PROMPTS_DIR}/${prompt_file}'." >&2
      exit 1
    fi

    page_prefix="${page_file%%-*}-"
    prompt_prefix="${prompt_file%%-*}-"

    if [[ "${page_prefix}" != "${expected_prefix}" ]]; then
      echo "Error: Page file '${page_file}' is out of sequence; expected prefix '${expected_prefix}'." >&2
      exit 1
    fi

    if [[ "${prompt_prefix}" != "${expected_prefix}" ]]; then
      echo "Error: Prompt file '${prompt_file}' is out of sequence; expected prefix '${expected_prefix}'." >&2
      exit 1
    fi
  done
}

ensure_latexmk() {
  if ! command -v latexmk >/dev/null 2>&1; then
    echo "Error: latexmk is required for magazine builds." >&2
    exit 1
  fi

  if [[ ! -f "${LATEXMKRC_FILE}" ]]; then
    echo "Error: Missing magazine latexmk config at '${LATEXMKRC_FILE}'." >&2
    exit 1
  fi
}

build_variant() {
  local tex_file="$1"
  local dist_name="$2"
  local output_pdf="${CACHE_OUT_DIR}/${tex_file%.tex}.pdf"

  validate_assets
  ensure_latexmk

  mkdir -p "${CACHE_AUX_DIR}" "${CACHE_OUT_DIR}" "${DIST_DIR}"

  (
    cd "${MAGAZINE_DIR}"
    latexmk \
      -pdf \
      -halt-on-error \
      -interaction=nonstopmode \
      -recorder \
      -file-line-error \
      -f \
      -gg \
      -cd \
      -r "${LATEXMKRC_FILE}" \
      "tex/${tex_file}"
  )

  if [[ ! -f "${output_pdf}" ]]; then
    echo "Error: Expected output PDF '${output_pdf}' not found." >&2
    exit 1
  fi

  cp "${output_pdf}" "${DIST_DIR}/${dist_name}"

  if [[ ! -f "${DIST_DIR}/${dist_name}" ]]; then
    echo "Error: Expected final PDF '${DIST_DIR}/${dist_name}' not found." >&2
    exit 1
  fi

  echo "✅ Built: ${DIST_DIR}/${dist_name}"
}

doctor() {
  validate_assets

  if command -v latexmk >/dev/null 2>&1; then
    echo "✅ latexmk available"
  else
    echo "⚠️  latexmk not found (required for magazine builds)"
  fi

  echo "✅ Magazine assets validated (${#PAGE_FILES[@]} pages/prompts)"
}

clean() {
  mkdir -p "${CACHE_AUX_DIR}" "${CACHE_OUT_DIR}" "${DIST_DIR}"
  rm -f "${CACHE_AUX_DIR}"/* "${CACHE_OUT_DIR}"/* "${DIST_DIR}/reflector-magazine.pdf" "${DIST_DIR}/reflector-magazine-print.pdf"
  echo "✅ Cleaned magazine build artifacts"
}

ACTION="${1:-build}"

case "${ACTION}" in
  doctor)
    doctor
    ;;
  build)
    build_variant "magazine.tex" "reflector-magazine.pdf"
    ;;
  build-print)
    build_variant "magazine-print.tex" "reflector-magazine-print.pdf"
    ;;
  build-all)
    build_variant "magazine.tex" "reflector-magazine.pdf"
    build_variant "magazine-print.tex" "reflector-magazine-print.pdf"
    ;;
  clean)
    clean
    ;;
  --help|-h|help)
    usage
    ;;
  *)
    echo "Error: Unknown action '${ACTION}'." >&2
    usage >&2
    exit 1
    ;;
esac
