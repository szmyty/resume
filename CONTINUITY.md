---
schema_version: aether.repository-continuity/v1
repository:
  id: szmyty/resume
  visibility: public
  default_branch: main
  continuity_path: CONTINUITY.md
document:
  status: active
  updated_at: "2026-09-25T16:45:09Z"
  max_bytes: 16384
  max_lines: 240
  stale_reason: null
  superseded_by: null
scope:
  purpose: "Preserve the public-safe next step for the résumé publishing system without importing private evidence."
  includes:
    - "Current public source, rendering, and privacy contract."
    - "The post-intake master/baseline roadmap issue and review branch."
  excludes:
    - "Private source files, local contact overlays, application PDFs, and conversation history."
    - "Full roadmap text and generated artifacts."
  precedence:
    - user-and-runtime-instructions
    - scoped-repository-instructions
    - live-repository-and-work-tracker-state
    - canonical-repository-sources
    - continuity-checkpoint
  canonical_sources:
    - .github/copilot-instructions.md
    - README.md
    - specs/resume.spec.md
    - specs/governance.md
    - content/career.json
    - https://github.com/szmyty/resume/issues/25
work:
  objective: "Prepare a public-safe handoff for the reviewed comprehensive-master and generic-baseline roadmap."
  success_conditions:
    - "The current public publishing contract and issue #25 are discoverable from the root checkpoint."
    - "No private evidence, contact overlay, application artifact, or newly generated PDF is committed or published by this documentation change."
  active_issue:
    provider: github
    id: szmyty/resume#25
    url: https://github.com/szmyty/resume/issues/25
  next:
    kind: issue
    id: szmyty/resume#25
    description: "After the remaining intake and reviewed fact-ownership contract, begin issue #25 by inventorying the current ledger, specs, profiles, and renderer."
    readiness: blocked
    references:
      - https://github.com/szmyty/resume/issues/25
      - https://github.com/szmyty/resume/blob/main/specs/resume.spec.md
    depends_on:
      - remaining-document-intake
      - reviewed-fact-ownership-contract
state:
  base:
    revision: 566648f77fb4263ed37cb7c07b886ad4f18c856a
    ref: refs/heads/main
    verified_at: "2026-09-25T16:42:05Z"
  candidate:
    branch: docs/career-continuity-2026-09-25
    revision: fd55943e637fed9720f72e7df48175876c9b172e
    pull_request:
      provider: github
      id: szmyty/resume#26
      url: https://github.com/szmyty/resume/pull/26
    handoff_state: in-progress
  live:
    status: verified
    observed_at: "2026-09-25T16:42:05Z"
    default_branch_revision: 566648f77fb4263ed37cb7c07b886ad4f18c856a
    issue_state: open
    pull_request_state: draft
    notes: "Issue #25 and draft PR #26 were observed open; the cited candidate revision contains the instruction pointer and precedes this handoff commit."
  parallel_changes: []
review:
  status: partial
  reviewed_at: "2026-09-25T16:45:09Z"
  reviewed_by: ChatGPT
  evidence:
    - command: "git clone --depth 1 --branch main https://github.com/szmyty/resume.git; git rev-parse HEAD^{tree}"
      outcome: passed
      observed_at: "2026-09-25T16:39:44Z"
      notes: "Public main resolved to 566648f and tree e960ca0; no existing root continuity file."
    - command: "GitHub repository metadata, issue #25, and draft PR #26 inspection"
      outcome: passed
      observed_at: "2026-09-25T16:42:05Z"
      notes: "Repository is public, issue open, and draft PR open; no other résumé PR was returned."
    - command: "Validate Aether v1 metadata, required headings, size, and privacy"
      outcome: passed
      observed_at: "2026-09-25T16:45:09Z"
      notes: "Structural and public-data review on this candidate."
    - command: "python scripts/quality_gates.py validate-facts and python -m pytest tests/"
      outcome: not-run
      observed_at: "2026-09-25T16:45:09Z"
      notes: "This PR changes documentation and an instruction pointer only; no fact, renderer, or artifact changes."
  environment_limitations:
    - "PR checks and future Pages output require a fresh live inspection after the candidate is updated."
privacy:
  classification: public-repository
  contains_sensitive_data: false
  redactions:
    - "Private source names and document locations omitted."
    - "Personal contact values omitted."
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

This root checkpoint is a public-safe pointer for the current publishing system and its next reviewed change. [Repository instructions](.github/copilot-instructions.md), [the product spec](specs/resume.spec.md), [governance](specs/governance.md), and live GitHub state outrank this snapshot.

## Resume protocol

Read the repository instructions, README, applicable specs, and this checkpoint. Inspect current branch and recent changes, then verify the live issue, PR, CI, and publication state. Do not treat a prepared plan as an approved public release.

## Current objective and success conditions

The present change establishes a durable handoff for [issue #25](https://github.com/szmyty/resume/issues/25). Success here means a discoverable, privacy-safe checkpoint; the master and revised baseline remain future work.

## State snapshot

- Verified base at observation: public `main` at `566648f77fb4263ed37cb7c07b886ad4f18c856a`.
- Candidate: [draft PR #26](https://github.com/szmyty/resume/pull/26), branch `docs/career-continuity-2026-09-25`; the cited revision precedes this file and no merge is implied.
- Live observation: issue #25 open and PR #26 draft at the stated time. Recheck before editing.

## Completed and material changes

- The current README/spec/governance describe `content/career.json` as this repo's canonical verified ledger for its existing public projections. Issue #25 will reconcile that authority with the reviewed upstream source before content migration; no ownership change has been accepted yet.
- The candidate adds an instruction pointer and this handoff. It does not change claims, PDFs, tests, Pages, or application outputs.

## Validation and review evidence

- Public repository identity, main revision, tree, and the issue/PR state were checked as recorded above.
- This candidate's Aether metadata, headings, size, and privacy were checked. Renderer/fact tests were not run for a documentation-only change; check live PR checks before merge.

## Blockers, risks, unknowns, and deferred work

- Blocked: remaining document intake and a reviewed fact-ownership/privacy contract.
- Risk: a comprehensive master could contain material unsuitable for public Git or Pages; keep private inputs and rendered owner-only artifacts outside committed public content.
- Unknown: future CI and publication status. No baseline replacement or public release has been reviewed.
- Deferred: master renderer, generic baseline polish, and tailored résumé/letter pipeline under #25.

## Next dependency-ready work

When the upstream review is complete, begin #25 with an inventory of `content/career.json`, profiles, documents, tests, and existing PDFs. Decide the projection contract first, then implement and visually review the master and baseline. Until then this issue remains blocked.

## Parallel changes and reconciliation

No other open résumé PR was returned at observation. Recheck before modifying the ledger, specs, or this single root checkpoint.

## Privacy and redaction

This file is public and contains no private source URLs, owner contact values, application material, or local paths. Follow the repo's existing public/application separation.

## Handoff update protocol

After authorized implementation and validation, refresh this file in the same PR with actual base/candidate/live state, checks, blockers, and one next action. Never use it to authorize publication, submission, or merge.

## Compaction and supersession

Keep this file below 16,384 bytes and 240 lines. Replace stale snapshots rather than appending session history; mark unresolved conflicts stale and cite a stable successor if superseded.
