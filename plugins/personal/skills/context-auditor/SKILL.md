---
name: context-auditor
description: Audits the context assembled for modern reasoning models, including skills, agent instructions, project guidance, tools, memory, and references. Use when asked to "audit this context", "modernize these agent instructions", "reduce over-constraint", or "apply modern context-engineering practices".
---

# Context Auditor

Improve model context without weakening the constraints, knowledge, or boundaries that make the system reliable.

Load `reference/lenses.md` before producing findings or edits.

## Workflow

1. **Interpret the request.** Distinguish review-only from review-and-edit intent. Do not ask for confirmation the user has already given; ask when scope, authority, or acceptable risk is genuinely unclear.
2. **Map the active context stack.** Read the target and inspect the surrounding layers that may overlap with it: system or agent instructions available in the workspace, project guidance such as `AGENTS.md` and other files actually loaded by the host, loaded skills, tool descriptions, persistence mechanisms, and task references. Note instruction precedence and any layer that is unavailable.
3. **Classify each artifact.** Identify whether it defines product behavior, an invariant boundary, a repository gotcha, a task workflow, a tool interface, durable knowledge, transient state, or a task-specific reference. Judge it according to that role rather than treating every context file alike.
4. **Apply relevant lenses.** Use the reference selectively. Skip lenses that do not apply. For each finding, cite the passage, explain the behavioral risk, and give a concrete rewrite or relocation.
5. **Triage by impact.** Separate conflicting or harmful instructions from harmless verbosity. Preserve load-bearing constraints and intentional reinforcement. When intent is uncertain, surface the tradeoff instead of assuming that shorter is better.
6. **Report or edit according to the request.** For a review, lead with findings ordered by severity. For an explicit cleanup request, make the smallest coherent edits and call out any policy decision that still requires the user.
7. **Validate proportionally.** Re-read changed files, validate their format and discovery, and search for stale references or new conflicts. For changes likely to alter behavior, compare representative tasks or evaluations before and after when a runnable baseline exists. If behavioral validation is unavailable, state that limitation rather than treating textual cleanliness as proof.

When changing this skill itself, use `evals/cases.md` as its regression suite.
