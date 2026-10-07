"""
Integration tests for MIDI analysis scripts.

Tests all 6 MIDI scripts with programmatically generated test fixtures.
Tests happy paths, multi-track handling, error paths, and JSON output validation.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

# Try to import MIDI generation libraries
try:
    import mido
    from mido import Message, MidiFile, MidiTrack, MetaMessage
    HAS_MIDO = True
except ImportError:
    HAS_MIDO = False

try:
    from music21 import converter
    HAS_MUSIC21 = True
except ImportError:
    HAS_MUSIC21 = False


# ============================================================================
# Test Fixtures - MIDI File Generation
# ============================================================================

@pytest.fixture(scope="session")
def scripts_dir():
    """Return path to scripts/midi directory."""
    return Path(__file__).parent.parent / "scripts" / "midi"


@pytest.fixture(scope="session")
def test_midi_dir(tmp_path_factory):
    """Create directory for test MIDI files."""
    return tmp_path_factory.mktemp("test_midi")


@pytest.fixture(scope="session")
def simple_midi_cmajor(test_midi_dir):
    """Generate a simple MIDI file with C major scale at 120 BPM in 4/4 time."""
    if not HAS_MIDO:
        pytest.skip("mido required for MIDI generation")

    file_path = test_midi_dir / "simple_cmajor.mid"

    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)

    # Set tempo to 120 BPM (500000 microseconds per beat)
    track.append(MetaMessage('set_tempo', tempo=500000))

    # Set time signature to 4/4
    track.append(MetaMessage('time_signature', numerator=4, denominator=4))

    # Add C major scale: C4 to C5
    # MIDI pitches: C4=60, D4=62, E4=64, F4=65, G4=67, A4=69, B4=71, C5=72
    scale_notes = [60, 62, 64, 65, 67, 69, 71, 72]

    for pitch in scale_notes:
        # Note on with velocity 64 (medium volume)
        track.append(Message('note_on', note=pitch, velocity=64, time=0))
        # Note off after 480 ticks (one quarter note at 480 ticks per beat)
        track.append(Message('note_off', note=pitch, velocity=64, time=480))

    # End of track
    track.append(MetaMessage('end_of_track', time=0))

    mid.save(str(file_path))
    return file_path


@pytest.fixture(scope="session")
def multitrack_midi(test_midi_dir):
    """Generate a multi-track MIDI file with melody, bass, and chords."""
    if not HAS_MIDO:
        pytest.skip("mido required for MIDI generation")

    file_path = test_midi_dir / "multitrack.mid"

    mid = MidiFile()

    # Track 0: Tempo and time signature
    track0 = MidiTrack()
    mid.tracks.append(track0)
    track0.append(MetaMessage('set_tempo', tempo=500000))  # 120 BPM
    track0.append(MetaMessage('time_signature', numerator=4, denominator=4))
    track0.append(MetaMessage('end_of_track', time=0))

    # Track 1: Melody (C major scale)
    track1 = MidiTrack()
    mid.tracks.append(track1)
    track1.append(MetaMessage('track_name', name='Melody'))
    track1.append(Message('program_change', program=0, time=0))  # Piano

    melody_notes = [60, 62, 64, 65, 67, 69, 71, 72]  # C major scale
    for pitch in melody_notes:
        track1.append(Message('note_on', note=pitch, velocity=64, time=0))
        track1.append(Message('note_off', note=pitch, velocity=64, time=480))

    track1.append(MetaMessage('end_of_track', time=0))

    # Track 2: Bass (C major chord tones)
    track2 = MidiTrack()
    mid.tracks.append(track2)
    track2.append(MetaMessage('track_name', name='Bass'))
    track2.append(Message('program_change', program=32, time=0))  # Acoustic bass

    bass_notes = [48, 52, 55, 48]  # C3, E3, G3, C3 (chord tones)
    for pitch in bass_notes:
        track2.append(Message('note_on', note=pitch, velocity=64, time=0))
        track2.append(Message('note_off', note=pitch, velocity=64, time=960))  # Half notes

    track2.append(MetaMessage('end_of_track', time=0))

    # Track 3: Chords (C major chord)
    track3 = MidiTrack()
    mid.tracks.append(track3)
    track3.append(MetaMessage('track_name', name='Chords'))
    track3.append(Message('program_change', program=0, time=0))  # Piano

    # C major chord: C4, E4, G4 played together
    chord_pitches = [60, 64, 67]

    # Play chord for 4 beats
    for pitch in chord_pitches:
        track3.append(Message('note_on', note=pitch, velocity=64, time=0))

    # Release all notes after 4 beats (1920 ticks)
    for i, pitch in enumerate(chord_pitches):
        time_delta = 1920 if i == 0 else 0
        track3.append(Message('note_off', note=pitch, velocity=64, time=time_delta))

    track3.append(MetaMessage('end_of_track', time=0))

    mid.save(str(file_path))
    return file_path


@pytest.fixture(scope="session")
def rhythmic_midi(test_midi_dir):
    """Generate a MIDI file with clear rhythmic patterns."""
    if not HAS_MIDO:
        pytest.skip("mido required for MIDI generation")

    file_path = test_midi_dir / "rhythmic.mid"

    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)

    track.append(MetaMessage('set_tempo', tempo=500000))  # 120 BPM
    track.append(MetaMessage('time_signature', numerator=4, denominator=4))

    # Create a rhythmic pattern: quarter, quarter, eighth, eighth, quarter
    # Using same pitch (C4=60) to emphasize rhythm
    pitch = 60

    # Pattern repeated 4 times
    for _ in range(4):
        # Quarter note
        track.append(Message('note_on', note=pitch, velocity=64, time=0))
        track.append(Message('note_off', note=pitch, velocity=64, time=480))

        # Quarter note
        track.append(Message('note_on', note=pitch, velocity=64, time=0))
        track.append(Message('note_off', note=pitch, velocity=64, time=480))

        # Eighth note
        track.append(Message('note_on', note=pitch, velocity=64, time=0))
        track.append(Message('note_off', note=pitch, velocity=64, time=240))

        # Eighth note
        track.append(Message('note_on', note=pitch, velocity=64, time=0))
        track.append(Message('note_off', note=pitch, velocity=64, time=240))

        # Quarter note
        track.append(Message('note_on', note=pitch, velocity=64, time=0))
        track.append(Message('note_off', note=pitch, velocity=64, time=480))

    track.append(MetaMessage('end_of_track', time=0))

    mid.save(str(file_path))
    return file_path


@pytest.fixture(scope="session")
def melodic_pattern_midi(test_midi_dir):
    """Generate a MIDI file with repeated melodic motifs."""
    if not HAS_MIDO:
        pytest.skip("mido required for MIDI generation")

    file_path = test_midi_dir / "melodic_pattern.mid"

    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)

    track.append(MetaMessage('set_tempo', tempo=500000))  # 120 BPM
    track.append(MetaMessage('time_signature', numerator=4, denominator=4))

    # Create a clear melodic motif: C-D-E (60-62-64)
    # Repeat it 3 times to ensure it's detected
    motif = [60, 62, 64]

    for _ in range(3):
        for pitch in motif:
            track.append(Message('note_on', note=pitch, velocity=64, time=0))
            track.append(Message('note_off', note=pitch, velocity=64, time=480))

        # Add a different note between repetitions
        track.append(Message('note_on', note=67, velocity=64, time=0))  # G
        track.append(Message('note_off', note=67, velocity=64, time=480))

    track.append(MetaMessage('end_of_track', time=0))

    mid.save(str(file_path))
    return file_path


@pytest.fixture(scope="session")
def structured_midi_aba(test_midi_dir):
    """Generate a MIDI file with clear A-B-A structure."""
    if not HAS_MIDO:
        pytest.skip("mido required for MIDI generation")

    file_path = test_midi_dir / "structured_aba.mid"

    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)

    track.append(MetaMessage('set_tempo', tempo=500000))  # 120 BPM
    track.append(MetaMessage('time_signature', numerator=4, denominator=4))

    # Section A: C major arpeggio (C-E-G)
    section_a = [60, 64, 67, 72]  # C4-E4-G4-C5

    # Play section A (4 measures)
    for _ in range(4):
        for pitch in section_a:
            track.append(Message('note_on', note=pitch, velocity=64, time=0))
            track.append(Message('note_off', note=pitch, velocity=64, time=480))

    # Section B: F major arpeggio (F-A-C)
    section_b = [65, 69, 72, 77]  # F4-A4-C5-F5

    # Play section B (4 measures)
    for _ in range(4):
        for pitch in section_b:
            track.append(Message('note_on', note=pitch, velocity=64, time=0))
            track.append(Message('note_off', note=pitch, velocity=64, time=480))

    # Section A again (4 measures)
    for _ in range(4):
        for pitch in section_a:
            track.append(Message('note_on', note=pitch, velocity=64, time=0))
            track.append(Message('note_off', note=pitch, velocity=64, time=480))

    track.append(MetaMessage('end_of_track', time=0))

    mid.save(str(file_path))
    return file_path


@pytest.fixture(scope="session")
def chord_progression_midi(test_midi_dir):
    """Generate a MIDI file with a clear chord progression (I-IV-V-I in C major)."""
    if not HAS_MIDO:
        pytest.skip("mido required for MIDI generation")

    file_path = test_midi_dir / "chord_progression.mid"

    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)

    track.append(MetaMessage('set_tempo', tempo=500000))  # 120 BPM
    track.append(MetaMessage('time_signature', numerator=4, denominator=4))

    # I-IV-V-I progression in C major
    # I (C major): C-E-G (60-64-67)
    # IV (F major): F-A-C (65-69-72)
    # V (G major): G-B-D (67-71-74)
    # I (C major): C-E-G (60-64-67)

    chords = [
        [60, 64, 67],  # C major (I)
        [65, 69, 72],  # F major (IV)
        [67, 71, 74],  # G major (V)
        [60, 64, 67],  # C major (I)
    ]

    for chord_pitches in chords:
        # Play all notes of chord simultaneously
        for pitch in chord_pitches:
            track.append(Message('note_on', note=pitch, velocity=64, time=0))

        # Hold for 4 beats (whole note)
        # Release first note after 1920 ticks, others immediately after
        for i, pitch in enumerate(chord_pitches):
            time_delta = 1920 if i == 0 else 0
            track.append(Message('note_off', note=pitch, velocity=64, time=time_delta))

    track.append(MetaMessage('end_of_track', time=0))

    mid.save(str(file_path))
    return file_path


@pytest.fixture(scope="session")
def corrupt_midi(test_midi_dir):
    """Create a corrupted MIDI file (invalid header)."""
    file_path = test_midi_dir / "corrupt.mid"
    # Write garbage data that's not a valid MIDI file
    file_path.write_bytes(b"This is not a valid MIDI file" * 100)
    return file_path


@pytest.fixture(scope="session")
def empty_midi(test_midi_dir):
    """Create an empty MIDI file (no notes)."""
    if not HAS_MIDO:
        pytest.skip("mido required for MIDI generation")

    file_path = test_midi_dir / "empty.mid"

    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)

    track.append(MetaMessage('set_tempo', tempo=500000))
    track.append(MetaMessage('time_signature', numerator=4, denominator=4))
    track.append(MetaMessage('end_of_track', time=0))

    mid.save(str(file_path))
    return file_path


# ============================================================================
# Helper Functions
# ============================================================================

def check_music21_available():
    """Check if music21 is installed."""
    try:
        import music21
        return True
    except ImportError:
        return False


def run_midi_script(scripts_dir, script_name, *args, timeout=30):
    """
    Run a MIDI analysis script and return parsed JSON output.

    Args:
        scripts_dir: Path to scripts/midi directory
        script_name: Name of script (e.g., "analyze_midi_key.py")
        *args: Command-line arguments to pass to script
        timeout: Maximum execution time in seconds

    Returns:
        tuple: (json_output, returncode, stdout, stderr)
    """
    script_path = scripts_dir / script_name

    result = subprocess.run(
        [sys.executable, str(script_path)] + [str(arg) for arg in args],
        capture_output=True,
        text=True,
        timeout=timeout
    )

    # Try to parse JSON output from stdout OR stderr
    json_output = None

    # First try stdout (for success cases)
    if result.stdout.strip():
        try:
            json_output = json.loads(result.stdout)
        except json.JSONDecodeError:
            pass

    # If no JSON in stdout, try stderr (error cases)
    if json_output is None and result.stderr.strip():
        # Look for JSON in stderr
        for line in result.stderr.split('\n'):
            if line.strip().startswith('{'):
                try:
                    json_output = json.loads(line)
                    break
                except json.JSONDecodeError:
                    pass

    return json_output, result.returncode, result.stdout, result.stderr


def assert_valid_success_json(output, analysis_type):
    """Assert that JSON output has valid success structure."""
    assert output is not None, "JSON output should not be None"
    assert output.get("status") == "success", f"Status should be 'success', got {output.get('status')}"
    assert output.get("analysis_type") == analysis_type
    assert "file" in output
    assert "duration_seconds" in output
    assert "truncated" in output
    assert "data" in output
    assert isinstance(output["data"], dict)
    assert "warnings" in output


def assert_valid_error_json(output, expected_error_code=None):
    """Assert that JSON output has valid error structure."""
    assert output is not None, "JSON output should not be None"
    assert output.get("status") == "error", f"Status should be 'error', got {output.get('status')}"
    assert "error" in output
    assert "code" in output["error"]
    assert "message" in output["error"]

    if expected_error_code:
        assert output["error"]["code"] == expected_error_code


# ============================================================================
# Tests for analyze_midi_key.py
# ============================================================================

@pytest.mark.skipif(not check_music21_available(), reason="music21 required")
class TestAnalyzeMidiKey:
    """Integration tests for analyze_midi_key.py script."""

    def test_key_valid_midi(self, scripts_dir, simple_midi_cmajor):
        """Test key analysis with valid MIDI file."""
        output, returncode, stdout, stderr = run_midi_script(
            scripts_dir, "analyze_midi_key.py", simple_midi_cmajor
        )

        assert returncode == 0, f"Script failed: {stderr}"
        assert_valid_success_json(output, "midi_key")

        # Check data fields
        data = output["data"]
        assert "key" in data
        assert "mode" in data
        assert "confidence" in data
        assert "modulations" in data

        # Key should be one of the 12 pitches
        assert data["key"] in ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        assert data["mode"] in ['major', 'minor']
        assert 0.0 <= data["confidence"] <= 1.0
        assert isinstance(data["modulations"], list)

    def test_key_multitrack_midi(self, scripts_dir, multitrack_midi):
        """Test key analysis with multi-track MIDI file."""
        output, returncode, stdout, stderr = run_midi_script(
            scripts_dir, "analyze_midi_key.py", multitrack_midi
        )

        assert returncode == 0, f"Script failed: {stderr}"
        assert_valid_success_json(output, "midi_key")

        # Should detect C major
        data = output["data"]
        assert data["key"] == "C"
        assert data["mode"] == "major"

    def test_key_missing_file(self, scripts_dir, test_midi_dir):
        """Test key analysis with non-existent file."""
        missing_file = test_midi_dir / "does_not_exist.mid"
        output, returncode, stdout, stderr = run_midi_script(
            scripts_dir, "analyze_midi_key.py", missing_file
        )

        assert returncode != 0, "Should fail with non-zero exit code"
        assert_valid_error_json(output, "FILE_NOT_FOUND")

    def test_key_corrupt_file(self, scripts_dir, corrupt_midi):
        """Test key analysis with corrupted MIDI file."""
        output, returncode, stdout, stderr = run_midi_script(
            scripts_dir, "analyze_midi_key.py", corrupt_midi
        )

        assert returncode != 0, "Should fail with non-zero exit code"
        assert_valid_error_json(output)
        # Could be CORRUPT_FILE or ANALYSIS_FAILED
        assert output["error"]["code"] in ["CORRUPT_FILE", "ANALYSIS_FAILED"]

    def test_key_empty_midi(self, scripts_dir, empty_midi):
        """Test key analysis with empty MIDI file (no notes)."""
        output, returncode, stdout, stderr = run_midi_script(
            scripts_dir, "analyze_midi_key.py", empty_midi
        )

        assert returncode != 0, "Should fail with non-zero exit code"
        assert_valid_error_json(output, "ANALYSIS_FAILED")


# ============================================================================
# Tests for analyze_midi_chords.py
# ============================================================================

@pytest.mark.skipif(not check_music21_available(), reason="music21 required")
class TestAnalyzeMidiChords:
    """Integration tests for analyze_midi_chords.py script."""

    def test_chords_valid_midi(self, scripts_dir, chord_progression_midi):
        """Test chord analysis with valid MIDI file."""
        output, returncode, stdout, stderr = run_midi_script(
            scripts_dir, "analyze_midi_chords.py", chord_progression_midi
        )

        assert returncode == 0, f"Script failed: {stderr}"
        assert_valid_success_json(output, "midi_chords")

        # Check data fields
        data = output["data"]
        assert "key_context" in data
        assert "chord_progression" in data
        assert isinstance(data["chord_progression"], list)

        # Each chord should have required fields
        for chord in data["chord_progression"]:
            assert "time" in chord
            assert "chord" in chord
            assert "roman" in chord
            assert "duration" in chord
            assert isinstance(chord["time"], (int, float))
            assert isinstance(chord["duration"], (int, float))

    def test_chords_multitrack_midi(self, scripts_dir, multitrack_midi):
        """Test chord analysis with multi-track MIDI file."""
        output, returncode, stdout, stderr = run_midi_script(
            scripts_dir, "analyze_midi_chords.py", multitrack_midi
        )

        assert returncode == 0, f"Script failed: {stderr}"
        assert_valid_success_json(output, "midi_chords")

        # Should detect chords from multiple tracks
        data = output["data"]
        assert len(data["chord_progression"]) > 0

    def test_chords_missing_file(self, scripts_dir, test_midi_dir):
        """Test chord analysis with non-existent file."""
        missing_file = test_midi_dir / "does_not_exist.mid"
        output, returncode, stdout, stderr = run_midi_script(
            scripts_dir, "analyze_midi_chords.py", missing_file
        )

        assert returncode != 0, "Should fail with non-zero exit code"
        assert_valid_error_json(output, "FILE_NOT_FOUND")

    def test_chords_corrupt_file(self, scripts_dir, corrupt_midi):
        """Test chord analysis with corrupted MIDI file."""
        output, returncode, stdout, stderr = run_midi_script(
            scripts_dir, "analyze_midi_chords.py", corrupt_midi
        )

        assert returncode != 0, "Should fail with non-zero exit code"
        assert_valid_error_json(output)
        assert output["error"]["code"] in ["CORRUPT_FILE", "ANALYSIS_FAILED"]


# ============================================================================
# Tests for analyze_midi_melody.py
# ============================================================================

@pytest.mark.skipif(not check_music21_available(), reason="music21 required")
class TestAnalyzeMidiMelody:
    """Integration tests for analyze_midi_melody.py script."""

    def test_melody_valid_midi(self, scripts_dir, melodic_pattern_midi):
        """Test melody analysis with valid MIDI file containing patterns."""
        output, returncode, stdout, stderr = run_midi_script(
            scripts_dir, "analyze_midi_melody.py", melodic_pattern_midi
        )

        assert returncode == 0, f"Script failed: {stderr}"
        assert_valid_success_json(output, "midi_melody")

        # Check data fields
        data = output["data"]
        assert "melodic_motifs" in data
        assert "total_notes" in data
        assert "unique_motifs_found" in data
        assert isinstance(data["melodic_motifs"], list)
        assert isinstance(data["total_notes"], int)
        assert isinstance(data["unique_motifs_found"], int)

        # Each motif should have required fields
        for motif in data["melodic_motifs"]:
            assert "pattern" in motif
            assert "length" in motif
            assert "occurrences" in motif
            assert "positions_seconds" in motif
            assert isinstance(motif["pattern"], list)
            assert isinstance(motif["length"], int)
            assert isinstance(motif["occurrences"], int)
            assert isinstance(motif["positions_seconds"], list)

    def test_melody_multitrack_midi(self, scripts_dir, multitrack_midi):
        """Test melody analysis with multi-track MIDI file."""
        output, returncode, stdout, stderr = run_midi_script(
            scripts_dir, "analyze_midi_melody.py", multitrack_midi
        )

        assert returncode == 0, f"Script failed: {stderr}"
        assert_valid_success_json(output, "midi_melody")

    def test_melody_missing_file(self, scripts_dir, test_midi_dir):
        """Test melody analysis with non-existent file."""
        missing_file = test_midi_dir / "does_not_exist.mid"
        output, returncode, stdout, stderr = run_midi_script(
            scripts_dir, "analyze_midi_melody.py", missing_file
        )

        assert returncode != 0, "Should fail with non-zero exit code"
        assert_valid_error_json(output, "FILE_NOT_FOUND")

    def test_melody_corrupt_file(self, scripts_dir, corrupt_midi):
        """Test melody analysis with corrupted MIDI file."""
        output, returncode, stdout, stderr = run_midi_script(
            scripts_dir, "analyze_midi_melody.py", corrupt_midi
        )

        assert returncode != 0, "Should fail with non-zero exit code"
        assert_valid_error_json(output)
        assert output["error"]["code"] in ["CORRUPT_FILE", "ANALYSIS_FAILED"]

    def test_melody_empty_midi(self, scripts_dir, empty_midi):
        """Test melody analysis with empty MIDI file (no notes)."""
        output, returncode, stdout, stderr = run_midi_script(
            scripts_dir, "analyze_midi_melody.py", empty_midi
        )

        assert returncode != 0, "Should fail with non-zero exit code"
        assert_valid_error_json(output, "ANALYSIS_FAILED")


# ============================================================================
# Tests for analyze_midi_rhythm.py
# ============================================================================

@pytest.mark.skipif(not check_music21_available(), reason="music21 required")
class TestAnalyzeMidiRhythm:
    """Integration tests for analyze_midi_rhythm.py script."""

    def test_rhythm_valid_midi(self, scripts_dir, rhythmic_midi):
        """Test rhythm analysis with valid MIDI file."""
        output, returncode, stdout, stderr = run_midi_script(
            scripts_dir, "analyze_midi_rhythm.py", rhythmic_midi
        )

        assert returncode == 0, f"Script failed: {stderr}"
        assert_valid_success_json(output, "midi_rhythm")

        # Check data fields
        data = output["data"]
        assert "time_signature" in data
        assert "tempo_bpm" in data
        assert "note_durations" in data
        assert "syncopation_score" in data

        # Validate time signature format
        assert "/" in data["time_signature"]

        # Validate tempo
        assert isinstance(data["tempo_bpm"], int)
        assert data["tempo_bpm"] > 0

        # Validate note durations
        assert isinstance(data["note_durations"], dict)
        expected_durations = ["whole", "half", "quarter", "eighth", "sixteenth"]
        for duration_type in expected_durations:
            assert duration_type in data["note_durations"]
            assert isinstance(data["note_durations"][duration_type], int)

        # Validate syncopation score
        assert 0.0 <= data["syncopation_score"] <= 1.0

    def test_rhythm_multitrack_midi(self, scripts_dir, multitrack_midi):
        """Test rhythm analysis with multi-track MIDI file."""
        output, returncode, stdout, stderr = run_midi_script(
            scripts_dir, "analyze_midi_rhythm.py", multitrack_midi
        )

        assert returncode == 0, f"Script failed: {stderr}"
        assert_valid_success_json(output, "midi_rhythm")

    def test_rhythm_missing_file(self, scripts_dir, test_midi_dir):
        """Test rhythm analysis with non-existent file."""
        missing_file = test_midi_dir / "does_not_exist.mid"
        output, returncode, stdout, stderr = run_midi_script(
            scripts_dir, "analyze_midi_rhythm.py", missing_file
        )

        assert returncode != 0, "Should fail with non-zero exit code"
        assert_valid_error_json(output, "FILE_NOT_FOUND")

    def test_rhythm_corrupt_file(self, scripts_dir, corrupt_midi):
        """Test rhythm analysis with corrupted MIDI file."""
        output, returncode, stdout, stderr = run_midi_script(
            scripts_dir, "analyze_midi_rhythm.py", corrupt_midi
        )

        assert returncode != 0, "Should fail with non-zero exit code"
        assert_valid_error_json(output)
        assert output["error"]["code"] in ["CORRUPT_FILE", "ANALYSIS_FAILED"]


# ============================================================================
# Tests for analyze_midi_structure.py
# ============================================================================

@pytest.mark.skipif(not check_music21_available(), reason="music21 required")
class TestAnalyzeMidiStructure:
    """Integration tests for analyze_midi_structure.py script."""

    def test_structure_valid_midi(self, scripts_dir, structured_midi_aba):
        """Test structure analysis with valid MIDI file with A-B-A form."""
        output, returncode, stdout, stderr = run_midi_script(
            scripts_dir, "analyze_midi_structure.py", structured_midi_aba
        )

        assert returncode == 0, f"Script failed: {stderr}"
        assert_valid_success_json(output, "midi_structure")

        # Check data fields
        data = output["data"]
        assert "sections" in data
        assert "num_sections" in data
        assert "detected_form" in data
        assert "section_sequence" in data

        assert isinstance(data["sections"], list)
        assert isinstance(data["num_sections"], int)
        assert isinstance(data["detected_form"], str)
        assert isinstance(data["section_sequence"], list)

        assert [(section["start_measure"], section["end_measure"])
                for section in data["sections"]] == [(1, 4), (5, 8), (9, 12)]
        assert output["duration_seconds"] == pytest.approx(24.0)

        # Each section should have required fields
        for section in data["sections"]:
            assert "label" in section
            assert "start_measure" in section
            assert "end_measure" in section
            assert "start_time_seconds" in section
            assert "end_time_seconds" in section

    def test_structure_multitrack_midi(self, scripts_dir, multitrack_midi):
        """Test structure analysis with multi-track MIDI file."""
        output, returncode, stdout, stderr = run_midi_script(
            scripts_dir, "analyze_midi_structure.py", multitrack_midi
        )

        assert returncode == 0, f"Script failed: {stderr}"
        assert_valid_success_json(output, "midi_structure")

        sections = output["data"]["sections"]
        assert [(section["start_measure"], section["end_measure"])
                for section in sections] == [(1, 2)]
        assert output["duration_seconds"] == pytest.approx(4.0)

    def test_structure_missing_file(self, scripts_dir, test_midi_dir):
        """Test structure analysis with non-existent file."""
        missing_file = test_midi_dir / "does_not_exist.mid"
        output, returncode, stdout, stderr = run_midi_script(
            scripts_dir, "analyze_midi_structure.py", missing_file
        )

        assert returncode != 0, "Should fail with non-zero exit code"
        assert_valid_error_json(output, "FILE_NOT_FOUND")

    def test_structure_corrupt_file(self, scripts_dir, corrupt_midi):
        """Test structure analysis with corrupted MIDI file."""
        output, returncode, stdout, stderr = run_midi_script(
            scripts_dir, "analyze_midi_structure.py", corrupt_midi
        )

        assert returncode != 0, "Should fail with non-zero exit code"
        assert_valid_error_json(output)
        assert output["error"]["code"] in ["CORRUPT_FILE", "ANALYSIS_FAILED"]

    def test_structure_empty_midi(self, scripts_dir, empty_midi):
        """Test structure analysis with empty MIDI file (no notes)."""
        output, returncode, stdout, stderr = run_midi_script(
            scripts_dir, "analyze_midi_structure.py", empty_midi
        )

        assert returncode != 0, "Should fail with non-zero exit code"
        assert_valid_error_json(output, "ANALYSIS_FAILED")


# ============================================================================
# Tests for analyze_midi_metrics.py
# ============================================================================

@pytest.mark.skipif(not check_music21_available(), reason="music21 required")
class TestAnalyzeMidiMetrics:
    """Integration tests for analyze_midi_metrics.py script."""

    def test_metrics_valid_midi(self, scripts_dir, simple_midi_cmajor):
        """Test metrics analysis with valid MIDI file."""
        output, returncode, stdout, stderr = run_midi_script(
            scripts_dir, "analyze_midi_metrics.py", simple_midi_cmajor
        )

        assert returncode == 0, f"Script failed: {stderr}"
        assert_valid_success_json(output, "midi_metrics")

        # Check data fields
        data = output["data"]
        assert "note_count" in data
        assert "track_count" in data
        assert "voice_leading" in data
        assert "note_density_per_second" in data
        assert "pitch_range" in data

        # Validate note count
        assert isinstance(data["note_count"], int)
        assert data["note_count"] > 0

        # Validate track count
        assert isinstance(data["track_count"], int)
        assert data["track_count"] > 0

        # Validate voice leading
        vl = data["voice_leading"]
        assert "stepwise_motion_pct" in vl
        assert "leap_motion_pct" in vl
        assert "average_interval" in vl
        assert 0.0 <= vl["stepwise_motion_pct"] <= 1.0
        assert 0.0 <= vl["leap_motion_pct"] <= 1.0

        # Validate note density
        assert isinstance(data["note_density_per_second"], (int, float))
        assert data["note_density_per_second"] >= 0

        # Validate pitch range
        pr = data["pitch_range"]
        assert "lowest" in pr
        assert "highest" in pr

    def test_metrics_multitrack_midi(self, scripts_dir, multitrack_midi):
        """Test metrics analysis with multi-track MIDI file."""
        output, returncode, stdout, stderr = run_midi_script(
            scripts_dir, "analyze_midi_metrics.py", multitrack_midi
        )

        assert returncode == 0, f"Script failed: {stderr}"
        assert_valid_success_json(output, "midi_metrics")

        # Should detect multiple tracks
        data = output["data"]
        assert data["track_count"] > 1

    def test_metrics_missing_file(self, scripts_dir, test_midi_dir):
        """Test metrics analysis with non-existent file."""
        missing_file = test_midi_dir / "does_not_exist.mid"
        output, returncode, stdout, stderr = run_midi_script(
            scripts_dir, "analyze_midi_metrics.py", missing_file
        )

        assert returncode != 0, "Should fail with non-zero exit code"
        assert_valid_error_json(output, "FILE_NOT_FOUND")

    def test_metrics_corrupt_file(self, scripts_dir, corrupt_midi):
        """Test metrics analysis with corrupted MIDI file."""
        output, returncode, stdout, stderr = run_midi_script(
            scripts_dir, "analyze_midi_metrics.py", corrupt_midi
        )

        assert returncode != 0, "Should fail with non-zero exit code"
        assert_valid_error_json(output)
        assert output["error"]["code"] in ["CORRUPT_FILE", "ANALYSIS_FAILED"]

    def test_metrics_empty_midi(self, scripts_dir, empty_midi):
        """Test metrics analysis with empty MIDI file (no notes)."""
        output, returncode, stdout, stderr = run_midi_script(
            scripts_dir, "analyze_midi_metrics.py", empty_midi
        )

        assert returncode != 0, "Should fail with non-zero exit code"
        assert_valid_error_json(output, "ANALYSIS_FAILED")


# ============================================================================
# Multi-Track Handling Tests
# ============================================================================

@pytest.mark.skipif(not check_music21_available(), reason="music21 required")
class TestMultiTrackHandling:
    """Test all scripts properly handle multi-track MIDI files."""

    @pytest.mark.parametrize("script_name,analysis_type", [
        ("analyze_midi_key.py", "midi_key"),
        ("analyze_midi_chords.py", "midi_chords"),
        ("analyze_midi_melody.py", "midi_melody"),
        ("analyze_midi_rhythm.py", "midi_rhythm"),
        ("analyze_midi_structure.py", "midi_structure"),
        ("analyze_midi_metrics.py", "midi_metrics"),
    ])
    def test_multitrack_support(self, scripts_dir, multitrack_midi, script_name, analysis_type):
        """Test that script properly handles multi-track MIDI files."""
        output, returncode, stdout, stderr = run_midi_script(
            scripts_dir, script_name, multitrack_midi
        )

        assert returncode == 0, f"{script_name} failed with multi-track MIDI: {stderr}"
        assert_valid_success_json(output, analysis_type)


# ============================================================================
# Error Handling Tests
# ============================================================================

@pytest.mark.skipif(not check_music21_available(), reason="music21 required")
class TestErrorHandling:
    """Test error handling across all MIDI scripts."""

    @pytest.mark.parametrize("script_name", [
        "analyze_midi_key.py",
        "analyze_midi_chords.py",
        "analyze_midi_melody.py",
        "analyze_midi_rhythm.py",
        "analyze_midi_structure.py",
        "analyze_midi_metrics.py",
    ])
    def test_missing_file_handling(self, scripts_dir, test_midi_dir, script_name):
        """Test that scripts handle missing files correctly."""
        missing_file = test_midi_dir / "does_not_exist.mid"
        output, returncode, stdout, stderr = run_midi_script(
            scripts_dir, script_name, missing_file
        )

        assert returncode != 0, f"{script_name} should fail with missing file"
        assert_valid_error_json(output, "FILE_NOT_FOUND")

    @pytest.mark.parametrize("script_name", [
        "analyze_midi_key.py",
        "analyze_midi_chords.py",
        "analyze_midi_melody.py",
        "analyze_midi_rhythm.py",
        "analyze_midi_structure.py",
        "analyze_midi_metrics.py",
    ])
    def test_corrupt_file_handling(self, scripts_dir, corrupt_midi, script_name):
        """Test that scripts handle corrupt files gracefully."""
        output, returncode, stdout, stderr = run_midi_script(
            scripts_dir, script_name, corrupt_midi
        )

        assert returncode != 0, f"{script_name} should fail on corrupt file"
        assert output is not None, "Should return JSON even on error"
        assert output.get("status") == "error"
        assert output["error"]["code"] in ["CORRUPT_FILE", "ANALYSIS_FAILED"]

    @pytest.mark.parametrize("script_name", [
        "analyze_midi_key.py",
        "analyze_midi_chords.py",
        "analyze_midi_melody.py",
        "analyze_midi_rhythm.py",
        "analyze_midi_structure.py",
        "analyze_midi_metrics.py",
    ])
    def test_unsupported_format(self, scripts_dir, test_midi_dir, script_name):
        """Test that scripts reject unsupported file formats."""
        unsupported_file = test_midi_dir / "test.txt"
        unsupported_file.write_text("This is not a MIDI file")

        output, returncode, stdout, stderr = run_midi_script(
            scripts_dir, script_name, unsupported_file
        )

        assert returncode != 0, f"{script_name} should reject unsupported format"
        assert_valid_error_json(output, "UNSUPPORTED_FORMAT")


# ============================================================================
# JSON Output Validation Tests
# ============================================================================

@pytest.mark.skipif(not check_music21_available(), reason="music21 required")
class TestJSONOutputValidation:
    """Test that all scripts produce valid, parseable JSON output."""

    @pytest.mark.parametrize("script_name,analysis_type", [
        ("analyze_midi_key.py", "midi_key"),
        ("analyze_midi_chords.py", "midi_chords"),
        ("analyze_midi_melody.py", "midi_melody"),
        ("analyze_midi_rhythm.py", "midi_rhythm"),
        ("analyze_midi_structure.py", "midi_structure"),
        ("analyze_midi_metrics.py", "midi_metrics"),
    ])
    def test_json_is_valid_and_parseable(self, scripts_dir, simple_midi_cmajor, script_name, analysis_type):
        """Test that script output is valid JSON that can be parsed."""
        output, returncode, stdout, stderr = run_midi_script(
            scripts_dir, script_name, simple_midi_cmajor
        )

        assert returncode == 0, f"{script_name} failed: {stderr}"

        # Verify we got JSON output
        assert output is not None, f"{script_name} did not return JSON"

        # Verify JSON can be re-serialized (proves it's valid)
        try:
            json_str = json.dumps(output)
            reparsed = json.loads(json_str)
            assert reparsed == output
        except Exception as e:
            pytest.fail(f"{script_name} output is not valid JSON: {e}")

        # Verify structure
        assert_valid_success_json(output, analysis_type)

    @pytest.mark.parametrize("script_name", [
        "analyze_midi_key.py",
        "analyze_midi_chords.py",
        "analyze_midi_melody.py",
        "analyze_midi_rhythm.py",
        "analyze_midi_structure.py",
        "analyze_midi_metrics.py",
    ])
    def test_error_json_is_valid_and_parseable(self, scripts_dir, corrupt_midi, script_name):
        """Test that error output is valid JSON that can be parsed."""
        output, returncode, stdout, stderr = run_midi_script(
            scripts_dir, script_name, corrupt_midi
        )

        assert returncode != 0, f"{script_name} should fail on corrupt file"

        # Verify we got JSON output even on error
        assert output is not None, f"{script_name} did not return JSON on error"

        # Verify JSON can be re-serialized
        try:
            json_str = json.dumps(output)
            reparsed = json.loads(json_str)
            assert reparsed == output
        except Exception as e:
            pytest.fail(f"{script_name} error output is not valid JSON: {e}")

        # Verify error structure
        assert_valid_error_json(output)
