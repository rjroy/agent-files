---
name: asset-workflow
description: Coordinate authorized visual-asset work through concept exploration, production 2D art or Blender modeling, derivatives, real-consumer integration, and separate approvals.
---

# Asset workflow

The user is the visual director; the agent owns the brief, execution, evidence, and handoff. These instructions describe how to execute work and do not themselves authorize concept generation, modeling, production derivatives, integration, or asset creation. Obtain task authorization and preserve every approval boundary.

## Context and approvals

Consult `<project-root>/docs/asset-direction.md` when present; it may link to a project-specific guide. Direction is not approval for an individual asset. If absent, rely on the user brief and authorized references. Ask only for missing decisions that block the next authorized step; do not require a context file.

Never collapse or infer these gates:

1. **Description approval:** write a concise brief; obtain explicit approval of purpose, silhouette, style, readability, intended consumer, and constraints. A general request is not approval of a proposed description.
2. **Choose a branch:** exploratory imagery uses [concept-art](../concept-art/SKILL.md), requiring exact-version concept approval before Blender modeling. Production 2D art uses [asset-art](../asset-art/SKILL.md), requiring separately authorized generation and exact-version artwork approval. A concept is not production art; a brief and this skill authorize neither.
3. **Model and critique:** use [blender-model](../blender-model/SKILL.md) and [blender-visualize](../blender-visualize/SKILL.md) for reproducible previews of actual geometry. Inspect evidence. Assess silhouette, proportion, construction, detail, topology, and visible geometry flaws in neutral/restrained views. Presentation differences (lighting, emission, bloom, exposure, tone mapping, reflections, final materials) alone do not block geometry approval or trigger geometry changes; preserve meaningful material separation and report caveats. Final appearance is evaluated separately in the consumer. Iterate in bounded batches; if geometry stops materially improving, pause with evidence. Obtain explicit model approval; concept approval is not model approval.
4. **Integration and acceptance:** only after the relevant approved source, integrate into the actual runtime under separate authorization. Verify in the actual consumer and obtain separate explicit runtime acceptance. Screenshots or successful checks do not imply acceptance.

After model acceptance, use [asset-production](../asset-production/SKILL.md) for explicitly authorized production derivatives and their review before promotion. Production authorization is not integration authorization. The 2D branch similarly keeps artwork, derivatives, integration, and acceptance separate.

Pilot approval plus explicit authorization for a defined remainder permits parallel independent work where practical and one combined end review; do not interrupt for redundant approvals inside that scope. Pause for new scope, material/design decisions, or blockers. If approval is withheld, return to the relevant gate and reset approvals proportionally. Preserve approved versions and decision history. Silence, renders, broad requests, and checks are not approval.

## Routing and maintained handoff

Visual direction belongs to the user/designer. Use only available specialists and tools authorized for the task; unavailable route/model is a blocker to report, not permission to silently substitute another visual specialist. Keep the maintained package stable and relocatable: approved editable/master source, current deterministic generator, only reusable validation/preview scripts, approved brief/concept as relevant, and concise README. Record provenance/permissions, distinct approval states and revision history, versions and reproduction steps, orientation/scale, measured bounds, expected consumer and known limitations. Mark pending outputs candidates. Stable filenames are preferred; permanent numbered iteration directories are not required.

Never overwrite the approved/current source during active iteration: work on a temporary copy and preserve the prior version until the replacement is regenerated and checked. Keep production exports separate from authoring sources; create only within authorized derivative/export work and integrate only under separate authorization. Archive useful earlier versions/evidence where appropriate; do not accumulate every log, failed attempt, render, duplicate script, or regenerated copy. Before cleanup, verify durable approved evidence, provenance, final outputs and regeneration; remove only specifically authorized scratch/superseded files. Keep native image staging until durable copy and provenance are verified.

Choose Git, LFS, or external storage according to project policy; explain size and backup consequences. Do not categorically exclude binaries, install LFS, or commit without authorization. Verify regeneration from packaged sources before claiming reproducibility. Do not invent polygon, texture, draw-call, memory, or performance budgets; mark unknowns unknown. Preserve separate description, concept/artwork, model, derivative, integration, and runtime-acceptance decisions.
