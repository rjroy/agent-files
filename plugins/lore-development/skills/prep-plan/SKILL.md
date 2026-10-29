---
name: prep-plan
description: Use when the user asks to plan work before implementation, including "make a plan", "plan this", "prepare a plan", "prep plan", "plan the implementation", or "break this into steps". Develop the implementation approach, scope, sequencing, dependencies, trade-offs, and appropriate validation with the user; optionally save a working plan. Start from the current request, intent, design, brainstorm, or research. This is the primary skill for implementation-planning requests, not verification-planning, which focuses on how to verify a change.
---

# Prep Plan

Think through how to make the user's present what and why real. Discuss the approach and meaningful evidence with the user before execution; revise when repository facts or other evidence change the picture. A written plan is optional working context for `/implement`, not a contract. This skill does not add an approval requirement.

**Do not use `EnterPlanMode`.** This skill discusses an approach; it need not produce a document or start code changes.

## Process

**Understand the work.** Start from the user's current request and clarify the intended outcome and motivation. When an intent is supplied, check the proposed plan against its stated problem, outcomes, examples, and preserve/change boundaries. Identify material omissions, conflicts, or departures and discuss them with the user; the current user direction prevails, and a material departure from an intent should be surfaced rather than silently assumed. Do not make the intent an exhaustive checklist or demand a coverage matrix. Use the `explorer` or code-exploration agents when they help; inspect relevant code and tests as needed to understand existing behavior, likely change surfaces, and constraints. Treat brainstorms, designs, research, old specs, and plans as suggestions or historical context, not instructions that override current direction. Surface concrete safety or compatibility consequences when relevant.

**Explore uncertainty.** Identify assumptions or unanswered questions that could materially change the approach. Discuss meaningful options with the user and use repository evidence to narrow or revise them. Ask for a decision where the user's direction does not resolve an important choice; do not turn every open detail into a blocker or require all uncertainty to be eliminated before planning.

**Discuss the approach.** Sketch a coherent path using existing capabilities where they fit. Name affected surfaces and useful sequencing, dependencies, compatibility concerns, and meaningful project-specific validation or review. Keep scope proportionate; tests or other evidence may support several parts of the work, and do not need a one-to-one mapping to goals or artifacts. Revise the approach when code, tests, or discussion reveal a better path. Avoid exhaustive obligation maps, coverage matrices, and ceremonial reconciliation.

**Record if useful.** If a written plan will help the work, save concise, disposable context after discussing the approach. Do not require a particular template or mandatory sections. The user can proceed, revise, or set the plan aside; it does not lock implementation choices or supersede current direction. Plans and notes are not promoted to reference material.

**Fresh-eyes review.** When an independent review would materially improve the plan, invoke the registered `oracle` agent with this request envelope: `procedure` `plan-reviewer`; `scope` the plan; `request` an independent review of feasibility and fit to current direction; `inputs` the plan path and relevant context; `mode` `initial-review`. Use a fresh invocation for each review. If the agent is unavailable, resolve that procedure through the shared `agent-procedures` base; do not load a retired root prompt directly. Address material findings in proportion to the work; do not repeat broad review or require review ceremony for its own sake. A review cannot make historical artifacts binding or reject a plan only because it departs from them.

## Saving

If useful, save to `.lore/local/plans/[feature-name].md` using kebab-case. Before creating any local output, resolve `../../scripts/ensure_local.py` from this skill's installed directory (not the project cwd or a global path), then run it with `python3 <resolved-helper-path> <explicit-project-root>`. Write only after setup succeeds; report setup failure as a blocker for local output rather than falling back to `.lore/work/`. This is required only when writing local output, not for discussing a plan. Load `../../shared/frontmatter-schema.md` (resolved from this skill's base directory) for common frontmatter fields. New documents start `draft`; use `approved` only for explicit user approval (including editing to approve) or a request for the relevant next process step, never infer it from arbitrary edits. Use `completed` when applicable agent work is done, independently of approval; use `archived` when archived. Status tracks lifecycle, not maturity/correctness. Current user direction may revise approved artifacts; approval is not a veto or mandatory gate. Don't ask approval for minor transitions or every document. Keep enough concrete sequencing and evidence planning to help implementation without exhaustive traceability tables. Treat the file as temporary working context: new user direction and evidence can change the approach, and the plan is not promoted to reference.

Write the body in Markdown. Use a diagram only when it makes meaningful dependencies or trade-offs easier to discuss.
