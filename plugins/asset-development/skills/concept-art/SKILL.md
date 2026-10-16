---
name: concept-art
description: Generate and verify exploratory concept images for an explicitly approved asset brief using the user's authorized Codex image-generation route.
---

# Concept art

Follow [asset-workflow](../asset-workflow/SKILL.md). This is for exploratory concepts, not production artwork, modeling, derivatives, or runtime integration. Require an approved brief and task-specific image-generation authorization.

Use only the authorized `codex exec` image-generation route. The route flag `--skip-git-repo-check` is not permission or a sandbox/authentication bypass. Do not use other bypass flags or weaken controls. A previously verified invocation is not a guarantee of current availability.

1. Confirm approved brief and task authorization; include intended view, silhouette/material cues, constraints and authorized references. Keep one stable asset directory; record revisions in its README/history instead of permanent numbered folders.
2. The image tool may write to its native staging location before an authorized copy; do not assume it obeys exact-destination-only instructions. Allow normal native staging, then copy the real output to an authorized candidate path. Do not guess a temp path. If direct output is required, verify the launcher can read references and write the destination. Launcher user/context may differ; report exact access failure. Never use blanket chmod, sudo, permission workarounds, or installations.
3. Pass the prompt through stdin and request actual image output and its absolute path, e.g.:

   ```bash
   codex exec --skip-git-repo-check - <<'PROMPT'
   Generate one actual concept image for this approved brief: [brief, intended framing, authorized references]. Use the normal image-generation output mechanism and report absolute native output path(s). Do not modify unrelated project files.
   PROMPT
   ```

   `-o/--output-last-message` writes text, not an image.
4. Verify native path exists, contains nonempty image data, decodes and can be visually inspected. Compare with brief/references; command success is not evidence of quality. Copy the real image to an authorized candidate path, verify decoding and source/copy checksums, inspect it, and record native/durable paths, dimensions/format, checksum, tool/version, date, and status. Do not overwrite an approved image before replacement approval. Keep native original until durable copy and provenance are verified.
5. Report failure at its stage (launcher/DNS/access, generation, missing/unusable output, copy, or decode/view) with exact paths/diagnostics. Do not bypass controls, use a placeholder, or claim success without inspection.
6. Present the actual verified image and obtain explicit approval of that exact version before promoting it. Record approval separately from brief approval and preserve prior approved evidence in an authorized archive/history. Concept approval does not approve model, export, integration, or runtime acceptance.

No verified image means no concept-art handoff and no progression through concept approval.
