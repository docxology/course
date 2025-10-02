# Module: tools.formatters

**File:** `src/curriculum/tools/formatters.py`

## Description

Formatting utilities.

## Functions

### `format_datetime`

Format datetime to string.

Args:
    dt: Datetime object to format
    format_str: Format string
    
Returns:
    Formatted datetime string

**Parameters:**

- `dt: datetime`

- `format_str: str`

### `format_duration`

Format duration in seconds to human-readable string.

Args:
    seconds: Duration in seconds
    
Returns:
    Formatted duration string (e.g., "2h 30m")

**Parameters:**

- `seconds: int`

### `truncate_text`

Truncate text to maximum length.

Args:
    text: Text to truncate
    max_length: Maximum length
    suffix: Suffix to add when truncated
    
Returns:
    Truncated text

**Parameters:**

- `text: str`

- `max_length: int`

- `suffix: str`

### `format_file_size`

Format file size in bytes to human-readable string.

Args:
    size_bytes: Size in bytes
    
Returns:
    Formatted size string (e.g., "1.5 MB")

**Parameters:**

- `size_bytes: int`

### `format_percentage`

Format decimal as percentage.

Args:
    value: Decimal value (0.0 to 1.0)
    decimal_places: Number of decimal places
    
Returns:
    Formatted percentage string

**Parameters:**

- `value: float`

- `decimal_places: int`

### `slugify`

Convert text to URL-safe slug.

Args:
    text: Text to slugify
    
Returns:
    URL-safe slug

**Parameters:**

- `text: str`
