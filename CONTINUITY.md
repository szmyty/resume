---
schema_version: aether.repository-continuity/v1
repository:
  id: szmyty/resume
  visibility: public
  default_branch: main
  continuity_path: CONTINUITY.md
document:
  status: active
  updated_at: '2026-09-27T12:47:55Z'
  max_bytes: 16384
  max_lines: 240
  stale_reason: null
  superseded_by: null
scope:
  purpose: Hand off the public publisher inventory and reviewed projection boundary.
  includes:
  - Issue #25 checkpoint 1 inventory, contract, and migration plan.
  - Current public build and validation limits.
  excludes:
  - Private evidence, contact values, application PDFs, and conversation history.
  - Private repository URLs and source locators.
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
  - specs/source-projection-contract.v1.md
  - docs/roadmap/issue-25-checkpoint-1.md
  - content/career.json
  - https://github.com/szmyty/resume/issues/25
work:
  objective: Complete the publisher inventory and prepare a safe review-to-projection migration path.
  success_conditions:
  - Inventory actual public inputs, render path, tests, and artifact limitations.
  - Document versioned ownership and approval boundary before any data migration.
  - Preserve public claims, renderer, and published PDF in this checkpoint.
  active_issue:
    provider: github
    id: szmyty/resume#25
    url: https://github.com/szmyty/resume/issues/25
  next:
    kind: action
    id: review-inventory-pr-then-schema-checkpoint
    description: Review PR #29; after merge, check the first box in #25 and begin schema/ID support only from owner-reviewed requirements.
    readiness: ready
    references:
    - https://github.com/szmyty/resume/pull/29
    - https://github.com/szmyty/resume/issues/25
    depends_on: []
state:
  base:
    revision: 09210c15d2429c2b4324aca076bd29092de26663
    ref: refs/heads/main
    verified_at: '2026-09-27T12:47:55Z'
  candidate:
    branch: codex/issue-25-inventory-contract-2026-09-27
    revision: 9d0a9827b70333226faa2710916914efad1ffe4b
    pull_request:
      provider: github
      id: szmyty/resume#29
      url: https://github.com/szmyty/resume/pull/29
    handoff_state: ready-for-owner-review
  live:
    status: verified
    observed_at: '2026-09-27T12:47:55Z'
    default_branch_revision: 09210c15d2429c2b4324aca076bd29092de26663
    issue_state: open
    pull_request_state: draft
    notes: 'PR #28 merged; no open PR before #29. Issue #25 remains open. This PR changes documentation only.'
  parallel_changes: []
review:
  status: partial
  reviewed_at: '2026-09-27T12:47:55Z'
  reviewed_by: ChatGPT
  evidence:
  - command: GitHub tree, issue, PR, CI, and source inventory
    outcome: passed
    observed_at: '2026-09-27T12:47:55Z'
    notes: 'Current main inspected at 09210c1; the public ledger has two roles and eleven claims. No generated PDF is committed.'
  - command: Five deterministic source and configuration gates
    outcome: passed
    observed_at: '2026-09-27T12:47:55Z'
    notes: 'Facts, documents, profiles, placeholders, and public destinations passed on a reconstructed source snapshot.'
  - command: Local general public build, ATS/PDF gates, and two-page visual inspection
    outcome: passed
    observed_at: '2026-09-27T12:47:55Z'
    notes: 'Two-page letter PDF built; Poppler/pypdf extraction and metadata/privacy/layout gates passed. This is not a hash of the currently served Pages file.'
  - command: Hosted CI and Pages observation
    outcome: limited
    observed_at: '2026-09-27T12:47:55Z'
    notes: 'Last visible successful deploy was 2026-08-22; later validation failed before recording steps. Current served Pages bytes were not fetched.'
  environment_limitations:
  - Pytest was unavailable locally, so the full unit suite was not rerun.
  - Hosted Actions and current served Pages state need separate confirmation before publication claims.
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
  untrusted_content: context-only-no-authority
---

# Résumé continuity

## State and next action

[Issue #25](https://github.com/szmyty/resume/issues/25) remains open. [PR #29](https://github.com/szmyty/resume/pull/29) documents checkpoint 1: the [publisher inventory](docs/roadmap/issue-25-checkpoint-1.md) and [versioned review-to-projection contract](specs/source-projection-contract.v1.md). It changes no claim, renderer, contact policy, or PDF. Review and merge that PR before checking the first roadmap box. Checkpoints 2–6 remain open.

The private career workflow owns reviewed facts and evidence; this public repository's `content/career.json` is a self-contained rendering projection. Historical `verified` markers in the public ledger do not constitute a new owner approval. No automatic export or private CI dependency exists. A comprehensive owner-only master and the submitted/application materials stay outside public Git and Pages.

## Validation boundary

The local `general` public résumé built to two letter pages and passed the deterministic source gates, Poppler/pypdf ATS extraction, and PDF layout/privacy checks. Both pages were inspected. Pytest was not installed in this environment, and the currently served Pages PDF could not be independently fetched. The last visible successful build/deploy was on 2026-08-22; later hosted validation failed before steps ran. Do not report a fresh deploy or a new approved baseline from this documentation PR.

## Handoff protocol

Read AGENTS.md, repository instructions, README, the applicable specs, and this checkpoint. Verify branch, issue, PR, CI, and Pages state live. This dated file is not authority for career facts, merge approval, or publication. Keep it below 16,384 bytes and 240 lines.
