"""JSON output formatting utilities for audio analysis scripts."""

import json
import sys
from typing import Any, Dict, List, Optional


def create_success_output(
    file_path: str,
    analysis_type: str,
    data: Dict[str, Any],
    duration_seconds: Optional[float] = None,
    truncated: bool = False,
    warnings: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Create a success JSON output envelope.

    Args:
        file_path: Path to analyzed file
        analysis_type: Type of analysis performed (e.g., 'tempo', 'key', 'beats')
        data: Analysis results data
        duration_seconds: Duration of analyzed audio/MIDI in seconds
        truncated: Whether file was truncated before analysis
        warnings: List of warning messages (non-fatal issues)

    Returns:
        Dictionary with standard output envelope
    """
    return {
        "status": "success",
        "file": str(file_path),
        "analysis_type": analysis_type,
        "duration_seconds": duration_seconds,
        "truncated": truncated,
        "data": data,
        "warnings": warnings or [],
        "error": None
    }


def create_error_output(
    file_path: str,
    analysis_type: str,
    error_code: str,
    error_message: str,
    error_details: Any = None
) -> Dict[str, Any]:
    """
    Create an error JSON output envelope.

    Args:
        file_path: Path to analyzed file (or attempted path)
        analysis_type: Type of analysis attempted
        error_code: Error code (from errors.py constants)
        error_message: Human-readable error message
        error_details: Additional error details (optional)

    Returns:
        Dictionary with standard error envelope
    """
    return {
        "status": "error",
        "file": str(file_path),
        "analysis_type": analysis_type,
        "duration_seconds": None,
        "truncated": False,
        "data": None,
        "warnings": [],
        "error": {
            "code": error_code,
            "message": error_message,
            "details": error_details
        }
    }


def print_json(output: Dict[str, Any], indent: int = 2) -> None:
    """
    Print JSON output to stdout.

    Args:
        output: Dictionary to serialize as JSON
        indent: Number of spaces for indentation (default: 2)
    """
    print(json.dumps(output, indent=indent))


def print_error(message: str) -> None:
    """
    Print error message to stderr.

    Args:
        message: Error message to print
    """
    print(message, file=sys.stderr)


def output_success(
    file_path: str,
    analysis_type: str,
    data: Dict[str, Any],
    duration_seconds: Optional[float] = None,
    truncated: bool = False,
    warnings: Optional[List[str]] = None
) -> None:
    """
    Create and print success output to stdout.

    Args:
        file_path: Path to analyzed file
        analysis_type: Type of analysis performed
        data: Analysis results data
        duration_seconds: Duration of analyzed audio/MIDI in seconds
        truncated: Whether file was truncated before analysis
        warnings: List of warning messages
    """
    output = create_success_output(
        file_path=file_path,
        analysis_type=analysis_type,
        data=data,
        duration_seconds=duration_seconds,
        truncated=truncated,
        warnings=warnings
    )
    print_json(output)


def output_error(
    file_path: str,
    analysis_type: str,
    error_code: str,
    error_message: str,
    error_details: Any = None
) -> None:
    """
    Create and print error output to stdout, and error message to stderr.

    Args:
        file_path: Path to analyzed file (or attempted path)
        analysis_type: Type of analysis attempted
        error_code: Error code constant
        error_message: Human-readable error message
        error_details: Additional error details
    """
    output = create_error_output(
        file_path=file_path,
        analysis_type=analysis_type,
        error_code=error_code,
        error_message=error_message,
        error_details=error_details
    )
    print_json(output)
    print_error(f"Error: {error_message}")
