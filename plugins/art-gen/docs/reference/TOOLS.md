# Available Tools

## generate_image_replicate

Generate an image using AI models via Replicate.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `prompt` | string | Yes | Text prompt describing the image |
| `model` | string | Yes | Model ID from catalog (use `list_image_models_replicate` to see options) |
| `output_file_name` | string | Yes | Filename to save (e.g., "my-image.png") |
| `output_directory` | string | No | Directory to save the output file |
| `parameters` | object | No | Model-specific settings (aspect_ratio, resolution, etc.) |

### Example Usage

**Simple generation:**
```
Generate an image using flux-2-pro: "a serene mountain landscape at sunset"
Save it as mountain-sunset.png
```

**With custom parameters:**
```
Generate an image using flux-2-pro: "cyberpunk city street, neon lights, rain"
with aspect_ratio 16:9 and resolution "2 MP"
```

### Response Format

```json
{
  "success": true,
  "model": "black-forest-labs/flux-2-pro",
  "prompt": "a serene mountain landscape at sunset",
  "saved_files": [
    "/home/user/projects/mountain-sunset.png"
  ],
  "parameters": {
    "aspect_ratio": "16:9",
    "output_format": "png"
  }
}
```

### Error Handling

If generation fails, you'll receive:

```json
{
  "success": false,
  "error": "Error message description"
}
```

Common errors:
- Invalid API token
- Model not found
- Invalid parameters
- Rate limit exceeded

---

## list_image_models_replicate

List available image generation models with descriptions and quality ratings.

### Parameters

None required.

### Example Usage

```
What image models are available?
```

### Response Format

```json
[
  {
    "model": "black-forest-labs/flux-2-pro",
    "description": "Use for final/polished images. Best quality and prompt adherence.",
    "cost": 0.05,
    "photorealism": 88,
    "artistic_quality": 82
  },
  {
    "model": "black-forest-labs/flux-schnell",
    "description": "Use for rapid iteration and drafts. Most cost-efficient at $0.003/image.",
    "cost": 0.003,
    "photorealism": 40,
    "artistic_quality": 35
  }
]
```

---

## get_model_parameters_replicate

Query available parameters for a specific model.

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `model` | string | Yes | Model ID (e.g., "black-forest-labs/flux-2-pro") |

### Response Format

```json
{
  "model": "black-forest-labs/flux-2-pro",
  "parameters": {
    "aspect_ratio": {
      "type": "string",
      "default": "1:1",
      "options": ["1:1", "16:9", "9:16", "3:2", "2:3", "4:5", "5:4"]
    },
    "resolution": {
      "type": "string",
      "default": "1 MP",
      "options": ["0.5 MP", "1 MP", "2 MP", "4 MP"]
    }
  }
}
```

---

## Choosing the Right Model

### For Quality: Flux 2 Pro (Recommended)
- Best overall quality and prompt adherence
- Use for final/polished images
- $0.05 per image

### For Speed: Flux Schnell
- Fastest generation times ($0.003/image)
- Good for rapid iteration and drafts
- Great for testing prompts

### For Text in Images: Ideogram V3 Balanced
- Best text rendering quality
- Use for logos, posters, signs
- $0.06 per image

### For Vector Graphics: Recraft V3 SVG
- Outputs scalable vector graphics
- Use for icons and illustrations
- $0.08 per image
