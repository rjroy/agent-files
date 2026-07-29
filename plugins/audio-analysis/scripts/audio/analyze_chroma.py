#!/usr/bin/env python3
"""
Chromagram Analysis Script

Extracts pitch class distribution (chromagram) over time from audio files using librosa.

Usage:
    python analyze_chroma.py <file_path>

Output:
    JSON to stdout with time_points, pitch_classes, and chroma_matrix
    Errors to stderr with non-zero exit code

Requirements:
    - Audio file (WAV, MP3, FLAC, OGG, M4A)
    - Files >10 minutes are truncated with warning
    - Output limited to 200 time points; longer files are downsampled uniformly
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
MAX_TIME_POINTS = 200  # REQ-NF-12: limit to 200 time points
SAMPLE_RATE = 22050  # librosa default
ANALYSIS_TYPE = "chroma"
PITCH_CLASSES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


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


def downsample_chroma(chroma, target_points: int = MAX_TIME_POINTS):
    """
    Uniformly downsample chroma matrix to target number of time points.

    Args:
        chroma: Chroma matrix (12 x N)
        target_points: Target number of time points

    Returns:
        Downsampled chroma matrix (12 x target_points)
    """
    num_frames = chroma.shape[1]

    if num_frames <= target_points:
        return chroma

    # Calculate indices to sample uniformly
    # Use linspace to get evenly spaced indices
    indices = np.linspace(0, num_frames - 1, target_points, dtype=int)

    # Select frames at those indices
    return chroma[:, indices]


def analyze_chroma(y, sr):
    """
    Extract chromagram (pitch class distribution over time).

    Args:
        y: Audio samples
        sr: Sample rate

    Returns:
        Dictionary with time_points, pitch_classes, chroma_matrix

    Raises:
        AnalysisError: If analysis fails
    """
    try:
        # Extract chromagram using Constant-Q transform
        # This is more accurate for pitch than standard FFT-based chroma
        chroma_cqt = librosa.feature.chroma_cqt(y=y, sr=sr)

        # chroma_cqt shape: (12, num_frames)
        # 12 rows = pitch classes (C, C#, D, ..., B)
        # num_frames = time points

        # Downsample if needed (REQ-NF-12)
        num_frames = chroma_cqt.shape[1]
        if num_frames > MAX_TIME_POINTS:
            chroma_cqt = downsample_chroma(chroma_cqt, MAX_TIME_POINTS)

        # Get time points for each frame
        # After potential downsampling, recalculate frame times
        num_frames_final = chroma_cqt.shape[1]
        hop_length = 512  # librosa default

        # Generate time points for the frames we have
        if num_frames > MAX_TIME_POINTS:
            # If we downsampled, create evenly spaced time points
            duration = librosa.get_duration(y=y, sr=sr)
            time_points = np.linspace(0, duration, num_frames_final)
        else:
            # If no downsampling, use librosa's frame timing
            time_points = librosa.frames_to_time(
                np.arange(num_frames_final),
                sr=sr,
                hop_length=hop_length
            )

        # Format output data
        # Round values to 3 decimal places
        data = {
            "time_points": [round(t, 3) for t in time_points.tolist()],
            "pitch_classes": PITCH_CLASSES,
            "chroma_matrix": [[round(val, 3) for val in row] for row in chroma_cqt.tolist()]
        }

        return data

    except Exception as e:
        raise AnalysisError(
            ANALYSIS_FAILED,
            f"Chromagram analysis failed: {str(e)}",
            str(e)
        )


def main():
    """Main entry point for chromagram analysis script."""
    parser = argparse.ArgumentParser(
        description="Extract chromagram (pitch class distribution) from audio files"
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

        # Analyze chroma
        data = analyze_chroma(y, sr)

        # Build warnings list
        warnings = []
        if truncated:
            warnings.append(
                f"Audio file truncated to {MAX_DURATION_SECONDS // 60} minutes for analysis"
            )

        # Check if we downsampled
        if len(data["time_points"]) == MAX_TIME_POINTS:
            warnings.append(
                f"Chromagram downsampled to {MAX_TIME_POINTS} time points for output size"
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
