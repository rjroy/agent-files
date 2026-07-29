#!/usr/bin/env python3
"""
MIDI Key Detection Script

Estimates musical key and mode using music21's Krumhansl-Schmuckler algorithm.
Detects modulations by analyzing the piece in segments.

Usage:
    python analyze_midi_key.py <file_path>

Output:
    JSON to stdout with key, mode, confidence, and modulations array
    Errors to stderr with non-zero exit code

Requirements:
    - MIDI file (.mid, .midi)
    - music21 library for MIDI analysis
"""

import sys
import argparse
from pathlib import Path

# Add parent directory to path for shared imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from music21 import converter, analysis, stream, note, chord, key
except ImportError as e:
    print(f"Error: Missing required library: {e}", file=sys.stderr)
    print("Install with: pip install music21", file=sys.stderr)
    sys.exit(1)

from shared import (
    validate_midi_file,
    output_success,
    output_error,
    AnalysisError,
    CORRUPT_FILE,
    ANALYSIS_FAILED
)


# Constants
ANALYSIS_TYPE = "midi_key"
SEGMENT_DURATION_QUARTERS = 32  # Analyze in segments of 32 quarter notes (~8 bars in 4/4)
MIN_CONFIDENCE_FOR_MODULATION = 0.7  # Only report modulations with high confidence
KEY_CHANGE_THRESHOLD = 0.15  # Minimum confidence difference to declare a modulation


def load_midi(file_path: Path):
    """
    Load MIDI file using music21.

    Args:
        file_path: Path to MIDI file

    Returns:
        Tuple of (parsed_stream, duration_seconds)

    Raises:
        AnalysisError: If file cannot be loaded
    """
    try:
        # Parse MIDI file
        # music21 handles multi-track MIDI automatically
        score = converter.parse(str(file_path))

        # Flatten multi-track to single stream for analysis
        # This combines all tracks into one stream while preserving timing
        if hasattr(score, 'parts') and len(score.parts) > 1:
            # Multi-track MIDI: merge all parts
            flat_stream = score.flatten()
        else:
            # Single track or already flat
            flat_stream = score.flatten()

        # Calculate duration in seconds
        # music21 uses quarter notes as default time unit
        duration_seconds = flat_stream.duration.quarterLength / 2.0  # Assuming 120 BPM default

        # Try to get actual tempo if available
        tempos = flat_stream.flatten().getElementsByClass('MetronomeMark')
        if tempos:
            # Use first tempo marking
            tempo_bpm = tempos[0].number
            duration_seconds = (flat_stream.duration.quarterLength / tempo_bpm) * 60.0

        return flat_stream, duration_seconds

    except Exception as e:
        raise AnalysisError(
            CORRUPT_FILE,
            f"Failed to load MIDI file: {str(e)}",
            str(e)
        )


def analyze_key_segment(segment_stream):
    """
    Analyze key of a stream segment using Krumhansl-Schmuckler.

    Args:
        segment_stream: music21 Stream object to analyze

    Returns:
        Tuple of (key_name, mode, confidence) or None if analysis fails
    """
    try:
        # Use music21's built-in Krumhansl-Schmuckler key analysis
        # This implements the algorithm specified in the plan (TD-2)
        analyzed_key = segment_stream.analyze('key')

        if analyzed_key is None:
            return None

        # Extract key components
        key_name = analyzed_key.tonic.name
        mode = analyzed_key.mode  # 'major' or 'minor'

        # Get correlation coefficient as confidence
        # music21's analyze() returns a Key object with correlationCoefficient
        confidence = getattr(analyzed_key, 'correlationCoefficient', 0.5)

        return key_name, mode, confidence

    except Exception:
        return None


def detect_modulations(flat_stream, overall_key, overall_mode):
    """
    Detect key modulations by analyzing the piece in segments.

    Args:
        flat_stream: Flattened music21 Stream
        overall_key: Overall key of the piece
        overall_mode: Overall mode of the piece

    Returns:
        List of modulation dictionaries with time_seconds, new_key, new_mode
    """
    modulations = []

    # Get total duration in quarter notes
    total_quarters = flat_stream.duration.quarterLength

    # If piece is too short for segmentation, skip modulation detection
    if total_quarters < SEGMENT_DURATION_QUARTERS * 2:
        return modulations

    # Analyze in segments
    current_offset = 0
    current_key = overall_key
    current_mode = overall_mode

    # Get tempo for time conversion (default to 120 BPM)
    tempo_bpm = 120.0
    tempos = flat_stream.getElementsByClass('MetronomeMark')
    if tempos:
        tempo_bpm = tempos[0].number

    while current_offset < total_quarters:
        # Extract segment
        segment_end = min(current_offset + SEGMENT_DURATION_QUARTERS, total_quarters)

        # Get notes/chords in this segment
        segment_elements = flat_stream.getElementsByOffset(
            current_offset,
            segment_end,
            includeEndBoundary=False,
            mustFinishInSpan=False,
            mustBeginInSpan=False
        )

        # Create a new stream with these elements
        segment_stream = stream.Stream()
        for element in segment_elements:
            if isinstance(element, (note.Note, chord.Chord)):
                segment_stream.append(element)

        # Skip if segment is too sparse
        if len(segment_stream.notesAndRests) < 4:
            current_offset += SEGMENT_DURATION_QUARTERS
            continue

        # Analyze segment key
        result = analyze_key_segment(segment_stream)

        if result:
            seg_key, seg_mode, seg_confidence = result

            # Check if this represents a modulation
            if seg_confidence >= MIN_CONFIDENCE_FOR_MODULATION:
                # Key changed?
                if seg_key != current_key or seg_mode != current_mode:
                    # Convert offset to seconds
                    time_seconds = (current_offset / tempo_bpm) * 60.0

                    # Record modulation
                    modulations.append({
                        "time_seconds": round(time_seconds, 1),
                        "new_key": seg_key,
                        "new_mode": seg_mode
                    })

                    # Update current key
                    current_key = seg_key
                    current_mode = seg_mode

        current_offset += SEGMENT_DURATION_QUARTERS

    return modulations


def analyze_midi_key(file_path: Path):
    """
    Analyze MIDI file for key and modulations.

    Args:
        file_path: Path to MIDI file

    Returns:
        Tuple of (data_dict, duration_seconds)

    Raises:
        AnalysisError: If analysis fails
    """
    try:
        # Load MIDI file
        flat_stream, duration_seconds = load_midi(file_path)

        # Analyze overall key using Krumhansl-Schmuckler
        overall_result = analyze_key_segment(flat_stream)

        if overall_result is None:
            raise AnalysisError(
                ANALYSIS_FAILED,
                "Could not determine key from MIDI file",
                "The file may not contain enough melodic/harmonic content"
            )

        key_name, mode, confidence = overall_result

        # Detect modulations
        modulations = detect_modulations(flat_stream, key_name, mode)

        # Build result according to schema from plan
        data = {
            'key': key_name,
            'mode': mode,
            'confidence': round(confidence, 2),
            'modulations': modulations
        }

        return data, duration_seconds

    except AnalysisError:
        raise
    except Exception as e:
        raise AnalysisError(
            ANALYSIS_FAILED,
            f"MIDI key analysis failed: {str(e)}",
            str(e)
        )


def main():
    """Main entry point for MIDI key analysis script."""
    parser = argparse.ArgumentParser(
        description="Estimate musical key and detect modulations from MIDI files"
    )
    parser.add_argument(
        "file_path",
        help="Path to MIDI file (.mid, .midi)"
    )

    args = parser.parse_args()

    try:
        # Validate MIDI file
        file_path, file_size, extension = validate_midi_file(args.file_path)

        # Analyze MIDI key
        data, duration_seconds = analyze_midi_key(file_path)

        # Output success
        output_success(
            file_path=str(file_path),
            analysis_type=ANALYSIS_TYPE,
            data=data,
            duration_seconds=round(duration_seconds, 2),
            truncated=False,
            warnings=[]
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
