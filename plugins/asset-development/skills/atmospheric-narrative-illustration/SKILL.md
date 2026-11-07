---
name: atmospheric-narrative-illustration
description: >-
  Apply opt-in Atmospheric Narrative Illustration art direction to briefs, prompts,
  and visual reviews: cinematic narrative-led scenes, graphic-novel linework,
  painterly environments, controlled palettes, legible silhouettes, and grounded
  surrealism. Use for splash art, concept illustrations, and game imagery when
  this style is requested or approved; not an asset-creation workflow or authorization.
---

# Atmospheric Narrative Illustration

## Purpose

Create **stylized cinematic illustrations that communicate a story at a glance**. The image should feel like a significant moment in a larger world, not merely a visually attractive collection of objects.

This is an **opt-in creative art-direction overlay**, not a fixed model preset, exact color palette, tool route, or replacement workflow. Apply it only when the user requests or approves this style for the current work. Loading this skill does not authorize image generation, modeling, production derivatives, software installation, or runtime integration. Brief and prompt drafting or visual review alone does not call for generating an image.

## Project context

Consult `<project-root>/docs/asset-direction.md` when present, including any linked project-specific production guide. Project paths resolve from the consuming project root, not this skill directory. Context describes direction, not approval of an individual asset. If absent, use the user's brief and authorized references; ask only for missing requirements that critically block the next authorized step. Do not require creating a context file.

Preserve project identity, approved characters, palettes, dimensions, and reference requirements. This style is not a universal default for the project or the user's other assets. Identify conflicts between the style, project guidance, and the task for the user rather than silently choosing. A specific user instruction takes precedence over this style guide.

## Core style definition

> Atmospheric Narrative Illustration blends graphic-novel linework, painterly environmental texture, deliberate (sometimes Art Deco–influenced) geometry, physically coherent but nonphotorealistic worlds, atmospheric depth, controlled color palettes, and selective cinematic lighting. Narrative clarity, readable silhouettes, and emotional resonance take priority over spectacle or ornament. Surreal or fantastical elements remain grounded in recognizable physical cues. Default content is PG-13, with no gore.

## Priority order

When visual requirements within this style conflict, preserve these priorities in order; they do not override the approved brief or workflow gates:

1. **Narrative clarity** — the viewer should understand the primary action, relationship, discovery, or tension.
2. **Composition and silhouettes** — the focal point must read immediately, including at reduced display size.
3. **Emotional tone** — color, posture, scale, negative space, and light should communicate the intended feeling.
4. **Physical coherence** — spatial relationships, perspective, lighting, and object interactions should make sense, even when the premise is impossible.
5. **Atmosphere and texture** — add depth and lived-in character without obscuring the story.
6. **Decorative detail** — use only where it supports the preceding goals.

## Visual language

### Composition

- Treat the scene as one frame from an unfolding narrative: imply a **before** and an **after**.
- Establish a single dominant focal point or an intentionally legible relationship between two focal points.
- Prefer strong silhouettes, controlled value grouping, and clear separation between foreground, middle ground, and background.
- Use deliberate geometry: arches, corridors, roads, platforms, repeated structures, and leading lines can organize the image.
- Art Deco geometry is an **optional compositional influence**, not a universal decorative motif.
- Preserve negative space where it helps orientation, scale, typography placement, or emotional effect.
- Use an intentional camera position and perspective; keep character placement and sightlines readable.

### Drawing and surfaces

- **Stylized, not photorealistic.** Subjects and settings should be identifiable and convincing without aiming for camera-real rendering.
- Use graphic-novel-informed linework: selective contours, visible strokes, and confident shape design.
- Integrate painterly textures into architecture, foliage, clouds, terrain, clothing, and worn surfaces.
- Let linework define structure; let painting, light, and atmosphere establish volume and mood.
- Avoid generic glossy 3D, plastic-smooth surfaces, hyperreal skin, and indiscriminate microdetail.

### Color and light

- Establish a limited, controlled palette fitted to the specific world and narrative beat.
- Use accents to direct attention, not to saturate every region.
- Prefer selective, motivated light sources: a lantern, a door, a distant window, a setting sun, an approaching threat.
- Make lighting reinforce the story and preserve legible silhouettes.
- Use atmospheric perspective, haze, mist, smoke, or layered contrast when useful, but do not conceal necessary actions.
- **Do not automatically apply the user's separate personal-brand colors.** Project-specific palettes take precedence.

### Reality and the fantastical

- Ground surreal imagery with familiar materials, plausible weight, recognizable architecture, and coherent cause/effect.
- Allow an extraordinary element to be extraordinary against an understandable environment.
- Avoid gratuitous visual chaos, unexplained floating details, or impossible anatomy that distracts from the intended premise.
- Keep tension, mystery, menace, and the uncanny possible without explicit violence or gore.

### Characters and emotion

- Prioritize readable pose, gesture, gaze, and spatial relationships over facial microexpression.
- Make the character's intention clear: guiding, resisting, searching, discovering, hesitating, fleeing, etc.
- Convey emotion through composition and action rather than exaggerated facial expressions or explanatory labels.
- Avoid irrelevant background figures or props that compete with the main narrative.

## Prompt-building guidance

When drafting a brief or prompt for an authorized image task, identify:

1. **Narrative moment:** What is happening in this exact instant? What changes next?
2. **Audience inference:** What should a viewer understand without a caption?
3. **Subject and action:** Who or what is central, and what specifically are they doing?
4. **Setting and grounding:** What recognizable materials and environmental cues make the scene credible?
5. **Composition:** Camera position, framing, subject size, visual hierarchy, leading lines, and negative space.
6. **Light and palette:** Main light source, restrained colors, contrast, and any meaningful accent.
7. **Mood:** The specific emotional register, such as curiosity, quiet awe, apprehension, resolve, or melancholy.
8. **Output constraints:** Aspect ratio, target resolution, use case, typography-safe area, transparency, or continuity with references.

Write the visual portion of the image prompt in this general order, alongside the execution skill's required delivery and verification instructions:

1. The **scene's story and primary action** in one or two sentences.
2. The **framing and composition** required to make it readable.
3. The **distinctive visual style** and material treatment.
4. The **lighting, palette, atmosphere, and mood**.
5. **Explicit constraints** and elements to avoid.

### Reusable prompt scaffold

```text
Create an Atmospheric Narrative Illustration of [specific scene and narrative moment].

Story and action: [central subject, action, relationship, and implied stakes].
Composition: [camera angle, framing, foreground/midground/background,
visual focal point, silhouette separation, directional geometry, negative space].
Environment: [recognizable physical cues, surfaces, materials, and spatial logic].
Visual treatment: stylized cinematic illustration; graphic-novel linework;
painterly environmental texture; deliberate geometric composition;
physically coherent but nonphotorealistic rendering.
Lighting and color: [motivated key light], [controlled palette], [selective accents],
[atmospheric depth without sacrificing action readability].
Mood: [intended emotion, communicated through posture, scale, space, and light].
Constraints: [aspect ratio, use case, reference fidelity, content and exclusions].
Prioritize narrative clarity, readable silhouettes, and emotional resonance.
Avoid glossy photorealism, gratuitous detail, visual clutter, and gore.
```

Adapt rather than copying the scaffold verbatim into every generation request. Concrete scene instructions usually matter more than repeated style adjectives. This scaffold supplies visual direction only; it does not select a tool, authorize execution, or replace the chosen workflow's prompt requirements.

## Continuity and editing

When editing an existing image or generating a related variant within authorized scope:

- Clearly distinguish **immutable content** (characters, objects, text, staging, meaning) from **editable presentation** (palette, shading, texture, atmosphere).
- Preserve the identity and spatial relationships of established subjects unless the request expressly changes them.
- Keep the same narrative beat even when shifting the rendering treatment.
- For a requested localized change, explicitly instruct the model to leave everything else unchanged.
- Treat exact text and reference-image fidelity as hard constraints when supplied in the approved brief.
- Preserve approved versions and submit a separate candidate for exact-version approval through the execution workflow; a style correction does not authorize overwriting approved work.

## Evaluation rubric

Inspect actual candidate images at full size **and** thumbnail size. For prompt-only reviews, assess the proposed direction and state that no image has been inspected. Ask:

- **Story:** Can a viewer state what's happening without an explanation?
- **Focus:** Is the intended subject the first thing the eye finds?
- **Action:** Can the viewer read poses, gestures, and relationships unambiguously?
- **Space:** Are scale, perspective, and the positions of subjects coherent?
- **Tone:** Does the scene convey the specified emotion without relying on a caption?
- **Style:** Are ink-like shapes and painterly atmosphere working together rather than competing?
- **Restraint:** Is anything flashy, decorative, or over-detailed at the expense of meaning?
- **Content:** Does the image stay within the PG-13 / no-gore default or the user's explicitly requested permissible content constraints?

If a check fails, identify the specific visual cause (e.g., staging, contrast, perspective, light position) rather than simply asking for “more cinematic” or “more atmospheric.” Propose a focused correction; execute revisions only within the authorized scope and iteration rules. Passing this rubric is review evidence, not user approval or technical verification.

## Frequent failure modes and corrections

| Failure | Corrective direction |
| --- | --- |
| Beautiful but unclear scene | Simplify the number of subjects and explicitly describe the primary action and focal relationship. |
| Characters blend into scenery | Strengthen silhouette separation, change value contrast, or simplify adjacent shapes. |
| Excessive haze obscures story | Confine haze to depth layers; preserve local contrast around the subject. |
| Surreal elements feel arbitrary | Add familiar scale references, physical support, and plausible environmental responses. |
| Generic fantasy concept-art look | Emphasize specific narrative staging, ink-like contours, and restrained environmental painting. |
| Too photorealistic / glossy | Specify stylized drawing, visible texture, simplified shapes, and no photoreal finish. |
| Ornate Art Deco overwhelms scene | Use geometry as a compositional tool, not decoration. |
| Correct style, wrong action | Make the intended gesture, distance, facing, and line of sight explicit. |
| Too many competing colors | Limit the palette and reserve the strongest accent for the focal point. |

## Scope and boundaries

- The style can span fantasy, science fiction, grounded contemporary scenes, and the uncanny.
- It is **not** inherently dark, dystopian, medieval, or Art Deco; those are scene-specific choices.
- It is **not** synonymous with any particular game, project, mascot, or personal-brand identity.
- It does **not** mandate a fixed aspect ratio, palette, character, lantern, arch, or setting.
- Default to PG-13 storytelling and no gore, unless the user explicitly requests different permissible content.

## Example: applying the style

```text
A lone traveler stands beneath a weathered stone arch at the edge of a
flooded railway platform. Beyond the arch, a train approaches through blue
mist; its windows emit a restrained amber glow. The traveler has just
noticed someone waiting at the opposite end of the platform.

Three-quarter-wide composition, human silhouettes legible, arch and tracks
leading the eye toward the distant figure. Physically coherent perspective,
wet stone reflections, convincing weight and scale. Stylized cinematic
illustration, graphic-novel linework and painterly environmental surfaces.
Controlled slate-blue and warm-amber palette, selective motivated lighting,
layered atmospheric depth. Mood of discovery and unease, not horror.
The narrative encounter must be readable at thumbnail size. No gore,
photoreal gloss, excessive ornament, or distracting extra figures.
```

## Relationship to execution skills

- [asset-workflow](../asset-workflow/SKILL.md) owns the brief, branch choice, authorization, approval gates, source preservation, and handoff. Use this overlay to inform visual direction, not replace that workflow. Description approval, exact-version concept/artwork approval, model approval, derivative review, integration authorization, and runtime acceptance remain distinct; style selection or a passing review grants none of them.
- [concept-art](../concept-art/SKILL.md) owns exploratory concept generation and verified exact-version review. [asset-art](../asset-art/SKILL.md) owns production 2D artwork, agreed SVG/raster mode, technical verification, and exact-version artwork approval. Both require their approved brief and task-specific authorization and use the authorized Codex route. This overlay does not supply an alternative route; a concept is not production art.
- [blender-model](../blender-model/SKILL.md) owns separately authorized model construction/revision. An approved illustration may guide composition, silhouette, and mood; it grants no modeling permission and is not a pixel-matching contract unless explicitly requested. Do not turn painterly texture, haze, or presentation effects into geometry requirements without an approved reason.
- [blender-visualize](../blender-visualize/SKILL.md) owns authorized read-only rendering and inspection of actual saved geometry. Preserve neutral/restrained diagnostic views; do not beautify or hide defects to satisfy this style. Separate observed shape issues from lighting/material presentation, and do not replace model-render evidence with generated imagery. A render is not model approval or consumer-fidelity proof.
- [asset-production](../asset-production/SKILL.md) owns separately authorized derivatives from accepted sources. Neither this overlay nor an attractive source image authorizes export, optimization, integration, or runtime acceptance. Verify appearance in the actual consumer under the separately authorized workflow.
