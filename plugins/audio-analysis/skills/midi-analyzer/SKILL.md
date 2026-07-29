---
name: midi-analyzer
description: Use this skill when the user asks about analyzing MIDI files for musical characteristics like key, chords, melody patterns, rhythm, structure, or composition metrics. Triggers on questions about MIDI key detection, chord progressions, Roman numeral analysis, melodic motifs, rhythmic patterns, time signatures, song form (A-B-A), or composition complexity metrics.
---

# MIDI Analyzer

## Overview

This skill provides capabilities for extracting musical information from MIDI files (.mid, .midi). Each analysis script uses music21 for parsing and outputs structured JSON to stdout via the Bash tool.

## Decision Guidance

**Map user requests to scripts:**

| User Question | Script to Use |
|--------------|---------------|
| "What key is this MIDI in?" | `analyze_midi_key.py` |
| "Show me the chord progression" | `analyze_midi_chords.py` |
| "Find melodic patterns/motifs" | `analyze_midi_melody.py` |
| "Analyze the rhythm/time signature" | `analyze_midi_rhythm.py` |
| "What's the song structure/form?" | `analyze_midi_structure.py` |
| "How complex is this piece?" | `analyze_midi_metrics.py` |

## Quick Reference

All scripts are located in `audio-analysis-plugin/scripts/midi/` and follow this pattern:

```bash
python scripts/midi/<script_name>.py <file_path>
```

### 1. Key Detection (`analyze_midi_key.py`)

Identifies key/mode using Krumhansl-Schmuckler algorithm with modulation tracking.

```bash
python scripts/midi/analyze_midi_key.py /path/to/file.mid
```

**Output Fields:**
- `key`: Primary key (C, C#, D, etc.)
- `mode`: major or minor
- `confidence`: Detection confidence (0-1)
- `modulations`: Array of key changes with measure numbers

### 2. Chord Analysis (`analyze_midi_chords.py`)

Extracts chord progression with Roman numeral notation.

```bash
python scripts/midi/analyze_midi_chords.py /path/to/file.mid
```

**Output Fields:**
- `key_context`: Key used for Roman numeral analysis
- `chord_progression`: Array of chord objects with:
  - `chord_symbol`: e.g., "Cmaj", "Dm", "G7"
  - `roman_numeral`: e.g., "I", "ii", "V7"
  - `root`: Root note name
  - `quality`: major, minor, diminished, augmented, dominant7
  - `measure`: Measure number
  - `beat`: Beat position within measure

### 3. Melody Analysis (`analyze_midi_melody.py`)

Identifies recurring melodic motifs and patterns.

```bash
python scripts/midi/analyze_midi_melody.py /path/to/file.mid
```

**Output Fields:**
- `motifs`: Array of motif objects with:
  - `pattern`: Interval sequence (e.g., [2, -2, 3])
  - `occurrences`: Number of times the pattern appears
  - `first_occurrence`: Starting measure/beat
  - `notes`: Example note names

### 4. Rhythm Analysis (`analyze_midi_rhythm.py`)

Analyzes time signature, tempo, durations, and syncopation.

```bash
python scripts/midi/analyze_midi_rhythm.py /path/to/file.mid
```

**Output Fields:**
- `time_signature`: e.g., "4/4", "3/4", "6/8"
- `tempo_bpm`: Tempo in beats per minute
- `note_durations`: Distribution of note lengths (whole, half, quarter, etc.)
- `syncopation_score`: Measure of rhythmic complexity (0-1)
- `total_measures`: Number of measures in the piece

### 5. Structure Analysis (`analyze_midi_structure.py`)

Identifies formal structure (A-B-A form, verse/chorus sections).

```bash
python scripts/midi/analyze_midi_structure.py /path/to/file.mid
```

**Output Fields:**
- `sections`: Array of section objects with:
  - `label`: Section identifier (A, B, C, etc.)
  - `start_measure`: Starting measure number
  - `end_measure`: Ending measure number
  - `start_time_seconds`: Start time in seconds
  - `end_time_seconds`: End time in seconds
- `detected_form`: Overall form description (e.g., "A-B-A (Ternary Form)")
- `section_sequence`: Array of labels in order (e.g., ["A", "B", "A"])

### 6. Complexity Metrics (`analyze_midi_metrics.py`)

Calculates composition complexity statistics.

```bash
python scripts/midi/analyze_midi_metrics.py /path/to/file.mid
```

**Output Fields:**
- `note_count`: Total notes in the piece
- `track_count`: Number of MIDI tracks
- `pitch_range`: Object with `lowest`, `highest`, `span` (in semitones)
- `note_density`: Notes per measure
- `voice_leading`: Object with:
  - `stepwise_motion_percentage`: Proportion of intervals <= 2 semitones
  - `average_interval`: Mean interval size in semitones
  - `total_intervals`: Number of melodic intervals analyzed

## Common Output Envelope

All scripts return JSON with this structure:

```json
{
  "status": "success",
  "file": "/path/to/input.mid",
  "analysis_type": "midi_key",
  "data": { ... },
  "duration_seconds": 180.5,
  "truncated": false,
  "warnings": []
}
```

**Error responses:**
```json
{
  "status": "error",
  "file": "/path/to/input.mid",
  "analysis_type": "midi_key",
  "error": {
    "code": "CORRUPT_FILE",
    "message": "Failed to load MIDI file",
    "details": "..."
  }
}
```

## Constraints

- **File size limit**: 100MB maximum
- **Supported formats**: .mid, .midi
- **Motif detection**: 3-8 notes, minimum 2 occurrences
- **Section detection**: 4-measure minimum segments

## Example Workflow

To analyze a MIDI composition comprehensively:

```bash
# Detect key (including modulations)
python scripts/midi/analyze_midi_key.py composition.mid

# Extract chord progression
python scripts/midi/analyze_midi_chords.py composition.mid

# Find recurring melodic patterns
python scripts/midi/analyze_midi_melody.py composition.mid

# Analyze formal structure
python scripts/midi/analyze_midi_structure.py composition.mid

# Get complexity metrics
python scripts/midi/analyze_midi_metrics.py composition.mid
```

For detailed script documentation, see @midi-script-guide.md
