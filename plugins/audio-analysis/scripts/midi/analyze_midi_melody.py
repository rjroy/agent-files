#!/usr/bin/env python3
"""
MIDI Melodic Pattern Detection Script

Identifies recurring melodic motifs and patterns in MIDI files.
Extracts note sequences and finds repeated melodic fragments.

Usage:
    python analyze_midi_melody.py <file_path>

Output:
    JSON to stdout with melodic motifs and their occurrences
    Errors to stderr with non-zero exit code

Requirements:
    - MIDI file (.mid, .midi)
    - music21 library for MIDI analysis
"""

import sys
import argparse
from pathlib import Path
from collections import defaultdict
from typing import List, Tuple, Dict

# Add parent directory to path for shared imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from music21 import converter, stream, note, chord, instrument
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
ANALYSIS_TYPE = "midi_melody"
MIN_MOTIF_LENGTH = 3  # Minimum notes in a motif
MAX_MOTIF_LENGTH = 8  # Maximum notes in a motif
MIN_OCCURRENCES = 2   # Minimum times a pattern must appear to be considered a motif
PITCH_TOLERANCE_SEMITONES = 0  # Exact pitch matching (0 = exact, >0 = allow transposition)


def load_midi(file_path: Path):
    """
    Load MIDI file and extract melody track.

    Args:
        file_path: Path to MIDI file

    Returns:
        Tuple of (melody_stream, tempo_bpm)

    Raises:
        AnalysisError: If file cannot be loaded
    """
    try:
        # Parse MIDI file
        score = converter.parse(str(file_path))

        # Get tempo for time conversion (default to 120 BPM)
        tempo_bpm = 120.0
        tempos = score.flatten().getElementsByClass('MetronomeMark')
        if tempos:
            tempo_bpm = tempos[0].number

        # Extract melody track
        # Strategy: Use the track with the highest average pitch (usually melody)
        # or the first track if it's a single-track MIDI

        if hasattr(score, 'parts') and len(score.parts) > 1:
            # Multi-track: find melody track (highest average pitch)
            melody_part = None
            highest_avg_pitch = -1

            for part in score.parts:
                notes_in_part = part.flatten().notes
                if len(notes_in_part) > 0:
                    # Calculate average MIDI pitch
                    avg_pitch = sum(n.pitch.midi if isinstance(n, note.Note)
                                   else (max(p.midi for p in n.pitches) if isinstance(n, chord.Chord) else 0)
                                   for n in notes_in_part) / len(notes_in_part)

                    if avg_pitch > highest_avg_pitch:
                        highest_avg_pitch = avg_pitch
                        melody_part = part

            if melody_part is None:
                # Fallback to flattened score
                melody_stream = score.flatten()
            else:
                melody_stream = melody_part.flatten()
        else:
            # Single track or already flat
            melody_stream = score.flatten()

        return melody_stream, tempo_bpm

    except Exception as e:
        raise AnalysisError(
            CORRUPT_FILE,
            f"Failed to load MIDI file: {str(e)}",
            str(e)
        )


def extract_note_sequence(melody_stream) -> List[Tuple[int, float]]:
    """
    Extract a sequence of (pitch, offset) tuples from the melody stream.

    Args:
        melody_stream: music21 Stream containing melody

    Returns:
        List of (midi_pitch, offset_quarters) tuples
    """
    note_sequence = []

    for element in melody_stream.flatten().notesAndRests:
        # Only include actual notes (skip rests)
        if isinstance(element, note.Note):
            note_sequence.append((element.pitch.midi, element.offset))
        elif isinstance(element, chord.Chord):
            # For chords, take the highest note (melody line)
            highest_pitch = max(p.midi for p in element.pitches)
            note_sequence.append((highest_pitch, element.offset))

    return note_sequence


def find_motifs(note_sequence: List[Tuple[int, float]],
                min_length: int,
                max_length: int,
                min_occurrences: int) -> List[Dict]:
    """
    Find recurring melodic motifs in the note sequence.

    Args:
        note_sequence: List of (pitch, offset) tuples
        min_length: Minimum motif length in notes
        max_length: Maximum motif length in notes
        min_occurrences: Minimum number of times pattern must appear

    Returns:
        List of motif dictionaries with pattern, occurrences, and positions
    """
    if len(note_sequence) < min_length:
        return []

    # Extract just pitches for pattern matching
    pitches = [pitch for pitch, _ in note_sequence]

    # Dictionary to store pattern occurrences
    # Key: tuple of pitches, Value: list of starting indices
    pattern_occurrences = defaultdict(list)

    # Search for patterns of different lengths
    for length in range(min_length, max_length + 1):
        # Slide window across the pitch sequence
        for i in range(len(pitches) - length + 1):
            pattern = tuple(pitches[i:i + length])
            pattern_occurrences[pattern].append(i)

    # Filter patterns that occur at least min_occurrences times
    # and convert to result format
    motifs = []

    # Sort by number of occurrences (most frequent first)
    sorted_patterns = sorted(
        pattern_occurrences.items(),
        key=lambda x: len(x[1]),
        reverse=True
    )

    for pattern, indices in sorted_patterns:
        if len(indices) >= min_occurrences:
            # Convert pattern to note names
            pattern_notes = []
            for pitch_midi in pattern:
                # Convert MIDI pitch to note name
                from music21 import pitch
                p = pitch.Pitch(midi=pitch_midi)
                pattern_notes.append(p.nameWithOctave)

            # Get time positions for each occurrence
            positions = []
            for idx in indices:
                _, offset_quarters = note_sequence[idx]
                positions.append(offset_quarters)

            motifs.append({
                'pattern': pattern_notes,
                'length': len(pattern),
                'occurrences': len(indices),
                'positions_quarters': positions
            })

    return motifs


def convert_positions_to_seconds(motifs: List[Dict], tempo_bpm: float) -> List[Dict]:
    """
    Convert quarter note positions to seconds.

    Args:
        motifs: List of motif dictionaries
        tempo_bpm: Tempo in beats per minute

    Returns:
        Updated motif dictionaries with time in seconds
    """
    for motif in motifs:
        positions_seconds = [
            round((pos / tempo_bpm) * 60.0, 2)
            for pos in motif['positions_quarters']
        ]
        motif['positions_seconds'] = positions_seconds
        # Remove quarter note positions from output
        del motif['positions_quarters']

    return motifs


def analyze_midi_melody(file_path: Path):
    """
    Analyze MIDI file for melodic patterns and motifs.

    Args:
        file_path: Path to MIDI file

    Returns:
        Tuple of (data_dict, duration_seconds)

    Raises:
        AnalysisError: If analysis fails
    """
    try:
        # Load MIDI file
        melody_stream, tempo_bpm = load_midi(file_path)

        # Extract note sequence
        note_sequence = extract_note_sequence(melody_stream)

        if len(note_sequence) == 0:
            raise AnalysisError(
                ANALYSIS_FAILED,
                "No melodic content found in MIDI file",
                "The file may contain only rhythm or be empty"
            )

        # Find recurring motifs
        motifs = find_motifs(
            note_sequence,
            MIN_MOTIF_LENGTH,
            MAX_MOTIF_LENGTH,
            MIN_OCCURRENCES
        )

        # Convert positions to seconds
        motifs = convert_positions_to_seconds(motifs, tempo_bpm)

        # Calculate duration
        if note_sequence:
            last_note_offset = note_sequence[-1][1]
            duration_seconds = (last_note_offset / tempo_bpm) * 60.0
        else:
            duration_seconds = 0.0

        # Build result
        data = {
            'melodic_motifs': motifs,
            'total_notes': len(note_sequence),
            'unique_motifs_found': len(motifs)
        }

        return data, duration_seconds

    except AnalysisError:
        raise
    except Exception as e:
        raise AnalysisError(
            ANALYSIS_FAILED,
            f"MIDI melody analysis failed: {str(e)}",
            str(e)
        )


def main():
    """Main entry point for MIDI melody analysis script."""
    parser = argparse.ArgumentParser(
        description="Detect melodic patterns and recurring motifs in MIDI files"
    )
    parser.add_argument(
        "file_path",
        help="Path to MIDI file (.mid, .midi)"
    )

    args = parser.parse_args()

    try:
        # Validate MIDI file
        file_path, file_size, extension = validate_midi_file(args.file_path)

        # Analyze MIDI melody
        data, duration_seconds = analyze_midi_melody(file_path)

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
