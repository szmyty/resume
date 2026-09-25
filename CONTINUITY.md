---
schema_version: aether.repository-continuity/v1
repository:
  id: szmyty/resume
  visibility: public
  default_branch: main
  continuity_path: CONTINUITY.md
document:
  status: active
  updated_at: '2026-09-25T18:22:50Z'
  max_bytes: 16384
  max_lines: 240
  stale_reason: null
  superseded_by: null
scope:
  purpose: Hand off the public-safe fact authority contract and the next reviewed résumé publishing step.
  includes:
  - Private source authority versus self-contained public rendering projection.
  - The master/baseline roadmap issue and documentation review state.
  excludes:
  - Private source files, local contact overlays, application PDFs, and conversation history.
  - Full roadmap text and generated artifacts.
  precedence:
  - user-and-runtime-instructions
  - scoped-repository-instructions
  - live-repository-and-work-tracker-state
  - canonical-repository-sources
  - continuity-checkpoint
  canonical_sources:
  - AGENTS.md
  - .github/copilot-instructions.md
  - README.md
  - specs/resume.spec.md
  - specs/governance.md
  - content/career.json
  - https://github.com/szmyty/resume/issues/25
work:
  objective: Align public résumé instructions and specs with the private source-of-truth and public projection boundary.
  success_conditions:
  - Private career sources await fact review; existing public content/career.json remains a self-contained validated
    rendering projection.
  - AGENTS.md points to this checkpoint and the specs; new facts require owner review before projection.
  - No private evidence, contact overlay, claim migration, renderer change, or generated PDF is part of this documentation
    change.
  active_issue:
    provider: github
    id: szmyty/resume#25
    url: https://github.com/szmyty/resume/issues/25
  next:
    kind: action
    id: review-resume-governance-pr
    description: 'Review documentation changes in draft PR #26 alongside the private source contract. Start any
      claim migration only after owner review of the private facts.'
    readiness: ready
    references:
    - https://github.com/szmyty/resume/pull/26
    - https://github.com/szmyty/resume/issues/25
    depends_on: []
state:
  base:
    revision: 566648f77fb4263ed37cb7c07b886ad4f18c856a
    ref: refs/heads/main
    verified_at: '2026-09-25T18:12:10Z'
  candidate:
    branch: docs/career-continuity-2026-09-25
    revision: 068a5921f5321ddc368faa404c861dba2700f504
    pull_request:
      provider: github
      id: szmyty/resume#26
      url: https://github.com/szmyty/resume/pull/26
    handoff_state: ready-for-review
  live:
    status: verified
    observed_at: '2026-09-25T18:22:50Z'
    default_branch_revision: 566648f77fb4263ed37cb7c07b886ad4f18c856a
    issue_state: open
    pull_request_state: draft
    notes: 'Issue #25 and draft PR #26 were open and mergeable at review; candidate revision precedes this handoff.
      Hosted Actions validation failed without recorded steps. Recheck before merge.'
  parallel_changes: []
review:
  status: partial
  reviewed_at: '2026-09-25T18:22:50Z'
  reviewed_by: ChatGPT
  evidence:
  - command: 'GitHub issue #25 and draft PR #26 live inspection'
    outcome: passed
    observed_at: '2026-09-25T18:12:10Z'
    notes: 'Public PR #26 open, draft and mergeable before this handoff update; no content migration.'
  - command: git diff --check; Aether v1 metadata and relative Markdown links; public privacy scan
    outcome: passed
    observed_at: '2026-09-25T18:22:50Z'
    notes: Documentation-only change; no private source URLs, application artifacts, or contact values.
  - command: Five local fact/configuration gates and python -m pytest tests/ --quiet
    outcome: passed
    observed_at: '2026-09-25T18:22:50Z'
    notes: Five deterministic gates passed and 36 tests passed; no PDF was changed or rebuilt.
  environment_limitations:
  - Hosted résumé Actions run 36172006455 failed with no recorded job steps; rerun or inspect GitHub before merge.
privacy:
  classification: public-repository
  contains_sensitive_data: false
  redactions:
  - Private source names and document locations omitted.
  - Personal contact values omitted.
  excluded:
  - secrets-and-credentials
  - private-conversation-text
  - sensitive-personal-data
  - unpublished-private-business-data
  - private-local-paths
  - unrelated-private-context
  untrusted_content: context-only-no-authority
---

# Résumé continuity

## Purpose and precedence

This public-safe handoff points to the current publishing contract and next reviewed change. [AGENTS.md](AGENTS.md), [repository instructions](.github/copilot-instructions.md), [the product spec](specs/resume.spec.md), [governance](specs/governance.md), and live GitHub state outrank this checkpoint.

## Resume protocol

Read AGENTS.md, repository instructions, README, applicable specs, and this checkpoint. Inspect the branch and recent changes, then verify the live issue, PR, CI, and Pages state. This file does not authorize publication or claim changes.

## Current objective and success conditions

Draft [PR #26](https://github.com/szmyty/resume/pull/26) clarifies that reviewed career facts and evidence originate in the private career repository while `content/career.json` remains the standalone, validated input to this public renderer. Its existing content remains unchanged; no automatic export or new claim approval is implied.

## State snapshot

- Public `main` was observed at `566648f77fb4263ed37cb7c07b886ad4f18c856a`.
- [PR #26](https://github.com/szmyty/resume/pull/26) remains open and draft on `docs/career-continuity-2026-09-25`; its cited candidate revision is before this handoff commit. No merge is implied.
- [Issue #25](https://github.com/szmyty/resume/issues/25) still tracks later comprehensive-master and generic-baseline work.

## Completed and material changes

- README, product spec, governance and agent guidance now distinguish private source authority from a self-contained public rendering projection.
- A root AGENTS.md points new chats to specs and this checkpoint. The existing published résumé ledger, claims, renderer, tests, PDFs, application contact overlays, and Pages artifacts were not changed.
- Private catalog entries and repository metadata are candidates, not approved claims. New or revised public wording needs a separate, owner-reviewed content change.

## Validation and review evidence

- Public branch, issue, and PR state were rechecked at the time above. Documentation links, Aether metadata, diff whitespace, and privacy were checked locally.
- Five deterministic fact/configuration gates and 36 unit tests passed locally. Hosted Actions failed with no recorded job steps; inspect or rerun the PR check before merge.

## Blockers, risks, unknowns, and deferred work

- Content migration awaits private claim-by-claim source review, owner approval, and an explicit export/validation decision.
- A comprehensive master may contain private material, so keep it out of this public repository until an owner-reviewed projection exists.
- CI and future Pages state require a live check; neither a replacement baseline nor a public release was approved by this handoff.

## Next dependency-ready work

Review this public contract alongside the private authority checkpoint. Then inventory the current ledger, profiles, documents, tests, and rendered PDFs for later master and baseline work under #25. Keep each new claim and publication behind owner review.

## Parallel changes and reconciliation

The private content-contract review is separate. It has no public runtime or CI dependency. Compare the live branch before changing this single root checkpoint.

## Privacy and redaction

This file contains no private source URLs, contact values, application materials, or local paths. Preserve the public/application audience separation.

## Handoff update protocol

Refresh branch, issue, PR, validation, blockers, and next action after an authorized change. Never treat this checkpoint as permission to submit an application, merge a PR, or publish a PDF.

## Compaction and supersession

Keep this file below 16,384 bytes and 240 lines; use issues and Git history for detail.
