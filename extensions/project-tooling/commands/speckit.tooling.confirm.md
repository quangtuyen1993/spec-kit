---
description: "Confirm the audited project toolchain and create a governed tooling policy"
---

# Confirm Project Tooling

Require `.specify/project/tooling-inventory.json` and `tooling-report.md` from a completed audit.

1. Present a compact table of tools, versions, skills, environments, conflicts, and unknowns.
2. Ask the user to confirm required tools, exact/minimum versions, optional tools, supported
   environments, and verifier model policy.
3. Do not make ambiguous version or production-environment choices for the user.
4. Write confirmed policy to `.specify/project/tooling-policy.json` using
   `.specify/extensions/project-tooling/project-policy-template.json`.
5. Run scanner `check`; unresolved required conflicts keep status `confirmation_incomplete`.

This command writes policy only. It never installs or upgrades a tool.
