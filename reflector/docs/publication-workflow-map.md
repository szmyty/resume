<!-- SPDX-FileCopyrightText: 2026 Alan Szmyt -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Publication Workflow Map

Generated: 2026-06-02
Version: 0.1.1

---

## Overview

This document is the canonical reference for the `egohygiene/reflector` publication workflow
system. It documents workflow ownership, trigger conditions, artifact lifecycle, deployment
flow, and synchronization flow.

---

## Workflow Registry

| Workflow File | Display Name | Primary Trigger | Ownership Domain |
|---|---|---|---|
| `publication.yml` | Publication | `VERSION` change, `paper/**`, `workflow_dispatch` | Full release orchestration |
| `pages.yml` | Deploy GitHub Pages | `docs/**`, `paper/**`, `magazine/**`, `workflow_dispatch` | GitHub Pages deployment |
| `build-paper.yml` | Build Paper | `paper/**`, `workflow_dispatch` | Paper artifact CI |
| `build-magazine.yml` | Build Magazine | `magazine/**`, `workflow_dispatch` | Magazine artifact CI |
| `release-paper.yml` | Release Paper | `v*.*.*` tag push, `workflow_dispatch` | Tag-triggered release |
| `release-tag.yml` | Release Tag Automation | `VERSION` push to `main`, metadata files | Annotated tag creation |
| `release-please.yml` | Release Please | `paper/**`, `VERSION`, `CHANGELOG.md`, `workflow_dispatch` | Release PR automation |
| `synchronization.yml` | Synchronization Validation | metadata, paper, spec changes | Metadata / sync validation |
| `paper-quality.yml` | Paper Quality | `paper/**`, `workflow_dispatch` | LaTeX quality gate |
| `reuse.yml` | REUSE Compliance | push / PR | Licensing compliance |
| `commitlint.yml` | Commit Lint | push / PR | Commit message style |

---

## Workflow Ownership

### Release Ownership

**Canonical release owner:** `publication.yml` (release job)

`publication.yml` is the primary orchestrator for full publication releases. When `VERSION`
changes on `main`, it runs the complete pipeline:

```
detect-scope → validate → validate-reuse → audit-chktex
               → build-paper → build-magazine → package → release
```

`release-paper.yml` is a secondary release path triggered by `v*.*.*` tag push. It performs
the same release creation but includes an existence guard: if the release already exists (e.g.,
created by `publication.yml`), it skips creation to avoid race conditions.

`release-tag.yml` creates the annotated git tag when `VERSION` changes. The tag push then
triggers `release-paper.yml`.

**Release creation sequence for a VERSION bump:**

```
1. VERSION changes on main
   ├─ publication.yml triggers (paper/** paths detected)
   │   └─ Full pipeline → release job → GitHub Release created
   └─ release-tag.yml triggers
       └─ Creates annotated tag v{VERSION}
           └─ release-paper.yml triggers (v*.*.* tag)
               └─ Checks: release already exists? → skips if yes
```

### Deployment Ownership

**Canonical Pages deployment owner:** `pages.yml`

`pages.yml` is the sole workflow that deploys to GitHub Pages. It:
1. Detects scope (paper change, magazine change, or docs-only change)
2. Conditionally builds paper PDF and/or magazine PDFs
3. Synchronizes artifacts into `docs/`
4. Verifies synchronization integrity
5. Deploys `docs/` as the Pages site via `actions/deploy-pages@v5`

### Artifact Ownership

See [`audits/publication-artifact-inventory.json`](../audits/publication-artifact-inventory.json)
for the complete artifact lifecycle table.

---

## Deployment Flow

```
Source change (paper/**, docs/**, magazine/**)
        │
        ▼
pages.yml — Determine deployment scope
        │
        ├─ build_paper == true?
        │       ├─ YES → Build paper PDF (xu-cheng/latex-action@v4)
        │       │         paper/.cache/out/paper.pdf
        │       └─ NO  → Use fallback docs/reflector.pdf (if present)
        │                  or warn and skip PDF copy (graceful degradation)
        │
        ├─ build_magazine == true?
        │       ├─ YES → Build magazine PDFs (xu-cheng/latex-action@v4)
        │       │         magazine/dist/reflector-magazine.pdf
        │       │         magazine/dist/reflector-magazine-print.pdf
        │       └─ NO  → Use fallback docs/*.pdf (if present)
        │                  or warn and skip copy (graceful degradation)
        │
        ▼
Synchronize publication assets into docs/
        ├─ docs/reflector.pdf        (from paper build or fallback)
        ├─ docs/reflector-magazine.pdf
        ├─ docs/reflector-magazine-print.pdf
        ├─ docs/figures/hero.png     (from paper/figures/hero.png)
        └─ docs/publication.json     (generated)
        │
        ▼
Verify publication synchronization
        ├─ Static assets (index.html, hero.png, publication.json) required
        ├─ PDF checksums verified when build ran
        └─ PDF absence allowed (with warning) when build was skipped
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

## Full Release Flow

```
VERSION changes on main
        │
        ▼
publication.yml detect-scope
        ├─ Resolves BASE commit (with reachability guard)
        ├─ Detects changed files
        └─ Sets: full_release=true, paper_changed=true
        │
        ▼
Stage 1 — Validate (parallel)
        ├─ validate:         metadata sync, publication readiness, arXiv packaging,
        │                    build reproducibility, release lifecycle, audit holistic
        ├─ validate-reuse:   REUSE 3.3 compliance
        └─ audit-chktex:    LaTeX lint audit
        │
        ▼
Stage 2 — Build (parallel, after validate)
        ├─ build-paper:      paper PDF + arXiv source bundles
        └─ build-magazine:   magazine PDF (digital + print)
        │
        ▼
Stage 3 — Package (after build-paper + build-magazine + audit-chktex + validate)
        ├─ Assemble release/ staging directory
        ├─ Generate checksums.txt
        ├─ Stage release-manifest.json, publication-inventory.json
        ├─ Stage publication-readiness.md, chktex-audit.md, zenodo-readiness.md
        └─ Upload release artifacts as GitHub Actions artifact
        │
        ▼
Stage 4 — Release (after package + validate-reuse; dry_run check)
        ├─ Download release artifacts
        ├─ Create annotated release tag (if missing)
        ├─ Create GitHub Release via softprops/action-gh-release@v3
        │     Assets: reflector.pdf, reflector-magazine.pdf,
        │             reflector-magazine-print.pdf, arxiv bundles,
        │             checksums.txt, release-manifest.json,
        │             publication-inventory.json, publication-readiness.md,
        │             chktex-audit.md, zenodo-readiness.md, publication.json,
        │             source.zip
        └─ Validate distribution (Pages URLs + release assets)
```

---

## Synchronization Flow

### Metadata Synchronization

The canonical metadata layer lives in `metadata/`:

```
metadata/publication.yaml   ─┐
metadata/authors.yaml        ├─→ scripts/validate-metadata.py
metadata/citations.yaml      │      ├─→ publication.json (committed)
metadata/renderers.yaml      │      ├─→ CITATION.cff (committed)
metadata/repository.yaml    ─┘      ├─→ .zenodo.json (committed)
                                     └─→ codemeta.json (committed)
```

`synchronization.yml` runs `validate-metadata.py` on every metadata change to enforce
consistency across all derived metadata files.

### Artifact Synchronization

```
Build output                →  docs/ staging      →  _site/       →  Pages
paper/.cache/out/paper.pdf  →  docs/reflector.pdf  →  _site/*.pdf  →  egohygiene.github.io
magazine/dist/*.pdf         →  docs/*.pdf
paper/figures/hero.png      →  docs/figures/

docs/ staging               →  release/ staging   →  GitHub Release
docs/publication.json       →  release/reflector-v{VERSION}/
release-manifest.json       →  release/...
```

---

## Scope Detection

### `publication.yml` detect-scope

Determines whether to run a full release pipeline or a paper-only incremental build.

| Condition | `paper_changed` | `full_release` |
|---|---|---|
| `workflow_dispatch` with `release_scope=full` or `auto` | `true` | `true` |
| `workflow_dispatch` with `release_scope=paper` | `true` | `false` |
| `VERSION` file changed | `true` | `true` |
| `paper/**` or related scripts changed | `true` | `false` |
| No matching paths | `false` | `false` |

**Fallback:** If BASE commit is unreachable (force-push, rebase, first push), falls back to
`git ls-files` (full repository scan). This ensures scope detection never fails due to
missing history.

### `pages.yml` scope detection

Determines whether to rebuild paper and/or magazine on each Pages deployment trigger.

| Condition | `build_paper` | `build_magazine` |
|---|---|---|
| `workflow_dispatch` with explicit scope | per input | per input |
| `paper/**` or `.latexmkrc` changed | `true` | — |
| `magazine/**` changed | — | `true` |
| `docs/**` only | `false` | `false` |

---

## Known Coupling Points

| Coupling | Description | Risk |
|---|---|---|
| `release-tag.yml` → `release-paper.yml` | Tag creation in `release-tag.yml` triggers `release-paper.yml` via `v*.*.*` push event | Medium — can produce duplicate release attempts; mitigated by existence guard |
| `publication.yml` → `pages.yml` | Both may run on paper changes to main; Pages deploy after publication run may serve stale PDFs if triggered separately | Low — Pages uses its own build; no hard coupling |
| `synchronization.yml` → metadata files | `synchronization.yml` validates metadata consistency; if validation fails, publication is blocked | Medium — by design |

---

## Publication URLs

| Resource | URL |
|---|---|
| GitHub Pages index | `https://egohygiene.github.io/reflector/` |
| Paper PDF | `https://egohygiene.github.io/reflector/reflector.pdf` |
| Magazine PDF | `https://egohygiene.github.io/reflector/reflector-magazine.pdf` |
| Magazine Print PDF | `https://egohygiene.github.io/reflector/reflector-magazine-print.pdf` |
| Publication manifest | `https://egohygiene.github.io/reflector/publication.json` |
| Hero image | `https://egohygiene.github.io/reflector/figures/hero.png` |
| GitHub Releases | `https://github.com/egohygiene/reflector/releases` |
| Zenodo DOI | `https://doi.org/10.5281/zenodo.20477044` |
| Zenodo concept DOI | `https://doi.org/10.5281/zenodo.20477045` |

---

## Maintenance Checklist

When releasing a new version:

- [ ] Update `VERSION` file on `main`
- [ ] Update `CHANGELOG.md` with release notes
- [ ] Update `metadata/publication.yaml` version fields
- [ ] Run `python scripts/validate-metadata.py` locally to verify synchronization
- [ ] Update `docs/index.html` version string to match new VERSION
- [ ] Update `paper/macros/metadata.tex` `\paperdate` if release date changes
- [ ] Update `.zenodo.json` version field if releasing to Zenodo
- [ ] Verify `release-manifest.json` reflects the new version
- [ ] Push to `main` — `publication.yml` will orchestrate the full release pipeline
