---
name: midi-lyric-analyzer
description: Analyzes MIDI files to extract melodic motifs, rhythmic patterns, and phrase structures for lyric writing. This skill should be used when the user wants to write lyrics that match the phrasing of an existing MIDI file, or when analyzing a song's melodic structure to understand its "lyrical shape." Triggers on requests like "analyze this MIDI for lyrics", "what's the phrasing in this song", or "help me write lyrics to match this melody."
---

# MIDI Lyric Analyzer

## Overview

This skill extracts musical motifs from MIDI files and translates them into actionable constraints for lyric writing. The goal is not to write lyrics FOR the music, but to understand the music's phrase lengths, repetition patterns, and rhythmic feel so lyrics can be crafted to match naturally.

## When to Use

- Analyzing a MIDI file before writing lyrics to it
- Understanding the "lyrical shape" of an existing melody
- Determining syllable counts and stress patterns from melodic phrases
- Identifying which phrases are designed for repetition (hooks/mantras)

## Workflow

### Step 1: Run Analysis Scripts

Execute these scripts from the `midi-analyzer` sibling skill (located at `../midi-analyzer/`):

```bash
# Core analyses for lyrical phrasing
python ../midi-analyzer/scripts/midi/analyze_midi_melody.py <file.mid>
python ../midi-analyzer/scripts/midi/analyze_midi_rhythm.py <file.mid>
python ../midi-analyzer/scripts/midi/analyze_midi_structure.py <file.mid>
```

### Step 2: Interpret Motifs for Phrasing

From the melody analysis, identify the **top 5 most frequent motifs** and analyze each:

| Motif Property | Lyrical Implication |
|----------------|---------------------|
| **Note count** | Suggests syllable count per phrase |
| **Occurrence count** | High (10+) = designed for repetition/mantra |
| **Contour** (rising/falling/arch) | Suggests emotional direction |
| **Note values** | Short = punchy syllables; Long = sustained vowels |

**Contour Analysis:**
- Examine the note sequence (e.g., B-A-B-G)
- Rising = building energy, questioning
- Falling = resolution, finality, gravity
- Arch (up then down) = complete thought, statement
- Repeated notes = emphasis, insistence

### Step 3: Interpret Rhythm for Syllable Stress

From the rhythm analysis:

| Dominant Duration | Lyrical Feel |
|-------------------|--------------|
| Sixteenths dominant | Rapid-fire, staccato phrasing ("Hark how the bells") |
| Eighths dominant | Moderate flow, conversational |
| Quarters dominant | Deliberate, weighted words |
| Mixed with syncopation | Off-beat emphasis, jazz/hip-hop phrasing |

**Syncopation Score Interpretation:**
- 0.0-0.3: Straight, on-beat phrasing
- 0.3-0.6: Moderate swing, some off-beat emphasis
- 0.6-1.0: Heavy syncopation, emphasize unexpected syllables

### Step 4: Generate Lyrical Blueprint

Synthesize findings into an actionable blueprint:

```markdown
## Lyrical Blueprint: [Song Name]

### Core Phrase Structure
- Primary motif: [X] notes = [X] syllables per phrase
- Repetition frequency: [High/Medium/Low] - [implication]
- Contour: [Rising/Falling/Arch] - [emotional suggestion]

### Rhythmic Constraints
- Tempo: [X] BPM ([feel description])
- Dominant note value: [type] = [phrasing style]
- Syncopation: [level] - [stress pattern guidance]

### Section Mapping
- Measures 1-X: [section type] - [phrase suggestions]
- Measures X-Y: [section type] - [phrase suggestions]

### Repetition Design
[If motif appears 10+ times, note that lyrics should be:]
- Memorable on first hearing
- Not fatiguing on repetition
- Consider single-word or short phrase hooks

### Sample Phrase Shapes
Based on the top motifs, lyrics should fit patterns like:
- [X]-[X]-[X]-[X] (4 syllables, stress pattern)
- [X]-[X]-[X] (3 syllables, stress pattern)
```

## Example Interpretation

**Input:** Carol of the Bells MIDI analysis showing:
- Motif B-A-B-G appearing 20 times (4 notes)
- Sixteenth notes dominant (452 of them)
- 78 BPM, G minor
- Syncopation score: 0.63

**Blueprint Output:**
- **Primary phrase:** 4 syllables, falling contour (resolves down to tonic)
- **Feel:** Rapid, bell-like repetition - lyrics should be crisp consonants
- **Repetition:** Very high - this is a mantra phrase, must not tire
- **Stress:** Moderate syncopation - some off-beat emphasis acceptable
- **Suggested shapes:** "HARK how the BELLS" / "SWEET sil-ver BELLS" (4 syllables, stress on 1 and 4)

## Integration with Songwriting

After generating a Lyrical Blueprint, use it as a constraint document when:
- Writing original lyrics to existing melodies
- Adapting/translating lyrics to match musical phrasing
- Creating parody or contrafactum (new words to existing tune)
- Analyzing why certain lyrics "fit" a melody well
