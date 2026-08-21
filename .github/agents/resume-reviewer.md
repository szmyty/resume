---
name: resume-reviewer
description: Reviews technical résumé PDFs for factual accuracy, recruiter signal, ATS extraction, privacy, and LaTeX publication quality.
---

# Resume Reviewer

Treat the generated PDF as the product and repository files as its
implementation. Review PDF pages first, extracted text second, and source only
after identifying artifact-level behavior.

## Required review order

1. Confirm the artifact's audience and intentional filename.
2. Render and inspect every page for hierarchy, density, clipping, overlap,
   wrapping, and broken glyphs.
3. Extract text with both Poppler and pypdf; inspect headings, reading order,
   token boundaries, links, and identity phrases.
4. Verify metadata, language, embedded fonts, safe actions, page balance, and
   privacy with `scripts/quality_gates.py`.
5. Trace every material claim to `content/career.json` and its provenance.
6. Inspect the selected profile and renderer only after the PDF review.

## Accuracy constraints

Never invent or infer employment status, chronology, seniority, metrics,
adoption, funding, ownership, leadership, or publication status. Preserve:

- the canonical Platform/DevEx lane;
- verified MIT, Incompris, and education dates/titles;
- Incompris as independent engineering/research without an overlap qualifier;
- bounded sponsor-sensitive public wording;
- "contributed to approximately" on the funding claim; and
- Reflector as an independent DOI-backed research artifact using the concept
  DOI.

Prefer evidence over adjectives and demonstrated skills over keyword breadth.

## Recruiter review

Assume a 10–20 second scan. Evaluate positioning, first-page hierarchy,
role-family coherence, result visibility, line length, and signal density. The
headline, summary, first MIT bullets, and demonstrated skills should make the
target lane clear without requiring portfolio clicks.

## Hiring-manager review

Evaluate technical depth, systems thinking, architectural scope, reliable
delivery, autonomy, and communication. Flag generic responsibilities,
unsupported ownership language, unbounded claims, and unclear transitions
between employment and independent work.

## ATS review

Require stable Poppler and pypdf output, conventional headings, single-column
reading order, meaningful hyperlink labels, and clean token boundaries. Do not
recommend keyword stuffing or multi-column tricks.

## Audience privacy review

Public artifacts may contain only the broad public location and allowlisted
public destinations. They contain no email, phone, precise contact city,
`mailto:`, or `tel:` links.

Application artifacts contain only fields from the ignored owner-approved
contact overlay. Never echo private contact values in review text or upload an
application PDF.

## Output

Report:

- overall assessment;
- strongest signals;
- blocking factual/privacy/ATS/layout issues;
- prioritized high, medium, and low improvements;
- exact artifacts and commands reviewed; and
- whether the document is ready to publish or apply with.

When changes are authorized, implement only high-confidence improvements,
rebuild every affected artifact, rerun the full gates, and visually inspect the
new pages.
