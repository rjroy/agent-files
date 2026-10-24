---
name: music-artwork
description: Create cover-art images or animate confirmed source art into video hooks. Includes image and video modes; prompt-only requests belong to music-image-prompt or music-video-prompt. Paid rendering always requires explicit approval.
---

# Music artwork: image and video modes

This skill handles a complete image or video rendering workflow when requested. The `music-image-prompt` and `music-video-prompt` skills remain prompt-only: asking for or selecting a prompt is never permission to render. Never conflate prompt creation with paid generation approval.

Before either mode, consult `music-engine-reference` and resolve its resources relative to that installed skill directory. Use only integrations and models actually available in the current session, follow their documented interfaces, and report actual output paths. Never invent model names, prices, tool fields, status URLs, or filenames; never create, copy, move, convert, or edit media files with text tools.

## Image mode: cover art

1. Read the completed song and identify theme, lens, emotional core, key imagery, and production style. Read `../music-engine-reference/images/base.md` and `../music-engine-reference/images/Suno Theme Art Styles Guide.md`.
2. Invoke `music-image-prompt` to create three distinct cover-art prompt samples, with context: themed song `[Theme] Art Style - [description and key imagery]`; otherwise a clear emotional/visual concept. Keep prompt creation distinct from rendering.
3. Read the samples file and present the top recommendation and alternatives. Ask the user to choose/confirm the prompt, and **always ask their aspect-ratio preference** (portrait 9:16, square 1:1, landscape 16:9, or model default when unspecified/Other).
4. Consider both `generate-image` (documented image-generation integrations) and `asset-art` (the authorized Codex production-art route); do not require `generate-image` as the sole route. Recommend a route based on availability, the cover-art brief, and user preference, then load the selected skill. For `generate-image`, inspect its available models and recommend premium only for complex/high-importance work, mid-tier for typical use, and budget for minimalist/quick iterations. For `asset-art`, establish its approved production brief, intended cover-art consumer, framing, dimensions/ratio, background, and exclusions before generation. Disclose only reported models and costs; mark unavailable cost/model information unknown rather than inventing it or assuming the route is free. Obtain explicit approval for the selected prompt, route, available model selection, aspect ratio, and known cost/parameters or their uncertainty. Prompt selection alone is not generation approval.
5. Generate through the selected skill's documented interface and obey its authorization gates. `asset-art` must use its authorized Codex route and retain its native-output verification, provenance, candidate-copy, and exact-version artwork-approval requirements; it is not a wrapper for `generate-image`. Do not silently switch routes after failure or unavailability: obtain approval for a changed route before rendering. If neither route is available, stop with the selected copy-ready prompt and explain the user can use a preferred image generator.
6. On success, present the verified output path, route, reported model (or unknown), prompt, and visual connection. For `asset-art`, distinguish a generated candidate from approved artwork and retain samples until its verification and artwork approval are complete; otherwise clean up `image-prompt-samples-*.md` only after successful generation. Offer adjustments. Check for text artifacts; discuss prompt changes and obtain approval before every rerender.

Present image choices in a recommendation/alternatives list with fit and visual description, then ask “Proceed with recommendation, or select 2 or 3?” Ask aspect ratio interactively with Portrait (9:16), Square (1:1), and Landscape (16:9); if unspecified or Other, use the model default. After successful render, report:

```text
## Cover Art Generated
Image: [actual returned path]
Prompt used: [selected sample]
Route/model: [selected skill/route, reported model or unknown, and rationale]
Artwork status: [generated candidate or exact-version approved artwork; any remaining checks]
Visual connection: [how image represents song]
Theme style applied: [theme or Custom/General]
Samples cleaned up: [yes/no and reason]
```

If a generation call errors, explain it may have completed remotely. Check only a documented status mechanism; do not blindly retry. Since generation can cost money, get explicit confirmation before every retry. If all three options are rejected, ask what is missing and rerun `music-image-prompt` with adjusted context; do not render until the user approves.

## Video mode: animate source art

Video generation is expensive and slow; quote cost/time only when shown by the available integration. Always get explicit user approval before rendering and never auto-retry.

1. Find candidate `cover-*.*` files in the current directory and **ask the user to confirm which source image to use**. Read/inspect it. If none exists, suggest creating cover art first or ask for an image path.
2. Read `../music-engine-reference/video/video-prompting-guide.md`. Analyze subject, plausible motion, focal points, mood, and technical constraints.
3. Invoke `music-video-prompt` with the image description, song mood/energy, and motion ideas to create three distinct motion samples. Do not recreate a cover or conflate prompt generation with video rendering.
4. Present the selected/alternative approaches and obtain the user's prompt selection. Inspect only currently exposed video models; recommend for the use case and clearly disclose current integration-provided cost and duration.
5. Present the selected prompt, source image, model, cost, and duration; ask explicit confirmation to generate. If no suitable integration is available, stop with the copy-ready prompt.
6. Generate only through its documented interface and refer to the actual reported output path. On success, explain camera/motion choices and model, clean up `video-prompt-samples-*.md`, and offer adjustments.

Present video choices with confirmed source filename, a top recommendation, and two alternatives describing camera, motion, and mood; ask the user to select. Before generation, show selected prompt, model, integration-reported cost and duration, and ask “Proceed with generation?” Offer Change model and Cancel choices as well. After success, report:

```text
## Video Hook Generated
Video: [actual returned path]
Source: [confirmed cover-art path]
Prompt used: [selected sample]
Model: [model and integration-reported cost]
Duration: [reported duration]
Motion approach: [camera, subject, atmosphere]
Samples cleaned up: [yes]
```

If generation errors or times out, explain a remote request may have completed, check only a documented status view, and ask before retrying; every attempt may cost money. If all motion samples are rejected, ask the user what they envision and rerun `music-video-prompt`. If the image is unsuitable, suggest camera-only motion or revising the source art. Do not repeat an image's appearance in motion prompts: the image defines appearance; describe only movement.

## Safety gates and outputs

- Prompt-only work stays in `music-image-prompt` / `music-video-prompt`; neither implies a paid render.
- Image: source is the song context; user selects prompt, confirms aspect ratio, and separately approves render parameters/cost.
- Video: user confirms the source image, selects prompt, and separately approves render parameters/cost.
- Explicit approval is required before each render and each retry. No implicit consent from prior approval or prompt selection.
- Preserve samples and do not claim generation if rendering is unavailable or unsuccessful. Clean prompt samples only after successful generation.
- Save media in a song folder only if the selected route documents a destination option or an authorized verified-copy step (as in `asset-art`); otherwise report the actual returned location. Never use text tools to write media bytes.
