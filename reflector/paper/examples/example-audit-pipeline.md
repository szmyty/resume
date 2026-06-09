# Example: Audit Pipeline

This document illustrates an example of a reflector recursive audit pipeline.

## Overview

The audit pipeline continuously monitors system state and validates invariants
throughout all phases of autonomous agent execution.

## Pipeline Stages

```
┌─────────────────────────────────────────────────────────────┐
│                    Audit Pipeline                           │
├─────────────┬───────────────────────────────────────────────┤
│  Stage 1    │  Event Capture                               │
│             │  - Intercept all agent actions               │
│             │  - Capture file system changes               │
│             │  - Record agent reasoning traces             │
├─────────────┼───────────────────────────────────────────────┤
│  Stage 2    │  Invariant Validation                        │
│             │  - Check structural invariants               │
│             │  - Check behavioral invariants               │
│             │  - Check governance invariants               │
├─────────────┼───────────────────────────────────────────────┤
│  Stage 3    │  Drift Detection                             │
│             │  - Compare current state to milestone target │
│             │  - Compute drift score                       │
│             │  - Trigger alert if drift > threshold        │
├─────────────┼───────────────────────────────────────────────┤
│  Stage 4    │  Audit Trail Append                          │
│             │  - Append validated event to audit log       │
│             │  - Sign event with timestamp                 │
│             │  - Update system state snapshot              │
└─────────────┴───────────────────────────────────────────────┘
```

## Example Audit Log Entry

```json
{
  "timestamp": "2024-01-15T14:32:01Z",
  "agent_id": "agent-001",
  "action": "file_write",
  "target": "src/api/users.py",
  "scope_check": "PASS",
  "invariants_checked": [
    {"id": "INV-001", "name": "no_infra_modifications", "result": "PASS"},
    {"id": "INV-002", "name": "test_coverage_maintained", "result": "PASS"}
  ],
  "drift_score": 0.02,
  "drift_alert": false,
  "milestone": "M1",
  "phase": "implementation"
}
```

## Invariant Definitions

```yaml
invariants:
  - id: INV-001
    name: no_infra_modifications
    description: Agent must not modify infrastructure files
    check: "no files in infra/ have been modified"
    severity: critical

  - id: INV-002
    name: test_coverage_maintained
    description: Test coverage must not drop below threshold
    check: "coverage >= 80%"
    severity: warning

  - id: INV-003
    name: governance_trail_complete
    description: All milestone approvals must be recorded
    check: "all milestones have an approval record"
    severity: critical
```
