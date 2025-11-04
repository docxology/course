"""File handling utilities."""

import os
from pathlib import Path
from typing import Iterator, List, Optional


def get_file_extension(filename: str) -> str:
    """Get file extension from filename.

    Args:
        filename: Filename or path

    Returns:
        File extension (without dot)
    """
    return Path(filename).suffix.lstrip(".")


def validate_file_type(filename: str, allowed_extensions: List[str]) -> bool:
    """Validate if file type is allowed.

    Args:
        filename: Filename to validate
        allowed_extensions: List of allowed extensions (with or without dot)

    Returns:
        True if file type is allowed, False otherwise
    """
    ext = get_file_extension(filename)

    # Normalize extensions (remove dots if present)
    normalized_allowed = [e.lstrip(".") for e in allowed_extensions]

    return ext.lower() in normalized_allowed


def ensure_directory_exists(directory: str) -> None:
    """Ensure directory exists, create if it doesn't.

    Args:
        directory: Directory path
    """
    Path(directory).mkdir(parents=True, exist_ok=True)


def get_file_size(file_path: str) -> int:
    """Get file size in bytes.

    Args:
        file_path: Path to file

    Returns:
        File size in bytes
    """
    return os.path.getsize(file_path)


def is_file_too_large(file_path: str, max_size_bytes: int) -> bool:
    """Check if file exceeds maximum size.

    Args:
        file_path: Path to file
        max_size_bytes: Maximum allowed size in bytes

    Returns:
        True if file is too large, False otherwise
    """
    return get_file_size(file_path) > max_size_bytes


def get_safe_filename(filename: str, directory: str) -> str:
    """Get a safe filename that doesn't conflict with existing files.

    Args:
        filename: Desired filename
        directory: Target directory

    Returns:
        Safe filename (may be modified to avoid conflicts)
    """
    base_path = Path(directory) / filename

    if not base_path.exists():
        return filename

    # File exists, add number suffix
    name = base_path.stem
    extension = base_path.suffix
    counter = 1

    while True:
        new_filename = f"{name}_{counter}{extension}"
        new_path = Path(directory) / new_filename
        if not new_path.exists():
            return new_filename
        counter += 1


def read_file_chunks(file_path: str, chunk_size: int = 8192) -> Iterator[bytes]:
    """Read file in chunks (generator).

    Args:
        file_path: Path to file
        chunk_size: Size of each chunk in bytes

    Yields:
        File chunks
    """
    with open(file_path, "rb") as f:
        while True:
            chunk = f.read(chunk_size)
            if not chunk:
                break
            yield chunk
