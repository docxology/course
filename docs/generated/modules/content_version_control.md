# Module: content.version_control

**File:** `src/curriculum/content/version_control.py`

## Description

Version control service for content.

## Classes

### `VersionControlService`

Service for managing content versions.

**Methods:** 10


**Method List:**

- `__init__`: Initialize version control service.

- `create_version`: Create a new version snapshot of content.

- `get_version`: Get a specific version.

- `get_content_versions`: Get all versions for specific content.

- `get_latest_version`: Get the latest version of content.

- `restore_version`: Restore content to a specific version.

- `compare_versions`: Compare two versions (simplified).

- `get_version_count`: Get count of versions for content.

- `delete_version`: Delete a version (soft delete).

- `increment_version`: Increment semantic version number.
