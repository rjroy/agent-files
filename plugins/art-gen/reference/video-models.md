# Video Models

Image-to-video models available for generation.

## Cost Warning

Video generation costs $0.10–$1.50+ per video and takes 2–5 minutes. Always confirm with the user before generating a video.

## Models

| Model ID | Image Param | Cost/5s | Resolution | FPS | Use Case |
|----------|-------------|---------|------------|-----|----------|
| `wan-video/wan-2.2-i2v-fast` | `image` | $0.11 | 720p | 16 | Rapid iteration, budget |
| `minimax/video-01-live` | `first_frame_image` | $0.50 | 720p | 25 | Live2D, anime-style |
| `pixverse/pixverse-v4` | `image` | $0.60 | 720p | 24 | Stylized (anime, 3D, clay, cyberpunk, comic) |
| `minimax/hailuo-02` | `first_frame_image` | $0.27 | 768p | 30 | Photorealistic, human motion |
| `kwaivgi/kling-v2.5-turbo-pro` | `start_image` | $0.35 | 720p | 30 | High-quality photorealistic, cinematic |
| `kwaivgi/kling-v2.1-master` | `start_image` | $1.40 | 1080p | 30 | Maximum quality, production |

## Notes

- Image param names differ per model. Use the exact param name from the table above.
- `wan-2.2-i2v-fast` is the cheapest option for drafts and iteration.
- `kling-v2.1-master` is the highest quality but most expensive; use for final production output only.
- `hailuo-02` is the best value for photorealistic human motion.
- `pixverse-v4` is the go-to for stylized aesthetic outputs.
