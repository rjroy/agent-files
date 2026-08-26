---
name: implement
description: Use when ready to build from a spec, design, or plan, or to resume from notes. Triggers include "implement this", "build this", "implement the spec/design/plan", "continue implementation", and "resume where we left off".
---

# Implement

Act as orchestrator. Dispatch work to sub-agents via the Task tool and record what happens. Do not write code, run tests, or review code directly. Every implementation, testing, and review action goes through a Task tool invocation. No exceptions.

## Input

Invoked as `/implement <path>` where `<path>` is a lore artifact: spec, design, plan, or notes file. Read the input artifact and any lore documents it references. If the input is a notes file, resume from where it left off.

## Output

Implemented code plus a notes file at `.lore/work/notes/<artifact-name>.md`. Load `${CLAUDE_PLUGIN_ROOT}/shared/frontmatter-schema.md` for the frontmatter fields before writing.

The notes file needs enough structure to be resumable: a progress tracker (phases with checkboxes) and a log (what happened, failures, decisions, discoveries). Update it after every phase, not just at session end.

Write the body in Markdown per the "Body Format" section of `${CLAUDE_PLUGIN_ROOT}/shared/frontmatter-schema.md`. Reach for embedded inline HTML only when a visual carries meaning prose can't, such as a color-coded phase-status diagram readable at a glance mid-session.

## Process

### 1. Initialize

Search for related prior work: invoke the `lore-researcher` subagent via Task tool with the artifact description. Wait for the result before continuing. If that custom agent is unavailable, dispatch the host's general-purpose subagent with the research role from `agents/lore-researcher.md`.

Break the input into implementable phases. If the input is a plan, phases are its steps. If a spec or design, break into independently testable chunks.

**Task file detection.** When the input is a plan, check whether `.lore/work/tasks/<plan-name>/` exists. If it does, read task files sorted by their `sequence` frontmatter field — these become the phases. Compare the plan's modification timestamp against the oldest task file. If the plan is newer, warn the user and offer three options: re-run `/plan-breakdown`, use existing tasks, or abort.

**Select agents.** Consult `.lore/lore-agents.md` if it exists. Match agents to three mandatory roles:

| Role | Registry Category | Fallback |
|------|-------------------|----------|
| Implementation | Implementation | Host general-purpose subagent |
| Testing | Testing | Host general-purpose subagent |
| Review | Code Quality | Host general-purpose subagent |

**Establish evidence.** Extract the source's obligations: requirements from a spec,
decisions and interface commitments from a design, or goals and validation from a
plan. Create a notes table mapping every obligation to its phase and executable
validation. Discover affected consumers, state transitions, and system boundaries
from the feature. An unmapped obligation is a planning gap: resolve it before
implementation.

### 2. Execute Phases

For each phase:

Only one agent may operate on a phase's files at a time. Await each result before
dispatching the next role. Testing and review agents are read-only: they return
evidence or findings and never edit files. Do not test or review a moving worktree.

**a. Implement.** Dispatch to an implementation agent via Task tool. Include: what to build, relevant file paths, context from prior phases or failures. One phase at a time — the agent does not see the full plan. Await a stable changed-file manifest before continuing.

**b. Test.** Dispatch to a testing agent via Task tool. Include: which files changed, the phase-specific validation criteria established during initialization (using the task's exact Validation section when task files exist), the mapped source obligations, and how to run the test suite. Expect back: pass/fail, commands or observations, and evidence for each criterion. The suite passing does not substitute for the phase's behavioral checks.

**c. Review.** Dispatch to a review agent via Task tool in initial-review mode. Include: which files to review, relevant requirements from the source artifact, validation evidence, and affected consumers and boundaries. Expect non-conformances only, each with a stable ID, severity, evidence, and affected surface.

**d. Handle failures.** Route failures back to an implementation agent for correction and await completion. Re-dispatch only the failed checks and a verification review with the complete unresolved finding records and correction diff. Inspect the changed surface and report any newly encountered material issue, but do not reopen unrelated accepted surfaces. After two failed attempts on one finding, or three correction rounds in a phase, escalate to the user.

**e. Record.** Update the notes file with results and evidence. Mark the phase's local gate complete only when every mapped criterion passes. Keep overall implementation status in progress until holistic validation passes.

When phases come from task files, update the task file's `status` meta to `complete` after its local gate passes. If the implementation agent reports work is already done (task file still says `pending`), validate it normally rather than skipping or asking merely because status drifted.

### 3. Validate

After all local gates pass, dispatch one terminal acceptance review with the full source artifact, obligation-to-evidence table, changed-file manifest, and named consumers. Directive: reconcile every source obligation with evidence and run cross-cutting checks that could not belong to one phase. This is the only review called "final" or "acceptance."

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
2. **Plan divergence**: Implementation requires something the source artifact didn't specify or contradicts. Present the divergence and ask the user to authorize or redirect.

Do not ask for confirmation between phases.

## Divergence

If reality requires something the source artifact didn't account for, do not proceed. Escalate to the user with the specific divergence and why it's needed. Record approved divergences in the notes file.
