<!-- SPDX-FileCopyrightText: 2026 Alan Szmyt -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Publication System — Action Items

Generated: 2026-06-02
Source audit: [`audits/publication-system-audit.md`](./publication-system-audit.md)

---

## Overview

Action items are derived from the findings in the publication system audit. They are organized into three tiers: small (< 1 hour), medium (1–4 hours), and large (> 4 hours). Each item includes impact, complexity, and rationale.

Items are ordered by priority within each tier.

---

## Small Tasks

### S1 — Add `git cat-file` guard to `publication.yml` detect-scope

**File:** `.github/workflows/publication.yml`
**Finding:** F1
**Impact:** Eliminates `fatal: bad object` errors that cause the entire publication workflow to fail on initial branch pushes, force-pushes, or rebased branches.
**Complexity:** Low — single code block addition, ~5 lines.

**Change:**
In the `detect-scope` job, after resolving `BASE` from `github.event.before` or `git rev-list --max-count=1 HEAD^`, add a reachability guard before running `git diff`:

```bash
if [[ -n "${BASE}" ]] && ! git cat-file -e "${BASE}^{commit}" 2>/dev/null; then
  echo "Base commit ${BASE} is unavailable in checkout history; falling back to full repository scan."
  BASE=""
fi
```

This mirrors the guard already present in `pages.yml` and `publication.yml`'s verify step, completing the consistent application pattern.

**Rationale:** The same guard exists in `pages.yml` but was not applied to `publication.yml`. One missing guard is the root cause of the `fatal: bad object` failure class.

---

### S2 — Fix `.zenodo.json` license field

**File:** `.zenodo.json`
**Finding:** F4
**Impact:** Corrects the license Zenodo will display and record for the deposited work. Currently records MIT; should be Apache-2.0.
**Complexity:** Low — single value change.

**Change:**
```json
"license": "apache-2.0"
```

Zenodo accepts SPDX license identifiers. `Apache-2.0` (case-insensitive `apache-2.0`) is the correct identifier for this repository.

**Rationale:** The repository uses Apache-2.0 across all SPDX headers, `REUSE.toml`, and `LICENSES/Apache-2.0.txt`. The MIT value in `.zenodo.json` is an oversight from an earlier draft.

---

### S3 — Fix `docs/index.html` hardcoded version string

**File:** `docs/index.html`
**Finding:** F2, F9
**Impact:** Corrects the public-facing version displayed on the GitHub Pages landing page. Currently shows `v0.0.1` when the canonical version is `v0.1.1`.
**Complexity:** Low — update hardcoded string, optionally add JS to read from `docs/publication.json`.

**Option A (minimal):** Replace `v0.0.1` with the current version string `v0.1.1`.

**Option B (durable):** Add a small inline JavaScript snippet that fetches `publication.json` and populates the version `<dd>` element dynamically, so it auto-updates with each Pages deployment.

**Rationale:** The landing page version is the first thing visitors see. A stale version number undermines trust in the deployment's accuracy.

---

### S4 — Replace `\today` in paper macros with a fixed date

**File:** `paper/macros/metadata.tex`
**Finding:** F12
**Impact:** Achieves full build reproducibility — two identical builds produce byte-identical (or structurally identical) PDFs with the same embedded date.
**Complexity:** Low — replace `\today` with a fixed date string.

**Change:**
Replace:
```latex
\newcommand{\paperdate}{\today}
```
With:
```latex
\newcommand{\paperdate}{2026-05-22}
```

The date `2026-05-22` matches `date_released` in `metadata/publication.yaml`. Update this value when a new version is released.

**Rationale:** `\today` introduces timestamp drift — the PDF's printed date changes with every build. This is flagged by `scripts/validate-build-reproducibility.py` as a warning.

---

### S5 — Add Zenodo integration setup documentation

**File:** `docs/release-process.md`
**Finding:** F6
**Impact:** Documents the manual steps required to enable Zenodo GitHub integration and trigger the first deposit. Unblocks the Zenodo archival workflow.
**Complexity:** Low — prose addition to existing documentation.

**Content to add:**
A "Zenodo Setup" section covering:
1. Log in to Zenodo and enable GitHub integration for `egohygiene/reflector`
2. Create the first GitHub Release (which triggers Zenodo harvesting)
3. Verify the DOI mints correctly and matches `metadata/publication.yaml`
4. Note that Zenodo harvests source archives, not release PDF assets
5. Steps to update DOI metadata after minting (if DOIs change from placeholders)

**Rationale:** The Zenodo integration is a manual one-time setup. Without documentation, it will not be completed.

---

## Medium Tasks

### M1 — Fix Pages fallback for missing `docs/` PDFs

**Files:** `.github/workflows/pages.yml`, `docs/reflector.pdf` (placeholder), or workflow logic
**Finding:** F3
**Impact:** Eliminates the "Expected PDF not found at `docs/reflector.pdf`" failure that occurs whenever `pages.yml` runs for a non-paper change (e.g., a docs-only commit).
**Complexity:** Medium — requires choosing and implementing one of several architectural approaches.

**Option A — Commit placeholder PDFs to `docs/`:**
Add empty/placeholder PDF files to `docs/` so the fallback path has a file to reference. The actual content is replaced on each build. Pro: minimal workflow change. Con: commits binary files to the repository.

**Option B — Make synchronization step graceful for skipped builds:**
Modify the "Synchronize publication assets into docs" step to skip the PDF check when the build was skipped AND the `docs/` PDF is absent. Print a warning and continue. This means a Pages deployment after a non-build-triggering change may serve stale PDFs from the last deployment (which is fine — Pages retains them from the previous deployment's `_site/` artifact).

**Option C — Always build all artifacts:**
Remove incremental build logic from `pages.yml` and always build paper and magazine on every trigger. Pro: eliminates the fallback problem entirely. Con: every `docs/` change triggers a full LaTeX build (slow).

**Recommended:** Option B is the least disruptive. The Pages deployment already serves the last deployed PDFs. Making the synchronization step non-fatal for missing local PDFs preserves the incremental build benefit.

**Rationale:** This is the most common reported failure mode ("Expected PDF not found at: docs/reflector.pdf"). It is triggered by any non-paper/magazine push that touches `docs/`.

---

### M2 — Consolidate dual release creation paths

**Files:** `.github/workflows/publication.yml`, `.github/workflows/release-paper.yml`, `.github/workflows/release-tag.yml`
**Finding:** F5
**Impact:** Eliminates the race condition between `publication.yml` and `release-paper.yml` both trying to create the same GitHub Release.
**Complexity:** Medium — requires workflow coordination decisions.

**Recommended approach:**
- `publication.yml` remains the canonical full-release orchestrator (it already has the full validation → build → package → release pipeline).
- `release-paper.yml` is modified to skip release creation when `publication.yml` is responsible (e.g., by checking if a release already exists, or by removing the release creation step and making it an artifact-only workflow).
- `release-tag.yml` continues creating the annotated tag, but `release-paper.yml`'s release creation step becomes a no-op if the release already exists (soft failure mode).

Alternatively, add a release-exists check at the top of `release-paper.yml`:
```bash
if gh release view "${TAG}" >/dev/null 2>&1; then
  echo "Release ${TAG} already exists. Skipping."
  exit 0
fi
```

**Rationale:** Two workflows targeting the same release object under race conditions produces intermittent failures that are hard to debug. The coordination cost is low; the ambiguity cost is high.

---

### M3 — Create and execute GitHub Release v0.1.1

**Files:** GitHub Release UI or `gh` CLI, `audits/zenodo-readiness.md`
**Finding:** F6 (downstream)
**Impact:** Enables Zenodo archival, satisfies Phase 5 of `TODO.md`, and provides the canonical release artifact set for v0.1.1.
**Complexity:** Medium — requires triggering the release workflow and verifying all assets attach correctly.

**Steps:**
1. Ensure all GitHub Actions pass on `main`.
2. Manually dispatch `publication.yml` with `dry_run: false` and `release_scope: full` or wait for the next VERSION change to trigger automatically.
3. Verify GitHub Release `v0.1.1` is created with all expected assets (reflector.pdf, reflector-magazine.pdf, reflector-magazine-print.pdf, checksums.txt, release-manifest.json).
4. Verify Zenodo harvests the release (requires Zenodo GitHub integration enabled per S5).

**Rationale:** The `zenodo-readiness.md` checklist documents a handoff for v0.1.0 that was never completed. The current version is v0.1.1. Without a GitHub Release, Zenodo cannot mint a DOI.

---

### M4 — Decouple arXiv bundle production from LaTeX build

**Files:** `.github/workflows/publication.yml`
**Finding:** F11
**Impact:** Allows the arXiv source bundle (a zip of `paper/` sources) to be generated and validated even when the LaTeX build fails. Useful for source-level debugging.
**Complexity:** Medium — requires splitting job dependency chain.

**Change:**
In `publication.yml`, create a `build-arxiv-source` job that:
- Depends only on `detect-scope` (not on `build-paper`)
- Zips the `paper/` source tree
- Uploads as an artifact

The full `reflector-arxiv-vX.Y.Z.zip` artifact (source + PDF) can still be assembled in the `package` job after both `build-paper` and `build-arxiv-source` complete.

**Rationale:** The arXiv source bundle is a zip of LaTeX sources — it does not require a successful PDF build. Decoupling allows source inspection even when the paper fails to compile.

---

## Large Tasks

### L1 — Fix Pages deployment to handle absent `docs/` PDFs durably

**Files:** `.github/workflows/pages.yml`, potentially `docs/`
**Finding:** F3 (extended)
**Impact:** Makes the Pages deployment reliable across all trigger conditions, not just full builds.
**Complexity:** Large — requires architectural decision about artifact persistence strategy.

**Context:**
The root issue is that GitHub Pages stores its deployed artifact in GitHub's Pages infrastructure, but the repository's `docs/` directory is the staging ground used between builds. When a non-build change triggers `pages.yml`, there are no PDFs in `docs/` because they were never committed.

**Full solution options:**

1. **Use GitHub Pages artifact caching:** After each successful build, upload the built PDFs as a long-lived GitHub Actions cache artifact keyed to the branch. On subsequent runs, restore from cache if the build is skipped.

2. **Commit PDFs to `docs/` as part of the release process:** A post-build commit step adds PDFs to `docs/` and pushes to `main`. Future non-build runs always have PDFs available. Con: PDF churn in git history.

3. **Download last successful release assets on fallback:** When build is skipped, use `gh release download` to fetch the latest PDFs from the GitHub Release. Con: requires `contents: read` on `releases`, adds latency.

4. **Split `pages.yml` into two jobs:** (a) a conditional build job, and (b) an artifact-merge job that combines newly built artifacts with previously deployed ones. Con: complex orchestration.

**Recommended:** Option 1 (artifact caching) is the most idiomatic GitHub Actions solution with no git-history impact.

**Rationale:** This is the highest-impact deployment failure. The current fallback is dead code that always fails. A durable solution is needed before the publication infrastructure can be considered production-stable.

---

### L2 — Unify publication documentation into a single reference

**Files:** New file `docs/publication-system-reference.md`, updates to multiple existing docs
**Finding:** F10
**Impact:** Reduces onboarding time and debugging friction. Provides a single authoritative map of the publication system for contributors and CI troubleshooting.
**Complexity:** Large — synthesis across 8+ documents, requires validation against current state.

**Content:**
- End-to-end publication pipeline diagram (source → build → deploy → release → archive)
- Complete artifact lifecycle table (every artifact, its producer, location, consumer, and destination)
- Workflow trigger table (every workflow, what triggers it, what it does)
- Failure mode reference (known failure conditions and their mitigations)
- Maintenance checklist (what to update when releasing a new version)

**Rationale:** The current documentation state requires reading 5–8 files to understand one end-to-end scenario. A single reference document would serve as the authoritative answer to "how does publication work?" and reduce the overhead of future infrastructure work.

---

### L3 — Automate Zenodo PDF upload on release

**Files:** `.github/workflows/publication.yml` or new `zenodo-upload.yml`
**Finding:** F6 (Zenodo receives source archive only)
**Impact:** Ensures Zenodo archives the generated PDFs alongside source. Currently Zenodo receives only the source zip from GitHub's automatic release archive.
**Complexity:** Large — requires Zenodo API integration, secret management, and testing.

**Approach:**
Use the Zenodo REST API (via `ZENODO_TOKEN` secret) to:
1. Create a new Zenodo deposition for each release.
2. Upload the built PDFs and arXiv bundles directly.
3. Set metadata from `.zenodo.json`.
4. Publish the deposition.

This replaces the passive "GitHub integration webhook" approach with an active programmatic deposit.

**Prerequisites:**
- `ZENODO_TOKEN` secret in repository settings
- Zenodo concept record ID confirmed
- API integration tested on Zenodo sandbox first

**Rationale:** Without PDF upload automation, the Zenodo archive records source code but not the canonical publication artifacts (PDFs). Academic consumers expect to download the PDF from the DOI — currently they would get a source archive.

---

## Task Summary

| ID | Tier | Task | Impact | Complexity |
|---|---|---|---|---|
| S1 | Small | Add `git cat-file` guard to `publication.yml` | Eliminates `fatal: bad object` | Low |
| S2 | Small | Fix `.zenodo.json` license field | Correct Zenodo license record | Low |
| S3 | Small | Fix `docs/index.html` version string | Correct public version display | Low |
| S4 | Small | Replace `\today` with fixed date in paper macros | Achieve full build reproducibility | Low |
| S5 | Small | Document Zenodo integration setup steps | Unblock Zenodo deposit | Low |
| M1 | Medium | Fix Pages fallback for missing `docs/` PDFs | Eliminate deployment failures | Medium |
| M2 | Medium | Consolidate dual release creation paths | Eliminate release race conditions | Medium |
| M3 | Medium | Create GitHub Release v0.1.1 | Enable Zenodo archival | Medium |
| M4 | Medium | Decouple arXiv bundle from LaTeX build | Allow source inspection on build failure | Medium |
| L1 | Large | Fix Pages deployment artifact persistence | Durable Pages deployments | Large |
| L2 | Large | Unify publication documentation | Reduce onboarding/debugging friction | Large |
| L3 | Large | Automate Zenodo PDF upload on release | Zenodo archives PDFs, not just source | Large |
