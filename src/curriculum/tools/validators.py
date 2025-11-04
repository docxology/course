"""Validation utilities."""

import re
from typing import Optional
from urllib.parse import urlparse


def validate_email(email: str) -> bool:
    """Validate email address format.

    Args:
        email: Email address to validate

    Returns:
        True if email is valid, False otherwise
    """
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_url(url: str) -> bool:
    """Validate URL format.

    Args:
        url: URL to validate

    Returns:
        True if URL is valid, False otherwise
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def sanitize_filename(filename: str, max_length: int = 255) -> str:
    """Sanitize filename by removing invalid characters.

    Args:
        filename: Original filename
        max_length: Maximum allowed length

    Returns:
        Sanitized filename
    """
    # Remove invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', "", filename)

    # Replace spaces with underscores
    sanitized = sanitized.replace(" ", "_")

    # Limit length
    if len(sanitized) > max_length:
        name, ext = sanitized.rsplit(".", 1) if "." in sanitized else (sanitized, "")
        name = name[: max_length - len(ext) - 1]
        sanitized = f"{name}.{ext}" if ext else name

    return sanitized


def validate_slug(slug: str) -> bool:
    """Validate URL-safe slug format.

    Args:
        slug: Slug to validate

    Returns:
        True if slug is valid, False otherwise
    """
    pattern = r"^[a-z0-9]+(?:-[a-z0-9]+)*$"
    return bool(re.match(pattern, slug))


def validate_version(version: str) -> bool:
    """Validate semantic version format (x.y.z).

    Args:
        version: Version string to validate

    Returns:
        True if version is valid semver, False otherwise
    """
    pattern = r"^\d+\.\d+\.\d+$"
    return bool(re.match(pattern, version))


def validate_hex_color(color: str) -> bool:
    """Validate hexadecimal color code.

    Args:
        color: Color code to validate

    Returns:
        True if color is valid hex, False otherwise
    """
    pattern = r"^#(?:[0-9a-fA-F]{3}){1,2}$"
    return bool(re.match(pattern, color))
