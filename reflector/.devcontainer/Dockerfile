# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0
#
# reflector Dev Container — production-grade recursive development environment.
#
# Provides:
#   - Python 3.12 + uv for project dependency management
#   - Task (taskfile.dev) for local workflow orchestration
#   - act (nektos/act) for local GitHub Actions testing
#   - Full TeXLive + latexmk + biber + pandoc for publication workflows
#   - GitHub CLI (via devcontainer feature)
#   - Docker socket access (via devcontainer feature)
#   - Ergonomic CLI tools: ripgrep, fd, bat, fzf, zoxide

FROM mcr.microsoft.com/devcontainers/base:ubuntu-24.04

ARG DEBIAN_FRONTEND=noninteractive

# ---------------------------------------------------------------------------
# System packages
# ---------------------------------------------------------------------------
# Core utilities, Python, LaTeX toolchain, and ergonomic CLI tools.
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Python
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    # Core utilities
    jq \
    tree \
    unzip \
    # Search and navigation
    ripgrep \
    fd-find \
    fzf \
    zoxide \
    # Ergonomic tools
    bat \
    # LaTeX publication toolchain
    texlive-latex-base \
    texlive-latex-recommended \
    texlive-latex-extra \
    texlive-bibtex-extra \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    texlive-science \
    biber \
    latexmk \
    # Document conversion
    pandoc \
    && rm -rf /var/lib/apt/lists/*

# Resolve binary aliases for cross-distro compatibility.
# fd-find installs as fdfind on some Ubuntu versions; bat as batcat on < 22.10.
RUN if [ -f /usr/bin/fdfind ] && [ ! -e /usr/local/bin/fd ]; then \
        ln -s /usr/bin/fdfind /usr/local/bin/fd; \
    fi \
 && if [ -f /usr/bin/batcat ] && [ ! -e /usr/local/bin/bat ]; then \
        ln -s /usr/bin/batcat /usr/local/bin/bat; \
    fi

# ---------------------------------------------------------------------------
# uv — Python package and project manager
# ---------------------------------------------------------------------------
RUN curl -LsSf https://astral.sh/uv/install.sh \
    | env UV_INSTALL_DIR=/usr/local/bin sh

# ---------------------------------------------------------------------------
# Task — taskfile.dev workflow runner
# ---------------------------------------------------------------------------
RUN sh -c "$(curl --location https://taskfile.dev/install.sh)" -- -d -b /usr/local/bin

# ---------------------------------------------------------------------------
# act — local GitHub Actions runner (nektos/act)
# ---------------------------------------------------------------------------
RUN curl -sSf https://raw.githubusercontent.com/nektos/act/master/install.sh \
    | bash -s -- -b /usr/local/bin

# ---------------------------------------------------------------------------
# Shell initialisation for the vscode user
# ---------------------------------------------------------------------------
# Initialise zoxide in bash for the default non-root dev user.
RUN echo 'eval "$(zoxide init bash)"' >> /home/vscode/.bashrc \
 && echo 'eval "$(zoxide init bash)"' >> /root/.bashrc
