"""Pytest configuration and shared fixtures for audio analysis tests."""

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock

import pytest

# Add parent directory to path so we can import scripts module
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def mock_valid_path(tmp_path):
    """Create a mock valid file path for testing."""
    test_file = tmp_path / "test_audio.wav"
    test_file.write_text("mock audio data")
    return test_file


@pytest.fixture
def mock_midi_path(tmp_path):
    """Create a mock MIDI file path for testing."""
    test_file = tmp_path / "test_song.mid"
    test_file.write_text("mock midi data")
    return test_file


@pytest.fixture
def mock_large_file(tmp_path):
    """Create a mock file that appears large via stat."""
    test_file = tmp_path / "large_audio.wav"
    test_file.write_text("data")
    return test_file


@pytest.fixture
def mock_stat_small():
    """Mock stat result for a small file (1MB)."""
    stat_result = Mock()
    stat_result.st_size = 1024 * 1024  # 1MB
    stat_result.st_mode = 0o100644  # Regular file mode
    return stat_result


@pytest.fixture
def mock_stat_large():
    """Mock stat result for a large file (150MB)."""
    stat_result = Mock()
    stat_result.st_size = 150 * 1024 * 1024  # 150MB
    stat_result.st_mode = 0o100644  # Regular file mode
    return stat_result


@pytest.fixture
def mock_stat_boundary():
    """Mock stat result for a file at the boundary (exactly 100MB)."""
    stat_result = Mock()
    stat_result.st_size = 100 * 1024 * 1024  # 100MB exactly
    stat_result.st_mode = 0o100644  # Regular file mode
    return stat_result


@pytest.fixture
def mock_stat_zero():
    """Mock stat result for an empty file."""
    stat_result = Mock()
    stat_result.st_size = 0
    stat_result.st_mode = 0o100644  # Regular file mode
    return stat_result


@pytest.fixture
def sample_analysis_data():
    """Sample analysis data for success outputs."""
    return {
        "tempo": 120.0,
        "confidence": 0.95,
        "beats": [0.5, 1.0, 1.5, 2.0]
    }


@pytest.fixture
def sample_warnings():
    """Sample warning messages."""
    return ["Low confidence in tempo detection", "File may be truncated"]


@pytest.fixture
def reset_cwd():
    """Fixture to save and restore current working directory."""
    original_cwd = Path.cwd()
    yield original_cwd
    os.chdir(original_cwd)
