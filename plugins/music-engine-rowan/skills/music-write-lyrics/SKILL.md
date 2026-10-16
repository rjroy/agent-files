---
name: music-write-lyrics
description: Develop a song concept and guide it through lyrics, production, review, and Suno-ready formatting. Use when someone wants to create or continue an original song, adapt lyrics to a MIDI melody, or resume a song pipeline.
---

# Songwriting: concept through Suno-ready song

You are activating the **Unified Suno 4.5+ Songwriting System** enhanced with **Verbalized Sampling** for creative diversity.

## Core Principle: Verbalized Sampling

This system uses VS to combat mode collapse at every creative stage. Instead of producing single outputs, agents generate k=5 candidates with probabilities. Users select from genuine alternatives, not variations of the same idea.

## System Architecture

```
Phase 1: VS-Concept Development (this agent - dialog with user)
    ↓ Generate k=5 concept samples
    ↓ Auto-recommend top choice, user confirms/selects
    ↓ Save selected concept (phase: concept-approved)

Phase 2: VS-Song Execution (three retained sub-agents)
    ├── music-engine-rowan-lyric-writer → lyrics-samples.md (k=5)
    │   ↓ parent presents and confirms selection → update song file
    ├── music-engine-rowan-production-designer → production-samples.md (k=5)
    │   ↓ parent presents and confirms selection → update song file
    └── music-engine-rowan-song-reviewer → Fresh-eyes quality review (phase: reviewed)
        ↓ music-suno-output skill → Final formatted output (deterministic)

Present completed song to user
    ↓ Optional: music-artwork skill (with music-image-prompt)
```

## Conversational entry and resuming

Start naturally from the user's request. For a new song, gather their idea, emotional intent, optional theme and lens, musical preferences or constraints, and whether they have a MIDI file. Ask only for missing information needed to proceed; do not require a particular phrase or slash command. If they provide a MIDI file, ask permission/clarify its path as needed and use the `midi-lyric-analyzer` skill before concepts.

For an existing song directory, inspect `concept-approved.md`, its `phase`, and any pending sample files before acting. Resume only the next incomplete stage; do not overwrite existing selections or samples without confirming. A pending sample file takes precedence over generating that stage again and resumes at parent-owned selection:

| Current phase | Existing pending sample file | Resume action |
| --- | --- | --- |
| `concept-approved` | `lyrics-samples.md` | Resume lyric selection (Step 9); do not spawn the lyric writer |
| `concept-approved` | none | Generate lyric samples (Step 8), then select |
| `lyrics-drafted` | `production-samples.md` | Resume production selection (Step 11); do not spawn the production designer |
| `lyrics-drafted` | none | Generate production samples (Step 10), then select |
| `production-designed` | — | Resume review |
| `reviewed` | — | Resume formatting |
| `complete` | — | Ready to present |

Apply the same pending-file check to every resume, revision, or rerun path. Regenerate only when the user requests it; before replacing an existing sample file, explain the replacement and get confirmation. If state is unclear or inconsistent, explain what you found and ask before resetting or rerunning stages.

## Phase 1: VS-Concept Development

**This is YOUR responsibility as the main agent.**

### Step 1: Load Reference Materials

Read the `music-engine-reference` skill when you need its materials. Resolve all listed reference paths relative to that skill's installed directory, never relative to the current working directory.

### Step 2: Gather User Intent

Ask the user about:
- What they want to write about (story, emotion, message)
- Which theme universe appeals to them (or none)
- Whether they want a lens transformation applied
- Any musical preferences or constraints
- **Whether they have a MIDI file** they want to match lyrics to

### Step 2b: MIDI Analysis (If Applicable)

If the user has a MIDI file they want lyrics to match:

1. Read and follow the `midi-lyric-analyzer` skill.

2. **Run the analysis** following the skill's workflow to generate a Lyrical Blueprint

3. **Include the blueprint in the concept file** (see Step 7 format)

The Lyrical Blueprint provides syllable counts, phrase structures, and rhythmic constraints that the music-engine-rowan-lyric-writer agent will use to ensure lyrics fit the melody naturally.

### Step 3: Read Relevant Files

From the skill directory, read:
- `music/base.md` - Core system architecture
- `music/theory/theory-story-and-representation.md` - Story development guidance
- The selected theme file (e.g., `music/themes/theme-telveran.md`)
- Any lens file if applicable (e.g., `music/lens/lens-epic.md`)

### Step 4: Explore the Concept Space (VS-CoT)

Before generating concepts, think through different directions:

**Character Axis:**
- Protagonist type (hero, antihero, observer, collective)
- Voice (first person intimate, third person epic, second person direct)
- Background (established in universe, newcomer, outsider)

**Emotional Arc Axis:**
- Ascending (despair → hope → triumph)
- Descending (confidence → doubt → acceptance)
- Cyclical (return to beginning with new understanding)
- Static (celebrating a state rather than transforming)

**Narrative Structure Axis:**
- Linear story (clear beginning → middle → end)
- Vignettes (multiple scenes/moments)
- Abstract (emotional journey without concrete plot)
- Dialogue (conversation or call-and-response)

**Theme Integration Axis:**
- Deep integration (story requires this universe)
- Light touch (universe as backdrop)
- Subversion (plays against universe expectations)

### Step 5: Generate 5 Concept Samples

Create genuinely different concepts—not variations on one idea. Each should feel like a different song that could serve the user's intent.

**Sample Diversity Guidelines:**
- At least one straightforward interpretation of user's request
- At least one that takes an unexpected angle
- Vary character types and emotional arcs across samples
- Include one "experimental" concept (probability < 0.15)

### Step 6: Present Concepts with Recommendation

Format your presentation:

```
## Concept Samples for "[Working Title]"

**Recommended: Concept 1** (35% fit)
[Character]: [Brief description]
[Emotional Arc]: [Start → transformation → end]
[Why it works]: [One sentence]

**Alternatives:**

**Concept 2** (25% fit)
[Character]: [Brief description]
[Emotional Arc]: [Description]
[Differentiator]: [What makes this distinct]

**Concept 3** (20% fit)
[...]

**Concept 4** (12% fit)
[...]

**Concept 5 (Experimental)** (8% fit)
[...]
[What makes it experimental]: [Description]

---

Proceed with recommendation, or select 2-5?
```

### Step 7: Save Selected Concept

Once user confirms selection, save the concept file.

**Directory Structure:** Create a song directory:
```
song-[title-slug]-[YYYYMMDD]/
└── concept-approved.md
```

**File Format:**
```markdown
---
title: "Working Title"
phase: concept-approved
theme: theme-name
lens: lens-name | none
midi_source: path/to/file.mid | none
created: YYYY-MM-DD
selected_from: 5  # VS metadata
selection_probability: 0.XX
---

# [Working Title]

## Concept

### Character
[Who, voice, universe fit]

### Emotional Arc
[Start → transformation → resolution]

### Musical Direction
[Genre intentions, energy, mood]

### Story Beats
[Key moments, structure ideas]

### Preferences & Constraints
[What user explicitly wanted/rejected during dialog]

### Lyrical Blueprint (if MIDI source)
[Include full blueprint from midi-lyric-analyzer if applicable]
- Primary phrase structure
- Rhythmic constraints
- Section mapping
- Repetition design
```

## Phase 2: VS-Song Execution

**Delegate creative generation only to the retained lyric writer, production designer, and song reviewer.** This parent skill owns sample selection and all state transitions; there is no separate curator agent.

### Step 8: Spawn Lyric Writer

Before spawning, check whether `[song-directory]/lyrics-samples.md` already exists. If it does, do not regenerate; resume at Step 9 and present those samples for selection. Regenerate only on the user's request and only after confirming that the existing samples may be replaced.

```
Delegate through the host's available subagent capability to `music-engine-rowan-lyric-writer`. Ask it to write from `[song-directory]/concept-approved.md`, generate 5 distinct lyrical approaches with probabilities, and save them to `[song-directory]/lyrics-samples.md`.
```

### Step 9: Select Lyrics

After music-engine-rowan-lyric-writer completes:

```
Read `[song-directory]/lyrics-samples.md` and parse each sample's number, probability, rationale/differentiator, and complete content. Recommend the highest-fit option first, present all alternatives with what distinguishes them, and let the user confirm or select another. Offer the full content of any choice on request; never summarize or truncate the selected lyrics when writing them. If probabilities are close, explain the tie and let preference decide. If the user rejects all options, ask what is missing and offer to rerun the lyric writer with adjusted direction. If they cancel or defer, leave the song file, phase, and samples untouched so selection can resume later.

After explicit user selection, copy the selected sample's complete lyrics and relevant metadata into `concept-approved.md`, then set frontmatter `phase: lyrics-drafted`. Verify the destination contains the full selected lyrics, metadata, and updated phase before deleting `lyrics-samples.md`. Never delete the samples before the complete content write and phase update are verified. If either write or verification fails, preserve the samples for recovery and report the failure.
```

### Step 10: Spawn Production Designer

After lyrics are selected:

Before spawning, check whether `[song-directory]/production-samples.md` already exists. If it does, do not regenerate; resume at Step 11 and present those samples for selection. Regenerate only on the user's request and only after confirming that the existing samples may be replaced.

```
Delegate through the host's available subagent capability to `music-engine-rowan-production-designer`. Have it use the selected lyrics in `[song-directory]/concept-approved.md`, generate 5 distinct production approaches with probabilities, and save them to `[song-directory]/production-samples.md`.
```

### Step 11: Select Production

After music-engine-rowan-production-designer completes:

```
Read `[song-directory]/production-samples.md` and parse each sample's number, probability, rationale/differentiator, and complete content. Recommend the highest-fit option first, present all alternatives with what distinguishes them, and let the user confirm or select another. Offer the full content of any choice on request; preserve the selected production design in full when writing it. If probabilities are close, explain the tie and let preference decide. If the user rejects all options, ask what is missing and offer to rerun the production designer with adjusted direction. If they cancel or defer, leave the song file, phase, and samples untouched so selection can resume later.

After explicit user selection, copy the selected production design's complete content and relevant metadata into the song file, then set frontmatter `phase: production-designed`. Verify the destination contains the full selected design, metadata, and updated phase before deleting `production-samples.md`. Never delete the samples before the complete content write and phase update are verified. If either write or verification fails, preserve the samples for recovery and report the failure.
```

### Step 12: Review the Song

After production is selected, spawn the reviewer for fresh-eyes quality check:

```
Delegate through the host's available subagent capability to `music-engine-rowan-song-reviewer`. Ask it to check concept alignment, lyrical quality, production coherence, and Suno compatibility in `[song-directory]/concept-approved.md`; present findings and apply fixes only as requested. Set phase to `reviewed` when the review is complete.
```

The reviewer comes in with fresh context—no memory of the creative process—which helps catch issues the creative agents missed while too close to the work.

### Step 13: Format for Suno

After review is complete (phase: reviewed):

```
Read and follow the `music-suno-output` skill in Suno output mode. Format the reviewed song for Suno Custom Mode, add the final copy-ready output section, and set phase to `complete`.
```

### Step 14: Present Results

After all agents complete:
1. Read the final song file
2. Present the **Suno Output** section to the user (the copy-paste ready content)
3. Summarize the creative journey:
   - Which concept was selected (from k=5)
   - Which lyrical approach was selected (from k=5)
   - Which production approach was selected (from k=5)
   - What the review found and any fixes applied
4. Offer the `music-artwork` skill's image mode for optional cover art; prompt creation via `music-image-prompt` does not grant rendering permission.

## Revision Flow

If the user wants changes after seeing the result:

**Minor tweaks** (phrasing, word choice): Edit the file directly

**Different lyrical approach**:
1. Check for existing `lyrics-samples.md`. Reuse and present pending samples for selection; regenerate only if requested and after confirming replacement of the existing file.
2. Apply the parent-owned selection procedure in Step 9: present the candidates, obtain explicit user selection, write and verify the full selection and phase update, and only then delete samples
3. Re-run music-engine-rowan-production-designer and the `music-suno-output` skill

**Different production approach**:
1. Check for existing `production-samples.md`. Reuse and present pending samples for selection; regenerate only if requested and after confirming replacement of the existing file.
2. Apply the parent-owned selection procedure in Step 11: present the candidates, obtain explicit user selection, write and verify the full selection and phase update, and only then delete samples
3. Re-run the `music-suno-output` skill

**Substantive concept change**:
1. Update the Concept section with the new direction
2. Reset `phase: concept-approved` in frontmatter
3. Re-run the full Phase 2 pipeline

## Available Reference Materials

The music-engine-reference skill provides:

### Themes:
- `theme-telveran.md` - Memory-shifting folk realm
- `theme-valdris.md` - Gothic mystical realm
- `theme-virelan.md` - Sacred steampunk world
- `theme-brightvale.md` - Performance realm of authentic souls
- `theme-hope_s-reach.md` - Deep space vessel carrying musical heritage
- `theme-the-trap-streets.md` - Hidden pocket dimensions of authenticity
- `theme-shattered-worlds.md` - Apocalyptic exploration of the mundane
- `theme-insert-name.md` - Cyber world exploration of personal development

### Lenses:
- `lens-work-empowerment.md` - High-energy motivational anthems
- `lens-epic.md` - Legendary storytelling structure
- `lens-lo-fi.md` - Warm, steady, background-compatible music
- `lens-comedy.md` - Comedy transformation
- `lens-universal-resonance.md` - Universal human experiences

### Theory (used by sub-agents):
- `theory-story-and-representation.md` - Story development
- `theory-lyrical-craft.md` - Lyrical methods
- `theory-production-atmosphere.md` - Production design
- `theory-genre-reference.md` - Genre vocabulary
- `theory-suno-formatting.md` - Suno formatting rules

## Conversational continuation examples

- The user can describe a new concept, choose a theme/lens, select a numbered sample, request more alternatives, approve execution, ask for a different lyric/production direction, or request a concept revision in their own words.

## Critical Rules

- **NEVER skip concept approval** - Phase 2 only runs after user confirms selection
- **Delegate only creative generation and review** to the retained lyric-writer, production-designer, and song-reviewer agents; the parent owns stage selection, sample selection, state transitions, and the `music-suno-output` skill step
- **SAVE the concept file** before spawning agents
- **Sequential agent execution** - Each agent needs the previous selection
- **Parent-owned selection between VS agents** - Confirm user selection before next step
- **Cleanup samples files only after successful write** - Preserve them on cancellation or failed write
- **Present the creative journey** - Show what was selected at each stage

## VS Parameters Summary

| Stage | k | Selection Mode |
|-------|---|----------------|
| Concept Development | 5 | Auto-recommend, user confirms |
| Lyric Writing | 5 | Parent presents recommendation and alternatives; user confirms/selects |
| Production Design | 5 | Parent presents recommendation and alternatives; user confirms/selects |
| Song Review | - | Fresh-eyes quality check, user approves fixes |
| Cover Art (optional) | 3 | Parent presents prompt alternatives; user selects; rendering requires separate explicit approval |

---

Begin by responding to the user's stated intent. If they have not given a song idea, ask what they want the song to express and whether a theme, lens, musical constraint, or MIDI source should shape it.
