<!-- SPDX-FileCopyrightText: 2026 Alan Szmyt -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Zenodo Integration Audit

Generated: 2026-06-03

## Audit Summary

Zenodo integration is metadata-ready but archival behavior remains incomplete for full
publication artifacts.

## Current State

- `.zenodo.json` exists and is populated with DOI, concept DOI, license, creators, and
  repository relation metadata.
- Release process produces `zenodo-readiness.md` handoff artifacts.
- Current Zenodo harvesting model is GitHub-release driven and source-archive oriented.

## What Zenodo Is Guaranteed to Receive Today

- GitHub source archive (`source.zip` / tag source archive path).
- Release metadata indirectly via GitHub release integration.

## What Is Not Guaranteed Today

- `reflector.pdf`
- `reflector-magazine.pdf`
- `reflector-magazine-print.pdf`
- `reflector-arxiv-vX.Y.Z.zip`
- `reflector-arxiv-vX.Y.Z.tar.gz`
- `publication-inventory.json`

## DOI Metadata Synchronization Check

DOI metadata surfaces are currently synchronized for canonical DOI values:

- `metadata/publication.yaml`
- `CITATION.cff`
- `.zenodo.json`
- `codemeta.json`
- `publication.json`
- `release-manifest.json`

Validation command result at audit time:

- `python3 scripts/validate-metadata.py` → pass

## Gaps

1. Zenodo deposit inventory is not explicitly tied to the canonical release bundle.
2. PDF and arXiv archival is not guaranteed through the passive GitHub integration path.
3. DOI issuance/update process remains partially manual.

## Recommendations

1. Define Zenodo target inventory as the canonical release bundle (not source-only).
2. Add release-to-Zenodo automated deposition workflow using Zenodo API token.
3. Upload deterministic metadata companions (`checksums.txt`, `release-manifest.json`,
   `publication-inventory.json`) with publication files.
4. Add automated post-deposit verification to compare Zenodo files to canonical inventory.

