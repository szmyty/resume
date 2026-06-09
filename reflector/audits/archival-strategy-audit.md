<!-- SPDX-FileCopyrightText: 2026 Alan Szmyt -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Archival Strategy Audit

Generated: 2026-06-03

## Scope

This audit covers archival readiness across GitHub Releases, GitHub Pages, Zenodo, and
DOI-backed metadata surfaces.

## Current Archival Model

1. Canonical publication build and packaging path is `.github/workflows/publication.yml`.
2. Staged release artifacts are assembled in `release/reflector-vX.Y.Z/` and checksummed.
3. GitHub Release acts as the primary immutable distribution point.
4. GitHub Pages hosts discovery copies of PDFs.
5. Zenodo currently archives source archives via GitHub integration (not full release assets).

## Findings

### A1 — Release completeness gap (non-deterministic external distribution)

- Canonical workflow expects arXiv bundles and `publication-inventory.json` in release assets.
- Current published releases (`v0.1.0`, `v0.1.1`) do not include those assets.
- Result: published asset set is incomplete relative to staged publication contract.

### A2 — Archival destination mismatch

- Source archive (`source.zip`) is consistently present.
- Publication PDFs and arXiv bundles are not guaranteed in Zenodo archival path.
- Result: archival completeness differs by destination.

### A3 — Deterministic inventory exists but is not universally archived

- `checksums.txt`, `release-manifest.json`, and `publication-inventory.json` establish a
  deterministic inventory model.
- Only a subset is consistently present in current released artifacts.

## Canonical Bundle Definitions

### Canonical release bundle (required)

- `reflector.pdf`
- `reflector-magazine.pdf`
- `reflector-magazine-print.pdf`
- `reflector-arxiv-vX.Y.Z.zip`
- `reflector-arxiv-vX.Y.Z.tar.gz`
- `source.zip`
- `checksums.txt`
- `release-manifest.json`
- `publication-inventory.json`
- `publication.json`

### Canonical publication bundle (required + optional)

- Required publication outputs: paper + magazine PDFs, manifest, checksums
- Optional publication evidence: `publication-readiness.md`, `chktex-audit.md`,
  `zenodo-readiness.md`, `hero.png`

### Canonical archival bundle

- Canonical release bundle
- DOI-bearing metadata: `CITATION.cff`, `.zenodo.json`, `codemeta.json`,
  `metadata/publication.yaml`, `publication.json`, `release-manifest.json`

### Canonical arXiv bundle

- `reflector-arxiv-vX.Y.Z.zip` and `reflector-arxiv-vX.Y.Z.tar.gz`
- Built from `paper/` publication source tree and validated by arXiv packaging checks

## Recommendations

1. Enforce release-asset parity checks against canonical bundle for every release.
2. Ensure `publication-inventory.json` and arXiv bundles are always uploaded in the actual
   release path used for production tags.
3. Treat `checksums.txt` + manifest files as mandatory archival companions.
4. Introduce automated secondary archival upload (Zenodo API path) for full release bundle.
5. Keep DOI metadata synchronization checks as release gates.

## Implementation Roadmap (Future Automation)

- Phase 1: Normalize release upload path so published assets always match canonical package output.
- Phase 2: Add automated Zenodo deposition for canonical release bundle.
- Phase 3: Add post-release verification job that validates all destination inventories (Release,
  Pages, Zenodo) against `publication-inventory.json`.
- Phase 4: Add DOI metadata update automation for post-mint synchronization workflows.

