<!-- SPDX-FileCopyrightText: 2026 Alan Szmyt -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Publication System Audit

Generated: 2026-06-02

---

## Executive Summary

This audit covers the end-to-end publication infrastructure for the `egohygiene/reflector` repository. The system is architecturally sophisticated — deterministic LaTeX builds, multi-artifact staging, scope-detected incremental pipelines, and Zenodo/arXiv integration scaffolding. However, several structural fragilities and operational gaps have been identified that produce the failure classes noted in the issue: Pages deployment failures, stale artifacts, missing PDFs during deployment, and incremental build logic errors.

| Domain | Status | Severity |
|---|---|---|
| Build architecture | ✅ Functional | — |
| Incremental build logic | ⚠️ Fragile | High |
| GitHub Pages deployment | ⚠️ Fragile | High |
| GitHub Release workflow | ⚠️ Dual-path | Medium |
| Zenodo integration | ⚠️ Manual / incomplete | Medium |
| Artifact lifecycle | ⚠️ Ephemeral artifacts | Medium |
| Documentation | ⚠️ Stale / fragmented | Low–Medium |

**Summary verdict:** The publication infrastructure works under happy-path conditions but breaks predictably under edge conditions (first push to branch, shallow clones, skipped builds when `docs/` has no PDFs). No single point of failure, but multiple fragile seams that compound under real release pressure.

---

## Architecture Overview

### Build Architecture

#### Paper Build

| Stage | Location | Inputs | Outputs |
|---|---|---|---|
| Source | `paper/paper.tex` | All `paper/**` LaTeX sources | — |
| Config | `.latexmkrc` (root) | Build parameters | — |
| Build | `xu-cheng/latex-action@v4` (CI) or `scripts/build-paper.sh` (local) | `paper/paper.tex`, `.latexmkrc` | `paper/.cache/out/paper.pdf` |
| Distribution | `pages.yml` or `publication.yml` copy step | `paper/.cache/out/paper.pdf` | `docs/reflector.pdf` |

Dependencies: TeXLive (full), biber, latexmk, all figure assets in `paper/figures/` (figure1.png–figure17.png, hero.png).

Assumptions: `paper/.cache/` is a transient build directory (git-ignored). The output PDF is never committed to the repository directly.

#### Magazine Build (Digital + Print)

| Variant | Source | Config | Output |
|---|---|---|---|
| Digital | `magazine/tex/magazine.tex` | `magazine/tex/.latexmkrc` | `magazine/.cache/out/magazine.pdf` → `magazine/dist/reflector-magazine.pdf` |
| Print | `magazine/tex/magazine-print.tex` | `magazine/tex/.latexmkrc` | `magazine/.cache/out/magazine-print.pdf` → `magazine/dist/reflector-magazine-print.pdf` |

Inputs: 14 page PNGs in `magazine/pages/` (`page01-cover.png` through `page14-back-cover.png`), 14 prompt files in `magazine/prompts/`.

Validation: `scripts/build-magazine.sh doctor` checks page/prompt file counts and sequence before build.

Assumptions: Each page PNG is portrait 2:3 at 8in×12in zero-margin geometry.

#### arXiv Bundle Build

| Artifact | Producer | Process |
|---|---|---|
| `reflector-arxiv-vX.Y.Z.zip` | `publication.yml` package job | Zip of `paper/` source tree, excluding build cache |
| `reflector-arxiv-vX.Y.Z.tar.gz` | `publication.yml` package job | Same, as tarball |

Inputs: `paper/00README.json` (arXiv manifest), all LaTeX sources, all figure assets.

Dependencies: arXiv packaging validation passes 31 checks (`scripts/validate-arxiv-packaging.py`).

### Deployment Architecture

```
Build (CI)
  ├─ paper/.cache/out/paper.pdf
  ├─ magazine/.cache/out/magazine.pdf
  └─ magazine/.cache/out/magazine-print.pdf
        ↓
Synchronize to docs/
  ├─ docs/reflector.pdf
  ├─ docs/reflector-magazine.pdf
  ├─ docs/reflector-magazine-print.pdf
  └─ docs/figures/hero.png
        ↓
_site/ (copy of docs/)
        ↓
GitHub Pages (actions/deploy-pages@v5)
  └─ https://egohygiene.github.io/reflector/

VERSION change →
  publication.yml full release path →
    release/reflector-vX.Y.Z/
      ↓
    GitHub Release (via gh cli)
      ↓
    Zenodo (manual trigger via GitHub release webhook)
```

#### Expected vs. Actual Paths

| Artifact | Expected Path | Committed to Repo | Present at Deploy Time |
|---|---|---|---|
| `reflector.pdf` | `docs/reflector.pdf` | ❌ No | Only during `pages.yml` run (transient) |
| `reflector-magazine.pdf` | `docs/reflector-magazine.pdf` | ❌ No | Only during `pages.yml` run (transient) |
| `reflector-magazine-print.pdf` | `docs/reflector-magazine-print.pdf` | ❌ No | Only during `pages.yml` run (transient) |
| `docs/figures/hero.png` | `docs/figures/hero.png` | ❌ No (source: `paper/figures/hero.png`) | Only during `pages.yml` run (transient) |
| `docs/publication.json` | `docs/publication.json` | ❌ No | Generated during `pages.yml` run |
| Release staging | `release/reflector-vX.Y.Z/` | ❌ No | Created and destroyed per run |

### Workflow Landscape

| Workflow | Trigger | Key Jobs | Notes |
|---|---|---|---|
| `publication.yml` | VERSION / paper changes, `workflow_dispatch` | detect-scope, validate, validate-reuse, audit-chktex, build-paper, build-magazine, package, release | Main orchestrator; 7 jobs |
| `pages.yml` | `docs/**`, `paper/**`, `magazine/**`, `workflow_dispatch` | deploy (single job) | Standalone Pages deployment |
| `build-paper.yml` | `paper/**`, `workflow_dispatch` | build | Lightweight paper build (artifact only) |
| `build-magazine.yml` | `magazine/**`, `workflow_dispatch` | build | Lightweight magazine build |
| `release-paper.yml` | `v*.*.*` tag push, `workflow_dispatch` | release | Tag-triggered release creation |
| `release-please.yml` | `paper/**`, `VERSION`, `CHANGELOG.md`, `workflow_dispatch` | release-please | Release PR automation |
| `release-tag.yml` | `VERSION`, metadata files, `workflow_dispatch` | tag | Automated tag creation from VERSION |
| `synchronization.yml` | metadata, paper, spec changes | validate-metadata, validate-publication-readiness, validate-build-reproducibility, validate-arxiv-packaging, validate-release-lifecycle | Metadata and sync validation |
| `paper-quality.yml` | `paper/**`, `workflow_dispatch` | build, lint (ChkTeX) | Quality gate; runs in parallel |
| `reuse.yml` | (inferred) | REUSE compliance check | Licensing compliance |
| `commitlint.yml` | PR/push | Commit message lint | Style enforcement |

---

## Findings

### F1 — Missing `git cat-file` Guard in `publication.yml` detect-scope

**Severity: High**
**Domain: Incremental Build Logic**

`pages.yml` includes a guard to verify the BASE commit is reachable before running `git diff`:

```bash
if [[ -n "${BASE}" ]] && ! git cat-file -e "${BASE}^{commit}" 2>/dev/null; then
  echo "Base commit ${BASE} is unavailable in checkout history; falling back to full repository scan."
  BASE=""
fi
```

`publication.yml` detect-scope job does NOT have this guard. After resolving `github.event.before` or `HEAD^`, it directly runs:

```bash
CHANGED_FILES="$(git diff --name-only "${BASE}" "${GITHUB_SHA}")"
```

If BASE is an unreachable commit (e.g., force-pushed branch, first push after a shallow clone, or a commit that was squashed/rebased), this produces `fatal: bad object` and the entire workflow fails before any build job runs.

**Root cause:** Inconsistent application of the BASE-availability guard. `pages.yml` received the fix; `publication.yml` did not.

**Failure condition:** Any push where `github.event.before` references a commit not present in the fetch-depth=0 history (e.g., branch force-push, rebased branch, initial push).

---

### F2 — Stale `docs/index.html` Version Reference

**Severity: Medium**
**Domain: Documentation / Deployment**

`docs/index.html` contains:

```html
<dd>v0.0.1, canonical route <code>reflector.pdf</code></dd>
```

The canonical version in `VERSION` is `0.1.1`. This creates a visible inconsistency on the published landing page at `https://egohygiene.github.io/reflector/`.

**Root cause:** `docs/index.html` is a manually maintained static file and is not templated from `VERSION` or any canonical metadata source. Version references drift as `VERSION` advances.

---

### F3 — Pages Fallback Fails When `docs/` PDFs Are Absent

**Severity: High**
**Domain: GitHub Pages Deployment**

The `pages.yml` "Synchronize publication assets into docs" step implements a fallback for skipped builds:

```bash
PDF_SOURCE="docs/reflector.pdf"
if [[ "${{ steps.scope.outputs.build_paper }}" == "true" ]]; then
  PDF_SOURCE="paper/.cache/out/paper.pdf"
else
  echo "Using existing docs/reflector.pdf (paper build skipped)."
fi
```

However, `docs/reflector.pdf` is **not committed to the repository**. It is a transient artifact generated during `pages.yml` runs. The `docs/` directory contains only static HTML, images, and metadata files.

**Impact:** Any push that triggers `pages.yml` but does not rebuild the paper (e.g., a docs-only change) will fail with:

```
Error: Expected PDF not found at 'docs/reflector.pdf'
```

This is the exact failure pattern described in the issue.

**Root cause:** The fallback design assumes PDFs are committed or previously staged into `docs/`. This assumption is not met. PDFs only exist in `docs/` transiently during a workflow run that built them.

**Same issue applies to:** `reflector-magazine.pdf`, `reflector-magazine-print.pdf`, `docs/figures/hero.png` (source: `paper/figures/hero.png`).

---

### F4 — License Mismatch in `.zenodo.json`

**Severity: Medium**
**Domain: Zenodo Integration**

`.zenodo.json` declares:

```json
"license": "mit"
```

The repository uses Apache-2.0 (REUSE.toml, LICENSES/Apache-2.0.txt, all SPDX headers). The license field in Zenodo metadata should reflect Apache-2.0.

**Impact:** When Zenodo ingests this file, it records MIT as the license for the archived publication. This misrepresents the actual license on the deposited work.

---

### F5 — Dual Release Execution Paths

**Severity: Medium**
**Domain: Release Workflow**

The repository has two separate release-creating workflows:

1. `publication.yml` — triggered by VERSION changes; includes a `package` job and a `release` job that creates a GitHub Release with full artifact inventory.
2. `release-paper.yml` — triggered by `v*.*.*` tag pushes; also creates a GitHub Release with PDFs, checksums, and manifests.

`release-tag.yml` creates annotated tags when VERSION changes on main, which then triggers `release-paper.yml`.

This means a single VERSION change on main can initiate **two independent GitHub Release creation attempts** for the same tag:
- One from `publication.yml` (via VERSION change trigger)
- One from `release-paper.yml` (via tag push triggered by `release-tag.yml`)

If both race to create the same release, the second will fail with a `release already exists` error. If one is slower and creates the release after the other has already attached artifacts, artifacts may be incomplete or duplicated.

**Root cause:** Incremental workflow decomposition created two parallel paths to the same destination without a coordination mechanism.

---

### F6 — Zenodo Integration Is Fully Manual

**Severity: Medium**
**Domain: Zenodo Archival**

`.zenodo.json` is present and populated. However, the Zenodo deposit workflow is:

1. Create GitHub Release manually
2. Zenodo GitHub integration (must be enabled in Zenodo settings) detects the release
3. Zenodo creates a deposit from the GitHub release source archive

**Issues:**
- Zenodo GitHub integration must be enabled manually in the Zenodo web interface — this is not documented or automated.
- Zenodo harvests the GitHub source archive (`.zip`/`.tar.gz`), **not the generated PDF artifacts** attached to the release.
- DOIs `10.5281/zenodo.20477044` and `10.5281/zenodo.20477045` are pre-assigned placeholder values, not necessarily minted by Zenodo. Their validity has not been verified.
- The `zenodo-readiness.md` audit (dated for v0.1.0) notes: "currently returns 404 (release object not yet created)" — the release has not been created.

**What Zenodo will archive:** Source code zip, not PDFs, not arXiv bundles. This is the most significant Zenodo architectural gap.

---

### F7 — Release Staging Directory Is Ephemeral

**Severity: Medium**
**Domain: Artifact Lifecycle**

The `release/reflector-vX.Y.Z/` directory is created during CI runs and never committed to the repository. It exists only as a GitHub Actions artifact or within a running workflow. The repository root contains no `release/` directory.

**Impact:**
- There is no persistent record of what was in any given release staging bundle outside of GitHub Releases themselves.
- If a workflow fails mid-packaging (after some artifacts are staged but before the GitHub Release is created), artifacts are lost.
- `scripts/stage-publication-release.py` assumes the staging directory is pre-populated; if called in isolation without the full workflow context, it fails.

---

### F8 — `publication.yml` Scope Detection Patterns Incomplete

**Severity: Low–Medium**
**Domain: Incremental Build Logic**

The `detect-scope` job in `publication.yml` does not include `magazine/**` as a pattern that sets `PAPER_CHANGED=true`. Magazine-only changes trigger `build-magazine.yml` and `pages.yml` directly, bypassing `publication.yml` entirely.

This means:
- Magazine-only releases are not possible through `publication.yml` — the only path is `pages.yml` (no release).
- If a magazine change also requires a new release, it must be accompanied by a VERSION change to trigger the full release pipeline.

This is likely intentional design, but is undocumented and creates confusion about when a new release is expected.

---

### F9 — Stale Version Reference in `docs/index.html`

**Severity: Low**
**Domain: Documentation**

(See F2 for root cause.) Additionally: `docs/index.html` contains a hardcoded placeholder status description ("v0.0.1") suggesting it was created early in the project and has not been updated.

---

### F10 — Documentation Fragmentation

**Severity: Low**
**Domain: Documentation**

Publication system documentation is distributed across:

| File | Content | Freshness |
|---|---|---|
| `docs/release-process.md` | Release pipeline overview | Current |
| `docs/publication-infrastructure.md` | Artifact paths, packaging contract | Current |
| `docs/publication-architecture.md` | High-level architectural notes | Sparse; underdeveloped |
| `docs/workflows.md` | Workflow overview | Current |
| `00-README.md` | Repository orientation | Current |
| `ROADMAP.md` | Long-term vision | Current |
| `TODO.md` | Completion checklist | Partially outdated |
| `audits/publication-readiness-audit.md` | Readiness snapshot (dated) | Dated snapshot |
| `audits/zenodo-readiness.md` | Zenodo handoff checklist (v0.1.0) | Outdated (v0.1.0, release never created) |

There is no single document that maps the complete current end-to-end state of the publication system. Readers must synthesize across many files.

---

### F11 — `publication.yml` arXiv Scope Uses Inconsistent Build Paths

**Severity: Low**
**Domain: Build Architecture**

The `build-arxiv-bundles` job in `publication.yml` runs only when `paper_changed == 'true'`. However, the arXiv bundle is a zip of the `paper/` source tree — it does not depend on a built PDF. The bundle could be produced independently of the paper build job, but the current dependency chain requires the paper to build successfully before the arXiv bundle can be packaged.

This means a LaTeX build failure (e.g., broken figure path) blocks arXiv bundle generation even though the source zip could still be valid for manual inspection.

---

### F12 — `\today` in Paper Macros Breaks Reproducibility

**Severity: Low**
**Domain: Build Reproducibility**

`paper/macros/metadata.tex` uses `\today` for the paper date. This means two builds of identical source produce PDFs with different embedded dates. The build reproducibility validator flags this as a warning (documented in `audits/build-reproducibility.md`).

---

## Artifact Lifecycle

### Artifact Inventory

| Artifact | Producer | Location | Consumer | Publication Target |
|---|---|---|---|---|
| `paper/.cache/out/paper.pdf` | `xu-cheng/latex-action@v4` | Ephemeral (build container) | `pages.yml` copy step, `release-paper.yml` | — |
| `docs/reflector.pdf` | `pages.yml` copy step | Transient (not committed) | GitHub Pages upload | `egohygiene.github.io/reflector/reflector.pdf` |
| `magazine/.cache/out/magazine.pdf` | `xu-cheng/latex-action@v4` | Ephemeral | `pages.yml` copy step | — |
| `magazine/dist/reflector-magazine.pdf` | `pages.yml` / `build-magazine.yml` | Transient (not committed) | `pages.yml` → `docs/` | — |
| `docs/reflector-magazine.pdf` | `pages.yml` copy step | Transient | GitHub Pages upload | `egohygiene.github.io/reflector/reflector-magazine.pdf` |
| `docs/reflector-magazine-print.pdf` | `pages.yml` copy step | Transient | GitHub Pages upload | `egohygiene.github.io/reflector/reflector-magazine-print.pdf` |
| `docs/figures/hero.png` | `pages.yml` copy step (source: `paper/figures/hero.png`) | Transient | GitHub Pages upload | `egohygiene.github.io/reflector/figures/hero.png` |
| `release/reflector-vX.Y.Z/reflector.pdf` | `release-paper.yml` | Ephemeral | GitHub Release upload | GitHub Release asset |
| `release/reflector-vX.Y.Z/reflector-magazine.pdf` | `release-paper.yml` | Ephemeral | GitHub Release upload | GitHub Release asset |
| `release/reflector-vX.Y.Z/reflector-arxiv-vX.Y.Z.zip` | `release-paper.yml` | Ephemeral | GitHub Release upload | GitHub Release asset |
| `release/reflector-vX.Y.Z/checksums.txt` | `scripts/stage-publication-release.py` | Ephemeral | GitHub Release upload | GitHub Release asset |
| `release/reflector-vX.Y.Z/release-manifest.json` | `scripts/stage-publication-release.py` | Ephemeral | GitHub Release upload | GitHub Release asset |
| `release-manifest.json` (root) | Manually maintained | Committed | `scripts/validate-release-lifecycle.py`, `scripts/validate-metadata.py` | — |
| `publication.json` (root) | Manually maintained | Committed | Metadata validation, Pages manifest | — |
| `.zenodo.json` | Manually maintained | Committed | Zenodo GitHub integration | Zenodo deposit metadata |

### Key Observation: No Committed Artifacts

All generated PDF artifacts (paper, magazine) exist only transiently during CI runs. The repository itself contains no compiled artifacts. This is by design (artifacts in `.gitignore` via `.cache/`), but it means:

1. The `pages.yml` fallback path (reuse existing `docs/` PDFs when build is skipped) has no artifact to fall back to.
2. There is no "last known good" PDF in the repository without consulting the last successful GitHub Release or Pages deployment.

---

## Build Issues

| Issue | Location | Severity |
|---|---|---|
| Missing `git cat-file` guard | `publication.yml` detect-scope | High |
| `\today` timestamp drift | `paper/macros/metadata.tex` | Low |
| arXiv bundle production blocked by LaTeX failure | `publication.yml` build-arxiv-bundles job | Low |
| Magazine-only changes cannot trigger a release | `publication.yml` scope detection | Low |

---

## Deployment Issues

| Issue | Location | Severity |
|---|---|---|
| `docs/` PDFs missing when paper build is skipped | `pages.yml` synchronize step | High |
| `docs/figures/hero.png` missing when build is skipped | `pages.yml` synchronize step | High |
| `docs/index.html` has stale `v0.0.1` version | `docs/index.html` | Medium |
| `docs/publication.json` is generated per-run, not committed | `pages.yml` synchronize step | Medium |

---

## Release Issues

| Issue | Location | Severity |
|---|---|---|
| Dual release creation paths can race | `publication.yml` + `release-tag.yml` + `release-paper.yml` | Medium |
| Release staging directory is ephemeral | `release/reflector-vX.Y.Z/` | Medium |
| `release-paper.yml` builds paper independently (no artifact reuse from `publication.yml`) | `release-paper.yml` | Medium |
| `CHANGELOG.md` entry required but release-please manages changelog separately | `release-paper.yml` validation step | Low |

---

## Zenodo Issues

| Issue | Location | Severity |
|---|---|---|
| License field is `mit` (should be `apache-2.0`) | `.zenodo.json` | Medium |
| DOIs are pre-assigned placeholders, not yet verified | `.zenodo.json`, `metadata/publication.yaml`, `CITATION.cff` | Medium |
| GitHub Release for v0.1.0 was never created | `audits/zenodo-readiness.md` | High |
| Zenodo receives source archive only, not PDFs | Zenodo GitHub integration architecture | Medium |
| Zenodo integration enablement is undocumented | (no docs) | Medium |
| `zenodo-readiness.md` is dated v0.1.0; current version is v0.1.1 | `audits/zenodo-readiness.md` | Low |

---

## Documentation Issues

| Issue | File | Severity |
|---|---|---|
| `docs/index.html` version hardcoded as v0.0.1 | `docs/index.html` | Medium |
| `audits/zenodo-readiness.md` references v0.1.0 release that was never created | `audits/zenodo-readiness.md` | Medium |
| `docs/publication-architecture.md` is sparse and underdeveloped | `docs/publication-architecture.md` | Low |
| No single document describes the full current publication flow | Multiple files | Low |
| `TODO.md` items marked complete may be outdated (e.g., "All GitHub Actions passing" with known failures) | `TODO.md` | Low |

---

## Recommended Improvements

### Highest Priority

1. **Fix `publication.yml` detect-scope BASE guard (F1):** Add the `git cat-file -e "${BASE}^{commit}"` availability check before running `git diff`, matching the guard already in `pages.yml`. This is a one-line fix with high impact.

2. **Fix Pages fallback failure for missing `docs/` PDFs (F3):** Either (a) commit pre-built PDFs to `docs/` as part of the release process so the fallback has something to use, or (b) make the fallback graceful (skip verification rather than failing hard), or (c) always build all artifacts regardless of scope. Option (b) is the least disruptive short-term fix.

3. **Fix `.zenodo.json` license field (F4):** Change `"license": "mit"` to `"license": "Apache-2.0"` (Zenodo uses SPDX identifiers). This is a one-line fix.

### Medium Priority

4. **Resolve dual release paths (F5):** Decide whether `publication.yml` or `release-paper.yml` is the canonical release creator. The dual-path design creates race conditions. Recommended approach: `publication.yml` orchestrates the full release; `release-paper.yml` becomes a tag-only validation workflow (no release creation).

5. **Update `docs/index.html` to read version from `docs/publication.json` dynamically (F2/F9):** Replace the hardcoded `v0.0.1` with a JavaScript read of the `publication.json` manifest that is generated at deploy time.

6. **Document Zenodo integration enablement (F6):** Add a step-by-step checklist to `docs/release-process.md` for enabling the Zenodo GitHub integration and triggering first deposit.

7. **Clarify Zenodo artifact harvesting (F6):** Decide whether Zenodo should archive source only (current behavior via GitHub integration), or PDFs (requires manual Zenodo upload or API automation). Document the decision.

### Lower Priority

8. **Replace `\today` in paper macros with a fixed date (F12):** Resolves the build reproducibility warning. The date should derive from `metadata/publication.yaml:date_released`.

9. **Unify publication documentation into a single reference document (F10):** Create `docs/publication-system-reference.md` that synthesizes architecture, artifact paths, workflow triggers, and failure modes into one authoritative map.

10. **Decouple arXiv bundle production from LaTeX build success (F11):** The source zip can always be generated regardless of PDF build status. Split the arXiv bundle into a separate job that does not depend on `build-paper`.

---

## Prioritized Action Plan

| Priority | Issue | Impact | Effort |
|---|---|---|---|
| 1 | Add `git cat-file` guard to `publication.yml` detect-scope | Eliminates `fatal: bad object` failures | Small |
| 2 | Fix `.zenodo.json` license: `mit` → `Apache-2.0` | Correct Zenodo metadata | Small |
| 3 | Fix `docs/index.html` hardcoded version | Correct public-facing version display | Small |
| 4 | Resolve Pages fallback for missing `docs/` PDFs | Eliminate "Expected PDF not found" errors | Medium |
| 5 | Clarify and consolidate dual release paths | Eliminate release race conditions | Medium |
| 6 | Create and execute GitHub Release v0.1.1 | Enable Zenodo archival | Medium |
| 7 | Document Zenodo integration setup | Unblock Zenodo deposit | Small |
| 8 | Replace `\today` with fixed date in paper macros | Achieve full build reproducibility | Small |
| 9 | Decouple arXiv bundle from LaTeX build | Allow source inspection even on build failure | Medium |
| 10 | Unify publication documentation | Reduce onboarding and debugging friction | Large |
