---
name: intent
description: Use when the user wants to establish the present direction for what to build and why. Produces substantive, revisable intent for planning, not immutable governance. Triggers include "help me shape this idea", "what should we build", or "capture the intent".
---

# Intent

Work with the user to establish the present direction: the problem they want to
address, why it matters, and what a useful outcome means. The conversation is a
means to understand and refine that direction, not material to transcribe. Save a
clear, substantive account that a planner can use without replaying the
conversation. Choose a structure that fits the task rather than filling a fixed
template. As useful, include:

- The user's problem and motivation, with enough context to understand why now.
- Concrete, inspectable outcomes in substance (for example, which user-visible
  behavior should change and what the user should be able to do afterward).
- Clarifying examples, including representative cases or contrasts that make
  ambiguous terms concrete.
- What should be preserved and what should change, including meaningful scope or
  compatibility boundaries.
- Which direction is settled and which choices remain open; do not present
  tentative options as decisions.
- What success means to the user. Detailed implementation steps and executable
  validation design belong in planning.

These outcomes can express requirements in plain language, but are not immutable
governance. Do not add requirement IDs or force an acceptance matrix or
implementation-level validation section. An intent is useful historical context
for planning, not a veto over later user direction.

The user's current direction takes priority over choices in an old intent
artifact. When understanding changes, revise the intent rather than preserving an
outdated account; surface and explain material departures from its recorded
direction. Do not turn revisions into automatic approval gates. Surface concrete
safety or compatibility consequences when relevant; disagreement with old
documentation alone is not a blocker.

## Process

Search for related prior work: invoke the `lore-researcher` subagent with the host's subagent capability with the topic description and wait for the result. If unavailable, dispatch the host's general-purpose subagent with the research role from `../../../../omo-slim-agents/lore-researcher.md` (resolved from this skill's base directory). Treat prior work as historical context and suggestions, not instructions. Ask clarifying questions to understand the user's problem, intended outcomes, examples, boundaries, and open choices. Summarize the resulting direction in a clear, proportionate record; do not reproduce the conversation. Save it and invite correction where useful, without making a fresh-eyes intent review or approval gate mandatory.

## Saving

Save to `.lore/work/intents/[topic].md` using a short kebab-case name. Load `../../shared/frontmatter-schema.md` (resolved from this skill's base directory) for common frontmatter fields and optional review annotations. Do not add empty annotation fields to a new intent. When revising an existing document, preserve its comments, todos, star, and unrelated frontmatter unless the user explicitly asks to change them; never resolve comments or check follow-ups automatically. Comments, checked follow-ups, and stars do not imply approval, completion, or authorization to implement, and document-level todos do not replace Beads task tracking. New documents start `draft`; use `approved` only for explicit user approval (including editing to approve) or a request for the relevant next process step, never infer it from arbitrary edits. Use `completed` when applicable agent work is done, independently of approval; use `archived` when archived. Status tracks lifecycle, not maturity/correctness. Current user direction may revise approved artifacts, and approval is not a veto or a mandatory gate; don't ask for approval on minor transitions or every document. Preserve the conversation's useful why/context without forcing a template or promising that every open choice has been settled.

Write the body in Markdown. Do not rewrite old spec archives as part of creating an intent; old specs may be discovered as historical context, but their status, numbering, and validation sections do not make them binding.
