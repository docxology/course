"""Version control service for content."""

from typing import List, Optional
from uuid import UUID

from curriculum.core.content import Content, ContentVersion


class VersionControlService:
    """Service for managing content versions."""

    def __init__(self) -> None:
        """Initialize version control service."""
        self._versions: dict[UUID, ContentVersion] = {}
        self._content_versions: dict[UUID, List[UUID]] = {}  # content_id -> version_ids

    def create_version(self, content: Content, change_log: Optional[str] = None) -> ContentVersion:
        """Create a new version snapshot of content.

        Args:
            content: Content instance to version
            change_log: Optional description of changes

        Returns:
            Created ContentVersion instance
        """
        version = ContentVersion.create_from_content(content, change_log)
        self._versions[version.id] = version

        if content.id not in self._content_versions:
            self._content_versions[content.id] = []

        self._content_versions[content.id].append(version.id)

        # Update content's version history
        if version.id not in content.version_history:
            content.version_history.append(version.id)

        return version

    def get_version(self, version_id: UUID) -> Optional[ContentVersion]:
        """Get a specific version.

        Args:
            version_id: UUID of the version to retrieve

        Returns:
            ContentVersion instance if found, None otherwise
        """
        return self._versions.get(version_id)

    def get_content_versions(self, content_id: UUID) -> List[ContentVersion]:
        """Get all versions for specific content.

        Args:
            content_id: UUID of the content

        Returns:
            List of ContentVersion instances sorted by committed_at descending
        """
        version_ids = self._content_versions.get(content_id, [])
        versions = [self._versions[vid] for vid in version_ids if vid in self._versions]

        # Sort by committed_at descending
        versions.sort(key=lambda v: v.committed_at, reverse=True)
        return versions

    def get_latest_version(self, content_id: UUID) -> Optional[ContentVersion]:
        """Get the latest version of content.

        Args:
            content_id: UUID of the content

        Returns:
            Latest ContentVersion instance if found, None otherwise
        """
        versions = self.get_content_versions(content_id)
        return versions[0] if versions else None

    def restore_version(self, content: Content, version_id: UUID) -> Optional[Content]:
        """Restore content to a specific version.

        Args:
            content: Content instance to restore
            version_id: UUID of the version to restore to

        Returns:
            Restored Content instance if successful, None if version not found or doesn't match content
        """
        version = self.get_version(version_id)
        if not version or version.content_id != content.id:
            return None

        # Restore content from snapshot
        content.title = version.title
        content.description = version.description
        content.content_body = version.content_body
        content.content_url = version.content_url
        content.file_path = version.file_path
        content.update_timestamp()

        return content

    def compare_versions(self, version_id_1: UUID, version_id_2: UUID) -> Optional[dict]:
        """Compare two versions (simplified).

        Args:
            version_id_1: UUID of the first version
            version_id_2: UUID of the second version

        Returns:
            Dictionary containing comparison results with differences and is_identical flag,
            None if either version not found
        """
        v1 = self.get_version(version_id_1)
        v2 = self.get_version(version_id_2)

        if not v1 or not v2:
            return None

        differences = []

        if v1.title != v2.title:
            differences.append({"field": "title", "v1": v1.title, "v2": v2.title})

        if v1.description != v2.description:
            differences.append({"field": "description", "v1": v1.description, "v2": v2.description})

        if v1.content_body != v2.content_body:
            differences.append({"field": "content_body", "changed": True})

        return {
            "version_1": str(version_id_1),
            "version_2": str(version_id_2),
            "differences": differences,
            "is_identical": len(differences) == 0,
        }

    def get_version_count(self, content_id: UUID) -> int:
        """Get count of versions for content.

        Args:
            content_id: UUID of the content

        Returns:
            Total number of versions for the content
        """
        return len(self._content_versions.get(content_id, []))

    def delete_version(self, version_id: UUID) -> bool:
        """Delete a version (soft delete).

        Args:
            version_id: UUID of the version to delete

        Returns:
            True if version was deleted, False if not found
        """
        version = self.get_version(version_id)
        if not version:
            return False

        version.soft_delete()
        return True

    def increment_version(self, current_version: str, increment_type: str = "patch") -> str:
        """Increment semantic version number.

        Args:
            current_version: Current version string (e.g., "1.2.3")
            increment_type: Type of increment - "major", "minor", or "patch" (defaults to "patch")

        Returns:
            New version string, or "1.0.0" if current_version is invalid
        """
        try:
            parts = current_version.split(".")
            major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])

            if increment_type == "major":
                major += 1
                minor = 0
                patch = 0
            elif increment_type == "minor":
                minor += 1
                patch = 0
            else:  # patch
                patch += 1

            return f"{major}.{minor}.{patch}"
        except (ValueError, IndexError):
            return "1.0.0"
