"""Tests for tools module."""

import pytest
import os
import tempfile
from pathlib import Path
from uuid import uuid4


class TestValidators:
    """Tests for validation utilities."""

    def test_validate_email(self):
        """Test email validation."""
        from curriculum.tools.validators import validate_email

        # Valid emails
        assert validate_email("test@example.com") is True
        assert validate_email("user.name+tag@domain.co.uk") is True

        # Invalid emails
        assert validate_email("invalid-email") is False
        assert validate_email("@example.com") is False
        assert validate_email("test@") is False
        assert validate_email("") is False

    def test_validate_url(self):
        """Test URL validation."""
        from curriculum.tools.validators import validate_url

        # Valid URLs
        assert validate_url("https://example.com") is True
        assert validate_url("http://localhost:8080") is True
        assert validate_url("https://sub.domain.com/path?query=1") is True

        # Invalid URLs
        assert validate_url("not-a-url") is False
        assert validate_url("ftp://example.com") is True  # Valid FTP URL
        assert validate_url("") is False

    def test_sanitize_filename(self):
        """Test filename sanitization."""
        from curriculum.tools.validators import sanitize_filename

        # Valid filename
        result = sanitize_filename("test_file.txt")
        assert result == "test_file.txt"

        # Invalid characters should be removed
        result = sanitize_filename("test<file>.txt")
        assert "<" not in result and ">" not in result
        assert result == "testfile.txt"

        # Spaces should be replaced with underscores
        result = sanitize_filename("test file.txt")
        assert result == "test_file.txt"

    def test_validate_slug(self):
        """Test slug validation."""
        from curriculum.tools.validators import validate_slug

        # Valid slugs
        assert validate_slug("test-slug") is True
        assert validate_slug("another-slug") is True
        assert validate_slug("slug123") is True

        # Invalid slugs
        assert validate_slug("Test Slug") is False  # Contains space
        assert validate_slug("slug@domain") is False  # Contains special chars
        assert validate_slug("") is False

    def test_validate_version(self):
        """Test version validation."""
        from curriculum.tools.validators import validate_version

        # Valid versions
        assert validate_version("1.0.0") is True
        assert validate_version("2.15.3") is True
        assert validate_version("0.1.0") is True

        # Invalid versions
        assert validate_version("1.0") is False  # Missing patch
        assert validate_version("v1.0.0") is False  # Contains letter
        assert validate_version("1.0.0.0") is False  # Too many parts
        assert validate_version("") is False

    def test_validate_hex_color(self):
        """Test hex color validation."""
        from curriculum.tools.validators import validate_hex_color

        # Valid colors
        assert validate_hex_color("#ffffff") is True
        assert validate_hex_color("#000") is True
        assert validate_hex_color("#123456") is True

        # Invalid colors
        assert validate_hex_color("#gggggg") is False  # Invalid characters
        assert validate_hex_color("ffffff") is False  # Missing #
        assert validate_hex_color("#12345") is False  # Wrong length


class TestFormatters:
    """Tests for formatting utilities."""

    def test_format_datetime(self):
        """Test datetime formatting."""
        from curriculum.tools.formatters import format_datetime
        from datetime import datetime

        dt = datetime(2024, 1, 15, 14, 30, 45)
        result = format_datetime(dt, "%Y-%m-%d %H:%M:%S")

        assert result == "2024-01-15 14:30:45"

    def test_format_duration(self):
        """Test duration formatting."""
        from curriculum.tools.formatters import format_duration

        # Seconds
        assert format_duration(30) == "30s"
        assert format_duration(90) == "1m 30s"

        # Minutes
        assert format_duration(120) == "2m"
        assert format_duration(150) == "2m 30s"

        # Hours
        assert format_duration(3661) == "1h 1m"  # 1 hour, 1 minute, 1 second

    def test_truncate_text(self):
        """Test text truncation."""
        from curriculum.tools.formatters import truncate_text

        # No truncation needed
        result = truncate_text("Short text", 20)
        assert result == "Short text"

        # Truncation with suffix
        result = truncate_text("This is a very long text", 10)
        assert result == "This is..."

        # Custom suffix
        result = truncate_text("Long text", 5, ">>>")
        assert result == "Lo>>>"

    def test_format_file_size(self):
        """Test file size formatting."""
        from curriculum.tools.formatters import format_file_size

        # Bytes
        assert format_file_size(512) == "512.0 B"

        # Kilobytes
        assert format_file_size(1536) == "1.5 KB"

        # Megabytes
        assert format_file_size(1048576) == "1.0 MB"

        # Gigabytes
        assert format_file_size(1073741824) == "1.0 GB"

    def test_format_percentage(self):
        """Test percentage formatting."""
        from curriculum.tools.formatters import format_percentage

        # Basic formatting
        assert format_percentage(0.85) == "85.0%"
        assert format_percentage(0.123) == "12.3%"

        # Custom decimal places
        assert format_percentage(0.123, 2) == "12.30%"

    def test_slugify(self):
        """Test text slugification."""
        from curriculum.tools.formatters import slugify

        # Basic slugification
        assert slugify("Hello World") == "hello-world"
        assert slugify("Test 123") == "test-123"

        # Special characters
        assert slugify("Hello, World!") == "hello-world"

        # Multiple spaces and hyphens
        assert slugify("  Hello   --  World  ") == "hello-world"


class TestSecurity:
    """Tests for security utilities."""

    def test_generate_token(self):
        """Test token generation."""
        from curriculum.tools.security import generate_token

        token = generate_token(32)
        assert isinstance(token, str)
        assert len(token) == 64  # 32 bytes = 64 hex chars

    def test_generate_verification_code(self):
        """Test verification code generation."""
        from curriculum.tools.security import generate_verification_code

        code = generate_verification_code(6)
        assert isinstance(code, str)
        assert len(code) == 6
        assert code.isdigit()

    def test_hash_content(self):
        """Test content hashing."""
        from curriculum.tools.security import hash_content

        content = "Test content to hash"

        # SHA-256
        hash_256 = hash_content(content, "sha256")
        assert len(hash_256) == 64
        assert hash_256.isalnum()

        # SHA-512
        hash_512 = hash_content(content, "sha512")
        assert len(hash_512) == 128

        # MD5
        hash_md5 = hash_content(content, "md5")
        assert len(hash_md5) == 32

    def test_generate_api_key(self):
        """Test API key generation."""
        from curriculum.tools.security import generate_api_key

        api_key = generate_api_key()
        assert isinstance(api_key, str)
        assert api_key.startswith("ck_")
        assert len(api_key) > 10

    def test_mask_email(self):
        """Test email masking."""
        from curriculum.tools.security import mask_email

        # Normal email
        masked = mask_email("user@example.com")
        assert masked == "u**r@example.com"

        # Short local part
        masked = mask_email("a@b.com")
        assert masked == "a*@b.com"

        # Long local part
        masked = mask_email("verylongusername@example.com")
        assert masked == "v**************e@example.com"

    def test_mask_sensitive_data(self):
        """Test sensitive data masking."""
        from curriculum.tools.security import mask_sensitive_data

        # Normal data
        masked = mask_sensitive_data("sensitive_data_123", 4)
        assert masked == "**************_123"

        # Short data
        masked = mask_sensitive_data("abc", 4)
        assert masked == "***"

        # Data shorter than show_chars
        masked = mask_sensitive_data("abc", 5)
        assert masked == "***"


class TestFileHandling:
    """Tests for file handling utilities."""

    def test_get_file_extension(self):
        """Test file extension extraction."""
        from curriculum.tools.file_handling import get_file_extension

        assert get_file_extension("document.pdf") == "pdf"
        assert get_file_extension("file.txt") == "txt"
        assert get_file_extension("no_extension") == ""
        assert get_file_extension("path/to/file.md") == "md"

    def test_validate_file_type(self):
        """Test file type validation."""
        from curriculum.tools.file_handling import validate_file_type

        # Valid files
        assert validate_file_type("document.pdf", [".pdf", ".doc"]) is True
        assert validate_file_type("file.txt", [".txt", ".md"]) is True

        # Invalid files
        assert validate_file_type("script.exe", [".pdf", ".doc"]) is False
        assert validate_file_type("file", []) is False

    def test_ensure_directory_exists(self):
        """Test directory creation."""
        from curriculum.tools.file_handling import ensure_directory_exists

        with tempfile.TemporaryDirectory() as temp_dir:
            test_dir = Path(temp_dir) / "test" / "nested" / "dir"

            # Directory shouldn't exist initially
            assert not test_dir.exists()

            # Create directory
            ensure_directory_exists(str(test_dir))

            # Directory should now exist
            assert test_dir.exists()
            assert test_dir.is_dir()

    def test_get_file_size(self):
        """Test file size retrieval."""
        from curriculum.tools.file_handling import get_file_size

        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("Test content")
            temp_file = f.name

        try:
            size = get_file_size(temp_file)
            assert size > 0
            assert isinstance(size, int)
        finally:
            os.unlink(temp_file)

    def test_is_file_too_large(self):
        """Test file size validation."""
        from curriculum.tools.file_handling import is_file_too_large

        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("Test content")
            temp_file = f.name

        try:
            # File should not be too large
            assert is_file_too_large(temp_file, 1000000) is False

            # File should be too large for very small limit
            assert is_file_too_large(temp_file, 1) is True
        finally:
            os.unlink(temp_file)

    def test_get_safe_filename(self):
        """Test safe filename generation."""
        from curriculum.tools.file_handling import get_safe_filename

        with tempfile.TemporaryDirectory() as temp_dir:
            # Test with non-existent file
            filename = get_safe_filename("test.txt", temp_dir)
            assert filename == "test.txt"

            # Create the file
            test_file = Path(temp_dir) / "test.txt"
            test_file.touch()

            # Should generate safe filename
            filename = get_safe_filename("test.txt", temp_dir)
            assert filename != "test.txt"
            assert filename.startswith("test_")
            assert filename.endswith(".txt")

    def test_read_file_chunks(self):
        """Test file reading in chunks."""
        from curriculum.tools.file_handling import read_file_chunks

        content = "Line 1\nLine 2\nLine 3\nLine 4\nLine 5"

        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write(content)
            temp_file = f.name

        try:
            chunks = list(read_file_chunks(temp_file, chunk_size=10))

            assert len(chunks) > 1  # Should be multiple chunks
            assert isinstance(chunks[0], bytes)

            # Reconstruct content
            reconstructed = b''.join(chunks).decode()
            assert reconstructed == content
        finally:
            os.unlink(temp_file)
