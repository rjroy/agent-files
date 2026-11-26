---
description: Use when the user asks to generate, create, edit, animate, or process images. Covers text-to-image generation, image editing (img2img), video generation from images, and background removal.
---

# generate-image skill

## Choose the route before rendering

This skill owns tool selection for image creation and editing, including raster inputs for SVG tracing. A render must be explicitly requested or approved. A prompt, concept approval, modeling request, or review alone does not authorize rendering. Preserve the calling workflow's approvals, including approval for paid rendering; unknown cost is not evidence that a route is free. Do not require the user to choose a model unless they want a specific one or a material tradeoff needs their decision.

For normal image work, use the OpenAI routes below in order. If the user has explicitly authorized a special Replicate route, use that route instead.

1. **OpenCode's built-in `generate_image` first, when it can use OpenAI.** Check the current model catalog (the `models` tool with `type: "image"` and `provider: "openai"`). When the user does not specify a particular model or variant, omit `model` and use the effective `experimental.image_generate.model` default only if it names a specific OpenAI image model and the current catalog confirms that exact model is available and suitable. A missing or unsupported default can silently select a different provider; do not call the built-in tool with an unconfirmed default. If the user explicitly requests a particular OpenAI model or variant, the built-in route must match it via a confirmed default or an exact `model` selection permitted by the tool and verified in the catalog. For references or edits, also verify that the selected model supports source-image input for the requested operation; a listing alone does not establish that capability.
2. **Otherwise use OpenAI via Codex.** If built-in availability, OpenAI selection, or the needed input capability cannot be confirmed before calling it, use the Codex route below for new images or edits. This is a route decision before rendering, not a retry. Do not silently substitute a different model when the user requires a specific one.
3. **Replicate is opt-in.** Use the scripts below only for a special use case the user explicitly authorizes on Replicate, such as a requested Replicate model, video integration, or background-removal route. Confirm paid use and any material limitations first. Availability of a token, an installed script, or a catalog entry is not authorization.

If an attempted render fails or the output cannot be verified, report the stage and what happened. A remote request may already have completed or incurred a charge. Check only a documented status mechanism where applicable. Do not automatically retry, switch routes, use a placeholder, or claim success; get explicit authorization for any retry or route change after an attempt.

## OpenCode built-in image generation and editing

Pass the actual brief in `prompt` and, when applicable, 1 to 8 authorized local paths or URLs in `images`. Each call creates or edits one image. If specifying `path`, use a fresh candidate path: the tool may change its extension to match the actual format and overwrite a matching file. Wait for the automatic completion notification. Do not sleep, poll, or check the file while the job is running. Verify the actual saved path reported in the notification.

## Text-to-image and editing: OpenAI via Codex

Before invoking `codex exec`, verify that the effective login in the same project directory and environment is the user's ChatGPT subscription login, not API-key authentication. Use a non-secret status check such as `codex login status`; use the reported authentication mode, not just the exit code. Do not inspect credential files, tokens, or secret environment values. If ChatGPT authentication cannot be confirmed or the native tool is unavailable, report the blocker. Do not switch provider, authenticate on the user's behalf, install dependencies, or change configuration.

Pass the actual user request and the execution limits as one safely quoted prompt argument. Require exactly one attempt with Codex's native OpenAI `image_gen` tool. If that attempt fails or is unavailable, stop and report it without retrying, rerendering, or switching tools, routes, or providers (including Codex's Python/API fallback). Tell Codex to leave the source and project files unchanged, do no integration, and leave any output in native staging. Codex reports the actual native output path; the calling agent verifies it and handles any authorized copy. Do not pass a project destination for Codex to write to. For an edit, verify and attach the authorized local source with `--image` and specify what to change and preserve. If the source is not available as a local file, ask for an authorized local copy if needed. For example:

```bash
codex exec -- 'Make exactly one native OpenAI image_gen attempt to generate an image of a happy sun trying to make sad sunflowers happy. Do not retry, rerender, or switch tools, routes, or providers. Leave output in native staging; do not copy it, edit project files, or integrate it. Report the actual native saved path, or stop and report failure or unavailability.'
codex exec --image "$source" -- 'Make exactly one native OpenAI image_gen attempt to soften the shadows in the attached image without changing its composition. Do not retry, rerender, or switch tools, routes, or providers. Leave the source and project files unchanged and leave output in native staging; do not copy or integrate it. Report the actual native saved path, or stop and report failure or unavailability.'
```

If the project is not a Git repository, the installed CLI accepts `--skip-git-repo-check`; this does not grant additional file permissions. Read Codex's final reply as prose, not a list of paths. Do not assume a default staging directory is where the image was saved.

## Verify the saved output

For either OpenAI route, check that the reported file exists, is nonempty, and decodes as an image, then inspect it against the request before presenting the actual verified path. Resolve relative paths from the user's project directory. Report the route and the model only when known. If the artifact needs a durable project location, copy the verified native output only to an authorized, non-overwriting candidate path and verify that copy. Apply the calling workflow's additional checks for provenance, image fidelity, transparency, and exact-version approval.

## Video

Video is a separate request that always requires confirmation before rendering. Use an available video integration only as authorized for the confirmed source, motion prompt and disclosed cost and duration (mark unknowns). If using OpenCode's built-in `generate_video`, follow its current schema and wait for its completion notification without polling; verify the actual saved video before reporting it. Use the Replicate video route below only when specifically authorized. No automatic retry or substitution.

## Replicate model catalogs

Set `ART_GEN_SKILL_DIR` to the absolute skill directory supplied by the OpenCode skill loader. Read the appropriate catalog by resolving its path from that canonical base, never from the user's working directory:

`$ART_GEN_SKILL_DIR/../../reference/image-models.md`
`$ART_GEN_SKILL_DIR/../../reference/video-models.md`
`$ART_GEN_SKILL_DIR/../../reference/img2img-models.md`
`$ART_GEN_SKILL_DIR/../../reference/remove-bg-models.md`

Prices in all four catalogs are historical and non-authoritative. Before asking the user to authorize any Replicate request, disclose the current integration- or provider-reported price for the proposed settings, or mark the cost unknown if it cannot be verified. Do not use catalog prices as quotes.

## Replicate prerequisites

All scripts require `REPLICATE_API_TOKEN` in the environment. If unset, the script exits 1 with an error directing to replicate.com/account/api-tokens. Surface this to the user if it occurs.

## Replicate script invocations

Set `ART_GEN_SKILL_DIR` to the loader-provided absolute directory of this skill and invoke each script through its absolute skill-derived path. Keep the shell's working directory at the user's project directory; **do not `cd` to the skill or collection directory**. The scripts resolve output paths against `process.cwd()` and read relative image paths from that same working directory, so user paths such as `assets/source.png` and `generated/result.png` remain relative to the project directory. Use OpenCode's shell tool and preserve its original project working directory for every command.

### Text-to-image (authorized Replicate use only)

```
bun "$ART_GEN_SKILL_DIR/../../src/generate-image.ts" --prompt <string> --output <path> [--model <string>] [--aspect-ratio <string>] [--width <number>] [--height <number>] [--num-outputs <number>] [--seed <number>] [--params <json>]
```

Flags:
- `--prompt` (required) — generation prompt
- `--output` (required) — output file path
- `--model` — default: `black-forest-labs/flux-schnell`; see `$ART_GEN_SKILL_DIR/../../reference/image-models.md` for options
- `--aspect-ratio` — e.g. `16:9`, `1:1`
- `--width`, `--height` — explicit pixel dimensions; if `--aspect-ratio` is also set, it takes precedence and the dimension flags are ignored with a warning
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

> **Cost and time warning:** Video generation can incur charges and take several minutes. Disclose current integration-reported cost and duration or mark them unknown. Always confirm with the user before running video generation.

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

## Replicate script output

- **stdout** — each line is a saved file path; verify the actual files before presenting them to the user
- **stderr** — progress updates and error messages; surface to the user on failure, suppress on success unless the content is relevant
