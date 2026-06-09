# Example: Agent Workflow

This document illustrates an example of a reflector-compliant agent workflow.

## Scenario

A scoped agent is tasked with implementing a new API endpoint within the
governance contract boundaries defined for the `feature/user-profile` scope.

## Workflow Steps

```
1. Agent receives task: "Implement GET /users/{id} endpoint"

2. Agent verifies scope:
   - Allowed: /src/api/, /tests/api/, /docs/api/
   - Prohibited: /infra/, /config/, governance contracts

3. Agent begins implementation:
   - Generates handler code in /src/api/users.py
   - Generates tests in /tests/api/test_users.py
   - Updates API documentation

4. Audit layer monitors:
   - All file modifications logged to audit trail
   - No scope violations detected

5. Agent reaches Milestone M1: "Feature implementation complete"
   - Emits milestone completion signal
   - Suspends autonomous progression

6. Milestone synchronization layer:
   - Runs automated validation suite
   - Checks: tests pass, coverage ≥ 80%, no lint errors
   - Validation result: PASS

7. Human governance checkpoint:
   - Reviewer receives summary: "3 files changed, all tests pass"
   - Reviewer approves

8. Agent proceeds to next phase:
   - Opens pull request
   - Attaches audit trail as PR artifact
```

## Governance Contract (Abbreviated)

```yaml
scope:
  allowed_paths:
    - src/api/
    - tests/api/
    - docs/api/
  prohibited_paths:
    - infra/
    - .github/
obligations:
  - emit_audit_events: true
  - halt_at_milestone: true
  - request_approval_for_out_of_scope: true
milestones:
  - id: M1
    name: Feature implementation complete
    validation:
      - tests_pass: true
      - coverage_threshold: 80
      - lint_clean: true
```
