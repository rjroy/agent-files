"""Error codes and error handling utilities for audio analysis scripts."""

# Error code constants
FILE_NOT_FOUND = "FILE_NOT_FOUND"
PATH_TRAVERSAL = "PATH_TRAVERSAL"
FILE_TOO_LARGE = "FILE_TOO_LARGE"
UNSUPPORTED_FORMAT = "UNSUPPORTED_FORMAT"
CORRUPT_FILE = "CORRUPT_FILE"
ANALYSIS_FAILED = "ANALYSIS_FAILED"


class AnalysisError(Exception):
    """Base exception for analysis errors with structured error information."""

    def __init__(self, code: str, message: str, details=None):
        self.code = code
        self.message = message
        self.details = details
        super().__init__(message)

    def to_dict(self):
        """Convert error to dictionary for JSON serialization."""
        return {
            "code": self.code,
            "message": self.message,
            "details": self.details
        }
