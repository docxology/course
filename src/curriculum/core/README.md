# Core Module

The core module contains fundamental models, base classes, and essential data structures used throughout the Curriculum Repository System.

## Components

### Base Classes
- `BaseEntity`: Base entity with UUID, timestamps, and soft delete
- `TimestampMixin`: Timestamp functionality
- `UUIDMixin`: UUID primary key functionality
- `SoftDeleteMixin`: Soft delete functionality
- `PagedResponse`: Paginated response wrapper

### Core Models
- `Content`: Educational content entity
- `User`: User management and authentication
- `Metadata`: Dublin Core and LRMI metadata
- `Analytics`: Learning event tracking

## Usage

```python
from curriculum.core import BaseEntity, Content, User

# Create content
content = Content(
    title="Python Basics",
    content_type="lesson",
    format="markdown",
    author_id=user_id,
)
```

## Testing

```bash
pytest tests/unit/test_core.py
pytest tests/integration/test_learning.py  # Core models used in integration tests
```

