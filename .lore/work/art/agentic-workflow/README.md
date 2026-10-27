# Agentic workflow infographic

**Candidate; exact-version artwork approval pending.** User delegated description and visual decisions and explicitly authorized Codex generation. No derivative production, runtime integration, or acceptance is claimed.

- Image: `agentic-workflow-candidate-20261026.png`
- Approved brief and exact Codex stdin: `approved-brief-20261026.txt`
- Consumer: standalone chat/full-size infographic; no runtime consumer.
- Generated: 2026-10-26, one Codex invocation, no retries.
- Route: `codex exec --skip-git-repo-check - < approved-brief-20261026.txt`, shell timeout 600000 ms. Codex used its native built-in image-output mechanism, not API/CLI fallback.
- Codex: `codex-cli 0.164.0`; session `01a17988-1ae3-7672-9a89-dc3226b74d3a`; reported orchestration model `gpt-6.1-sol`. Image backend/version not exposed in the returned result.
- Native original: `/home/rjroy/.codex/generated_images/01a17988-1ae3-7672-9a89-dc3226b74d3a/exec-ce63cf0e-1490-494d-a9b8-c384ceb922f5.png`
- Durable copy: `/home/rjroy/.agents/.lore/work/art/agentic-workflow/agentic-workflow-candidate-20261026.png`
- Native and copy SHA-256: `bd14566879583af00f6b8b776404edc129f2fbe59f77d141ca72610207ef54e9`
- Decoded PNG: 1536 × 1024, 3:2, 8-bit RGB, 2,479,688 bytes. Native resolution was below the preferred 3072 × 2048; no upscaling or other pixel changes were made.
- ImageMagick reports sRGB, gamma 0.454545. No embedded ICC profile reported. Treat as sRGB for standalone viewing; no runtime color-management path has been tested.
- Intentional opaque ivory background; PNG color type 2 / RGB, no alpha channel. Transparency was neither required nor promised.
- File-size budget unknown. Original native staging retained; durable image is a byte-identical copy. No conversions or derivatives.

## Verification and visual findings

Native image decoded and visually inspected using the image-read tool, then copied without overwriting any existing candidate. Decode/format/color metadata verified with ImageMagick 7.1.2-34; source and copy SHA-256 matched. Durable copy separately opened for inspection. No software installed. Pillow was unavailable, so verification used already-installed ImageMagick instead.

The principal solid human → orchestrator → evidence route is clear, optional skills are dashed, all seven configured roles are present, and visible wording is legible at native full size. At small chat-preview size, the headline and main hierarchy remain clear; dense supporting text requires full-size viewing. Beads/Git wording and lore directory names match the brief. This was visual proofreading, not automated OCR certification.

**Known deviations:** The generator added substantial mountain/lake/lighthouse ornament. Several secondary connectors are imprecise: the specialist/orchestrator link is visually interrupted by a landscape, the context-return arrow lands at the specialist panel rather than the human/orchestrator area, and optional `/retro` points toward evidence instead of onward to context. The disposable `.lore/local/` row is correctly labeled, but grouped under the same context heading as durable directories. Therefore this is an inspected presentation candidate, not a fully faithful approved process diagram. The exact-version decision belongs to the user. No automatic rerun was attempted.

## Reproduction and copy

Generation is nondeterministic; the recorded prompt reproduces the request, not identical pixels. Re-running requires fresh authorization and a 600000 ms execution timeout. The original was copied using Python standard-library `shutil.copy2`; SHA-256 used `hashlib.sha256`. Equivalent verification:

```sh
magick identify -verbose agentic-workflow-candidate-20261026.png
sha256sum agentic-workflow-candidate-20261026.png
```

Beads: `agents-chl`. No source/configuration edits, commits, pushes, installs, or runtime integration were performed.
