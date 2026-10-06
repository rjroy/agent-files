---
name: prep-plan
description: Use to think through an implementation approach with the user, discuss useful evidence, and optionally record a working plan. Input can be conversational intent, design, brainstorm, research, or a prompt. Triggers include "prep plan", "prepare a plan", "plan this", "make a plan", "plan the implementation", and "break this into steps".
---

# Prep Plan

Think through how to make the user's present what and why real. Discuss the approach and meaningful evidence with the user before execution; revise when repository facts or other evidence change the picture. A written plan is optional working context for `/implement`, not a contract. This skill does not add an approval requirement.

**Do not use `EnterPlanMode`.** This skill discusses an approach; it need not produce a document or start code changes.

## Process

**Understand the work.** Start from the user's current request and clarify the intended outcome and motivation. Use the `lore-researcher` or code-exploration agents when they help; inspect relevant code and tests as needed to understand existing behavior, likely change surfaces, and constraints. Treat intents, designs, brainstorms, research, old specs, and plans as suggestions or historical context, not instructions that override current direction. Surface concrete safety or compatibility consequences when relevant.

**Explore uncertainty.** Identify assumptions or unanswered questions that could materially change the approach. Discuss meaningful options with the user and use repository evidence to narrow or revise them. Ask for a decision where the user's direction does not resolve an important choice; do not turn every open detail into a blocker or require all uncertainty to be eliminated before planning.

**Discuss the approach.** Sketch a coherent path using existing capabilities where they fit. Name affected surfaces and useful sequencing, dependencies, compatibility concerns, and meaningful project-specific validation or review. Keep scope proportionate; tests or other evidence may support several parts of the work, and do not need a one-to-one mapping to goals or artifacts. Revise the approach when code, tests, or discussion reveal a better path. Avoid exhaustive obligation maps, coverage matrices, and ceremonial reconciliation.

**Record if useful.** If a written plan will help the work, save concise, disposable context after discussing the approach. Do not require a particular template or mandatory sections. The user can proceed, revise, or set the plan aside; it does not lock implementation choices or supersede current direction. Plans and notes are not promoted to reference material.

**Fresh-eyes review.** When an independent review would materially improve the plan, use the `plan-reviewer` in initial-review mode. If unavailable, use a general-purpose reviewer with the role from `agents/plan-reviewer.md`. Address material findings in proportion to the work; do not repeat broad review or require review ceremony for its own sake. A review cannot make historical artifacts binding or reject a plan only because it departs from them.

## Saving

If useful, save to `.lore/local/plans/[feature-name].md` using kebab-case. Before creating any local output, resolve `../../scripts/ensure_local.py` from this skill's installed directory (not the project cwd or a global path), then run it with `python3 <resolved-helper-path> <explicit-project-root>`. Write only after setup succeeds; report setup failure as a blocker for local output rather than falling back to `.lore/work/`. This is required only when writing local output, not for discussing a plan. Load `../../shared/frontmatter-schema.md` (resolved from this skill's base directory) for common frontmatter fields. Keep enough concrete sequencing and evidence planning to help implementation without exhaustive traceability tables. Treat the file as temporary working context: new user direction and evidence can change the approach, and the plan is not promoted to reference.

Write the body in Markdown. Use a diagram only when it makes meaningful dependencies or trade-offs easier to discuss.
