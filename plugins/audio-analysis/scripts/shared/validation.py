"""File validation utilities for audio analysis scripts."""

import os
from pathlib import Path
from typing import Tuple

from .errors import (
    AnalysisError,
    FILE_NOT_FOUND,
    PATH_TRAVERSAL,
    FILE_TOO_LARGE,
    UNSUPPORTED_FORMAT
)

# File size limit: 100MB
MAX_FILE_SIZE = 100 * 1024 * 1024

# Supported file formats
AUDIO_FORMATS = {'.wav', '.mp3', '.flac', '.ogg', '.m4a'}
MIDI_FORMATS = {'.mid', '.midi'}
ALL_FORMATS = AUDIO_FORMATS | MIDI_FORMATS


def validate_file_path(file_path: str, check_traversal: bool = True) -> Path:
    """
    Validate file path for safety and existence.

    Args:
        file_path: Path to validate
        check_traversal: If True, check for path traversal attempts

    Returns:
        Resolved absolute Path object

    Raises:
        AnalysisError: If validation fails
    """
    # Resolve to absolute path
    try:
        resolved_path = Path(file_path).resolve()
    except (OSError, RuntimeError) as e:
        raise AnalysisError(
            FILE_NOT_FOUND,
            f"Invalid file path: {file_path}",
            str(e)
        )

    # Check for path traversal if requested
    if check_traversal:
        # Get current working directory
        cwd = Path.cwd().resolve()

        # Check if the resolved path escapes the current directory
        # This catches .. attempts that resolve outside working directory
        try:
            # If the path starts with cwd, it's safe
            # If it doesn't, it might be attempting traversal
            # We allow absolute paths, but reject ones with .. that escape
            original_path = Path(file_path)
            if '..' in original_path.parts:
                # Has .., verify it doesn't escape
                # We allow it only if it stays within or goes to absolute path
                if not str(resolved_path).startswith(str(cwd)):
                    # Check if it's an absolute path that was provided
                    if not original_path.is_absolute():
                        raise AnalysisError(
                            PATH_TRAVERSAL,
                            f"Path traversal detected: {file_path}",
                            f"Resolved to {resolved_path} outside working directory {cwd}"
                        )
        except ValueError:
            # Different drives on Windows, or other path issues
            pass

    # Check file exists
    if not resolved_path.exists():
        raise AnalysisError(
            FILE_NOT_FOUND,
            f"File not found: {file_path}",
            f"Resolved path: {resolved_path}"
        )

    # Check it's a file, not a directory
    if not resolved_path.is_file():
        raise AnalysisError(
            FILE_NOT_FOUND,
            f"Path is not a file: {file_path}",
            f"Resolved path: {resolved_path}"
        )

    return resolved_path


def validate_file_size(file_path: Path, max_size: int = MAX_FILE_SIZE) -> int:
    """
    Validate file size is within limits.

    Args:
        file_path: Path to check
        max_size: Maximum allowed size in bytes

    Returns:
        File size in bytes

    Raises:
        AnalysisError: If file exceeds size limit
    """
    file_size = file_path.stat().st_size

    if file_size > max_size:
        size_mb = file_size / (1024 * 1024)
        limit_mb = max_size / (1024 * 1024)
        raise AnalysisError(
            FILE_TOO_LARGE,
            f"File size {size_mb:.1f}MB exceeds limit of {limit_mb:.1f}MB",
            f"File: {file_path}"
        )

    return file_size


def validate_file_format(file_path: Path, allowed_formats: set = None) -> str:
    """
    Validate file format is supported.

    Args:
        file_path: Path to check
        allowed_formats: Set of allowed extensions (e.g., {'.wav', '.mp3'})
                        If None, uses ALL_FORMATS

    Returns:
        File extension (lowercase, with dot)

    Raises:
        AnalysisError: If format is not supported
    """
    if allowed_formats is None:
        allowed_formats = ALL_FORMATS

    extension = file_path.suffix.lower()

    if extension not in allowed_formats:
        raise AnalysisError(
            UNSUPPORTED_FORMAT,
            f"File format '{extension}' is not supported",
            f"Supported formats: {', '.join(sorted(allowed_formats))}"
        )

    return extension


def validate_audio_file(file_path: str) -> Tuple[Path, int, str]:
    """
    Complete validation for audio files.

    Args:
        file_path: Path to audio file

    Returns:
        Tuple of (resolved_path, file_size, extension)

    Raises:
        AnalysisError: If any validation fails
    """
    resolved_path = validate_file_path(file_path)
    file_size = validate_file_size(resolved_path)
    extension = validate_file_format(resolved_path, AUDIO_FORMATS)

    return resolved_path, file_size, extension


def validate_midi_file(file_path: str) -> Tuple[Path, int, str]:
    """
    Complete validation for MIDI files.

    Args:
        file_path: Path to MIDI file

    Returns:
        Tuple of (resolved_path, file_size, extension)

    Raises:
        AnalysisError: If any validation fails
    """
    resolved_path = validate_file_path(file_path)
    file_size = validate_file_size(resolved_path)
    extension = validate_file_format(resolved_path, MIDI_FORMATS)

    return resolved_path, file_size, extension
