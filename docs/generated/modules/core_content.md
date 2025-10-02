# Module: core.content

**File:** `src/curriculum/core/content.py`

## Description

Content models for educational materials.

## Classes

### `ContentStatus`

Content lifecycle status.

**Inherits from:** str, Enum

**Methods:** 0

### `ContentFormat`

Supported content formats.

**Inherits from:** str, Enum

**Methods:** 0

### `ContentType`

Type of educational content.

**Inherits from:** str, Enum

**Methods:** 0

### `Content`

Educational content entity.

**Inherits from:** BaseEntity

**Methods:** 4


**Method List:**

- `increment_views`: Increment view count.

- `increment_downloads`: Increment download count.

- `can_transition_to`: Check if content can transition to new status.

- `transition_to`: Transition content to new status.

### `ContentVersion`

Version snapshot of content.

**Inherits from:** BaseEntity

**Methods:** 1


**Method List:**

- `create_from_content`: Create a version snapshot from content.

### `ContentRelation`

Relationship between content items.

**Inherits from:** BaseEntity

**Methods:** 0
