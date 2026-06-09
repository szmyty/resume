#!/usr/bin/env bash
# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0

# ============================================================================
# mirror-policies.sh
#
# Mirrors the arXiv policy documentation into the repository for:
# - offline browsing
# - deterministic publishing workflows
# - publisher compliance analysis
# - schema extraction
# - validation automation
#
# Repository:
#   https://github.com/egohygiene/reflector
#
# Usage:
#   ./scripts/publishers/arxiv/mirror-policies.sh
# ============================================================================

set -o errexit
set -o nounset
set -o pipefail

# ============================================================================
# Configuration
# ============================================================================

readonly SCRIPT_DIRECTORY="$(
    cd "$(dirname "${BASH_SOURCE[0]}")" && pwd
)"

readonly REPOSITORY_ROOT="$(
    cd "${SCRIPT_DIRECTORY}/../../.." && pwd
)"

readonly PUBLISHER_NAME="arxiv"

readonly MIRROR_SOURCE_URL="https://info.arxiv.org/help/policies/"

readonly MIRROR_OUTPUT_DIRECTORY="${REPOSITORY_ROOT}/resources/publishers/arxiv/mirror/policies"

readonly MANIFEST_OUTPUT_PATH="${REPOSITORY_ROOT}/resources/publishers/arxiv/manifests/policies.json"

readonly USER_AGENT="Mozilla/5.0"

readonly HTTRACK_DEPTH="5"

readonly HTTRACK_INCLUDE_SCOPE="+info.arxiv.org/help/policies/*"

readonly HTTRACK_EXCLUDE_ALL="-*"

readonly HTTRACK_EXCLUDE_PDFS="-*.pdf"

readonly HTTRACK_EXCLUDE_SEARCH="-*/search/*"

readonly HTTRACK_EXCLUDE_CGI="-*/cgi-bin/*"

# ============================================================================
# Logging
# ============================================================================

log_info() {
    printf "[INFO] %s\n" "$*"
}

log_error() {
    printf "[ERROR] %s\n" "$*" >&2
}

# ============================================================================
# Utilities
# ============================================================================

command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# ============================================================================
# Dependency Verification
# ============================================================================

verify_dependencies() {
    if ! command_exists "httrack"; then
        log_error "Missing required dependency: httrack"

        printf "\n"
        printf "Install httrack using one of the following:\n"
        printf "\n"

        printf "  macOS (Homebrew)\n"
        printf "    brew install httrack\n"
        printf "\n"

        printf "  Debian / Ubuntu\n"
        printf "    sudo apt-get install httrack\n"
        printf "\n"

        printf "  Arch Linux\n"
        printf "    sudo pacman --sync httrack\n"
        printf "\n"

        exit 1
    fi

    log_info "Verified dependency: httrack"
}

# ============================================================================
# Directory Initialization
# ============================================================================

initialize_directories() {
    mkdir -p "${MIRROR_OUTPUT_DIRECTORY}"

    mkdir -p "$(dirname "${MANIFEST_OUTPUT_PATH}")"

    log_info "Initialized output directories"
}

# ============================================================================
# Cleanup
# ============================================================================

cleanup_previous_mirror() {
    if [[ -d "${MIRROR_OUTPUT_DIRECTORY}" ]]; then
        log_info "Removing previous mirror contents"

        rm -rf "${MIRROR_OUTPUT_DIRECTORY}"
    fi

    mkdir -p "${MIRROR_OUTPUT_DIRECTORY}"
}

# ============================================================================
# Mirror
# ============================================================================

mirror_arxiv_policies() {
    log_info "Starting arXiv policy mirror"

    log_info "Source URL:"
    log_info "${MIRROR_SOURCE_URL}"

    log_info "Output directory:"
    log_info "${MIRROR_OUTPUT_DIRECTORY}"

    httrack \
        "${MIRROR_SOURCE_URL}" \
        --path "${MIRROR_OUTPUT_DIRECTORY}" \
        --mirror \
        --depth="${HTTRACK_DEPTH}" \
        --near \
        --stay-on-same-domain \
        --robots=0 \
        --quiet \
        --clean \
        "--user-agent=${USER_AGENT}"

    log_info "Completed arXiv policy mirror"
}

# ============================================================================
# Manifest Generation
# ============================================================================

generate_manifest() {
    local mirrored_at_utc_timestamp

    mirrored_at_utc_timestamp="$(
        date -u +"%Y-%m-%dT%H:%M:%SZ"
    )"

    cat > "${MANIFEST_OUTPUT_PATH}" <<EOF
{
    "publisher": "${PUBLISHER_NAME}",
    "source": "${MIRROR_SOURCE_URL}",
    "mirrored_at": "${mirrored_at_utc_timestamp}",
    "tool": "httrack",
    "depth": ${HTTRACK_DEPTH},
    "user_agent": "${USER_AGENT}",
    "scope": "info.arxiv.org/help/policies/*",
    "output_directory": "resources/publishers/arxiv/mirror/policies",
    "offline_enabled": true,
    "link_rewriting": true
}
EOF

    log_info "Generated manifest:"
    log_info "${MANIFEST_OUTPUT_PATH}"
}

# ============================================================================
# Main
# ============================================================================

main() {
    verify_dependencies

    initialize_directories

    cleanup_previous_mirror

    mirror_arxiv_policies

    generate_manifest

    log_info "arXiv policy mirroring complete"
}

main "$@"
