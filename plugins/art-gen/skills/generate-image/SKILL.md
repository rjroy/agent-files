---
description: Use when the user asks to generate, create, edit, animate, or process images. Covers text-to-image generation, image editing (img2img), video generation from images, and background removal.
---

# generate-image skill

## Model catalogs

Read the appropriate catalog before selecting a model:

${CLAUDE_PLUGIN_ROOT}/reference/image-models.md
${CLAUDE_PLUGIN_ROOT}/reference/video-models.md
${CLAUDE_PLUGIN_ROOT}/reference/img2img-models.md
${CLAUDE_PLUGIN_ROOT}/reference/remove-bg-models.md

## Prerequisites

All scripts require `REPLICATE_API_TOKEN` in the environment. If unset, the script exits 1 with an error directing to replicate.com/account/api-tokens. Surface this to the user if it occurs.

## Script invocations

### Text-to-image

```
bun ${CLAUDE_PLUGIN_ROOT}/src/generate-image.ts --prompt <string> --output <path> [--model <string>] [--aspect-ratio <string>] [--width <number>] [--height <number>] [--num-outputs <number>] [--seed <number>] [--params <json>]
```

Flags:
- `--prompt` (required) — generation prompt
- `--output` (required) — output file path
- `--model` — default: `black-forest-labs/flux-schnell`; see image-models.md for options
- `--aspect-ratio` — e.g. `16:9`, `1:1`
- `--width`, `--height` — explicit pixel dimensions (overrides aspect-ratio)
- `--num-outputs` — number of images to generate
- `--seed` — for reproducible results
- `--params` — JSON blob of extra model-specific parameters

### Image editing (img2img)

```
bun ${CLAUDE_PLUGIN_ROOT}/src/edit-image.ts --image <path> --prompt <string> --model <string> --output <path> [--strength <number>] [--params <json>]
```

Flags:
- `--image` (required) — input image path
- `--prompt` (required) — edit prompt
- `--model` (required) — see img2img-models.md for supported models
- `--output` (required) — output file path
- `--strength` — blend between original and edit; default `0.75`; only used if model supports it
- `--params` — JSON blob of extra model-specific parameters

### Video generation

> **Cost and time warning:** Video generation costs $0.10–$1.50+ per video and takes 2–5 minutes. Always confirm with the user before running video generation.

```
bun ${CLAUDE_PLUGIN_ROOT}/src/generate-video.ts --image <path> --prompt <string> --model <string> --output <path> [--params <json>]
```

Flags:
- `--image` (required) — source image to animate
- `--prompt` (required) — motion/animation prompt
- `--model` (required) — see video-models.md for supported models
- `--output` (required) — output file path
- `--params` — JSON blob of extra model-specific parameters

### Background removal

```
bun ${CLAUDE_PLUGIN_ROOT}/src/remove-background.ts --image <path> --model <string> --output <path> [--params <json>]
```

Flags:
- `--image` (required) — input image path
- `--model` (required) — use `bria/remove-background`; see remove-bg-models.md
- `--output` (required) — output path; auto-corrected to `.png` if needed (transparency requires PNG)
- `--params` — JSON blob of extra model-specific parameters

## Output interpretation

- **stdout** — each line is a saved file path; present these to the user
- **stderr** — progress updates and error messages; surface to the user on failure, suppress on success unless the content is relevant
