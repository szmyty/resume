# Resume System Specification

<!-- SPDX-FileCopyrightText: 2026 Alan Szmyt -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

## Overview

This repository implements a specification-driven, LaTeX-based resume system. The architecture is designed to support iterative content development and profile-targeted resume variants generated from a shared section library.

---

## Repository Structure

```
resume/
├── resume.tex          # Main LaTeX entry point
├── resume.sty          # Resume style package
├── sections/           # Modular resume section files
│   ├── header.tex
│   ├── summary.tex
│   ├── experience.tex
│   ├── publications.tex
│   ├── education.tex
│   └── skills.tex
├── profiles/           # Profile variant definitions (YAML)
│   ├── ai-infra.yaml
│   ├── platform.yaml
│   ├── research.yaml
│   └── general.yaml
├── assets/             # Images, icons, and other static assets
├── outputs/            # Generated PDF artifacts
├── scripts/
│   └── build.py        # Build orchestration script
├── specs/
│   └── resume.spec.md  # This specification
└── .github/
    └── workflows/
        └── build-resume.yml
```

---

## Section Architecture

Each resume section is a standalone LaTeX file under `sections/`. Sections are included by `resume.tex` using `\input{sections/<name>}`.

| File | Purpose |
| --- | --- |
| `header.tex` | Contact information and name |
| `summary.tex` | Professional summary paragraph |
| `experience.tex` | Work history entries |
| `education.tex` | Academic background |
| `skills.tex` | Technical skills grouped by category |
| `publications.tex` | Publications, papers, or articles |

Sections can be conditionally included or reordered by generating a profile-targeted entry point from the YAML profile definitions at build time.

---

## Profile Architecture

Profile YAML files in `profiles/` define the intended audience, summary variant, section ordering, included sections, and keyword emphasis areas for a given resume variant.

### Profile Schema

```yaml
profile: <identifier>          # machine-readable profile ID
name: "<Human-Readable Label>"
description: >
  <Description of the target role family>

summary: >
  <Profile-specific summary variant>

section_order:                 # ordered list of sections to include
  - header
  - summary
  - experience
  - skills
  - education
  - publications               # optional

included_sections:             # sections enabled for the profile
  - header
  - summary
  - experience
  - skills
  - education
  - publications               # optional

keyword_emphasis:              # keywords to highlight in content
  - keyword one
  - keyword two
```

### Available Profiles

| Profile ID | Target Role Family |
| --- | --- |
| `ai-infra` | AI infrastructure and ML platform engineering |
| `platform` | Platform engineering, DevOps, and SRE |
| `research` | Research and academic positions |
| `general` | General software engineering |

---

## Style Package

`resume.sty` defines:

- Page geometry (compact margins for a single-page resume)
- Typography with `lmodern` and `microtype`
- Color palette (`resumeblue`, `resumegray`, etc.)
- Section heading formatting via `titlesec`
- List formatting via `enumitem`
- Reusable commands:
  - `\resumeentry{title}{org}{location}{dates}` — a single work or education entry
  - `\resumeskillgroup{category}{skills}` — a skill category line

---

## Build Process

```
profiles/*.yaml
    ↓  scripts/build.py
generated profile-specific .tex entry points
    ↓  latexmk (via .latexmkrc)
.cache/out/resume-<profile>.generated.pdf
    ↓  scripts/build.py
outputs/resume-<profile>.pdf
```

### latexmkrc Configuration

`.latexmkrc` sets:

- `$out_dir = ".cache/out"` — keeps build artifacts out of the source tree
- `$aux_dir = ".cache/aux"` — auxiliary files (`.aux`, `.log`, etc.)
- `$TEXINPUTS` — includes `sections/`, `styles/`, and `assets/` paths
- `$pdf_mode = 1` — pdflatex build

### Build Script

`scripts/build.py` wraps `latexmk` and:

1. Validates that `resume.tex`, `.latexmkrc`, and the selected profile definitions exist.
2. Loads profile metadata from `profiles/*.yaml`.
3. Generates a temporary profile-specific LaTeX entry point with ordered and filtered sections.
4. Runs `latexmk` with standard flags for each selected profile.
5. Copies the output PDF to `outputs/resume-<profile>.pdf`.
6. Optionally opens the generated PDF (`--open` flag).

### GitHub Actions

`.github/workflows/build-resume.yml` runs on every push or pull request that modifies resume source files:

1. Checks out the repository.
2. Runs `latexmk` via the `xu-cheng/latex-action` action.
3. Copies the PDF to `outputs/resume.pdf`.
4. Uploads the PDF as a build artifact (`resume-pdf`).
5. Posts a build summary with the artifact checksum.

---

## Artifact Generation Workflow

```
Push / PR to main
    ↓
GitHub Actions: build-resume.yml
    ↓
xu-cheng/latex-action (TeX Live)
    ↓
outputs/resume.pdf
    ↓
actions/upload-artifact → resume-pdf artifact
```

---

## Future Work

- Multi-profile CI matrix: build all profiles in parallel in the GitHub Actions workflow.
- Content population: fill in section files with actual resume content.
- Assets: add a headshot, icons, or other visual elements to `assets/`.
