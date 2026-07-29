---
name: audio-analyzer
description: Use this skill when the user asks about analyzing audio files for musical characteristics like tempo, key, beats, structure, or when comparing two audio files. Triggers on questions about BPM detection, key/mode detection, beat tracking, song structure analysis, chromagram analysis, spectrogram generation, harmonic-percussive separation, or audio file similarity.
---

# Audio Analyzer

## Overview

This skill provides capabilities for extracting musical information from audio files (WAV, MP3, FLAC, OGG, M4A). Each analysis script outputs structured JSON to stdout and can be invoked via the Bash tool.

## Decision Guidance

**Map user requests to scripts:**

| User Question | Script to Use |
|--------------|---------------|
| "What's the tempo/BPM?" | `analyze_tempo.py` |
| "What key is this in?" | `analyze_key.py` |
| "Where are the beats?" | `analyze_beats.py` |
| "What's the song structure?" | `analyze_structure.py` |
| "Show me the pitch distribution" | `analyze_chroma.py` |
| "Generate a spectrogram" | `generate_spectrogram.py` |
| "Is this more harmonic or percussive?" | `analyze_hpss.py` |
| "How similar are these two songs?" | `compare_audio.py` |

## Quick Reference

All scripts are located in `audio-analysis-plugin/scripts/audio/` and follow this pattern:

```bash
python scripts/audio/<script_name>.py <file_path> [options]
```

### 1. Tempo Analysis (`analyze_tempo.py`)

Extracts BPM and beat positions using librosa's beat tracker.

```bash
python scripts/audio/analyze_tempo.py /path/to/audio.wav
```

**Output Fields:**
- `tempo_bpm`: Detected tempo in beats per minute
- `confidence`: Detection confidence (0-1)
- `beat_frames`: Array of frame indices where beats occur
- `beat_times`: Array of beat timestamps in seconds

### 2. Key Detection (`analyze_key.py`)

Identifies musical key and mode using Krumhansl-Schmuckler algorithm.

```bash
python scripts/audio/analyze_key.py /path/to/audio.mp3
```

**Output Fields:**
- `key`: Detected key (C, C#, D, etc.)
- `mode`: major or minor
- `confidence`: Detection confidence (0-1)
- `alternative`: Secondary key/mode when confidence < 0.5

### 3. Beat Detection (`analyze_beats.py`)

Returns precise beat timestamp array for rhythm analysis.

```bash
python scripts/audio/analyze_beats.py /path/to/audio.flac
```

**Output Fields:**
- `beat_times`: Array of beat timestamps in seconds
- `beat_count`: Total number of detected beats
- `mean_beat_interval`: Average time between beats
- `tempo_estimate`: Estimated tempo from beat intervals

### 4. Structure Analysis (`analyze_structure.py`)

Identifies song sections (intro, verse, chorus, etc.) using feature similarity.

```bash
python scripts/audio/analyze_structure.py /path/to/audio.ogg
```

**Output Fields:**
- `sections`: Array of section objects with:
  - `label`: Section identifier (A, B, C, etc.)
  - `start_time`: Section start in seconds
  - `end_time`: Section end in seconds
- `num_sections`: Total sections detected

### 5. Chromagram Analysis (`analyze_chroma.py`)

Extracts pitch class distribution over time (limited to 200 time points).

```bash
python scripts/audio/analyze_chroma.py /path/to/audio.m4a
```

**Output Fields:**
- `time_points`: Array of timestamps for each frame
- `pitch_classes`: ["C", "C#", "D", ..., "B"]
- `chroma_matrix`: 12 x N matrix of pitch class energy values

### 6. Spectrogram Generation (`generate_spectrogram.py`)

Creates mel spectrogram visualization as PNG image.

```bash
python scripts/audio/generate_spectrogram.py /path/to/audio.wav --output /path/to/output.png
```

**Options:**
- `--output`: Output PNG path (defaults to temp directory)

**Output Fields:**
- `output_path`: Path to generated PNG file
- `n_mels`: Number of mel frequency bins
- `fmax`: Maximum frequency in Hz

### 7. HPSS Analysis (`analyze_hpss.py`)

Separates harmonic and percussive components, reports energy ratios.

```bash
python scripts/audio/analyze_hpss.py /path/to/audio.wav
```

**Output Fields:**
- `harmonic_ratio`: Proportion of harmonic energy (0-1)
- `percussive_ratio`: Proportion of percussive energy (0-1)
- `harmonic_rms`: RMS energy of harmonic component
- `percussive_rms`: RMS energy of percussive component

### 8. Audio Comparison (`compare_audio.py`)

Compares two audio files across tempo, key, and chroma dimensions.

```bash
python scripts/audio/compare_audio.py /path/to/audio1.wav /path/to/audio2.wav
```

**Output Fields:**
- `overall_similarity`: Weighted average similarity (0-1)
- `tempo_similarity`: How close the tempos are (0-1)
- `key_similarity`: Key/mode match score (0-1)
- `chroma_similarity`: Pitch distribution similarity (0-1)

## Common Output Envelope

All scripts return JSON with this structure:

```json
{
  "status": "success",
  "file": "/path/to/input.wav",
  "analysis_type": "tempo",
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
  "file": "/path/to/input.wav",
  "analysis_type": "tempo",
  "error": {
    "code": "CORRUPT_FILE",
    "message": "Failed to load audio file",
    "details": "..."
  }
}
```

## Constraints

- **File size limit**: 100MB maximum
- **Duration limit**: Files >10 minutes are truncated with warning
- **Supported formats**: WAV, MP3, FLAC, OGG, M4A
- **Chromagram limit**: Output limited to 200 time points

## Example Workflow

To analyze a song comprehensively:

```bash
# Get tempo and beats
python scripts/audio/analyze_tempo.py song.wav

# Detect key
python scripts/audio/analyze_key.py song.wav

# Find song structure
python scripts/audio/analyze_structure.py song.wav

# Generate visualization
python scripts/audio/generate_spectrogram.py song.wav --output song_spectrogram.png
```

For detailed script documentation, see @audio-script-guide.md
