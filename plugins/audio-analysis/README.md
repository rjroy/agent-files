# Audio Analysis Plugin

A Claude Code plugin that provides audio and MIDI file analysis capabilities through standalone Python scripts.

## Overview

This plugin enables Claude to extract musical information from audio and MIDI files, including:

**Audio Analysis (librosa-based):**
- Tempo/BPM detection
- Key and mode identification
- Beat tracking
- Song structure analysis
- Chromagram (pitch class distribution)
- Spectrogram visualization
- Harmonic-percussive separation
- Audio similarity comparison

**MIDI Analysis (music21-based):**
- Key detection with modulation tracking
- Chord progression with Roman numeral analysis
- Melodic motif detection
- Rhythmic analysis (time signature, syncopation)
- Structural form detection (A-B-A, verse-chorus)
- Composition complexity metrics

## Installation

### 1. Install Python Dependencies

```bash
cd audio-analysis-plugin
pip install -r requirements.txt
```

Or install manually:

```bash
# Audio analysis
pip install librosa numpy scipy scikit-learn matplotlib soundfile

# MIDI analysis
pip install music21
```

### 2. Configure Claude Code

Add the plugin to your Claude Code configuration by adding the path to your settings:

```json
{
  "plugins": [
    "/path/to/wyrd-gateway/audio-analysis-plugin"
  ]
}
```

### 3. Verify Installation

```bash
# Verify plugin loads
claude --debug

# Run tests
cd audio-analysis-plugin
pytest tests/ -v
```

## Usage

### Audio Analysis

```bash
# Detect tempo
python scripts/audio/analyze_tempo.py /path/to/song.wav

# Detect key
python scripts/audio/analyze_key.py /path/to/song.mp3

# Find beats
python scripts/audio/analyze_beats.py /path/to/song.flac

# Analyze structure
python scripts/audio/analyze_structure.py /path/to/song.ogg

# Get chromagram
python scripts/audio/analyze_chroma.py /path/to/song.m4a

# Generate spectrogram
python scripts/audio/generate_spectrogram.py /path/to/song.wav --output spectrogram.png

# Harmonic-percussive separation
python scripts/audio/analyze_hpss.py /path/to/song.wav

# Compare two files
python scripts/audio/compare_audio.py song1.wav song2.wav
```

### MIDI Analysis

```bash
# Detect key
python scripts/midi/analyze_midi_key.py /path/to/file.mid

# Extract chords
python scripts/midi/analyze_midi_chords.py /path/to/file.mid

# Find melodic patterns
python scripts/midi/analyze_midi_melody.py /path/to/file.mid

# Analyze rhythm
python scripts/midi/analyze_midi_rhythm.py /path/to/file.mid

# Detect structure
python scripts/midi/analyze_midi_structure.py /path/to/file.mid

# Get complexity metrics
python scripts/midi/analyze_midi_metrics.py /path/to/file.mid
```

## Output Format

All scripts output JSON to stdout with a consistent envelope:

**Success:**
```json
{
  "status": "success",
  "file": "/path/to/input.wav",
  "analysis_type": "tempo",
  "data": {
    "tempo_bpm": 120.5,
    "confidence": 0.85,
    "beat_times": [0.5, 1.0, 1.5, ...]
  },
  "duration_seconds": 180.5,
  "truncated": false,
  "warnings": []
}
```

**Error:**
```json
{
  "status": "error",
  "file": "/path/to/input.wav",
  "analysis_type": "tempo",
  "error": {
    "code": "FILE_NOT_FOUND",
    "message": "Input file does not exist",
    "details": "..."
  }
}
```

## Supported Formats

**Audio:** WAV, MP3, FLAC, OGG, M4A
**MIDI:** .mid, .midi

## Constraints

- **File size limit:** 100MB maximum
- **Audio duration:** Files >10 minutes are truncated with warning
- **Chromagram output:** Limited to 200 time points (longer files are downsampled)

## Skills

This plugin provides two skills for Claude:

- **audio-analyzer:** Invoked when users ask about analyzing audio files
- **midi-analyzer:** Invoked when users ask about analyzing MIDI files

Each skill includes decision guidance mapping user questions to the appropriate script.

## Project Structure

```
audio-analysis-plugin/
├── .claude-plugin/
│   └── plugin.json          # Plugin manifest
├── scripts/
│   ├── shared/              # Shared utilities
│   │   ├── __init__.py
│   │   ├── validation.py    # File validation
│   │   ├── output.py        # JSON output formatting
│   │   └── errors.py        # Error codes
│   ├── audio/               # Audio analysis scripts
│   │   ├── analyze_tempo.py
│   │   ├── analyze_key.py
│   │   ├── analyze_beats.py
│   │   ├── analyze_structure.py
│   │   ├── analyze_chroma.py
│   │   ├── generate_spectrogram.py
│   │   ├── analyze_hpss.py
│   │   └── compare_audio.py
│   └── midi/                # MIDI analysis scripts
│       ├── analyze_midi_key.py
│       ├── analyze_midi_chords.py
│       ├── analyze_midi_melody.py
│       ├── analyze_midi_rhythm.py
│       ├── analyze_midi_structure.py
│       └── analyze_midi_metrics.py
├── skills/
│   ├── audio-analyzer/
│   │   ├── SKILL.md
│   │   └── reference/
│   │       └── audio-script-guide.md
│   └── midi-analyzer/
│       ├── SKILL.md
│       └── reference/
│           └── midi-script-guide.md
├── tests/
│   ├── conftest.py
│   ├── test_shared.py       # Unit tests for shared utilities
│   ├── test_audio_scripts.py # Integration tests for audio scripts
│   ├── test_midi_scripts.py  # Integration tests for MIDI scripts
│   └── test_acceptance.py    # Spec acceptance tests
├── requirements.txt
├── pyproject.toml
└── README.md
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test files
pytest tests/test_shared.py -v        # Unit tests
pytest tests/test_audio_scripts.py -v # Audio integration tests
pytest tests/test_midi_scripts.py -v  # MIDI integration tests
pytest tests/test_acceptance.py -v    # Acceptance tests

# Run with coverage
pytest tests/ --cov=scripts --cov-report=html
```

## Development

### Requirements

- Python 3.9+
- librosa >= 0.10.0
- music21 >= 9.1.0
- numpy, scipy, scikit-learn, matplotlib

### Adding New Scripts

1. Create script in `scripts/audio/` or `scripts/midi/`
2. Use shared utilities from `scripts/shared/`
3. Follow JSON output envelope format
4. Add tests in `tests/`
5. Update skill SKILL.md with decision guidance

## License

Part of the Wyrd Gateway project.
