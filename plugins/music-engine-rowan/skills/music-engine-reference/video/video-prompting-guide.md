---
description: Best practices for AI video generation prompts, focusing on image-to-video workflows
source: Multiple sources (see citations below)
download_date: 2025-12-04
---

# AI Video Prompting Guide

Research compiled from industry guides and best practices for image-to-video AI generation.

## Core Principle: Motion, Not Appearance

**The image defines how things look. Your prompt describes how they move.**

This is the fundamental difference between image and video prompting. With image-to-video:
- The first frame is already set
- Your job is to describe motion, change, and camera behavior
- Avoid re-describing visual elements already in the image

> "Your image already defines how things appear. Your job is to describe how they move. Talk about what should change, move, or be revealed."
> — [InVideo](https://invideo.io/blog/best-prompts-for-ai-image-to-video/)

## Prompt Structure

### Recommended Formula

```
[Camera Movement] + [Subject Action] + [Scene Details] + [Atmosphere/Style]
```

Or more detailed:
```
[Camera Shot + Motion] + [Subject + Description] + [Action] + [Scene + Description] + [Lighting] + [Style/Mood]
```

### Optimal Length

60-100 words. Rich in detail but focused on what's happening in the frame.

### Key Components

| Component | What to Include |
|-----------|----------------|
| **Camera Movement** | Type, direction, speed, style |
| **Subject Motion** | Physical movements, expressions, gestures |
| **Scene Context** | Time of day, weather, location |
| **Atmosphere** | Emotional tone, mood |
| **Lighting** | Quality, direction, style |
| **Style** | Cinematic approach, aesthetic |

## Camera Movement Terminology

### Movement Types

| Term | Description | AI Prompt Usage |
|------|-------------|-----------------|
| **Static/Locked** | No camera movement | "Static shot", "locked camera" |
| **Pan** | Horizontal rotation on fixed point | "Pan left", "Pan right", "Slow pan" |
| **Tilt** | Vertical rotation on fixed point | "Tilt up", "Tilt down" |
| **Dolly/Push** | Camera moves toward/away from subject | "Dolly in", "Push in", "Pull out" |
| **Truck** | Camera moves horizontally parallel to subject | "Truck left", "Truck right" |
| **Tracking** | Camera follows a moving subject | "Camera tracks behind", "Tracking shot" |
| **Zoom** | Focal length change (no physical movement) | "Zoom in", "Zoom out", "Crash zoom" |
| **Pedestal** | Camera moves vertically up/down | "Pedestal up", "Pedestal down" |
| **Orbit** | Camera circles around subject | "Orbit around subject", "360-degree orbit" |
| **Roll** | Camera rotates around lens axis | "Dutch angle roll", "Camera roll" |
| **Handheld** | Natural shake, documentary feel | "Handheld", "Handheld calm style" |
| **Crane** | Sweeping vertical movement | "Crane shot", "Crane up" |

### Intensity & Speed

- Use adjectives: "slow", "gentle", "rapid", "smooth", "sweeping"
- Some models accept numeric intensity (-10 to +10)
- Speed keywords: "slow motion", "hyperspeed", "timelapse"

### Shot Types

| Shot | Effect | When to Use |
|------|--------|-------------|
| **Close-up** | Emphasizes emotion, detail | Character moments, objects |
| **Wide shot** | Establishes scale, environment | Scene-setting, landscapes |
| **Low angle** | Conveys power, heroism | Dramatic reveals |
| **High angle** | Suggests vulnerability | Emotional moments |
| **Over-the-shoulder** | Adds intimacy | Dialogue, following |
| **Dutch angle** | Creates unease | Tension, surrealism |
| **POV** | Character perspective | Immersion |
| **FPV/Drone** | Dynamic aerial | Action, reveals |

## Subject Motion

Since appearance is defined by the image, focus on:

- **Physical movement**: "walks forward", "turns head", "reaches out"
- **Expressions**: "smiles slowly", "eyes widen"
- **Gestures**: "waves hand", "nods"
- **Environmental motion**: "leaves rustle", "water ripples", "smoke drifts"

### Action Verbs for Motion

Replace static verbs with movement:
- Instead of "is" → "glides", "drifts", "swirls"
- Instead of "stands" → "shifts weight", "breathes", "sways"

## Best Practices

### Do

1. **Be specific with camera instructions** — "Slow dolly in" not "camera moves"
2. **Use strong movement verbs** — Replace static descriptions with action
3. **Match motion to image** — Don't ask for complex movements that contradict the starting frame
4. **Keep movements limited** — 1-3 movements max per 5-second clip
5. **Add tone/style words** — "cinematic", "dreamy", "nostalgic", "moody"
6. **Describe end state for reveals** — For pull-back shots, describe what's revealed

### Don't

1. **Re-describe appearance** — The image already shows this
2. **Use negative phrasing** — Say what you want, not what you don't
3. **Be vague** — "Make it cool" or "add movement" won't work
4. **Overload with actions** — Too many simultaneous movements = confusion
5. **Use abstract concepts** — "Feeling of nostalgia" → becomes literal or ignored

## Model-Specific Notes

### Minimax Hailuo (hailuo-02)

- Best for photorealistic live-action content
- Excellent physics simulation and realistic human motion
- Works best with moderate actions (slow pans, zooms, subtle animations)
- Prompt formula: [Camera Shot + Motion] + [Subject + Description] + [Action] + [Scene + Description] + [Lighting] + [Style/Mood]

### Minimax Video-01-Live

- Optimized for anime/Live2D content
- Natural character animation
- Output matches input aspect ratio

### Kling (v2.5-turbo-pro, v2.1-master)

- Excellent prompt adherence and cinematic quality
- Strong at camera language and professional cinematography
- Master version: 1080p output, premium quality

### PixVerse v4

- Style presets: anime, 3d_animation, clay, cyberpunk, comic
- Good for stylized/artistic content

### WAN 2.2 (Fast)

- Best for rapid iteration and concept testing
- Speed-optimized, lowest cost
- Excels with: panning, pull-backs, tracking, fisheye, slow motion, timelapse

## Example Prompts

### Simple Camera Movement
```
Static shot. Woman blinks slowly, a slight smile forming. Soft ambient light.
```

### Tracking Shot
```
Camera tracks smoothly behind the subject as they walk through the forest.
Dappled sunlight filters through leaves. Cinematic, peaceful atmosphere.
```

### Dramatic Reveal
```
Slow pull-back from close-up of eye, revealing face, then full figure
standing at cliff edge. Ocean waves crash below. Golden hour lighting,
epic scale.
```

### Product Shot
```
Camera orbits right around the product. Soft light glides across the
metallic surface. Clean white background, commercial photography style.
```

### Documentary Feel
```
Handheld camera, subtle drift. Subject turns toward camera, expression
shifts from contemplation to resolve. Natural lighting, intimate documentary
feel.
```

### Anime/Stylized
```
Dynamic zoom in on character's determined expression. Hair flows in wind.
Cherry blossom petals drift past. Anime style, dramatic lighting.
```

## Sources

- [InVideo: Best AI Image to Video Prompts](https://invideo.io/blog/best-prompts-for-ai-image-to-video/)
- [Civitai's Guide to Video Gen Prompting](https://education.civitai.com/civitais-guide-to-video-gen-prompting/)
- [Runway Gen-4 Video Prompting Guide](https://help.runwayml.com/hc/en-us/articles/39789879462419-Gen-4-Video-Prompting-Guide)
- [Artlist: AI Camera Shots](https://artlist.io/blog/camera-shots-ai/)
- [Segmind: Hailuo Minimax Prompts Guide](https://blog.segmind.com/hailuo-minimax-ai-video-prompt-guide/)
- [FilmArt: Minimax Hailuo Image to Video](https://filmart.ai/minimax-hailuo-image-to-video/)
- [Roughcut Media: Cinematic Camera Movement Terms](https://roughcut.media/2025/11/03/cinematic-camera-movement-terms-for-ai-video-prompting/)
- [Imagine Art: Camera Movements](https://www.imagine.art/blogs/camera-movements)
- [Higgsfield: Camera Controls](https://higgsfield.ai/camera-controls)
