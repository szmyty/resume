<!-- SPDX-FileCopyrightText: 2026 Alan Szmyt -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Release Process

This document describes the end-to-end publication release lifecycle for reflector.

---

## Overview

The publication release lifecycle is orchestrated by a single canonical workflow:

```
.github/workflows/publication.yml
```

This workflow encodes the following deterministic pipeline:

```
VERSION
  ↓
validate
  ↓
audit
  ↓
build
  ↓
package
  ↓
github release
  ↓
archive-ready
```

---

## VERSION — Canonical Source of Truth

[`VERSION`](../VERSION) is the single source of truth for all release metadata.

All release surfaces derive from `VERSION` and are validated automatically:

| Surface | File |
|---|---|
| Publication metadata | `metadata/publication.yaml` |
| Publication manifest | `publication.json` |
| Release manifest | `release-manifest.json` |
| Release-Please manifest | `.release-please-manifest.json` |
| Citation metadata | `CITATION.cff` |
| Zenodo metadata | `.zenodo.json` |
| CodeMeta metadata | `codemeta.json` |

**Drift between `VERSION` and any surface is a validation failure.**

The `scripts/validate-release-lifecycle.py` script enforces synchronization across all surfaces.

---

## Workflow

### Trigger

The publication workflow triggers automatically when:

- `VERSION` changes on `main` (push event)
- Any publication source changes on `main` (paper, magazine, metadata, scripts)
- A `workflow_dispatch` event is issued manually

### Stages

#### Stage 1 — Validate

Runs all synchronization and publication integrity checks:

| Job | Script | Output |
|---|---|---|
| Metadata synchronization | `scripts/validate-metadata.py` | pass/fail |
| Release lifecycle contracts | `scripts/validate-release-lifecycle.py` | pass/fail |
| arXiv packaging readiness | `scripts/validate-arxiv-packaging.py` | `audits/arxiv-validation.md` |
| Build reproducibility | `scripts/validate-build-reproducibility.py` | `audits/build-reproducibility.md` |
| Publication readiness | `scripts/audit-publication-readiness.py` | `audits/publication-readiness.md` |
| REUSE compliance | `fsfe/reuse-action` | pass/fail |

Validation failures block all downstream stages.

#### Stage 2 — Audit (parallel with Stage 1)

Runs static analysis and generates audit reports:

| Job | Tool | Output |
|---|---|---|
| ChkTeX lint | `chktex` + `scripts/audit-chktex.py` | `audits/chktex-audit.md` |

Critical ChkTeX warnings (W11, W17, W19) block downstream stages.

#### Stage 3 — Build (depends on Stage 1)

Builds all publication artifacts in parallel:

| Job | Action | Output |
|---|---|---|
| Build paper | `xu-cheng/latex-action@v4` | `paper/.cache/out/paper.pdf` → `dist/reflector.pdf` |
| Build magazine (digital) | `xu-cheng/latex-action@v4` | `magazine/.cache/out/magazine.pdf` → `reflector-magazine.pdf` |
| Build magazine (print) | `xu-cheng/latex-action@v4` | `magazine/.cache/out/magazine-print.pdf` → `reflector-magazine-print.pdf` |

#### Stage 4 — Package (depends on Stages 2 and 3)

Aggregates all artifacts, generates release bundles, and prepares the full release payload:

```
release/reflector-vX.Y.Z/
├── reflector.pdf                       # canonical paper PDF
├── reflector-magazine.pdf              # digital magazine PDF
├── reflector-magazine-print.pdf        # print magazine PDF
├── reflector-arxiv-vX.Y.Z.zip          # arXiv submission bundle (ZIP)
├── reflector-arxiv-vX.Y.Z.tar.gz       # arXiv submission bundle (TAR.GZ)
├── source.zip                          # full source archive
├── checksums.txt                       # SHA-256 checksums for all assets
├── release-manifest.json               # generated staged release manifest
├── publication.json                    # publication metadata
├── publication-readiness.md            # publication readiness report
├── chktex-audit.md                     # ChkTeX audit report
├── zenodo-readiness.md                 # Zenodo readiness report
├── hero.png                            # hero image
└── release-notes.md                    # changelog-derived release notes
```

**arXiv Bundle Contents:**

```
arxiv/
├── paper.tex
├── references.bib
├── .latexmkrc
├── sections/
├── figures/
├── diagrams/
├── assets/
├── references/
├── styles/
├── macros/
├── config/
└── 00README.json
```

The arXiv bundle is reproducible and deterministic:
- `tar` uses `--sort=name` and epoch `--mtime`
- `zip` uses `-X` to strip extended attributes

#### Stage 5 — Release (depends on Stage 4)

Creates the annotated release tag (if absent) and publishes the GitHub Release with all canonical artifacts attached.

**Release assets:**

| Asset | Description |
|---|---|
| `reflector.pdf` | Canonical paper PDF |
| `reflector-magazine.pdf` | Digital magazine PDF |
| `reflector-magazine-print.pdf` | Print magazine PDF |
| `source.zip` | Full source archive |
| `checksums.txt` | SHA-256 checksums |
| `release-manifest.json` | Generated staged release manifest |
| `publication-readiness.md` | Publication readiness audit |
| `chktex-audit.md` | ChkTeX audit report |
| `zenodo-readiness.md` | Zenodo readiness report |

---

## Releasing a New Version

To trigger a complete publication release:

1. **Update `VERSION`:**

   ```
   0.1.0  →  0.1.1
   ```

2. **Synchronize all version surfaces:**

   Update the following to match `VERSION`:

   - `metadata/publication.yaml` → `version: "0.1.1"`
   - `publication.json` → `"version": "0.1.1"`, `"release_tag": "v0.1.1"`
   - `release-manifest.json` → `"current_version": "0.1.1"`
   - `.release-please-manifest.json` → `".": "0.1.1"`
   - `CITATION.cff` → `version: 0.1.1`
   - `.zenodo.json` → `"version": "0.1.1"`
   - `codemeta.json` → `"version": "0.1.1"`

3. **Add changelog entry:**

   Add a section to `CHANGELOG.md`:

   ```markdown
   ## [0.1.1] — YYYY-MM-DD

   ### Changed
   - Description of changes.
   ```

4. **Push to `main`.**

The publication workflow will:
- validate all surfaces are synchronized
- build all artifacts
- generate audit reports and checksums
- create the release tag `v0.1.1`
- publish the GitHub Release with all assets

---

## Manual Dispatch

The publication workflow can be triggered manually via `workflow_dispatch`:

| Input | Description | Default |
|---|---|---|
| `paper` | Paper source directory | `paper` |
| `dry_run` | Skip GitHub Release creation | `false` |
| `fail_on_warnings` | Fail on any ChkTeX warning | `false` |

Use `dry_run: true` to test the full pipeline without publishing a release.

For the canonical staging layout, checksum contract, and manifest generation rules, see [`docs/publication-infrastructure.md`](publication-infrastructure.md).

---

## arXiv Workflow

When a GitHub Release is published:

1. Download `reflector-arxiv-vX.Y.Z.tar.gz` or `reflector-arxiv-vX.Y.Z.zip` from the release.
2. Validate the arXiv bundle locally using `python scripts/validate-arxiv-packaging.py`.
3. Upload to [arxiv.org](https://arxiv.org) via the submission portal.
4. Record the arXiv identifier (`arxiv_id`) in `metadata/publication.yaml`.
5. Update `CITATION.cff` and `.zenodo.json` with the arXiv ID.
6. Tag a metadata-update release.

---

## Zenodo Workflow

The `zenodo-readiness.md` report (included in every GitHub Release) provides a deterministic handoff checklist for Zenodo archival:

1. Open `zenodo-readiness.md` from the GitHub Release assets.
2. Verify all checklist items pass.
3. Create a Zenodo deposit manually at [zenodo.org](https://zenodo.org).
4. Upload all release artifacts.
5. Submit for review.
6. Record the assigned DOI in `metadata/publication.yaml`, `CITATION.cff`, `.zenodo.json`, and `codemeta.json`.
7. Regenerate release metadata so DOI fields remain synchronized.

**DOI assignment is always manual.** The workflow prepares all metadata and artifacts; DOI minting requires a human decision.

---

## DOI Canonicalization

reflector now tracks two Zenodo DOI forms:

- **Version DOI (canonical for citation):** `10.5281/zenodo.20477044`
- **Concept DOI (latest-family discovery):** `10.5281/zenodo.20477045`

Canonical usage policy:

1. Use the **version DOI** in citation metadata (`CITATION.cff`, `codemeta.json`, release manifest DOI fields) to preserve reproducibility.
2. Track the **concept DOI** for discovery and latest-release routing metadata.
3. Keep both DOI forms synchronized via `scripts/validate-metadata.py`.

Future DOI-aware release lifecycle:

```
Release
  ↓
Zenodo DOI assigned
  ↓
metadata/publication.yaml + citation surfaces synchronized
  ↓
metadata validation + release metadata publish
```

---

## Rollback Workflow

If a release needs to be rolled back:

1. Delete the GitHub Release via the GitHub web interface.
2. Delete the release tag:

   ```bash
   git push origin --delete vX.Y.Z
   git tag --delete vX.Y.Z
   ```

3. Revert `VERSION` and all synchronized surfaces to the previous version.
4. Push the revert to `main`.

The publication workflow will re-run and create a corrected release.

---

## Related Files

| File | Purpose |
|---|---|
| `.github/workflows/publication.yml` | Canonical publication orchestrator |
| `.github/workflows/release-tag.yml` | VERSION-driven tag automation |
| `.github/workflows/release-paper.yml` | Tag-driven release (legacy entry point) |
| `.github/workflows/synchronization.yml` | Continuous synchronization validation |
| `.github/workflows/paper-quality.yml` | Paper quality checks (ChkTeX) |
| `.github/workflows/pages.yml` | GitHub Pages deployment |
| `scripts/validate-metadata.py` | Metadata synchronization validator |
| `scripts/validate-release-lifecycle.py` | Release lifecycle contract validator |
| `scripts/validate-arxiv-packaging.py` | arXiv packaging validator |
| `scripts/audit-publication-readiness.py` | Publication readiness auditor |
| `scripts/audit-chktex.py` | ChkTeX audit report generator |
| `VERSION` | Canonical version source |
| `metadata/publication.yaml` | Publication metadata |
| `release-manifest.json` | Release manifest schema |
| `CHANGELOG.md` | Changelog (release notes source) |

---

## Conventions

- All artifacts use the `reflector-` prefix.
- All release assets are deterministic and reproducible.
- No manual asset uploads are required.
- No manual artifact collection is required.
- The `release/` directory is ephemeral (CI-only); it is not committed.
