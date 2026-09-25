# Career Document Governance

<!-- SPDX-FileCopyrightText: 2026 Alan Szmyt -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

## Source of truth

The private career repository is the authority for career facts and supporting
evidence as they are reviewed. Cataloged source files and repository metadata
alone do not establish an approved claim. `content/career.json` is the public
repository's self-contained rendering projection for identity, chronology,
claims, research artifacts, education, demonstrated skills, public-safe
provenance, and audience privacy rules. It remains the only factual input to
this renderer. Profiles
select fact IDs; they never copy or rewrite facts. LaTeX files control
presentation only, except for optional CV extension sections.

The existing published ledger remains the starting baseline. Reclassifying it
as a projection does not independently verify its existing sources or approve
new claims. No automatic source export exists. The private repo is consulted
during editorial review, never by public CI or runtime builds.

Do not invent or infer:

- employment status for overlapping work;
- seniority beyond a verified title;
- ownership, adoption, leadership, funding, or performance metrics;
- sponsor-sensitive context in the public projection; or
- peer review or publication status for an independent research artifact.

## Fact change workflow

1. Identify and review the source fact and evidence in the private career
   repository, including contribution, outcome, and sensitivity limits.
2. Obtain owner approval for each new or revised factual claim and its exact
   public/application wording. Prior publication alone is not independent
   verification of a newly proposed expansion.
3. Add or update only the approved projection in `content/career.json` with
   stable IDs and public-safe provenance. Never copy private evidence, private
   source URLs or paths, contact data, or application-state notes into public Git.
4. Preserve required metric qualifiers in both audience projections.
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

Repository history and the public rendering ledger's safe provenance fields
provide publication traceability. The private career repository retains the
underlying evidence and review history. Audit logs in `audits/` remain
timestamped and tracked.

## Pull request expectations

A career-content PR documents reviewed source identifiers that are safe to
disclose, owner approval, and affected claim IDs. A rendering or
quality-gate PR lists affected artifact paths and validation commands. A
cohesive application-readiness PR may combine both when its body explicitly
separates:

- reviewed public projection/content changes;
- renderer/layout changes;
- build regressions; and
- validation/CI changes.

Do not publish a PR that exposes a local contact overlay or generated
application artifact.
