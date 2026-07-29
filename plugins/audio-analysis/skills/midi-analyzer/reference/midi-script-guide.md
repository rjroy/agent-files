# MIDI Analysis Script Reference Guide

This document provides comprehensive documentation for all MIDI analysis scripts in the Audio Analysis Plugin.

## Prerequisites

**Required Python packages:**
```bash
pip install music21
```

**Supported MIDI formats:** .mid, .midi (Standard MIDI File format)

---

## Script Details

### analyze_midi_key.py

**Purpose:** Detect musical key and mode, track modulations throughout the piece.

**CLI Interface:**
```bash
python analyze_midi_key.py <file_path>
```

**Arguments:**
| Argument | Required | Description |
|----------|----------|-------------|
| `file_path` | Yes | Path to MIDI file |

**Algorithm:**
- Uses music21's Krumhansl-Schmuckler key-finding algorithm
- Analyzes piece in 32-quarter-note segments (~8 bars in 4/4)
- Reports modulations when key confidence changes significantly

**Output Schema:**
```json
{
  "key": "G",
  "mode": "major",
  "confidence": 0.85,
  "modulations": [
    {
      "measure": 17,
      "new_key": "D",
      "new_mode": "major",
      "confidence": 0.78
    }
  ]
}
```

**Notes:**
- `modulations` array is empty if no key changes detected
- Minimum confidence for modulation reporting: 0.7
- Key change threshold: 0.15 confidence difference

---

### analyze_midi_chords.py

**Purpose:** Extract chord progression with Roman numeral functional analysis.

**CLI Interface:**
```bash
python analyze_midi_chords.py <file_path>
```

**Arguments:**
| Argument | Required | Description |
|----------|----------|-------------|
| `file_path` | Yes | Path to MIDI file |

**Algorithm:**
- Uses music21's `chordify()` to reduce score to chords
- Applies `romanNumeralFromChord()` for functional analysis
- Quantizes to 0.5 quarter-note grid for cleaner output

**Output Schema:**
```json
{
  "key_context": {
    "key": "C",
    "mode": "major"
  },
  "chord_progression": [
    {
      "chord_symbol": "Cmaj",
      "roman_numeral": "I",
      "root": "C",
      "quality": "major",
      "measure": 1,
      "beat": 1.0
    },
    {
      "chord_symbol": "Dm",
      "roman_numeral": "ii",
      "root": "D",
      "quality": "minor",
      "measure": 1,
      "beat": 3.0
    },
    {
      "chord_symbol": "G7",
      "roman_numeral": "V7",
      "root": "G",
      "quality": "dominant7",
      "measure": 2,
      "beat": 1.0
    }
  ]
}
```

**Quality Values:**
- `major`: Major triad
- `minor`: Minor triad
- `diminished`: Diminished triad
- `augmented`: Augmented triad
- `dominant7`: Dominant seventh chord
- `major7`: Major seventh chord
- `minor7`: Minor seventh chord

**Notes:**
- Minimum chord duration: 0.1 quarter notes
- Roman numerals follow standard notation (uppercase = major, lowercase = minor)

---

### analyze_midi_melody.py

**Purpose:** Identify recurring melodic motifs and patterns.

**CLI Interface:**
```bash
python analyze_midi_melody.py <file_path>
```

**Arguments:**
| Argument | Required | Description |
|----------|----------|-------------|
| `file_path` | Yes | Path to MIDI file |

**Algorithm:**
- Extracts melodic line (top voice or designated melody track)
- Converts to interval sequences
- Searches for repeated patterns using sliding window

**Output Schema:**
```json
{
  "motifs": [
    {
      "pattern": [2, -2, 3, -1],
      "pattern_description": "step up, step down, skip up, step down",
      "occurrences": 4,
      "first_occurrence": {
        "measure": 1,
        "beat": 1.0
      },
      "example_notes": ["C4", "D4", "C4", "E4", "D4"]
    }
  ],
  "total_motifs_found": 3
}
```

**Notes:**
- `pattern` array contains intervals in semitones (positive = up, negative = down)
- Motif length: 3-8 notes
- Minimum occurrences: 2 (patterns appearing once are not reported)
- Identifies patterns by interval sequence, not absolute pitch

---

### analyze_midi_rhythm.py

**Purpose:** Analyze rhythmic characteristics including time signature and syncopation.

**CLI Interface:**
```bash
python analyze_midi_rhythm.py <file_path>
```

**Arguments:**
| Argument | Required | Description |
|----------|----------|-------------|
| `file_path` | Yes | Path to MIDI file |

**Algorithm:**
- Extracts time signature from MIDI metadata
- Calculates note duration distribution
- Computes syncopation score based on off-beat note placement

**Output Schema:**
```json
{
  "time_signature": "4/4",
  "tempo_bpm": 120.0,
  "total_measures": 32,
  "note_durations": {
    "whole": 0.02,
    "half": 0.15,
    "quarter": 0.45,
    "eighth": 0.30,
    "sixteenth": 0.08
  },
  "syncopation_score": 0.35,
  "average_note_duration_quarters": 0.75
}
```

**Notes:**
- `note_durations` values are proportions (sum to ~1.0)
- `syncopation_score` ranges 0-1 (0 = on-beat, 1 = highly syncopated)
- Handles complex meters (6/8, 3/4, 5/4, etc.)
- Tempo defaults to 120 BPM if not specified in MIDI

---

### analyze_midi_structure.py

**Purpose:** Detect formal structure and section boundaries (A-B-A form, etc.).

**CLI Interface:**
```bash
python analyze_midi_structure.py <file_path>
```

**Arguments:**
| Argument | Required | Description |
|----------|----------|-------------|
| `file_path` | Yes | Path to MIDI file |

**Algorithm:**
- Segments piece into 4-measure chunks
- Extracts pitch class distribution for each segment
- Calculates pairwise similarity using cosine similarity
- Groups similar segments and assigns labels

**Output Schema:**
```json
{
  "sections": [
    {
      "label": "A",
      "start_measure": 1,
      "end_measure": 8,
      "start_time_seconds": 0.0,
      "end_time_seconds": 16.0
    },
    {
      "label": "B",
      "start_measure": 9,
      "end_measure": 16,
      "start_time_seconds": 16.0,
      "end_time_seconds": 32.0
    },
    {
      "label": "A",
      "start_measure": 17,
      "end_measure": 24,
      "start_time_seconds": 32.0,
      "end_time_seconds": 48.0
    }
  ],
  "num_sections": 3,
  "detected_form": "A-B-A (Ternary Form)",
  "section_sequence": ["A", "B", "A"]
}
```

**Detected Form Descriptions:**
- `A-B-A (Ternary Form)`: Standard ternary form
- `A-B-A variant (Rounded Binary)`: Extended ternary
- `Verse-Chorus form (A-B alternating)`: Pop/rock structure
- `Single section (Strophic or through-composed)`: No repeated sections
- `Multi-section form (A-B-C...)`: Three or more distinct sections
- `Custom form`: Pattern doesn't match standard forms

**Notes:**
- Minimum similarity threshold for same section: 0.7
- Segment length: 4 measures
- Time conversion uses tempo and time signature from MIDI

---

### analyze_midi_metrics.py

**Purpose:** Calculate composition complexity metrics.

**CLI Interface:**
```bash
python analyze_midi_metrics.py <file_path>
```

**Arguments:**
| Argument | Required | Description |
|----------|----------|-------------|
| `file_path` | Yes | Path to MIDI file |

**Algorithm:**
- Counts notes and tracks
- Calculates pitch range statistics
- Analyzes voice leading (stepwise vs. skip motion)
- Computes note density

**Output Schema:**
```json
{
  "note_count": 456,
  "track_count": 4,
  "pitch_range": {
    "lowest": "C3",
    "lowest_midi": 48,
    "highest": "C6",
    "highest_midi": 84,
    "span_semitones": 36,
    "span_octaves": 3.0
  },
  "note_density": {
    "notes_per_measure": 14.25,
    "notes_per_beat": 3.56
  },
  "voice_leading": {
    "stepwise_motion_percentage": 0.65,
    "skip_motion_percentage": 0.35,
    "average_interval_semitones": 2.8,
    "total_intervals_analyzed": 452
  }
}
```

**Notes:**
- Stepwise motion: intervals <= 2 semitones (seconds)
- Skip motion: intervals > 2 semitones (thirds and larger)
- Higher stepwise percentage indicates smoother voice leading
- Note density excludes rests

---

## Error Codes

All MIDI scripts use consistent error codes:

| Code | Description |
|------|-------------|
| `FILE_NOT_FOUND` | Input file does not exist |
| `PATH_TRAVERSAL` | Path contains traversal sequences (security) |
| `FILE_TOO_LARGE` | File exceeds 100MB limit |
| `UNSUPPORTED_FORMAT` | File extension not .mid or .midi |
| `CORRUPT_FILE` | File cannot be parsed as valid MIDI |
| `ANALYSIS_FAILED` | Analysis algorithm encountered an error |

**Error Response Format:**
```json
{
  "status": "error",
  "file": "/path/to/input.mid",
  "analysis_type": "midi_key",
  "error": {
    "code": "CORRUPT_FILE",
    "message": "Failed to load MIDI file: Invalid header",
    "details": "music21 raised MidiException: not a valid MIDI file"
  }
}
```

---

## Performance Characteristics

| Script | Typical Runtime |
|--------|-----------------|
| `analyze_midi_key.py` | ~1-3 seconds |
| `analyze_midi_chords.py` | ~2-5 seconds |
| `analyze_midi_melody.py` | ~1-3 seconds |
| `analyze_midi_rhythm.py` | ~1-2 seconds |
| `analyze_midi_structure.py` | ~2-4 seconds |
| `analyze_midi_metrics.py` | ~1-2 seconds |

Runtime depends on MIDI file complexity (number of tracks, notes, and measures).

---

## music21 Requirements

These scripts require music21 version 7.0+ for full functionality. Key features used:

- `converter.parse()`: MIDI file loading
- `analysis.discrete.KrumhanslSchmuckler`: Key detection
- `stream.chordify()`: Chord extraction
- `roman.romanNumeralFromChord()`: Functional analysis
- `note`, `chord`, `stream`: Core music21 objects

Install with:
```bash
pip install music21
```

For advanced features (MuseScore rendering), see music21 documentation for additional setup.
