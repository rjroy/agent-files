---
name: simplify
description: This skill should be used when the user wants to clean up code without changing behavior. Dispatches cleanup agents, runs tests to verify behavior is preserved, then runs code review. Triggers include "simplify this", "clean up this code", "refactor without changing behavior", "reduce complexity".
---

# Simplify

Orchestrate code cleanup through agent delegation. Preserve behavior. Don't change what the code does.

Act as orchestrator. Dispatch work to sub-agents with the host's subagent capability. Do not edit code directly.

## Input

Invoked as `/simplify` with optional arguments:

- **No args**: simplify files with uncommitted changes (`git status`)
- **File pattern**: simplify files matching the pattern
- **Notes path** (`.lore/work/notes/*.md`): resume a previous session

## Process

Only one agent may operate on the target files at a time. Await cleanup before
testing and testing before review. Testing and review agents are read-only and
return findings rather than editing files.

**Cleanup.** Select a simplification agent from `.lore/lore-agents.md` when available; otherwise dispatch the host's general-purpose subagent with the file list and a strict preserve-behavior cleanup role.

**Test.** Dispatch a testing agent with the host's subagent capability. Include which files changed and how to run the test suite. Expect pass/fail and notable findings. If tests fail, diagnose and route back to the cleanup agent for correction. After two failed attempts on the same issue, escalate to the user.

**Review.** Dispatch a review agent with the host's subagent capability. Include which files to review and the requirement that behavior must be preserved. Give each finding a stable ID. Route findings back to the cleanup agent for correction, then request verification with the complete unresolved finding records and correction diff. Inspect the changed surface and report newly encountered material issues without reopening unrelated accepted surfaces. After two failed attempts on one finding or three total correction rounds, escalate to the user.

## Output

Record what happened in a notes file at `.lore/work/notes/simplify-<identifier>.md`. Load `../../shared/frontmatter-schema.md (resolved from this skill's base directory)` for the frontmatter fields. The body is freeform — capture which files were processed, what was simplified, any failures and how they were resolved.

Write the body in Markdown per the "Body Format" section of `../../shared/frontmatter-schema.md (resolved from this skill's base directory)`. Reach for embedded inline HTML only when a visual carries meaning prose can't, such as a color-coded per-file outcome table.

## Escalation

Two conditions require human intervention. Everything else is autonomous.

1. **Stuck loop**: Two failed attempts on one finding or three correction rounds.
2. **Behavior change detected**: Tests fail in a way that suggests behavior changed rather than a cleanup regression.
