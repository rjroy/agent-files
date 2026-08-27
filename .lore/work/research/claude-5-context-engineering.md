---
title: Claude 5 context engineering guidance
date: 2026-08-26
status: active
tags: [context-engineering, claude-5, agent-design, prompting]
---

# Claude 5 context engineering guidance

## Key Findings

Anthropic reports that it removed more than 80% of Claude Code's system prompt for Claude 5-generation models without a measurable loss on its coding evaluations. Its explanation is not simply that shorter prompts perform better. Newer models can make more situational judgments, while overlapping rules, examples, and repeated instructions consume context and create conflicts the model must resolve.

The recommended direction is:

- Replace blanket behavioral rules with concise statements of intent and local convention.
- Design expressive tool interfaces instead of teaching tool use primarily through examples.
- Load specialized guidance only when the task calls for it.
- Put tool-specific behavior in tool descriptions rather than repeating it globally.
- Keep repository instruction files focused on purpose and non-obvious gotchas.
- Store durable user and project knowledge in dedicated memory mechanisms rather than treating the root instruction file as a memory dump.
- Prefer high-fidelity references such as code, tests, HTML mockups, and rubrics over simplified prose descriptions when they express the target more precisely.

## Then and Now

| Earlier pattern | Recommended pattern | Reason |
|---|---|---|
| Give categorical rules | Let the model exercise judgment within stated intent and local conventions | Universal rules are wrong in valid edge cases and can conflict across context sources |
| Supply tool-use examples | Design clear, expressive interfaces and schemas | Examples can anchor exploration to the demonstrated paths |
| Put all guidance in the initial context | Use progressive disclosure through skills, references, and deferred tools | Most specialized guidance is irrelevant to most requests |
| Repeat important instructions | Put each instruction at its natural boundary | Repetition adds noise and opportunities for inconsistency |
| Use `CLAUDE.md` as memory | Use dedicated automatic memory | Root instructions should remain stable and operational |
| Reduce specs to simple Markdown prose | Use rich, executable, or directly inspectable references | Tests and code often communicate requirements with higher fidelity |

## Context Roles

Anthropic assigns different responsibilities to each context source:

- **System prompt:** Define the product, operating environment, and agent role. This deserves careful design when building an agent harness.
- **`CLAUDE.md`:** Briefly explain the repository and capture non-obvious constraints or gotchas. Do not restate facts discoverable from the repository.
- **Skills:** Provide selectively loaded, opinionated guidance specific to a person, team, product, or task. Split long skills into supporting files.
- **References:** Supply detailed task-specific truth, preferably in high-fidelity forms such as code, tests, mockups, or explicit rubrics.
- **Memory:** Retain durable facts about the user and ongoing work without expanding global operating instructions.

## Important Qualifications

The article describes empirical results from Anthropic's Claude Code evaluations, but does not publish the evaluation suite, ablations, or failure-rate details. The reported 80% reduction therefore supports experimentation, not indiscriminate deletion.

Some constraints should remain explicit: safety boundaries, irreversible-operation policy, compliance requirements, tool invariants, and genuinely unusual repository conventions. The useful distinction is not rules versus no rules. It is invariant constraints versus choices the model can infer from context.

The advice is model-dependent. A mixed-model harness may need model-specific context profiles or interfaces that remain legible to less capable models.

## Potential Application Here

This repository already uses progressive disclosure through skills, but its global instruction context contains duplicated sections, repeated Beads guidance, categorical wording, and operational details that could potentially move closer to the relevant tool or skill. A useful audit would classify every instruction as one of:

- Hard invariant that belongs globally
- Repository-specific gotcha
- Task-specific guidance that belongs in a skill
- Tool behavior that belongs in a tool description
- Durable fact that belongs in memory
- Redundant or discoverable information that can be removed

The next step should be measurement before broad simplification: select representative tasks, record baseline outcomes and instruction conflicts, simplify one layer at a time, then compare correctness, intervention rate, tool behavior, and token usage.

## Source

- Thariq Shihipar, "The new rules of context engineering for Claude 5 generation models," Claude blog, July 24, 2026: https://claude.com/blog/the-new-rules-of-context-engineering-for-claude-5-generation-models
