# AI Agents Guide - Content Module

## Overview

The content module handles all aspects of educational content management, from creation to publication and distribution.

## Module Structure

```
content/
├── content.py      # Content CRUD operations
├── metadata.py     # Metadata management
├── rendering.py    # Multi-format rendering
├── version_control.py # Version control
├── __init__.py     # Module exports
├── README.md       # Module documentation
└── AGENTS.md       # This file
```

## Development Guidelines

### When Working on Content Services

1. **Always use the Content model** from core:
```python
from curriculum.core import Content, ContentStatus, ContentFormat, ContentType

content = Content(
    title="Lesson Title",
    content_type=ContentType.LESSON,
    format=ContentFormat.MARKDOWN,
    author_id=user_id,
)
```

2. **Implement proper status transitions**:
```python
def publish_content(self, content_id: UUID) -> Optional[Content]:
    content = self.get_content(content_id)
    if content and content.status == ContentStatus.APPROVED:
        content.transition_to(ContentStatus.PUBLISHED)
        return content
    return None
```

3. **Use version control for changes**:
```python
def update_content(self, content_id: UUID, **updates) -> Optional[Content]:
    content = self.get_content(content_id)
    if not content:
        return None

    # Create version before updating
    self.version_control.create_version(content)

    # Apply updates
    for field, value in updates.items():
        setattr(content, field, value)

    return content
```

### Testing Requirements

- **Test all CRUD operations**
- **Test status transitions**
- **Test search functionality**
- **Test content relationships**
- **Test version control**

Example test:
```python
def test_content_lifecycle():
    # Create content
    content = content_service.create_content(
        title="Test Lesson",
        content_type=ContentType.LESSON,
        format=ContentFormat.MARKDOWN,
        author_id=user_id,
    )

    # Test status transitions
    content.transition_to(ContentStatus.INTERNAL_REVIEW)
    assert content.status == ContentStatus.INTERNAL_REVIEW

    # Test publishing
    content.status = ContentStatus.APPROVED
    published = content_service.publish_content(content.id)
    assert published.status == ContentStatus.PUBLISHED
```

### Content Rendering

1. **Support multiple formats**:
```python
def render_content(self, content: Content, target_format: str) -> Dict[str, Any]:
    if content.format == ContentFormat.MARKDOWN:
        return self._render_markdown(content, target_format)
    elif content.format == ContentFormat.HTML:
        return self._render_html(content, target_format)
```

2. **Handle format conversion**:
```python
def _render_markdown(self, content: Content, target_format: str) -> Dict[str, Any]:
    if target_format == "html":
        html_output = markdown.convert(content.content_body)
        return {"format": "html", "content": html_output}
```

### Version Control Integration

1. **Create versions on significant changes**:
```python
def update_content(self, content_id: UUID, **updates) -> Optional[Content]:
    content = self.get_content(content_id)

    # Create version snapshot
    version = self.version_control.create_version(content, "Content updated")

    # Apply changes
    for field, value in updates.items():
        setattr(content, field, value)

    return content
```

### Metadata Management

1. **Use Dublin Core standards**:
```python
metadata = MetadataService()
dublin_core = DublinCore(
    title=content.title,
    creator=[content.author_id],
    type=ResourceType.TEXT,
)
```

2. **Add LRMI extensions for educational content**:
```python
lrmi = LRMIMetadata(
    educational_use=[EducationalUse.LECTURE],
    learning_resource_type=[LearningResourceType.LESSON],
    typical_age_range="18-25",
)
```

### Search Integration

1. **Index content for search**:
```python
async def index_content(self, content: Content) -> bool:
    await self.search_service.index_content(content)
    return True
```

### Performance Considerations

- **Lazy loading** for related content
- **Caching** for frequently accessed content
- **Pagination** for large result sets
- **Background processing** for heavy operations

### Common Patterns

#### Content Hierarchy
```python
def get_children(self, parent_id: UUID) -> List[Content]:
    return [
        content for content in self._content_store.values()
        if content.parent_id == parent_id and not content.is_deleted
    ]
```

#### Content Validation
```python
def validate_content(self, content: Content) -> Dict[str, Any]:
    issues = []
    if not content.title or len(content.title) < 3:
        issues.append("Title too short")
    return {"valid": len(issues) == 0, "issues": issues}
```

### Extension Points

- Custom content types
- Additional export formats
- Custom metadata fields
- Advanced search capabilities
- Content recommendation algorithms

