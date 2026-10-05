---
name: specify
description: This skill should be used when the user wants to define the requirements of a feature or project. Produces numbered requirements and validation criteria. Triggers include "write a spec for", "define the requirements", "what should this do", "capture the requirements".
---

# Specify

Define what to build and how to know it's done. Write first for the person who must
decide whether the behavior is right, then add the contract an agent needs to build
it. Not how to build it; that is the plan.

## Process

Search for related prior work: invoke the `lore-researcher` subagent with the host's subagent capability with the topic description and wait for the result. If unavailable, dispatch the host's general-purpose subagent with the research role from `agents/lore-researcher.md`. Review relevant lore context. Ask clarifying questions. Draft. Save. Then run a fresh-eyes review.

After saving, invoke the `spec-reviewer` subagent with the host's subagent capability in initial-review mode on the saved spec. If unavailable, dispatch the host's general-purpose subagent with the role from `agents/spec-reviewer.md`. If findings are corrected, invoke verification mode with the complete unresolved finding records and changed sections. After those findings close, run one terminal broad acceptance review. Corrections from that review receive targeted verification with their complete finding records; do not run another broad review unless accepted scope changed.

## Document Order

Use this default reading order unless the feature clearly needs another:

1. Goal and user problem
2. Two or three representative user-visible examples
3. Plain-language explanation of any model, benchmark, or core rule
4. Visible behavior and important product choices
5. Special cases and scope boundaries
6. Numbered requirements
7. AI Validation
8. Optional Technical Contract

Keep implementation detail in the Technical Contract rather than forcing readers
through it to understand the feature. Requirements should state observable outcomes,
not repeat contract prose. Avoid legalistic repetition and repeated "shall" wording.

When scope boundaries matter, distinguish behavior the feature preserves from
behavior it replaces or retires. Do not prescribe new artifacts, checklists, or
infrastructure unless the goal requires them; keep unrelated cleanup and
unapproved contract retirement out of scope.

**Requirement readability:** Every numbered requirement must stand on its own, or explicitly name the prior requirement, contract, or authority it depends on and state the observable consequence. Approval, governance, and document status are context, not product requirements.

## Requirements

Number requirements with a namespaced prefix to avoid collisions across specs: `REQ-{PREFIX}-N`

Derive the prefix from the spec filename — take the first 1-2 segments of the kebab-case name, uppercase. `auth-flow.md` → `REQ-AUTH-FLOW`. `checkout.md` → `REQ-CHECKOUT`. Override with a `req-prefix` frontmatter field when the auto-generated prefix is awkward or shorter IDs are preferred.

## Validation

Every spec needs an AI Validation section. It answers: how will the AI verify this is done? It must be behavioral and actionable — something the AI can run or observe. When in doubt, invoke `/define-validation` to work through it.

## Saving

Save to `.lore/work/specs/[feature-name].md` using kebab-case. Load `../../shared/frontmatter-schema.md (resolved from this skill's base directory)` for the frontmatter fields. Adapt the default order when useful, but preserve its human-first progression. Requirements must be numbered and validation explicit.

Write the body Markdown-first per the "Body Format" section of `../../shared/frontmatter-schema.md (resolved from this skill's base directory)`. Reach for embedded inline HTML only where scannability needs it — per-requirement status badges and anchor links per requirement ID so cross-references work.
