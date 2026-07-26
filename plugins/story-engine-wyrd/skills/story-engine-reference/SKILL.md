---
name: story-engine-reference
description: Reference library providing access to all story creation resources - worlds, theory modules, lenses, and format guidelines. Commands invoke this skill to load reference materials.
---

# Story Engine Reference Skill

This skill is a **passive reference library** for the story-engine-wyrd plugin. It should be invoked by commands to access materials, not presented directly to users. Commands handle user interaction and workflow orchestration.

## Purpose

The story-engine-reference skill provides organized access to:
- **Story worlds** (fictional universes with distinct identities)
- **Theory modules** (narrative craft fundamentals)
- **Genre lenses** (cross-world transformations)
- **Format guidelines** (story length and structure specifications)

## Organization

```
story-engine-reference/
├── SKILL.md (this file)
└── story/
    ├── base.md                           # Core system architecture
    ├── theory/                           # Narrative theory modules
    │   ├── theory-narrative-structure.md
    │   ├── theory-character-development.md
    │   ├── theory-prose-craft.md
    │   └── theory-dialogue-and-voice.md
    ├── worlds/                           # Story universes
    │   ├── world-telvaren.md
    │   ├── world-valdris.md
    │   ├── world-virelan.md
    │   ├── world-brightvale.md
    │   ├── world-hopes-reach.md
    │   ├── world-trap-streets.md
    │   ├── world-shattered-worlds.md
    │   └── world-insert-name.md
    ├── lenses/                           # Genre transformations
    │   ├── lens-mystery.md
    │   ├── lens-romance.md
    │   ├── lens-horror.md
    │   └── lens-coming-of-age.md
    └── formats/                          # Story format guidelines
        ├── format-flash-fiction.md
        ├── format-short-story.md
        ├── format-epic.md
        └── format-serialized.md
```

## Usage by Commands

Commands should:

1. **Invoke this skill first** using the Skill tool
2. **Load story/base.md** to understand system architecture
3. **Load materials contextually** based on workflow phase:
   - Phase 1 (Concept): world + lens + theory-narrative-structure + format
   - Phase 2 (Development): theory-character-development
   - Phase 3 (Execution): theory-prose-craft + theory-dialogue-and-voice
4. **Drop previous context** when moving to next phase (avoid cognitive overload)

## Reference File Structure

### Story Worlds

Each world file provides:
- World concept and unique mechanics
- Character archetypes
- Typical conflicts and themes
- Narrative conventions
- Tone and atmosphere
- Visual/sensory elements

**Current worlds:**
- **Telvaren** - Memory-shifting reality where what's remembered becomes truth
- **Valdris** - Gothic realm with Valdris the Whisperer as bridge between life and death
- **Virelan** - Sacred industrial steampunk where divine judgment operates through machinery
- **Brightvale** - Performance vs authenticity, survival through emotional labor
- **Hope's Reach** - Deep space vessel where music is survival technology for one unified people
- **Trap Streets** - Hidden pocket dimensions for the unwelcome and displaced
- **Shattered Worlds** - Walking apocalypses where The Walker triggers reality cessation at human scale
- **Insert Name** - Digital realm where programs evolve beyond their original functions

### Genre Lenses

Lenses transform any world's story by applying genre conventions:
- **Mystery** - Investigation, clues, revelation
- **Romance** - Relationship dynamics, emotional arcs
- **Horror** - Suspense, dread, uncanny elements
- **Coming-of-Age** - Growth, identity, transformation

Lenses are **additive** - they work WITH world mechanics, not replace them.

### Theory Modules

Modular narrative craft fundamentals:
- **Narrative Structure** - Plot, pacing, conflict, tension
- **Character Development** - Arcs, motivations, relationships, depth
- **Prose Craft** - Description, style, voice, sensory detail
- **Dialogue and Voice** - Character speech, authenticity, subtext

### Agent-Specific Theory Loading

Each agent loads only the theory modules relevant to its task:

- **concept-developer** → `theory-narrative-structure.md` + world file + lens file (if applicable)
- **character-builder** → `theory-character-development.md` + world file
- **prose-writer** → `theory-prose-craft.md` + `theory-dialogue-and-voice.md`
- **quality-checker** → reads rubrics file (no theory needed)
- **continuity-validator** → reads story bible files (no theory needed)

### Format Guidelines

Story length and structure specifications:
- **Flash Fiction** - 100-1000 words, single moment/revelation
- **Short Story** - 1000-5000 words, complete arc
- **Epic** - Multi-chapter, complex plotting, expansive scope
- **Serialized** - Chapter-by-chapter structure for ongoing narratives

## Integration Pattern

**Example workflow (from write-story command):**

```markdown
## Step 1: Load Reference Skill

Use the Skill tool:
- command: "story-engine-wyrd:story-engine-reference"

## Step 2: Load Core Architecture

Read file:
- story-engine-reference/story/base.md

## Step 3: Load Contextual Materials

Based on user selections, read:
- World file (e.g., story/worlds/world-telvaren.md)
- Lens file if applicable (e.g., story/lenses/lens-mystery.md)
- Theory module (e.g., story/theory/theory-narrative-structure.md)
- Format guidelines (e.g., story/formats/format-short-story.md)
```

## Key Principles

1. **Passive library** - This skill doesn't drive interaction, commands do
2. **Contextual loading** - Load only what's needed per workflow phase
3. **Drop previous context** - Release loaded materials when moving forward
4. **Modular combination** - World + Lens + Format creates infinite variety
5. **Theory grounding** - All creation decisions reference loaded theory

## Commands That Use This Skill

- `/story-engine-wyrd:write-story` - Main story creation workflow
- `/story-engine-wyrd:develop-character` - Character development helper
- `/story-engine-wyrd:plan-plot` - Plot structure planning

## Note on User Interaction

When this skill is loaded, DO NOT:
- Present all reference materials to the user
- List all available options unprompted
- Dump theory content unnecessarily

Instead:
- Load materials silently as needed
- Use loaded materials to inform your creation process
- Present only the final creative output to users
- Reference theory in quality checkpoints (internal validation)
