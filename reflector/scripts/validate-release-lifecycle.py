#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml


SEMVER_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")
REQUIRED_RELEASE_WORKFLOW_TOKENS = (
    "python scripts/validate-release-lifecycle.py",
    "python scripts/validate-metadata.py",
    "Create GitHub Release",
    "checksums.txt",
    "release-manifest.json",
    "zenodo-readiness.md",
)
REQUIRED_TAG_WORKFLOW_TOKENS = (
    "VERSION",
    "metadata/publication.yaml",
    "git tag -a",
    "git push origin",
)
REQUIRED_PUBLICATION_WORKFLOW_TOKENS = (
    "python scripts/validate-metadata.py",
    "python scripts/validate-release-lifecycle.py",
    "Create GitHub Release",
    "checksums.txt",
    "release-manifest.json",
    "zenodo-readiness.md",
    "reflector-arxiv",
)


def log_error(message: str) -> None:
    print(f"[release-lifecycle] {message}", file=sys.stderr)


def load_json(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        log_error(f"Missing required file: {path}.")
    except json.JSONDecodeError as error:
        log_error(f"Invalid JSON in {path}: {error}.")
    return None


def load_yaml(path: Path) -> dict | None:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        log_error(f"Missing required file: {path}.")
        return None
    except yaml.YAMLError as error:
        log_error(f"Invalid YAML in {path}: {error}.")
        return None
    if not isinstance(data, dict):
        log_error(f"Expected mapping at root of {path}.")
        return None
    return data


def validate_version_surfaces(repo_root: Path) -> bool:
    version_value = (repo_root / "VERSION").read_text(encoding="utf-8").strip()
    if not SEMVER_PATTERN.fullmatch(version_value):
        log_error(f"VERSION must be semantic version MAJOR.MINOR.PATCH, got '{version_value}'.")
        return False

    publication_yaml = load_yaml(repo_root / "metadata" / "publication.yaml")
    publication_json = load_json(repo_root / "publication.json")
    release_manifest = load_json(repo_root / "release-manifest.json")
    release_please_manifest = load_json(repo_root / ".release-please-manifest.json")
    if any(item is None for item in (publication_yaml, publication_json, release_manifest, release_please_manifest)):
        return False

    checks: list[tuple[str, str | None, str]] = [
        ("metadata/publication.yaml.version", str(publication_yaml.get("version")), version_value),
        ("publication.json.version", str(publication_json.get("version")), version_value),
        ("publication.json.version_source", str(publication_json.get("version_source")), "VERSION"),
        ("publication.json.release_tag", str(publication_json.get("release_tag")), f"v{version_value}"),
        ("release-manifest.json.current_version", str(release_manifest.get("current_version")), version_value),
        (".release-please-manifest.json['.']", str(release_please_manifest.get(".")), version_value),
    ]

    valid = True
    for field_name, actual, expected in checks:
        if actual != expected:
            valid = False
            log_error(f"{field_name} must equal '{expected}' (found '{actual}').")
    return valid


def validate_workflow_contracts(repo_root: Path) -> bool:
    release_workflow_path = repo_root / ".github" / "workflows" / "release-paper.yml"
    tag_workflow_path = repo_root / ".github" / "workflows" / "release-tag.yml"
    publication_workflow_path = repo_root / ".github" / "workflows" / "publication.yml"

    try:
        release_workflow_text = release_workflow_path.read_text(encoding="utf-8")
        tag_workflow_text = tag_workflow_path.read_text(encoding="utf-8")
    except FileNotFoundError as error:
        log_error(f"Missing required workflow file: {error.filename}.")
        return False

    valid = True
    for token in REQUIRED_RELEASE_WORKFLOW_TOKENS:
        if token not in release_workflow_text:
            valid = False
            log_error(f"release-paper.yml is missing required token: '{token}'.")

    for token in REQUIRED_TAG_WORKFLOW_TOKENS:
        if token not in tag_workflow_text:
            valid = False
            log_error(f"release-tag.yml is missing required token: '{token}'.")

    if publication_workflow_path.exists():
        publication_workflow_text = publication_workflow_path.read_text(encoding="utf-8")
        for token in REQUIRED_PUBLICATION_WORKFLOW_TOKENS:
            if token not in publication_workflow_text:
                valid = False
                log_error(f"publication.yml is missing required token: '{token}'.")

    return valid


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    checks = [
        validate_version_surfaces(repo_root),
        validate_workflow_contracts(repo_root),
    ]
    if not all(checks):
        return 1
    print("[release-lifecycle] release lifecycle validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
