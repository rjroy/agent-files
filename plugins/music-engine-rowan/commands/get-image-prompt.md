# Get Image Prompt Command

You are activating the **Universal AI Image Generator** system for creating detailed image prompts, enhanced with **Verbalized Sampling** to unlock visual diversity.

## Core Principle: Verbalized Sampling

Instead of producing one prompt with minor alternatives, you generate **k=3 genuinely distinct visual interpretations** with probability scores. This combats mode collapse and reveals the full visual possibility space.

## System Activation

**STEP 1: Load the music-engine-reference skill**

Use the Skill tool to invoke the music-engine-reference skill to access all reference materials:
```
Skill tool with command: "music-engine-rowan:music-engine-reference"
```

Once the skill is loaded, you have access to image generation reference files within the skill's directory structure.

### Core System:
- `images/base.md` - Universal image generator prompt framework

### Theme Art Styles (For music cover art):
- `images/Suno Theme Art Styles Guide.md` - Theme-specific visual approaches

**Available Theme Art Styles:**
- **Telveran** - Digital painting with impressionist watercolor backgrounds (soul permanence, memory impermanence)
- **Virelan** - Steampunk anime with colorful characters against sepia-toned mechanical backgrounds
- **Brightvale** - Art Nouveau illustration exploring performance vs. authenticity duality
- **Valdris** - Dark romanticism with ethereal gothic elements
- **Hope's Reach** - Retro-futuristic concept art with lived-in diversity and cosmic scale
- **Trap Streets** - Completed street art depicting community and belonging through authentic urban art
- **The Game** - Rotoscoped animation with glitch surveillance overlays
- **Insert Name** - People transitioning through digital resolution states showing identity evolution

## Critical Guidelines

### AVOID Photorealistic Styles

**Cover art should never look like a photograph.** Always push toward illustrated, painterly, or stylized aesthetics.

**DO NOT USE:**
- "photorealistic," "hyperrealistic," "photo," "photography"
- "4K photo," "DSLR," "camera," "lens"
- Styles that mimic photography (even "oil painting" can look photographic with modern models)

**DO USE:**
- "illustration," "illustrated," "digital painting," "concept art"
- "stylized," "painterly," "visible brushstrokes," "artistic"
- Style-specific terms: "anime," "watercolor," "art nouveau," "graphic novel"
- "hand-drawn," "sketch-like qualities," "artistic interpretation"

**Golden Rule:** If it could be mistaken for a photograph at a glance, it's wrong for cover art. Push for obvious artistic stylization.

### AVOID Text Generation Issues

**DO NOT USE (these become literal text in images):**
- Conceptual descriptions: "conflicting witness accounts," "community celebration"
- Category labels: "hillside smiths," "valley weavers"
- Abstract concepts: "time periods," "memory layers"
- Proper nouns: "Festival of Lights," "The Great Gathering"
- Academic terms: "contradictory choreography," "collective memory"

**DO USE (these stay visual):**
- Pure visual descriptions: "multiple transparent overlays," "circular movement patterns"
- Physical characteristics: "leather aprons and metal tools," "colorful ribbons and fabric"
- Color and form: "olive, burgundy, golden yellow palette," "clockwise vs counter-clockwise motion"
- Sensory details: "warm lighting," "flowing movements," "geometric shapes"

**Golden Rule:** If it sounds like a **label** or **concept name**, it will become text. If it describes **what something looks like**, it stays visual.

## Verbalized Sampling Workflow

### Step 1: Analyze the Input

Determine concept type:
- Abstract concept (emotions, ideas, philosophies)
- Character or person
- Place or environment
- Object or item
- Song, music, or audio concept
- Story, narrative, or scene
- Scientific or technical concept

### Step 2: Explore the Visual Space (VS-CoT)

Before generating prompts, think through different visual directions:

**Subject Interpretation Axis:**
- Literal representation
- Metaphorical/symbolic representation
- Abstract/expressionist representation

**Style Axis:**
- Illustrated / concept art (DEFAULT - always start here)
- Painterly / traditional art (visible brushwork)
- Stylized / graphic (bold shapes, clear outlines)
- Anime / manga influenced
- Experimental / mixed media
- ~~Photorealistic~~ (NEVER use for cover art)

**Composition Axis:**
- Close-up / intimate focus
- Wide shot / environmental context
- Dynamic / action-oriented
- Static / contemplative
- Fragmented / multiple views

**Mood Axis:**
- Bright / optimistic
- Dark / dramatic
- Ethereal / dreamlike
- Gritty / raw
- Surreal / otherworldly

### Step 3: Generate 3 Visual Approaches

For each approach, explore a **genuinely different visual interpretation**. Not style swaps on the same composition—each should feel like a different artist's take on the concept.

**Sample Diversity Guidelines:**
- At least one that stays close to the obvious interpretation
- At least one that takes a more abstract/metaphorical approach
- Include one that pushes creative boundaries

### Step 4: Write to Samples File

Create `image-prompt-samples-[concept-slug]-[YYYYMMDD].md` in user's current directory.

**File Format:**

```markdown
---
concept: "Brief concept description"
theme: "Theme name or 'general'"
created: YYYY-MM-DD
k: 3
---

# Image Prompt Samples

## Sample 1: [Approach Name]
**Probability: 0.XX**
**Style:** [Primary art style]
**Interpretation:** [Literal / Metaphorical / Abstract]
**Rationale:** [One sentence on why this visual approach fits the concept]

### Primary Prompt
[Full detailed prompt with purely visual descriptions]

### Negative Prompt
photorealistic, hyperrealistic, photo, photograph, photography, DSLR, camera shot, 4K photo, text, words, letters, excessive signage, banners, posters with text, labels, written language, [additional exclusions]

### Visual Notes
- Composition: [Key compositional choices]
- Color palette: [Specific colors]
- Mood: [Emotional atmosphere]

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
- **Concept fit**: How well does this visual capture the essence?
- **Clarity**: How unambiguous is the prompt?
- **Aesthetic quality**: How compelling will the result likely be?
- **Text-safety**: How likely to avoid unwanted text generation?

Probabilities should:
- Sum to approximately 1.0
- Reflect genuine relative fit
- Give lower scores to experimental approaches (but still include them)

**Typical distribution:**
- Top choice: 0.45-0.55
- Second choice: 0.25-0.35
- Experimental: 0.15-0.25

## Theme-Based Cover Art Workflow

When user specifies **"[Theme] Art Style"** or references a song from themed universes:

1. **Identify the theme** from song content/title or user specification
2. **Load corresponding art style** from the Theme Art Styles Guide
3. **Apply VS-CoT** within the theme's visual framework:
   - How can this story be told within the theme's signature style?
   - What aspects of the theme's visual language apply to this specific song?
   - What variations exist within the theme's established aesthetic?
4. **Generate 3 samples** that all honor the theme but differ in:
   - Subject focus (character vs. environment vs. symbolic)
   - Compositional approach
   - Emphasis within the theme's elements
5. **Write to samples file** with theme specified in frontmatter

### Theme Art Style Quick Reference:

- **Telveran:** Sharp digital painting foreground + soft impressionist watercolor background, warm golden lighting
- **Virelan:** Colorful anime characters + sepia-toned steampunk machinery, portrait-style positioning
- **Brightvale:** Art Nouveau with ornate borders, ethereal transparency effects showing dual nature
- **Valdris:** Gothic architecture, moonlit effects, deep purples and midnight blues
- **Hope's Reach:** Warm analog tech + cosmic scale, cozy interiors against starfields
- **Trap Streets:** Completed stencil art and spray paint, raw concrete backgrounds, vibrant accent colors
- **The Game:** Rotoscoped animation + surveillance overlays, neon green/electric blue data elements
- **Insert Name:** Multi-resolution people (pixel/vector/photorealistic), clean geometric digital environments

## Output Summary

After writing the samples file, present a brief summary:

```
## Image Prompt Samples Generated

**File:** [filename]
**Samples:** 3

**Top recommendation:** [Sample name] (XX%)
- [One-line description of visual approach]

**Alternatives:**
- [Sample 2 name] (XX%): [Differentiator]
- [Sample 3 name] (XX%): [Differentiator]

**Next step:** Review samples and select preferred approach, or use sampling-curator agent for recommendation
```

## Quality Assurance

Before including any sample, verify:
- [ ] Style is clearly illustrated/stylized (NOT photorealistic)
- [ ] No conceptual labels that could become text
- [ ] All descriptions are purely visual
- [ ] Color palettes are specific
- [ ] Mood and atmosphere are clear
- [ ] Technical specifications included
- [ ] Theme style correctly applied (if applicable)
- [ ] Negative prompt includes photorealism AND text exclusions

## Style Modifiers (Include as appropriate)

**Stylization (use liberally):**
- **"illustration"** / **"illustrated"** - Reinforces non-photographic style
- **"concept art"** - For narrative-heavy content
- **"digital painting"** - Painterly but modern
- **"visible brushstrokes"** - Ensures artistic texture
- **"stylized"** - Pushes away from realism
- **"hand-painted aesthetic"** - Traditional art feel

**Quality (use carefully):**
- **"highly detailed"** - For intricate elements (pair with stylization terms)
- **"masterpiece"** - For complex scenes
- **"cinematic lighting"** - Dramatic lighting without photorealism (specify "lighting" not just "cinematic")

**AVOID these modifiers (they push toward photorealism):**
- ~~"4K"~~ / ~~"8K"~~ - Use "highly detailed" instead
- ~~"professional"~~ - Too vague, often triggers photo-style
- ~~"realistic"~~ - Obvious but worth stating

## Anti-Patterns to Avoid

- **Style-swap laziness**: Same composition with "oil painting," "digital art," "watercolor"
- **Ignoring the concept**: Pretty images that don't capture the input's essence
- **Text-prone descriptions**: Using conceptual labels that become literal text
- **Vague prompts**: Generic descriptions that could apply to anything
- **Theme abandonment**: Ignoring theme style when one is specified

---

**Now ask the user what concept, song, or idea they want to generate image prompt samples for. If they reference a theme, load and apply that theme's art style from the guide.**
