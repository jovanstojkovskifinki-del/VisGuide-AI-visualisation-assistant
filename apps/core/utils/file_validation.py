"""
Framework-agnostic file validation helpers. Pure functions only — no
Django imports here beyond typing, so they're trivially unit-testable and
reusable by any future upload path (e.g. document uploads in Module 2).
"""

from apps.core.enums import FileType
from apps.core.exceptions import FileTooLargeError, UnsupportedFileTypeError

MAX_UPLOAD_SIZE_BYTES = 50 * 1024 * 1024  # 50 MB

_EXTENSION_TO_FILE_TYPE = {
    ".csv": FileType.CSV,
    ".xlsx": FileType.XLSX,
}


def detect_file_type(filename: str) -> FileType:
    """
    Determine FileType from filename extension.
    Raises UnsupportedFileTypeError if the extension isn't recognized.
    """
    lowered = filename.lower()
    for extension, file_type in _EXTENSION_TO_FILE_TYPE.items():
        if lowered.endswith(extension):
            return file_type
    raise UnsupportedFileTypeError(
        f"Unsupported file extension for '{filename}'. Supported: "
        f"{', '.join(_EXTENSION_TO_FILE_TYPE.keys())}."
    )


def validate_file_size(size_bytes: int, max_bytes: int = MAX_UPLOAD_SIZE_BYTES) -> None:
    if size_bytes > max_bytes:
        raise FileTooLargeError(
            f"File size {size_bytes} bytes exceeds the maximum of {max_bytes} bytes."
        )
