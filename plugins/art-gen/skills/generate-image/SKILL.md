---
description: Use when the user asks to generate, create, edit, animate, or process images. Covers text-to-image generation, image editing (img2img), video generation from images, and background removal.
---

# generate-image skill

## Model catalogs

Set `ART_GEN_SKILL_DIR` to the absolute skill directory supplied by the OpenCode skill loader. Read the appropriate catalog by resolving its path from that canonical base, never from the user's working directory:

`$ART_GEN_SKILL_DIR/../../reference/image-models.md`
`$ART_GEN_SKILL_DIR/../../reference/video-models.md`
`$ART_GEN_SKILL_DIR/../../reference/img2img-models.md`
`$ART_GEN_SKILL_DIR/../../reference/remove-bg-models.md`

## Prerequisites

All scripts require `REPLICATE_API_TOKEN` in the environment. If unset, the script exits 1 with an error directing to replicate.com/account/api-tokens. Surface this to the user if it occurs.

## Script invocations

Set `ART_GEN_SKILL_DIR` to the loader-provided absolute directory of this skill and invoke each script through its absolute skill-derived path. Keep the shell's working directory at the user's project directory; **do not `cd` to the skill or collection directory**. The scripts resolve output paths against `process.cwd()` and read relative image paths from that same working directory, so user paths such as `assets/source.png` and `generated/result.png` remain relative to the project directory. Use OpenCode's shell tool and preserve its original project working directory for every command.

### Text-to-image

```
bun "$ART_GEN_SKILL_DIR/../../src/generate-image.ts" --prompt <string> --output <path> [--model <string>] [--aspect-ratio <string>] [--width <number>] [--height <number>] [--num-outputs <number>] [--seed <number>] [--params <json>]
```

Flags:
- `--prompt` (required) — generation prompt
- `--output` (required) — output file path
- `--model` — default: `black-forest-labs/flux-schnell`; see `$ART_GEN_SKILL_DIR/../../reference/image-models.md` for options
- `--aspect-ratio` — e.g. `16:9`, `1:1`
- `--width`, `--height` — explicit pixel dimensions (overrides aspect-ratio)
- `--num-outputs` — number of images to generate
- `--seed` — for reproducible results
- `--params` — JSON blob of extra model-specific parameters

### Image editing (img2img)

```
bun "$ART_GEN_SKILL_DIR/../../src/edit-image.ts" --image <path> --prompt <string> --model <string> --output <path> [--strength <number>] [--params <json>]
```

Flags:
- `--image` (required) — input image path
- `--prompt` (required) — edit prompt
- `--model` (required) — see `$ART_GEN_SKILL_DIR/../../reference/img2img-models.md` for supported models
- `--output` (required) — output file path
- `--strength` — blend between original and edit; default `0.75`; only used if model supports it
- `--params` — JSON blob of extra model-specific parameters

### Video generation

> **Cost and time warning:** Video generation costs $0.10–$1.50+ per video and takes 2–5 minutes. Always confirm with the user before running video generation.

```
bun "$ART_GEN_SKILL_DIR/../../src/generate-video.ts" --image <path> --prompt <string> --model <string> --output <path> [--params <json>]
```

Flags:
- `--image` (required) — source image to animate
- `--prompt` (required) — motion/animation prompt
- `--model` (required) — see `$ART_GEN_SKILL_DIR/../../reference/video-models.md` for supported models
- `--output` (required) — output file path
- `--params` — JSON blob of extra model-specific parameters

### Background removal

```
bun "$ART_GEN_SKILL_DIR/../../src/remove-background.ts" --image <path> --model <string> --output <path> [--params <json>]
```

Flags:
- `--image` (required) — input image path
- `--model` (required) — use `bria/remove-background`; see `$ART_GEN_SKILL_DIR/../../reference/remove-bg-models.md`
- `--output` (required) — output path; auto-corrected to `.png` if needed (transparency requires PNG)
- `--params` — JSON blob of extra model-specific parameters

### Project-relative media paths

For example, with the shell working directory still set to `/home/user/projects/album`, an edit can use `--image assets/source.png --output generated/source-edited.png`. Invoke the script by its skill-derived absolute path, but do not change directories: those media paths resolve against `/home/user/projects/album`, not the installed art-gen collection.

## Output interpretation

- **stdout** — each line is a saved file path; present these to the user
- **stderr** — progress updates and error messages; surface to the user on failure, suppress on success unless the content is relevant
