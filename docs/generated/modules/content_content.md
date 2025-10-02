# Module: content.content

**File:** `src/curriculum/content/content.py`

## Description

Content management service.

## Classes

### `ContentService`

Service for managing educational content.

**Methods:** 15


**Method List:**

- `__init__`: Initialize content service.

- `create_content`: Create new content.

- `get_content`: Retrieve content by ID.

- `update_content`: Update content fields.

- `delete_content`: Soft delete content.

- `publish_content`: Publish content (change status to published).

- `transition_status`: Transition content to a new status.

- `list_content`: List content with pagination and filtering.

- `search_content`: Search content by title and description.

- `add_tag`: Add a tag to content.

- `remove_tag`: Remove a tag from content.

- `get_children`: Get all child content of a parent.

- `increment_views`: Increment view count for content.

- `increment_downloads`: Increment download count for content.

- `get_content_count`: Get total count of non-deleted content.
