# Img2Img Models

Models that accept one or more reference images as input.

## Models

| Model ID | Image Param | Param Is Array | Strength Param | Cost | Notes |
|----------|-------------|---------------|----------------|------|-------|
| `black-forest-labs/flux-2-pro` | `input_images` | yes | none | $0.05 | Up to 8 reference images |
| `google/nano-banana-pro` | `image_input` | yes | none | $0.15 | Up to 14 reference images, accurate text rendering |
| `prunaai/p-image-edit` | `images` | yes | none | $0.02 | Fast edits; refer to inputs as "image 1", "image 2" in the prompt |
| `stability-ai/stable-diffusion-img2img` | `image` | no (scalar) | `prompt_strength` | — | Traditional img2img with strength control |

## Notes

- For `prunaai/p-image-edit`: reference uploaded images in the prompt by position ("image 1", "image 2"). This is how the model identifies which input to operate on.
- For `stability-ai/stable-diffusion-img2img`: `prompt_strength` controls how much the output deviates from the input image (higher = more prompt influence).
- `flux-2-pro` and `nano-banana-pro` accept multiple reference images but do not expose a strength parameter.
