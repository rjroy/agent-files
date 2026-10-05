---
name: plan-breakdown
description: Use when a plan exists and needs validation gates added to each step before implementation begins. Produces task files that implement can consume. Triggers include "break down this plan", "add validation to the plan steps", "plan-breakdown", and "gate this plan".
---

# Plan Breakdown

A plan describes what to build. This skill adds what's missing: how do you know each step is done?

Invoke when a plan is complex enough that explicit validation at each step matters before handing off to implement. Simple plans don't need it — implement can work from the plan directly.

## Input

Invoked as `/plan-breakdown <path>` where `<path>` is a plan in `.lore/work/plans/`. Read the plan and any spec it references.

## What to Add

For each plan step, define:
- **What**: concrete enough that an agent reading the task and compact whole-change context knows what to build; carry forward relevant reuse, replacement, deletion, intentional retirement, and retained-contract decisions
- **Validation**: proportionate evidence, not "run the tests" — name observable criteria such as "the CLI outputs X when called with Y". Reuse sufficient existing tests/evidence and add checks for distinct plausible defects; do not require one new test per requirement, task, or layer
- **Why**: the requirement or goal this step satisfies, with a reference back to the source
- **Files**: affected files (guidance, not a constraint)

Map source obligations to tasks and sufficient executable evidence before saving.
Discover affected consumers, state transitions, and system boundaries. Use realistic
interfaces and persistence where mocks could hide behavior. Consolidate redundant
checks and remove tests solely protecting behavior explicitly approved for retirement;
do not impose LOC, test-count, or coverage quotas.

Split a step only when it bundles genuinely different concerns with different validation needs. Resist over-decomposition — the value is the validation gates, not artificial granularity.

Save the task list. The saved files are the review vehicle.

If the project mirrors tasks into an external tracker, list and reconcile existing
children before creating any. Reuse tasks by source plan and step identity. Inspect
the tracker's hierarchy and dependency propagation before adding edges, never make a
parent depend on its own descendant to represent completion, and verify ready and
blocked state after mutation.

## Output

Save task files to `.lore/work/tasks/<plan-name>/NNN-<task-name>.md`. Load `../../shared/frontmatter-schema.md (resolved from this skill's base directory)` for the frontmatter fields. Set `status: pending` and include a `sequence` frontmatter field for ordering.

Each task file body: What, Validation, Why, Files sections.

Write the body in Markdown per the "Body Format" section of `../../shared/frontmatter-schema.md (resolved from this skill's base directory)`. Reach for embedded inline HTML only when a visual carries meaning prose can't, such as a color-coded status badge or a diagram a reviewing agent needs at a glance.

Stop here. The user invokes `/implement` when ready.
