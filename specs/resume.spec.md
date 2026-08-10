# Career Document Publishing System — Specification

<!-- SPDX-FileCopyrightText: 2026 Alan Szmyt -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

## Overview

This repository implements a specification-driven, LaTeX-based publishing system
that generates résumés and CVs from **shared canonical career content**.

The architecture separates five distinct concepts so documents can be varied
without duplicating career facts:

1. **Content/evidence** — canonical facts in `sections/*.tex`
2. **Document type** — résumé vs CV (`documents/*.yaml`)
3. **Profile** — role-family emphasis (`profiles/*.yaml`)
4. **Target** — optional application-specific overlay (`targets/*.yaml`)
5. **Template/theme** — LaTeX presentation (`templates/`, `*.sty`)

---

## Repository Structure

```
resume/
├── documents/              # Document type manifests
│   ├── resume.yaml
│   └── cv.yaml
├── profiles/               # Role-family profiles
│   ├── ai-infra.yaml
│   ├── platform.yaml
│   ├── research.yaml
│   └── general.yaml
├── targets/                # Application-specific overlays (optional)
│   └── example.yaml
├── sections/               # Canonical LaTeX content (shared)
│   ├── header.tex
│   ├── summary.tex
│   ├── experience.tex
│   ├── publications.tex
│   ├── education.tex
│   ├── skills.tex
│   ├── projects.tex        # CV extension point (stub)
│   ├── talks.tex           # CV extension point (stub)
│   ├── awards.tex          # CV extension point (stub)
│   └── service.tex         # CV extension point (stub)
├── templates/              # LaTeX document preamble templates
│   ├── resume/template.tex
│   └── cv/template.tex
├── resume.tex              # Canonical résumé entry point (backward-compat)
├── resume.sty              # Résumé style package
├── cv.sty                  # CV style package
├── scripts/
│   ├── build.py            # Build CLI and config resolution
│   └── quality_gates.py    # Validation and ATS extraction checks
├── tests/
│   └── test_config.py      # Configuration resolution tests
├── dist/                   # Generated PDF output (not committed)
├── outputs/                # Backward-compat copies (not committed)
└── specs/
    ├── resume.spec.md      # This specification
    └── governance.md       # Repository governance
```

---

## Configuration Resolution

Resolution merge order (later entries win):

```
document manifest defaults
  → profile
  → target overlay
  → CLI overrides
```

### Document manifest (`documents/*.yaml`)

Provides section pool, default template, default page size, and default section
ordering. The filename stem must match `document_type`.

```yaml
document_type: resume           # resume | cv
default_template: resume        # LaTeX style package name
default_page_size: letter       # letter | a4
section_pool:
  - header
  - summary
  - experience
  - publications
  - education
  - skills
default_section_order:
  - header
  - summary
  - experience
  - publications
  - education
  - skills
```

### Profile schema (`profiles/*.yaml`)

Defines role-family section ordering, included sections, and keyword emphasis.
The profile `id` must match the filename stem.

```yaml
profile: general                # must match filename
name: "General Software Engineering"
description: >
  Optional description of the target role family.

section_order:
  - header
  - summary
  - experience
  - publications
  - education
  - skills

included_sections:
  - header
  - summary
  - experience
  - publications
  - education
  - skills

keyword_emphasis:
  - software engineering
  - systems architecture
```

Validation rules:
- `profile` must match the filename stem.
- All sections in `section_order` and `included_sections` must be in the
  document's `section_pool`.
- Every `included_sections` entry must appear in `section_order`.
- No duplicates in `section_order`.
- `keyword_emphasis` must have at least one entry.

### Target overlay schema (`targets/*.yaml`)

Targets are **thin overlays** that express only what is application-specific.
They do not duplicate career content.

```yaml
target: example                 # must match filename
description: >
  Human-readable description of the target.

# All fields below are optional overrides:
document_type: resume           # override document type
profile: general                # override profile
page_size: letter               # override page size
section_order:                  # override section ordering
  - header
  - summary
  - skills
  - experience
  - education
  - publications
output_basename: alan-szmyt-resume-general-example   # override output filename
```

### Resolved `BuildConfig`

After merging all layers, a `BuildConfig` is produced:

| Field | Source |
|---|---|
| `document_type` | document manifest |
| `profile` | CLI `--profile` |
| `template` | document manifest `default_template` |
| `page_size` | CLI `--page-size` > target > document manifest default |
| `section_order` | target > profile > (implicit from included_sections) |
| `included_sections` | profile `included_sections` ∩ section_pool |
| `output_basename` | target `output_basename` or `alan-szmyt-{doc}-{profile}[-{target}]` |
| `target` | CLI `--target` (or None) |

---

## Section Architecture

Sections are standalone LaTeX files in `sections/`. They contain only content —
no layout logic beyond what primitives (`\resumeentry`, `\resumeskillgroup`)
provide.

### Résumé sections

| File | Purpose |
|---|---|
| `header.tex` | Name, contact, and profile links |
| `summary.tex` | Professional summary |
| `experience.tex` | Work history |
| `publications.tex` | Publications and papers |
| `education.tex` | Academic background |
| `skills.tex` | Technical skills |

### CV extension points (empty stubs)

| File | Future purpose |
|---|---|
| `projects.tex` | Selected projects and open-source software |
| `talks.tex` | Talks and presentations |
| `awards.tex` | Awards and honors |
| `service.tex` | Professional service and open-source contributions |

Optional sections that are not in a profile's `included_sections` are silently
omitted. No empty headings are emitted.

---

## Template Architecture

Each document type has a preamble template in `templates/<type>/template.tex`.

The build system reads the template, substitutes placeholders, then appends
`\begin{document}`, the selected section `\input` commands, and `\end{document}`.

### Placeholders

| Placeholder | Substituted value |
|---|---|
| `{{PAGE_CLASS}}` | `letterpaper` or `a4paper` |
| `{{DOCUMENT_TITLE}}` | `Alan Szmyt Resume` or `Alan Szmyt Cv` |
| `{{DOCUMENT_SUBJECT}}` | Descriptive subtitle |
| `{{PDF_KEYWORDS}}` | Keyword metadata string |

### Style packages

| File | Purpose |
|---|---|
| `resume.sty` | Résumé: compact geometry, fancyhdr, shared primitives |
| `cv.sty` | CV: generous multi-page margins, page numbers, shared primitives |

Shared primitives in both styles:
- `\resumeentry{title}{org}{location}{dates}` — work or education entry
- `\resumeskillgroup{category}{skills}` — skill category line

CV-only primitives:
- `\cvpublication{title}{venue}{year}{doi-url}` — publication entry
- `\cvevent{title}{org}{location}{date-range}` — CV event entry

---

## Build Process

```
documents/*.yaml + profiles/*.yaml [+ targets/*.yaml]
    ↓  scripts/build.py → resolve_config()
BuildConfig
    ↓  render_document()
    ↓  templates/<type>/template.tex + sections/*.tex
generated .tex file (ephemeral)
    ↓  latexmk (via .latexmkrc)
.cache/out/<basename>.pdf
    ↓  scripts/build.py
dist/<doc>/<profile>/alan-szmyt-<doc>-<profile>.pdf
outputs/<basename>.pdf  (backward-compat copy)
```

### Output naming

```
dist/<document_type>/<profile>/<basename>.pdf
dist/<document_type>/<profile>/<target>/<basename>.pdf
```

Examples:
```
dist/resume/general/alan-szmyt-resume-general.pdf
dist/cv/research/alan-szmyt-cv-research.pdf
dist/resume/general/example/alan-szmyt-resume-general-example.pdf
```

---

## Quality Validation

| Command | Purpose |
|---|---|
| `validate-documents` | Validate `documents/*.yaml` manifests |
| `validate-profiles` | Validate `profiles/*.yaml` definitions |
| `check-placeholders` | Scan for TODO/FIXME/placeholder content |
| `validate-ats` | Extract text from PDF and check headings |

ATS validation requirements:
- Extracted text is non-empty and exceeds 200 characters.
- Required headings (`Summary`, `Experience`, `Education`, `Skills`) are present.
- Text is extractable (no content rendered solely as images).

---

## ATS and machine-readability requirements

Both résumé and CV outputs must remain machine-readable:

- No important content rendered solely as images.
- No text converted to outlines.
- Single-column layout for résumé (ATS-conservative default).
- Hyperlinks retain readable labels.
- Logical reading order matches visual order.

---

## Backward compatibility

The previous invocation `python scripts/build.py --profile <name>` continues to
work. It defaults to `--document resume`.

Output directory changed from `outputs/resume-<profile>.pdf` to
`dist/resume/<profile>/alan-szmyt-resume-<profile>.pdf`.
A backward-compatible copy is written to `outputs/` for tooling that still
reads that path.

---

## Follow-up work (not in this release)

The architecture supports the following future extensions without restructuring:

- Populate CV extension-point sections (projects, talks, awards, service).
- Add a `research-software` profile.
- Add a UFZ RSE application target overlay (page size A4, tailored section emphasis).
- Add evidence-maturity metadata to career claims.
- Add a cover-letter document type.
