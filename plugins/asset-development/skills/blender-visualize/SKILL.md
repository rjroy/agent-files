---
name: blender-visualize
description: Render and inspect an authorized saved Blender project for visual critique without modifying its source model.
---

# Blender visualization and inspection

Read [asset-workflow](../asset-workflow/SKILL.md) first. This skill renders existing saved `.blend` for inspection; it does not build/revise the model, alter its source, or approve it.

## Gate and render set

- Rendering and inspection are included in requested modeling work. Identify the saved `.blend`, direction and review purpose; select suitable cameras, diagnostic angles and output directory when not specified.
- Use absolute source path and record modification time or checksum before rendering. Source is read-only: do not save, pack, relink, alter materials/geometry/cameras or resave as a side effect.
- Ask only when a consequential visual choice cannot be resolved from the direction; routine camera, lens, scale and composition choices are agent-owned. References are evidence, not ground truth. Keep project direction separate from reusable visualization practice.
- Use the specified comparison view when supplied and neutral/restrained lighting for model review, with audience/context views when needed to assess the complete composition. Render actual saved geometry; generated reference/concept imagery is not a model render. These are visual evidence, not final-product/runtime-fidelity proof. Inspect/present actual images. Assess silhouette, proportions, construction, detail, topology and geometry defects. Lighting, emission, bloom, exposure, tone mapping, reflections or final material alone need not trigger geometry revisions; preserve material separation and report appearance caveats. Keep shape/structural checks distinct from aesthetic assessment and approval. Final appearance is assessed separately in the consumer. Do not beautify or hide failures.
- Render separate labeled diagnostics as needed: front/three-quarter silhouette and useful side/back; neutral material/shape view; wireframe/topology or orthographic only for a specific diagnostic. Use temporary copy or separately generated scene state, never alter source. Do not overwrite comparison image; distinguish diagnostics from gameplay truth. Blender output does not promise consumer appearance.
- Verify asset in frame and not clipped; confirm projection, lens, aspect, framing and side. Check how emission/transparency/shadows/tone mapping/color management/reflections affect shape. Use smallest meaningful resolution/sample count; do not add dependencies or change system settings. Keep views within the requested scope.

## Safe read-only execution

- Inspect installed Blender version/help before command syntax. Options are order-sensitive; render options follow file they apply to. For example: `blender --background /absolute/source.blend --render-output /absolute/output/view-#### --render-format PNG --use-extension 1 --render-frame 1` (Blender adds frame number). For temporary read-only scripts use `blender --background /absolute/source.blend --python-exit-code 1 --python /absolute/script.py`, confirming installed syntax and output behavior first.
- Bound each process timeout; capture logs, exit code and expected paths. Nonzero exit, timeout, missing/empty/partial output is failure. Verify file size, decode/open and visually inspect; extension alone is not proof. If unable to view/decode, state limitation.
- Compare source checksum/modification time before and after; if changed, stop and report unexpected mutation, do not silently restore. On failure preserve logs/partial output; inspect exact temporary paths before cleanup. Stop only process started for this task; never blanket-kill. Retry only after safe diagnosis.

## Critique and handoff

The agent owns inspection and critique; user is visual director, not expected to perform artist labor. Compare with the brief, approved concept and current accepted aggregate. Distinguish observed geometry from presentation differences and uncertain inference; consolidate material findings by view and severity (silhouette, proportion, overlap, artifact, visibility, framing), stating lighting/material effects separately. Structural checks are not aesthetic approval, and critique findings are evidence for judgment, not automatic vetoes. Propose the smallest authorized correction; ask before expanding scope or changing direction. Iterate in bounded batches, then stop when the candidate meets the target or further changes have no material benefit; present residual caveats for user judgment rather than pursuing perfection indefinitely. A render is evidence, not approval.

Return stable source, relevant reusable tools/concept and selected review-image paths. Keep useful approval evidence; bound iteration previews/logs in task scratch. At acceptance, consolidate only with explicit cleanup authorization: present a keep/delete inventory, verify links/dependencies, and independently reopen/render the consolidated package before removing specifically authorized duplicates or superseded files. Never delete the only approved source/evidence or assume experiment-path work is disposable. Record version, renderer, camera, lighting, resolution, source-integrity and image-verification results and limitations. Keep preview distinct from runtime evidence. Never claim model or runtime acceptance without explicit user approval.

Before execution verify task scope, source and unchanged-source plan, chosen camera/views, output paths, syntax, timeout, expected images, decode/view and integrity checks, cleanup scope. Record what images will be produced and what they assess. Do not create substitute assets or stop for routine unspecified views.
