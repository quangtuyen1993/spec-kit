# Project Tooling and Independent Verification

This extension keeps project lifecycle mutations separate from feature/task delivery.

## Install

```bash
specify extension add project-tooling
```

## Project lifecycle

```text
speckit.project-tooling.audit
→ speckit.project-tooling.confirm
→ speckit.project-tooling.update
→ verified project baseline
```

For an existing repository, audit before creating a constitution or feature plan. The scanner
records declared, imported, executed, installed, required, and unknown states separately, with
evidence. Audit never installs tools. Update requires explicit approval for exact commands.

Artifacts:

```text
.specify/project/
├── tooling-inventory.json
├── tooling-policy.json
├── tooling-report.md
├── update-plan.json
└── verification-policy.json
```

## Feature/task lifecycle

```text
specify → clarify → plan → tasks → analyze → implement → verify → converge
```

Feature commands consume the project tooling snapshot but do not mutate SDKs, runtimes, skills,
MCP servers, devices, containers, or CI baselines. A missing tool blocks the feature and hands
control back to the project lifecycle.

## Independent verification

Use `speckit.project-tooling.verify-task` after implementation and
`speckit.project-tooling.verify-feature` before delivery. The
verifier is read-only and must use the model class configured in
`.specify/project/verification-policy.json`. If that model is unavailable and downgrade is false,
verification is blocked.

Task states are:

```text
pending → implemented → verification_pending → verified | rejected | blocked
```

Only `verified` is complete.
