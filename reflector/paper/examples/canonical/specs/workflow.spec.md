# workflow.spec.md

## Objective
Describe a bounded recursive workflow for issue-to-artifact execution.

## Phases
1. `orient`: scope issue and acceptance criteria.
2. `align`: confirm relevant specs are current.
3. `execute`: generate or modify bounded artifact set.
4. `audit`: run reflective checks against acceptance criteria.
5. `synchronize`: record checkpoint and continuation decision.

## Transition Conditions
- `orient -> align`: issue scope and acceptance criteria are explicit.
- `align -> execute`: required specs are present and non-conflicting.
- `execute -> audit`: artifact set is committed to a reviewable diff.
- `audit -> synchronize`: audit verdict is not `fail`.

## Recursion Rule
Each synchronized cycle must produce either:
- a stabilized milestone, or
- a new scoped issue with inherited context.
