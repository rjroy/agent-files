#!/usr/bin/env python3
"""
Audio Comparison Script

Compares two audio files for similarity across multiple dimensions:
- Tempo (BPM)
- Key and mode
- Chroma (pitch class distribution)

Usage:
    python compare_audio.py <file_path_1> <file_path_2>

Output:
    JSON to stdout with similarity scores (0-1) for each dimension
    Errors to stderr with non-zero exit code

Requirements:
    - Two audio files (WAV, MP3, FLAC, OGG, M4A)
    - Files >10 minutes are truncated with warning
"""

import sys
import argparse
from pathlib import Path

# Add parent directory to path for shared imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import librosa
    import numpy as np
except ImportError as e:
    print(f"Error: Missing required library: {e}", file=sys.stderr)
    print("Install with: pip install librosa", file=sys.stderr)
    sys.exit(1)

from shared import (
    validate_audio_file,
    output_success,
    output_error,
    AnalysisError,
    CORRUPT_FILE,
    ANALYSIS_FAILED
)


# Constants
MAX_DURATION_SECONDS = 10 * 60  # 10 minutes
SAMPLE_RATE = 22050  # librosa default
ANALYSIS_TYPE = "compare"

# Key profiles for Krumhansl-Schmuckler algorithm
MAJOR_PROFILE = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
MINOR_PROFILE = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
PITCH_CLASSES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

# Similarity weights (must sum to 1.0)
TEMPO_WEIGHT = 0.3
KEY_WEIGHT = 0.3
CHROMA_WEIGHT = 0.4


def load_audio(file_path: Path, max_duration: int = MAX_DURATION_SECONDS):
    """
    Load audio file with optional duration truncation.

    Args:
        file_path: Path to audio file
        max_duration: Maximum duration in seconds

    Returns:
        Tuple of (audio_samples, sample_rate, duration_seconds, truncated)

    Raises:
        AnalysisError: If file cannot be loaded
    """
    try:
        # Load audio with librosa
        y, sr = librosa.load(
            str(file_path),
            sr=SAMPLE_RATE,
            duration=max_duration,
            mono=True
        )

        # Calculate actual duration
        duration_seconds = librosa.get_duration(y=y, sr=sr)

        # Check if file was truncated
        truncated = abs(duration_seconds - max_duration) < 1.0

        return y, sr, duration_seconds, truncated

    except Exception as e:
        raise AnalysisError(
            CORRUPT_FILE,
            f"Failed to load audio file: {str(e)}",
            str(e)
        )


def extract_tempo(y, sr):
    """
    Extract tempo (BPM) from audio.

    Args:
        y: Audio samples
        sr: Sample rate

    Returns:
        Tempo in BPM as float
    """
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    tempo, _ = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
    # librosa 0.10+ returns a one-element ndarray for the estimated tempo.
    return float(np.asarray(tempo).reshape(-1)[0])


def compute_chromagram(y, sr):
    """
    Compute averaged chromagram (pitch class distribution).

    Args:
        y: Audio samples
        sr: Sample rate

    Returns:
        12-element numpy array of pitch class weights
    """
    chroma_cqt = librosa.feature.chroma_cqt(y=y, sr=sr)
    # Average across time to get overall distribution
    pitch_distribution = np.mean(chroma_cqt, axis=1)
    # Normalize
    if np.sum(pitch_distribution) > 0:
        pitch_distribution /= np.sum(pitch_distribution)
    return pitch_distribution


def correlate_with_profile(pitch_distribution, key_profile):
    """
    Compute Pearson correlation between pitch distribution and key profile.

    Args:
        pitch_distribution: 12-element array of pitch class weights
        key_profile: 12-element array of key profile weights

    Returns:
        Correlation coefficient (0-1 range)
    """
    # Normalize key profile
    profile_normalized = (key_profile - np.mean(key_profile)) / np.std(key_profile)

    # Normalize pitch distribution
    dist_normalized = (pitch_distribution - np.mean(pitch_distribution)) / np.std(pitch_distribution)

    # Compute Pearson correlation
    correlation = np.corrcoef(dist_normalized, profile_normalized)[0, 1]

    # Ensure correlation is in valid range
    correlation = max(0.0, min(1.0, correlation))

    return correlation


def detect_key(y, sr):
    """
    Detect musical key using Krumhansl-Schmuckler algorithm.

    Args:
        y: Audio samples
        sr: Sample rate

    Returns:
        Tuple of (key_name, mode) e.g., ('C', 'major')
    """
    pitch_distribution = compute_chromagram(y, sr)

    # Test all 24 keys
    best_correlation = -1
    best_key = None
    best_mode = None

    # Test all major keys
    for i in range(12):
        rotated_profile = np.roll(MAJOR_PROFILE, i)
        correlation = correlate_with_profile(pitch_distribution, rotated_profile)
        if correlation > best_correlation:
            best_correlation = correlation
            best_key = PITCH_CLASSES[i]
            best_mode = 'major'

    # Test all minor keys
    for i in range(12):
        rotated_profile = np.roll(MINOR_PROFILE, i)
        correlation = correlate_with_profile(pitch_distribution, rotated_profile)
        if correlation > best_correlation:
            best_correlation = correlation
            best_key = PITCH_CLASSES[i]
            best_mode = 'minor'

    return best_key, best_mode


def compute_tempo_similarity(tempo1, tempo2):
    """
    Compute tempo similarity (0-1).

    Uses normalized absolute difference.

    Args:
        tempo1: First tempo in BPM
        tempo2: Second tempo in BPM

    Returns:
        Similarity score 0-1 (1 = identical, 0 = very different)
    """
    if max(tempo1, tempo2) == 0:
        return 1.0

    # Compute normalized difference
    # similarity = 1 - (absolute_difference / max_tempo)
    # This gives 1.0 for identical tempos, decreasing to 0 for very different ones
    diff = abs(tempo1 - tempo2)
    max_tempo = max(tempo1, tempo2)
    similarity = 1.0 - (diff / max_tempo)

    # Clamp to [0, 1]
    return max(0.0, min(1.0, similarity))


def compute_key_similarity(key1, mode1, key2, mode2):
    """
    Compute key similarity (0-1).

    Scoring:
    - Same key and mode: 1.0
    - Relative keys (e.g., C major / A minor): 0.5
    - Same tonic, different mode: 0.3
    - Different keys: 0.0

    Args:
        key1: First key name
        mode1: First mode ('major' or 'minor')
        key2: Second key name
        mode2: Second mode ('major' or 'minor')

    Returns:
        Similarity score 0-1
    """
    # Same key and mode
    if key1 == key2 and mode1 == mode2:
        return 1.0

    # Same tonic, different mode
    if key1 == key2:
        return 0.3

    # Check for relative keys
    # Relative keys: major key and its relative minor (3 semitones down)
    # e.g., C major <-> A minor, G major <-> E minor
    key1_idx = PITCH_CLASSES.index(key1)
    key2_idx = PITCH_CLASSES.index(key2)

    if mode1 == 'major' and mode2 == 'minor':
        # key2 should be 3 semitones below key1
        relative_minor_idx = (key1_idx - 3) % 12
        if key2_idx == relative_minor_idx:
            return 0.5

    if mode1 == 'minor' and mode2 == 'major':
        # key2 should be 3 semitones above key1
        relative_major_idx = (key1_idx + 3) % 12
        if key2_idx == relative_major_idx:
            return 0.5

    # Different, unrelated keys
    return 0.0


def compute_chroma_similarity(chroma1, chroma2):
    """
    Compute chroma similarity using cosine similarity (0-1).

    Args:
        chroma1: First chromagram (12-element array)
        chroma2: Second chromagram (12-element array)

    Returns:
        Cosine similarity 0-1 (1 = identical distribution)
    """
    # Compute cosine similarity
    dot_product = np.dot(chroma1, chroma2)
    norm1 = np.linalg.norm(chroma1)
    norm2 = np.linalg.norm(chroma2)

    if norm1 == 0 or norm2 == 0:
        return 0.0

    similarity = dot_product / (norm1 * norm2)

    # Clamp to [0, 1]
    return max(0.0, min(1.0, similarity))


def compare_audio_files(file1: Path, file2: Path):
    """
    Compare two audio files across multiple dimensions.

    Args:
        file1: Path to first audio file
        file2: Path to second audio file

    Returns:
        Dictionary with similarity scores and metadata

    Raises:
        AnalysisError: If analysis fails
    """
    try:
        # Load both files
        y1, sr1, duration1, truncated1 = load_audio(file1)
        y2, sr2, duration2, truncated2 = load_audio(file2)

        # Extract features from file 1
        tempo1 = extract_tempo(y1, sr1)
        key1, mode1 = detect_key(y1, sr1)
        chroma1 = compute_chromagram(y1, sr1)

        # Extract features from file 2
        tempo2 = extract_tempo(y2, sr2)
        key2, mode2 = detect_key(y2, sr2)
        chroma2 = compute_chromagram(y2, sr2)

        # Compute similarity scores
        tempo_similarity = compute_tempo_similarity(tempo1, tempo2)
        key_similarity = compute_key_similarity(key1, mode1, key2, mode2)
        chroma_similarity = compute_chroma_similarity(chroma1, chroma2)

        # Compute overall similarity (weighted average)
        overall_similarity = (
            TEMPO_WEIGHT * tempo_similarity +
            KEY_WEIGHT * key_similarity +
            CHROMA_WEIGHT * chroma_similarity
        )

        # Format output data
        data = {
            "file1": {
                "tempo_bpm": round(tempo1, 2),
                "key": key1,
                "mode": mode1,
                "duration_seconds": round(duration1, 2),
                "truncated": truncated1
            },
            "file2": {
                "tempo_bpm": round(tempo2, 2),
                "key": key2,
                "mode": mode2,
                "duration_seconds": round(duration2, 2),
                "truncated": truncated2
            },
            "tempo_similarity": round(float(tempo_similarity), 3),
            "key_similarity": round(float(key_similarity), 3),
            "chroma_similarity": round(float(chroma_similarity), 3),
            "overall_similarity": round(float(overall_similarity), 3)
        }

        # Collect warnings
        warnings = []
        if truncated1:
            warnings.append(
                f"File 1 truncated to {MAX_DURATION_SECONDS // 60} minutes for analysis"
            )
        if truncated2:
            warnings.append(
                f"File 2 truncated to {MAX_DURATION_SECONDS // 60} minutes for analysis"
            )

        return data, warnings

    except Exception as e:
        raise AnalysisError(
            ANALYSIS_FAILED,
            f"Audio comparison failed: {str(e)}",
            str(e)
        )


def main():
    """Main entry point for audio comparison script."""
    parser = argparse.ArgumentParser(
        description="Compare two audio files for similarity"
    )
    parser.add_argument(
        "file_path_1",
        help="Path to first audio file (WAV, MP3, FLAC, OGG, M4A)"
    )
    parser.add_argument(
        "file_path_2",
        help="Path to second audio file (WAV, MP3, FLAC, OGG, M4A)"
    )

    args = parser.parse_args()

    try:
        # Validate both audio files
        file1, file_size1, ext1 = validate_audio_file(args.file_path_1)
        file2, file_size2, ext2 = validate_audio_file(args.file_path_2)

        # Compare files
        data, warnings = compare_audio_files(file1, file2)

        # Output success
        # Use file1 as the primary file path for output
        output_success(
            file_path=str(file1),
            analysis_type=ANALYSIS_TYPE,
            data=data,
            duration_seconds=data["file1"]["duration_seconds"],
            truncated=data["file1"]["truncated"] or data["file2"]["truncated"],
            warnings=warnings
        )

        sys.exit(0)

    except AnalysisError as e:
        # Handle known analysis errors
        output_error(
            file_path=f"{args.file_path_1}, {args.file_path_2}",
            analysis_type=ANALYSIS_TYPE,
            error_code=e.code,
            error_message=e.message,
            error_details=e.details
        )
        sys.exit(1)

    except Exception as e:
        # Handle unexpected errors
        output_error(
            file_path=f"{args.file_path_1}, {args.file_path_2}",
            analysis_type=ANALYSIS_TYPE,
            error_code=ANALYSIS_FAILED,
            error_message=f"Unexpected error: {str(e)}",
            error_details=str(e)
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
