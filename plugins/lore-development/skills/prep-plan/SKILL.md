---
name: prep-plan
description: Use when ready to build a reviewable implementation plan as a lore artifact. Input can be a spec, design, brainstorm, research, or a well-defined prompt. Triggers include "prep plan", "prepare a plan", "plan this", "make a plan", "plan the implementation", and "break this into steps".
---

# Prep Plan

Build an implementation plan the user can review and approve before any code is written. The plan is the output. Implementation is a separate step via `/implement`.

**Do not use `EnterPlanMode`.** This skill authors a document, not a precursor to immediate code changes.

## Process

**Gather context.** Invoke the `lore-researcher` subagent with the host's subagent capability with the topic description and wait for the result. If unavailable, dispatch the host's general-purpose subagent with the research role from `agents/lore-researcher.md`. Read relevant lore artifacts (spec, design, brainstorm, research). Explore the codebase with the host's exploration subagent to understand what exists and where changes will land.

**Surface gaps before drafting.** If the input has ambiguous requirements, contradictions, or unstated assumptions that would force guesses, list them and ask the user to resolve them first. A plan built on unreviewed assumptions fails during implementation.

**Draft collaboratively.** Plan the smallest coherent end state using existing capabilities where they fit. Name the affected surfaces and, where relevant, what is reused, replaced, deleted, or intentionally retired; preserve unapproved contracts and leave unrelated cleanup out of scope. Map the goal or requirements to concrete implementation steps and proportionate executable evidence. Reuse sufficient existing tests or evidence; add checks for distinct plausible defects, not one new test per requirement, task, or layer. Order steps by dependency and flag specialized expertise where it materially matters. Include cross-cutting validation and evidence reconciliation without creating a new phase when existing steps can cover them.

**Save.** The saved file is the review vehicle — don't present the plan in chat before saving.

**Fresh-eyes review.** After saving, invoke the `plan-reviewer` subagent with the host's subagent capability in initial-review mode on the saved plan. If unavailable, dispatch the host's general-purpose subagent with the role from `agents/plan-reviewer.md`. If findings are corrected, invoke verification mode with the complete unresolved finding records and changed sections. After those findings close, run one terminal broad acceptance review. Corrections from that review receive targeted verification with their complete finding records; do not run another broad review unless accepted scope changed.

## Saving

Save to `.lore/work/plans/[feature-name].md` using kebab-case. Load `../../shared/frontmatter-schema.md (resolved from this skill's base directory)` for the frontmatter fields. The document body is freeform — what matters is that steps are concrete (files, functions, changes) and the source artifact or goal is clearly referenced so validation has something to check against.

Write the body Markdown-first per the "Body Format" section of `../../shared/frontmatter-schema.md (resolved from this skill's base directory)`. Reach for embedded inline HTML when the step flow needs it — a visual step sequence with dependency indicators, and validation gates distinguished visually from the step description.
