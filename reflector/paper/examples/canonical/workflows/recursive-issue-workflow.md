# Recursive Issue Workflow Example

## Scenario
A scoped issue requests a new appendix artifact describing milestone stabilization.

## Lightweight Execution Loop
```text
Issue #142 (scoped)
  -> specification-checkpoint (workflow + synchronization specs verified)
  -> execution (appendix artifact generated)
  -> reflective-audit (scope, consistency, drift checks)
  -> synchronization-checkpoint (conditional-pass)
  -> follow-up Issue #143 (diagram clarification)
  -> synchronization-checkpoint (pass)
```

## Checkpoint Ledger (Example)
| checkpoint | issue | verdict | continuation |
|---|---|---|---|
| cp-142-a | #142 | conditional-pass | open follow-up #143 |
| cp-143-a | #143 | pass | authorize milestone closure |

## Milestone Stabilization Rule
A milestone is stable when all linked checkpoint verdicts are `pass` and no drift signal remains open.
