#!/usr/bin/env python3
"""
Spectrogram Generation Script

Generates mel spectrogram visualization as PNG image from audio files using librosa.

Usage:
    python generate_spectrogram.py <file_path> [--output <path.png>]

Output:
    JSON to stdout with output_path and spectrogram metadata
    PNG file created at specified path or temp directory
    Errors to stderr with non-zero exit code

Requirements:
    - Audio file (WAV, MP3, FLAC, OGG, M4A)
    - Files >10 minutes are truncated with warning
"""

import sys
import argparse
import tempfile
from pathlib import Path

# Add parent directory to path for shared imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import librosa
    import librosa.display
    import numpy as np
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
except ImportError as e:
    print(f"Error: Missing required library: {e}", file=sys.stderr)
    print("Install with: pip install librosa matplotlib", file=sys.stderr)
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
ANALYSIS_TYPE = "spectrogram"
FIGURE_SIZE = (12, 6)  # Width x Height in inches
DPI = 100  # Resolution


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


def generate_spectrogram(y, sr, output_path: Path):
    """
    Generate mel spectrogram and save as PNG image.

    Args:
        y: Audio samples
        sr: Sample rate
        output_path: Path where PNG will be saved

    Returns:
        Dictionary with spectrogram metadata

    Raises:
        AnalysisError: If generation fails
    """
    try:
        # Generate mel spectrogram
        # Mel scale is perceptually motivated frequency scale
        mel_spec = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128)

        # Convert to decibel scale for better visualization
        mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)

        # Create figure and plot
        plt.figure(figsize=FIGURE_SIZE)

        # Display spectrogram with proper axes
        img = librosa.display.specshow(
            mel_spec_db,
            sr=sr,
            x_axis='time',
            y_axis='mel',
            cmap='viridis'
        )

        # Add axis labels
        plt.xlabel('Time (s)', fontsize=12)
        plt.ylabel('Frequency (Hz)', fontsize=12)
        plt.title('Mel Spectrogram', fontsize=14)

        # Add colorbar
        cbar = plt.colorbar(img, format='%+2.0f dB')
        cbar.set_label('Amplitude (dB)', fontsize=11)

        # Adjust layout to prevent label cutoff
        plt.tight_layout()

        # Save figure
        plt.savefig(str(output_path), dpi=DPI, bbox_inches='tight')
        plt.close()

        # Get spectrogram metadata
        duration = librosa.get_duration(y=y, sr=sr)
        n_frames = mel_spec.shape[1]
        n_mels = mel_spec.shape[0]

        metadata = {
            "output_path": str(output_path),
            "format": "png",
            "width_pixels": FIGURE_SIZE[0] * DPI,
            "height_pixels": FIGURE_SIZE[1] * DPI,
            "duration_seconds": round(duration, 2),
            "n_frames": n_frames,
            "n_mels": n_mels,
            "sample_rate": sr
        }

        return metadata

    except Exception as e:
        raise AnalysisError(
            ANALYSIS_FAILED,
            f"Spectrogram generation failed: {str(e)}",
            str(e)
        )


def main():
    """Main entry point for spectrogram generation script."""
    parser = argparse.ArgumentParser(
        description="Generate mel spectrogram PNG from audio files"
    )
    parser.add_argument(
        "file_path",
        help="Path to audio file (WAV, MP3, FLAC, OGG, M4A)"
    )
    parser.add_argument(
        "--output",
        help="Output path for PNG file (default: temp directory)",
        default=None
    )

    args = parser.parse_args()

    try:
        # Validate audio file
        file_path, file_size, extension = validate_audio_file(args.file_path)

        # Determine output path
        if args.output:
            output_path = Path(args.output).resolve()
            # Ensure parent directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
        else:
            # Create temp file with .png extension
            # Use suffix to ensure proper extension
            temp_file = tempfile.NamedTemporaryFile(
                suffix='.png',
                delete=False,
                prefix='spectrogram_'
            )
            output_path = Path(temp_file.name)
            temp_file.close()

        # Load audio with truncation
        y, sr, duration_seconds, truncated = load_audio(file_path, MAX_DURATION_SECONDS)

        # Generate spectrogram
        metadata = generate_spectrogram(y, sr, output_path)

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
            data=metadata,
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
