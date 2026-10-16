---
name: blender-model
description: Build or revise an editable Blender asset and reproducible scripts from an approved brief or concept, only after explicit modeling authorization.
---

# Blender model craft

Read [asset-workflow](../asset-workflow/SKILL.md) first. This skill owns construction/revision of the native Blender model; workflow owns approvals, iteration, provenance, export, and acceptance. Skill authoring does not authorize asset creation.

## Gate and inputs

- Start only with explicit modeling authorization identifying approved brief/concept, scope, output location, expected consumer and source if revising. Mood imagery or general direction is not authorization.
- Consult project context/references as relevant, but do not treat project direction as universal style or approval. Ask about material ambiguity rather than promoting guesses.
- Record references, source, output, consumer, Blender version and uncertainties in concise README/handoff; separate manifest is optional. Model only approved scope; ask before a new focal feature, direction change, or asset-count expansion.

## Build for shape

Plan at game/consumer distance: dominant silhouette, proportion landmarks, negative spaces and form hierarchy. Check multiple views and intended camera before details; block out, compare to approved evidence, refine.

- Build coherent forms with deliberate mesh flow/topology where silhouette or deformation warrants. Use curves for continuous paths; control bevels, endpoints and joins. Apply bevels, weighted normals, subdivision and supporting loops selectively; document modifier choices for target pipeline.
- Primitives are useful starting stock, not a finished design language. Avoid uniform disconnected blunt primitives; intentionally shape transitions, taper, joints, overlap, contours and scale. Join/intersect where the design calls for unified mass; separate only where it reads as a designed component.
- Inspect topology, normals, smoothing boundaries, inappropriate open/non-manifold edges, self-intersections, thin surfaces and shading artifacts. Prefer economical geometry; avoid hidden detail with no intended-view benefit.
- Preserve meaningful material assignment/separation and export structure. Keep procedural nodes understandable; do not assume Blender shaders map identically to glTF/consumer. Model renders are geometry evidence, not final material presentation. Avoid relying on color alone for gameplay meaning.
- Give names, collections, origins, scale, transforms, units and orientation purpose; separate logical editable parts, not incidental faces.

## Editable source and reproducibility

- Maintain current editable `.blend`, its generator, and only reusable validation/preview scripts. Scripts are reproducible source for generated geometry/materials. Avoid duplicate history, manifests and run logs.
- Prefer deterministic, relocatable scripts: fixed names/settings; no reliance on selection/UI state, session-specific temp inputs or external downloads. Do not add dependencies or third-party 3D generators. Verify regeneration from packaged source before claiming reproducible.
- If manual sculpting/editing is necessary, preserve script-built base and record exactly what is manual and not reproducible.
- Never overwrite approved/current source during iteration. Build candidate separately, retain prior source, then promote after explicit model approval and record revision/history. Use stable package paths and authorized archive rather than permanent numbered folders. Use absolute paths in commands but relocatable package layout in scripts.
- Reopen saved file in background mode or otherwise verify load; confirm expected objects/materials/bounds and record real process exit status. Do not claim success after exception/timeout.

## Export, safety and handoff

- Keep `.blend` authoritative. Export GLB/glTF only when specifically authorized for evaluation/delivery. Inspect installed exporter options rather than guessing flags; use explicit selection, modifier/material/transform settings for consumer.
- Verify orientation, scale, origin and normals after export in intended consumer. Check supported materials, textures, transparency and emissive behavior. An attractive Blender render does not prove consumer appearance; Cycles is not the runtime renderer.
- Report stable source/generator/concept/export paths, measured bounds/scale, useful object counts, tool/version, assumptions, technical caveats and approval status. Keep logs/intermediates outside package unless needed to explain failure or substantiate approval.
- Use Blender background Python for scripted work with bounded timeout; capture stdout/stderr and actual exit code. On failure/timeout, report it, preserve partial outputs for diagnosis, inspect paths before cleanup; clean only specific temporary files/processes started. Never blanket-kill processes. Diagnose before retrying; existing/partial output is not success.
- Before execution, verify authorization and absolute input/output paths; state reads/writes; ensure new revision cannot replace source; confirm deterministic settings, no unapproved generation, checks and timeout/recovery. If any fails, stop and request direction.
- Model approval is explicit. No runtime integration or accepted-asset claim without it. Post-acceptance derivatives use [asset-production](../asset-production/SKILL.md) and require separate authorization.
