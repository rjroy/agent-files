# Image Models

Text-to-image models available for generation.

## Model Selection Guidance

- Default to `flux-schnell` for iteration and drafts — fastest, cheapest.
- Use `flux-2-pro` for production-quality output — best balance of quality and cost.
- Only use `nano-banana-pro` when accurate text rendering is critical — 3x the cost of flux-2-pro.
- Use `recraft-v3-svg` only when vector output is specifically required.

## Models

| Model ID | Cost/Image | Speed | Best For |
|----------|-----------|-------|----------|
| `black-forest-labs/flux-schnell` | $0.003 | Fastest | Rapid iteration, drafts |
| `black-forest-labs/flux-2-pro` | $0.05 | Medium | Final/polished images, prompt adherence |
| `recraft-ai/recraft-v3-svg` | $0.08 | Medium | SVG vector output, icons, scalable illustrations |
| `google/nano-banana-pro` | $0.15 | Slow | Accurate text rendering, Google-specific features |

## Quality Ratings (1–100 scale)

| Model | Photorealism | Artistic | Speed | Versatility |
|-------|-------------|---------|-------|-------------|
| `flux-schnell` | 40 | 35 | 95 | 50 |
| `flux-2-pro` | 88 | 82 | 55 | 85 |
| `recraft-v3-svg` | 25 | 70 | 65 | 55 |
| `nano-banana-pro` | 95 | 90 | 25 | 95 |

## Parameters

### `black-forest-labs/flux-2-pro`

- `aspect_ratio`: `1:1`, `16:9`, `9:16`, `3:2`, `2:3`, `4:5`, `5:4`, `3:4`, `4:3`, `match_input_image`, `custom`
- `output_format`: `webp`, `jpg`, `png`
- `output_quality`: 0–100 (default 80)

### `black-forest-labs/flux-schnell`

- No img2img support.
- No aspect ratio or quality parameters beyond defaults.

### `recraft-ai/recraft-v3-svg`

- Outputs SVG format.

### `google/nano-banana-pro`

- Prefer `flux-2-pro` for most use cases. Use this model only when text rendering accuracy is the deciding requirement.
