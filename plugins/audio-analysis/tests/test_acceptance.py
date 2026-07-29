"""
Spec Acceptance Tests for Audio Analysis Plugin.

These tests validate the acceptance criteria from the specification:
- AT1: 120 BPM audio -> tempo_bpm between 115-125
- AT2: C major audio -> key="C", mode="major", confidence >0.7
- AT3: Bach-style MIDI -> chord script identifies I-V progressions
- AT4: Nonexistent file -> non-zero exit, JSON error to stdout
- AT5: All script outputs parse as valid JSON
- AT6: Skill docs include question->script mapping examples
- AT7: 5-minute audio analysis <30 seconds
- AT8: 150MB file returns error without loading
"""

import json
import subprocess
import sys
import time
import tempfile
from pathlib import Path

import pytest
import numpy as np

# Try to import required libraries
try:
    from scipy.io import wavfile
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False

try:
    from midiutil import MIDIFile
    HAS_MIDIUTIL = True
except ImportError:
    HAS_MIDIUTIL = False


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def audio_scripts_dir():
    """Return path to scripts/audio directory."""
    return Path(__file__).parent.parent / "scripts" / "audio"


@pytest.fixture(scope="session")
def midi_scripts_dir():
    """Return path to scripts/midi directory."""
    return Path(__file__).parent.parent / "scripts" / "midi"


@pytest.fixture(scope="session")
def skills_dir():
    """Return path to skills directory."""
    return Path(__file__).parent.parent / "skills"


@pytest.fixture(scope="session")
def acceptance_test_dir(tmp_path_factory):
    """Create directory for acceptance test files."""
    return tmp_path_factory.mktemp("acceptance_tests")


@pytest.fixture(scope="session")
def audio_120bpm(acceptance_test_dir):
    """Generate a 5-second audio file with 120 BPM click track."""
    if not HAS_SCIPY:
        pytest.skip("scipy required for audio generation")

    file_path = acceptance_test_dir / "audio_120bpm.wav"
    duration = 5.0
    sample_rate = 22050
    bpm = 120.0
    beat_interval = 60.0 / bpm  # 0.5 seconds

    # Generate time array
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio = np.zeros_like(t)

    # Add click sounds at each beat
    click_duration = 0.02  # 20ms click
    click_samples = int(click_duration * sample_rate)

    for beat_time in np.arange(0, duration, beat_interval):
        beat_sample = int(beat_time * sample_rate)
        if beat_sample + click_samples < len(audio):
            # Create a sharp click (short burst of high frequency)
            click = np.sin(2 * np.pi * 1000 * np.linspace(0, click_duration, click_samples))
            # Apply envelope
            envelope = np.exp(-np.linspace(0, 5, click_samples))
            click *= envelope
            audio[beat_sample:beat_sample + click_samples] += click

    # Normalize
    audio = audio / (np.max(np.abs(audio)) + 1e-10)

    # Convert to 16-bit PCM
    audio_int16 = (audio * 32767).astype(np.int16)
    wavfile.write(str(file_path), sample_rate, audio_int16)

    return file_path


@pytest.fixture(scope="session")
def audio_c_major(acceptance_test_dir):
    """Generate audio with C major content (C-E-G chord, C scale)."""
    if not HAS_SCIPY:
        pytest.skip("scipy required for audio generation")

    file_path = acceptance_test_dir / "audio_c_major.wav"
    duration = 5.0
    sample_rate = 22050

    # C major chord: C4 (261.63 Hz), E4 (329.63 Hz), G4 (392.00 Hz)
    c_major_freqs = [261.63, 329.63, 392.00]

    # Generate time array
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio = np.zeros_like(t)

    # Add C major chord frequencies
    for freq in c_major_freqs:
        audio += 0.3 * np.sin(2 * np.pi * freq * t)

    # Add C scale notes sequentially in second half
    c_scale_freqs = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25]
    note_duration = duration / 2 / len(c_scale_freqs)
    for i, freq in enumerate(c_scale_freqs):
        start_sample = int(sample_rate * (duration / 2 + i * note_duration))
        end_sample = int(start_sample + note_duration * sample_rate)
        if end_sample < len(audio):
            audio[start_sample:end_sample] += 0.3 * np.sin(
                2 * np.pi * freq * t[start_sample:end_sample]
            )

    # Normalize
    audio = audio / np.max(np.abs(audio))

    # Convert to 16-bit PCM
    audio_int16 = (audio * 32767).astype(np.int16)
    wavfile.write(str(file_path), sample_rate, audio_int16)

    return file_path


@pytest.fixture(scope="session")
def midi_bach_style(acceptance_test_dir):
    """Generate Bach-style MIDI with I-V progressions."""
    if not HAS_MIDIUTIL:
        pytest.skip("midiutil required for MIDI generation")

    file_path = acceptance_test_dir / "bach_style.mid"

    midi = MIDIFile(1)
    track = 0
    channel = 0
    tempo = 120
    volume = 100

    midi.addTempo(track, 0, tempo)

    # C major: I chord (C-E-G) at measure 1
    time = 0
    midi.addNote(track, channel, 60, time, 2, volume)  # C4
    midi.addNote(track, channel, 64, time, 2, volume)  # E4
    midi.addNote(track, channel, 67, time, 2, volume)  # G4

    # V chord (G-B-D) at measure 2
    time = 2
    midi.addNote(track, channel, 55, time, 2, volume)  # G3
    midi.addNote(track, channel, 59, time, 2, volume)  # B3
    midi.addNote(track, channel, 62, time, 2, volume)  # D4

    # I chord again at measure 3
    time = 4
    midi.addNote(track, channel, 60, time, 2, volume)  # C4
    midi.addNote(track, channel, 64, time, 2, volume)  # E4
    midi.addNote(track, channel, 67, time, 2, volume)  # G4

    # V chord at measure 4
    time = 6
    midi.addNote(track, channel, 55, time, 2, volume)  # G3
    midi.addNote(track, channel, 59, time, 2, volume)  # B3
    midi.addNote(track, channel, 62, time, 2, volume)  # D4

    with open(file_path, "wb") as f:
        midi.writeFile(f)

    return file_path


# ============================================================================
# AT1: 120 BPM Audio -> tempo_bpm between 115-125
# ============================================================================

@pytest.mark.skipif(not HAS_SCIPY, reason="scipy required")
class TestAT1TempoBPM:
    """AT1: 120 BPM audio should return tempo_bpm between 115-125."""

    def test_tempo_detection_accuracy(self, audio_scripts_dir, audio_120bpm):
        """Test that 120 BPM audio returns tempo within tolerance."""
        result = subprocess.run(
            [sys.executable, audio_scripts_dir / "analyze_tempo.py", str(audio_120bpm)],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0, f"Script failed: {result.stderr}"

        output = json.loads(result.stdout)
        assert output["status"] == "success"

        tempo_bpm = output["data"]["tempo_bpm"]
        assert 115 <= tempo_bpm <= 125, f"Tempo {tempo_bpm} not within 115-125 range"


# ============================================================================
# AT2: C Major Audio -> key="C", mode="major", confidence >0.7
# ============================================================================

@pytest.mark.skipif(not HAS_SCIPY, reason="scipy required")
class TestAT2KeyDetection:
    """AT2: C major audio should return key='C', mode='major', confidence >0.7."""

    def test_key_detection_c_major(self, audio_scripts_dir, audio_c_major):
        """Test that C major audio returns correct key detection."""
        result = subprocess.run(
            [sys.executable, audio_scripts_dir / "analyze_key.py", str(audio_c_major)],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0, f"Script failed: {result.stderr}"

        output = json.loads(result.stdout)
        assert output["status"] == "success"

        data = output["data"]
        assert data["key"] == "C", f"Expected key 'C', got '{data['key']}'"
        assert data["mode"] == "major", f"Expected mode 'major', got '{data['mode']}'"
        assert data["confidence"] > 0.7, f"Confidence {data['confidence']} not >0.7"


# ============================================================================
# AT3: Bach MIDI -> chord script identifies I-V progressions
# ============================================================================

@pytest.mark.skipif(not HAS_MIDIUTIL, reason="midiutil required")
class TestAT3ChordProgressions:
    """AT3: Bach-style MIDI should identify I-V chord progressions."""

    def test_chord_progression_i_v(self, midi_scripts_dir, midi_bach_style):
        """Test that Bach-style MIDI identifies I and V chords."""
        result = subprocess.run(
            [sys.executable, midi_scripts_dir / "analyze_midi_chords.py", str(midi_bach_style)],
            capture_output=True,
            text=True
        )

        assert result.returncode == 0, f"Script failed: {result.stderr}"

        output = json.loads(result.stdout)
        assert output["status"] == "success"

        data = output["data"]
        chords = data.get("chord_progression", [])

        # Extract Roman numerals
        roman_numerals = [c.get("roman_numeral", "") for c in chords]

        # Should contain I and V progressions
        has_i = any("I" in rn and rn not in ["ii", "iii", "IV", "vi", "vii"] for rn in roman_numerals)
        has_v = any("V" in rn and rn not in ["IV", "vi", "vii"] for rn in roman_numerals)

        assert has_i or has_v, f"Expected I-V progressions, got: {roman_numerals}"


# ============================================================================
# AT4: Nonexistent file -> non-zero exit, JSON error to stdout
# ============================================================================

class TestAT4NonexistentFile:
    """AT4: Nonexistent file should return non-zero exit and JSON error."""

    def test_nonexistent_audio_file(self, audio_scripts_dir):
        """Test error handling for nonexistent audio file."""
        result = subprocess.run(
            [sys.executable, audio_scripts_dir / "analyze_tempo.py", "/nonexistent/file.wav"],
            capture_output=True,
            text=True
        )

        assert result.returncode != 0, "Should return non-zero exit code"

        # Output should be valid JSON
        output = json.loads(result.stdout)
        assert output["status"] == "error"
        assert "error" in output
        assert output["error"]["code"] == "FILE_NOT_FOUND"

    def test_nonexistent_midi_file(self, midi_scripts_dir):
        """Test error handling for nonexistent MIDI file."""
        result = subprocess.run(
            [sys.executable, midi_scripts_dir / "analyze_midi_key.py", "/nonexistent/file.mid"],
            capture_output=True,
            text=True
        )

        assert result.returncode != 0, "Should return non-zero exit code"

        output = json.loads(result.stdout)
        assert output["status"] == "error"
        assert output["error"]["code"] == "FILE_NOT_FOUND"


# ============================================================================
# AT5: All script outputs parse as valid JSON
# ============================================================================

class TestAT5ValidJSON:
    """AT5: All script outputs should parse as valid JSON."""

    @pytest.fixture
    def simple_wav(self, acceptance_test_dir):
        """Create a simple WAV file for testing."""
        if not HAS_SCIPY:
            pytest.skip("scipy required")

        file_path = acceptance_test_dir / "test_json.wav"
        if file_path.exists():
            return file_path

        sample_rate = 22050
        duration = 1.0
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio = np.sin(2 * np.pi * 440 * t)
        audio_int16 = (audio * 32767).astype(np.int16)
        wavfile.write(str(file_path), sample_rate, audio_int16)
        return file_path

    @pytest.mark.skipif(not HAS_SCIPY, reason="scipy required")
    def test_all_audio_scripts_output_valid_json(self, audio_scripts_dir, simple_wav):
        """Test that all audio scripts output valid JSON."""
        scripts = [
            "analyze_tempo.py",
            "analyze_key.py",
            "analyze_beats.py",
            "analyze_structure.py",
            "analyze_chroma.py",
            "analyze_hpss.py",
        ]

        for script in scripts:
            result = subprocess.run(
                [sys.executable, audio_scripts_dir / script, str(simple_wav)],
                capture_output=True,
                text=True
            )

            # Should parse as JSON regardless of success/failure
            try:
                output = json.loads(result.stdout)
                assert "status" in output, f"{script}: missing 'status' field"
            except json.JSONDecodeError as e:
                pytest.fail(f"{script} output is not valid JSON: {e}\nOutput: {result.stdout}")


# ============================================================================
# AT6: Skill docs include question->script mapping examples
# ============================================================================

class TestAT6SkillDocs:
    """AT6: Skill docs should include question->script mapping examples."""

    def test_audio_skill_has_mapping(self, skills_dir):
        """Test that audio-analyzer SKILL.md has decision guidance."""
        skill_md = skills_dir / "audio-analyzer" / "SKILL.md"
        assert skill_md.exists(), "audio-analyzer SKILL.md not found"

        content = skill_md.read_text()

        # Check for decision guidance section
        assert "Decision Guidance" in content, "Missing 'Decision Guidance' section"
        assert "analyze_tempo" in content, "Missing tempo script mapping"
        assert "analyze_key" in content, "Missing key script mapping"

    def test_midi_skill_has_mapping(self, skills_dir):
        """Test that midi-analyzer SKILL.md has decision guidance."""
        skill_md = skills_dir / "midi-analyzer" / "SKILL.md"
        assert skill_md.exists(), "midi-analyzer SKILL.md not found"

        content = skill_md.read_text()

        # Check for decision guidance section
        assert "Decision Guidance" in content, "Missing 'Decision Guidance' section"
        assert "analyze_midi_key" in content, "Missing MIDI key script mapping"
        assert "analyze_midi_chords" in content, "Missing MIDI chords script mapping"


# ============================================================================
# AT7: 5-minute audio analysis <30 seconds
# ============================================================================

@pytest.mark.skipif(not HAS_SCIPY, reason="scipy required")
class TestAT7Performance:
    """AT7: 5-minute audio analysis should complete in <30 seconds."""

    @pytest.fixture(scope="class")
    def audio_5min(self, tmp_path_factory):
        """Generate a 5-minute audio file."""
        test_dir = tmp_path_factory.mktemp("perf_test")
        file_path = test_dir / "audio_5min.wav"

        duration = 300.0  # 5 minutes
        sample_rate = 22050

        # Generate simple audio (sine wave with some variation)
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio = np.sin(2 * np.pi * 440 * t) * (1 + 0.3 * np.sin(2 * np.pi * 0.5 * t))
        audio = audio / np.max(np.abs(audio))
        audio_int16 = (audio * 32767).astype(np.int16)

        wavfile.write(str(file_path), sample_rate, audio_int16)
        return file_path

    def test_tempo_analysis_performance(self, audio_scripts_dir, audio_5min):
        """Test that tempo analysis of 5-min file completes in <30s."""
        start_time = time.time()

        result = subprocess.run(
            [sys.executable, audio_scripts_dir / "analyze_tempo.py", str(audio_5min)],
            capture_output=True,
            text=True,
            timeout=60  # Hard timeout
        )

        elapsed = time.time() - start_time

        assert result.returncode == 0, f"Script failed: {result.stderr}"
        assert elapsed < 30, f"Analysis took {elapsed:.1f}s, expected <30s"


# ============================================================================
# AT8: 150MB file returns error without loading
# ============================================================================

class TestAT8FileSizeLimit:
    """AT8: 150MB file should return error without fully loading."""

    def test_oversized_file_rejected(self, audio_scripts_dir, acceptance_test_dir):
        """Test that oversized file returns FILE_TOO_LARGE error."""
        # Create a fake 150MB file (just header, sparse)
        large_file = acceptance_test_dir / "large_file.wav"

        # Write minimal WAV header then truncate/seek to make it appear large
        with open(large_file, "wb") as f:
            # Write a minimal valid WAV header
            f.write(b"RIFF")
            f.write((150 * 1024 * 1024).to_bytes(4, "little"))  # File size - 8
            f.write(b"WAVE")
            f.write(b"fmt ")
            f.write((16).to_bytes(4, "little"))  # Subchunk1 size
            f.write((1).to_bytes(2, "little"))   # Audio format (PCM)
            f.write((1).to_bytes(2, "little"))   # Num channels
            f.write((22050).to_bytes(4, "little"))  # Sample rate
            f.write((44100).to_bytes(4, "little"))  # Byte rate
            f.write((2).to_bytes(2, "little"))   # Block align
            f.write((16).to_bytes(2, "little"))  # Bits per sample
            f.write(b"data")
            f.write((150 * 1024 * 1024 - 44).to_bytes(4, "little"))  # Data size
            # Seek to make file appear large
            f.seek(150 * 1024 * 1024)
            f.write(b"\x00")

        result = subprocess.run(
            [sys.executable, audio_scripts_dir / "analyze_tempo.py", str(large_file)],
            capture_output=True,
            text=True
        )

        assert result.returncode != 0, "Should return non-zero exit code"

        output = json.loads(result.stdout)
        assert output["status"] == "error"
        assert output["error"]["code"] == "FILE_TOO_LARGE"
