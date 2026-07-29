#!/usr/bin/env python3
"""
Harmonic-Percussive Source Separation (HPSS) Script

Separates audio into harmonic and percussive components and analyzes their characteristics.

Usage:
    python analyze_hpss.py <file_path>

Output:
    JSON to stdout with harmonic/percussive energy ratios and statistics
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
ANALYSIS_TYPE = "hpss"


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


def compute_rms_energy(y):
    """
    Compute RMS energy of audio signal.

    Args:
        y: Audio samples

    Returns:
        RMS energy as float
    """
    return float(np.sqrt(np.mean(y**2)))


def compute_spectral_centroid(y, sr):
    """
    Compute mean spectral centroid (brightness measure).

    Args:
        y: Audio samples
        sr: Sample rate

    Returns:
        Mean spectral centroid in Hz
    """
    centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
    return float(np.mean(centroid))


def analyze_hpss(y, sr):
    """
    Perform harmonic-percussive source separation and analyze components.

    Args:
        y: Audio samples
        sr: Sample rate

    Returns:
        Dictionary with harmonic and percussive statistics

    Raises:
        AnalysisError: If analysis fails
    """
    try:
        # Perform harmonic-percussive source separation (REQ-F-7)
        # This separates the audio into two components:
        # - Harmonic: sustained tones (melody, chords)
        # - Percussive: transient sounds (drums, attacks)
        y_harmonic, y_percussive = librosa.effects.hpss(y)

        # Compute RMS energy for each component
        harmonic_energy = compute_rms_energy(y_harmonic)
        percussive_energy = compute_rms_energy(y_percussive)
        total_energy = harmonic_energy + percussive_energy

        # Compute energy ratios (avoid division by zero)
        if total_energy > 0:
            harmonic_ratio = harmonic_energy / total_energy
            percussive_ratio = percussive_energy / total_energy
        else:
            harmonic_ratio = 0.0
            percussive_ratio = 0.0

        # Compute spectral centroids (brightness measure)
        # Higher centroid = brighter sound
        harmonic_centroid = compute_spectral_centroid(y_harmonic, sr)
        percussive_centroid = compute_spectral_centroid(y_percussive, sr)

        # Compute zero crossing rates (rough measure of noisiness)
        # Higher ZCR = more noise-like, percussive
        harmonic_zcr = float(np.mean(librosa.feature.zero_crossing_rate(y_harmonic)))
        percussive_zcr = float(np.mean(librosa.feature.zero_crossing_rate(y_percussive)))

        # Format output data
        data = {
            "harmonic_energy": round(harmonic_energy, 4),
            "percussive_energy": round(percussive_energy, 4),
            "harmonic_ratio": round(harmonic_ratio, 3),
            "percussive_ratio": round(percussive_ratio, 3),
            "harmonic_spectral_centroid_hz": round(harmonic_centroid, 2),
            "percussive_spectral_centroid_hz": round(percussive_centroid, 2),
            "harmonic_zero_crossing_rate": round(harmonic_zcr, 4),
            "percussive_zero_crossing_rate": round(percussive_zcr, 4)
        }

        return data

    except Exception as e:
        raise AnalysisError(
            ANALYSIS_FAILED,
            f"HPSS analysis failed: {str(e)}",
            str(e)
        )


def main():
    """Main entry point for HPSS analysis script."""
    parser = argparse.ArgumentParser(
        description="Separate audio into harmonic and percussive components"
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

        # Analyze HPSS
        data = analyze_hpss(y, sr)

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
