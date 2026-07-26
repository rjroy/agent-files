# Story Engine of Wyrd

<img src="assets/logo.svg" width="120" align="right" />

A prose fiction system for creating stories across multiple formats, fictional worlds, and genre lenses. Built for writers who want collaborative AI assistance without surrendering authorship.

## Features

### Multi-Format Support
- **Flash Fiction** — Single chapter, complete story
- **Short Story** — 2–5 chapters, contained narratives
- **Epic** — 6–15 chapters, expansive world-building
- **Serialized** — 15+ chapters, novel-length narratives

### Six Distinct Story Worlds
Each world has unique mechanics, character archetypes, and narrative conventions:

- **Telvaren** — Memory-shifting reality where what's remembered becomes truth
- **Valdris** — Gothic realm with death as a navigable threshold
- **Virelan** — Sacred industrial steampunk where divine judgment operates through machinery
- **Brightvale** — Performance vs authenticity in a world of emotional survival
- **Hope's Reach** — Deep space vessel where music is survival technology
- **Trap Streets** — Hidden pocket dimensions for the unwelcome and displaced

### Genre Lenses
Transform stories across worlds using thematic lenses: mystery, romance, horror, coming-of-age.

### Verbalized Sampling
Instead of single outputs, the engine generates 5 distinct candidate approaches with probabilities for each creative decision. You select the best direction, reducing mode collapse and improving creative diversity.

### Persistent State
All work saves to `.story-state/` with metadata tracking, allowing resumption from any chapter or creative phase.

## Commands

### `/story-engine-wyrd:write-story`
Main entry point for story creation. Orchestrates multi-agent workflow for concept development, character building, prose writing, quality checking, and continuity validation.

**Input formats:**
- Natural language: `/story-engine-wyrd:write-story A cyberpunk heist across 12 chapters`
- File reference: `/story-engine-wyrd:write-story ./my-outline.md`
- Resume: `/story-engine-wyrd:write-story continue .story-state/Cyberpunk-Heist/PLAN.md`

### `/story-engine-wyrd:plan-plot`
Develop a structured plot outline before writing. Creates a chapter-by-chapter breakdown with conflict escalation and thematic arcs.

### `/story-engine-wyrd:develop-character`
Build deep character profiles with backstory, motivation, voice patterns, and relationship maps. Generates character-world interactions.

### `/story-engine-wyrd:review-story`
Comprehensive multi-pass review covering narrative structure, continuity, prose quality, character consistency, and thematic coherence. Provides revision guidance.

## Specialized Agents

The system delegates creative work to specialized agents:

- **Concept Developer** — Explores story premise, identifies core conflicts, and validates world fit
- **Character Builder** — Develops detailed character profiles with depth and consistency
- **Prose Writer** — Executes chapter writing with attention to voice, pacing, and sensory detail
- **Sampling Curator** — Evaluates 5 candidate approaches and recommends the strongest direction
- **Quality Checker** — Line-edits for prose quality, grammar, and style consistency
- **Continuity Validator** — Tracks character development, plot threads, and world consistency across chapters
- **Final Review** — Holistic assessment of narrative completeness and thematic resonance

## Skills

### `story-engine-reference`
Passive reference library providing access to story worlds, narrative theory modules, genre lenses, and format guidelines. Invoked by commands to load contextual materials.

### `story-compiler`
Aggregates completed chapters into final story documents with metadata, formatting, and optional export.

## Workflow

1. **Concept** — Specify format, world (optional), and story premise
2. **Planning** — Develop plot outline and character profiles
3. **Writing** — Generate chapters with verbalized sampling for creative decisions
4. **Review** — Multi-pass quality and continuity checking
5. **Iteration** — Resume at any point to revise or extend

## Story State

Stories store work in `.story-state/[StoryName]/`:

```
.story-state/Cyberpunk-Heist/
├── metadata.json          # Progress tracking
├── PLAN.md               # Plot outline
├── characters.md         # Character profiles
├── chapter-1.md
├── chapter-2.md
└── ...
```

Resume any story by referencing its PLAN.md file.

## Getting Started

1. **Write a story:** `/story-engine-wyrd:write-story Your story concept here`
2. **Let the engine guide you:** Respond to format and world questions
3. **Make creative decisions:** Select between 5 candidate approaches for each chapter
4. **Review and iterate:** Use the review command to assess and refine

## Theory and Craft

The engine draws from narrative craft fundamentals covering:
- Story structure and pacing
- Character development and motivation
- Prose craft and voice
- Dialogue and interaction
- World-building and setting

Reference these modules throughout the writing process for craft guidance.

## Philosophy

The Story Engine is built on three principles:

1. **Collaborative, not substitute** — You decide what happens; the engine handles execution
2. **Judgment stays with you** — Verbalized sampling gives you options, not decisions
3. **Persistent and resumable** — Your work survives interruption; resume from anywhere

## License

MIT

## Author

Ronald Roy (gsdwig@gmail.com)
