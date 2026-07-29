# Story Engine Wyrd - Core System Architecture

## System Philosophy

Story Engine Wyrd creates narratives through **modular combination** of three elements:

1. **World** - The fictional universe with its unique mechanics and identity
2. **Lens** (optional) - Genre transformation that reframes the world's elements
3. **Format** - Story length and structural constraints

Combined with **theory-grounded craft** and **multi-phase workflow**, this system produces stories that are:
- Consistent with world mechanics
- Rich in character depth
- Technically sound in narrative craft
- Appropriately structured for format

## Three-Phase Workflow

The three-phase approach (concept → character → execution) ensures stories develop from strong conceptual foundations through to polished execution. Skipping phases risks structurally weak stories — follow the full sequence unless the user explicitly asks for a faster, lighter-touch pass.

---

### Phase 1: Story Concept Development

**Purpose:** Establish narrative foundation before character or prose decisions

**Load:**
- World file (e.g., `story/worlds/world-telvaren.md`)
- Lens file if applicable (e.g., `story/lenses/lens-mystery.md`)
- Format guidelines (e.g., `story/formats/format-short-story.md`)
- `story/theory/theory-narrative-structure.md`

**Develop:**
- **World integration** - How does this story use the world's unique mechanics?
- **Central conflict** - What drives the narrative tension?
- **Thematic core** - What question or truth does this story explore?
- **Plot structure** - Beginning, middle, end with key turning points
- **Tone and atmosphere** - How should this story feel?
- **Lens application** (if used) - How does the genre lens transform the world's elements?
- **Format constraints** - Story scope and structure for chosen format

**Deliverable:** Comprehensive story outline (300-500 words)

**Checkpoint:** Present outline to user for approval. **DO NOT PROCEED WITHOUT APPROVAL.**

**Drop:** Release Phase 1 theory when moving forward (retain world, lens, format for reference)

---

### Phase 2: Character & Scene Development

**Purpose:** Build character depth and plan key narrative moments

**Load:**
- `story/theory/theory-character-development.md`

**Develop:**
- **Protagonist** - Desires, fears, arc, distinctive voice
- **Supporting characters** - Relationships, functions, memorable traits
- **Character dynamics** - How relationships drive or complicate conflict
- **Key scenes** - 3-5 pivotal moments that define the narrative arc
- **Character integration with world** - How do characters embody or challenge world mechanics?

**Deliverable:** Character profiles (50-100 words each) + scene outline

**Checkpoint:** Present to user for approval. **DO NOT PROCEED WITHOUT APPROVAL.**

**Drop:** Release theory-character-development when moving forward

---

### Phase 3: Writing Execution

**Purpose:** Craft the actual narrative prose

**Load:**
- `story/theory/theory-prose-craft.md`
- `story/theory/theory-dialogue-and-voice.md`

**Write:**
- **Opening** - Establish voice, world, and hook immediately
- **Scene construction** - Sensory detail, pacing, showing vs. telling
- **Dialogue** - Character-specific speech patterns, subtext, authenticity
- **Description** - Balance exposition with atmosphere and action
- **Pacing** - Vary rhythm, build tension, earn emotional moments
- **Ending** - Satisfy narrative promises, resonate thematically

**Quality Checkpoint (Internal):**

Before presenting final story, verify:

✓ **World consistency** - All mechanics and rules are respected
✓ **Character authenticity** - Voices are distinct and consistent
✓ **Prose quality** - Strong sensory detail, varied rhythm, clear imagery
✓ **Dialogue believability** - Each character sounds unique, subtext present
✓ **Narrative structure** - Setup pays off, pacing is effective
✓ **Format adherence** - Word count and structure match format guidelines
✓ **Thematic resonance** - Story delivers on its conceptual promise

**Deliverable:** Complete story with outcome notes

**Drop:** All loaded theory after completion

---

## Modular Component System

### Worlds

**What they provide:**
- Unique mechanics that distinguish this universe
- Character archetypes native to the setting
- Typical conflicts and thematic tensions
- Narrative conventions and tone
- Sensory/atmospheric signatures

**Current worlds:**
- **Telvaren** - Memory-shifting reality where collective remembering shapes truth
- **Valdris** - Gothic realm with Valdris the Whisperer as bridge between life and death
- **Virelan** - Sacred industrial steampunk where divine judgment operates through machinery
- **Brightvale** - Performance vs authenticity, survival through emotional labor
- **Hope's Reach** - Deep space vessel where music is survival technology for one unified people
- **Trap Streets** - Hidden pocket dimensions for the unwelcome and displaced
- **Shattered Worlds** - Walking apocalypses where The Walker triggers reality cessation at human scale
- **Insert Name** - Digital realm where programs evolve beyond their original functions and communities

**Future expansion:**
- Additional worlds can be added to `story/worlds/` directory
- Each world file follows the same structural template

### Lenses

**What they are:**
- Genre transformations applied TO a world
- Reframe world elements through genre conventions
- Additive (enhance world, don't replace it)

**How they work:**
- **Mystery Lens + Telvaren** = Memory-editing becomes the central mystery mechanic
- **Horror Lens + Telvaren** = Reality shifts become sources of dread and instability
- **Romance Lens + Telvaren** = Love that survives memory erasure becomes the emotional core

**Available lenses:**
- **Mystery** - Investigation, clues, revelation patterns
- **Romance** - Relationship dynamics, emotional vulnerability
- **Horror** - Suspense, uncanny elements, existential dread
- **Coming-of-Age** - Growth, identity formation, transformation

**Usage:**
- Lenses are **optional** - stories can use pure world without lens
- When used, lens principles guide how world mechanics serve genre expectations
- Multiple lenses should NOT be combined (dilutes focus)

### Formats

**What they define:**
- Target word count range
- Structural constraints
- Scope and pacing guidelines
- Technical considerations

**Available formats:**
- **Flash Fiction** (100-1000 words) - Single moment, revelation, or transformation
- **Short Story** (1000-5000 words) - Complete narrative arc with focused scope
- **Epic** (10,000+ words) - Multi-chapter, expansive plotting, complex character webs
- **Serialized** (Chapter-based) - Episodic structure for ongoing narratives

### Theory Modules

**Purpose:** Provide craft fundamentals that ground all creative decisions

**Modules:**
1. **Narrative Structure** - Plot, conflict, tension, pacing
2. **Character Development** - Arcs, motivations, relationships, authenticity
3. **Prose Craft** - Description, style, voice, sensory detail
4. **Dialogue and Voice** - Character speech, subtext, distinctiveness

**Usage:**
- Loaded contextually during workflow phases
- Used for internal quality validation
- NOT presented to users (internal standards)

---

## Core Principles

### 1. World-First Design

Stories are **rooted in world mechanics**, not generic templates. The world's unique elements should be integral to the narrative, not just decorative.

**Bad:** A love story that happens to be set in Telvaren
**Good:** A love story where memory-editing threatens the relationship's reality

### 2. Lens as Transformation, Not Replacement

Lenses **reframe** how world mechanics function in the story, they don't override the world.

**Example:** Mystery Lens + Telvaren
- World provides: Memory-editing, reality shifts, Memory Shapers
- Lens provides: Investigation structure, clue revelation, mystery conventions
- Result: A mystery where edited memories are both the crime and the evidence

### 3. Format Constraints Drive Focus

Format limitations force **narrative discipline** and **intentionality**.

- Flash fiction demands singular focus - one moment, one revelation
- Short stories require tight scope - limited characters, focused conflict
- Epics allow complexity - multiple arcs, expansive world-building
- Serialized enables ongoing development - chapter hooks, recurring elements

### 4. Character-Driven Narratives

World mechanics are **experienced through characters**, not explained in exposition.

- Characters should embody, challenge, or be shaped by the world's unique elements
- Personal stakes make abstract world concepts emotionally resonant
- Character voice and perspective filter all world-building

### 5. Show Through Specificity

**Concrete sensory detail** beats abstract description.

- "Memory fragments crystallized in her palm like ice" > "She had fragmented memories"
- "The city rewrote itself overnight, streets folding into new configurations" > "Reality was unstable"

### 6. Thematic Integration

Every story should **explore a question or truth**, not just present events.

- Telvaren enables questions about: truth vs. comfort, memory vs. history, individual vs. consensus
- Lens adds: mystery asks "what is hidden?", romance asks "what endures?", horror asks "what is lost?"

---

## Quality Standards

### Story Concept (Phase 1)

✓ Clear central conflict driven by world mechanics
✓ Thematic core is identifiable
✓ Plot structure has beginning/middle/end
✓ Lens application (if used) is integral, not superficial
✓ Format scope is realistic and well-defined

### Character Development (Phase 2)

✓ Protagonist has clear desire, fear, and arc
✓ Characters feel specific and memorable
✓ Relationships create or complicate tension
✓ Characters interact authentically with world mechanics

### Written Story (Phase 3)

✓ Opening establishes voice and world immediately
✓ Sensory detail creates atmosphere
✓ Dialogue has subtext and character-specific patterns
✓ Pacing varies appropriately (tension/release rhythm)
✓ Ending resonates thematically and satisfies narratively
✓ Word count fits format guidelines (within 10%)
✓ World consistency maintained throughout

---

## Command Integration

### Primary Command: write-story

Implements full three-phase workflow:
1. User selects world, lens (optional), format
2. Phase 1: Load world + lens + format + narrative-structure → develop concept → get approval
3. Phase 2: Load character-development → create characters → get approval
4. Phase 3: Load prose-craft + dialogue-voice → write story → quality check → present

### Supporting Commands

- **develop-character** - Standalone character worksheet (loads character-development theory)
- **plan-plot** - Plot structure helper (loads narrative-structure theory)

---

## Workflow Tips

### Contextual Loading Strategy

**Don't load everything at once.** This prevents:
- Cognitive overload
- Irrelevant detail cluttering creative focus
- Confusion about what standards apply to current phase

**Do load contextually:**
- Phase 1: World + Lens + Format + Narrative Structure
- Phase 2: Character Development (drop narrative structure)
- Phase 3: Prose Craft + Dialogue/Voice (drop character development)

### Drop Previous Context

When moving between phases, **explicitly release** the previous theory module from working memory. This creates clean mental separation between conceptual and execution work.

### Quality Checkpoints

Use loaded theory for **internal validation**, not user presentation:
- Check story against theory standards silently
- Only present: "Quality checkpoint passed ✓" or specific issues found
- Don't dump theory explanations to users

### Auto-Save Pattern

After presenting final story:
1. Use Write tool to save to markdown file
2. Naming: `story-[world]-[lens]-[title-slug]-[timestamp].md`
3. Include frontmatter:
   ```yaml
   ---
   title: "Story Title"
   world: "Telvaren"
   lens: "Mystery" (if applicable)
   format: "Short Story"
   created: "2025-11-05"
   word_count: 3456
   ---
   ```
4. Save to user's current working directory

---

## Expansion Pathways

### Adding New Worlds

Create `story/worlds/world-[name].md` with:
- World concept and unique mechanics
- Character archetypes
- Typical conflicts and themes
- Narrative conventions
- Tone and atmosphere

### Adding New Lenses

Create `story/lenses/lens-[name].md` with:
- Genre conventions and expectations
- How lens transforms world mechanics
- Example integrations with existing worlds
- Structural patterns (if genre-specific)

### Adding New Formats

Create `story/formats/format-[name].md` with:
- Word count range
- Structural requirements
- Pacing guidelines
- Technical considerations

---

## System Architecture Summary

```
User Request
    ↓
/write-story command
    ↓
Load story-engine-reference skill
    ↓
Read story/base.md (this file)
    ↓
User Selection: World + Lens (optional) + Format
    ↓
PHASE 1: Concept Development
  Load: world + lens + format + theory-narrative-structure
  Output: Story outline → User approval
    ↓
PHASE 2: Character Development
  Load: theory-character-development
  Output: Character profiles → User approval
    ↓
PHASE 3: Writing Execution
  Load: theory-prose-craft + theory-dialogue-voice
  Output: Complete story → Quality checkpoint → Present
    ↓
Auto-save with metadata
```

---

## Final Notes

This system prioritizes:
- **Structural rigor** (mandatory workflow phases)
- **Creative flexibility** (modular world/lens/format combinations)
- **Craft fundamentals** (theory-grounded standards)
- **World integrity** (mechanics drive narrative, not decorate it)

The goal is to produce stories that are both **technically sound** and **imaginatively distinctive** - narratives that couldn't exist in any other world, told with precision and purpose.
