# Module: tools.security

**File:** `src/curriculum/tools/security.py`

## Description

Security utilities.

## Functions

### `generate_token`

Generate a secure random token.

Args:
    length: Length of token in bytes
    
Returns:
    Hexadecimal token string

**Parameters:**

- `length: int`

### `generate_verification_code`

Generate a numeric verification code.

Args:
    length: Length of code
    
Returns:
    Numeric verification code

**Parameters:**

- `length: int`

### `hash_content`

Hash content using specified algorithm.

Args:
    content: Content to hash
    algorithm: Hash algorithm (sha256, sha512, md5)
    
Returns:
    Hexadecimal hash string

**Parameters:**

- `content: str`

- `algorithm: str`

### `generate_api_key`

Generate an API key.

Returns:
    API key string

### `mask_email`

Mask email address for privacy.

Args:
    email: Email address to mask

Returns:
    Masked email address

**Parameters:**

- `email: str`

### `mask_sensitive_data`

Mask sensitive data, showing only specified number of characters.

Args:
    data: Data to mask
    show_chars: Number of characters to show at end
    
Returns:
    Masked data

**Parameters:**

- `data: str`

- `show_chars: int`
