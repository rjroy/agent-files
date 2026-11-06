---
name: asset-art
description: Produce authorized SVG or raster 2D artwork from an approved production brief using Codex, then verify and present the exact candidate for approval.
---

# 2D asset art

Follow the production 2D branch in [asset-workflow](../asset-workflow/SKILL.md). This is not exploratory concept art ([concept-art](../concept-art/SKILL.md)), Blender modeling/derivatives, or runtime implementation. Require an explicitly approved production brief and task-specific artwork-creation authorization, including the chosen SVG-authoring or raster-generation mode.

## Before generation

- Confirm approved brief, authorized references, intended consumer/role and exclusions. Resolve visual decisions with the user/designer rather than inventing direction.
- Agree expected consumer, framing, silhouette, safe padding, consistent set scale, transparent pixels vs intended background, projected display sizes, dimensions/ratio, and file-size budget. Mark unknown budgets unknown.
- Keep lettering out of reusable art unless approved. Put accessible labels and hit controls in DOM/UI; runtime glow, overlays and animation are not reusable source art.
- Consult current project direction/references; flag conflicts instead of choosing silently.

## Choose SVG or raster

- Offer **SVG** as a first-class option. Recommend it for scalable icons, marks, diagrams, and vector-style illustrations when it fits the approved direction and intended consumer. Codex authors SVG markup directly; this is not a native SVG export from the image-generation tool.
- Keep **PNG** available for raster illustrations, textures, sprites, and other bitmap artwork, including transparent output when verified. Do not substitute simplified SVG for an approved raster target or rasterize an approved vector master without authorization.
- Agree the format in the brief. For SVG, specify the `viewBox`, aspect ratio, and projected display sizes; for raster, specify pixel dimensions. Preserve editable SVG or the high-quality raster original as the master. WebP remains an option where suitable, not a required replacement for PNG.

## Authorized generation and verification

Use only the authorized Codex route; send the approved prompt via stdin. For raster generation, allow the tool's normal native image staging. For SVG authoring, name an authorized, non-overwriting candidate source path in the prompt. Verify the resulting artwork before packaging:

```bash
codex exec --skip-git-repo-check - <<'PROMPT'
[Approved production brief, chosen format/mode, and task-specific authorization.] Create actual 2D production artwork. For raster, use the normal image-output mechanism; for SVG, author a self-contained SVG at the authorized candidate source path. Report absolute source/output path(s). Do not modify unrelated project files.
PROMPT
```

`--skip-git-repo-check` is a route flag, not permission or sandbox bypass. Do not add bypass flags, weaken controls, install tools, change global configuration, or use permission workarounds. `-o/--output-last-message` writes text, not an image. Never substitute a placeholder. Report exact staging/destination access failures; do not improvise.

### Execution timeout and recovery

- Set the shell/execution tool timeout explicitly to **600000 milliseconds (10 minutes)** for the Codex generation command. Do not inherit a short default such as 120 seconds. This is a host execution setting, not a flag to add to `codex exec`.
- A timeout does not prove generation failed or stopped. Report the exact error and check the original process and native output locations for recoverable results before proposing another attempt. Do not start a duplicate while the original is still running.
- Recover and verify an existing output when available. If no usable output is found, obtain explicit authorization before retrying; never retry automatically or switch generation routes to evade the timeout.

1. Verify native output exists, is nonempty, and decodes (raster) or parses and renders (SVG). Visually inspect it against the approved brief and references. For SVG, inspect the source for a valid `viewBox`, clipping, missing dependencies, scripts/event handlers, and external resource references; require self-contained artwork without active content. Do not disguise an embedded bitmap as editable vector artwork. Record the renderer/version used for inspection.
2. If transparency is required, inspect decoded alpha pixels for raster or a transparent-background render for SVG, verifying transparent and opaque pixels. A checkerboard in RGB is not transparency. Composite over dark and light backgrounds; inspect halos, matte color and premultiplication. Never promise real alpha. If absent, stop and ask for an approved alternative/removal route; do not silently key or destructively remove background.
3. Review projected display size and relevant crops/selected states. For sets, compare framing, silhouette, scale and style together. Review reusable art without runtime effects masking defects.
4. Copy the verified original to a stable candidate package following the consuming project's existing conventions. Keep approved source/master distinct from production derivatives; never overwrite approved files. Preserve SVG as vector master or the high-quality raster original. PNG remains an allowed raster format; choose reproducible PNG or WebP derivatives only where suitable and separately authorized (WebP only when required alpha is verified); do not blanket-convert lossily. Record source/copy hashes, provenance/native and durable paths, tool/version/date, status, format, pixel dimensions or SVG `viewBox`/dimensions, color space and runtime sRGB handling, and any authorized derivative dimensions/ratio/size. Include minimal reproduction/conversion commands and relevant versions, not historic scratch cruft. Inspection renders are evidence, not approved production derivatives.
5. Present the inspected candidate and obtain exact-version artwork approval before promotion. Artwork approval is not derivative approval or runtime acceptance. Derivatives need separate authorization/review; integration and acceptance require actual-consumer verification and separate approval.

If decode/render, transparency verification, provenance, copy, inspection, or approval is incomplete, label candidate and report remaining work. Do not claim production handoff without real inspected art and provenance.

## Prompt template

```text
Asset and role: [what this art represents and where it appears]
Approved direction: [approved description; cite authorized references]
Framing and consistency: [view/crop, silhouette, safe padding, scale]
Delivery: [agreed projected sizes, ratio/dimensions, file-size budget; mark unknowns]
Format/mode: [SVG authoring with viewBox and authorized candidate source path, or raster generation such as PNG with pixel dimensions]
Background/alpha: [real transparent pixels required, or intended background]
Constraints: [palette/material cues, exclusions; no baked text, labels, controls, glow, or animation unless approved]
Output: create actual artwork with the authorized Codex route and approved mode; report source/native absolute path. Do not modify unrelated files.
```

## Handoff checklist

- [ ] Approved brief, chosen SVG/raster mode, and task-specific creation authorization recorded.
- [ ] Native raster decodes or SVG parses/renders with source checks; artwork visually inspected against brief.
- [ ] Required transparency verified at pixel level (raster or SVG inspection render) and on dark/light composites, or blocker/approved alternative recorded.
- [ ] Projected-size/crop and set-consistency review completed.
- [ ] Candidate path, hashes, provenance, versions/date, dimensions/format, color space and status recorded.
- [ ] Exact artwork approval, derivative approval, and runtime acceptance remain distinct.
