---
schema_version: aether.repository-continuity/v1
repository:
  id: szmyty/resume
  visibility: public
  default_branch: main
  continuity_path: CONTINUITY.md
document:
  status: active
  updated_at: '2026-09-25T18:51:44Z'
  max_bytes: 16384
  max_lines: 240
  stale_reason: null
  superseded_by: null
scope:
  purpose: Hand off the merged public fact-authority contract and later reviewed document work.
  includes:
  - Self-contained rendering projection and owner-reviewed claim gate.
  - Merged governance changes and the comprehensive-master/baseline roadmap.
  excludes:
  - Private evidence, contact overlays, application PDFs, and conversation history.
  - Private repository URLs, source locators, and full roadmap text.
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
  objective: Prepare the public document system for later owner-reviewed fact projection and baseline work without changing current claims or PDFs.
  success_conditions:
  - Existing content/career.json remains the self-contained validated public renderer input.
  - New public claim wording is source-reviewed and owner-approved before projection.
  - Private master and contact overlays stay out of public Git, CI, and Pages.
  active_issue:
    provider: github
    id: szmyty/resume#25
    url: https://github.com/szmyty/resume/issues/25
  next:
    kind: action
    id: inventory-publishing-inputs-for-later-reviewed-baseline
    description: 'Inventory the current public claim ledger, profiles, documents, renderer, tests, and PDFs under #25; wait for approved claim reviews before any content migration or baseline replacement.'
    readiness: ready
    references:
    - https://github.com/szmyty/resume/issues/25
    depends_on: []
state:
  base:
    revision: d36ac2dea84718d2c54e98f5cafc8de680a12fca
    ref: refs/heads/main
    verified_at: '2026-09-25T18:51:44Z'
  candidate:
    branch: null
    revision: null
    pull_request: null
    handoff_state: no-active-change
  live:
    status: verified
    observed_at: '2026-09-25T18:51:44Z'
    default_branch_revision: d36ac2dea84718d2c54e98f5cafc8de680a12fca
    issue_state: open
    pull_request_state: merged
    notes: 'Documentation PR #26 merged into main. Issue #25 remains open; no claim migration, renderer change, replacement PDF, or new Pages publication was part of #26.'
  parallel_changes: []
review:
  status: partial
  reviewed_at: '2026-09-25T18:51:44Z'
  reviewed_by: ChatGPT
  evidence:
  - command: GitHub PR #26, issue #25, and default branch inspection
    outcome: passed
    observed_at: '2026-09-25T18:51:44Z'
    notes: 'PR #26 merged as d36ac2d; the six changed files were documentation, without a changed claim ledger or PDF.'
  - command: Five local fact/configuration gates and python -m pytest tests/ --quiet
    outcome: passed
    observed_at: '2026-09-25T18:22:50Z'
    notes: 'Five deterministic gates and 36 tests passed locally before merge; no PDF was rebuilt.'
  - command: Hosted Actions after PR #26 merge
    outcome: limited
    observed_at: '2026-09-25T18:37:00Z'
    notes: 'Post-merge run 36174507790 failed validation with zero recorded steps; build and Pages deploy were skipped.'
  environment_limitations:
  - Hosted Actions did not validate or deploy the merged documentation change. Inspect live CI and Pages state separately before claiming a successful release.
privacy:
  classification: public-repository
  contains_sensitive_data: false
  redactions:
  - Private source locators and contact values omitted.
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

This public-safe checkpoint records the merged publishing contract and next reviewed step. [AGENTS.md](AGENTS.md), [repository instructions](.github/copilot-instructions.md), [the product spec](specs/resume.spec.md), [governance](specs/governance.md), and live GitHub state outrank this file.

## Resume protocol

Read AGENTS.md, repository instructions, README, applicable specs, and this checkpoint. Inspect the branch and recent changes; verify live issue, PR, CI, and Pages state before changing content. This file does not authorize publication or claim changes.

## Current objective and success conditions

[Documentation PR #26](https://github.com/szmyty/resume/pull/26) merged the authority and handoff wording. `content/career.json` remains a standalone validated renderer input; new or revised public facts require source review and owner approval before they enter it. No automatic export or new claim approval resulted from that merge.

## State snapshot

- Public `main` was observed at merge commit `d36ac2dea84718d2c54e98f5cafc8de680a12fca`; PR #26 is merged, not an outstanding draft.
- [Issue #25](https://github.com/szmyty/resume/issues/25) remains open for later reviewed comprehensive-master, generic-baseline, and tailoring work. Its inventory and document-production checklist is not complete merely because the authority documentation merged.

## Completed and material changes

- README, product spec, governance, and agent guidance distinguish reviewed career fact authority from the public renderer's self-contained content projection.
- The existing published ledger, claims, renderer, tests, PDFs, and application contact overlays were not changed by PR #26.
- Future fact revisions need separate owner-reviewed changes; metadata or a historic draft alone cannot approve a new public claim.

## Validation and review evidence

- Before merge, documentation links, continuity metadata, diff whitespace, and public privacy were checked locally. Five deterministic gates and 36 tests passed.
- Post-merge Actions run `36174507790` failed validation before recording a step; build and Pages deploy were skipped. No current served Pages state was verified. Do not report hosted CI or deploy as successful.

## Blockers, risks, unknowns, and deferred work

- Content migration awaits claim-by-claim evidence review, owner approval, and a deliberate export/validation decision.
- The comprehensive master can contain private material; only an owner-reviewed public projection belongs here.
- A replacement generic baseline or Pages release was not approved by the documentation merge.

## Next dependency-ready work

Inventory the current `content/career.json`, profiles, document manifests, renderer, tests, and actual PDFs under #25. Prepare an implementation plan for reviewed master and baseline work. Keep content and publication changes behind owner review.

## Parallel changes and reconciliation

Fact review proceeds in its authoritative private workflow. This public renderer has no runtime or CI dependency on private sources. Verify current public branch and issue state before editing this handoff.

## Privacy and redaction

This file contains no private source URLs, contact values, application materials, or local paths. Preserve the public/application audience separation.

## Handoff update protocol

Refresh branch, issue, PR, validation, blockers, and next action after a reviewed change. This checkpoint never authorizes an application submission, PR merge, or PDF publication. Keep it below 16,384 bytes and 240 lines.
