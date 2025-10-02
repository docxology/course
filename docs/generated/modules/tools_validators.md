# Module: tools.validators

**File:** `src/curriculum/tools/validators.py`

## Description

Validation utilities.

## Functions

### `validate_email`

Validate email address format.

Args:
    email: Email address to validate
    
Returns:
    True if email is valid, False otherwise

**Parameters:**

- `email: str`

### `validate_url`

Validate URL format.

Args:
    url: URL to validate
    
Returns:
    True if URL is valid, False otherwise

**Parameters:**

- `url: str`

### `sanitize_filename`

Sanitize filename by removing invalid characters.

Args:
    filename: Original filename
    max_length: Maximum allowed length
    
Returns:
    Sanitized filename

**Parameters:**

- `filename: str`

- `max_length: int`

### `validate_slug`

Validate URL-safe slug format.

Args:
    slug: Slug to validate
    
Returns:
    True if slug is valid, False otherwise

**Parameters:**

- `slug: str`

### `validate_version`

Validate semantic version format (x.y.z).

Args:
    version: Version string to validate
    
Returns:
    True if version is valid semver, False otherwise

**Parameters:**

- `version: str`

### `validate_hex_color`

Validate hexadecimal color code.

Args:
    color: Color code to validate
    
Returns:
    True if color is valid hex, False otherwise

**Parameters:**

- `color: str`
