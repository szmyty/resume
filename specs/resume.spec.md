# Career Document Publishing Specification

<!-- SPDX-FileCopyrightText: 2026 Alan Szmyt -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

## 1. Product contract

The system generates deterministic, ATS-readable PDFs from one validated career
ledger. It must support:

- a canonical two-page Platform/DevEx résumé;
- Platform/DevEx, research/AI-assisted-systems, and mobile/geospatial role
  variants;
- a permanently public sanitized projection;
- application projections containing only owner-approved contact fields; and
- résumé and CV templates without duplicating career claims.

The generated PDF is the product. YAML, JSON, Python, and LaTeX are its
implementation.

## 2. Source layers

### 2.1 Canonical fact ledger

`content/career.json` owns:

- public identity and recruiter destinations;
- public/application privacy policies;
- role chronology and classification;
- audience-specific claim text;
- metric qualifiers;
- research-artifact status and concept DOI;
- education chronology;
- evidenced skill groups; and
- provenance for every role, claim, artifact, and education record.

Every provenance object contains `source`, `status`, and `reviewed_on`. Only
`status: verified` records may render.

Claim identifiers are immutable references. A claim contains:

```json
{
  "subject": "role-id",
  "application_text": "Owner-approved application wording.",
  "public_text": "Sanitized public wording.",
  "profiles": ["platform"],
  "sensitivity": "public-bounded",
  "provenance": {
    "source": "source-id",
    "status": "verified",
    "reviewed_on": "YYYY-MM-DD"
  }
}
```

Quantified claims may define required qualifiers. Every projection must retain
all qualifiers.

### 2.2 Role profiles

`profiles/*.yaml` select and order canonical content. Required fields:

```yaml
profile: platform
name: "Platform and Developer Experience"
description: >
  Human-readable lane description.
output_label: "Platform-DevEx"
headline: "Role-specific headline"
summary: >
  Role-specific summary grounded in canonical claims.
section_order:
  - header
  - summary
  - experience
  - independent
  - skills
  - publications
  - education
included_sections:
  - header
  - summary
  - experience
  - independent
  - skills
  - publications
  - education
claim_ids:
  - verified-claim-id
skill_group_ids:
  - evidenced-skill-group-id
keyword_emphasis:
  - platform engineering
```

Rules:

- the profile ID matches the filename stem;
- claim IDs exist and explicitly allow the role lane;
- every skill group has evidence among the selected claims;
- included sections appear exactly once in the section order; and
- role headlines must not upgrade verified seniority.

The required profile set is `general`, `platform`, `research`, and
`mobile-geospatial`. `general` is the canonical Platform/DevEx baseline.

### 2.3 Document manifests

`documents/*.yaml` define `resume` and `cv` template, default page size, section
pool, and default section order. Résumé sections are:

```text
header, summary, experience, independent, publications, education, skills
```

The CV may additionally use `projects`, `talks`, `awards`, and `service`. These
extension sections live in `sections/*.tex`; canonical career sections are
rendered from the JSON ledger and never duplicated as LaTeX source.

### 2.4 Target overlays

`targets/*.yaml` are optional thin overlays. They may constrain document type or
profile and override page size, section order, or output basename. A declared
document/profile mismatch fails; it is never silently ignored.

### 2.5 Audience overlay

`--audience public` is the default and renders:

- `identity.public_location`;
- allowlisted HTTPS profile links; and
- every claim's `public_text`.

The canonical `identity.public_location` value, `Greater Boston, MA`, is an
owner-approved permanent-public regional label. It is intentionally distinct
from the optional application-overlay `location` field.

It renders no email, phone, precise contact city, `mailto:` link, or `tel:`
link.

`--audience application` requires `--contact-file`. The ignored JSON overlay may
contain only `email`, `phone`, and `location`, and it must contain an email or a
phone number. It renders every selected claim's `application_text`.

## 3. Configuration resolution

```text
document manifest defaults
  → profile
  → optional target overlay
  → explicit CLI page-size override
  → audience/contact projection
```

The resolved `BuildConfig` contains document type, profile, template, page size,
section order, selected claims and skills, role copy, audience, approved contact
data, and output basename.

## 4. Rendering

`scripts/build.py`:

1. validates all source inputs;
2. resolves the configuration;
3. selects public or application claim projections;
4. escapes text for LaTeX;
5. generates an ephemeral `<basename>.generated.tex`;
6. runs `latexmk`;
7. reads `.cache/out/<basename>.generated.pdf`; and
8. publishes to `dist/` plus the compatibility `outputs/` copy.

The `.generated` suffix in step 7 is part of the build contract. Dropping it
causes successful TeX compilation to fail at artifact publication and is covered
by a regression test.

## 5. Artifact paths and names

```text
dist/<document>/<profile>/<audience>/[<target>/]<filename>.pdf
```

Required résumé names:

```text
Alan-Szmyt-Resume.pdf
Alan-Szmyt-Resume-Platform-DevEx.pdf
Alan-Szmyt-Resume-Research-AI-Systems.pdf
Alan-Szmyt-Resume-Mobile-Geospatial.pdf
```

Non-baseline public role files add `-Public`. Application names never contain
`-Public`. `CV` remains uppercase in CV filenames.

## 6. PDF and ATS contract

Every published résumé must pass both Poppler and pypdf extraction. Gates check:

- non-empty text and minimum extraction length;
- `Summary`, `Experience`, `Education`, and `Skills` headings;
- canonical identity phrases;
- known token-join regressions and reading-order defects;
- exactly two pages;
- at least 30% of words on each page, preventing near-empty spill pages while
  permitting a section-aligned second page;
- at least 58% vertical text occupancy on each page;
- intentional title, subject, author, keywords, creator, and `en-US` language;
- embedded fonts and safe catalog actions;
- allowlisted recruiter links;
- intentional filename; and
- audience privacy invariants.

Public destinations are validated deterministically locally and for network
reachability in CI. HTTP authentication/authorization responses are tolerated;
broken destinations are not.

## 7. CI contract

CI validates facts, profiles, manifests, destinations, privacy, and unit tests.
It builds four public résumé projections and four application role projections.
Application builds use synthetic CI-only contact data and are never uploaded.

CI uploads:

- public résumé PDFs;
- the fully validated public research CV; and
- two Poppler-rendered PNG pages for each public résumé.

The artifact inventory records page count and SHA-256.

## 8. Non-negotiable facts

Quality gates lock the canonical lane, identity location class, verified
employment dates and titles, education dates, Incompris independent-work
classification, bounded funding wording, Reflector's independent-artifact
status, and its version-independent concept DOI.

Incompris overlap must not acquire a part-time, full-time, consulting, or similar
employment-status qualifier without explicit owner verification.
