<!-- SPDX-FileCopyrightText: 2026 Alan Szmyt -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Publication Workflow Reference

Generated: 2026-06-03
Version: 0.1.1

---

## Overview

This document is the canonical workflow registry for the `egohygiene/reflector` publication
system. It documents every GitHub Actions workflow: trigger conditions, job structure, artifact
outputs, dependencies, and ownership.

For the broader publication architecture, see
[`docs/publication-system-reference.md`](publication-system-reference.md).

---

## Workflow Registry

| Workflow File | Display Name | Trigger Events | Ownership Domain |
|---|---|---|---|
| `publication.yml` | Publication | VERSION change, `paper/**`, `workflow_dispatch` | Full release orchestration |
| `pages.yml` | Deploy GitHub Pages | `docs/**`, `paper/**`, `magazine/**`, `workflow_dispatch` | GitHub Pages deployment |
| `build-paper.yml` | Build Paper | `paper/**`, `workflow_dispatch` | Paper artifact CI |
| `build-magazine.yml` | Build Magazine | `magazine/**`, `workflow_dispatch` | Magazine artifact CI |
| `release-paper.yml` | Release Paper | `v*.*.*` tag push, `workflow_dispatch` | Tag-triggered release |
| `release-tag.yml` | Release Tag Automation | `VERSION`, metadata files, `workflow_dispatch` | Annotated tag creation |
| `release-please.yml` | Release Please | `paper/**`, `VERSION`, `CHANGELOG.md`, `workflow_dispatch` | Release PR automation |
| `synchronization.yml` | Synchronization Validation | metadata, paper, spec changes | Metadata / sync validation |
| `paper-quality.yml` | Paper Quality | `paper/**`, `workflow_dispatch` | LaTeX quality gate |
| `reuse.yml` | REUSE Compliance | push / PR | Licensing compliance |
| `commitlint.yml` | Commit Lint | pull_request | Commit message style |

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

`release-paper.yml` is a secondary release path triggered by `v*.*.*` tag pushes. It includes
an existence guard: if the release already exists (created by `publication.yml`), it skips
release creation to avoid race conditions.

`release-tag.yml` creates the annotated git tag when `VERSION` changes. The tag push then
triggers `release-paper.yml`.

**Release creation sequence for a VERSION bump:**

```
VERSION changes on main
        ├─ publication.yml triggers (VERSION path)
        │       └─ Full pipeline → release job → GitHub Release created
        └─ release-tag.yml triggers (VERSION path)
                └─ Creates annotated tag vX.Y.Z
                        └─ release-paper.yml triggers (v*.*.* tag)
                                └─ Checks: release already exists?
                                        YES → skip
                                        NO  → create release
```

### Deployment Ownership

**Canonical Pages deployment owner:** `pages.yml`

`pages.yml` is the sole workflow that deploys to GitHub Pages. It:
1. Detects scope (paper change, magazine change, or docs-only change)
2. Conditionally builds paper PDF and/or magazine PDFs
3. Synchronizes artifacts into `docs/`
4. Verifies synchronization integrity
5. Deploys `docs/` as the Pages site via `actions/deploy-pages@v5`

### Validation Ownership

**Canonical metadata validation owner:** `synchronization.yml`

`synchronization.yml` runs `validate-metadata.py` on every metadata change to enforce
consistency across all derived metadata files.

**Canonical quality gate owner:** `paper-quality.yml`

`paper-quality.yml` runs ChkTeX on every paper change and generates a structured audit report.

---

## Workflow Details

### `publication.yml` — Publication Orchestrator

**File:** `.github/workflows/publication.yml`
**Trigger:** Push to `main` when `VERSION`, `metadata/**`, `paper/**`, or related paths change; `workflow_dispatch`
**Purpose:** Full release pipeline — validates, builds, packages, and publishes a GitHub Release

**Inputs (workflow_dispatch):**
| Input | Type | Default | Description |
|---|---|---|---|
| `paper` | string | `paper` | Paper source directory |
| `dry_run` | boolean | `false` | Skip GitHub Release creation |
| `fail_on_warnings` | boolean | `false` | Fail on any ChkTeX warning |
| `release_scope` | choice | `auto` | `auto`, `full`, `paper` |

**Jobs:**
| Job | Depends On | Description |
|---|---|---|
| `detect-scope` | — | Determines `paper_changed` and `full_release` flags from changed files |
| `validate` | `detect-scope` | Runs metadata, arXiv, reproducibility, readiness, and lifecycle validators |
| `validate-reuse` | `detect-scope` | Validates REUSE 3.3 licensing compliance |
| `audit-chktex` | `detect-scope` | Runs ChkTeX on paper; critical warnings (W11, W17, W19) are blocking |
| `build-paper` | `validate` | Builds paper PDF and arXiv source bundles |
| `build-magazine` | `validate` | Builds magazine PDFs (digital + print) |
| `package` | `build-paper`, `build-magazine`, `audit-chktex`, `validate` | Assembles staged release directory, generates checksums and manifests |
| `release` | `package`, `validate-reuse` | Creates annotated tag, creates GitHub Release, validates distribution |

**Outputs per job:**
| Job | Artifact | Description |
|---|---|---|
| `build-paper` | `paper-artifacts` | `paper/.cache/out/paper.pdf`, arXiv bundles |
| `build-magazine` | `magazine-artifacts` | Magazine PDFs |
| `audit-chktex` | `chktex-audit-report` | `audits/chktex-audit.md` |
| `validate` | `publication-readiness-report` | `audits/publication-readiness.md` |
| `package` | `release-artifacts` | Full `release/reflector-vX.Y.Z/` directory |

**Scope routing:**
- `paper/**` changes: `build-paper` + arXiv bundles (no GitHub Release)
- `VERSION` change: full pipeline including `build-magazine`, `package`, and `release`

---

### `pages.yml` — GitHub Pages Deployment

**File:** `.github/workflows/pages.yml`
**Trigger:** Push to `main` when `docs/**`, `paper/**`, or `magazine/**` changes; `workflow_dispatch`
**Purpose:** Builds and deploys the GitHub Pages site

**Permissions:** `pages: write`, `id-token: write`, `contents: read`

**Inputs (workflow_dispatch):**
| Input | Type | Default | Description |
|---|---|---|---|
| `paper` | string | `paper` | Paper source directory |
| `build_paper` | boolean | (auto-detected) | Force paper build |
| `build_magazine` | boolean | (auto-detected) | Force magazine build |

**Jobs:**
| Job | Description |
|---|---|
| `deploy` | Single-job workflow: detects scope → builds → syncs → verifies → deploys |

**Steps in `deploy` job:**
1. **Determine deployment scope** — resolves `build_paper` and `build_magazine` from changed files or explicit inputs
2. **Build paper PDF** (conditional) — runs `xu-cheng/latex-action@v4` on `paper/paper.tex`
3. **Build magazine PDFs** (conditional) — runs `xu-cheng/latex-action@v4` on digital and print variants
4. **Synchronize publication assets into docs/** — copies PDFs and hero.png; warns and skips gracefully if build was skipped and no fallback exists
5. **Verify publication synchronization** — checks static assets; PDF verification is conditional on build availability
6. **Upload Pages artifact** — uploads `docs/` as `_site/` via `actions/upload-pages-artifact@v3`
7. **Deploy to GitHub Pages** — publishes `_site/` via `actions/deploy-pages@v5`

---

### `build-paper.yml` — Paper CI Build

**File:** `.github/workflows/build-paper.yml`
**Trigger:** Push or PR to `main` when `paper/**` changes; `workflow_dispatch`
**Purpose:** Lightweight paper CI — builds PDF and uploads as artifact (no release)

**Jobs:**
| Job | Description |
|---|---|
| `build` | Runs `xu-cheng/latex-action@v4` on `paper/paper.tex`; uploads `paper.pdf` as artifact |

---

### `build-magazine.yml` — Magazine CI Build

**File:** `.github/workflows/build-magazine.yml`
**Trigger:** Push or PR to `main` when `magazine/**` changes; `workflow_dispatch`
**Purpose:** Lightweight magazine CI — builds digital and print PDFs

**Jobs:**
| Job | Description |
|---|---|
| `build` | Matrix build (digital + print variants) using `xu-cheng/latex-action@v4` |

---

### `release-paper.yml` — Tag-Triggered Release

**File:** `.github/workflows/release-paper.yml`
**Trigger:** Push of `v*.*.*` tag (e.g., `v0.1.1`); `workflow_dispatch`
**Purpose:** Secondary release path — creates GitHub Release when a version tag is pushed

**Pre-check:** Runs `gh release view ${TAG}` before attempting release creation. If the release
already exists (created by `publication.yml`), the job exits cleanly without creating a
duplicate.

**Jobs:**
| Job | Description |
|---|---|
| `release` | Builds paper PDF, assembles release assets, generates checksums, creates GitHub Release |

**Artifacts uploaded:**
- `reflector.pdf`
- `reflector-magazine.pdf`
- `reflector-magazine-print.pdf`
- `checksums.txt`
- `release-manifest.json`
- `publication-readiness.md`
- `chktex-audit.md`
- `zenodo-readiness.md`
- `source.zip`

**Note:** `reflector-arxiv-vX.Y.Z.zip`, `reflector-arxiv-vX.Y.Z.tar.gz`, and
`publication-inventory.json` are produced by `publication.yml` but may not be present in
releases created solely by `release-paper.yml`. See
[`audits/archival-strategy-audit.md`](../audits/archival-strategy-audit.md) for details.

---

### `release-tag.yml` — Version Tag Automation

**File:** `.github/workflows/release-tag.yml`
**Trigger:** Push to `main` when `VERSION`, `metadata/**`, or related metadata files change; `workflow_dispatch`
**Purpose:** Creates an annotated git tag from `VERSION` when a version change is detected

**Jobs:**
| Job | Description |
|---|---|
| `tag` | Reads `VERSION`, validates release lifecycle, creates annotated tag `vX.Y.Z` |

**Downstream effect:** The tag push triggers `release-paper.yml` via `v*.*.*` pattern.

---

### `release-please.yml` — Release PR Automation

**File:** `.github/workflows/release-please.yml`
**Trigger:** Push to `main` when `paper/**`, `VERSION`, or `CHANGELOG.md` changes; `workflow_dispatch`
**Purpose:** Opens and maintains a Release Please PR to track version bumps and changelog entries

**Jobs:**
| Job | Description |
|---|---|
| `release-please` | Runs `google-github-actions/release-please-action` against `CHANGELOG.md` |

---

### `synchronization.yml` — Synchronization Validation

**File:** `.github/workflows/synchronization.yml`
**Trigger:** Push or PR to `main` when metadata, paper, or spec files change; `workflow_dispatch`
**Purpose:** Validates that all metadata surfaces remain synchronized with `VERSION`

**Jobs:**
| Job | Script | Output |
|---|---|---|
| `validate-metadata` | `scripts/validate-metadata.py` | Pass/fail — DOI, version, author synchronization |
| `validate-arxiv` | `scripts/validate-arxiv-packaging.py` | `audits/arxiv-validation.md` |
| `validate-lifecycle` | `scripts/validate-release-lifecycle.py` | Pass/fail — version surface consistency |
| `validate-reproducibility` | `scripts/validate-build-reproducibility.py` | `audits/build-reproducibility.md` |

---

### `paper-quality.yml` — Paper Quality Gate

**File:** `.github/workflows/paper-quality.yml`
**Trigger:** Push or PR to `main` when `paper/**` changes; `workflow_dispatch`
**Purpose:** Runs ChkTeX on the paper and generates a structured quality report

**Jobs:**
| Job | Tool | Output |
|---|---|---|
| `lint` | `chktex` + `scripts/audit-chktex.py` | `audits/chktex-audit.md` |

**Blocking warnings:** W11 (wrong type of quotes), W17 (using `$$` in math), W19 (unpaired `$`)

---

### `reuse.yml` — REUSE Compliance

**File:** `.github/workflows/reuse.yml`
**Trigger:** Push and pull requests (all paths)
**Purpose:** Validates REUSE 3.3 / SPDX licensing compliance

**Jobs:**
| Job | Tool | Output |
|---|---|---|
| `compliance` | `fsfe/reuse-action` | Pass/fail — all files must have SPDX headers or `.reuse/dep5` |

---

### `commitlint.yml` — Commit Message Style

**File:** `.github/workflows/commitlint.yml`
**Trigger:** Pull request (opened, edited, synchronize, reopened)
**Purpose:** Validates Conventional Commits format for all commits in the PR

**Jobs:**
| Job | Tool | Output |
|---|---|---|
| `lint-commits` | `commitlint` with `.commitlintrc.json` | Pass/fail |

---

## Workflow Dependencies

```
Push to main
        │
        ├─ paper/** changed
        │       ├─ build-paper.yml (artifact CI)
        │       ├─ paper-quality.yml (ChkTeX quality gate)
        │       ├─ publication.yml (detect-scope → paper build path)
        │       ├─ pages.yml (paper build + deploy)
        │       └─ synchronization.yml (metadata validation)
        │
        ├─ magazine/** changed
        │       ├─ build-magazine.yml (artifact CI)
        │       └─ pages.yml (magazine build + deploy)
        │
        ├─ VERSION changed
        │       ├─ publication.yml (detect-scope → full release path)
        │       ├─ release-tag.yml (create annotated tag)
        │       │       └─ v*.*.* tag created
        │       │               └─ release-paper.yml (secondary release path)
        │       └─ synchronization.yml
        │
        ├─ metadata/** changed
        │       └─ synchronization.yml
        │
        └─ docs/** changed
                └─ pages.yml (docs-only deploy; no paper/magazine rebuild)

Pull Request
        ├─ commitlint.yml (commit style gate)
        ├─ reuse.yml (license compliance)
        ├─ paper/** changed → build-paper.yml, paper-quality.yml
        └─ magazine/** changed → build-magazine.yml
```

---

## Scope Detection Details

### `publication.yml` detect-scope Job

**Purpose:** Determines `paper_changed` and `full_release` output flags used by downstream jobs.

**Algorithm:**
1. Resolve `BASE` from `github.event.before`; fall back to `HEAD^`
2. Guard: if `BASE` is not reachable in checkout history, fall back to `git ls-files` (full scan)
3. Run `git diff --name-only "${BASE}" "${GITHUB_SHA}"` to get changed files
4. Set flags based on path patterns

**Output flags:**
| Flag | Set When | Effect |
|---|---|---|
| `paper_changed` | `paper/**`, `metadata/**`, `scripts/**`, `VERSION`, or explicit `workflow_dispatch` scope | Triggers `build-paper` job |
| `full_release` | `VERSION` changed, or `release_scope=full` or `release_scope=auto` | Triggers `build-magazine`, `package`, and `release` jobs |

---

## Known Issues and Gotchas

| Issue | Workflow | Description |
|---|---|---|
| Magazine-only releases require VERSION bump | `publication.yml` | Magazine changes alone do not trigger `publication.yml` release path; must accompany a VERSION change |
| arXiv bundles absent from `release-paper.yml` releases | `release-paper.yml` | arXiv bundles are only generated by `publication.yml`; tags created without a VERSION bump produce incomplete releases |
| `workflow_dispatch` dry run | `publication.yml` | Set `dry_run: true` to run full pipeline without creating a GitHub Release |
| Shallow clone scope fallback | `publication.yml`, `pages.yml` | BASE commit unavailability triggers full scan; expected behavior on force-push or rebase |

---

## Related Documents

| Document | Purpose |
|---|---|
| [`docs/publication-system-reference.md`](publication-system-reference.md) | End-to-end publication lifecycle overview |
| [`docs/publication-artifact-reference.md`](publication-artifact-reference.md) | Artifact lifecycle and ownership |
| [`docs/publication-workflow-map.md`](publication-workflow-map.md) | Detailed flow diagrams for deployment, release, and synchronization |
| [`docs/release-process.md`](release-process.md) | Step-by-step release instructions |
| [`audits/publication-system-audit.md`](../audits/publication-system-audit.md) | Infrastructure audit findings |
| [`audits/publication-infrastructure-audit-followup.md`](../audits/publication-infrastructure-audit-followup.md) | Resolution tracking for audit findings |
