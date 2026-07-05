---
description: "Deterministically audit project tooling without installing or updating anything"
---

# Audit Project Tooling

This command belongs to the **project lifecycle**, not a feature lifecycle.

1. Locate the project root containing `.specify/`.
2. Run:

   ```bash
   python3 .specify/extensions/project-tooling/scripts/tooling_audit.py audit \
     --root . --output .specify/project/tooling-inventory.json
   ```

3. Read the generated inventory and create `.specify/project/tooling-report.md` with separate
   sections for declared, imported, executed, installed, conflicting, missing, and unknown items.
4. Cite file/line evidence for project usage and executable evidence for local availability.
5. Never read secret values, infer a required version without evidence, install tools, or modify
   feature artifacts.
6. If `.specify/project/tooling-policy.json` exists, also run `check` and report the exit status.

Output status is `audited`, `conflicts_found`, or `blocked`. It is never `updated`.
