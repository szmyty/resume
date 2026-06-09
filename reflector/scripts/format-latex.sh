#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0

set -euo pipefail

if ! command -v latexindent >/dev/null 2>&1; then
  echo "latexindent not found; skipping LaTeX formatting."
  exit 0
fi

for file in "$@"; do
  latexindent -w -l .latexindent.yml "${file}"
  shopt -s nullglob
  backups=("${file}.bak"*)
  if (( ${#backups[@]} > 0 )); then
    rm -f "${backups[@]}"
  fi
done
