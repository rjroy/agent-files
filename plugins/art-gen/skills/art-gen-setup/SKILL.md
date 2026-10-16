---
name: art-gen-setup
description: Use when setting up or repairing the local art-gen script dependencies, or when the user asks to install art-gen's Bun packages. Installs dependencies in the art-gen collection without changing the user's working directory or running a generation task.
---

# Set up art-gen

Use this workflow only when the user asks to set up or repair the art-gen installation. This installs JavaScript dependencies; it does not generate an image or video.

## Locate the installation

Use the absolute directory supplied by the OpenCode skill loader as the canonical skill base, then resolve the art-gen collection root two directories above it. Do not infer the root from the process working directory, repository layout, or a provider-specific environment variable. Run the install from the resolved collection root so Bun uses its `package.json` and `bun.lock`.

## Requirements and install

1. Check that `bun` is available. If it is not, explain that Bun is required and ask the user to install it before continuing; do not substitute another package manager.
2. From the resolved collection root, run `bun install`.
3. Report whether installation succeeded. On failure, preserve the error and explain the next actionable step; do not claim setup succeeded.

Do not run a generation script as a setup check: the scripts call Replicate and may incur costs. If the user asks for a runtime check, explain that the generation scripts require a `REPLICATE_API_TOKEN` and obtain confirmation before any generation request.
