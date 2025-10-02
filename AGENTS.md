# AI Agents & Development Guide

## Purpose

This document serves as a comprehensive guide for AI coding agents (like Claude, GPT-4, etc.) working on the Curriculum Repository System. It provides context, conventions, and guidelines for effective collaboration on this codebase.

## Project Context

### What This Project Does

The Curriculum Repository System is a full-featured educational content management platform that:
- Manages educational content across multiple formats (Markdown, HTML, LaTeX, SCORM, etc.)
- Implements educational metadata standards (Dublin Core, LRMI)
- Provides comprehensive learning analytics (xAPI-compliant)
- Supports assessment creation and auto-grading
- Enables version control for educational content
- Renders content in multiple output formats

### Target Users

1. **Content Creators**: Educators creating course materials
2. **Students**: Learners consuming educational content
3. **Instructors**: Teachers managing courses and grading
4. **Administrators**: System managers and analysts

## Architecture Overview

### Layer Structure

```
Presentation Layer (API) → Service Layer → Model Layer → Data Layer
```

1. **Models**: Pydantic models defining data structures
2. **Services**: Business logic and orchestration
3. **API**: FastAPI endpoints (to be implemented)
4. **Utils**: Helper functions and utilities

### Key Design Principles

1. **Separation of Concerns**: Each module has a single, well-defined responsibility
2. **Dependency Injection**: Services receive dependencies via constructor
3. **Type Safety**: Full type hints throughout the codebase
4. **Test-Driven Development**: Write tests before implementation
5. **No Mock Data**: Use real data structures in tests
6. **Immutability Preference**: Models use Pydantic's validation

## Code Conventions

### Naming Conventions

- **Classes**: PascalCase (`ContentService`, `User`)
- **Functions/Methods**: snake_case (`create_content`, `get_user`)
- **Constants**: UPPER_SNAKE_CASE (`MAX_UPLOAD_SIZE`)
- **Private members**: Leading underscore (`_internal_cache`)
- **Type variables**: PascalCase with T suffix (`ModelT`)

### Modular File Organization

The system is organized into focused modules, each with its own directory:

```
src/curriculum/
├── core/                # Base classes and fundamental models
│   ├── base.py         # Base entities and mixins
│   ├── content.py      # Core content models
│   ├── user.py         # User models
│   ├── metadata.py     # Metadata models
│   ├── __init__.py     # Module exports
│   ├── README.md       # Module documentation
│   └── AGENTS.md       # Development guide
├── content/             # Content management services
│   ├── content.py      # Content CRUD operations
│   ├── metadata.py     # Metadata management
│   ├── rendering.py    # Multi-format rendering
│   ├── version_control.py # Version control
│   └── ...
├── learning/            # Learning and assessment services
│   ├── analytics.py    # Learning analytics
│   ├── assessment.py  # Assessment management
│   ├── progress.py     # Progress tracking
│   └── ...
├── users/              # User management and authentication
│   ├── user.py        # User service
│   ├── authentication.py # Auth service
│   └── ...
├── ai/                 # AI-powered features
│   ├── ai_features.py # Intelligent tutoring
│   ├── content_creation.py # AI content generation
│   ├── research.py    # Research tools
│   └── ...
├── communication/      # Communication features
│   ├── communication.py # Forums and messaging
│   ├── collaboration.py # Group work
│   └── ...
├── accessibility/      # Accessibility features
│   ├── accessibility.py # WCAG compliance
│   └── ...
├── mobile/             # Mobile and offline features
│   ├── mobile.py      # Mobile optimization
│   ├── offline.py     # Offline capabilities
│   └── ...
├── integration/        # External integrations
│   ├── integration.py # LMS integration
│   ├── distribution.py # Content distribution
│   ├── export.py      # Export formats
│   ├── gamification.py # Gamification
│   └── ...
├── search/             # Search and discovery
│   ├── search.py      # Elasticsearch integration
│   ├── visualization.py # Interactive charts
│   ├── website.py     # Course websites
│   └── ...
├── db/                 # Database layer
│   ├── base.py        # Database interface
│   ├── mongodb.py     # MongoDB adapter
│   ├── postgresql.py  # PostgreSQL adapter
│   └── ...
├── routes/             # API endpoints
│   ├── main.py        # FastAPI application
│   ├── content.py     # Content endpoints
│   ├── users.py       # User endpoints
│   └── ...
├── tools/              # Utility functions
│   ├── validators.py  # Input validation
│   ├── formatters.py  # Data formatting
│   ├── security.py    # Security utilities
│   ├── file_handling.py # File operations
│   └── ...
├── config.py          # Configuration management
├── cli.py             # Command-line interface
├── orchestration.py   # Service coordination layer
└── __init__.py        # Main package exports

tests/                   # Comprehensive test suite
├── core/               # Core module tests
├── content/            # Content module tests
├── learning/           # Learning module tests
├── ai/                 # AI module tests
├── communication/      # Communication tests
├── accessibility/      # Accessibility tests
├── mobile/             # Mobile tests
├── integration/        # Integration tests
├── search/             # Search tests
├── conftest.py         # Test configuration
└── test_integration.py # End-to-end tests
```

### Import Order (isort)

1. Standard library imports
2. Third-party imports
3. Local application imports

Example:
```python
from datetime import datetime
from typing import List, Optional

from pydantic import Field

from curriculum.core import BaseEntity
from curriculum.content import ContentService
from curriculum.learning import AssessmentService
```

## Working with Modular Structure

### Module Organization

Each module is self-contained with its own:
- **Services**: Business logic for the domain
- **Models**: Data structures specific to the module
- **Tests**: Comprehensive test coverage
- **Documentation**: README and AGENTS.md files
- **Dependencies**: Clear import relationships

### Development Workflow

1. **Identify the module** for your changes
2. **Read the module's AGENTS.md** for specific guidelines
3. **Follow module-specific patterns** and conventions
4. **Write tests** in the module's test directory
5. **Update module documentation** as needed

### Cross-Module Communication

Use the orchestration layer for complex interactions:

```python
from curriculum.orchestration import CurriculumOrchestrator

orchestrator = CurriculumOrchestrator()

# Complex workflow involving multiple modules
result = await orchestrator.create_complete_learning_experience(
    user_id=user_id,
    course_title="Python Programming",
    instructor_id=instructor_id,
)
```

### Adding New Modules

1. **Create module directory** under `src/curriculum/`
2. **Add core services** and models
3. **Create `__init__.py`** with exports
4. **Add README.md** and **AGENTS.md**
5. **Create test directory** under `tests/`
6. **Update main imports** in `src/curriculum/__init__.py`

## Model Design Patterns

### Base Entity Pattern

All domain models inherit from `BaseEntity`:

```python
class BaseEntity(UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """Base entity with UUID, timestamps, and soft delete."""
```

Provides:
- `id`: UUID primary key
- `created_at`, `updated_at`: Timestamps
- `is_deleted`, `deleted_at`: Soft delete functionality

### Enums for State

Use string enums for states and types:

```python
class ContentStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
```

### Validation in Models

Leverage Pydantic's validation:

```python
class Content(BaseEntity):
    title: str = Field(min_length=1, max_length=500)
    tags: List[str] = Field(default_factory=list)
```

## Service Layer Patterns

### In-Memory Storage Pattern

Current services use dictionaries for storage (production would use databases):

```python
class ContentService:
    def __init__(self) -> None:
        self._content_store: dict[UUID, Content] = {}
```

### Method Signatures

Return `Optional[Model]` when retrieval might fail:

```python
def get_content(self, content_id: UUID) -> Optional[Content]:
    """Retrieve content by ID."""
    return self._content_store.get(content_id)
```

Return boolean for success/failure operations:

```python
def delete_content(self, content_id: UUID) -> bool:
    """Soft delete content."""
```

## Testing Guidelines

### Test Structure

```python
class TestContentService:
    """Tests for ContentService."""
    
    def test_create_content(self, content_service):
        """Test creating content."""
        # Arrange
        author_id = uuid4()
        
        # Act
        content = content_service.create_content(...)
        
        # Assert
        assert content is not None
```

### Fixtures

Use pytest fixtures defined in `conftest.py`:

```python
@pytest.fixture
def sample_user(user_service):
    """Create a sample user."""
    return user_service.create_user(...)
```

### Test Coverage Requirements

- Minimum 80% overall coverage
- 100% coverage for critical paths (auth, grading)
- Test both success and failure cases
- Test edge cases and boundary conditions

## Common Tasks Guide

### Adding a New Model

1. Create model in appropriate `models/*.py` file
2. Inherit from `BaseEntity`
3. Add type hints and Field validators
4. Add to `models/__init__.py`
5. Write model tests in `tests/test_models.py`

### Adding a New Service

1. Create service in `services/*.py`
2. Add `__init__` with storage initialization
3. Implement CRUD methods
4. Add to `services/__init__.py`
5. Create fixture in `tests/conftest.py`
6. Write service tests in `tests/test_*_service.py`

### Adding a New Feature

1. Write tests first (TDD)
2. Implement minimum code to pass tests
3. Refactor for clarity
4. Update documentation
5. Ensure type hints are complete
6. Run code quality checks

## Error Handling

### Validation Errors

Use Pydantic's built-in validation:

```python
from pydantic import ValidationError

try:
    user = User(email="invalid")
except ValidationError as e:
    # Handle validation error
```

### Business Logic Errors

Return `None` or raise specific exceptions:

```python
def publish_content(self, content_id: UUID) -> Optional[Content]:
    content = self.get_content(content_id)
    if not content:
        return None
    
    if content.status != ContentStatus.APPROVED:
        return None  # Can't publish unapproved content
```

## Configuration

### Environment Variables

All configuration via `.env` file and `Settings` class:

```python
from curriculum.config import settings

database_url = settings.database_url
```

### Feature Flags

Use settings for feature toggles:

```python
if settings.enable_versioning:
    # Version control logic
```

## Educational Standards Integration

### Dublin Core Metadata

15-element schema for resource description:
- title, creator, subject, description, publisher
- contributor, date, type, format, identifier
- source, language, relation, coverage, rights

### LRMI Extensions

Educational-specific metadata:
- educationalAlignment, educationalUse
- learningResourceType, interactivityType
- typicalAgeRange, timeRequired

### xAPI (Experience API)

Learning activity tracking:
- Actor (who)
- Verb (did what)
- Object (to what)
- Context, Result, Timestamp

## Performance Considerations

### Current Implementation

- In-memory storage for development/testing
- Synchronous operations
- No caching layer

### Production Recommendations

1. Replace in-memory stores with databases:
   - PostgreSQL for relational data
   - MongoDB for content documents
   - Redis for caching

2. Add async/await support:
   - AsyncIO for I/O operations
   - Background tasks for heavy processing

3. Implement caching:
   - Redis for frequently accessed data
   - CDN for static content

## Security Best Practices

### Password Handling

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"])
hashed = pwd_context.hash(password)
```

### JWT Tokens

```python
from jose import jwt

token = jwt.encode(payload, secret_key, algorithm="HS256")
```

### Input Validation

Always validate via Pydantic models:

```python
class CreateContentRequest(BaseModel):
    title: str = Field(min_length=1, max_length=500)
```

## Debugging Tips

### Common Issues

1. **Import Errors**: Check `__init__.py` exports
2. **Type Errors**: Run `mypy src/`
3. **Test Failures**: Run with `-v` for verbose output
4. **Validation Errors**: Check Field constraints

### Useful Commands

```bash
# Run specific test
pytest tests/test_content_service.py::TestContentService::test_create_content -v

# Check types
mypy src/curriculum/services/content.py

# Format and check
black src/ && flake8 src/
```

## Future Enhancements

### Planned Features

1. **API Layer**: FastAPI REST endpoints
2. **Database Integration**: SQLAlchemy + MongoDB
3. **Search**: Elasticsearch integration
4. **Real-time**: WebSocket support
5. **File Upload**: S3/CDN integration
6. **Email**: Notification system
7. **Async**: Full async/await support

### Extension Points

- Custom authentication backends
- Additional content formats
- External LMS integrations
- Custom analytics processors
- Alternative rendering engines

## Best Practices for AI Agents

### When Modifying Code

1. **Read existing code first**: Understand patterns and conventions
2. **Follow TDD**: Write tests before implementation
3. **Maintain type safety**: Add type hints to all new code
4. **Update tests**: Ensure all tests pass after changes
5. **Document changes**: Update docstrings and comments
6. **Check quality**: Run black, flake8, mypy

### When Adding Features

1. **Check for existing patterns**: Follow established conventions
2. **Consider abstractions**: Use base classes and mixins
3. **Think about testing**: Design for testability
4. **Plan for production**: Consider scalability
5. **Update documentation**: Keep README and this file current

### When Debugging

1. **Read error messages carefully**: They usually point to the issue
2. **Check type hints**: MyPy catches many bugs
3. **Review tests**: Tests document expected behavior
4. **Use breakpoints**: Python debugger (pdb) is helpful
5. **Check logs**: Add logging for complex operations

## Questions to Ask

Before implementing a feature:

1. Does this follow existing patterns?
2. Are there type hints for all parameters and returns?
3. Are there tests covering success and failure cases?
4. Is the code documented with clear docstrings?
5. Does this integrate with existing standards (Dublin Core, xAPI)?
6. Is error handling appropriate?
7. Are configuration values using settings?

## Resources

### Internal Documentation

- `README.md`: Project overview and setup
- `draft/curriculum_repository_specification.md`: Detailed architecture spec
- Code docstrings: Inline documentation

### External Standards

- [Dublin Core](https://www.dublincore.org/)
- [LRMI](https://www.lrmi.net/)
- [xAPI](https://xapi.com/)
- [SCORM](https://scorm.com/)

### Python Libraries

- [Pydantic](https://docs.pydantic.dev/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Pytest](https://docs.pytest.org/)

---

**Last Updated**: September 2025

**For Questions**: Open an issue on GitHub
