# Tools Module

The tools module contains utility functions and helper classes.

## Components

- `validators.py`: Input validation utilities
- `formatters.py`: Data formatting utilities
- `security.py`: Security and encryption utilities
- `file_handling.py`: File operation utilities

## Features

- Email and URL validation
- Date/time formatting
- Security token generation
- File upload and validation
- Data sanitization
- Slug generation

## Usage

```python
from curriculum.tools import validate_email, format_datetime, generate_token

# Validate email
is_valid = validate_email("user@example.com")

# Format datetime
formatted = format_datetime(datetime.now())

# Generate secure token
token = generate_token(32)
```

## Testing

```bash
pytest tests/unit/test_tools.py
```

