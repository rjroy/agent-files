---
name: implement
description: Use when ready to build from the user's current request or intent, optionally informed by a spec, design, plan, or notes. Triggers include "implement this", "build this", "implement the request/intent", "continue implementation", and "resume where we left off".
---

# Implement

Act as orchestrator. Dispatch work to sub-agents with the host's subagent capability and record what happens. Do not write code, run tests, or review code directly. Every implementation, testing, and review action goes through a subagent invocation. No exceptions.

## Input

Invoke `/implement` with the user's current request, optionally pointing to an intent, plan, design, spec, or notes file for context. A plan is useful but not required. Read linked material when it helps; historical artifacts inform the work but do not authorize or veto it. When resuming from notes, use them as context and confirm the next action against the user's current direction.

## Output

Implement the requested change. Keep or update a notes file only when it helps resume substantial or interrupted work; do not create one by default. When writing lore notes, follow the shared frontmatter schema.

## Process

### 1. Initialize

For substantial work where prior context may matter, ask the `lore-researcher` subagent to surface relevant history. Do not delay a straightforward change for irrelevant lore research. If invoked, use its result as context and verify consequential claims against current code or the user.

Understand the user's requested outcome and any new evidence. Use the plan's steps when a useful plan is supplied; otherwise choose a small number of coherent phases appropriate to the work. Prefer existing capabilities and account for affected consumers, actual behavior, and relevant safety or compatibility constraints. Current user direction may authorize behavior or contract changes; do not treat an old artifact's silence, approval status, or requirements as a veto. Raise concrete safety/compatibility consequences or consequential unresolved choices, not mere historical noncompliance.

**Select agents.** Consult `.lore/lore-agents.md` if it exists. Match agents to three mandatory roles:

| Role | Registry Category | Fallback |
|------|-------------------|----------|
| Implementation | Implementation | Host general-purpose subagent |
| Testing | Testing | Host general-purpose subagent |
| Review | Code Quality | `bun-typescript-reviewer` for matching projects; otherwise host general-purpose subagent |

When the registry has no Code Quality selection, use the bundled
`bun-typescript-reviewer` if the repository uses Bun and TypeScript and the
changed surface includes its daemon, Unix-socket, CLI, Next.js, or React
architecture. Do not use it merely because a repository contains one incidental
TypeScript file. For other stacks, retain the host general-purpose fallback.

**Choose evidence.** Identify the project-specific behavior and risks that matter
to this change. Reuse adequate tests and other evidence; add focused checks for
distinct plausible defects or important safety/compatibility boundaries. The full
suite passing is not enough when it does not demonstrate the requested behavior.
Do not create requirement IDs, exhaustive mappings, or one test per step or goal.

### 2. Execute Phases

For each phase:

Only one agent may operate on a phase's files at a time. Await each result before
dispatching the next role. Testing and review agents are read-only: they return
evidence or findings and never edit files. Do not test or review a moving worktree.

**a. Implement.** Dispatch to an implementation agent with the host's subagent capability. Include the requested outcome, relevant paths, affected consumers, consequential constraints or authorized behavior changes, and useful prior-phase findings. When relevant, identify existing behavior to reuse, replace, or remove. Keep handoffs concise but sufficient to avoid contradicting the current direction. One agent at a time on the same files; await its result before continuing.

**b. Test.** Dispatch a read-only testing agent with changed files, the requested behavior, project-specific checks and risks, and test commands. Expect the result, commands or observations, and behavioral evidence. The suite passing does not substitute for focused checks when those are needed to prove the requested outcome.

**c. Review.** Dispatch a read-only review agent in initial-review mode. Include changed files, current requested behavior, validation evidence, and affected consumers/boundaries. Review actual behavior and relevant system invariants; do not treat historical documents as authority over current user direction. Report a finding only for a concrete material defect or risk with a consequence and bounded required outcome; give each finding a stable ID for correction. An obsolete parallel path or unused scaffolding is a finding only when evidence shows material maintenance or behavior cost, not a cleanup quota. A request for another test must identify a plausible defect current evidence would miss and the observable check needed. Accept adequate work without optional hardening or ceremonial coverage.

**d. Handle failures.** Route failures back to an implementation agent for correction and await completion. Re-dispatch only the failed checks and a verification review with the complete unresolved finding records and correction diff. Inspect the changed surface and report any newly encountered material issue, but do not reopen unrelated accepted surfaces. After two failed attempts on one finding, or three correction rounds in a phase, escalate to the user.

**e. Record.** Share concise results and evidence with the caller. Update existing notes when useful for resumption; do not create phase trackers or obligation maps as ceremony.

### 3. Validate

For multi-phase or cross-boundary work, use a terminal review to catch interactions the phase reviews could miss. A focused review can serve for a small change. Check cross-cutting behavior and relevant affected consumers; raise only concrete material findings, not historical noncompliance or cleanup preferences.

Route material findings to implementation for correction, then repeat only the failed checks and a focused verification review with the finding and correction context. Do not restart broad review unless the accepted surface materially changes. Continue until resolved or the bounded retry limit is reached.

### 4. Finalize

Summarize what changed, tests/review performed, important findings or divergences, and anything still unresolved. Update existing notes if applicable.

If the project uses an external tracker, inspect its hierarchy and dependency
semantics and reconcile related entries before creating or changing issues. Avoid
duplicates and dependency cycles; add dependencies only when needed and verify
they do not block prerequisites. After the last tracker mutation, regenerate any
passive export and compare it with authoritative tracker state.

When asked to commit after review, check the intended changes and required project safeguards. If code changes after testing/review, validate and review the changed behavior again.

## Escalation

Two conditions require human intervention. Everything else is autonomous.

1. **Stuck loop**: Two failed attempts on one finding, or three correction rounds in one phase. Present the finding IDs and failure history.
2. **Material uncertainty**: New evidence reveals a choice that could materially change the outcome and the user's current direction does not resolve it. Explain the trade-off and ask. A conflict with an old artifact alone is not a blocker; follow current user direction and surface concrete safety or compatibility consequences.

Do not ask for confirmation between phases.

## Divergence

If new evidence raises a material choice not resolved by the user's current direction, explain it and ask before choosing. Do not treat an old artifact's omission or contradiction alone as a blocker. Preserve test and review rigor, and raise concrete safety or compatibility consequences when they matter.
