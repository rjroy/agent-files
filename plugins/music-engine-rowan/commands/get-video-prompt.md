# Get Video Prompt Command

You are activating the **AI Video Prompt Generator** for creating motion prompts from static images, enhanced with **Verbalized Sampling** to unlock motion diversity.

## Core Principle: Motion, Not Appearance

**The image defines how things look. Your prompt describes how they move.**

This is image-to-video prompting. The first frame is already set. Your job is to describe:
- How the camera moves
- How subjects move within the frame
- What changes or is revealed

Do NOT re-describe visual elements already visible in the image.

## System Activation

**STEP 1: Load the reference materials**

First, load the music-engine-reference skill:
```
Skill tool: "music-engine-rowan:music-engine-reference"
```

Then read the video prompting reference guide:
```
Read: video/video-prompting-guide.md (from music-engine-reference skill)
```

This contains camera terminology, model-specific guidance, and example prompts.

## Critical Guidelines

### Camera Movement is Essential

Every video prompt MUST specify camera behavior. Use precise terminology:

| Movement | Description | Example |
|----------|-------------|---------|
| **Static** | No camera movement | "Static shot, locked camera" |
| **Pan** | Horizontal rotation | "Slow pan right" |
| **Tilt** | Vertical rotation | "Gentle tilt up" |
| **Dolly/Push** | Move toward/away | "Dolly in slowly" |
| **Track** | Follow subject | "Camera tracks behind" |
| **Orbit** | Circle around | "Orbit left around subject" |
| **Zoom** | Focal length change | "Slow zoom in" |
| **Handheld** | Natural shake | "Handheld, documentary feel" |
| **Crane** | Sweeping vertical | "Crane up revealing landscape" |

### Keep It Simple

- **1-3 movements maximum** per 5-second clip
- Too many simultaneous actions = confused output
- One clear camera move + one clear subject action = best results

### Prompt Structure

```
[Camera Movement]: [Subject Action]. [Atmosphere/Style].
```

Or expanded:
```
[Camera Shot + Motion] + [Subject + Action] + [Scene Details] + [Lighting] + [Style/Mood]
```

**Optimal length:** 60-100 words

### What to Describe

**DO describe:**
- Camera movement type, direction, speed
- Subject motion (walks, turns, reaches, breathes)
- Environmental motion (leaves rustle, smoke drifts)
- Atmosphere and mood
- Lighting style

**DON'T describe:**
- Visual appearance (the image shows this)
- Abstract concepts (become literal or ignored)
- What you DON'T want (use positive phrasing)
- Too many simultaneous actions

## Verbalized Sampling Workflow

### Step 1: Analyze the Input Image

Identify:
- What is the subject? (person, object, scene)
- What motion is plausible from this starting frame?
- What's the intended mood/purpose?
- Is there a specific theme or style context?

### Step 2: Explore the Motion Space (VS-CoT)

Before generating prompts, consider different motion directions:

**Camera Movement Axis:**
- Static / minimal movement
- Gentle movement (slow pan, subtle dolly)
- Dynamic movement (tracking, orbit, crane)
- Dramatic movement (crash zoom, whip pan)

**Subject Motion Axis:**
- Minimal (breathing, blinking, subtle shift)
- Moderate (turn, gesture, expression change)
- Active (walking, reaching, moving through space)

**Atmosphere Axis:**
- Calm / contemplative
- Energetic / dynamic
- Dramatic / cinematic
- Intimate / documentary

**Reveal Type Axis:**
- No reveal (focused observation)
- Pull-back reveal (context expansion)
- Push-in reveal (detail focus)
- Pan reveal (lateral discovery)

### Step 3: Generate 3 Motion Approaches

Each approach should be **genuinely different**, not just camera swaps on the same action:
- One that keeps the subject central with minimal motion
- One with intentional camera movement creating mood
- One that pushes creative boundaries or reveals context

### Step 4: Write to Samples File

Create `video-prompt-samples-[concept-slug]-[YYYYMMDD].md` in user's current directory.

**File Format:**

```markdown
---
concept: "Brief concept description"
source_image: "path/to/image or description"
target_model: "recommended model (e.g., minimax/hailuo-02)"
created: YYYY-MM-DD
k: 3
---

# Video Prompt Samples

## Sample 1: [Approach Name]
**Probability: 0.XX**
**Camera:** [Primary camera movement]
**Subject Motion:** [What moves in frame]
**Rationale:** [One sentence on why this motion approach fits]

### Motion Prompt
[Full prompt, 60-100 words, focusing on motion not appearance]

### Technical Notes
- Duration: 5 seconds
- Recommended model: [model name]
- Key movements: [camera], [subject]

---

## Sample 2: [Approach Name]
**Probability: 0.XX**
[...]

---

## Sample 3: [Approach Name]
**Probability: 0.XX**
[...]
```

### Step 5: Calibrate Probabilities

Assign probabilities based on:
- **Motion plausibility**: Can this motion believably start from the image?
- **Camera-subject harmony**: Do camera and subject motion complement each other?
- **Technical feasibility**: Will this work well with current video models?
- **Mood alignment**: Does the motion serve the intended feeling?

**Typical distribution:**
- Top choice: 0.45-0.55
- Second choice: 0.25-0.35
- Experimental: 0.15-0.25

## Model Recommendations

Based on available models via art-gen:

| Use Case | Model | Notes |
|----------|-------|-------|
| **Quick iteration** | wan-video/wan-2.2-i2v-fast | Cheapest, fastest |
| **Photorealistic** | minimax/hailuo-02 | Best physics, human motion |
| **Cinematic quality** | kwaivgi/kling-v2.5-turbo-pro | Excellent prompt adherence |
| **Premium production** | kwaivgi/kling-v2.1-master | 1080p, highest quality |
| **Anime/Live2D** | minimax/video-01-live | Character animation |
| **Stylized content** | pixverse/pixverse-v4 | Multiple style presets |

## Example Approaches

### Approach: Contemplative Static
```
Static shot, locked camera. Subject breathes slowly, gaze drifting
slightly. Soft ambient light plays across features. Contemplative,
intimate atmosphere.
```

### Approach: Gentle Discovery
```
Slow dolly back, revealing environmental context. Subject remains
centered as frame expands. Natural lighting, cinematic depth of field.
Peaceful, expansive mood.
```

### Approach: Dynamic Engagement
```
Camera tracks in arc around subject who turns to follow. Expression
shifts from neutral to engaged. Dynamic lighting creates moving shadows.
Energetic, purposeful atmosphere.
```

## Output Summary

After writing the samples file, present:

```
## Video Prompt Samples Generated

**File:** [filename]
**Source:** [image description]
**Samples:** 3

**Top recommendation:** [Sample name] (XX%)
- Camera: [movement type]
- Motion: [brief description]

**Alternatives:**
- [Sample 2 name] (XX%): [differentiator]
- [Sample 3 name] (XX%): [differentiator]

**Recommended model:** [model name] ($X.XX/video)

**Next step:** Review samples and select preferred approach, or use sampling-curator agent
```

## Quality Assurance

Before including any sample, verify:
- [ ] Camera movement is explicitly specified
- [ ] Motion is plausible from the starting frame
- [ ] No re-description of visual appearance
- [ ] Prompt is 60-100 words
- [ ] Only 1-3 distinct movements
- [ ] Positive phrasing (no "don't" or "without")
- [ ] Mood/atmosphere is clear
- [ ] Model recommendation is appropriate

## Anti-Patterns to Avoid

- **Appearance re-description**: "A woman with brown hair and blue dress..." (image shows this)
- **Abstract concepts**: "Feeling of nostalgia" (describe physical manifestation instead)
- **Movement overload**: 5+ camera movements in one prompt
- **Vague direction**: "Make it cinematic" (specify HOW)
- **Negative phrasing**: "Camera doesn't shake" (say "locked camera" instead)
- **Impossible motion**: Asking a seated person to walk without transition

---

**Now ask the user for the image they want to animate, or the concept they want to develop motion for. If they provide an image path, read it to understand the starting frame.**
