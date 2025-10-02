# Module: routes.content

**File:** `src/curriculum/routes/content.py`

## Description

Content API routes.

## Classes

### `CreateContentRequest`

Request model for creating content.

**Inherits from:** BaseModel

**Methods:** 0

### `UpdateContentRequest`

Request model for updating content.

**Inherits from:** BaseModel

**Methods:** 0

### `ContentResponse`

Response model for content.

**Inherits from:** BaseModel

**Methods:** 0

## Functions

### `create_content`

Create new content.

**Parameters:**

- `request: CreateContentRequest`

### `get_content`

Get content by ID.

**Parameters:**

- `content_id: UUID`

### `update_content`

Update content.

**Parameters:**

- `content_id: UUID`

- `request: UpdateContentRequest`

- `content_id_path: UUID`

### `delete_content`

Soft delete content.

**Parameters:**

- `content_id: UUID`

### `publish_content`

Publish content.

**Parameters:**

- `content_id: UUID`

### `change_content_status`

Change content status.

**Parameters:**

- `content_id: UUID`

- `new_status: ContentStatus`

- `content_id_path: UUID`

### `list_content`

List content with pagination and filtering.

**Parameters:**

- `page: int`

- `page_size: int`

- `status: Optional[ContentStatus]`

- `author_id: Optional[UUID]`

- `search: Optional[str]`

### `render_content`

Render content in specified format.

**Parameters:**

- `content_id: UUID`

- `format: str`

### `download_content`

Download content (increment download count).

**Parameters:**

- `content_id: UUID`

### `get_content_versions`

Get all versions of content.

**Parameters:**

- `content_id: UUID`

### `get_content_children`

Get child content items.

**Parameters:**

- `content_id: UUID`

### `_content_to_response`

Convert Content model to response model.

**Parameters:**

- `content: Content`
