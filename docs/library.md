# Library walkthrough

Create a Markdown lesson using the content service. Run this example from
the installed checkout with `uv run --no-sync python`.

```python
from uuid import uuid4

from curriculum.content.content import ContentService
from curriculum.core.content import ContentFormat, ContentStatus, ContentType

service = ContentService()
lesson = service.create_content(
    title="Reading a bar chart",
    content_type=ContentType.LESSON,
    format=ContentFormat.MARKDOWN,
    author_id=uuid4(),
    content_body="Compare the lengths of the bars.",
)

assert lesson.status is ContentStatus.DRAFT
assert service.get_content(lesson.id) == lesson
assert [entry.id for entry in service.list_content().items] == [lesson.id]
```

Use the returned UUID for later operations on the same service instance.
The [content module](reference/modules/content.md) owns updates,
revision history, hierarchy and publication state. The [core
module](reference/modules/core.md) owns content metadata and the
content-type, format and lifecycle enums.

The content format is metadata on the record. Converting a document
calls a rendering service and may require a format-specific tool such as
Pandoc. The [architecture guide](architecture.md) describes storage and
the [module reference](reference/modules/index.md) maps the remaining
capabilities.
