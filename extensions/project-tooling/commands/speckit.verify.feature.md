---
description: "Independently verify a complete feature before review or deployment"
---

# Verify Feature

Run after all feature tasks are individually verified and before delivery.

1. Enforce the same model and read-only policy as task verification.
2. Build a full traceability matrix across requirements, acceptance scenarios, plan decisions,
   constitution principles, tasks, code, and evidence.
3. Run complete architecture, contract, security, unit, integration, performance, device/platform,
   recovery, and deployment gates required by the feature.
4. Distinguish pass, fail, blocked, incomplete, and not-run. A subset cannot represent a full suite.
5. Write `.specify/verifications/<feature>/feature.json` only.
6. Reject delivery for any critical/high finding, unverified required scenario, secret leak,
   architecture violation, failed full suite, or dishonest evidence.

Convergence may follow only after this independent report exists.
