#!/usr/bin/env python3
"""
Tempo and Beat Analysis Script

Extracts tempo (BPM), beat frames, and beat times from audio files using librosa.

Usage:
    python analyze_tempo.py <file_path>

Output:
    JSON to stdout with tempo_bpm, confidence, beat_frames, beat_times
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
SAMPLE_RATE = 22050  # librosa default, good for tempo analysis
ANALYSIS_TYPE = "tempo"


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


def analyze_tempo(y, sr):
    """
    Analyze tempo and beat positions.

    Args:
        y: Audio samples
        sr: Sample rate

    Returns:
        Dictionary with tempo_bpm, confidence, beat_frames, beat_times

    Raises:
        AnalysisError: If analysis fails
    """
    try:
        # Extract tempo and beat frames using librosa
        # onset_envelope provides the signal for beat tracking
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)

        # Get tempo and beat frames
        # tempo is returned as array, beat_frames is array of frame indices
        tempo, beat_frames = librosa.beat.beat_track(
            onset_envelope=onset_env,
            sr=sr
        )

        # Convert beat frames to time stamps
        beat_times = librosa.frames_to_time(beat_frames, sr=sr)

        # Calculate confidence from beat strength
        # Higher beat strength indicates clearer rhythm
        beat_strength = np.mean([onset_env[int(f)] if int(f) < len(onset_env) else 0
                                 for f in beat_frames])
        max_strength = np.max(onset_env) if len(onset_env) > 0 else 1.0

        # Normalize to 0-1 range
        confidence = float(beat_strength / max_strength) if max_strength > 0 else 0.0

        # Ensure confidence is in valid range
        confidence = max(0.0, min(1.0, confidence))

        # Format output data
        data = {
            "tempo_bpm": float(tempo),
            "confidence": round(confidence, 2),
            "beat_frames": beat_frames.tolist(),
            "beat_times": [round(t, 3) for t in beat_times.tolist()]
        }

        return data

    except Exception as e:
        raise AnalysisError(
            ANALYSIS_FAILED,
            f"Tempo analysis failed: {str(e)}",
            str(e)
        )


def main():
    """Main entry point for tempo analysis script."""
    parser = argparse.ArgumentParser(
        description="Extract tempo and beat information from audio files"
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

        # Analyze tempo
        data = analyze_tempo(y, sr)

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
