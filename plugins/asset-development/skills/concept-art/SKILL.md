---
name: concept-art
description: Generate and verify exploratory concept images for an explicitly approved asset brief using the built-in image-generation tool.
---

# Concept art

Follow [asset-workflow](../asset-workflow/SKILL.md). This is for exploratory concepts, not production artwork, modeling, derivatives, or runtime integration. Require an approved brief and task-specific image-generation authorization. Production SVG follows the raster-first tracing route in [asset-art](../asset-art/SKILL.md); concept approval does not authorize that work.

Use the built-in `experimental_image_generate` tool only for user-authorized image creation or editing. If unavailable or unsuccessful, report the blocker; do not use paid external fallbacks or art-generation scripts.

1. Confirm approved brief and task authorization; include intended view, silhouette/material cues, constraints and authorized references. Keep one stable asset directory; record revisions in its README/history instead of permanent numbered folders.
2. Call `experimental_image_generate` with `prompt` describing the approved brief and, when applicable, `images` containing 1 to 8 authorized local paths or URLs as references or edit sources. Each call creates or edits one image. An optional `path` specifies the output location, but its extension is replaced with the actual format and an existing file is overwritten. Choose a separate authorized candidate path, never an approved image. Omit `model` unless the user explicitly requests a particular model or variant; then discover its ID with the models tool rather than guessing.
3. The call starts a background job and returns immediately. Wait for the automatic completion notification and use its actual saved path; never poll, sleep, or check the file while the job is running. Do not repeat a request unless the user asks. If no path was specified, treat the returned location as native staging and copy the completed output to an authorized candidate path. Do not guess paths.
4. Once completed, verify the actual output contains nonempty image data and decodes, then read and visually inspect it against the brief and references before presenting it for approval. If copying, verify decoding and source/copy checksums and inspect the durable candidate. Record native/durable paths, dimensions/format, checksum, tool/version when available, date, and status. Do not overwrite an approved image before replacement approval. Keep the native original until durable copy and provenance are verified.
5. Report failure at its stage (tool availability/access, generation, missing/unusable output, copy, or decode/view) with exact paths/diagnostics. Do not bypass controls, use a placeholder, or claim success without inspection.
6. Present the actual verified image and obtain explicit approval of that exact version before promoting it. Record approval separately from brief approval and preserve prior approved evidence in an authorized archive/history. Concept approval does not approve model, export, integration, or runtime acceptance.

No verified image means no concept-art handoff and no progression through concept approval.
