# synchronization.spec.md

## Purpose
Define checkpoint contracts for recursive synchronization cycles.

## Scope
This specification governs synchronization checkpoints for issue-driven paper and publication work.

## Checkpoint Types
- `specification-checkpoint`: confirm active specs match scoped issue intent.
- `artifact-checkpoint`: verify generated artifacts are complete and internally consistent.
- `audit-checkpoint`: record reflective audit result and drift signals.
- `continuation-checkpoint`: authorize the next recursive issue.

## Required Evidence
Each checkpoint record must include:
- checkpoint id and timestamp
- artifact set hash (or commit SHA)
- audit verdict (`pass`, `conditional-pass`, `fail`)
- continuation decision with reviewer identity

## Bounded Execution Rules
- A workflow may only cross one checkpoint per scoped issue.
- `conditional-pass` checkpoints require a follow-up issue before continuation.
- Any unresolved `fail` blocks recursive continuation.
