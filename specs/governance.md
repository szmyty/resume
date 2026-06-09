# Resume Repository Governance

<!-- SPDX-FileCopyrightText: 2026 Alan Szmyt -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

## Overview

This document defines repeatable repository governance for publication, auditing, profile evolution, and generated artifacts.

## Build Workflow

1. Run profile and content checks:
   - `python scripts/quality_gates.py validate-profiles`
   - `python scripts/quality_gates.py check-placeholders`
2. Build all profiles or a specific profile:
   - `python scripts/build.py`
   - `python scripts/build.py --profile <profile-id>`
3. For CI, `.github/workflows/build-resume.yml` validates profiles/content, builds the resume PDF, runs ATS extraction validation, and uploads an artifact.

## Audit Workflow

Store each repository audit in `audits/` using UTC timestamps:

- `audits/audit-YYYY-MM-DDTHHMMSSZ.log`
- Example: `audits/audit-2026-06-09T155821Z.log`

Minimum audit log structure:

1. Title line (audit name)
2. Timestamp line in UTC (`Timestamp: YYYY-MM-DDTHHMMSSZ`)
3. Repository and scope lines
4. Findings grouped by topic, with actionable recommendations
5. Final conclusion and priority order

## Profile Workflow

When introducing or modifying profile variants:

1. Update a profile definition in `profiles/*.yaml`.
2. Ensure section ordering and included sections remain valid for supported sections.
3. Run profile validation:
   - `python scripts/quality_gates.py validate-profiles`
4. Build and review the affected profile output:
   - `python scripts/build.py --profile <profile-id>`

## Artifact Generation Workflow

Local artifact flow:

1. `scripts/build.py` generates profile-specific LaTeX entry points.
2. `latexmk` compiles PDFs via `.latexmkrc`.
3. Final artifacts are copied to `outputs/resume-<profile>.pdf`.

CI artifact flow:

1. `.github/workflows/build-resume.yml` builds `resume.tex`.
2. The CI output is copied to `outputs/resume.pdf`.
3. Artifact `resume-pdf` is uploaded by GitHub Actions.

## Artifact Policy

### Naming conventions

- Local profile artifacts: `outputs/resume-<profile>.pdf`
- CI publication artifact path: `outputs/resume.pdf`
- CI artifact name: `resume-pdf`
- Audit artifacts: `audits/audit-YYYY-MM-DDTHHMMSSZ.log`

### Retention expectations

- GitHub Actions artifact retention is 30 days (`retention-days: 30` in workflow configuration).
- Audit logs in `audits/` are retained in git history for long-term traceability.

### Versioning approach

- Repository history (commit SHA) is the source of truth for content/version changes.
- Audit files are timestamp-versioned through their filename.
- Generated PDFs should be treated as build outputs tied to the commit and profile that produced them.
