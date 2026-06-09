# SPDX-FileCopyrightText: 2026 Alan Szmyt
# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parent.parent / "scripts" / "stage-publication-release.py"
REQUIRED_FILES = (
    "reflector.pdf",
    "reflector-magazine.pdf",
    "reflector-magazine-print.pdf",
    "reflector-arxiv-v0.1.0.zip",
    "reflector-arxiv-v0.1.0.tar.gz",
    "source.zip",
    "publication.json",
    "publication-readiness.md",
    "chktex-audit.md",
    "zenodo-readiness.md",
    "release-notes.md",
)


def create_staged_release(tmp_path: Path) -> Path:
    release_dir = tmp_path / "release" / "reflector-v0.1.0"
    release_dir.mkdir(parents=True)
    for index, name in enumerate(REQUIRED_FILES, start=1):
        (release_dir / name).write_text(f"artifact-{index}\n", encoding="utf-8")
    return release_dir


def run_release_stage(tmp_path: Path, release_dir: Path, *extra_args: str) -> subprocess.CompletedProcess[str]:
    command = [
        sys.executable,
        str(SCRIPT_PATH),
        "--release-dir",
        str(release_dir),
        "--version",
        "0.1.0",
        "--tag",
        "v0.1.0",
        "--paper-name",
        "reflector",
        "--repository",
        "egohygiene/reflector",
        "--commit",
        "abc123",
        "--generated-at",
        "2026-05-31T00:00:00Z",
        "--doi",
        "10.5281/zenodo.20477044",
        "--doi-url",
        "https://doi.org/10.5281/zenodo.20477044",
        "--concept-doi",
        "10.5281/zenodo.20477045",
        "--concept-doi-url",
        "https://doi.org/10.5281/zenodo.20477045",
    ]
    for name in REQUIRED_FILES:
        command.extend(["--require", name])
    command.extend(extra_args)
    return subprocess.run(
        command,
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )


def test_stage_publication_release_generates_deterministic_inventory(tmp_path: Path) -> None:
    release_dir = create_staged_release(tmp_path)

    result = run_release_stage(tmp_path, release_dir)

    assert result.returncode == 0, result.stderr

    checksums_path = release_dir / "checksums.txt"
    manifest_path = release_dir / "release-manifest.json"
    inventory_path = release_dir / "publication-inventory.json"
    assert checksums_path.is_file()
    assert manifest_path.is_file()
    assert inventory_path.is_file()

    checksum_lines = checksums_path.read_text(encoding="utf-8").splitlines()
    assert checksum_lines == sorted(checksum_lines, key=lambda line: line.split("  ", 1)[1])

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["version"] == "0.1.0"
    assert manifest["tag"] == "v0.1.0"
    assert manifest["generated_at"] == "2026-05-31T00:00:00Z"
    assert manifest["release_dir"] == "release/reflector-v0.1.0"
    assert manifest["doi"] == "10.5281/zenodo.20477044"
    assert manifest["doi_url"] == "https://doi.org/10.5281/zenodo.20477044"
    assert manifest["concept_doi"] == "10.5281/zenodo.20477045"
    assert manifest["concept_doi_url"] == "https://doi.org/10.5281/zenodo.20477045"
    assert manifest["checksums"]["path"] == "release/reflector-v0.1.0/checksums.txt"
    assert [artifact["filename"] for artifact in manifest["artifacts"]] == sorted(REQUIRED_FILES)
    assert all(
        artifact["path"].startswith("release/reflector-v0.1.0/")
        for artifact in manifest["artifacts"]
    )

    inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    assert inventory["project"] == "reflector"
    assert inventory["tag"] == "v0.1.0"
    assert {item["artifact"] for item in inventory["artifacts"]} == set(REQUIRED_FILES) | {
        "checksums.txt",
        "release-manifest.json",
    }
    for item in inventory["artifacts"]:
        assert item["checksum"]
        assert item["release_url"].endswith(f"/{item['artifact']}")
        assert isinstance(item["publication_target"], list)
        assert item["publication_target"]


def test_stage_publication_release_reports_missing_required_artifact(tmp_path: Path) -> None:
    release_dir = create_staged_release(tmp_path)
    (release_dir / "source.zip").unlink()

    result = run_release_stage(tmp_path, release_dir)

    assert result.returncode == 1
    assert "Missing required release artifact 'source.zip'." in result.stderr
    assert str((release_dir / "source.zip").resolve()) in result.stderr
