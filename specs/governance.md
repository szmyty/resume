# Career Document Governance

<!-- SPDX-FileCopyrightText: 2026 Alan Szmyt -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

## Source of truth

`content/career.json` is the only canonical source for identity, chronology,
claims, research artifacts, education, demonstrated skills, provenance, and
audience privacy rules. Profiles select fact IDs; they never copy or rewrite
facts. LaTeX files control presentation only, except for optional CV extension
sections.

Do not invent or infer:

- employment status for overlapping work;
- seniority beyond a verified title;
- ownership, adoption, leadership, funding, or performance metrics;
- sponsor-sensitive context in the public projection; or
- peer review or publication status for an independent research artifact.

## Fact change workflow

1. Identify an owner-approved source.
2. Add or update the canonical record and its provenance.
3. Provide public/application text separately when sensitivity differs.
4. Preserve required metric qualifiers in both projections.
5. Select the fact by ID from the relevant profile.
6. Run `validate-facts`, `validate-profiles`, and unit tests.
7. Build and inspect every affected audience/profile artifact.

Owner verification is required before changing any locked date, title,
classification, metric, contact policy, or artifact status.

## Privacy policy

Public artifacts may contain only the broad public location and allowlisted
public links. They must not contain personal email, phone, precise contact city,
application-state notes, `mailto:` URIs, or `tel:` URIs.

`Greater Boston, MA` is explicitly approved for the permanent-public projection
as broad regional context. It is not sourced from an application overlay and
must remain public unless the owner approves a canonical policy change.

Application contact data must live in an ignored local JSON file. Supported
fields are exactly `email`, `phone`, and `location`. Unknown fields fail closed.
Never commit, log, upload, or place application contact data in CI artifacts.

The committed example and CI fixture use non-production values only.

## Role profile workflow

1. Keep a profile within one named role family.
2. Select only claims approved for that family.
3. Select only skill groups evidenced by selected claims.
4. Keep the headline and summary consistent with verified seniority.
5. Validate profiles and build both public and application projections.
6. Inspect page hierarchy, wrapping, density, and reading order.

The canonical lane is Platform/DevEx. Research/AI-assisted systems and
mobile/geospatial are role variants, not separate fact sources.

## Publication checklist

Before a résumé artifact is considered ready:

```bash
python scripts/quality_gates.py validate-facts
python scripts/quality_gates.py validate-documents
python scripts/quality_gates.py validate-profiles
python scripts/quality_gates.py check-placeholders
python scripts/quality_gates.py validate-destinations --audience public
python -m pytest tests/ -v
```

Then build the artifact and run `validate-ats` plus `validate-pdf` with the
matching audience and, for application artifacts, the same contact overlay used
to build it.

Finally render both pages to images and inspect:

- clipping, overlap, missing or broken glyphs;
- hierarchy and scanability;
- balanced page density;
- line wrapping and bullet rhythm; and
- public/application contact projection.

The PDF is the release artifact. Passing source tests does not replace visual
inspection.

## Artifact policy

Generated PDFs, PNG renders, caches, and contact overlays are not committed.
Artifacts use intentional recruiter-facing names and live under:

```text
dist/<document>/<profile>/<audience>/[<target>/]
```

CI uploads only public PDFs and public visual renders for 30 days. Application
variants are validation-only and remain runner-local. The CI summary records
page counts and SHA-256 hashes.

Repository history and the canonical ledger's provenance fields provide source
traceability. Audit logs in `audits/` remain timestamped and tracked.

## Pull request expectations

A career-content PR documents its source and affected claim IDs. A rendering or
quality-gate PR lists affected artifact paths and validation commands. A
cohesive application-readiness PR may combine both when its body explicitly
separates:

- canonical fact/content changes;
- renderer/layout changes;
- build regressions; and
- validation/CI changes.

Do not publish a PR that exposes a local contact overlay or generated
application artifact.
