# Copilot Instructions — szmyty/resume

<!-- SPDX-FileCopyrightText: 2026 Alan Szmyt -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

## Repository purpose

This repository is a specification-driven LaTeX publishing system that generates
**résumés and CVs** for Alan Szmyt from shared canonical career content.

It produces deterministic, ATS-safe, text-extractable PDF documents in multiple
variants (document type × profile × optional target × page size) without
duplicating source content.

---

## Source-of-truth rules

**Never invent, fabricate, or silently rewrite career facts.**

- Do not add employment history, dates, or metrics that cannot be verified from
  existing repository content.
- Do not add skills, tools, or projects that are not already present in the
  canonical section files.
- Do not change employment dates, education dates, or degree information.
- Do not rewrite existing bullet points unless the task explicitly authorizes it
  and the content remains factually accurate.
- Content changes (sections/*.tex, profiles/*.yaml) and rendering-system changes
  (scripts/, templates/, documents/, .sty files) must remain separable. Never
  combine them in the same commit without a clear justification.

---

## Architecture

Five concepts are explicitly separated:

| Concept | Location | Purpose |
|---|---|---|
| Content/evidence | `sections/*.tex` | Canonical career facts (shared by all variants) |
| Document type | `documents/*.yaml` | résumé vs CV; section pool; template |
| Profile | `profiles/*.yaml` | Role-family emphasis; section ordering |
| Target | `targets/*.yaml` | Optional application-specific overlay |
| Template/theme | `templates/`, `*.sty` | LaTeX presentation/layout |

Resolution merge order:
```
document manifest defaults → profile → target overlay → CLI overrides
```

---

## Build and test commands

```bash
# List available documents, profiles, and targets
python scripts/build.py --list

# Build a résumé
python scripts/build.py --document resume --profile general

# Build a CV
python scripts/build.py --document cv --profile research

# Build with A4 page size
python scripts/build.py --document cv --profile research --page-size a4

# Build with a target overlay
python scripts/build.py --document resume --profile general --target example

# Backward-compatible (defaults to --document resume)
python scripts/build.py --profile general

# Quality gates
python scripts/quality_gates.py validate-documents
python scripts/quality_gates.py validate-profiles
python scripts/quality_gates.py check-placeholders
python scripts/quality_gates.py validate-ats --pdf dist/resume/general/alan-szmyt-resume-general.pdf

# Tests (no LaTeX required)
python -m pytest tests/ -v
```

---

## Output layout

```
dist/
  resume/
    general/
      alan-szmyt-resume-general.pdf
    research/
      alan-szmyt-resume-research.pdf
  cv/
    research/
      alan-szmyt-cv-research.pdf
    research/
      example/
        alan-szmyt-cv-research-example.pdf
```

Generated PDFs are not committed to the repository (covered by `.gitignore`).

---

## Generated-file policy

- `*.generated.tex` — ephemeral build inputs, not committed.
- `dist/**/*.pdf` — generated build outputs, not committed.
- `outputs/**/*.pdf` — backward-compatible copies, not committed.
- `.cache/` — LaTeX auxiliary files, not committed.
- Source files (`sections/`, `profiles/`, `documents/`, `targets/`, `templates/`,
  `*.sty`, `*.tex` at root) are the authoritative inputs and are committed.

---

## How to extend the system

### Add a new profile
1. Create `profiles/<name>.yaml` following the existing profile schema.
2. Run `python scripts/quality_gates.py validate-profiles`.
3. Build: `python scripts/build.py --document resume --profile <name>`.

### Add a new application target
1. Create `targets/<name>.yaml` with optional overrides.
2. Build: `python scripts/build.py --document resume --profile general --target <name>`.

### Add an optional CV section
1. Create `sections/<name>.tex` with the section content (or as an empty stub).
2. Add the section name to `documents/cv.yaml` → `section_pool`.
3. Add it to the desired profile's `section_order` and `included_sections`.

### Add/modify a template
1. Edit or create `templates/<document_type>/template.tex` and the corresponding
   `<name>.sty` file.
2. Update `documents/<type>.yaml` → `default_template` if introducing a new style.
3. Content files must not be modified as part of a template change.

### Build letter vs A4
```bash
python scripts/build.py --document resume --profile general --page-size letter
python scripts/build.py --document resume --profile general --page-size a4
```
