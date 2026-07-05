---
description: "Independently and read-only verify one implemented task"
---

# Verify Task

Input requires a task ID and active feature.

1. Load constitution, project tooling/verification policy, feature spec, plan, tasks, contracts,
   and the task's current implementation.
2. Require the configured verifier model class. If unavailable and downgrade is false, write a
   blocked report and stop.
3. Operate read-only on production code, tests, and configuration. Allowed writes are the
   verification report plus the matching task ledger row/checkbox after the verdict is known.
4. Independently map the task to requirements and acceptance criteria. Do not trust implementer
   summaries or checked boxes.
5. Inspect for placeholder/no-op tests, broad assertions, disabled checks, architecture violations,
   secret exposure, and unfaithful mocks.
6. Run every required full suite and faithful environment. Never edit code/tests to force a pass.
7. Record exact commands, totals, findings, blockers, model class, read-only status, and verdict.

Verdicts: `verified`, `rejected`, `blocked`, or `not_verified`. Only `verified` completes the task;
`rejected` returns it to implementation. On `verified`, update the ledger and checkbox. On every
other verdict, keep the checkbox unchecked and record the exact state.
