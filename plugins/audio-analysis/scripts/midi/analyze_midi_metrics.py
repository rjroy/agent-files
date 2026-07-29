#!/usr/bin/env python3
"""
MIDI Complexity Metrics Script

Calculates complexity metrics for MIDI files including note count, voice leading,
note density, and pitch range.

Usage:
    python analyze_midi_metrics.py <file_path>

Output:
    JSON to stdout with complexity metrics
    Errors to stderr with non-zero exit code

Requirements:
    - MIDI file (.mid, .midi)
    - music21 library for MIDI analysis
"""

import sys
import argparse
from pathlib import Path
from typing import List, Dict, Tuple

# Add parent directory to path for shared imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from music21 import converter, stream, note, chord, pitch
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
ANALYSIS_TYPE = "midi_metrics"
STEPWISE_MOTION_THRESHOLD = 2  # Intervals <= 2 semitones are stepwise


def load_midi(file_path: Path):
    """
    Load MIDI file using music21.

    Args:
        file_path: Path to MIDI file

    Returns:
        Tuple of (parsed_score, tempo_bpm)

    Raises:
        AnalysisError: If file cannot be loaded
    """
    try:
        # Parse MIDI file
        score = converter.parse(str(file_path))

        # Get tempo (default to 120 BPM)
        tempo_bpm = 120.0
        tempos = score.flatten().getElementsByClass('MetronomeMark')
        if tempos:
            tempo_bpm = tempos[0].number

        return score, tempo_bpm

    except Exception as e:
        raise AnalysisError(
            CORRUPT_FILE,
            f"Failed to load MIDI file: {str(e)}",
            str(e)
        )


def count_notes(score) -> int:
    """
    Count total notes across all tracks.

    Args:
        score: music21 Score object

    Returns:
        Total number of notes
    """
    flat_stream = score.flatten()
    note_count = 0

    for element in flat_stream.notesAndRests:
        if isinstance(element, note.Note):
            note_count += 1
        elif isinstance(element, chord.Chord):
            # Each note in a chord counts separately
            note_count += len(element.pitches)

    return note_count


def count_tracks(score) -> int:
    """
    Count number of tracks/parts in the score.

    Args:
        score: music21 Score object

    Returns:
        Number of tracks
    """
    if hasattr(score, 'parts'):
        return len(score.parts)
    else:
        # Single track MIDI
        return 1


def analyze_voice_leading(score) -> Dict:
    """
    Calculate voice leading metrics including stepwise motion percentage.

    Args:
        score: music21 Score object

    Returns:
        Dictionary with voice leading statistics
    """
    # Extract all notes in order with their pitches
    flat_stream = score.flatten()
    pitches_sequence = []

    for element in flat_stream.notesAndRests:
        if isinstance(element, note.Note):
            pitches_sequence.append(element.pitch.midi)
        elif isinstance(element, chord.Chord):
            # For chords, take the highest note (melody)
            highest_pitch = max(p.midi for p in element.pitches)
            pitches_sequence.append(highest_pitch)

    if len(pitches_sequence) < 2:
        return {
            'stepwise_motion_pct': 0.0,
            'leap_motion_pct': 0.0,
            'average_interval': 0.0
        }

    # Calculate intervals between consecutive notes
    intervals = []
    stepwise_count = 0
    leap_count = 0

    for i in range(len(pitches_sequence) - 1):
        interval = abs(pitches_sequence[i + 1] - pitches_sequence[i])
        intervals.append(interval)

        if interval <= STEPWISE_MOTION_THRESHOLD:
            stepwise_count += 1
        else:
            leap_count += 1

    # Calculate percentages
    total_intervals = len(intervals)
    stepwise_pct = stepwise_count / total_intervals if total_intervals > 0 else 0.0
    leap_pct = leap_count / total_intervals if total_intervals > 0 else 0.0

    # Average interval size
    avg_interval = sum(intervals) / len(intervals) if intervals else 0.0

    return {
        'stepwise_motion_pct': round(stepwise_pct, 2),
        'leap_motion_pct': round(leap_pct, 2),
        'average_interval': round(avg_interval, 1)
    }


def calculate_note_density(score, tempo_bpm: float) -> float:
    """
    Calculate note density (notes per second).

    Args:
        score: music21 Score object
        tempo_bpm: Tempo in beats per minute

    Returns:
        Notes per second
    """
    flat_stream = score.flatten()
    total_notes = count_notes(score)

    # Calculate duration in seconds
    total_quarter_length = flat_stream.duration.quarterLength
    seconds_per_quarter = 60.0 / tempo_bpm
    duration_seconds = total_quarter_length * seconds_per_quarter

    if duration_seconds == 0:
        return 0.0

    return round(total_notes / duration_seconds, 2)


def find_pitch_range(score) -> Dict:
    """
    Find the lowest and highest pitches in the score.

    Args:
        score: music21 Score object

    Returns:
        Dictionary with lowest and highest pitch names
    """
    flat_stream = score.flatten()
    all_pitches = []

    for element in flat_stream.notesAndRests:
        if isinstance(element, note.Note):
            all_pitches.append(element.pitch.midi)
        elif isinstance(element, chord.Chord):
            for p in element.pitches:
                all_pitches.append(p.midi)

    if not all_pitches:
        return {
            'lowest': None,
            'highest': None
        }

    lowest_midi = min(all_pitches)
    highest_midi = max(all_pitches)

    # Convert MIDI to note names
    lowest_pitch = pitch.Pitch(midi=lowest_midi)
    highest_pitch = pitch.Pitch(midi=highest_midi)

    return {
        'lowest': lowest_pitch.nameWithOctave,
        'highest': highest_pitch.nameWithOctave
    }


def analyze_midi_metrics(file_path: Path):
    """
    Analyze MIDI file for complexity metrics.

    Args:
        file_path: Path to MIDI file

    Returns:
        Tuple of (data_dict, duration_seconds)

    Raises:
        AnalysisError: If analysis fails
    """
    try:
        # Load MIDI file
        score, tempo_bpm = load_midi(file_path)

        # Count notes
        note_count = count_notes(score)

        if note_count == 0:
            raise AnalysisError(
                ANALYSIS_FAILED,
                "No notes found in MIDI file",
                "The file may be empty or contain only rests"
            )

        # Count tracks
        track_count = count_tracks(score)

        # Analyze voice leading
        voice_leading = analyze_voice_leading(score)

        # Calculate note density
        note_density = calculate_note_density(score, tempo_bpm)

        # Find pitch range
        pitch_range = find_pitch_range(score)

        # Calculate duration
        flat_stream = score.flatten()
        total_quarter_length = flat_stream.duration.quarterLength
        seconds_per_quarter = 60.0 / tempo_bpm
        duration_seconds = total_quarter_length * seconds_per_quarter

        # Build result according to schema from plan
        data = {
            'note_count': note_count,
            'track_count': track_count,
            'voice_leading': voice_leading,
            'note_density_per_second': note_density,
            'pitch_range': pitch_range
        }

        return data, duration_seconds

    except AnalysisError:
        raise
    except Exception as e:
        raise AnalysisError(
            ANALYSIS_FAILED,
            f"MIDI metrics analysis failed: {str(e)}",
            str(e)
        )


def main():
    """Main entry point for MIDI metrics analysis script."""
    parser = argparse.ArgumentParser(
        description="Calculate complexity metrics for MIDI files"
    )
    parser.add_argument(
        "file_path",
        help="Path to MIDI file (.mid, .midi)"
    )

    args = parser.parse_args()

    try:
        # Validate MIDI file
        file_path, file_size, extension = validate_midi_file(args.file_path)

        # Analyze MIDI metrics
        data, duration_seconds = analyze_midi_metrics(file_path)

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
