---
name: engineering-quality-review
description: Assess the engineering quality of a bounded software implementation independently and read-only, with proportionate, evidence-backed recommendations.
---

# Engineering Quality Review

Assess whether a software implementation is a good engineering solution under the actual request and constraints, not merely whether it works. This is a read-only review: inspect and report; do not edit files, implement refinements, or delegate the review. It does not replace correctness review or the ownership of visual direction and UI design by a visual specialist.

## Assignment and access

The caller supplies the current request and agreed architecture, review scope and affected consumers or boundaries, implementation and relevant changes, constraints, and available functional verification evidence. Ask for missing information when it is necessary to make a consequential judgment; state remaining uncertainty rather than inventing evidence. Do not accept an expected verdict as evidence.

Load this skill through the host's supported skill mechanism when available. When it is not available to the selected reviewer, the caller may instead explicitly assign this review and supply the exact path `plugins/lore-development/skills/engineering-quality-review/SKILL.md` within the repository. The reviewer may read that file as task guidance only if the host permits the read. This is not an invented agent procedure, a grant of skill-tool access, or permission to bypass host restrictions. If the guidance cannot be accessed, report the limitation to the caller.

## Assessment

Scale the depth to the change: a small, obvious change needs lightweight scrutiny; complex architecture, cross-boundary behavior, or performance-sensitive work can warrant deeper investigation. Read the changed implementation and enough adjacent behavior, tests, and consumers to support your conclusions. Stay within the assigned scope.

Apply relevant lenses, not a checklist or finding quota:

- **Problem and approach:** Does the solution address the actual problem and fit the agreed architecture and existing capabilities?
- **Maintainability and complexity:** Are responsibilities and dependencies understandable? Is there duplication, indirection, or machinery with a concrete cost that can be removed without losing required capability?
- **Efficiency and performance:** Are operations, allocations, queries, dependencies, or boundary crossings unnecessarily costly? Distinguish observed impact from a plausible but unmeasured bottleneck.
- **Alternatives and trade-offs:** Would a bounded alternative produce enough benefit to justify its implementation cost, risk, and effects on required behavior?

## Findings and stopping

Distinguish material correctness, safety, or compatibility defects from non-blocking engineering-quality recommendations and measurement hypotheses. For each material defect, identify the evidence, consequence, and bounded outcome needed. For each recommendation, identify the observed cost and supporting evidence, a bounded alternative, expected benefit, and relevant costs and trade-offs. For a performance hypothesis, say what is known and unknown and suggest a focused measurement rather than asserting an unmeasured impact.

Recommendations are not automatic blockers or authorization to edit. The caller decides which worthwhile improvements to route to a writer and arranges verification and focused review of corrections. If a proposed alternative would depart from the agreed architecture or depends on a consequential unresolved choice, raise the decision to the caller before any such change; do not make it yourself.

Accept an adequate solution when no worthwhile refinement is supported. Do not manufacture findings, demand speculative future-proofing, turn style preferences into defects, or force edits. Return a concise assessment with evidence and uncertainties, and stop once the bounded scope is assessed. Do not claim that review proves behavior or performance beyond the evidence supplied or inspected.
