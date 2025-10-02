# Module: tools.file_handling

**File:** `src/curriculum/tools/file_handling.py`

## Description

File handling utilities.

## Functions

### `get_file_extension`

Get file extension from filename.

Args:
    filename: Filename or path
    
Returns:
    File extension (without dot)

**Parameters:**

- `filename: str`

### `validate_file_type`

Validate if file type is allowed.

Args:
    filename: Filename to validate
    allowed_extensions: List of allowed extensions (with or without dot)
    
Returns:
    True if file type is allowed, False otherwise

**Parameters:**

- `filename: str`

- `allowed_extensions: List[str]`

### `ensure_directory_exists`

Ensure directory exists, create if it doesn't.

Args:
    directory: Directory path

**Parameters:**

- `directory: str`

### `get_file_size`

Get file size in bytes.

Args:
    file_path: Path to file
    
Returns:
    File size in bytes

**Parameters:**

- `file_path: str`

### `is_file_too_large`

Check if file exceeds maximum size.

Args:
    file_path: Path to file
    max_size_bytes: Maximum allowed size in bytes
    
Returns:
    True if file is too large, False otherwise

**Parameters:**

- `file_path: str`

- `max_size_bytes: int`

### `get_safe_filename`

Get a safe filename that doesn't conflict with existing files.

Args:
    filename: Desired filename
    directory: Target directory
    
Returns:
    Safe filename (may be modified to avoid conflicts)

**Parameters:**

- `filename: str`

- `directory: str`

### `read_file_chunks`

Read file in chunks (generator).

Args:
    file_path: Path to file
    chunk_size: Size of each chunk in bytes
    
Yields:
    File chunks

**Parameters:**

- `file_path: str`

- `chunk_size: int`
