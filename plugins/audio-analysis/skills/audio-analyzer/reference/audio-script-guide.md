# Audio Analysis Script Reference Guide

This document provides comprehensive documentation for all audio analysis scripts in the Audio Analysis Plugin.

## Prerequisites

**Required Python packages:**
```bash
pip install librosa numpy scipy scikit-learn matplotlib
```

**Supported audio formats:** WAV, MP3, FLAC, OGG, M4A

---

## Script Details

### analyze_tempo.py

**Purpose:** Extract tempo (BPM) and beat frame positions from audio files.

**CLI Interface:**
```bash
python analyze_tempo.py <file_path>
```

**Arguments:**
| Argument | Required | Description |
|----------|----------|-------------|
| `file_path` | Yes | Path to audio file |

**Algorithm:** Uses librosa's `beat.beat_track()` with onset strength envelope.

**Output Schema:**
```json
{
  "tempo_bpm": 120.5,
  "confidence": 0.85,
  "beat_frames": [22, 65, 108, ...],
  "beat_times": [0.5, 1.48, 2.45, ...]
}
```

**Notes:**
- Confidence is calculated from beat strength relative to maximum onset strength
- Beat frames are integer indices; use `beat_times` for timestamps in seconds

---

### analyze_key.py

**Purpose:** Estimate musical key and mode (major/minor) using pitch class profiles.

**CLI Interface:**
```bash
python analyze_key.py <file_path>
```

**Arguments:**
| Argument | Required | Description |
|----------|----------|-------------|
| `file_path` | Yes | Path to audio file |

**Algorithm:** Krumhansl-Schmuckler key-finding algorithm using constant-Q chromagram.

**Output Schema:**
```json
{
  "key": "G",
  "mode": "major",
  "confidence": 0.72,
  "alternative": null
}
```

When confidence < 0.5:
```json
{
  "key": "E",
  "mode": "minor",
  "confidence": 0.42,
  "alternative": {
    "key": "G",
    "mode": "major",
    "confidence": 0.38
  }
}
```

**Notes:**
- Tests all 24 keys (12 major + 12 minor)
- Provides alternative when primary confidence is below 0.5 threshold
- Uses Pearson correlation between pitch distribution and key profiles

---

### analyze_beats.py

**Purpose:** Extract precise beat timestamps as an array.

**CLI Interface:**
```bash
python analyze_beats.py <file_path>
```

**Arguments:**
| Argument | Required | Description |
|----------|----------|-------------|
| `file_path` | Yes | Path to audio file |

**Output Schema:**
```json
{
  "beat_times": [0.5, 1.02, 1.53, 2.04, ...],
  "beat_count": 245,
  "mean_beat_interval": 0.5,
  "tempo_estimate": 120.0
}
```

**Notes:**
- `tempo_estimate` is derived from mean beat interval (60 / mean_interval)
- More focused than `analyze_tempo.py` which also returns frame indices

---

### analyze_structure.py

**Purpose:** Identify structural sections (intro, verse, chorus) in songs.

**CLI Interface:**
```bash
python analyze_structure.py <file_path>
```

**Arguments:**
| Argument | Required | Description |
|----------|----------|-------------|
| `file_path` | Yes | Path to audio file |

**Algorithm:**
1. Compute chroma features and MFCCs
2. Calculate self-similarity matrix
3. Detect section boundaries using novelty function
4. Cluster similar sections using agglomerative clustering

**Output Schema:**
```json
{
  "sections": [
    {
      "label": "A",
      "start_time": 0.0,
      "end_time": 32.5
    },
    {
      "label": "B",
      "start_time": 32.5,
      "end_time": 65.0
    },
    {
      "label": "A",
      "start_time": 65.0,
      "end_time": 97.5
    }
  ],
  "num_sections": 3
}
```

**Notes:**
- Minimum section length: 5 seconds
- Maximum sections: 20
- Labels (A, B, C...) indicate similarity; repeated labels mean similar content

---

### analyze_chroma.py

**Purpose:** Extract pitch class distribution (chromagram) over time.

**CLI Interface:**
```bash
python analyze_chroma.py <file_path>
```

**Arguments:**
| Argument | Required | Description |
|----------|----------|-------------|
| `file_path` | Yes | Path to audio file |

**Output Schema:**
```json
{
  "time_points": [0.0, 0.5, 1.0, ...],
  "pitch_classes": ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"],
  "chroma_matrix": [
    [0.1, 0.2, 0.15, ...],
    [0.05, 0.08, 0.12, ...],
    ...
  ]
}
```

**Notes:**
- Output limited to 200 time points maximum (REQ-NF-12)
- Longer files are uniformly downsampled
- `chroma_matrix` is 12 rows (pitch classes) x N columns (time points)
- Values represent energy/intensity for each pitch class at each time

---

### generate_spectrogram.py

**Purpose:** Generate mel spectrogram visualization as PNG image.

**CLI Interface:**
```bash
python generate_spectrogram.py <file_path> [--output <output_path>]
```

**Arguments:**
| Argument | Required | Description |
|----------|----------|-------------|
| `file_path` | Yes | Path to audio file |
| `--output` | No | Output PNG path (defaults to temp directory) |

**Output Schema:**
```json
{
  "output_path": "/tmp/spectrogram_abc123.png",
  "n_mels": 128,
  "fmax": 8000
}
```

**Notes:**
- Figure size: 12x6 inches at 100 DPI
- Uses matplotlib with non-interactive Agg backend
- Includes labeled axes (Time, Hz) and colorbar

---

### analyze_hpss.py

**Purpose:** Separate audio into harmonic and percussive components, report energy ratios.

**CLI Interface:**
```bash
python analyze_hpss.py <file_path>
```

**Arguments:**
| Argument | Required | Description |
|----------|----------|-------------|
| `file_path` | Yes | Path to audio file |

**Algorithm:** Uses librosa's `effects.hpss()` for harmonic-percussive source separation.

**Output Schema:**
```json
{
  "harmonic_ratio": 0.65,
  "percussive_ratio": 0.35,
  "harmonic_rms": 0.0234,
  "percussive_rms": 0.0126
}
```

**Notes:**
- Ratios sum to 1.0
- Higher `harmonic_ratio` indicates more tonal/melodic content
- Higher `percussive_ratio` indicates more drums/rhythm content
- RMS values are root mean square energy (absolute, not normalized)

---

### compare_audio.py

**Purpose:** Compare two audio files for similarity across multiple dimensions.

**CLI Interface:**
```bash
python compare_audio.py <file_path_1> <file_path_2>
```

**Arguments:**
| Argument | Required | Description |
|----------|----------|-------------|
| `file_path_1` | Yes | Path to first audio file |
| `file_path_2` | Yes | Path to second audio file |

**Similarity Weights:**
- Tempo: 30%
- Key: 30%
- Chroma: 40%

**Output Schema:**
```json
{
  "overall_similarity": 0.78,
  "tempo_similarity": 0.92,
  "key_similarity": 0.75,
  "chroma_similarity": 0.72,
  "file1": {
    "tempo_bpm": 120.0,
    "key": "G",
    "mode": "major"
  },
  "file2": {
    "tempo_bpm": 118.5,
    "key": "G",
    "mode": "major"
  }
}
```

**Notes:**
- All similarity scores range from 0 (completely different) to 1 (identical)
- Tempo similarity uses exponential decay based on BPM difference
- Key similarity: 1.0 for same key/mode, 0.5 for relative major/minor, 0.0 otherwise
- Chroma similarity uses cosine similarity of averaged pitch distributions

---

## Error Codes

All scripts use consistent error codes:

| Code | Description |
|------|-------------|
| `FILE_NOT_FOUND` | Input file does not exist |
| `PATH_TRAVERSAL` | Path contains traversal sequences (security) |
| `FILE_TOO_LARGE` | File exceeds 100MB limit |
| `UNSUPPORTED_FORMAT` | File extension not in supported list |
| `CORRUPT_FILE` | File cannot be decoded as audio |
| `ANALYSIS_FAILED` | Analysis algorithm failed |

**Error Response Format:**
```json
{
  "status": "error",
  "file": "/path/to/input.wav",
  "analysis_type": "tempo",
  "error": {
    "code": "CORRUPT_FILE",
    "message": "Failed to load audio file: Invalid audio data",
    "details": "librosa.load raised AudioDecodeError"
  }
}
```

---

## Performance Characteristics

| Script | Typical Runtime (3-min file) |
|--------|------------------------------|
| `analyze_tempo.py` | ~2-3 seconds |
| `analyze_key.py` | ~2-3 seconds |
| `analyze_beats.py` | ~2-3 seconds |
| `analyze_structure.py` | ~5-8 seconds |
| `analyze_chroma.py` | ~2-3 seconds |
| `generate_spectrogram.py` | ~3-4 seconds |
| `analyze_hpss.py` | ~3-4 seconds |
| `compare_audio.py` | ~5-7 seconds |

All scripts are tested to complete within 30 seconds for 5-minute files.
