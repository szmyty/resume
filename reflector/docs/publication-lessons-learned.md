<!-- SPDX-FileCopyrightText: 2026 Alan Szmyt -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Publication Lessons Learned

Generated: 2026-06-03
Version: 0.1.1

---

## Overview

This document captures lessons learned during the design, implementation, and stabilization of
the `egohygiene/reflector` publication infrastructure. It distills findings from infrastructure
audits, workflow debugging, and the stabilization effort into durable guidance for this project
and future publication repositories.

Source audits:

- [`audits/publication-system-audit.md`](../audits/publication-system-audit.md)
- [`audits/publication-system-action-items.md`](../audits/publication-system-action-items.md)
- [`audits/publication-infrastructure-audit-followup.md`](../audits/publication-infrastructure-audit-followup.md)
- [`audits/archival-strategy-audit.md`](../audits/archival-strategy-audit.md)
- [`audits/zenodo-integration-audit.md`](../audits/zenodo-integration-audit.md)
- [`audits/doi-metadata-audit.md`](../audits/doi-metadata-audit.md)

---

## Reflector Publication Lessons

### L-R1 — Canonical Version Source Eliminates Drift

**Lesson:** Designate a single file (`VERSION`) as the canonical source of truth for the release
version. All other surfaces (metadata YAML, JSON manifests, citation files, Zenodo metadata)
derive from this source and are validated against it.

**What worked:** `scripts/validate-release-lifecycle.py` enforces synchronization across 7
metadata surfaces on every push. Version drift never reaches the release pipeline.

**What to replicate:** Every publication project should have a `VERSION` file and a validation
script that verifies all derived surfaces before any release action proceeds.

---

### L-R2 — Scope Detection Saves Build Time

**Lesson:** Incremental builds based on changed file paths significantly reduce CI time for
paper-only changes vs. full releases.

**What worked:** `detect-scope` in `publication.yml` distinguishes between paper changes
(rebuild paper only) and `VERSION` changes (full release pipeline). Paper changes that don't
affect the magazine or release assets run in under half the time of a full pipeline.

**What to replicate:** Use `git diff --name-only` to scope CI jobs to affected subsystems.
Provide `workflow_dispatch` inputs to override scope detection for manual runs.

**Gotcha:** Scope detection can fail if the BASE commit is unreachable (force-push, rebase,
shallow clone). Always add a `git cat-file -e` reachability guard before running `git diff`
on an unvalidated commit reference. Failing to add this guard produces `fatal: bad object`
and aborts the entire workflow before any build job runs.

---

### L-R3 — Guard All Commit References Before Use

**Lesson:** Any commit reference derived from `github.event.before` or `HEAD^` may be
unreachable in the current checkout history.

**Pattern to use:**
```bash
if [[ -n "${BASE}" ]] && ! git cat-file -e "${BASE}^{commit}" 2>/dev/null; then
  echo "Base commit is unavailable; falling back to full repository scan."
  BASE=""
fi
```

**What went wrong:** `publication.yml` was missing this guard while `pages.yml` had it.
The inconsistency caused `publication.yml` to fail on force-pushed branches and rebased PRs
while `pages.yml` handled the same condition gracefully.

**Rule:** Apply the same reachability guard to every workflow that resolves a BASE commit.
Inconsistent application creates an asymmetric failure surface.

---

### L-R4 — Build Artifacts Must Not Be Assumed Present

**Lesson:** Generated PDFs are never committed to the repository. Any workflow step that
assumes a PDF exists at a local path (e.g., `docs/reflector.pdf`) without having built it in
the same run will fail.

**What went wrong:** `pages.yml` had a fallback that assumed `docs/reflector.pdf` was
available when the paper build was skipped. Because PDFs are not committed, this fallback
always failed on non-paper changes (e.g., docs-only pushes).

**What was fixed:** The synchronization step now warns and skips the PDF copy gracefully when
the build was skipped and no local fallback exists. GitHub Pages retains the previously
deployed PDFs from the last successful build, so the deployed site remains intact.

**Rule:** Never write fallback logic that assumes the presence of a non-committed build
artifact. Either build the artifact or skip the step explicitly.

---

### L-R5 — Two Workflows Targeting the Same Resource Require Coordination

**Lesson:** When two independent workflows can create the same GitHub Release object, they will
eventually race. Race conditions produce intermittent failures that are difficult to debug in CI.

**What went wrong:** `publication.yml` (triggered by VERSION change) and `release-paper.yml`
(triggered by tag push from `release-tag.yml`) both attempted to create the same GitHub Release.
Under normal execution order, one would fail with "release already exists."

**What was fixed:** `release-paper.yml` now runs `gh release view ${TAG}` before any release
creation step. If the release exists, it exits cleanly. This converts a race condition into a
soft handoff.

**Rule:** When two workflows can target the same resource (a release, a deployment, a tag),
the secondary path must include an existence check and a clean exit. Never rely on timing.

---

### L-R6 — Deterministic Artifacts Enable Reproducibility Audits

**Lesson:** All release artifacts should be byte-deterministic (or structurally identical)
across equivalent builds. This enables cryptographic verification of released assets.

**What was implemented:**
- `tar` uses `--sort=name` and `--mtime=@0` for deterministic ordering
- `zip` uses `-X` to strip extended attributes
- `checksums.txt` provides SHA-256 for all assets
- `scripts/validate-build-reproducibility.py` flags non-deterministic inputs (e.g., `\today`)

**What remains:** `\today` in LaTeX paper macros was already replaced with a fixed date string
(`2026-05-22`), but this must be kept synchronized when a new release is created.

**Rule:** Treat reproducibility as an architectural constraint, not an optimization. Build
scripts and CI configuration should enforce it from the start.

---

### L-R7 — Metadata Synchronization Must Be Automated

**Lesson:** Manually maintaining synchronization across 7+ metadata surfaces (VERSION,
publication.yaml, CITATION.cff, .zenodo.json, codemeta.json, release-manifest.json,
publication.json) is error-prone and does not scale.

**What was implemented:** `scripts/validate-metadata.py` validates cross-file consistency for
version, DOI, author, and title fields. DOI drift, version drift, and author metadata
inconsistencies are all caught before release.

**What went wrong before automation:** `.zenodo.json` had `"license": "mit"` (incorrect) and
`docs/index.html` had a stale `v0.0.1` version string — both caused by manual drift.

**Rule:** Any metadata surface that derives from a canonical source must be validated
programmatically, not by human review. Build the validation script before building the release
pipeline.

---

## Publication Workflow Lessons

### L-W1 — Stage Before Upload

**Lesson:** Assemble all release artifacts into a single staging directory before uploading
anything. Never upload artifacts piecemeal from different paths in the same workflow.

**What was implemented:** All artifacts are staged into `release/reflector-vX.Y.Z/` by the
`package` job. `scripts/stage-publication-release.py` validates completeness, generates
checksums, and emits manifests before any upload occurs.

**Why it matters:** Piecemeal uploads create partial releases if the workflow fails mid-upload.
A staging step with an all-or-nothing validation gate ensures the release is complete or the
upload does not proceed.

---

### L-W2 — Dry Run Mode Is Essential

**Lesson:** Every release workflow must support a `dry_run` mode that runs the entire pipeline
without creating the actual release.

**What was implemented:** `publication.yml` accepts `dry_run: true` as a `workflow_dispatch`
input. The full validation → build → package pipeline runs, but the `release` job skips the
`softprops/action-gh-release@v3` step.

**Why it matters:** Without dry run, the only way to test a release pipeline is to run a
real release. This creates fear around testing and encourages untested changes.

---

### L-W3 — Scope Gates Prevent Unnecessary Work

**Lesson:** Use job-level `if:` conditions on `needs.detect-scope.outputs.*` to prevent
expensive jobs (LaTeX compilation) from running when they are not needed.

**What was implemented:** `build-paper` only runs when `paper_changed == 'true'`;
`build-magazine`, `package`, and `release` only run when `full_release == 'true'`.

**Gotcha:** Magazine-only changes (no VERSION bump) never trigger `publication.yml`'s full
release pipeline. Magazine builds that also require a release must be accompanied by a VERSION
change. This is intentional design but was not documented and caused confusion.

---

### L-W4 — Document Workflow Ownership Explicitly

**Lesson:** In a multi-workflow release system, every workflow must have a clearly documented
ownership domain. Overlapping ownership produces race conditions, redundant work, and
debugging confusion.

**What was missing:** The boundary between `publication.yml` and `release-paper.yml` was
implicit. Both workflows could create a GitHub Release, but neither documented when the other
was expected to handle it.

**What was implemented:** `docs/publication-workflow-reference.md` and
`docs/publication-workflow-map.md` explicitly document the ownership hierarchy:
- `publication.yml` is the canonical release owner
- `release-paper.yml` is the secondary path (tag-triggered)
- `release-tag.yml` is the tag automation layer

---

### L-W5 — arXiv Bundle Should Be Decoupled from LaTeX Build Success

**Lesson:** The arXiv source bundle (a zip of LaTeX sources) does not require a successfully
compiled PDF. Decoupling arXiv bundle generation from the paper build job allows source
inspection even when the paper fails to compile.

**Current state:** arXiv bundle generation is coupled to `build-paper` job success. If the
LaTeX build fails, no arXiv bundle is produced.

**Future recommendation:** Create a `build-arxiv-source` job that depends only on
`detect-scope`, not on `build-paper`. This allows contributors to inspect and submit the source
bundle independently of a successful CI PDF build.

---

## Audit Findings Summary

The following table summarizes all findings from the publication system audit and their
resolution status:

| Finding | Severity | Status | Resolution |
|---|---|---|---|
| F1 — Missing `git cat-file` guard in `publication.yml` | High | ✅ Fixed | Added BASE reachability guard to detect-scope |
| F2 — Stale `docs/index.html` version reference | Medium | ✅ Fixed | Updated hardcoded version string to `v0.1.1` |
| F3 — Pages fallback fails when `docs/` PDFs absent | High | ✅ Fixed | Synchronization step now warns and skips gracefully |
| F4 — License mismatch in `.zenodo.json` | Medium | ✅ Fixed | Changed `"mit"` to `"apache-2.0"` |
| F5 — Dual release execution paths race | Medium | ✅ Fixed | `release-paper.yml` pre-checks for existing release |
| F6 — Zenodo integration fully manual | Medium | ⚠️ Deferred | Documentation added; API automation tracked separately |
| F7 — Release staging directory is ephemeral | Medium | ℹ️ By design | No persistent staging; GitHub Releases are the archive |
| F8 — `publication.yml` scope missing magazine changes | Low–Medium | ℹ️ By design | Magazine-only releases require VERSION bump (now documented) |
| F9 — Stale version in `docs/index.html` | Low | ✅ Fixed | Same as F2 |
| F10 — Documentation fragmentation | Low–Medium | ✅ Addressed | New reference documents created |
| F11 — arXiv bundle coupled to LaTeX build | Low | ⚠️ Deferred | Architectural improvement tracked |
| F12 — `\today` breaks reproducibility | Low | ✅ Fixed (prior) | `paper/macros/metadata.tex` uses fixed date |

---

## Future Recommendations

### FR-1 — Automate Zenodo PDF Upload

**Priority:** High
**Effort:** Large

Zenodo's GitHub integration only harvests the source archive. All PDFs and arXiv bundles must
be uploaded manually. Implementing a Zenodo API integration using `ZENODO_TOKEN` would:

1. Automatically deposit the canonical release bundle on every GitHub Release
2. Upload PDFs, arXiv bundles, and metadata companions directly
3. Record the assigned DOI in metadata surfaces for the next release cycle

**Prerequisite:** `ZENODO_TOKEN` secret in repository settings; Zenodo sandbox testing.

---

### FR-2 — Persist Build Artifacts via GitHub Actions Cache

**Priority:** Medium
**Effort:** Medium

The most common Pages deployment failure is a missing PDF fallback when the paper build is
skipped. A durable solution would cache built PDFs via GitHub Actions cache keyed to the
branch after each successful build. Non-paper changes that trigger Pages deployment would
restore the cached PDF instead of failing.

**Alternative:** Commit placeholder PDFs to `docs/` (accepted by Pages). This avoids caching
complexity but adds binary churn to git history.

---

### FR-3 — Decouple arXiv Bundle from LaTeX Build

**Priority:** Low
**Effort:** Medium

Create a `build-arxiv-source` job in `publication.yml` that depends only on `detect-scope`,
not on `build-paper`. This allows source bundle inspection and upload even when the paper fails
to compile.

---

### FR-4 — Automate `docs/index.html` Version Updates

**Priority:** Low
**Effort:** Low

`docs/index.html` contains a hardcoded version string that drifts as `VERSION` advances.
Options:
1. Add a CI step to update `docs/index.html` from `VERSION` before deployment
2. Add JavaScript to read `publication.json` and populate the version dynamically

Either approach eliminates the manual maintenance burden and prevents version drift from being
visible on the public Pages landing page.

---

### FR-5 — Normalize Release Asset Set

**Priority:** Medium
**Effort:** Low

Current releases (`v0.1.0`, `v0.1.1`) are missing `reflector-arxiv-vX.Y.Z.zip`,
`reflector-arxiv-vX.Y.Z.tar.gz`, and `publication-inventory.json` from the canonical release
bundle. Add a post-release validation job to `publication.yml` that verifies all canonical
bundle artifacts are present in the newly created GitHub Release.

---

### FR-6 — Post-Mint DOI Update Automation

**Priority:** Low
**Effort:** Medium

After Zenodo mints a DOI, all DOI-bearing metadata surfaces must be updated manually:
`metadata/publication.yaml`, `CITATION.cff`, `.zenodo.json`, `codemeta.json`. A script or
workflow step that applies a new DOI value across all surfaces (and then validates the result)
would reduce the risk of post-mint metadata drift.

---

## Institutional Knowledge

### Why `publication.yml` is the Canonical Orchestrator

`publication.yml` was designed as the single authoritative entry point for full publication
releases. All other release-adjacent workflows (`release-tag.yml`, `release-paper.yml`) are
satellites that either prepare for or respond to events in `publication.yml`'s pipeline.

This architecture concentrates the release logic in one place and makes the full release flow
auditable from a single workflow file.

### Why Artifacts Are Not Committed to the Repository

All generated PDFs are excluded from the repository via `.gitignore` / `.cache/`. This is
intentional:
- PDFs are binary files that bloat git history
- Every build is deterministic and reproducible from source
- GitHub Releases serve as the immutable artifact archive

The trade-off is that non-build-triggering changes that deploy to Pages have no local fallback
PDF. This is mitigated by graceful degradation (warning instead of failure) and by GitHub Pages
retaining the last successful deployment.

### Why Two Release Paths Exist

`release-paper.yml` predates `publication.yml` as the primary release mechanism. When
`publication.yml` was introduced as the canonical orchestrator, `release-paper.yml` was
retained as a fallback for tag-triggered releases (e.g., manually created tags). The existence
guard in `release-paper.yml` converts the dual-path architecture from a race condition into a
redundancy.

Future cleanup: once `publication.yml` is the confirmed sole source of GitHub Releases,
`release-paper.yml` can be demoted to a no-op stub or removed entirely.

### Why `docs/` PDFs Are Transient

GitHub Pages deploys from the `_site/` artifact generated by `pages.yml`. The `docs/`
directory acts as the staging area for that artifact. Because PDFs are not committed to the
repository, they are only present in `docs/` during workflow runs that built them.

The Pages infrastructure retains the deployed `_site/` across runs — GitHub serves the last
successfully uploaded artifact until a new one is uploaded. So even if a docs-only push
skips the paper build, the previously built PDFs remain live on the Pages site.

---

## Summary: Key Principles for Future Publication Repositories

1. **One canonical version source.** `VERSION` is the only place a version string lives. Everything else derives from it.
2. **Validate before building.** All metadata synchronization checks run in Stage 1 before any expensive build work.
3. **Guard all commit references.** Every `git diff` against a stored commit reference must check reachability first.
4. **Stage before upload.** Assemble all artifacts, generate checksums, validate completeness — then upload.
5. **Dry run mode is required.** Release pipelines must be testable without creating real releases.
6. **Ownership must be explicit.** Every workflow owns exactly one domain. Overlapping ownership requires coordination guards.
7. **Artifacts are ephemeral.** Do not assume a build artifact exists from a prior run. Either build it or skip the step.
8. **Metadata drift is a release blocker.** Automated synchronization validation must run on every push that changes metadata surfaces.
9. **Graceful degradation over hard failure.** When an optional artifact is absent, warn and continue. Fail only on truly required artifacts.
10. **Document institutional knowledge.** Architecture decisions, ownership boundaries, and known quirks should be documented in durable reference files — not in commit messages or issue comments.

---

## Related Documents

| Document | Purpose |
|---|---|
| [`docs/publication-system-reference.md`](publication-system-reference.md) | End-to-end publication lifecycle overview |
| [`docs/publication-workflow-reference.md`](publication-workflow-reference.md) | Workflow registry and ownership |
| [`docs/publication-artifact-reference.md`](publication-artifact-reference.md) | Artifact lifecycle and ownership |
| [`audits/publication-system-audit.md`](../audits/publication-system-audit.md) | Full infrastructure audit with all findings |
| [`audits/publication-system-action-items.md`](../audits/publication-system-action-items.md) | Action items derived from the audit |
| [`audits/publication-infrastructure-audit-followup.md`](../audits/publication-infrastructure-audit-followup.md) | Resolution tracking |
