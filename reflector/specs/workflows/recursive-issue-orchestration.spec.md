---
title: Recursive Issue Orchestration Specification
version: 0.1.0
status: draft
category:
  - workflows
  - orchestration
  - recursion
tags:
  - synchronization-first
  - checkpoints
  - mixed-initiative
---

# Purpose

Define a reusable issue-to-artifact recursion contract for publication-oriented repositories.

---

# Lifecycle

1. **Orient**
   - scope issue boundaries
   - declare acceptance criteria
2. **Align**
   - reconcile active work with relevant specs/manifests
3. **Execute**
   - generate a bounded artifact set
4. **Audit**
   - run synchronization and readiness checks
5. **Synchronize**
   - record checkpoint evidence and continuation decision

---

# Continuation Rules

- A cycle MAY continue only after a non-failing audit verdict.
- A cycle MUST terminate in one of two states:
  - stabilized milestone artifact set, or
  - explicitly scoped successor issue.
- Successor issues MUST inherit synchronization context from the previous checkpoint.

---

# Governance and Collaboration

- Mixed-initiative collaboration is required: AI may propose and generate, humans approve checkpoint continuation.
- Architectural ambiguity MUST escalate to human review before recursive expansion.
- Checkpoints SHOULD be lightweight but explicit so recursive state remains observable.

---

# Repository Alignment

This pattern aligns with reflector's current execution surfaces:
- orchestration tooling: `reflector/`, `scripts/`
- synchronization/audit artifacts: `audits/`
- governance boundaries: issue/PR review plus milestone checkpoints
