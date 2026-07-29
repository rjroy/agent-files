#!/usr/bin/env python3
"""
MIDI Rhythm Analysis Script

Analyzes rhythmic structures including time signature, tempo, note durations,
and syncopation patterns in MIDI files.

Usage:
    python analyze_midi_rhythm.py <file_path>

Output:
    JSON to stdout with time signature, tempo, note duration distribution, and syncopation score
    Errors to stderr with non-zero exit code

Requirements:
    - MIDI file (.mid, .midi)
    - music21 library for MIDI analysis
"""

import sys
import argparse
from pathlib import Path
from collections import Counter
from typing import Dict, Tuple

# Add parent directory to path for shared imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from music21 import converter, stream, note, chord, meter, tempo as m21_tempo
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
ANALYSIS_TYPE = "midi_rhythm"

# Duration thresholds in quarter notes
# These are the standard note duration values
WHOLE_NOTE = 4.0
HALF_NOTE = 2.0
QUARTER_NOTE = 1.0
EIGHTH_NOTE = 0.5
SIXTEENTH_NOTE = 0.25

# Tolerance for duration classification (to handle slight variations)
DURATION_TOLERANCE = 0.1


def load_midi(file_path: Path):
    """
    Load MIDI file and prepare for rhythm analysis.

    Args:
        file_path: Path to MIDI file

    Returns:
        music21 Score object

    Raises:
        AnalysisError: If file cannot be loaded
    """
    try:
        # Parse MIDI file
        score = converter.parse(str(file_path))
        return score

    except Exception as e:
        raise AnalysisError(
            CORRUPT_FILE,
            f"Failed to load MIDI file: {str(e)}",
            str(e)
        )


def extract_time_signature(score) -> str:
    """
    Extract time signature from MIDI file.

    Args:
        score: music21 Score object

    Returns:
        Time signature as string (e.g., "4/4", "3/4", "6/8")
    """
    # Look for time signature in the score
    time_sigs = score.flatten().getElementsByClass(meter.TimeSignature)

    if time_sigs:
        # Use the first time signature found
        ts = time_sigs[0]
        return ts.ratioString  # Returns format like "4/4"
    else:
        # Default to 4/4 if not specified
        return "4/4"


def extract_tempo(score) -> float:
    """
    Extract tempo (BPM) from MIDI file.

    Args:
        score: music21 Score object

    Returns:
        Tempo in beats per minute
    """
    # Look for tempo markings
    tempos = score.flatten().getElementsByClass('MetronomeMark')

    if tempos:
        # Use the first tempo marking
        return float(tempos[0].number)
    else:
        # Default to 120 BPM if not specified
        return 120.0


def classify_duration(duration_quarters: float) -> str:
    """
    Classify note duration into standard rhythmic values.

    Args:
        duration_quarters: Duration in quarter notes

    Returns:
        Duration category: "whole", "half", "quarter", "eighth", "sixteenth", or "other"
    """
    # Check against standard durations with tolerance
    if abs(duration_quarters - WHOLE_NOTE) <= DURATION_TOLERANCE:
        return "whole"
    elif abs(duration_quarters - HALF_NOTE) <= DURATION_TOLERANCE:
        return "half"
    elif abs(duration_quarters - QUARTER_NOTE) <= DURATION_TOLERANCE:
        return "quarter"
    elif abs(duration_quarters - EIGHTH_NOTE) <= DURATION_TOLERANCE:
        return "eighth"
    elif abs(duration_quarters - SIXTEENTH_NOTE) <= DURATION_TOLERANCE:
        return "sixteenth"
    else:
        # Handle dotted notes and other common durations
        if abs(duration_quarters - 1.5) <= DURATION_TOLERANCE:  # Dotted quarter
            return "quarter"
        elif abs(duration_quarters - 0.75) <= DURATION_TOLERANCE:  # Dotted eighth
            return "eighth"
        elif abs(duration_quarters - 3.0) <= DURATION_TOLERANCE:  # Dotted half
            return "half"
        else:
            return "other"


def analyze_note_durations(score) -> Dict[str, int]:
    """
    Analyze and categorize all note durations in the MIDI file.

    Args:
        score: music21 Score object

    Returns:
        Dictionary mapping duration categories to counts
    """
    duration_counter = Counter()

    # Get all notes from all parts
    flat_score = score.flatten()

    for element in flat_score.notesAndRests:
        # Only count actual notes (skip rests)
        if isinstance(element, (note.Note, chord.Chord)):
            duration_quarters = element.quarterLength
            category = classify_duration(duration_quarters)

            # Don't include "other" in the final output
            if category != "other":
                duration_counter[category] += 1

    # Ensure all standard durations are present (even if 0)
    result = {
        "whole": duration_counter.get("whole", 0),
        "half": duration_counter.get("half", 0),
        "quarter": duration_counter.get("quarter", 0),
        "eighth": duration_counter.get("eighth", 0),
        "sixteenth": duration_counter.get("sixteenth", 0)
    }

    return result


def calculate_syncopation_score(score, time_sig_str: str) -> float:
    """
    Calculate a syncopation score based on off-beat note placements.

    Args:
        score: music21 Score object
        time_sig_str: Time signature as string (e.g., "4/4")

    Returns:
        Syncopation score between 0.0 (no syncopation) and 1.0 (highly syncopated)
    """
    # Parse time signature
    numerator = int(time_sig_str.split('/')[0])
    denominator = int(time_sig_str.split('/')[1])

    # Determine beat unit in quarter notes
    # For 4/4, beat is 1.0 quarter notes
    # For 3/4, beat is 1.0 quarter notes
    # For 6/8, beat is 1.5 quarter notes (dotted quarter)
    if denominator == 8 and numerator % 3 == 0:
        # Compound meter (6/8, 9/8, 12/8)
        beat_duration = 1.5
    else:
        # Simple meter
        beat_duration = 4.0 / denominator

    flat_score = score.flatten()
    total_notes = 0
    syncopated_notes = 0

    for element in flat_score.notesAndRests:
        if isinstance(element, (note.Note, chord.Chord)):
            total_notes += 1

            # Get the offset within the measure
            offset = element.offset

            # Check if note starts on an off-beat
            # A note is on-beat if its offset is a multiple of the beat duration
            position_in_beat = offset % beat_duration

            # Tolerance for floating-point comparison
            tolerance = 0.05

            # Check if note is off-beat (not at beat_duration intervals)
            is_on_beat = position_in_beat < tolerance or (beat_duration - position_in_beat) < tolerance

            if not is_on_beat:
                # Further check: is it on a subdivision?
                # Eighth note subdivisions (half of beat)
                position_in_subdivision = offset % (beat_duration / 2)
                is_on_subdivision = position_in_subdivision < tolerance or ((beat_duration / 2) - position_in_subdivision) < tolerance

                # Consider it syncopated if it's truly off the grid
                if not is_on_subdivision:
                    syncopated_notes += 1

    if total_notes == 0:
        return 0.0

    # Calculate syncopation score as ratio
    syncopation_score = syncopated_notes / total_notes

    return round(syncopation_score, 2)


def analyze_midi_rhythm(file_path: Path):
    """
    Analyze MIDI file for rhythmic characteristics.

    Args:
        file_path: Path to MIDI file

    Returns:
        Tuple of (data_dict, duration_seconds)

    Raises:
        AnalysisError: If analysis fails
    """
    try:
        # Load MIDI file
        score = load_midi(file_path)

        # Extract time signature
        time_signature = extract_time_signature(score)

        # Extract tempo
        tempo_bpm = extract_tempo(score)

        # Analyze note durations
        note_durations = analyze_note_durations(score)

        # Calculate syncopation score
        syncopation_score = calculate_syncopation_score(score, time_signature)

        # Calculate duration
        flat_score = score.flatten()
        duration_seconds = (flat_score.duration.quarterLength / tempo_bpm) * 60.0

        # Build result according to schema from plan
        data = {
            'time_signature': time_signature,
            'tempo_bpm': int(tempo_bpm),
            'note_durations': note_durations,
            'syncopation_score': syncopation_score
        }

        return data, duration_seconds

    except AnalysisError:
        raise
    except Exception as e:
        raise AnalysisError(
            ANALYSIS_FAILED,
            f"MIDI rhythm analysis failed: {str(e)}",
            str(e)
        )


def main():
    """Main entry point for MIDI rhythm analysis script."""
    parser = argparse.ArgumentParser(
        description="Analyze rhythmic structures in MIDI files including time signature, tempo, and syncopation"
    )
    parser.add_argument(
        "file_path",
        help="Path to MIDI file (.mid, .midi)"
    )

    args = parser.parse_args()

    try:
        # Validate MIDI file
        file_path, file_size, extension = validate_midi_file(args.file_path)

        # Analyze MIDI rhythm
        data, duration_seconds = analyze_midi_rhythm(file_path)

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
