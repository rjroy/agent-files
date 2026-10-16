---
name: blender-visualize
description: Render and inspect an authorized saved Blender project for visual critique without modifying its source model.
---

# Blender visualization and inspection

Read [asset-workflow](../asset-workflow/SKILL.md) first. This skill renders existing saved `.blend` for inspection; it does not build/revise the model, alter its source, or approve it.

## Gate and render set

- Render only with authorization identifying exact saved `.blend`, approved brief/concept, comparison camera/composition, diagnostic angles, output directory and review purpose.
- Use absolute source path and record modification time or checksum before rendering. Source is read-only: do not save, pack, relink, alter materials/geometry/cameras or resave as a side effect.
- Ask for missing camera, lens, scale or composition requirements; references are evidence, not ground truth. Keep project direction separate from reusable visualization practice.
- Use approved comparison view and neutral/restrained lighting for model review. Render reproducible previews of actual geometry, not final product or runtime-fidelity proof. Inspect/present actual images. Assess silhouette, proportions, construction, detail, topology and geometry defects. Lighting, emission, bloom, exposure, tone mapping, reflections or final material alone must not trigger geometry revisions or block model approval. Preserve material separation and report appearance caveats; final appearance is assessed separately in integration. Do not beautify or hide failures.
- When authorized, render separate labeled diagnostics: front/three-quarter silhouette and useful side/back; neutral material/shape view; wireframe/topology or orthographic only for a specific diagnostic. Use temporary copy or separately generated scene state, never alter source. Do not overwrite comparison image; distinguish diagnostics from gameplay truth. Blender output does not promise consumer appearance.
- Verify asset in frame and not clipped; confirm projection, lens, aspect, framing and side. Check how emission/transparency/shadows/tone mapping/color management/reflections affect shape. Use smallest meaningful resolution/sample count; do not add dependencies or change system settings. Render only authorized views.

## Safe read-only execution

- Inspect installed Blender version/help before command syntax. Options are order-sensitive; render options follow file they apply to. For example: `blender --background /absolute/source.blend --render-output /absolute/output/view-#### --render-format PNG --use-extension 1 --render-frame 1` (Blender adds frame number). For temporary read-only scripts use `blender --background /absolute/source.blend --python-exit-code 1 --python /absolute/script.py`, confirming installed syntax and output behavior first.
- Bound each process timeout; capture logs, exit code and expected paths. Nonzero exit, timeout, missing/empty/partial output is failure. Verify file size, decode/open and visually inspect; extension alone is not proof. If unable to view/decode, state limitation.
- Compare source checksum/modification time before and after; if changed, stop and report unexpected mutation, do not silently restore. On failure preserve logs/partial output; inspect exact temporary paths before cleanup. Stop only process started for this task; never blanket-kill. Retry only after safe diagnosis.

## Critique and handoff

The agent owns inspection and critique; user is visual director, not expected to perform artist labor. Compare with approved brief/concept. Distinguish observed geometry from presentation differences and uncertain inference; report concrete issues by view (silhouette, proportion, overlap, artifact, visibility, framing), state lighting/material effects separately. Propose smallest in-scope geometry revision; ask before expanding/changing direction. Render is evidence, not approval.

Return stable source/scripts/concept and selected review-image paths. Keep useful approval evidence, put iteration previews/logs in task scratch/archive, remove only after needed evidence preserved. Record version, renderer, camera, lighting, resolution, source-integrity and image-verification results and limitations. Keep preview distinct from runtime evidence. Never claim model approval or runtime acceptance without separate approval.

Before execution verify authorization, source and unchanged-source plan, approved camera/views, output paths, syntax, timeout, expected images, decode/view and integrity checks, cleanup scope. State what images will be produced and what they assess. If camera/view or approval is missing, stop; do not render substitute/create assets.
