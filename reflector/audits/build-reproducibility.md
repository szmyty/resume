# Build Reproducibility Validation Report

Generated at: `2026-05-28T00:51:22Z`

## Executive Summary

- Total checks: **27**
- Pass: **26**
- Warn: **1**
- Fail: **0**

Overall result: ⚠️ **Conditionally deterministic** (non-failing issues remain)

## Goal Checklist

- [x] Build configuration declares deterministic controls
- [x] Build script uses deterministic invocation flags
- [x] Bibliography compilation is deterministic
- [ ] Builds are timestamp-independent
- [x] Build artifacts are isolated from version control
- [x] CI/CD pipeline is reproducible
- [x] Publication manifests are stable

## Detailed Checks

### Bibliography determinism

| Check | Result | Details |
| --- | --- | --- |
| biber uses fixed --input-directory | ✅ PASS | biber is configured with --input-directory=.cache/aux for fixed input. |
| biber uses fixed --output-directory | ✅ PASS | biber is configured with --output-directory=.cache/aux for fixed output. |
| Bibliography sorting mode is deterministic | ✅ PASS | biblatex sorting='nyt' is deterministic. |

### Build configuration

| Check | Result | Details |
| --- | --- | --- |
| max_repeat is declared | ✅ PASS | .latexmkrc declares $max_repeat = 10 to cap rebuild iterations. |
| force_mode is enabled | ✅ PASS | .latexmkrc enables $force_mode = 1 for deterministic rebuild. |
| Output directory is fixed | ✅ PASS | .latexmkrc fixes $out_dir to .cache/out. |
| Aux directory is fixed | ✅ PASS | .latexmkrc fixes $aux_dir to .cache/aux. |
| do_cd is enabled | ✅ PASS | .latexmkrc enables $do_cd = 1 for stable relative path resolution. |
| PDF mode is declared | ✅ PASS | .latexmkrc declares $pdf_mode = 1 for pdflatex output. |
| TEXINPUTS paths are explicit | ✅ PASS | .latexmkrc declares explicit TEXINPUTS search paths. |
| TEXMFOUTPUT is fixed | ✅ PASS | .latexmkrc fixes TEXMFOUTPUT to the aux directory. |
| emulate_aux is enabled | ✅ PASS | .latexmkrc enables $emulate_aux = 1 for aux directory emulation. |

### Build script

| Check | Result | Details |
| --- | --- | --- |
| Build script invokes repository .latexmkrc | ✅ PASS | scripts/build-paper.sh invokes the root .latexmkrc via -r flag. |
| Build script uses -gg for full rebuild | ✅ PASS | scripts/build-paper.sh uses -gg to force a full, clean rebuild. |
| Build script uses -halt-on-error | ✅ PASS | scripts/build-paper.sh uses -halt-on-error for clean failure detection. |
| Build script uses -interaction=nonstopmode | ✅ PASS | scripts/build-paper.sh uses -interaction=nonstopmode for non-interactive reproducible runs. |
| Build script enables -recorder | ✅ PASS | scripts/build-paper.sh enables -recorder for dependency tracking. |
| Build uses set -euo pipefail | ✅ PASS | scripts/build-paper.sh uses set -euo pipefail for strict error handling. |

### CI/CD reproducibility

| Check | Result | Details |
| --- | --- | --- |
| CI workflow provides TeXLive toolchain | ✅ PASS | CI build workflow provides a TeXLive toolchain (via latex-action or explicit install). |
| CI invokes build-paper.sh | ✅ PASS | CI build workflow invokes scripts/build-paper.sh. |
| CI installs latexmk | ✅ PASS | CI build workflow installs latexmk. |

### Manifest stability

| Check | Result | Details |
| --- | --- | --- |
| publication.json has required keys | ✅ PASS | publication.json includes required project, status, and version keys. |
| release-manifest.json exists | ✅ PASS | release-manifest.json exists. |

### Output stability

| Check | Result | Details |
| --- | --- | --- |
| .cache/ is git-ignored | ✅ PASS | .cache/ build artifacts are excluded from version control. |
| Generated PDFs are git-ignored | ✅ PASS | Generated PDF files are excluded from version control (via .cache/ exclusion). |

### Timestamp independence

| Check | Result | Details |
| --- | --- | --- |
| Paper date does not use \today | ⚠️ WARN | Paper date uses \today in macros/metadata.tex — this introduces build timestamp drift. Consider replacing \today with a fixed date string for reproducible artifacts. |
| Section files do not use dynamic date commands | ✅ PASS | No section files use \today or \DTMnow. |

## Unresolved Issues

- ⚠️ **Timestamp independence / Paper date does not use \today**: Paper date uses \today in macros/metadata.tex — this introduces build timestamp drift. Consider replacing \today with a fixed date string for reproducible artifacts.

## Recommended Fixes

- Replace `\today` in `macros/metadata.tex` with a fixed date string (e.g., `\newcommand{\paperdate}{2025-01-01}`) to eliminate timestamp drift between builds.

## Determinism Confidence Assessment

**Confidence level: Medium**

The build infrastructure declares deterministic controls across:
- latexmk iteration capping (`$max_repeat`)
- Fixed output and auxiliary directories
- Explicit TEXINPUTS path ordering
- Isolated biber bibliography processing
- CI/CD toolchain pinning

Non-failing warnings remain (see Unresolved Issues). Addressing these would increase determinism confidence to High.
