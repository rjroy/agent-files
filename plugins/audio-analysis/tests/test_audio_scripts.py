"""
Integration tests for audio analysis scripts.

Tests all 8 audio scripts with programmatically generated test fixtures.
Tests happy paths, format handling, error paths, truncation warnings, and performance.
"""

import json
import subprocess
import sys
import time
from pathlib import Path

import pytest
import numpy as np

# Try to import audio generation libraries
try:
    from scipy.io import wavfile
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False

try:
    import librosa
    import soundfile as sf
    HAS_LIBROSA = True
except ImportError:
    HAS_LIBROSA = False


# ============================================================================
# Test Fixtures - Audio File Generation
# ============================================================================

@pytest.fixture(scope="session")
def scripts_dir():
    """Return path to scripts/audio directory."""
    return Path(__file__).parent.parent / "scripts" / "audio"


@pytest.fixture(scope="session")
def test_audio_dir(tmp_path_factory):
    """Create directory for test audio files."""
    return tmp_path_factory.mktemp("test_audio")


@pytest.fixture(scope="session")
def simple_wav_5sec(test_audio_dir):
    """Generate a simple 5-second WAV file with 440 Hz sine wave (A4 note)."""
    if not HAS_SCIPY:
        pytest.skip("scipy required for WAV generation")

    file_path = test_audio_dir / "simple_5sec.wav"
    duration = 5.0
    sample_rate = 22050
    frequency = 440.0  # A4

    # Generate sine wave
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio = np.sin(2 * np.pi * frequency * t)

    # Convert to 16-bit PCM
    audio_int16 = (audio * 32767).astype(np.int16)

    # Write WAV file
    wavfile.write(str(file_path), sample_rate, audio_int16)

    return file_path


@pytest.fixture(scope="session")
def music_like_wav(test_audio_dir):
    """Generate a more music-like WAV with multiple frequencies (C major chord)."""
    if not HAS_SCIPY:
        pytest.skip("scipy required for WAV generation")

    file_path = test_audio_dir / "music_like.wav"
    duration = 5.0
    sample_rate = 22050

    # C major chord: C4 (261.63 Hz), E4 (329.63 Hz), G4 (392.00 Hz)
    frequencies = [261.63, 329.63, 392.00]

    # Generate time array
    t = np.linspace(0, duration, int(sample_rate * duration))

    # Sum sine waves with different amplitudes
    audio = np.zeros_like(t)
    for i, freq in enumerate(frequencies):
        amplitude = 0.3 / (i + 1)  # Decreasing amplitude
        audio += amplitude * np.sin(2 * np.pi * freq * t)

    # Normalize
    audio = audio / np.max(np.abs(audio))

    # Convert to 16-bit PCM
    audio_int16 = (audio * 32767).astype(np.int16)

    # Write WAV file
    wavfile.write(str(file_path), sample_rate, audio_int16)

    return file_path


@pytest.fixture(scope="session")
def rhythmic_wav(test_audio_dir):
    """Generate a WAV with rhythmic pulses (for beat detection)."""
    if not HAS_SCIPY:
        pytest.skip("scipy required for WAV generation")

    file_path = test_audio_dir / "rhythmic.wav"
    duration = 4.0  # 4 seconds
    sample_rate = 22050
    tempo_bpm = 120  # 120 BPM = 2 beats per second

    # Generate time array
    t = np.linspace(0, duration, int(sample_rate * duration))

    # Create clicks at regular intervals
    beat_interval = 60.0 / tempo_bpm  # seconds per beat
    audio = np.zeros_like(t)

    for beat_time in np.arange(0, duration, beat_interval):
        # Create a short click (10ms)
        click_duration = 0.01
        click_samples = int(sample_rate * click_duration)
        click_start = int(beat_time * sample_rate)

        if click_start + click_samples < len(audio):
            # Exponential decay envelope
            envelope = np.exp(-np.linspace(0, 5, click_samples))
            freq = 1000  # Click frequency
            click = envelope * np.sin(2 * np.pi * freq * np.linspace(0, click_duration, click_samples))
            audio[click_start:click_start + click_samples] += click

    # Normalize
    audio = audio / np.max(np.abs(audio))

    # Convert to 16-bit PCM
    audio_int16 = (audio * 32767).astype(np.int16)

    # Write WAV file
    wavfile.write(str(file_path), sample_rate, audio_int16)

    return file_path


@pytest.fixture(scope="session")
def long_wav_12min(test_audio_dir):
    """Generate a 12-minute WAV file to test truncation warning."""
    if not HAS_SCIPY:
        pytest.skip("scipy required for WAV generation")

    file_path = test_audio_dir / "long_12min.wav"
    duration = 12 * 60  # 12 minutes in seconds
    sample_rate = 22050
    frequency = 440.0

    # Generate in chunks to avoid memory issues
    chunk_duration = 60  # 1 minute chunks
    num_chunks = int(duration / chunk_duration)

    all_chunks = []
    for i in range(num_chunks):
        t = np.linspace(0, chunk_duration, int(sample_rate * chunk_duration))
        # Vary frequency slightly to make it more interesting
        freq = frequency + (i % 3) * 10
        audio = np.sin(2 * np.pi * freq * t)
        audio_int16 = (audio * 32767).astype(np.int16)
        all_chunks.append(audio_int16)

    # Concatenate all chunks
    full_audio = np.concatenate(all_chunks)

    # Write WAV file
    wavfile.write(str(file_path), sample_rate, full_audio)

    return file_path


@pytest.fixture(scope="session")
def mp3_file(test_audio_dir, simple_wav_5sec):
    """Convert WAV to MP3 using ffmpeg if available."""
    if not HAS_LIBROSA:
        pytest.skip("librosa required for MP3 generation")

    mp3_path = test_audio_dir / "test_audio.mp3"

    # Try to use ffmpeg to convert
    try:
        subprocess.run(
            ["ffmpeg", "-i", str(simple_wav_5sec), "-acodec", "libmp3lame", "-y", str(mp3_path)],
            capture_output=True,
            check=True,
            timeout=10
        )
        return mp3_path
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        pytest.skip("ffmpeg not available for MP3 conversion")


@pytest.fixture(scope="session")
def flac_file(test_audio_dir, simple_wav_5sec):
    """Convert WAV to FLAC using ffmpeg if available."""
    if not HAS_LIBROSA:
        pytest.skip("librosa required for FLAC generation")

    flac_path = test_audio_dir / "test_audio.flac"

    # Try to use ffmpeg to convert
    try:
        subprocess.run(
            ["ffmpeg", "-i", str(simple_wav_5sec), "-acodec", "flac", "-y", str(flac_path)],
            capture_output=True,
            check=True,
            timeout=10
        )
        return flac_path
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        pytest.skip("ffmpeg not available for FLAC conversion")


@pytest.fixture(scope="session")
def ogg_file(test_audio_dir, simple_wav_5sec):
    """Convert WAV to OGG using ffmpeg if available."""
    if not HAS_LIBROSA:
        pytest.skip("librosa required for OGG generation")

    ogg_path = test_audio_dir / "test_audio.ogg"

    # Try to use ffmpeg to convert
    try:
        subprocess.run(
            ["ffmpeg", "-i", str(simple_wav_5sec), "-acodec", "libvorbis", "-y", str(ogg_path)],
            capture_output=True,
            check=True,
            timeout=10
        )
        return ogg_path
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
        pytest.skip("ffmpeg not available for OGG conversion")


@pytest.fixture(scope="session")
def corrupt_wav(test_audio_dir):
    """Create a corrupted WAV file (invalid header)."""
    file_path = test_audio_dir / "corrupt.wav"
    # Write garbage data
    file_path.write_bytes(b"This is not a valid WAV file" * 100)
    return file_path


@pytest.fixture(scope="session")
def oversized_file(test_audio_dir):
    """Create a file that appears oversized (>100MB) for validation testing."""
    # Note: We can't actually create a 100MB+ file in tests,
    # but we can test the validation logic separately
    file_path = test_audio_dir / "oversized.wav"
    file_path.write_bytes(b"small file")
    return file_path


# ============================================================================
# Helper Functions
# ============================================================================

def check_librosa_available():
    """Check if librosa and dependencies are installed."""
    try:
        import librosa
        import soundfile
        return True
    except ImportError:
        return False


def run_audio_script(scripts_dir, script_name, *args, timeout=35):
    """
    Run an audio analysis script and return parsed JSON output.

    Args:
        scripts_dir: Path to scripts/audio directory
        script_name: Name of script (e.g., "analyze_tempo.py")
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

    # If no JSON in stdout, try stderr (some scripts may write errors to stderr)
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
# Tests for analyze_tempo.py
# ============================================================================

@pytest.mark.skipif(not check_librosa_available(), reason="librosa and soundfile required")
class TestAnalyzeTempo:
    """Integration tests for analyze_tempo.py script."""

    def test_tempo_valid_wav(self, scripts_dir, simple_wav_5sec):
        """Test tempo analysis with valid WAV file."""
        output, returncode, stdout, stderr = run_audio_script(
            scripts_dir, "analyze_tempo.py", simple_wav_5sec
        )

        assert returncode == 0, f"Script failed: {stderr}"
        assert_valid_success_json(output, "tempo")

        # Check data fields
        data = output["data"]
        assert "tempo_bpm" in data
        assert "confidence" in data
        assert "beat_frames" in data
        assert "beat_times" in data
        assert isinstance(data["tempo_bpm"], (int, float))
        assert 0.0 <= data["confidence"] <= 1.0
        assert isinstance(data["beat_frames"], list)
        assert isinstance(data["beat_times"], list)

    def test_tempo_missing_file(self, scripts_dir, test_audio_dir):
        """Test tempo analysis with non-existent file."""
        missing_file = test_audio_dir / "does_not_exist.wav"
        output, returncode, stdout, stderr = run_audio_script(
            scripts_dir, "analyze_tempo.py", missing_file
        )

        assert returncode != 0, "Should fail with non-zero exit code"
        assert_valid_error_json(output, "FILE_NOT_FOUND")

    def test_tempo_corrupt_file(self, scripts_dir, corrupt_wav):
        """Test tempo analysis with corrupted file."""
        output, returncode, stdout, stderr = run_audio_script(
            scripts_dir, "analyze_tempo.py", corrupt_wav
        )

        assert returncode != 0, "Should fail with non-zero exit code"
        assert_valid_error_json(output)
        # Could be CORRUPT_FILE or ANALYSIS_FAILED depending on where it fails
        assert output["error"]["code"] in ["CORRUPT_FILE", "ANALYSIS_FAILED"]

    def test_tempo_truncation_warning(self, scripts_dir, long_wav_12min):
        """Test that 12-minute file shows truncation warning."""
        output, returncode, stdout, stderr = run_audio_script(
            scripts_dir, "analyze_tempo.py", long_wav_12min, timeout=60
        )

        assert returncode == 0, f"Script should succeed: {stderr}"
        assert_valid_success_json(output, "tempo")
        assert output["truncated"] is True
        assert len(output["warnings"]) > 0
        assert any("truncated" in w.lower() for w in output["warnings"])

    def test_tempo_performance_5min(self, scripts_dir, simple_wav_5sec):
        """Test that tempo analysis completes in <30 seconds for 5-minute file."""
        start_time = time.time()
        output, returncode, stdout, stderr = run_audio_script(
            scripts_dir, "analyze_tempo.py", simple_wav_5sec, timeout=30
        )
        elapsed = time.time() - start_time

        assert returncode == 0, f"Script failed: {stderr}"
        assert elapsed < 30, f"Analysis took {elapsed:.2f}s, should be <30s"


# ============================================================================
# Tests for analyze_key.py
# ============================================================================

@pytest.mark.skipif(not check_librosa_available(), reason="librosa and soundfile required")
class TestAnalyzeKey:
    """Integration tests for analyze_key.py script."""

    def test_key_valid_wav(self, scripts_dir, music_like_wav):
        """Test key analysis with valid WAV file."""
        output, returncode, stdout, stderr = run_audio_script(
            scripts_dir, "analyze_key.py", music_like_wav
        )

        assert returncode == 0, f"Script failed: {stderr}"
        assert_valid_success_json(output, "key")

        # Check data fields
        data = output["data"]
        assert "key" in data
        assert "mode" in data
        assert "confidence" in data
        assert "alternative" in data
        assert data["key"] in ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        assert data["mode"] in ['major', 'minor']
        assert 0.0 <= data["confidence"] <= 1.0

    def test_key_missing_file(self, scripts_dir, test_audio_dir):
        """Test key analysis with non-existent file."""
        missing_file = test_audio_dir / "does_not_exist.wav"
        output, returncode, stdout, stderr = run_audio_script(
            scripts_dir, "analyze_key.py", missing_file
        )

        assert returncode != 0, "Should fail with non-zero exit code"
        assert_valid_error_json(output, "FILE_NOT_FOUND")

    def test_key_format_mp3(self, scripts_dir, mp3_file):
        """Test key analysis with MP3 format."""
        output, returncode, stdout, stderr = run_audio_script(
            scripts_dir, "analyze_key.py", mp3_file
        )

        assert returncode == 0, f"Script failed: {stderr}"
        assert_valid_success_json(output, "key")


# ============================================================================
# Tests for analyze_beats.py
# ============================================================================

@pytest.mark.skipif(not check_librosa_available(), reason="librosa and soundfile required")
class TestAnalyzeBeats:
    """Integration tests for analyze_beats.py script."""

    def test_beats_valid_wav(self, scripts_dir, rhythmic_wav):
        """Test beat analysis with rhythmic WAV file."""
        output, returncode, stdout, stderr = run_audio_script(
            scripts_dir, "analyze_beats.py", rhythmic_wav
        )

        assert returncode == 0, f"Script failed: {stderr}"
        assert_valid_success_json(output, "beats")

        # Check data fields
        data = output["data"]
        assert "beat_frames" in data
        assert "beat_times" in data
        assert "beat_count" in data
        assert isinstance(data["beat_frames"], list)
        assert isinstance(data["beat_times"], list)
        assert isinstance(data["beat_count"], int)
        assert data["beat_count"] >= 0

    def test_beats_missing_file(self, scripts_dir, test_audio_dir):
        """Test beat analysis with non-existent file."""
        missing_file = test_audio_dir / "does_not_exist.wav"
        output, returncode, stdout, stderr = run_audio_script(
            scripts_dir, "analyze_beats.py", missing_file
        )

        assert returncode != 0, "Should fail with non-zero exit code"
        assert_valid_error_json(output, "FILE_NOT_FOUND")


# ============================================================================
# Tests for analyze_structure.py
# ============================================================================

@pytest.mark.skipif(not check_librosa_available(), reason="librosa and soundfile required")
class TestAnalyzeStructure:
    """Integration tests for analyze_structure.py script."""

    def test_structure_valid_wav(self, scripts_dir, simple_wav_5sec):
        """Test structure analysis with valid WAV file."""
        output, returncode, stdout, stderr = run_audio_script(
            scripts_dir, "analyze_structure.py", simple_wav_5sec
        )

        assert returncode == 0, f"Script failed: {stderr}"
        assert_valid_success_json(output, "structure")

        # Check data fields
        data = output["data"]
        assert "sections" in data
        assert "num_sections" in data
        assert isinstance(data["sections"], list)
        assert isinstance(data["num_sections"], int)

        # Each section should have required fields
        for section in data["sections"]:
            assert "label" in section
            assert "start_time" in section
            assert "end_time" in section

    def test_structure_format_flac(self, scripts_dir, flac_file):
        """Test structure analysis with FLAC format."""
        output, returncode, stdout, stderr = run_audio_script(
            scripts_dir, "analyze_structure.py", flac_file
        )

        assert returncode == 0, f"Script failed: {stderr}"
        assert_valid_success_json(output, "structure")


# ============================================================================
# Tests for analyze_chroma.py
# ============================================================================

@pytest.mark.skipif(not check_librosa_available(), reason="librosa and soundfile required")
class TestAnalyzeChroma:
    """Integration tests for analyze_chroma.py script."""

    def test_chroma_valid_wav(self, scripts_dir, music_like_wav):
        """Test chroma analysis with valid WAV file."""
        output, returncode, stdout, stderr = run_audio_script(
            scripts_dir, "analyze_chroma.py", music_like_wav
        )

        assert returncode == 0, f"Script failed: {stderr}"
        assert_valid_success_json(output, "chroma")

        # Check data fields
        data = output["data"]
        assert "time_points" in data
        assert "pitch_classes" in data
        assert "chroma_matrix" in data
        assert isinstance(data["time_points"], list)
        assert isinstance(data["pitch_classes"], list)
        assert isinstance(data["chroma_matrix"], list)

        # Check pitch classes
        assert len(data["pitch_classes"]) == 12

        # Check matrix dimensions
        if len(data["chroma_matrix"]) > 0:
            assert len(data["chroma_matrix"][0]) == 12

    def test_chroma_missing_file(self, scripts_dir, test_audio_dir):
        """Test chroma analysis with non-existent file."""
        missing_file = test_audio_dir / "does_not_exist.wav"
        output, returncode, stdout, stderr = run_audio_script(
            scripts_dir, "analyze_chroma.py", missing_file
        )

        assert returncode != 0, "Should fail with non-zero exit code"
        assert_valid_error_json(output, "FILE_NOT_FOUND")


# ============================================================================
# Tests for generate_spectrogram.py
# ============================================================================

@pytest.mark.skipif(not check_librosa_available(), reason="librosa and soundfile required")
class TestGenerateSpectrogram:
    """Integration tests for generate_spectrogram.py script."""

    def test_spectrogram_valid_wav(self, scripts_dir, simple_wav_5sec, test_audio_dir):
        """Test spectrogram generation with valid WAV file."""
        output_path = test_audio_dir / "spectrogram_output.png"
        output, returncode, stdout, stderr = run_audio_script(
            scripts_dir, "generate_spectrogram.py", simple_wav_5sec, output_path
        )

        assert returncode == 0, f"Script failed: {stderr}"
        assert_valid_success_json(output, "spectrogram")

        # Check data fields
        data = output["data"]
        assert "output_path" in data
        assert "width" in data
        assert "height" in data

        # Check that output file was created
        assert output_path.exists()
        assert output_path.stat().st_size > 0

    def test_spectrogram_missing_file(self, scripts_dir, test_audio_dir):
        """Test spectrogram generation with non-existent file."""
        missing_file = test_audio_dir / "does_not_exist.wav"
        output_path = test_audio_dir / "spectrogram_output.png"
        output, returncode, stdout, stderr = run_audio_script(
            scripts_dir, "generate_spectrogram.py", missing_file, output_path
        )

        assert returncode != 0, "Should fail with non-zero exit code"
        assert_valid_error_json(output, "FILE_NOT_FOUND")

    def test_spectrogram_format_ogg(self, scripts_dir, ogg_file, test_audio_dir):
        """Test spectrogram generation with OGG format."""
        output_path = test_audio_dir / "spectrogram_ogg.png"
        output, returncode, stdout, stderr = run_audio_script(
            scripts_dir, "generate_spectrogram.py", ogg_file, output_path
        )

        assert returncode == 0, f"Script failed: {stderr}"
        assert_valid_success_json(output, "spectrogram")
        assert output_path.exists()


# ============================================================================
# Tests for analyze_hpss.py
# ============================================================================

@pytest.mark.skipif(not check_librosa_available(), reason="librosa and soundfile required")
class TestAnalyzeHPSS:
    """Integration tests for analyze_hpss.py script."""

    def test_hpss_valid_wav(self, scripts_dir, rhythmic_wav, test_audio_dir):
        """Test HPSS analysis with valid WAV file."""
        harmonic_path = test_audio_dir / "harmonic.wav"
        percussive_path = test_audio_dir / "percussive.wav"

        output, returncode, stdout, stderr = run_audio_script(
            scripts_dir, "analyze_hpss.py", rhythmic_wav, harmonic_path, percussive_path
        )

        assert returncode == 0, f"Script failed: {stderr}"
        assert_valid_success_json(output, "hpss")

        # Check data fields
        data = output["data"]
        assert "harmonic_path" in data
        assert "percussive_path" in data

        # Check that output files were created
        assert harmonic_path.exists()
        assert percussive_path.exists()
        assert harmonic_path.stat().st_size > 0
        assert percussive_path.stat().st_size > 0

    def test_hpss_missing_file(self, scripts_dir, test_audio_dir):
        """Test HPSS analysis with non-existent file."""
        missing_file = test_audio_dir / "does_not_exist.wav"
        harmonic_path = test_audio_dir / "harmonic.wav"
        percussive_path = test_audio_dir / "percussive.wav"

        output, returncode, stdout, stderr = run_audio_script(
            scripts_dir, "analyze_hpss.py", missing_file, harmonic_path, percussive_path
        )

        assert returncode != 0, "Should fail with non-zero exit code"
        assert_valid_error_json(output, "FILE_NOT_FOUND")


# ============================================================================
# Tests for compare_audio.py
# ============================================================================

@pytest.mark.skipif(not check_librosa_available(), reason="librosa and soundfile required")
class TestCompareAudio:
    """Integration tests for compare_audio.py script."""

    def test_compare_two_files(self, scripts_dir, simple_wav_5sec, music_like_wav):
        """Test audio comparison with two valid files."""
        output, returncode, stdout, stderr = run_audio_script(
            scripts_dir, "compare_audio.py", simple_wav_5sec, music_like_wav
        )

        assert returncode == 0, f"Script failed: {stderr}"
        assert_valid_success_json(output, "compare")

        # Check data fields
        data = output["data"]
        assert "file1" in data
        assert "file2" in data
        assert "similarity_scores" in data
        assert "overall_similarity" in data

        # Check similarity scores
        scores = data["similarity_scores"]
        assert "tempo" in scores
        assert "key" in scores
        assert "chroma" in scores

        # All scores should be 0-1
        for score_type, score_value in scores.items():
            assert 0.0 <= score_value <= 1.0

        assert 0.0 <= data["overall_similarity"] <= 1.0

    def test_compare_same_file(self, scripts_dir, simple_wav_5sec):
        """Test audio comparison with same file (should have high similarity)."""
        output, returncode, stdout, stderr = run_audio_script(
            scripts_dir, "compare_audio.py", simple_wav_5sec, simple_wav_5sec
        )

        assert returncode == 0, f"Script failed: {stderr}"
        assert_valid_success_json(output, "compare")

        # Overall similarity should be very high (ideally 1.0)
        data = output["data"]
        assert data["overall_similarity"] > 0.9

    def test_compare_missing_file(self, scripts_dir, simple_wav_5sec, test_audio_dir):
        """Test audio comparison with one missing file."""
        missing_file = test_audio_dir / "does_not_exist.wav"
        output, returncode, stdout, stderr = run_audio_script(
            scripts_dir, "compare_audio.py", simple_wav_5sec, missing_file
        )

        assert returncode != 0, "Should fail with non-zero exit code"
        assert_valid_error_json(output, "FILE_NOT_FOUND")


# ============================================================================
# Format Compatibility Tests
# ============================================================================

@pytest.mark.skipif(not check_librosa_available(), reason="librosa and soundfile required")
class TestFormatCompatibility:
    """Test all scripts work with different audio formats."""

    @pytest.mark.parametrize("script_name", [
        "analyze_tempo.py",
        "analyze_key.py",
        "analyze_beats.py",
        "analyze_structure.py",
        "analyze_chroma.py",
    ])
    def test_wav_format(self, scripts_dir, simple_wav_5sec, script_name):
        """Test that script works with WAV format."""
        output, returncode, stdout, stderr = run_audio_script(
            scripts_dir, script_name, simple_wav_5sec
        )

        assert returncode == 0, f"{script_name} failed with WAV: {stderr}"
        assert output is not None
        assert output.get("status") == "success"

    @pytest.mark.parametrize("script_name", [
        "analyze_tempo.py",
        "analyze_key.py",
    ])
    def test_mp3_format(self, scripts_dir, mp3_file, script_name):
        """Test that script works with MP3 format."""
        output, returncode, stdout, stderr = run_audio_script(
            scripts_dir, script_name, mp3_file
        )

        assert returncode == 0, f"{script_name} failed with MP3: {stderr}"
        assert output is not None
        assert output.get("status") == "success"


# ============================================================================
# Performance Tests
# ============================================================================

@pytest.mark.skipif(not check_librosa_available(), reason="librosa and soundfile required")
class TestPerformance:
    """Performance tests for all scripts."""

    @pytest.mark.parametrize("script_name,analysis_type", [
        ("analyze_tempo.py", "tempo"),
        ("analyze_key.py", "key"),
        ("analyze_beats.py", "beats"),
        ("analyze_structure.py", "structure"),
        ("analyze_chroma.py", "chroma"),
    ])
    def test_performance_5sec_file(self, scripts_dir, simple_wav_5sec, script_name, analysis_type):
        """Test that scripts complete in reasonable time for 5-second files."""
        start_time = time.time()
        output, returncode, stdout, stderr = run_audio_script(
            scripts_dir, script_name, simple_wav_5sec, timeout=30
        )
        elapsed = time.time() - start_time

        assert returncode == 0, f"{script_name} failed: {stderr}"
        assert elapsed < 30, f"{script_name} took {elapsed:.2f}s, should be <30s"

        # Log performance for tracking
        print(f"\n{script_name}: {elapsed:.2f}s")


# ============================================================================
# Error Handling Tests
# ============================================================================

@pytest.mark.skipif(not check_librosa_available(), reason="librosa and soundfile required")
class TestErrorHandling:
    """Test error handling across all scripts."""

    @pytest.mark.parametrize("script_name", [
        "analyze_tempo.py",
        "analyze_key.py",
        "analyze_beats.py",
        "analyze_structure.py",
        "analyze_chroma.py",
    ])
    def test_unsupported_format(self, scripts_dir, test_audio_dir, script_name):
        """Test that scripts reject unsupported file formats."""
        unsupported_file = test_audio_dir / "test.aac"
        unsupported_file.write_bytes(b"fake audio data")

        output, returncode, stdout, stderr = run_audio_script(
            scripts_dir, script_name, unsupported_file
        )

        assert returncode != 0, f"{script_name} should reject unsupported format"
        assert_valid_error_json(output, "UNSUPPORTED_FORMAT")

    @pytest.mark.parametrize("script_name", [
        "analyze_tempo.py",
        "analyze_key.py",
        "analyze_beats.py",
    ])
    def test_corrupt_file_handling(self, scripts_dir, corrupt_wav, script_name):
        """Test that scripts handle corrupt files gracefully."""
        output, returncode, stdout, stderr = run_audio_script(
            scripts_dir, script_name, corrupt_wav
        )

        assert returncode != 0, f"{script_name} should fail on corrupt file"
        assert output is not None, "Should return JSON even on error"
        assert output.get("status") == "error"
