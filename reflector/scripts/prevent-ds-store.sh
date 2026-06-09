#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0

set -euo pipefail

if git diff --cached --name-only --diff-filter=AM | grep -Eq '(^|/)\.DS_Store$'; then
  echo "Do not commit .DS_Store files." >&2
  exit 1
fi
