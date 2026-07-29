#!/usr/bin/env python3
"""
Key Detection Script

Estimates musical key and mode (major/minor) using Krumhansl-Schmuckler algorithm.

Usage:
    python analyze_key.py <file_path>

Output:
    JSON to stdout with key, mode, confidence, and optional alternative
    Errors to stderr with non-zero exit code

Requirements:
    - Audio file (WAV, MP3, FLAC, OGG, M4A)
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
ANALYSIS_TYPE = "key"

# Krumhansl-Schmuckler key profiles
# Major profile: weights for each pitch class (C, C#, D, D#, E, F, F#, G, G#, A, A#, B)
MAJOR_PROFILE = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])

# Minor profile: weights for each pitch class
MINOR_PROFILE = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])

# Pitch class names
PITCH_CLASSES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

# Confidence threshold for providing alternative
LOW_CONFIDENCE_THRESHOLD = 0.5


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
        # duration parameter truncates to specified seconds
        y, sr = librosa.load(
            str(file_path),
            sr=SAMPLE_RATE,
            duration=max_duration,
            mono=True
        )

        # Calculate actual duration
        duration_seconds = librosa.get_duration(y=y, sr=sr)

        # Check if file was truncated
        # We can't know the original duration without loading the whole file,
        # so we check if loaded duration is close to max_duration
        truncated = abs(duration_seconds - max_duration) < 1.0

        return y, sr, duration_seconds, truncated

    except Exception as e:
        raise AnalysisError(
            CORRUPT_FILE,
            f"Failed to load audio file: {str(e)}",
            str(e)
        )


def compute_chromagram(y, sr):
    """
    Compute chromagram using constant-Q transform.

    Args:
        y: Audio samples
        sr: Sample rate

    Returns:
        Averaged pitch class distribution (12-element array)

    Raises:
        AnalysisError: If chromagram computation fails
    """
    try:
        # Compute constant-Q chromagram (REQ-F-2)
        # CQT provides better frequency resolution for musical pitch
        chroma_cqt = librosa.feature.chroma_cqt(y=y, sr=sr)

        # Average across time to get overall pitch class distribution
        # Shape: (12, time_frames) -> (12,)
        pitch_class_distribution = np.mean(chroma_cqt, axis=1)

        # Normalize to sum to 1 (makes it a proper distribution)
        if np.sum(pitch_class_distribution) > 0:
            pitch_class_distribution /= np.sum(pitch_class_distribution)

        return pitch_class_distribution

    except Exception as e:
        raise AnalysisError(
            ANALYSIS_FAILED,
            f"Chromagram computation failed: {str(e)}",
            str(e)
        )


def correlate_with_profile(pitch_distribution, key_profile):
    """
    Compute Pearson correlation between pitch distribution and key profile.

    Args:
        pitch_distribution: 12-element array of pitch class weights
        key_profile: 12-element array of key profile weights

    Returns:
        Correlation coefficient (0-1 range, higher is better match)
    """
    # Normalize key profile
    profile_normalized = (key_profile - np.mean(key_profile)) / np.std(key_profile)

    # Normalize pitch distribution
    dist_normalized = (pitch_distribution - np.mean(pitch_distribution)) / np.std(pitch_distribution)

    # Compute Pearson correlation
    correlation = np.corrcoef(dist_normalized, profile_normalized)[0, 1]

    # Ensure correlation is in valid range (handle edge cases)
    correlation = max(0.0, min(1.0, correlation))

    return correlation


def analyze_key(y, sr):
    """
    Analyze musical key using Krumhansl-Schmuckler algorithm.

    Args:
        y: Audio samples
        sr: Sample rate

    Returns:
        Dictionary with key, mode, confidence, and optional alternative

    Raises:
        AnalysisError: If analysis fails
    """
    try:
        # Compute pitch class distribution
        pitch_distribution = compute_chromagram(y, sr)

        # Test all 24 keys (12 major + 12 minor)
        candidates = []

        # Test all major keys
        for i in range(12):
            # Rotate profile to match key (0=C, 1=C#, etc.)
            rotated_profile = np.roll(MAJOR_PROFILE, i)
            correlation = correlate_with_profile(pitch_distribution, rotated_profile)

            candidates.append({
                'key': PITCH_CLASSES[i],
                'mode': 'major',
                'confidence': correlation
            })

        # Test all minor keys
        for i in range(12):
            # Rotate profile to match key
            rotated_profile = np.roll(MINOR_PROFILE, i)
            correlation = correlate_with_profile(pitch_distribution, rotated_profile)

            candidates.append({
                'key': PITCH_CLASSES[i],
                'mode': 'minor',
                'confidence': correlation
            })

        # Sort by confidence (highest first)
        candidates.sort(key=lambda x: x['confidence'], reverse=True)

        # Get top candidate
        primary = candidates[0]
        secondary = candidates[1]

        # Build result
        data = {
            'key': primary['key'],
            'mode': primary['mode'],
            'confidence': round(primary['confidence'], 2),
            'alternative': None
        }

        # Add alternative if confidence is low (REQ-F-23)
        if primary['confidence'] < LOW_CONFIDENCE_THRESHOLD:
            data['alternative'] = {
                'key': secondary['key'],
                'mode': secondary['mode'],
                'confidence': round(secondary['confidence'], 2)
            }

        return data

    except Exception as e:
        raise AnalysisError(
            ANALYSIS_FAILED,
            f"Key analysis failed: {str(e)}",
            str(e)
        )


def main():
    """Main entry point for key analysis script."""
    parser = argparse.ArgumentParser(
        description="Estimate musical key and mode from audio files"
    )
    parser.add_argument(
        "file_path",
        help="Path to audio file (WAV, MP3, FLAC, OGG, M4A)"
    )

    args = parser.parse_args()

    try:
        # Validate audio file
        file_path, file_size, extension = validate_audio_file(args.file_path)

        # Load audio with truncation
        y, sr, duration_seconds, truncated = load_audio(file_path, MAX_DURATION_SECONDS)

        # Analyze key
        data = analyze_key(y, sr)

        # Build warnings list
        warnings = []
        if truncated:
            warnings.append(
                f"Audio file truncated to {MAX_DURATION_SECONDS // 60} minutes for analysis"
            )

        # Output success
        output_success(
            file_path=str(file_path),
            analysis_type=ANALYSIS_TYPE,
            data=data,
            duration_seconds=round(duration_seconds, 2),
            truncated=truncated,
            warnings=warnings
        )

        sys.exit(0)

    except AnalysisError as e:
        # Handle known analysis errors
        output_error(
            file_path=args.file_path,
            analysis_type=ANALYSIS_TYPE,
            error_code=e.code,
            error_message=e.message,
            error_details=e.details
        )
        sys.exit(1)

    except Exception as e:
        # Handle unexpected errors
        output_error(
            file_path=args.file_path,
            analysis_type=ANALYSIS_TYPE,
            error_code=ANALYSIS_FAILED,
            error_message=f"Unexpected error: {str(e)}",
            error_details=str(e)
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
