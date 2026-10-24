---
name: asset-art
description: Produce authorized 2D artwork from an approved production brief using the authorized Codex image route, then verify and present the exact candidate for approval.
---

# 2D asset art

Follow the production 2D branch in [asset-workflow](../asset-workflow/SKILL.md). This is not exploratory concept art ([concept-art](../concept-art/SKILL.md)), Blender modeling/derivatives, or runtime implementation. Require an explicitly approved production brief and task-specific image-generation authorization.

## Before generation

- Confirm approved brief, authorized references, intended consumer/role and exclusions. Resolve visual decisions with the user/designer rather than inventing direction.
- Agree expected consumer, framing, silhouette, safe padding, consistent set scale, transparent pixels vs intended background, projected display sizes, dimensions/ratio, and file-size budget. Mark unknown budgets unknown.
- Keep lettering out of reusable art unless approved. Put accessible labels and hit controls in DOM/UI; runtime glow, overlays and animation are not reusable source art.
- Consult current project direction/references; flag conflicts instead of choosing silently.

## Authorized generation and verification

Use only the authorized Codex route; send the approved prompt via stdin and allow the tool's normal native staging, then copy the verified image to an authorized candidate path:

```bash
codex exec --skip-git-repo-check - <<'PROMPT'
[Approved production brief and task-specific authorization.] Generate actual 2D production artwork with the normal image-output mechanism. Report absolute native output path(s). Do not modify unrelated project files.
PROMPT
```

`--skip-git-repo-check` is a route flag, not permission or sandbox bypass. Do not add bypass flags, weaken controls, install tools, change global configuration, or use permission workarounds. `-o/--output-last-message` writes text, not an image. Never substitute a placeholder. Report exact staging/destination access failures; do not improvise.

### Execution timeout and recovery

- Set the shell/execution tool timeout explicitly to **600000 milliseconds (10 minutes)** for the Codex generation command. Do not inherit a short default such as 120 seconds. This is a host execution setting, not a flag to add to `codex exec`.
- A timeout does not prove generation failed or stopped. Report the exact error and check the original process and native output locations for recoverable results before proposing another attempt. Do not start a duplicate while the original is still running.
- Recover and verify an existing output when available. If no usable output is found, obtain explicit authorization before retrying; never retry automatically or switch generation routes to evade the timeout.

1. Verify native output exists, is nonempty, decodes and can be visually inspected. Compare against approved brief and references.
2. If alpha is required, inspect decoded alpha pixels and verify transparent and opaque pixels. A checkerboard in RGB is not transparency. Composite over dark and light backgrounds; inspect halos, matte color and premultiplication. Never promise real alpha. If absent, stop and ask for an approved alternative/removal route; do not silently key or destructively remove background.
3. Review projected display size and relevant crops/selected states. For sets, compare framing, silhouette, scale and style together. Review reusable art without runtime effects masking defects.
4. Copy the verified original to a stable candidate package following the consuming project's existing conventions. Keep approved source/master distinct from production derivatives; never overwrite approved files. Preserve high-quality native/master source. Choose reproducible PNG or WebP only where suitable (WebP only when required alpha is verified); do not blanket-convert lossily. Record source/copy hashes, provenance/native and durable paths, tool/version/date, status, decoded dimensions/format, color space and runtime sRGB handling, derivative dimensions/ratio/size. Include minimal reproduction/conversion commands and relevant versions, not historic scratch cruft.
5. Present the inspected candidate and obtain exact-version artwork approval before promotion. Artwork approval is not derivative approval or runtime acceptance. Derivatives need separate authorization/review; integration and acceptance require actual-consumer verification and separate approval.

If decode, alpha verification, provenance, copy, inspection, or approval is incomplete, label candidate and report remaining work. Do not claim production handoff without real inspected art and provenance.

## Prompt template

```text
Asset and role: [what this art represents and where it appears]
Approved direction: [approved description; cite authorized references]
Framing and consistency: [view/crop, silhouette, safe padding, scale]
Delivery: [agreed projected sizes, ratio/dimensions, file-size budget; mark unknowns]
Background/alpha: [real transparent pixels required, or intended background]
Constraints: [palette/material cues, exclusions; no baked text, labels, controls, glow, or animation unless approved]
Output: generate actual artwork with authorized route; report native absolute path. Do not modify unrelated files.
```

## Handoff checklist

- [ ] Approved brief and task-specific generation authorization recorded.
- [ ] Native image decodes and was visually inspected against brief.
- [ ] Required alpha verified at pixel level and on dark/light composites, or blocker/approved alternative recorded.
- [ ] Projected-size/crop and set-consistency review completed.
- [ ] Candidate path, hashes, provenance, versions/date, dimensions/format, color space and status recorded.
- [ ] Exact artwork approval, derivative approval, and runtime acceptance remain distinct.
