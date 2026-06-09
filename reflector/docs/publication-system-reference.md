<!-- SPDX-FileCopyrightText: 2026 Alan Szmyt -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Publication System Reference

Generated: 2026-06-03
Version: 0.1.1

---

## Overview

This document is the single authoritative reference for the `egohygiene/reflector` publication
system. It describes the complete end-to-end lifecycle — from source authoring through build,
validation, deployment, release, and archival — and serves as the canonical answer to
"how does publication work?"

For focused subsystem references, see:

- [`docs/publication-workflow-reference.md`](publication-workflow-reference.md) — workflow registry, triggers, ownership
- [`docs/publication-artifact-reference.md`](publication-artifact-reference.md) — artifact lifecycle, producers, consumers
- [`docs/release-process.md`](release-process.md) — step-by-step release instructions
- [`docs/publication-infrastructure.md`](publication-infrastructure.md) — packaging contract and staging layout

---

## Architecture Summary

The publication system has five architectural layers:

| Layer | Components | Purpose |
|---|---|---|
| **Source** | `paper/`, `magazine/`, `metadata/` | Canonical manuscript and metadata |
| **Build** | `scripts/`, `.latexmkrc`, `xu-cheng/latex-action@v4` | Deterministic artifact generation |
| **Validation** | `scripts/validate-*.py`, `scripts/audit-*.py` | Integrity, quality, and compliance gates |
| **Distribution** | `docs/`, `_site/`, GitHub Pages | Discovery and access surface |
| **Release** | `release/reflector-vX.Y.Z/`, GitHub Releases, Zenodo | Immutable archival and citation |

---

## End-to-End Publication Lifecycle

```
┌─────────────────────────────────────────────────────────────────────┐
│  SOURCE AUTHORING                                                   │
│  paper/paper.tex + paper/sections/*.tex + paper/figures/            │
│  magazine/tex/magazine.tex + magazine/pages/                        │
│  metadata/publication.yaml + metadata/authors.yaml                 │
└────────────────────────────┬────────────────────────────────────────┘
                             │ git push to main
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│  SCOPE DETECTION  (publication.yml → detect-scope job)             │
│  ┌─────────────────┬──────────────────┬────────────────────────┐   │
│  │ paper/** change │ VERSION change   │ workflow_dispatch       │   │
│  │ paper_changed=T │ full_release=T   │ explicit scope input    │   │
│  │ full_release=F  │ paper_changed=T  │                        │   │
│  └─────────────────┴──────────────────┴────────────────────────┘   │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STAGE 1 — VALIDATE  (parallel jobs)                               │
│  ├─ validate: metadata sync, arXiv packaging, reproducibility,     │
│  │            publication readiness, release lifecycle              │
│  ├─ validate-reuse: REUSE 3.3 compliance                           │
│  └─ audit-chktex: LaTeX quality lint (W11, W17, W19 are blocking)  │
└────────────────────────────┬────────────────────────────────────────┘
                             │ validation passes
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STAGE 2 — BUILD  (parallel jobs, after validate)                  │
│  ├─ build-paper:    paper/.cache/out/paper.pdf                     │
│  │                  reflector-arxiv-vX.Y.Z.zip + .tar.gz           │
│  └─ build-magazine: magazine/dist/reflector-magazine.pdf           │
│                     magazine/dist/reflector-magazine-print.pdf     │
└────────────────────────────┬────────────────────────────────────────┘
                             │ build succeeds
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STAGE 3 — PACKAGE  (after build + audit-chktex + validate)        │
│  release/reflector-vX.Y.Z/                                         │
│  ├─ reflector.pdf                    (canonical paper)             │
│  ├─ reflector-magazine.pdf           (digital magazine)            │
│  ├─ reflector-magazine-print.pdf     (print magazine)              │
│  ├─ reflector-arxiv-vX.Y.Z.zip       (arXiv bundle)               │
│  ├─ reflector-arxiv-vX.Y.Z.tar.gz    (arXiv bundle tarball)       │
│  ├─ source.zip                       (full source archive)         │
│  ├─ checksums.txt                    (SHA-256 for all assets)      │
│  ├─ release-manifest.json            (staged inventory)            │
│  ├─ publication-inventory.json       (canonical artifact listing)  │
│  ├─ publication.json                 (publication metadata)        │
│  ├─ publication-readiness.md         (readiness report)            │
│  ├─ chktex-audit.md                  (LaTeX quality report)        │
│  └─ zenodo-readiness.md              (Zenodo handoff checklist)    │
└────────────────────────────┬────────────────────────────────────────┘
                             │ package complete
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STAGE 4 — RELEASE  (after package + validate-reuse)               │
│  ├─ Create annotated release tag (if absent)                       │
│  ├─ Create GitHub Release via softprops/action-gh-release@v3       │
│  └─ Upload all staged artifacts as release assets                  │
└────────────────────────────┬────────────────────────────────────────┘
                             │ release published
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STAGE 5 — DEPLOY  (pages.yml, independent trigger)                │
│  ├─ Build paper PDF (if paper/** changed)                          │
│  ├─ Build magazine PDFs (if magazine/** changed)                   │
│  ├─ Synchronize artifacts into docs/                               │
│  └─ Deploy docs/ → _site/ → GitHub Pages                          │
└────────────────────────────┬────────────────────────────────────────┘
                             │ Pages live
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│  STAGE 6 — ARCHIVE  (manual, post-release)                         │
│  ├─ Zenodo: GitHub integration harvests source archive from release │
│  ├─ arXiv:  Manual upload of reflector-arxiv-vX.Y.Z bundle         │
│  └─ DOI:    Mint DOI, synchronize all metadata surfaces            │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Component Inventory

### Source Components

| Component | Path | Description |
|---|---|---|
| Paper manuscript | `paper/paper.tex` | Root LaTeX entry point |
| Paper sections | `paper/sections/*.tex` | Semantic section files |
| Paper figures | `paper/figures/` | Canonical figure assets (figure1.png–figure17.png, hero.png) |
| Paper macros | `paper/macros/` | Shared macro definitions |
| Paper style | `paper/styles/reflector.sty` | Publication style sheet |
| Paper config | `paper/config/` | Build configuration |
| Build config | `.latexmkrc` | Root latexmk configuration |
| Magazine source | `magazine/tex/magazine.tex` | Magazine LaTeX entry point |
| Magazine pages | `magazine/pages/` | Full-page PNG assets (page01–page14) |
| Canonical metadata | `metadata/publication.yaml` | Publication title, version, dates, DOI |
| Author metadata | `metadata/authors.yaml` | Author ORCID, affiliations |
| Version | `VERSION` | Single source of truth for release version |
| CHANGELOG | `CHANGELOG.md` | Release notes source |

### Build Components

| Component | Path | Description |
|---|---|---|
| Paper build script | `scripts/build-paper.sh` | Local paper build orchestrator |
| Magazine build script | `scripts/build-magazine.sh` | Local magazine build with doctor mode |
| LaTeX action | `xu-cheng/latex-action@v4` | CI LaTeX compilation |
| Release staging | `scripts/stage-publication-release.py` | Generates checksums.txt and release-manifest.json |

### Validation Components

| Component | Path | Purpose |
|---|---|---|
| Metadata validator | `scripts/validate-metadata.py` | Cross-file metadata synchronization |
| Release lifecycle | `scripts/validate-release-lifecycle.py` | Version surface consistency |
| arXiv packaging | `scripts/validate-arxiv-packaging.py` | 31-check arXiv bundle validation |
| Build reproducibility | `scripts/validate-build-reproducibility.py` | Deterministic build checks |
| Publication readiness | `scripts/audit-publication-readiness.py` | Holistic readiness assessment |
| ChkTeX audit | `scripts/audit-chktex.py` | LaTeX quality audit report |
| Holistic audit | `scripts/audit-holistic.py` | Combined system audit |

### Workflow Components

| Workflow | Path | Domain |
|---|---|---|
| Publication orchestrator | `.github/workflows/publication.yml` | Full release pipeline |
| Pages deployment | `.github/workflows/pages.yml` | GitHub Pages |
| Paper build | `.github/workflows/build-paper.yml` | Paper CI |
| Magazine build | `.github/workflows/build-magazine.yml` | Magazine CI |
| Release creation | `.github/workflows/release-paper.yml` | Tag-triggered release |
| Tag automation | `.github/workflows/release-tag.yml` | VERSION → git tag |
| Synchronization | `.github/workflows/synchronization.yml` | Metadata validation |
| Paper quality | `.github/workflows/paper-quality.yml` | ChkTeX quality gate |
| REUSE compliance | `.github/workflows/reuse.yml` | License compliance |
| Release Please | `.github/workflows/release-please.yml` | Release PR automation |
| Commit lint | `.github/workflows/commitlint.yml` | Commit style gate |

---

## Artifact Flow

### Build-Time Artifacts

```
paper/paper.tex
    └─→ xu-cheng/latex-action@v4
           └─→ paper/.cache/out/paper.pdf          (ephemeral)
                   ├─→ docs/reflector.pdf           (transient, pages.yml)
                   └─→ release/.../reflector.pdf    (ephemeral, release stage)

magazine/tex/magazine.tex
    └─→ xu-cheng/latex-action@v4
           ├─→ magazine/dist/reflector-magazine.pdf (transient)
           │       └─→ docs/reflector-magazine.pdf  (transient, pages.yml)
           └─→ magazine/dist/reflector-magazine-print.pdf (transient)
                   └─→ docs/reflector-magazine-print.pdf  (transient)

paper/ source tree
    └─→ publication.yml package job
           ├─→ reflector-arxiv-vX.Y.Z.zip
           └─→ reflector-arxiv-vX.Y.Z.tar.gz
```

### Metadata Artifacts

```
metadata/publication.yaml
metadata/authors.yaml
metadata/citations.yaml
metadata/renderers.yaml
metadata/repository.yaml
    └─→ scripts/validate-metadata.py
           ├─→ CITATION.cff              (committed, updated on drift)
           ├─→ .zenodo.json             (committed, updated on drift)
           ├─→ codemeta.json            (committed, updated on drift)
           └─→ publication.json         (committed, generated)
```

### Release Artifacts

```
All build artifacts + audit outputs
    └─→ scripts/stage-publication-release.py
           ├─→ release/reflector-vX.Y.Z/checksums.txt
           ├─→ release/reflector-vX.Y.Z/release-manifest.json
           └─→ release/reflector-vX.Y.Z/publication-inventory.json

release/reflector-vX.Y.Z/
    └─→ softprops/action-gh-release@v3
           └─→ GitHub Release vX.Y.Z
                   └─→ Zenodo (via GitHub integration webhook)
```

---

## Deployment Flow

```
Source change (paper/**, docs/**, magazine/**)
        │
        ▼
pages.yml triggered
        │
        ├─ paper/** or .latexmkrc changed?
        │       YES → Build paper PDF → paper/.cache/out/paper.pdf
        │       NO  → Skip paper build; use fallback if available
        │
        ├─ magazine/** changed?
        │       YES → Build magazine PDFs → magazine/dist/
        │       NO  → Skip magazine build
        │
        ▼
Synchronize into docs/
        ├─ docs/reflector.pdf
        ├─ docs/reflector-magazine.pdf
        ├─ docs/reflector-magazine-print.pdf
        ├─ docs/figures/hero.png  (from paper/figures/hero.png)
        └─ docs/publication.json (generated)
        │
        ▼
Verify publication synchronization
        ├─ Static assets verified (index.html, hero.png, publication.json)
        ├─ PDF checksums verified if build ran
        └─ PDF absence logged (not fatal) if build was skipped
        │
        ▼
Copy docs/ → _site/
        │
        ▼
Upload _site/ as GitHub Pages artifact
        │
        ▼
actions/deploy-pages@v5
        │
        ▼
https://egohygiene.github.io/reflector/
```

---

## Release Flow

```
VERSION changes on main
        │
        ├─ publication.yml triggered (VERSION change path)
        │       └─ detect-scope: full_release=true, paper_changed=true
        │
        └─ release-tag.yml triggered (VERSION change path)
                └─ Creates annotated git tag vX.Y.Z
                        └─ Triggers release-paper.yml (v*.*.* tag)
                                └─ Pre-checks: release already exists?
                                        YES → skip (publication.yml created it)
                                        NO  → create release (secondary path)

publication.yml full pipeline:
        validate (parallel) ──→ build-paper  ──→ package ──→ release
        validate-reuse ─────→ build-magazine ──↗
        audit-chktex ───────────────────────→ ↗
```

For complete release instructions, see [`docs/release-process.md`](release-process.md).

---

## Archival Flow

### GitHub Release (Primary Archive)

```
publication.yml release job
    └─→ GitHub Release vX.Y.Z
           ├─ reflector.pdf
           ├─ reflector-magazine.pdf
           ├─ reflector-magazine-print.pdf
           ├─ reflector-arxiv-vX.Y.Z.zip
           ├─ reflector-arxiv-vX.Y.Z.tar.gz
           ├─ source.zip
           ├─ checksums.txt
           ├─ release-manifest.json
           ├─ publication-inventory.json
           ├─ publication.json
           ├─ publication-readiness.md
           ├─ chktex-audit.md
           └─ zenodo-readiness.md
```

### Zenodo (Secondary Archive)

```
GitHub Release created
    └─→ Zenodo GitHub integration (must be enabled in Zenodo UI)
           └─→ Zenodo deposit (source archive only via webhook)
                   └─→ DOI minted: 10.5281/zenodo.20477044 (version)
                                   10.5281/zenodo.20477045 (concept)
```

**Note:** Zenodo's automatic GitHub integration harvests the GitHub source archive only.
PDFs and arXiv bundles must be manually uploaded until a Zenodo API integration is implemented.
See [`audits/zenodo-integration-audit.md`](../audits/zenodo-integration-audit.md) for details.

### arXiv (Tertiary Archive)

```
GitHub Release published
    └─→ Manual: download reflector-arxiv-vX.Y.Z.tar.gz
           └─→ Validate: python scripts/validate-arxiv-packaging.py
                   └─→ Manual: upload to arxiv.org
                           └─→ Record arXiv ID in metadata/publication.yaml
```

---

## Scope Detection Reference

### `publication.yml` Scope

| Trigger | `paper_changed` | `full_release` | Pipeline path |
|---|---|---|---|
| `workflow_dispatch` with `release_scope=full` or `auto` | `true` | `true` | Full release |
| `workflow_dispatch` with `release_scope=paper` | `true` | `false` | Paper + arXiv only |
| `VERSION` file changed | `true` | `true` | Full release |
| `paper/**`, `metadata/**`, `scripts/**` changed | `true` | `false` | Paper + arXiv only |
| No matching paths | `false` | `false` | No build |

**Fallback behavior:** If the BASE commit (from `github.event.before` or `HEAD^`) is not
reachable in checkout history (force-push, shallow clone, rebase), scope detection falls back
to `git ls-files` (full repository scan).

### `pages.yml` Scope

| Trigger | `build_paper` | `build_magazine` | Pages action |
|---|---|---|---|
| `workflow_dispatch` with explicit scope | per input | per input | Build + deploy |
| `paper/**` or `.latexmkrc` changed | `true` | `false` | Build paper + deploy |
| `magazine/**` changed | `false` | `true` | Build magazine + deploy |
| `docs/**` only | `false` | `false` | Deploy (no rebuild) |

---

## Metadata Synchronization

All release version surfaces derive from `VERSION` and must remain synchronized:

| Surface | File | Validation |
|---|---|---|
| Canonical version | `VERSION` | source of truth |
| Publication metadata | `metadata/publication.yaml` | `validate-metadata.py` |
| Publication manifest | `publication.json` | `validate-metadata.py` |
| Release manifest | `release-manifest.json` | `validate-release-lifecycle.py` |
| Release-Please manifest | `.release-please-manifest.json` | `validate-release-lifecycle.py` |
| Citation metadata | `CITATION.cff` | `validate-metadata.py` |
| Zenodo metadata | `.zenodo.json` | `validate-metadata.py` |
| CodeMeta metadata | `codemeta.json` | `validate-metadata.py` |

Drift between `VERSION` and any surface is a validation failure that blocks the release pipeline.

---

## Known Coupling Points

| Coupling | Description | Risk |
|---|---|---|
| `release-tag.yml` → `release-paper.yml` | Tag creation triggers release creation | Medium — mitigated by existence guard |
| `publication.yml` → `pages.yml` | Both may run on paper changes; independent builds | Low — no hard dependency |
| `synchronization.yml` → metadata files | Validation blocks publication on drift | Medium — by design |
| `docs/` PDFs | Not committed; only present transiently during Pages runs | High — builds that skip paper have no fallback PDF |

---

## Publication URLs

| Resource | URL |
|---|---|
| GitHub Pages index | `https://egohygiene.github.io/reflector/` |
| Paper PDF | `https://egohygiene.github.io/reflector/reflector.pdf` |
| Magazine PDF | `https://egohygiene.github.io/reflector/reflector-magazine.pdf` |
| Magazine print PDF | `https://egohygiene.github.io/reflector/reflector-magazine-print.pdf` |
| Publication manifest | `https://egohygiene.github.io/reflector/publication.json` |
| Hero image | `https://egohygiene.github.io/reflector/figures/hero.png` |
| GitHub Releases | `https://github.com/egohygiene/reflector/releases` |
| Zenodo DOI (version) | `https://doi.org/10.5281/zenodo.20477044` |
| Zenodo DOI (concept) | `https://doi.org/10.5281/zenodo.20477045` |

---

## Failure Mode Reference

| Failure | Trigger Condition | Symptom | Mitigation |
|---|---|---|---|
| `fatal: bad object` in detect-scope | Force-push, rebase, or first push to branch | `publication.yml` fails before any build job | BASE reachability guard falls back to `git ls-files` |
| `Expected PDF not found at docs/reflector.pdf` | `pages.yml` runs without paper build and no local PDF | Pages deployment fails | Synchronization step warns and skips copy gracefully |
| Dual release creation race | `publication.yml` and `release-paper.yml` both target same release | Second creation attempt fails with `release already exists` | `release-paper.yml` pre-checks for existing release; skips if present |
| Metadata drift blocks release | `VERSION` bumped without updating all metadata surfaces | `validate-release-lifecycle.py` fails | Run `python scripts/validate-metadata.py` before push |
| ChkTeX blocking warnings | Critical LaTeX warnings (W11, W17, W19) present | `audit-chktex` job fails; release blocked | Fix LaTeX source; use `fail_on_warnings=false` for temporary override |
| Zenodo receives source only | GitHub integration harvests source archive, not PDFs | Zenodo archive lacks canonical PDFs | Manual PDF upload to Zenodo; future: Zenodo API automation |

---

## Maintenance Checklist

When releasing a new version:

- [ ] Update `VERSION` file
- [ ] Update `CHANGELOG.md` with release notes
- [ ] Update `metadata/publication.yaml` — version, date fields
- [ ] Run `python scripts/validate-metadata.py` to verify all surfaces synchronized
- [ ] Update `docs/index.html` version string
- [ ] Update `paper/macros/metadata.tex` `\paperdate` if release date changes
- [ ] Push to `main` — `publication.yml` orchestrates the full pipeline
- [ ] Verify GitHub Release created with all canonical assets
- [ ] Manually upload PDFs and arXiv bundles to Zenodo deposit
- [ ] Record arXiv ID in `metadata/publication.yaml` after arXiv submission

---

## Related Documents

| Document | Purpose |
|---|---|
| [`docs/publication-workflow-reference.md`](publication-workflow-reference.md) | Workflow registry, triggers, ownership, dependencies |
| [`docs/publication-artifact-reference.md`](publication-artifact-reference.md) | Artifact lifecycle, producers, consumers, destinations |
| [`docs/publication-lessons-learned.md`](publication-lessons-learned.md) | Lessons learned and future recommendations |
| [`docs/release-process.md`](release-process.md) | Step-by-step release instructions |
| [`docs/publication-infrastructure.md`](publication-infrastructure.md) | Packaging contract and staging layout |
| [`docs/publication-workflow-map.md`](publication-workflow-map.md) | Detailed workflow flow diagrams |
| [`audits/publication-system-audit.md`](../audits/publication-system-audit.md) | Infrastructure audit findings |
| [`audits/publication-artifact-inventory.md`](../audits/publication-artifact-inventory.md) | Canonical artifact inventory |
| [`audits/archival-strategy-audit.md`](../audits/archival-strategy-audit.md) | Archival strategy and gaps |
