#!/usr/bin/env python3
"""
MIDI Chord Progression Analysis Script

Extracts chord progressions with Roman numeral notation from MIDI files.
Identifies chords with root, quality, and functional analysis in key context.

Usage:
    python analyze_midi_chords.py <file_path>

Output:
    JSON to stdout with key_context and chord_progression array
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
    from music21 import converter, key, roman, chord as m21_chord, note, stream
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
ANALYSIS_TYPE = "midi_chords"
MIN_CHORD_DURATION = 0.1  # Minimum duration in quarter notes to consider as a chord
QUANTIZE_GRID = 0.5  # Quantize chord positions to this grid (quarter notes)


def load_midi(file_path: Path):
    """
    Load MIDI file and flatten to single stream for chord analysis.

    Args:
        file_path: Path to MIDI file

    Returns:
        Tuple of (flattened_stream, tempo_bpm)

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

        return score, tempo_bpm

    except Exception as e:
        raise AnalysisError(
            CORRUPT_FILE,
            f"Failed to load MIDI file: {str(e)}",
            str(e)
        )


def detect_key(score):
    """
    Detect the key of the MIDI file.

    Args:
        score: music21 Score object

    Returns:
        music21 Key object

    Raises:
        AnalysisError: If key cannot be determined
    """
    try:
        # Flatten and analyze key
        flat_stream = score.flatten()
        analyzed_key = flat_stream.analyze('key')

        if analyzed_key is None:
            raise AnalysisError(
                ANALYSIS_FAILED,
                "Could not determine key from MIDI file",
                "The file may not contain enough harmonic content"
            )

        return analyzed_key

    except AnalysisError:
        raise
    except Exception as e:
        raise AnalysisError(
            ANALYSIS_FAILED,
            f"Key detection failed: {str(e)}",
            str(e)
        )


def extract_chords_from_score(score, tempo_bpm):
    """
    Extract chords from MIDI score using chordify.

    Args:
        score: music21 Score object
        tempo_bpm: Tempo in beats per minute

    Returns:
        List of dictionaries with time, chord_obj, and duration

    Notes:
        Uses music21's chordify() to collapse multi-track MIDI into vertical slices.
        This is the recommended approach per music21 documentation.
    """
    try:
        # Use chordify to collapse all tracks into vertical slices
        # This automatically handles multi-track MIDI and creates chord objects
        chordified = score.chordify()

        chord_data = []

        # Iterate through all elements in chordified stream
        for element in chordified.flatten().notesAndRests:
            # Skip rests and very short notes
            if isinstance(element, note.Rest):
                continue

            if element.quarterLength < MIN_CHORD_DURATION:
                continue

            # Get offset in quarter notes
            offset_quarters = element.offset

            # Convert to seconds
            time_seconds = (offset_quarters / tempo_bpm) * 60.0

            # Quantize to grid to reduce micro-timing variations
            time_seconds = round(time_seconds / (QUANTIZE_GRID / tempo_bpm * 60.0)) * (QUANTIZE_GRID / tempo_bpm * 60.0)

            # Get duration in seconds
            duration_seconds = (element.quarterLength / tempo_bpm) * 60.0

            chord_data.append({
                'time': round(time_seconds, 2),
                'chord_obj': element,
                'duration': round(duration_seconds, 2)
            })

        return chord_data

    except Exception as e:
        raise AnalysisError(
            ANALYSIS_FAILED,
            f"Chord extraction failed: {str(e)}",
            str(e)
        )


def get_chord_name(chord_obj):
    """
    Get chord name from music21 chord object.

    Args:
        chord_obj: music21 Note or Chord object

    Returns:
        String chord name (e.g., "Gmaj", "Cmaj", "Dmin7")
    """
    # Handle single notes (treat as major chord on that root)
    if isinstance(chord_obj, note.Note):
        return f"{chord_obj.pitch.name}maj"

    # Handle chord objects
    if isinstance(chord_obj, m21_chord.Chord):
        # Try to get common name
        try:
            # Get root and quality
            root = chord_obj.root().name
            quality = chord_obj.quality

            # Map quality to suffix
            if quality == 'major':
                suffix = 'maj'
            elif quality == 'minor':
                suffix = 'min'
            elif quality == 'diminished':
                suffix = 'dim'
            elif quality == 'augmented':
                suffix = 'aug'
            elif quality == 'dominant-seventh':
                suffix = '7'
            elif quality == 'major-seventh':
                suffix = 'maj7'
            elif quality == 'minor-seventh':
                suffix = 'min7'
            elif quality == 'diminished-seventh':
                suffix = 'dim7'
            elif quality == 'half-diminished-seventh':
                suffix = 'ø7'
            else:
                # Default to pitch class name
                suffix = 'maj'

            return f"{root}{suffix}"

        except Exception:
            # Fallback: just use root note
            try:
                root = chord_obj.root().name
                return f"{root}maj"
            except Exception:
                # Last resort: use first pitch
                if len(chord_obj.pitches) > 0:
                    return f"{chord_obj.pitches[0].name}maj"
                return "Unknown"

    return "Unknown"


def get_roman_numeral(chord_obj, analyzed_key):
    """
    Get Roman numeral analysis for a chord in the given key.

    Args:
        chord_obj: music21 Note or Chord object
        analyzed_key: music21 Key object

    Returns:
        String Roman numeral (e.g., "I", "IV", "V", "vi")
    """
    try:
        # Handle single notes
        if isinstance(chord_obj, note.Note):
            # Create a simple major chord from the note
            simple_chord = m21_chord.Chord([chord_obj.pitch])
            return str(roman.romanNumeralFromChord(simple_chord, analyzed_key).figure)

        # Handle chords
        if isinstance(chord_obj, m21_chord.Chord):
            # Use music21's romanNumeralFromChord function
            rn = roman.romanNumeralFromChord(chord_obj, analyzed_key)
            return str(rn.figure)

        return "?"

    except Exception:
        # Fallback: try to determine scale degree from root
        try:
            if isinstance(chord_obj, note.Note):
                root_pitch = chord_obj.pitch
            else:
                root_pitch = chord_obj.root()

            # Get scale degree
            scale_degree = analyzed_key.getScaleDegreeFromPitch(root_pitch)

            # Map to Roman numeral (simple major/minor logic)
            # This is a fallback and won't capture quality perfectly
            roman_numerals = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII']
            if scale_degree and 1 <= scale_degree <= 7:
                return roman_numerals[scale_degree - 1]

        except Exception:
            pass

        return "?"


def analyze_midi_chords(file_path: Path):
    """
    Analyze MIDI file for chord progression with Roman numerals.

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

        # Detect key
        analyzed_key = detect_key(score)

        # Extract chords
        chord_data = extract_chords_from_score(score, tempo_bpm)

        # Build chord progression with Roman numerals
        chord_progression = []

        for chord_info in chord_data:
            chord_obj = chord_info['chord_obj']

            # Get chord name and Roman numeral
            chord_name = get_chord_name(chord_obj)
            roman_numeral = get_roman_numeral(chord_obj, analyzed_key)

            chord_progression.append({
                'time': chord_info['time'],
                'chord': chord_name,
                'roman': roman_numeral,
                'duration': chord_info['duration']
            })

        # Calculate total duration
        if chord_progression:
            duration_seconds = max(
                c['time'] + c['duration'] for c in chord_progression
            )
        else:
            # Fallback to score duration
            duration_seconds = (score.flatten().duration.quarterLength / tempo_bpm) * 60.0

        # Build result according to schema from plan
        data = {
            'key_context': f"{analyzed_key.tonic.name} {analyzed_key.mode}",
            'chord_progression': chord_progression
        }

        return data, duration_seconds

    except AnalysisError:
        raise
    except Exception as e:
        raise AnalysisError(
            ANALYSIS_FAILED,
            f"MIDI chord analysis failed: {str(e)}",
            str(e)
        )


def main():
    """Main entry point for MIDI chord analysis script."""
    parser = argparse.ArgumentParser(
        description="Extract chord progressions with Roman numerals from MIDI files"
    )
    parser.add_argument(
        "file_path",
        help="Path to MIDI file (.mid, .midi)"
    )

    args = parser.parse_args()

    try:
        # Validate MIDI file
        file_path, file_size, extension = validate_midi_file(args.file_path)

        # Analyze MIDI chords
        data, duration_seconds = analyze_midi_chords(file_path)

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
