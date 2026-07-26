# Replicate API Reference

## Overview

Replicate is a platform for running machine learning models in the cloud. This server uses the Replicate API to generate images using a curated set of AI models.

## Getting Started

1. Sign up at [replicate.com](https://replicate.com)
2. Get your API token from [account settings](https://replicate.com/account/api-tokens)
3. Set the `REPLICATE_API_TOKEN` environment variable

## Available Image Models

### Flux 2 Pro (Recommended for Quality)
- **Model ID**: `black-forest-labs/flux-2-pro`
- **Cost**: $0.05 per image
- **Quality**: Excellent (88/100 photorealism)
- **Best for**: Final/polished images, production work

### Flux Schnell (Recommended for Speed)
- **Model ID**: `black-forest-labs/flux-schnell`
- **Cost**: $0.003 per image
- **Quality**: Good (40/100 photorealism)
- **Best for**: Rapid iteration, drafts, testing prompts

### Ideogram V3 Balanced (Best for Text)
- **Model ID**: `ideogram-ai/ideogram-v3-balanced`
- **Cost**: $0.06 per image
- **Quality**: Good (60/100 photorealism)
- **Best for**: Images containing text, logos, posters, signs

### Recraft V3 SVG (Vector Graphics)
- **Model ID**: `recraft-ai/recraft-v3-svg`
- **Cost**: $0.08 per image
- **Quality**: Specialized for vectors
- **Best for**: SVG output, icons, scalable illustrations

## API Usage

### Running a Prediction

```python
output = replicate_client.run(
    "black-forest-labs/flux-2-pro",
    input={
        "prompt": "a cat wearing a space suit",
        "aspect_ratio": "1:1",
        "resolution": "1 MP"
    }
)
```

### Common Parameters (Flux 2 Pro)

- `prompt` (string, required): Text description of desired image
- `aspect_ratio` (string): Image dimensions ("1:1", "16:9", "9:16", etc.)
- `resolution` (string): Output size ("0.5 MP", "1 MP", "2 MP", "4 MP")
- `output_format` (string): File format ("webp", "jpg", "png")
- `seed` (integer): Random seed for reproducible generation

## Output Format

The API returns an array of URLs pointing to the generated images:

```json
[
  "https://replicate.delivery/pbxt/..../output.png"
]
```

## Model Costs

| Model | Cost per Image |
|-------|----------------|
| flux-schnell | $0.003 |
| flux-2-pro | $0.05 |
| ideogram-v3-balanced | $0.06 |
| recraft-v3-svg | $0.08 |

## Resources

- [Replicate Documentation](https://replicate.com/docs)
- [Python Client](https://github.com/replicate/replicate-python)
- [Model Explorer](https://replicate.com/explore)
