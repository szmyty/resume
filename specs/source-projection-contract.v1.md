# Reviewed source to public projection contract (v1)

Status: proposed documentation for [roadmap #25](https://github.com/szmyty/resume/issues/25), checkpoint 1. This contract describes the review boundary around the existing `content/career.json` schema version 1. It does not migrate a fact, approve wording, or change a renderer.

## Ownership

| Layer | Authority and permitted content |
| --- | --- |
| Private career record | Source evidence, contribution attribution, chronology decisions, sensitivity, review history, and the owner-only comprehensive master. The private record decides whether a proposed claim is supportable; a catalog entry or repository URL alone is not approval. |
| This public repository's `content/career.json` | The self-contained, deliberately limited rendering projection. It contains only approved public-safe fields and separately approved public/application wording. Existing entries remain the historical baseline pending reconciliation, not newly approved claims under this contract. |
| `profiles/*.yaml` | Selection and ordering by stable claim and skill-group ID, plus reviewed headline/summary copy. Profiles do not become a second fact store. |
| `documents/*.yaml`, `targets/*.yaml`, templates | Presentation and configuration. A target may not introduce a fact or rewrite a claim to match a posting. |
| Ignored application contact overlay | Owner-approved email, phone, and/or location for a specific local application build. It never enters Git, CI artifacts, Pages, or a public PR. |
| Generated PDFs and Pages | Outputs from the validated public projection. The owner-only master and application PDFs are not public build artifacts. |

The public build, its tests, and Pages deployment must continue to work solely from committed public inputs. There is no automatic export, private fetch, or authenticated CI dependency.

## Review-to-projection transaction

1. In the private workflow, review the exact source and the applicant's contribution. Record conflicts, confidence, dates, and sensitivity there. GitHub activity can corroborate work and timing, but does not by itself prove authorship, production adoption, or business outcomes.
2. Resolve attribution, chronology, title, metrics, project affiliation, and skill depth with the owner. Preserve an explicit rejected/deferred decision as well as approved decisions. Do not equate the public ledger's historical `provenance.status: verified` with a new owner approval.
3. Prepare a claim-ID crosswalk privately. Preserve a public ID when its subject and meaning remain the same; give a genuinely new claim a new ID. Do not silently reuse an ID for materially different wording. Crosswalk evidence pointers remain private.
4. Obtain owner approval for the exact `application_text` and `public_text` projections and their audiences. Check sponsor sensitivity, required qualifiers, publication status, and recruiter links. An application-only claim still needs a public-safe projection if the current schema requires both; otherwise defer it until an explicitly reviewed schema change.
5. Open a separate public content PR containing only the approved projection, a safe provenance summary, and selected IDs. The PR lists affected IDs and the owner approval record without copying private source files, URLs, notes, or contact values. Inspect its complete diff.
6. Validate facts, documents, profiles, privacy, tests, public/application renders, extracted PDF text, links, and every affected page. Review the actual artifact with the owner before replacing the public baseline or publishing to Pages.

No step may turn an unapproved candidate master into public content by bulk copy. A release is a separate decision from source cataloging, rendering, or preparing a packet.

## Version and compatibility

- The current public ledger declares `schema_version: 1`. The existing validators, profile IDs, and renderer continue to consume that shape without a migration in this checkpoint.
- This document is **contract v1** for moving reviewed decisions into that projection. Its version is separate from the JSON schema number.
- A future schema revision must name its new fields and allowed states, validate old/new inputs during migration or provide a deliberate conversion, preserve stable IDs and metric qualifiers, and fail closed on unapproved claims. Change renderer, tests, and release gates in the same reviewed PR series before importing new data.
- If a proposed fact cannot be represented safely by the current public schema, keep it private. Do not add a free-form field or a LaTeX extension as a bypass.

## Publication boundary

The two-page public baseline remains the current artifact until an exact content and visual review is approved. The private comprehensive master should be generated in an owner-controlled private workflow; its evidence, local contact data, and resulting PDFs must stay outside this public repository and public CI. A later tailored packet records selected claim IDs privately and does not change canonical facts to suit a vacancy.
