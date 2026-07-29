"""Shared utilities for audio analysis scripts."""

from .errors import (
    AnalysisError,
    FILE_NOT_FOUND,
    PATH_TRAVERSAL,
    FILE_TOO_LARGE,
    UNSUPPORTED_FORMAT,
    CORRUPT_FILE,
    ANALYSIS_FAILED
)

from .validation import (
    validate_file_path,
    validate_file_size,
    validate_file_format,
    validate_audio_file,
    validate_midi_file,
    AUDIO_FORMATS,
    MIDI_FORMATS,
    ALL_FORMATS,
    MAX_FILE_SIZE
)

from .output import (
    create_success_output,
    create_error_output,
    print_json,
    print_error,
    output_success,
    output_error
)

__all__ = [
    # Error handling
    'AnalysisError',
    'FILE_NOT_FOUND',
    'PATH_TRAVERSAL',
    'FILE_TOO_LARGE',
    'UNSUPPORTED_FORMAT',
    'CORRUPT_FILE',
    'ANALYSIS_FAILED',
    # Validation
    'validate_file_path',
    'validate_file_size',
    'validate_file_format',
    'validate_audio_file',
    'validate_midi_file',
    'AUDIO_FORMATS',
    'MIDI_FORMATS',
    'ALL_FORMATS',
    'MAX_FILE_SIZE',
    # Output formatting
    'create_success_output',
    'create_error_output',
    'print_json',
    'print_error',
    'output_success',
    'output_error',
]
