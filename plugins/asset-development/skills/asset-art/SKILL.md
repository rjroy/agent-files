---
name: asset-art
description: Produce explicitly requested SVG or raster 2D artwork from a sufficient brief, then verify and present the exact candidate for approval.
---

# 2D asset art

Follow the production 2D branch in [asset-workflow](../asset-workflow/SKILL.md). This is not exploratory concept art ([concept-art](../concept-art/SKILL.md)), Blender modeling/derivatives, or runtime implementation. Require a sufficient brief and an explicit request for image creation, including the raster-first SVG or raster-only mode. Do not require a separate brief-approval turn.

## Before generation

- Capture the brief, authorized references, intended consumer/role and exclusions. Resolve consequential missing visual decisions with the user/designer rather than inventing direction.
- Establish expected consumer, framing, silhouette, safe padding, consistent set scale, transparent pixels vs intended background, projected display sizes, dimensions/ratio, and file-size budget where relevant. Choose routine unspecified details; mark unknown budgets unknown.
- Keep lettering out of reusable art unless approved. Put accessible labels and hit controls in DOM/UI; runtime glow, overlays and animation are not reusable source art.
- Consult current project direction/references; flag conflicts instead of choosing silently.

## Choose SVG or raster

- Offer **SVG** as a first-class option. Recommend it for scalable icons, marks, diagrams, and vector-style illustrations when it fits the approved direction and intended consumer. Produce artwork by generating a trace-friendly raster and tracing its regions into editable vector paths; the image tool does not itself generate editable SVG. Do not hand-author artwork shapes as the creation route.
- Keep **PNG** available for raster illustrations, textures, sprites, and other bitmap artwork, including transparent output when verified. Do not substitute simplified SVG for an approved raster target or rasterize an approved vector master without authorization.
- Establish the format from the request and brief; ask if a consequential format choice remains unresolved. For SVG, specify the `viewBox`, aspect ratio, projected display sizes, and raster source dimensions; for raster-only work, specify pixel dimensions. Preserve both the raster source and editable SVG for vector work, or the high-quality raster original for raster-only work. WebP remains an option where suitable, not a required replacement for PNG.

## Authorized generation and verification

For explicitly requested raster creation or editing, including the raster source for SVG production, call the built-in `experimental_image_generate` tool with `prompt` containing the brief and, when applicable, `images` containing 1 to 8 authorized local paths or URLs as references or edit sources. For a vector target, request a limited palette, flat colors, clean silhouettes, and no gradients or textures. Each call creates or edits one image. An optional `path` specifies the output location, but its extension is replaced with the actual format and an existing file is overwritten. Choose a separate candidate path, never an approved image. Omit `model` unless the user explicitly requests a particular model or variant; then discover its ID with the models tool rather than guessing.

The call starts a background job and returns immediately. Wait for the automatic completion notification and use its actual saved path; never poll, sleep, or check the file while the job is running. Do not repeat a request unless the user asks. If no path was specified, treat the returned location as native staging and copy the completed output to an authorized candidate path. Do not guess paths. If the tool is unavailable or fails, report the stage and exact diagnostics; do not use paid external fallbacks, art-generation scripts, or placeholders.

For the explicitly authorized SVG production mode, inspect the completed raster against the brief before tracing. Use a suitable available vector tracer, such as VTracer for color or Potrace for monochrome, to create a separate, non-overwriting SVG candidate. ImageMagick may prepare the bitmap but does not trace vector paths. Tracing and ordinary SVG cleanup/validation are part of this authorized creation process, not separate runtime derivative work; do not ask for redundant approval within that scope. Do not assume a tracer or preprocessing tool is installed, install tools without authorization, change global configuration, or use permission workarounds. If a required tool is unavailable, report the blocker and options and request direction; report staging or destination access failures.

1. After raster completion, verify the actual saved output is nonempty and decodes; for SVG, verify it parses and renders. Read and visually inspect the raster and actual SVG candidate against the brief and references before presenting it for approval. For SVG, inspect the actual editable vector paths and source for a valid `viewBox`, clipping, missing dependencies, scripts/event handlers, and external resource references; require self-contained artwork without active content. Do not embed a bitmap and claim it is vector artwork. Record the renderer/version used for inspection.
2. If transparency is required, inspect decoded alpha pixels for raster or a transparent-background render for SVG, verifying transparent and opaque pixels. A checkerboard in RGB is not transparency. Composite over dark and light backgrounds; inspect halos, matte color and premultiplication. Never promise real alpha. If absent, stop and ask for an approved alternative/removal route; do not silently key or destructively remove background.
3. Review projected display size and relevant crops/selected states. For sets, compare framing, silhouette, scale and style together. Review reusable art without runtime effects masking defects.
4. Place the verified original in a stable candidate package following the consuming project's existing conventions; if copying, verify source/copy hashes and inspect the durable candidate. Keep native staging until durable copy and provenance are verified. Keep approved source/master distinct from production derivatives; never overwrite approved files. Preserve the generated raster source and traced SVG vector master together, or the high-quality raster original for raster-only work. PNG remains an allowed raster format; choose reproducible PNG or WebP derivatives where suitable and requested (WebP only when required alpha is verified); do not blanket-convert lossily. Record source/copy hashes when applicable, provenance/native and durable paths, generation, preprocessing and tracing tools/versions when available, date, status, format, pixel dimensions or SVG `viewBox`/dimensions, color space and runtime sRGB handling, and any requested derivative dimensions/ratio/size. Include minimal reproduction/conversion commands and relevant versions where applicable, not historic scratch cruft. Inspection renders are evidence, not approved production derivatives.
5. Present the inspected candidate and obtain exact-version artwork approval before promotion. Requested derivatives may be prepared and inspected as candidates without another permission turn. Integration must be explicitly requested, including at the outset; after source acceptance continue already-requested integration, verify in the actual consumer, and obtain runtime appearance acceptance.

If decode/render, transparency verification, provenance, copy, inspection, or approval is incomplete, label candidate and report remaining work. Do not claim production handoff without real inspected art and provenance.

## Prompt template

```text
Asset and role: [what this art represents and where it appears]
Direction: [description from the brief; cite authorized references]
Framing and consistency: [view/crop, silhouette, safe padding, scale]
Delivery: [agreed projected sizes, ratio/dimensions, file-size budget; mark unknowns]
Format/mode: [raster-first traced SVG with source dimensions, viewBox and authorized candidate paths, or raster-only generation such as PNG with pixel dimensions]
Background/alpha: [real transparent pixels required, or intended background]
Constraints: [palette/material cues, exclusions; for SVG, limited palette, flat colors, clean silhouettes, no gradients or textures; no baked text, labels, controls, glow, or animation unless approved]
Output: create actual artwork using the approved mode and authorized candidate path; record the actual source/native path. Do not modify unrelated files.
```

## Handoff checklist

- [ ] Sufficient brief, chosen SVG/raster mode, and explicit image-creation request recorded.
- [ ] Native raster decodes and is inspected; traced SVG parses/renders with editable path and source checks; artwork visually inspected against brief.
- [ ] Required transparency verified at pixel level (raster or SVG inspection render) and on dark/light composites, or blocker/approved alternative recorded.
- [ ] Projected-size/crop and set-consistency review completed.
- [ ] Raster source and traced SVG preserved together for vector work; candidate paths, hashes, provenance, versions/date, dimensions/format, color space and status recorded.
- [ ] Exact artwork approval and, where applicable, runtime acceptance recorded; unaccepted derivatives remain candidates.
