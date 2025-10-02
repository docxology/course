"""Security utilities."""

import secrets
import hashlib
from typing import Optional


def generate_token(length: int = 32) -> str:
    """Generate a secure random token.
    
    Args:
        length: Length of token in bytes
        
    Returns:
        Hexadecimal token string
    """
    return secrets.token_hex(length)


def generate_verification_code(length: int = 6) -> str:
    """Generate a numeric verification code.
    
    Args:
        length: Length of code
        
    Returns:
        Numeric verification code
    """
    return ''.join(str(secrets.randbelow(10)) for _ in range(length))


def hash_content(content: str, algorithm: str = "sha256") -> str:
    """Hash content using specified algorithm.
    
    Args:
        content: Content to hash
        algorithm: Hash algorithm (sha256, sha512, md5)
        
    Returns:
        Hexadecimal hash string
    """
    if algorithm == "sha256":
        return hashlib.sha256(content.encode()).hexdigest()
    elif algorithm == "sha512":
        return hashlib.sha512(content.encode()).hexdigest()
    elif algorithm == "md5":
        return hashlib.md5(content.encode()).hexdigest()
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")


def generate_api_key() -> str:
    """Generate an API key.
    
    Returns:
        API key string
    """
    return f"ck_{generate_token(24)}"


def mask_email(email: str) -> str:
    """Mask email address for privacy.

    Args:
        email: Email address to mask

    Returns:
        Masked email address
    """
    if '@' not in email:
        return email

    local, domain = email.split('@')

    if len(local) <= 2:
        masked_local = local[0] + '*' * len(local)
    else:
        masked_local = local[0] + '*' * (len(local) - 2) + local[-1]

    return f"{masked_local}@{domain}"


def mask_sensitive_data(data: str, show_chars: int = 4) -> str:
    """Mask sensitive data, showing only specified number of characters.
    
    Args:
        data: Data to mask
        show_chars: Number of characters to show at end
        
    Returns:
        Masked data
    """
    if len(data) <= show_chars:
        return '*' * len(data)
    
    return '*' * (len(data) - show_chars) + data[-show_chars:]
