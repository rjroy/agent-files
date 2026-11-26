---
name: concept-art
description: Generate and verify exploratory concept images from a sufficient brief when image generation is explicitly requested.
---

# Concept art

Follow [asset-workflow](../asset-workflow/SKILL.md). This is for exploratory concepts, not production artwork, modeling, derivatives, or runtime integration. Require a sufficient brief and an explicit user request for image generation, not a separate brief-approval turn. Production SVG follows the raster-first tracing route in [asset-art](../asset-art/SKILL.md); concept approval alone does not authorize that work.

Load `generate-image` for authorized image creation or editing. It owns provider and tool selection, invocation, and failure handling. This skill owns the brief, candidate inspection, and concept approval.

1. Capture the brief and image-generation request; include intended view, silhouette/material cues, constraints and authorized references. Choose routine missing views or paths without blocking; ask about consequential visual decisions. Keep one stable asset directory; record revisions in its README/history instead of permanent numbered folders.
2. Give `generate-image` the brief, authorized references or edit source, and intended separate candidate path, never an approved image. Follow its completion and verification instructions for the selected route.
3. Use the actual saved path. If output was written to native staging, copy the completed output to an authorized candidate path. Do not guess paths or retry on failure.
4. Once completed, verify the actual output contains nonempty image data and decodes, then read and visually inspect it against the brief and references before presenting it for approval. If copying, verify decoding and source/copy checksums and inspect the durable candidate. Record native/durable paths, dimensions/format, checksum, tool/version when available, date, and status. Do not overwrite an approved image before replacement approval. Keep the native original until durable copy and provenance are verified.
5. Report failure at its stage (tool availability/access, generation, missing/unusable output, copy, or decode/view) with exact paths/diagnostics. Do not bypass controls, use a placeholder, or claim success without inspection.
6. Present the actual verified image and obtain explicit approval of that exact version before modeling. Record approval and preserve prior approved evidence in an authorized archive/history. If modeling was already requested, concept approval releases that work without another permission turn; a concept-only request does not authorize modeling. Concept approval is not final model or runtime acceptance.

No verified image means no concept-art handoff and no progression through concept approval.
