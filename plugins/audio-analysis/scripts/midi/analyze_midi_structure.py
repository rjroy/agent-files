#!/usr/bin/env python3
"""
MIDI Structure Detection Script

Identifies structural sections (A-B-A form, verse/chorus) in MIDI files.
Segments the piece by analyzing melodic and harmonic similarity.

Usage:
    python analyze_midi_structure.py <file_path>

Output:
    JSON to stdout with structural sections and labels
    Errors to stderr with non-zero exit code

Requirements:
    - MIDI file (.mid, .midi)
    - music21 library for MIDI analysis
"""

import sys
import argparse
from pathlib import Path
from typing import List, Dict, Tuple
from collections import defaultdict

# Add parent directory to path for shared imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from music21 import converter, stream, note, chord, key, analysis
    import numpy as np
except ImportError as e:
    print(f"Error: Missing required library: {e}", file=sys.stderr)
    print("Install with: pip install music21 numpy", file=sys.stderr)
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
ANALYSIS_TYPE = "midi_structure"
SEGMENT_LENGTH_MEASURES = 4  # Analyze in 4-measure segments
MIN_SEGMENT_SIMILARITY = 0.7  # Threshold for considering segments similar (same section)
SECTION_LABELS = ['A', 'B', 'C', 'D', 'E']  # Labels for distinct sections


def load_midi(file_path: Path):
    """
    Load MIDI file using music21.

    Args:
        file_path: Path to MIDI file

    Returns:
        Tuple of (parsed_score, tempo_bpm, time_signature)

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

        # Get time signature (default to 4/4)
        time_sig = "4/4"
        time_sigs = score.flatten().getElementsByClass('TimeSignature')
        if time_sigs:
            ts = time_sigs[0]
            time_sig = f"{ts.numerator}/{ts.denominator}"

        return score, tempo_bpm, time_sig

    except Exception as e:
        raise AnalysisError(
            CORRUPT_FILE,
            f"Failed to load MIDI file: {str(e)}",
            str(e)
        )


def extract_segment_features(segment_stream) -> Dict:
    """
    Extract musical features from a segment for comparison.

    Args:
        segment_stream: music21 Stream object

    Returns:
        Dictionary with pitch classes, intervals, and density
    """
    # Extract pitch class distribution (12-element vector)
    pitch_class_counts = [0] * 12
    note_count = 0
    intervals = []
    prev_pitch = None

    for element in segment_stream.flatten().notesAndRests:
        if isinstance(element, note.Note):
            pitch_class = element.pitch.pitchClass
            pitch_class_counts[pitch_class] += 1
            note_count += 1

            # Track intervals
            if prev_pitch is not None:
                interval = abs(element.pitch.midi - prev_pitch)
                intervals.append(interval)
            prev_pitch = element.pitch.midi

        elif isinstance(element, chord.Chord):
            # For chords, count all pitch classes
            for p in element.pitches:
                pitch_class_counts[p.pitchClass] += 1
                note_count += 1

    # Normalize pitch class distribution
    if note_count > 0:
        pitch_class_dist = [count / note_count for count in pitch_class_counts]
    else:
        pitch_class_dist = [0] * 12

    # Average interval
    avg_interval = sum(intervals) / len(intervals) if intervals else 0

    return {
        'pitch_class_dist': pitch_class_dist,
        'note_count': note_count,
        'avg_interval': avg_interval
    }


def calculate_segment_similarity(features1: Dict, features2: Dict) -> float:
    """
    Calculate similarity between two segments based on their features.

    Args:
        features1: Features from first segment
        features2: Features from second segment

    Returns:
        Similarity score between 0 and 1
    """
    # Cosine similarity of pitch class distributions
    pc1 = np.array(features1['pitch_class_dist'])
    pc2 = np.array(features2['pitch_class_dist'])

    # Avoid division by zero
    norm1 = np.linalg.norm(pc1)
    norm2 = np.linalg.norm(pc2)

    if norm1 == 0 or norm2 == 0:
        return 0.0

    cosine_sim = np.dot(pc1, pc2) / (norm1 * norm2)

    # Additional factors: note density and interval patterns
    density_diff = abs(features1['note_count'] - features2['note_count'])
    interval_diff = abs(features1['avg_interval'] - features2['avg_interval'])

    # Weight cosine similarity highest, penalize large differences
    similarity = cosine_sim * 0.7
    similarity -= min(density_diff / 20.0, 0.2)  # Cap penalty at 0.2
    similarity -= min(interval_diff / 12.0, 0.1)  # Cap penalty at 0.1

    return max(0.0, min(1.0, similarity))


def segment_by_measures(score, segment_length_measures: int, time_signature: str) -> List[Tuple[stream.Stream, float, float]]:
    """
    Divide score into measure-based segments.

    Args:
        score: music21 Score object
        segment_length_measures: Length of each segment in measures
        time_signature: Time signature string (e.g., "4/4")

    Returns:
        List of (segment_stream, start_measure, end_measure) tuples
    """
    # Flatten to single stream
    flat_stream = score.flatten()

    # Get total measures
    # In music21, measures are numbered starting from 1
    measures = flat_stream.getElementsByClass('Measure')
    if not measures:
        # If no explicit measures, estimate based on time signature
        # For now, treat the entire piece as one segment
        numerator = int(time_signature.split('/')[0])
        total_quarter_length = flat_stream.duration.quarterLength
        quarters_per_measure = numerator  # Simplified assumption
        total_measures = int(total_quarter_length / quarters_per_measure)
    else:
        total_measures = len(measures)

    segments = []
    current_measure = 1

    while current_measure <= total_measures:
        end_measure = min(current_measure + segment_length_measures, total_measures + 1)

        # Extract elements in this measure range
        segment_stream = stream.Stream()

        for element in flat_stream.notesAndRests:
            # Get measure number for this element
            element_measure = element.measureNumber if hasattr(element, 'measureNumber') else None

            if element_measure is None:
                # Estimate based on offset
                numerator = int(time_signature.split('/')[0])
                quarters_per_measure = numerator
                element_measure = int(element.offset / quarters_per_measure) + 1

            if current_measure <= element_measure < end_measure:
                segment_stream.append(element)

        if len(segment_stream.notesAndRests) > 0:
            segments.append((segment_stream, current_measure, end_measure - 1))

        current_measure = end_measure

    return segments


def label_sections(segment_similarities: List[Tuple[int, int, float]]) -> Dict[int, str]:
    """
    Assign section labels (A, B, C, etc.) based on segment similarities.

    Args:
        segment_similarities: List of (seg1_idx, seg2_idx, similarity) tuples

    Returns:
        Dictionary mapping segment index to label (e.g., {0: 'A', 1: 'B', 2: 'A'})
    """
    # Build similarity matrix
    num_segments = max(max(s[0], s[1]) for s in segment_similarities) + 1 if segment_similarities else 0

    if num_segments == 0:
        return []

    # Group similar segments together
    segment_groups = []  # List of sets, each set contains similar segment indices
    segment_labels = {}  # Map segment index to label

    for seg_idx in range(num_segments):
        # Check if this segment is similar to any existing group
        assigned = False

        for group in segment_groups:
            # Check similarity with any member of the group
            for group_member in group:
                # Find similarity between seg_idx and group_member
                similarity = 0.0
                for s1, s2, sim in segment_similarities:
                    if (s1 == seg_idx and s2 == group_member) or (s1 == group_member and s2 == seg_idx):
                        similarity = sim
                        break

                if similarity >= MIN_SEGMENT_SIMILARITY:
                    group.add(seg_idx)
                    assigned = True
                    break

            if assigned:
                break

        if not assigned:
            # Create new group
            segment_groups.append({seg_idx})

    # Assign labels to groups
    for label_idx, group in enumerate(segment_groups):
        if label_idx < len(SECTION_LABELS):
            label = SECTION_LABELS[label_idx]
        else:
            # Use numeric labels if we run out of letters
            label = f"Section{label_idx + 1}"

        for seg_idx in group:
            segment_labels[seg_idx] = label

    return segment_labels


def identify_common_forms(section_sequence: List[str]) -> str:
    """
    Identify common musical forms (A-B-A, verse-chorus, etc.).

    Args:
        section_sequence: List of section labels in order

    Returns:
        String describing the detected form
    """
    seq_str = ''.join(section_sequence)

    # Common patterns
    if seq_str.startswith('A') and seq_str.endswith('A') and 'B' in seq_str:
        # A-B-A form or variations
        if seq_str == 'ABA':
            return "A-B-A (Ternary Form)"
        elif seq_str.count('A') >= 3 and seq_str.count('B') >= 1:
            return "A-B-A variant (Rounded Binary)"
        else:
            return "Through-composed with recurring A section"

    elif len(set(section_sequence)) == 2:
        # Two distinct sections - likely verse-chorus
        labels = list(set(section_sequence))
        if section_sequence.count(labels[0]) > 1 and section_sequence.count(labels[1]) > 1:
            return f"Verse-Chorus form ({labels[0]}-{labels[1]} alternating)"

    elif len(set(section_sequence)) == 1:
        return "Single section (Strophic or through-composed)"

    elif len(set(section_sequence)) >= 3:
        return "Multi-section form (A-B-C...)"

    return "Custom form"


def analyze_midi_structure(file_path: Path):
    """
    Analyze MIDI file for structural sections.

    Args:
        file_path: Path to MIDI file

    Returns:
        Tuple of (data_dict, duration_seconds)

    Raises:
        AnalysisError: If analysis fails
    """
    try:
        # Load MIDI file
        score, tempo_bpm, time_signature = load_midi(file_path)

        # Segment by measures
        segments = segment_by_measures(score, SEGMENT_LENGTH_MEASURES, time_signature)

        if len(segments) == 0:
            raise AnalysisError(
                ANALYSIS_FAILED,
                "Could not segment MIDI file",
                "The file may not contain enough musical content"
            )

        # Extract features for each segment
        segment_features = []
        for segment_stream, start_measure, end_measure in segments:
            features = extract_segment_features(segment_stream)
            segment_features.append((features, start_measure, end_measure))

        # Calculate pairwise similarities
        similarities = []
        for i in range(len(segment_features)):
            for j in range(i + 1, len(segment_features)):
                similarity = calculate_segment_similarity(
                    segment_features[i][0],
                    segment_features[j][0]
                )
                similarities.append((i, j, similarity))

        # Label sections based on similarities
        segment_labels = label_sections(similarities)

        # Build section list with time boundaries
        sections = []
        section_sequence = []

        # Convert measures to time
        numerator = int(time_signature.split('/')[0])
        quarters_per_measure = numerator
        seconds_per_quarter = 60.0 / tempo_bpm

        for idx, (features, start_measure, end_measure) in enumerate(segment_features):
            label = segment_labels.get(idx, 'A')
            section_sequence.append(label)

            # Convert measures to seconds
            start_time = (start_measure - 1) * quarters_per_measure * seconds_per_quarter
            end_time = end_measure * quarters_per_measure * seconds_per_quarter

            sections.append({
                'label': label,
                'start_measure': start_measure,
                'end_measure': end_measure,
                'start_time_seconds': round(start_time, 2),
                'end_time_seconds': round(end_time, 2)
            })

        # Identify overall form
        detected_form = identify_common_forms(section_sequence)

        # Calculate duration
        if segments:
            last_segment = segments[-1]
            last_measure = last_segment[2]
            duration_seconds = last_measure * quarters_per_measure * seconds_per_quarter
        else:
            duration_seconds = 0.0

        # Build result
        data = {
            'sections': sections,
            'num_sections': len(sections),
            'detected_form': detected_form,
            'section_sequence': section_sequence
        }

        return data, duration_seconds

    except AnalysisError:
        raise
    except Exception as e:
        raise AnalysisError(
            ANALYSIS_FAILED,
            f"MIDI structure analysis failed: {str(e)}",
            str(e)
        )


def main():
    """Main entry point for MIDI structure analysis script."""
    parser = argparse.ArgumentParser(
        description="Identify structural sections and form in MIDI files"
    )
    parser.add_argument(
        "file_path",
        help="Path to MIDI file (.mid, .midi)"
    )

    args = parser.parse_args()

    try:
        # Validate MIDI file
        file_path, file_size, extension = validate_midi_file(args.file_path)

        # Analyze MIDI structure
        data, duration_seconds = analyze_midi_structure(file_path)

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
