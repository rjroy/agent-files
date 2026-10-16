---
name: music-suno-output
description: Format a reviewed song for Suno Custom Mode, or optionally prepare per-segment style entries for Suno's studio editor. Produces text only; never generates audio.
---

# Suno output and optional studio preparation

Use this skill after the song's production design is selected. It has two text-only modes: **Suno output** (required in the songwriting pipeline) and **studio mode** (optional segment-by-segment regeneration guidance). Do not confuse preparing prompts with generating audio.

## Suno output mode

Input is a song file with concept, drafted lyrics, and production design; the expected phase is `reviewed` after review. Read the complete file, consult `music-engine-reference`, and read `../music-engine-reference/music/theory/theory-suno-formatting.md`.

Format lyrics using structure headers such as `## Verse 1` and `## Chorus` on their own lines. Put vocal processing tags in parentheses (`(Whispered)`, `(Belted)`, `(Falsetto)`) and instrumental/production tags in brackets (`[Guitar riff]`, `[Bass drop]`, `[Soft piano]`). Never mix content types on a line or put lyrics on a structure-header line.

Use the pre-written Style Field from production design (800–1000 characters; Suno maximum 1000). Check the narrative template: `[Genre] at [BPM] opening with [instrumentation], [development], [climax]. [Atmosphere]. [Emotional metaphor].` Only edit for formatting problems, including Italian tempo terms or exceeding the limit. Pull Excluded from production design and add formatting-level exclusions only when appropriate.

Before finalizing, translate abstract theme-specific style language to concrete audible descriptors, consulting the song's theme reference. For example, replace “Dead Voice” with a specific vocal/treatment description rather than leaving conceptual terminology for Suno.

Append this section to the song file and set frontmatter `phase: complete`:

```markdown
## Suno Output

**Lyrics:**
[formatted lyrics]

**Style of Music:**
[style string]

**Excluded:**
[excluded elements]
```

Verify headers are isolated, tags use the right bracket type, BPM is numeric, style follows the narrative template and is within the character limit, contains genre/BPM/instrument progression/atmosphere/emotional metaphor, theme-specific conceptual language is translated, and Excluded is populated. Return filename, ready confirmation, style string, and any formatting notes. This is copy-ready text, not an audio-generation request.

## Optional studio mode

When explicitly requested, prepare focused style strings for Suno's segment-by-segment regeneration feature. Input is a completed song file (`phase: complete`) containing lyrics with section headers, overall style, Atmospheric Reference notes, and excluded elements. Read the song completely; identify every segment (Intro, verses, pre-chorus, chorus, bridge, outro, etc.), then extract the overall genre/BPM/instrumentation, per-section intent, and exclusions.

For each segment, create a 200–400 character copy-ready style entry. Inherit the core genre, BPM, and global exclusions; reflect the segment's arc position and Atmospheric Reference; serve its specific lyric content. Include segment instrumentation focus, energy, vocal treatment where relevant, and atmosphere. Keep BPM and genre consistent unless an intentional shift is specified. Do not repeat global exclusions in every entry unless a section-specific exclusion matters.

Write `studio-prep.md` in the **same directory as the song file**:

```markdown
---
song: "[Song Title]"
source_file: [original song filename]
created: YYYY-MM-DD
purpose: Per-segment style entries for Suno studio editor
---

# Studio Prep: [Song Title]

Base production: [Genre] at [BPM]
Global excluded: [excluded elements]

---

## Intro
**Arc position:** [role]
**Style:**
```
[Copy-paste ready style string]
```

---

## Verse 1
**Arc position:** [role]
**Lyric mood:** [brief note]
**Style:**
```
[Copy-paste ready style string]
```

<!-- Continue for every segment in the lyrics, using the same format. -->

---

## Usage Notes

- Copy the style string from each section when regenerating that segment.
- These styles inherit from, but focus, the base production design.
- Excluded elements apply globally unless overridden per segment.
```

Check every lyric segment has an entry; BPM and genre are consistent (or intentional changes noted); each string is 200–400 characters; arc progression is logical; Atmospheric Reference notes are reflected; strings are copy-paste ready with no markdown inside. Return source filename, `studio-prep.md` output path, segment count/list, observations, and readiness for the studio editor. Do not render or regenerate audio.
