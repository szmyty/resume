# Copilot Instructions — szmyty/resume

<!-- SPDX-FileCopyrightText: 2026 Alan Szmyt -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

## Purpose

This repository publishes ATS-readable résumés and CVs from its validated,
self-contained rendering ledger. The private career repository is the source
authority for career facts and evidence as they are reviewed. The PDF is the
product; public and application artifacts are different privacy projections
of selected facts.

## Non-negotiable source rules

- The private career repository is the authority for reviewed source facts
  and evidence. A cataloged source or repository is not an approved claim.
  `content/career.json` is this public repository's reviewed, self-contained
  rendering projection, not a second independent source of career truth.
- The existing public ledger is the starting publication baseline; this
  documentation update does not newly verify or approve its claims. New or
  changed facts require source review and owner approval before projection.
- The renderer and CI must never fetch private evidence or depend on private
  repository access. Keep private paths, URLs, notes, and source documents out
  of this public repository.
- No automatic fact export or source migration exists; update the public ledger
  only through an explicitly reviewed, owner-approved content change.
- Never invent or infer chronology, seniority, employment status, metrics,
  funding, adoption, ownership, or research status.
- Incompris remains independent engineering/research with no unverified
  overlap qualifier.
- Keep metric qualifiers, especially "contributed to" and "approximately".
- Reflector remains an independent DOI-backed research artifact using the
  concept DOI.
- Every role, claim, artifact, education item, and demonstrated skill needs
  verified provenance/evidence.
- Profiles reference claim and skill-group IDs; they do not duplicate facts.

## Privacy rules

- Public artifacts contain only the broad public location and allowlisted HTTPS
  recruiter links.
- Public artifacts contain no email, phone, precise contact city, `mailto:`
  link, or `tel:` link.
- Application contact data comes only from an ignored owner-approved JSON
  overlay containing `email`, `phone`, and/or `location`.
- Never commit or upload a completed contact overlay or application PDF.

## Architecture

| Layer | Location |
| --- | --- |
| Reviewed source facts and evidence | Private career repository (external to this public build) |
| Validated rendering projection/privacy | `content/career.json` |
| Audience contact example | `content/application-contact.example.json` |
| Role selection and copy | `profiles/*.yaml` |
| Résumé/CV manifests | `documents/*.yaml` |
| Optional target overlays | `targets/*.yaml` |
| Rendering | `scripts/build.py`, `templates/`, `*.sty` |
| Validation | `scripts/career.py`, `scripts/quality_gates.py`, `tests/` |
| Optional CV extension content | `sections/*.tex` |

Resolution order:

```text
document → profile → target → CLI override → audience/contact projection
```

## Commands

```bash
python scripts/build.py --list

python scripts/build.py \
  --document resume \
  --profile general \
  --audience public

python scripts/build.py \
  --document resume \
  --profile research \
  --audience application \
  --contact-file .local/application-contact.json

python scripts/quality_gates.py validate-facts
python scripts/quality_gates.py validate-documents
python scripts/quality_gates.py validate-profiles
python scripts/quality_gates.py check-placeholders
python scripts/quality_gates.py validate-destinations --audience public
python -m pytest tests/ -v

python scripts/quality_gates.py validate-ats \
  --pdf dist/resume/general/public/Alan-Szmyt-Resume.pdf \
  --audience public
python scripts/quality_gates.py validate-pdf \
  --pdf dist/resume/general/public/Alan-Szmyt-Resume.pdf \
  --audience public
```

## Change policy

For content changes, review the upstream source and obtain owner approval for
the exact audience projection. Record public-safe provenance in
`content/career.json`; never copy private evidence into this repository. For
profile changes, prove every selected skill through a selected claim. For
rendering changes, rebuild and visually inspect every affected two-page PDF.
For privacy changes, add negative and positive tests.

The latexmk artifact path includes `.generated.pdf`; keep the regression test
that protects this suffix.

Use intentional title-cased filenames. `CV` is uppercase, application filenames
omit `-Public`, and the permanent baseline is `Alan-Szmyt-Resume.pdf`.

Generated PDFs, rendered images, caches, and `.local/` data are not committed.

## Continuity handoff

Read the root `AGENTS.md`, applicable specs, and `CONTINUITY.md` after these
instructions. Verify the checkpoint's branch, issue, pull-request, and release
claims against live state; the checkpoint is a compact handoff, not a source
of facts or permission to publish. For an authorized repository change,
refresh it in the same pull request after validation and before presenting the
work.
