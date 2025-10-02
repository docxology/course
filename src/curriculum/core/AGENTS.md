# AI Agents Guide - Core Module

## Overview

The core module contains fundamental models, base classes, and essential data structures used throughout the Curriculum Repository System.

## Module Structure

```
core/
├── base.py         # Base classes and mixins
├── content.py      # Core content models
├── user.py         # User models
├── metadata.py     # Metadata models
└── README.md       # Module documentation
```

## Development Guidelines

### When Working on Core Models

1. **Always inherit from BaseEntity** for all domain models:
```python
class Content(BaseEntity):
    title: str = Field(min_length=1, max_length=500)
    # ... other fields
```

2. **Use appropriate mixins**:
   - `UUIDMixin` for primary keys
   - `TimestampMixin` for created_at/updated_at
   - `SoftDeleteMixin` for soft delete functionality

3. **Follow naming conventions**:
   - Classes: PascalCase
   - Methods: snake_case
   - Constants: UPPER_SNAKE_CASE
   - Private methods: _snake_case

4. **Use Pydantic validation**:
```python
class ContentStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"

class Content(BaseEntity):
    status: ContentStatus = ContentStatus.DRAFT
```

### Testing Requirements

- **100% test coverage** for all core functionality
- **Test both success and failure cases**
- **Test edge cases and boundary conditions**
- **Test inheritance and mixin behavior**

Example test:
```python
def test_content_creation():
    content = Content(
        title="Test Content",
        content_type=ContentType.LESSON,
        format=ContentFormat.MARKDOWN,
        author_id=uuid4(),
    )
    assert content.status == ContentStatus.DRAFT
    assert isinstance(content.id, UUID)
```

### Adding New Models

1. Create model in appropriate `core/*.py` file
2. Inherit from `BaseEntity`
3. Add comprehensive type hints and validation
4. Add to `core/__init__.py`
5. Write tests in `tests/core/`

### Common Patterns

#### Entity Relationships
```python
class Content(BaseEntity):
    parent_id: Optional[UUID] = None
    author_id: UUID
    contributors: List[UUID] = Field(default_factory=list)
```

#### Status Transitions
```python
def can_transition_to(self, new_status: ContentStatus) -> bool:
    transitions = {
        ContentStatus.DRAFT: [ContentStatus.INTERNAL_REVIEW],
        ContentStatus.INTERNAL_REVIEW: [ContentStatus.DRAFT, ContentStatus.EXTERNAL_REVIEW],
    }
    return new_status in transitions.get(self.status, [])
```

#### Validation
```python
class Content(BaseEntity):
    title: str = Field(min_length=1, max_length=500)
    tags: List[str] = Field(default_factory=list)
    custom_metadata: Dict[str, Any] = Field(default_factory=dict)
```

### Performance Considerations

- Core models should be lightweight
- Use Pydantic's built-in validation
- Avoid complex relationships in core models
- Consider serialization performance for API responses

### Security Considerations

- Use Pydantic validation for input sanitization
- Implement proper access control in services
- Consider data exposure in API responses

### Extension Points

- Custom metadata fields
- Additional content types
- Custom validation rules
- New base mixins for specific domains

