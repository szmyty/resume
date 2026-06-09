#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0
#
# postCreate.sh — Dev Container post-create initialisation for reflector.
#
# Runs once after the container is first created. Installs project
# dependencies, sets up pre-commit hooks, and prints a welcome summary.

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo "/workspaces/reflector")"
cd "${REPO_ROOT}"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
info()    { echo "  ▸ $*"; }
success() { echo "  ✅ $*"; }
warn()    { echo "  ⚠️  $*"; }
section() { echo ""; echo "── $* ──────────────────────────────────────"; }

# ---------------------------------------------------------------------------
# 1. Python environment
# ---------------------------------------------------------------------------
section "Python environment"
if command -v uv >/dev/null 2>&1; then
    info "Running: uv sync --all-extras"
    uv sync --all-extras
    success "Python dependencies installed via uv"
else
    warn "uv not found — skipping Python dependency sync"
fi

# ---------------------------------------------------------------------------
# 2. Pre-commit hooks
# ---------------------------------------------------------------------------
section "Pre-commit hooks"
if command -v pre-commit >/dev/null 2>&1; then
    info "Installing pre-commit hooks"
    uv run pre-commit install --install-hooks
    success "Pre-commit hooks installed"
elif uv run pre-commit --version >/dev/null 2>&1; then
    info "Installing pre-commit hooks via uv"
    uv run pre-commit install --install-hooks
    success "Pre-commit hooks installed"
else
    warn "pre-commit not found — run 'task install' then 'pre-commit install'"
fi

# ---------------------------------------------------------------------------
# 3. Toolchain summary
# ---------------------------------------------------------------------------
section "Toolchain verification"
check_tool() {
    local name="$1"
    local cmd="${2:-$1}"
    if command -v "${cmd}" >/dev/null 2>&1; then
        local version
        version=$("${cmd}" --version 2>&1 | head -1 || true)
        success "${name}: ${version}"
    else
        warn "${name}: not found"
    fi
}

check_tool "uv"
check_tool "python3"
check_tool "task"
check_tool "act"
check_tool "gh"
check_tool "latexmk"
check_tool "pdflatex" "pdflatex"
check_tool "biber"
check_tool "pandoc"
check_tool "git"
check_tool "rg" "rg"
check_tool "fd"
check_tool "fzf"
check_tool "zoxide"
check_tool "docker"

# Verify reflector package import
if uv run python -c "import reflector; print('reflector package import OK')" >/dev/null 2>&1; then
    success "reflector package importable"
else
    warn "reflector package not importable — check 'uv sync'"
fi

# ---------------------------------------------------------------------------
# 4. Welcome message
# ---------------------------------------------------------------------------
echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║         reflector Dev Container — Ready                  ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "  Quick start:"
echo "    task setup      — run full onboarding"
echo "    task doctor     — diagnose environment"
echo "    task test       — run tests"
echo "    task build      — build paper PDF"
echo "    task audit      — run publication audit"
echo "    task act-test   — run workflows locally with act"
echo ""
echo "  See README.md and docs/ for full documentation."
echo ""
