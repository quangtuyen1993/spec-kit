---
description: "Prepare, approve, execute, and verify project-level tool updates"
---

# Update Project Tooling

This is the only tooling command allowed to mutate project-level tools.

1. Require confirmed `.specify/project/tooling-policy.json`.
2. Run scanner `propose` into `.specify/project/update-plan.json`.
3. Resolve each action into an exact manager-specific command and explain lockfile/CI impact.
4. Show every command and request explicit user approval. Approval for one command does not approve
   adjacent updates.
5. Preserve dirty worktrees and never overwrite unrelated user changes.
6. Run only approved commands. Never print credentials or environment secret values.
7. Re-run `audit` and `check`; update `tooling-report.md` with exact results.
8. Any failed check leaves project status `tooling_unverified`; affected features remain blocked.

Never silently update SDKs, runtimes, dependencies, skills, MCP servers, device images, or CI.
