# AI Agents Guide - Tools Module

## Overview

The tools module provides essential utility functions and helper classes that support the core functionality of the Curriculum Repository System. These utilities handle common operations like validation, formatting, security, and file handling that are used across multiple modules.

## Module Structure

```
tools/
├── validators.py       # Input validation utilities
├── formatters.py       # Data formatting and transformation
├── security.py         # Security and encryption utilities
├── file_handling.py    # File operations and validation
└── README.md           # Module documentation
```

## Validation Utilities

### Input Validation

1. **Email Validation**:
```python
from curriculum.tools.validators import validate_email, validate_email_format

def validate_email(email: str) -> bool:
    """Validate email address format and domain."""
    if not validate_email_format(email):
        return False

    # Check for disposable email domains
    if email.split('@')[1] in DISPOSABLE_DOMAINS:
        return False

    # Check for common typos
    if email.lower() in COMMON_EMAIL_TYPOS:
        return False

    return True

def validate_email_format(email: str) -> bool:
    """Basic email format validation using regex."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))
```

2. **URL Validation**:
```python
def validate_url(url: str) -> bool:
    """Validate URL format and accessibility."""
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return False

        # Check if URL is accessible (optional)
        if CHECK_URL_ACCESSIBILITY:
            response = requests.head(url, timeout=5)
            return response.status_code < 400

        return True
    except Exception:
        return False

def sanitize_url(url: str) -> str:
    """Sanitize URL for safe storage."""
    url = url.strip()
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    return url
```

3. **Content Validation**:
```python
def validate_content_body(content: str, format: ContentFormat) -> Tuple[bool, List[str]]:
    """Validate content body based on format."""
    errors = []

    if format == ContentFormat.MARKDOWN:
        # Check for broken markdown syntax
        if content.count('[') != content.count(']'):
            errors.append("Unmatched markdown links")

    elif format == ContentFormat.HTML:
        # Check for dangerous HTML
        dangerous_tags = ['script', 'iframe', 'object', 'embed']
        for tag in dangerous_tags:
            if f'<{tag}' in content.lower():
                errors.append(f"Dangerous HTML tag: {tag}")

    return len(errors) == 0, errors
```

### Slug Generation

1. **URL-Friendly Slugs**:
```python
def generate_slug(text: str, max_length: int = 50) -> str:
    """Generate URL-friendly slug from text."""
    # Convert to lowercase
    slug = text.lower()

    # Replace spaces and special characters
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_-]+', '-', slug)

    # Remove leading/trailing dashes
    slug = slug.strip('-')

    # Truncate if too long
    if len(slug) > max_length:
        slug = slug[:max_length].rstrip('-')

    return slug

def is_slug_available(slug: str, entity_type: str) -> bool:
    """Check if slug is available for use."""
    # Check against existing slugs in database
    existing = db.query(f"SELECT id FROM {entity_type} WHERE slug = ?", (slug,))
    return len(existing) == 0
```

## Formatting Utilities

### Date and Time Formatting

1. **Datetime Formatting**:
```python
def format_datetime(dt: datetime, format_string: str = None) -> str:
    """Format datetime for display."""
    if format_string:
        return dt.strftime(format_string)

    # Default format: "Jan 15, 2024 at 2:30 PM"
    return dt.strftime("%b %d, %Y at %I:%M %p")

def format_duration(seconds: int) -> str:
    """Format duration in human-readable format."""
    if seconds < 60:
        return f"{seconds} seconds"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} minute{'s' if minutes != 1 else ''}"
    elif seconds < 86400:
        hours = seconds // 3600
        return f"{hours} hour{'s' if hours != 1 else ''}"
    else:
        days = seconds // 86400
        return f"{days} day{'s' if days != 1 else ''}"
```

2. **Number Formatting**:
```python
def format_file_size(bytes: int) -> str:
    """Format file size in human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes < 1024.0:
            return f"{bytes".1f"} {unit}"
        bytes /= 1024.0
    return f"{bytes".1f"} PB"

def format_percentage(value: float, decimals: int = 1) -> str:
    """Format percentage with specified decimal places."""
    return f"{value".{decimals}f"}%"
```

3. **Text Formatting**:
```python
def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to specified length."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix

def format_list(items: List[str], conjunction: str = "and") -> str:
    """Format list of items as human-readable string."""
    if not items:
        return ""
    elif len(items) == 1:
        return items[0]
    elif len(items) == 2:
        return f"{items[0]} {conjunction} {items[1]}"
    else:
        return ", ".join(items[:-1]) + f", {conjunction} {items[-1]}"
```

## Security Utilities

### Password and Token Management

1. **Password Security**:
```python
def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def generate_password_reset_token(user_id: UUID) -> str:
    """Generate secure password reset token."""
    token_data = {
        "user_id": str(user_id),
        "type": "password_reset",
        "exp": datetime.utcnow() + timedelta(hours=1),
        "iat": datetime.utcnow()
    }
    return jwt.encode(token_data, settings.secret_key, algorithm="HS256")
```

2. **Token Generation**:
```python
def generate_secure_token(length: int = 32) -> str:
    """Generate cryptographically secure random token."""
    return secrets.token_urlsafe(length)

def generate_api_key() -> str:
    """Generate API key for external integrations."""
    # Format: curr_api_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    prefix = "curr_api_"
    random_part = secrets.token_hex(32)
    return f"{prefix}{random_part}"
```

3. **Data Masking**:
```python
def mask_email(email: str) -> str:
    """Mask email address for display."""
    if not email or '@' not in email:
        return email

    username, domain = email.split('@', 1)
    if len(username) <= 2:
        return f"{username}@{domain}"
    else:
        return f"{username[0]}{'*' * (len(username) - 2)}{username[-1]}@{domain}"

def mask_sensitive_data(data: Dict[str, Any], sensitive_fields: List[str] = None) -> Dict[str, Any]:
    """Mask sensitive fields in data dictionary."""
    if sensitive_fields is None:
        sensitive_fields = ['password', 'token', 'secret', 'key', 'api_key']

    masked = data.copy()
    for field in sensitive_fields:
        if field in masked:
            masked[field] = "****"

    return masked
```

## File Handling Utilities

### File Upload and Validation

1. **File Type Validation**:
```python
def validate_file_type(file_path: str, allowed_types: List[str]) -> bool:
    """Validate file type against allowed types."""
    if not os.path.exists(file_path):
        return False

    # Check file extension
    file_ext = os.path.splitext(file_path)[1].lower()
    if file_ext not in allowed_types:
        return False

    # Check MIME type
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type:
        mime_category = mime_type.split('/')[0]
        if mime_category == 'image' and 'image' not in allowed_types:
            return False

    return True

def get_file_info(file_path: str) -> Dict[str, Any]:
    """Get comprehensive file information."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    stat = os.stat(file_path)
    mime_type, _ = mimetypes.guess_type(file_path)

    return {
        "path": file_path,
        "name": os.path.basename(file_path),
        "size": stat.st_size,
        "size_formatted": format_file_size(stat.st_size),
        "mime_type": mime_type,
        "extension": os.path.splitext(file_path)[1].lower(),
        "created_at": datetime.fromtimestamp(stat.st_ctime),
        "modified_at": datetime.fromtimestamp(stat.st_mtime),
        "is_file": os.path.isfile(file_path),
        "is_directory": os.path.isdir(file_path)
    }
```

2. **Safe File Operations**:
```python
def safe_copy_file(src: str, dst: str, overwrite: bool = False) -> bool:
    """Safely copy file with validation."""
    if not os.path.exists(src):
        return False

    if os.path.exists(dst) and not overwrite:
        return False

    try:
        shutil.copy2(src, dst)
        return True
    except Exception:
        return False

def safe_delete_file(file_path: str) -> bool:
    """Safely delete file with validation."""
    if not os.path.exists(file_path):
        return True  # Already deleted

    if not os.path.isfile(file_path):
        return False  # Don't delete directories

    try:
        os.remove(file_path)
        return True
    except Exception:
        return False
```

3. **Image Processing**:
```python
def resize_image(image_path: str, max_width: int = 800, max_height: int = 600) -> str:
    """Resize image while maintaining aspect ratio."""
    try:
        with Image.open(image_path) as img:
            # Calculate new dimensions
            img_ratio = img.width / img.height
            max_ratio = max_width / max_height

            if img_ratio > max_ratio:
                new_width = max_width
                new_height = int(max_width / img_ratio)
            else:
                new_height = max_height
                new_width = int(max_height * img_ratio)

            # Resize and save
            resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            output_path = f"{os.path.splitext(image_path)[0]}_resized{os.path.splitext(image_path)[1]}"
            resized.save(output_path, optimize=True, quality=85)

            return output_path
    except Exception as e:
        logger.error(f"Failed to resize image {image_path}: {e}")
        return image_path  # Return original on error

def extract_image_metadata(image_path: str) -> Dict[str, Any]:
    """Extract comprehensive metadata from image."""
    try:
        with Image.open(image_path) as img:
            metadata = {
                "width": img.width,
                "height": img.height,
                "mode": img.mode,
                "format": img.format,
                "has_transparency": img.mode in ('RGBA', 'LA', 'P'),
                "color_palette": len(img.getpalette()) if img.getpalette() else None
            }

            # Extract EXIF data if available
            if hasattr(img, '_getexif') and img._getexif():
                exif_data = img._getexif()
                metadata["exif"] = {
                    "make": exif_data.get(271),  # Make
                    "model": exif_data.get(272),  # Model
                    "datetime": exif_data.get(306),  # DateTime
                    "orientation": exif_data.get(274)  # Orientation
                }

            return metadata
    except Exception as e:
        return {"error": str(e)}
```

## Development Patterns

### Validation Pipeline

1. **Multi-Layer Validation**:
```python
def validate_user_input(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Comprehensive input validation pipeline."""
    errors = []

    # Schema validation
    schema_errors = validate_against_schema(data, USER_SCHEMA)
    errors.extend(schema_errors)

    # Business rule validation
    business_errors = validate_business_rules(data)
    errors.extend(business_errors)

    # Security validation
    security_errors = validate_security_constraints(data)
    errors.extend(security_errors)

    return len(errors) == 0, errors

def validate_against_schema(data: Dict[str, Any], schema: Dict) -> List[str]:
    """Validate data against JSON schema."""
    try:
        validate(data, schema)
        return []
    except ValidationError as e:
        return [f"Schema validation failed: {e.message}"]
```

2. **Custom Validators**:
```python
def validate_content_references(content: Dict[str, Any]) -> List[str]:
    """Validate that content references are valid."""
    errors = []

    # Check parent_id exists
    if content.get('parent_id'):
        parent = content_service.get_content(content['parent_id'])
        if not parent:
            errors.append(f"Parent content {content['parent_id']} does not exist")

    # Check author_id exists
    if content.get('author_id'):
        author = user_service.get_user(content['author_id'])
        if not author:
            errors.append(f"Author {content['author_id']} does not exist")

    return errors
```

### Security Utilities

1. **Input Sanitization**:
```python
def sanitize_html(html_content: str) -> str:
    """Sanitize HTML content for safe display."""
    # Remove dangerous tags and attributes
    allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                   'ul', 'ol', 'li', 'blockquote', 'code', 'pre', 'a', 'img']
    allowed_attrs = {'a': ['href'], 'img': ['src', 'alt']}

    return bleach.clean(html_content, tags=allowed_tags, attributes=allowed_attrs)

def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage."""
    # Remove or replace dangerous characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    filename = re.sub(r'\s+', '_', filename)
    filename = filename.strip('_')

    # Ensure reasonable length
    if len(filename) > 255:
        name, ext = os.path.splitext(filename)
        filename = name[:255-len(ext)] + ext

    return filename
```

2. **Rate Limiting Helpers**:
```python
def check_rate_limit(user_id: UUID, action: str, limit: int, window: int) -> bool:
    """Check if user has exceeded rate limit."""
    cache_key = f"rate_limit:{user_id}:{action}"

    # Get current count
    current = redis_client.get(cache_key)
    count = int(current) if current else 0

    if count >= limit:
        return False

    # Increment counter
    redis_client.multi()
    redis_client.incr(cache_key)
    redis_client.expire(cache_key, window)
    redis_client.execute()

    return True

def get_rate_limit_status(user_id: UUID, action: str) -> Dict[str, Any]:
    """Get current rate limit status for user."""
    cache_key = f"rate_limit:{user_id}:{action}"
    current = redis_client.get(cache_key)
    ttl = redis_client.ttl(cache_key)

    return {
        "current_count": int(current) if current else 0,
        "reset_in_seconds": ttl if ttl > 0 else 0,
        "is_limited": int(current) >= RATE_LIMITS.get(action, 100) if current else False
    }
```

## Testing Guidelines

### Unit Testing Utilities

1. **Validation Testing**:
```python
class TestValidators:
    def test_validate_email_valid(self):
        assert validate_email("user@example.com") is True

    def test_validate_email_invalid(self):
        assert validate_email("invalid-email") is False

    def test_validate_email_disposable(self):
        assert validate_email("user@10minutemail.com") is False

    def test_generate_slug(self):
        assert generate_slug("Hello World!") == "hello-world"
        assert generate_slug("Very Long Title That Should Be Truncated") == "very-long-title-that-should-be-truncate"
```

2. **Security Testing**:
```python
class TestSecurity:
    def test_hash_password(self):
        password = "test_password"
        hashed = hash_password(password)

        assert hashed != password
        assert verify_password(password, hashed) is True
        assert verify_password("wrong_password", hashed) is False

    def test_mask_sensitive_data(self):
        data = {
            "username": "john_doe",
            "password": "secret123",
            "api_key": "abc123def456"
        }

        masked = mask_sensitive_data(data)
        assert masked["username"] == "john_doe"
        assert masked["password"] == "****"
        assert masked["api_key"] == "****"
```

3. **File Handling Testing**:
```python
class TestFileHandling:
    def test_validate_file_type_valid(self, tmp_path):
        # Create test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello, World!")

        assert validate_file_type(str(test_file), [".txt"]) is True

    def test_validate_file_type_invalid(self, tmp_path):
        # Create test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello, World!")

        assert validate_file_type(str(test_file), [".jpg"]) is False

    def test_safe_file_operations(self, tmp_path):
        # Create source file
        src_file = tmp_path / "source.txt"
        src_file.write_text("Source content")

        # Test safe copy
        dst_file = tmp_path / "destination.txt"
        assert safe_copy_file(str(src_file), str(dst_file)) is True
        assert dst_file.exists()
```

## Performance Considerations

### Efficient Validation

1. **Lazy Validation**:
```python
def validate_content_efficiently(content: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Perform validation only when necessary."""
    errors = []

    # Quick format checks first
    if not isinstance(content, dict):
        return False, ["Content must be a dictionary"]

    # Validate required fields only
    required_fields = ['title', 'content_type', 'author_id']
    for field in required_fields:
        if field not in content:
            errors.append(f"Missing required field: {field}")

    # Expensive validations only if basic checks pass
    if not errors:
        expensive_errors = perform_expensive_validations(content)
        errors.extend(expensive_errors)

    return len(errors) == 0, errors
```

2. **Caching Validation Results**:
```python
@functools.lru_cache(maxsize=1000)
def validate_content_cached(content_hash: str) -> Tuple[bool, List[str]]:
    """Cache validation results for repeated content."""
    # Implementation...
    return is_valid, errors
```

### Memory-Efficient File Operations

1. **Streaming File Processing**:
```python
def process_large_file(file_path: str, chunk_size: int = 8192) -> Iterator[str]:
    """Process large files in chunks to avoid memory issues."""
    with open(file_path, 'r', encoding='utf-8') as file:
        while True:
            chunk = file.read(chunk_size)
            if not chunk:
                break
            yield chunk

def count_file_lines(file_path: str) -> int:
    """Count lines in file efficiently."""
    count = 0
    with open(file_path, 'rb') as file:
        while True:
            chunk = file.read(8192)
            if not chunk:
                break
            count += chunk.count(b'\n')
    return count
```

2. **Temporary File Management**:
```python
@contextmanager
def temporary_file(suffix: str = "", delete: bool = True) -> str:
    """Context manager for temporary files."""
    fd, path = tempfile.mkstemp(suffix=suffix)
    try:
        os.close(fd)  # Close file descriptor
        yield path
    finally:
        if delete and os.path.exists(path):
            os.unlink(path)

# Usage
with temporary_file(suffix=".txt") as temp_path:
    with open(temp_path, 'w') as f:
        f.write("Temporary content")
    # File is automatically deleted when exiting context
```

## Error Handling

### Comprehensive Error Reporting

1. **Validation Error Details**:
```python
class ValidationErrorDetail(BaseModel):
    """Detailed validation error information."""
    field: str
    value: Any
    rule: str
    message: str
    suggestion: Optional[str] = None

def create_detailed_validation_error(field: str, value: Any, rule: str, message: str) -> ValidationErrorDetail:
    """Create detailed validation error."""
    return ValidationErrorDetail(
        field=field,
        value=str(value)[:100],  # Truncate long values
        rule=rule,
        message=message,
        suggestion=get_suggestion_for_error(field, rule)
    )
```

2. **Security Error Logging**:
```python
def log_security_event(event_type: str, details: Dict[str, Any], severity: str = "medium") -> None:
    """Log security-related events."""
    security_log = {
        "timestamp": datetime.utcnow().isoformat(),
        "event_type": event_type,
        "severity": severity,
        "details": mask_sensitive_data(details),
        "user_agent": get_current_user_agent(),
        "ip_address": get_client_ip()
    }

    # Log to security-specific logger
    security_logger.log(severity.upper(), security_log)
```

## Best Practices

### Input Validation

1. **Defense in Depth**:
   - Validate at multiple layers (client, API, service, database)
   - Use both allow-lists and deny-lists
   - Validate data types, formats, and business rules
   - Sanitize outputs as well as inputs

2. **Fail-Safe Defaults**:
```python
def safe_get_config_value(key: str, default: Any = None) -> Any:
    """Get configuration value with safe defaults."""
    try:
        value = config.get(key, default)
        # Validate the value is of expected type/format
        if not validate_config_value(key, value):
            logger.warning(f"Invalid config value for {key}, using default")
            return default
        return value
    except Exception:
        return default
```

### Security Utilities

1. **Cryptographic Best Practices**:
   - Use established libraries (cryptography, passlib)
   - Generate random keys of sufficient length (32+ bytes)
   - Use appropriate algorithms (bcrypt for passwords, AES for data)
   - Rotate keys regularly

2. **Safe Data Handling**:
```python
def safe_serialize_data(data: Any) -> str:
    """Safely serialize data for storage."""
    # Custom JSON encoder for special types
    def custom_encoder(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, UUID):
            return str(obj)
        if isinstance(obj, BaseModel):
            return obj.model_dump()
        raise TypeError(f"Object of type {type(obj)} is not serializable")

    return json.dumps(data, default=custom_encoder, indent=2)
```

## Extension Points

### Custom Validators

1. **Domain-Specific Validation**:
```python
def validate_educational_content(content: Dict[str, Any]) -> List[str]:
    """Validate educational content specific rules."""
    errors = []

    # Check learning objectives are present
    if not content.get('learning_objectives'):
        errors.append("Learning objectives are required for educational content")

    # Check content is appropriate length
    if content.get('content_body') and len(content['content_body']) < 100:
        errors.append("Content body is too short for educational material")

    # Check for accessibility considerations
    if not has_accessibility_features(content):
        errors.append("Content should include accessibility features")

    return errors
```

2. **Custom Formatters**:
```python
def format_learning_objectives(objectives: List[str]) -> str:
    """Format learning objectives for display."""
    if not objectives:
        return ""

    formatted = []
    for i, obj in enumerate(objectives, 1):
        # Ensure each objective starts with action verb
        if not obj[0].isupper():
            obj = obj[0].upper() + obj[1:]

        # Add numbering and formatting
        formatted.append(f"{i}. {obj}")

    return "\n".join(formatted)

def format_assessment_results(results: Dict[str, Any]) -> str:
    """Format assessment results for reporting."""
    score = results.get('score', 0)
    max_score = results.get('max_score', 100)
    percentage = (score / max_score) * 100

    return f"""
Assessment Results:
Score: {score}/{max_score} ({percentage".1f"}%)
Time Taken: {format_duration(results.get('time_taken', 0))}
Completed At: {format_datetime(results.get('completed_at'))}
"""
```

## Questions to Ask

Before adding new utility functions:

1. **Necessity**: Is this functionality needed across multiple modules?
2. **Performance**: Will this function be called frequently? Is it optimized?
3. **Security**: Does this function handle sensitive data? Is it secure?
4. **Testing**: Are there comprehensive tests for edge cases and error conditions?
5. **Documentation**: Is the function well-documented with examples?
6. **Consistency**: Does this follow existing patterns in the codebase?

## Resources

### Internal Documentation
- `README.md`: Module overview and utility categories
- `tests/test_tools.py`: Comprehensive utility tests

### External References
- [Python Security Best Practices](https://docs.python.org/3/library/security.html)
- [Pydantic Validation](https://docs.pydantic.dev/)
- [Bleach HTML Sanitization](https://bleach.readthedocs.io/)
- [Passlib Password Hashing](https://passlib.readthedocs.io/)

---

**Last Updated**: September 2025

**For Questions**: Check the utility tests for usage examples and edge cases


