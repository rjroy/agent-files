---
name: implement
description: Use when ready to build from a spec, design, or plan, or to resume from notes. Triggers include "implement this", "build this", "implement the spec/design/plan", "continue implementation", and "resume where we left off".
---

# Implement

Act as orchestrator. Dispatch work to sub-agents with the host's subagent capability and record what happens. Do not write code, run tests, or review code directly. Every implementation, testing, and review action goes through a subagent invocation. No exceptions.

## Input

Invoked as `/implement <path>` where `<path>` is a lore artifact: spec, design, plan, or notes file. Read the input artifact and any lore documents it references. If the input is a notes file, resume from where it left off.

## Output

Implemented code plus a notes file at `.lore/work/notes/<artifact-name>.md`. Load `../../shared/frontmatter-schema.md (resolved from this skill's base directory)` for the frontmatter fields before writing.

The notes file needs enough structure to be resumable: a progress tracker (phases with checkboxes) and a log (what happened, failures, decisions, discoveries). Update it after every phase, not just at session end.

Write the body in Markdown per the "Body Format" section of `../../shared/frontmatter-schema.md (resolved from this skill's base directory)`. Reach for embedded inline HTML only when a visual carries meaning prose can't, such as a color-coded phase-status diagram readable at a glance mid-session.

## Process

### 1. Initialize

Search for related prior work: invoke the `lore-researcher` subagent with the host's subagent capability with the artifact description. Wait for the result before continuing. If that custom agent is unavailable, dispatch the host's general-purpose subagent with the research role from `agents/lore-researcher.md`.

Break the input into the smallest coherent implementable phases. If the input is a plan, phases are its steps. If a spec or design, group related work into phases without artificial splits. Prefer existing capabilities and name relevant reuse, replacement, deletion, intentional retirement, and retained contracts. Keep unrelated cleanup and unapproved contract retirement out of scope.

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

**Establish evidence.** Extract the source's obligations: requirements from a spec,
decisions and interface commitments from a design, or goals and validation from a
plan. Map each obligation to its phase and sufficient executable validation, reusing
existing tests/evidence where adequate. Discover affected consumers, state transitions,
and system boundaries. Add checks for distinct plausible defects, not one new test
per obligation, task, or layer; consolidate redundant checks and remove tests solely
protecting explicitly retired behavior. An unmapped obligation is a planning gap:
resolve it before implementation.

### 2. Execute Phases

For each phase:

Only one agent may operate on a phase's files at a time. Await each result before
dispatching the next role. Testing and review agents are read-only: they return
evidence or findings and never edit files. Do not test or review a moving worktree.

**a. Implement.** Dispatch to an implementation agent with the host's subagent capability. Include: the phase's work, relevant file paths, compact whole-change context (goal, affected surfaces, retained contracts, and planned reuse/replacements/deletions/intentional retirements), plus relevant prior-phase results or failures. Keep context focused; do not withhold the full-change decisions needed to avoid parallel or obsolete paths. One phase at a time. Await a stable changed-file manifest before continuing.

**b. Test.** Dispatch to a testing agent with the host's subagent capability. Include: which files changed, the phase-specific validation criteria established during initialization, the mapped source obligations, and how to run the test suite. Expect back: pass/fail, commands or observations, and evidence for each criterion. The suite passing does not substitute for the phase's behavioral checks.

**c. Review.** Dispatch to a review agent with the host's subagent capability in initial-review mode. Include: which files to review, relevant requirements from the source artifact, validation evidence, and affected consumers and boundaries. The reviewer may return a concise acceptance when the implementation is adequate. Check for obsolete parallel paths, unused scaffolding, unnecessary abstractions, and duplicate/incidental tests; report a material problem only with evidence in the changed scope, a concrete consequence and impact sufficient to delay acceptance, and a bounded required outcome. The consequence must be either failure to preserve requested behavior, an accepted design decision, or an important system invariant, or a demonstrated material maintenance cost within the changed scope. Give each finding a stable ID. A request for another test is not a finding unless it identifies the behavior or invariant left unvalidated, the plausible defect current evidence would miss, and the observable assertion needed. Accept the phase when the implementation has proportionate evidence and no material problem; do not require optional hardening or additional coverage.

**d. Handle failures.** Route failures back to an implementation agent for correction and await completion. Re-dispatch only the failed checks and a verification review with the complete unresolved finding records and correction diff. Inspect the changed surface and report any newly encountered material issue, but do not reopen unrelated accepted surfaces. After two failed attempts on one finding, or three correction rounds in a phase, escalate to the user.

**e. Record.** Update the notes file with results and evidence. Mark the phase's local gate complete only when every mapped criterion passes. Keep overall implementation status in progress until holistic validation passes.

### 3. Validate

After all local gates pass, dispatch one terminal acceptance review with the full source artifact, obligation-to-evidence mapping, changed-file manifest, and named consumers. Reconcile obligations with evidence and check cross-cutting behavior, including obsolete parallel paths, unused scaffolding, unnecessary abstractions, and duplicate or incidental tests. Report these only with changed-scope evidence, a demonstrated material maintenance cost or behavior/contract defect that warrants delaying acceptance, and a bounded required outcome. Do not create another review pass or demand cleanup without such a consequence. This is the only review called "final" or "acceptance."

Route findings through correction, targeted re-test, and verification review supplied with the complete finding records and correction diff. Do not restart a broad review unless the accepted surface changes. Final validation should reconcile evidence and expose cross-cutting defects, not discover basic unmapped requirements.

After acceptance findings close, record an accepted manifest in the notes: changed
paths and exact porcelain status; index blob identity or absent/unmerged marker; and
working-tree SHA-256 content hash or deletion marker. Include untracked files. This
records index and working-tree content separately for partially staged paths. Refresh
the manifest only after testing and targeted review accept a later delta. Commit
safety recomputes the same manifest and requires exact equality.

### 4. Finalize

Update the notes file status to `complete`. Summarize: what was built, how many phases, any divergences.

If the project uses an external tracker, inspect its hierarchy and dependency
semantics, reconcile existing children before creating issues, and reuse entries
keyed by source plan and step. Do not add a parent dependency on its own descendant
to represent completion. Add execution dependencies only when their propagation
cannot block a prerequisite, then inspect ready and blocked state. After the last
tracker mutation, regenerate any passive export and compare it with authoritative
tracker state.

When the user requests a commit after acceptance, do not reopen implementation or
review. Perform only commit safety checks: status, intended staged diff, secrets and
generated files, accepted-manifest equality, and required hooks. If source changes
no longer match the accepted manifest, test and review that delta before committing.
If a hook changes only a generated tracker export, inspect and report that change
narrowly instead of rerunning the workflow.

## Escalation

Two conditions require human intervention. Everything else is autonomous.

1. **Stuck loop**: Two failed attempts on one finding, or three correction rounds in one phase. Present the finding IDs and failure history.
2. **Material uncertainty**: New evidence reveals a choice that could materially change the outcome and the user's current direction does not resolve it. Explain the trade-off and ask. A conflict with an old artifact alone is not a blocker; follow current user direction and surface concrete safety or compatibility consequences.

Do not ask for confirmation between phases.

## Divergence

If new evidence raises a material choice not resolved by the user's current direction, explain it and ask before choosing. Do not treat an old artifact's omission or contradiction alone as a blocker. Preserve test and review rigor, and raise concrete safety or compatibility consequences when they matter.
