<!-- SPDX-FileCopyrightText: 2026 Alan Szmyt -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Publication Quality Workflow

This document describes the publication quality pipeline for the reflector paper,
including ChkTeX linting, automated quality checks, and the arXiv submission readiness process.

---

## Overview

The publication quality pipeline provides a reproducible quality gate that can be
run locally, through Taskfile, and through GitHub Actions before any release or
arXiv submission.

The pipeline catches:

- LaTeX structural issues (unmatched math, mismatched environments)
- Typographic problems (wrong quotes, dashes, non-breaking spaces)
- Style inconsistencies (deprecated commands, TeX primitives)
- Missing or broken references

---

## Tools

| Tool | Purpose | Config |
|------|---------|--------|
| [ChkTeX](https://www.nongnu.org/chktex/) | LaTeX semantic linter | `.chktexrc` |
| `scripts/lint-paper.sh` | ChkTeX wrapper with CI integration | — |
| `scripts/audit-chktex.py` | Generates structured audit report | — |
| `.github/workflows/paper-quality.yml` | CI quality gate workflow | — |

---

## Local Usage

### Prerequisites

ChkTeX must be installed. It is included in the TeX Live distribution:

```bash
# Ubuntu / Debian
sudo apt-get install chktex

# macOS with Homebrew TeX Live
# Already included in texlive-full

# Via tlmgr
tlmgr install chktex
```

Verify installation:

```bash
chktex --version
```

### Run individual checks

```bash
# Lint only — run ChkTeX and print warnings
task lint:paper

# Audit only — generate audits/chktex-audit.md
task audit:paper

# Full quality pipeline: build + lint + audit
task qa:paper
```

### Run scripts directly

```bash
# ChkTeX lint
./scripts/lint-paper.sh paper

# Write ChkTeX output to a file
./scripts/lint-paper.sh paper --output /tmp/chktex.txt

# Generate audit report
python scripts/audit-chktex.py --paper paper --output audits/chktex-audit.md
```

---

## CI Usage

The `paper-quality.yml` workflow runs automatically on:

- Pushes to `main` that modify paper source files (`.tex`, `.bib`, `.sty`)
- Pull requests targeting `main` with paper changes
- Manual dispatch via `workflow_dispatch`

### Workflow stages

1. **Build** — Compiles `paper/paper.tex` to PDF using `xu-cheng/latex-action`
2. **ChkTeX lint** — Runs ChkTeX with `.chktexrc` configuration
3. **Audit report** — Generates `audits/chktex-audit.md`
4. **Annotations** — Posts GitHub warning annotations on PR diffs
5. **Artifacts** — Uploads PDF, raw ChkTeX output, and audit report
6. **Quality gate** — Fails on critical warnings (W11, W17, W19)

### Artifacts

Each run produces:

| Artifact | Contents |
|----------|----------|
| `paper-quality-pdf` | Compiled PDF |
| `paper-chktex-output` | Raw ChkTeX output (`chktex-output.txt`) |
| `paper-chktex-audit` | Structured audit report (`audits/chktex-audit.md`) |
| `paper-quality-build-artifacts` | Build logs (on failure only) |

### Manual trigger with strict mode

To run the workflow with strict warning enforcement (fail on any warning):

1. Navigate to **Actions → Paper Quality → Run workflow**
2. Set `fail_on_warnings` to `true`

---

## Release Usage

Before merging a release version bump to `main`:

1. Run the full quality pipeline locally:

   ```bash
   task qa:paper
   ```

2. Review `audits/chktex-audit.md` for any remaining warnings.

3. Resolve all critical (W11, W17, W19) and high-severity (W2, W18) warnings.

4. Commit the updated `audits/chktex-audit.md` with the release:

   ```bash
   git add audits/chktex-audit.md
   git commit -m "docs: update chktex audit for release"
   ```

5. `release-tag.yml` will create an annotated `vMAJOR.MINOR.PATCH` tag from
   `VERSION` automatically, then `release-paper.yml` will build and publish the
   release artifacts (including checksums + Zenodo readiness report). Ensure
   `paper-quality.yml` passes cleanly before merging.

---

## arXiv Readiness Workflow

arXiv submissions have stricter requirements than general publication. Run the
full quality pipeline and address all warnings before submission.

### Checklist

- [ ] `task qa:paper` passes with no critical or high warnings
- [ ] `audits/chktex-audit.md` shows **Publication ready** status
- [ ] `task audit` passes (metadata + publication readiness checks)
- [ ] PDF compiles cleanly (no LaTeX errors in build log)
- [ ] All figures are referenced and exist as files
- [ ] All citations resolve in `references.bib`
- [ ] No overfull or underfull hboxes in critical sections (check `.cache/aux/paper.log`)
- [ ] Hyperlinks compile without broken URL warnings

### Inspecting build warnings

After running `task build`, inspect the LaTeX log for additional issues:

```bash
# Overfull hboxes
grep "Overfull" paper/.cache/aux/paper.log

# Underfull hboxes
grep "Underfull" paper/.cache/aux/paper.log

# Undefined references
grep "undefined" paper/.cache/aux/paper.log

# Citation warnings
grep "Citation" paper/.cache/aux/paper.log
```

The `scripts/print-latex-diagnostics.sh` script summarizes these automatically:

```bash
./scripts/print-latex-diagnostics.sh paper
```

---

## ChkTeX Configuration

ChkTeX is configured via `.chktexrc` at the repository root. The file documents
each suppressed warning with its justification.

### Severity levels

| Severity | Warning codes | Meaning |
|----------|---------------|---------|
| CRITICAL | W11, W17, W19 | Structural integrity — unmatched math/environments |
| HIGH | W2, W18 | Typographic correctness — non-breaking spaces, quotes |
| MEDIUM | W6, W8, W10, W13, W22, W33, W34, W38, W43 | Style and readability |
| LOW | All others | Informational / minor |

### Adding new suppressions

Before suppressing a warning in `.chktexrc`, verify that:

1. The warning produces only false positives for this manuscript.
2. The suppression does not mask a genuine issue.
3. A clear justification comment is added to `.chktexrc`.

### Inline suppressions

Inline suppressions (`%chktex N` comments in `.tex` files) are tracked as Warning 44
and reviewed during each audit. Use them sparingly and only when the `.chktexrc`
global suppression would hide legitimate warnings elsewhere.

---

## Troubleshooting

### ChkTeX not found

```
❌ chktex is not installed.
   Install it with: apt-get install chktex
```

Install ChkTeX using the instructions in the [Prerequisites](#prerequisites) section.

### No warnings found but paper has issues

ChkTeX checks semantic and typographic issues in LaTeX source. It does not
replace a full compilation check. Always run `task build` to catch compilation
errors that ChkTeX cannot detect.

### File not found warnings (W9)

Warning 9 is suppressed in `.chktexrc` because ChkTeX does not honour the
TEXINPUTS path used by the `latexmk` build system. File existence is validated
by the build step and `scripts/audit-publication-readiness.py`.

---

## See Also

- [Toolchain requirements](toolchain.md) — Full TeX Live setup
- [Publication architecture](publication-architecture.md) — Paper structure overview
- [Workflows](workflows.md) — All CI/CD workflows
- [ChkTeX manual](https://www.nongnu.org/chktex/ChkTeX.pdf) — Complete warning reference
