# Content Module

The content module handles all aspects of educational content management, including creation, versioning, rendering, and metadata management.

## Services

- `ContentService`: Core content CRUD operations
- `MetadataService`: Dublin Core and LRMI metadata management
- `RenderingService`: Multi-format content rendering
- `VersionControlService`: Git-based content versioning

## Features

- Multi-format content support (Markdown, HTML, LaTeX, PDF, SCORM, xAPI)
- Hierarchical content organization
- Content lifecycle management
- Full-text search integration
- Tag and taxonomy management

## Usage

```python
from curriculum.content import ContentService, RenderingService

content_service = ContentService()
rendering_service = RenderingService()

# Create content
content = content_service.create_content(
    title="Python Tutorial",
    content_type="lesson",
    format="markdown",
    author_id=user_id,
)

# Render content
rendered = rendering_service.render_content(content, "html")
```

## Testing

```bash
pytest tests/test_content/
```

