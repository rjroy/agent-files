#!/usr/bin/env python3
"""
Structure Detection Script

Identifies structural sections (intro, verse, chorus, etc.) in audio files using librosa.

Usage:
    python analyze_structure.py <file_path>

Output:
    JSON to stdout with sections array containing labels and start/end times
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
    from scipy.spatial.distance import cdist
    from sklearn.cluster import AgglomerativeClustering
except ImportError as e:
    print(f"Error: Missing required library: {e}", file=sys.stderr)
    print("Install with: pip install librosa scikit-learn scipy", file=sys.stderr)
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
ANALYSIS_TYPE = "structure"

# Structure detection parameters
MIN_SECTION_LENGTH = 5.0  # Minimum section length in seconds
MAX_SECTIONS = 20  # Maximum number of sections to detect


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


def assign_section_labels(boundaries, duration_seconds):
    """
    Assign generic labels to detected sections based on position.

    Args:
        boundaries: Array of section boundary times (in seconds)
        duration_seconds: Total duration of the audio

    Returns:
        List of label strings
    """
    num_sections = len(boundaries) - 1
    labels = []

    # Simple heuristic: first section is intro, last is outro, middle sections vary
    for i in range(num_sections):
        section_start = boundaries[i]
        section_duration = boundaries[i + 1] - section_start

        if i == 0 and section_duration < 20:
            # Short first section likely intro
            labels.append("intro")
        elif i == num_sections - 1 and section_duration < 30:
            # Short last section likely outro
            labels.append("outro")
        elif section_duration < MIN_SECTION_LENGTH:
            # Very short section might be a bridge or transition
            labels.append("bridge")
        else:
            # Generic section label
            # Alternate between verse and chorus for longer sections
            if (i - 1) % 2 == 0:
                labels.append("verse")
            else:
                labels.append("chorus")

    return labels


def analyze_structure(y, sr, duration_seconds):
    """
    Analyze structural sections in audio.

    Args:
        y: Audio samples
        sr: Sample rate
        duration_seconds: Duration of audio in seconds

    Returns:
        Dictionary with sections array and num_sections

    Raises:
        AnalysisError: If analysis fails
    """
    try:
        # Compute chroma features for harmonic analysis
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)

        # Compute MFCC features for timbral analysis
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)

        # Combine features
        features = np.vstack([chroma, mfcc])

        # Compute recurrence matrix to find self-similar sections
        R = librosa.segment.recurrence_matrix(
            features,
            mode='affinity',
            metric='cosine',
            width=3
        )

        # Detect segment boundaries using spectral clustering on recurrence matrix
        # Use librosa's built-in laplacian segmentation
        # Estimate number of segments based on duration
        # ~30 seconds per section on average
        estimated_sections = max(2, min(MAX_SECTIONS, int(duration_seconds / 30)))

        # Compute segment boundaries
        boundaries_frames = librosa.segment.agglomerative(
            features,
            estimated_sections
        )

        # Convert frame boundaries to time
        boundaries_times = librosa.frames_to_time(boundaries_frames, sr=sr)

        # Ensure we have start and end
        if boundaries_times[0] != 0.0:
            boundaries_times = np.insert(boundaries_times, 0, 0.0)
        if boundaries_times[-1] != duration_seconds:
            boundaries_times = np.append(boundaries_times, duration_seconds)

        # Remove duplicate boundaries and ensure minimum section length
        filtered_boundaries = [boundaries_times[0]]
        for i in range(1, len(boundaries_times)):
            if boundaries_times[i] - filtered_boundaries[-1] >= MIN_SECTION_LENGTH:
                filtered_boundaries.append(boundaries_times[i])

        # Always include the end
        if filtered_boundaries[-1] != duration_seconds:
            filtered_boundaries.append(duration_seconds)

        boundaries_times = np.array(filtered_boundaries)

        # Assign labels to sections
        labels = assign_section_labels(boundaries_times, duration_seconds)

        # Build sections array
        sections = []
        for i in range(len(boundaries_times) - 1):
            sections.append({
                "label": labels[i],
                "start_time": round(boundaries_times[i], 1),
                "end_time": round(boundaries_times[i + 1], 1)
            })

        # Format output data
        data = {
            "sections": sections,
            "num_sections": len(sections)
        }

        return data

    except Exception as e:
        raise AnalysisError(
            ANALYSIS_FAILED,
            f"Structure analysis failed: {str(e)}",
            str(e)
        )


def main():
    """Main entry point for structure analysis script."""
    parser = argparse.ArgumentParser(
        description="Identify structural sections in audio files"
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

        # Analyze structure
        data = analyze_structure(y, sr, duration_seconds)

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
