---
name: implement
description: Use when ready to build from the user's current request or intent, optionally informed by a spec, design, plan, or notes. Triggers include "implement this", "build this", "implement the request/intent", "continue implementation", and "resume where we left off".
---

# Implement

Act as orchestrator. Dispatch work to sub-agents with the host's subagent capability and record what happens. Do not write code, run tests, or review code directly. Every implementation, testing, and review action goes through a subagent invocation. No exceptions.

## Input

Invoke `/implement` with the user's current request, optionally pointing to an intent, plan, design, spec, or notes file for context. A plan is useful but not required. Read linked material when it helps; historical artifacts inform the work but do not authorize or veto it. When resuming from notes, use them as context and confirm the next action against the user's current direction.

## Output

Implement the requested change. Keep or update a notes file only when it helps resume substantial or interrupted work; do not create one by default. Save lore notes under `.lore/local/notes/` and follow the shared frontmatter schema. New agent-created notes start `draft`; use `approved` only after explicit user approval (including editing to approve) or when the user asks for the relevant next process step. Arbitrary edits are not approval. Mark applicable work `completed` when agent work is done; completion does not imply approval. Status tracks lifecycle, not maturity or correctness; current direction may revise approved artifacts and approval is not a veto or mandatory gate. Do not ask approval for minor transitions or every document. Before writing local output, resolve `../../scripts/ensure_local.py` from this skill's installed directory and run it with `python3 <resolved-helper-path> <explicit-project-root>`. Write only after setup succeeds; report setup failure as a blocker for local output, not a reason to fall back to `.lore/work/`. Do not run setup if no local output is useful.

## Process

### 1. Initialize

For substantial work where prior context may matter, ask the `explorer` subagent to surface relevant history. Do not delay a straightforward change for irrelevant research. If invoked, use its result as context and verify consequential claims against current code or the user.

Understand the user's requested outcome and any new evidence. Use the plan's steps when a useful plan is supplied; otherwise choose a small number of coherent phases appropriate to the work. Prefer existing capabilities and account for affected consumers, actual behavior, and relevant safety or compatibility constraints. Current user direction may authorize behavior or contract changes; do not treat an old artifact's silence, approval status, or requirements as a veto. Raise concrete safety/compatibility consequences or consequential unresolved choices, not mere historical noncompliance.

**Select agents.** Consult `.lore/lore-agents.md` if it exists. Match agents to three mandatory roles and record the reviewer selected for each phase. Honor a project-selected Code Quality reviewer and its own invocation contract; do not replace that choice merely because another reviewer is available.

| Role | Registry Category | Fallback |
|------|-------------------|----------|
| Implementation | Implementation | Host general-purpose subagent |
| Testing | Testing | Host general-purpose subagent |
| Review | Code Quality | Project-selected Code Quality reviewer; if none, the matching supported `oracle` procedure or host general-purpose reviewer |

When no project Code Quality reviewer is selected, use procedure
`bun-typescript-reviewer` with the registered `oracle` for Bun and
TypeScript changes to daemon, Unix-socket, CLI, Next.js, or React architecture.
Do not select it merely because a repository contains one incidental TypeScript
file. Use procedure `rust-daemon-cli-reviewer` with the registered
`oracle` for matching Rust daemon or CLI changes. For other stacks, retain
the host general-purpose reviewer fallback; do not invent a generic procedure.
For procedure-based correctness reviews through the `oracle` agent, include
`procedure`, `scope`, `request`, and `inputs`, and include `mode` only when
the selected procedure defines one. Standalone quality assignments follow the
host-supported agent contract and supplied quality guidance without a procedure
unless that contract actually requires one. Use the host general-purpose agent's
own contract for other-stack fallback. If a selected generic procedure is
unavailable, resolve it through the shared `agent-procedures` base rather than a
retired root prompt.

**Choose evidence.** Identify the project-specific behavior and risks that matter
to this change. Reuse adequate tests and other evidence; add focused checks for
distinct plausible defects or important safety/compatibility boundaries. The full
suite passing is not enough when it does not demonstrate the requested behavior.
Do not create requirement IDs, exhaustive mappings, or one test per step or goal.

**Own coordination.** This invocation coordinates correctness and engineering
quality; delegated writers, testers, and reviewers execute only their bounded
assignments and do not restart `implement`. Scale quality scrutiny to the work:
substantive implementation receives an independent engineering-quality assessment
after functional verification; a small, obvious change needs only a delegated
lightweight quality check, not an additional deep review.

### 2. Execute Phases

Use the phases supplied by a useful plan; the phase is the unit of scope, not
one large implementation handoff. Within each phase, make as many small,
testable-behavior cycles as useful. Prefer narrow slices with observable
behavior; do not combine separate behaviors merely to reduce agent handoffs.

Only one agent may operate on a phase's files at a time. Await each result before
dispatching the next role; never test or review a moving worktree. The
orchestrator does not write code, tests, or review code. Testing and review
agents are read-only: they return evidence or findings and never edit files.

For each testable behavior, follow this agent-run red-green cycle:

1. **Red — establish a focused failing test.** Dispatch a write-capable
   test-author agent first to inspect relevant existing tests. Reuse an adequate
   existing failing behavioral test when it validly demonstrates the missing
   behavior; otherwise have the agent write a focused behavioral test without
   implementing production behavior. A separate, read-only testing agent runs
   it and confirms RED because the requested behavior is missing. A failure from
   setup, imports, or an unrelated defect is not RED evidence: fix that
   test/setup problem or choose an adequate failing test. A test that already
   passes is not RED evidence. Do not weaken an assertion or test to manufacture
   a failure or obtain GREEN.
2. **Green — implement only what is needed.** Dispatch a production
   implementation agent with the requested outcome, relevant paths, affected
   consumers, consequential constraints or authorized behavior changes, the
   failing test and its confirmed behavior-specific failure, and useful
   prior-phase findings. Identify existing behavior to reuse, replace, or
   remove where relevant. It changes production behavior only, no speculative
   scaffolding or unrelated scope.
3. **Verify.** A separate read-only testing agent runs the focused test and
   relevant regressions, confirming GREEN and reporting commands and behavioral
   evidence. The full suite passing does not substitute for focused evidence
   when needed to prove the requested outcome.
4. **Review.** Dispatch the read-only reviewer selected during initialization in
   a fresh child invocation. If
   that reviewer is the generic `oracle`,
   select only the applicable supported procedure: `bun-typescript-reviewer` for
   matching Bun/TypeScript daemon, Unix-socket, CLI, Next.js, or React changes, or
   `rust-daemon-cli-reviewer` for matching Rust daemon/CLI changes. Its envelope
   includes that `procedure`, `scope` as the changed behavior and affected
   boundaries, `request` for material defects or risks, and `inputs` containing
   the current request, changed files/diff, relevant red/green evidence, and
   affected consumers; set `mode` to `initial-review`. For any other selected
   reviewer, follow that reviewer's own contract and pass its required context;
   do not substitute a different procedure or invent one. Review actual behavior
   and relevant invariants, not historical artifacts as authority over current
   direction. Report only concrete material defects or risks with consequences
   and bounded outcomes; preserve the selected reviewer's finding contract. Any
   correction verification or terminal review is a fresh invocation: never reuse
   or pass a prior child session. For code-reviewer procedures, verification uses
   the matching procedure, scope, request, and inputs containing the current
   request, complete unresolved finding records, changed sections, relevant
   validation evidence, and affected consumers, with `verification` mode. For
   other reviewers, follow their verification contract and include the complete
   unresolved finding records and changed sections when supported. Do not include
   author deliberation or an expected verdict. A terminal broad review, when
   called for below, is another fresh invocation of the selected reviewer using
   its broad-review contract; it does not make optional review mandatory for
   smaller work. Accept adequate work without optional hardening or ceremonial
   coverage. An obsolete parallel path or unused scaffolding is a finding only
   when evidence shows material maintenance or behavior cost, not a cleanup
   quota. A request for another test must identify a plausible defect current
   evidence would miss and the observable check needed.
5. **Assess refactoring opportunities.** Always dispatch a read-only assessment
   of the changed surface for useful behavior-preserving refactors after the
   correctness review and before the engineering-quality assessment. Looking for
   refactors is mandatory; making changes is optional. Record the disposition,
   including when no refactor is worthwhile. Route selected refactors to a
   separate writer invocation. The read-only tester reruns checks for the changed
   surface, followed by a focused read-only correction review; retain refactors
   only if behavior remains verified.
6. **Assess engineering quality.** For substantive implementation, load
   `../engineering-quality-review/SKILL.md` relative to this installed skill's
   directory and arrange an independent, read-only assessment using that guidance.
   Give the reviewer the current request, scope, agreed architecture, constraints,
   changed implementation and affected consumers, and functional verification
   evidence, without an expected verdict. Run this assessment after the mandatory
   refactoring assessment and any selected refactors; do not combine it with the
   earlier correctness review. Preserve defects-only procedures and
   project-selected reviewers in their own correctness invocations. Use an
   appropriate host-supported reviewer for the
   quality assignment; do not invent a procedure. If that reviewer cannot load the
   skill through the host's skill mechanism, provide the resolved absolute leaf
   path as task guidance for a direct read only where host permissions allow it.
   Do not imply skill-tool access or bypass a restriction; report inaccessible
   guidance to the caller.

   Keep correctness acceptance separate from disposition of quality
   recommendations and measurement hypotheses. Consider and explain dispositions
   of consequential recommendations; adequate work can be accepted without edits.
   Route selected refinements to a writer, reverify the changed surface, and obtain
   a focused read-only correction review. Preserve the existing correction limits
   and escalation for consequential unresolved architectural choices; do not
   restart broad review unless the accepted surface materially changes.

The write-capable test author may be a separate invocation of the implementation
agent or another suitable writer. Keep test-authoring, production implementation,
and optional refactor assignments explicit and separate; only the assigned
writer edits during that turn. Testing and review remain read-only.

Not every change has an executable failing-test cycle. For pure refactors, use
existing characterization/regression evidence to show behavior before and
after; do not demand an artificial RED. For non-executable changes such as
prompts, documentation, or visual work, record concrete before/after evidence
for the requested change instead of inventing a failing test. These exceptions
do not excuse skipping red-green TDD for testable code.

**Failure and correction.** Treat a failed red confirmation as a test/setup
problem unless the failure demonstrates the requested missing behavior. Route
implementation defects back through a focused test-first correction cycle; do
not skip directly to an untested patch. After changes, rerun the failed check
and relevant regression evidence, then use a read-only verification review
with the finding and correction context. Preserve stable finding IDs and the
existing limits: escalate after two failed attempts on one finding, or three
correction rounds in a phase. Do not reopen accepted unrelated surfaces.

**Record.** Share concise results and evidence with the caller. Update existing
notes when useful for resumption; do not create phase trackers or obligation
maps as ceremony.

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
