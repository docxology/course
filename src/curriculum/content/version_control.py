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

    def create_version(
        self, content: Content, change_log: Optional[str] = None
    ) -> ContentVersion:
        """Create a new version snapshot of content."""
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
        """Get a specific version."""
        return self._versions.get(version_id)

    def get_content_versions(self, content_id: UUID) -> List[ContentVersion]:
        """Get all versions for specific content."""
        version_ids = self._content_versions.get(content_id, [])
        versions = [self._versions[vid] for vid in version_ids if vid in self._versions]

        # Sort by committed_at descending
        versions.sort(key=lambda v: v.committed_at, reverse=True)
        return versions

    def get_latest_version(self, content_id: UUID) -> Optional[ContentVersion]:
        """Get the latest version of content."""
        versions = self.get_content_versions(content_id)
        return versions[0] if versions else None

    def restore_version(self, content: Content, version_id: UUID) -> Optional[Content]:
        """Restore content to a specific version."""
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

    def compare_versions(
        self, version_id_1: UUID, version_id_2: UUID
    ) -> Optional[dict]:
        """Compare two versions (simplified)."""
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
        """Get count of versions for content."""
        return len(self._content_versions.get(content_id, []))

    def delete_version(self, version_id: UUID) -> bool:
        """Delete a version (soft delete)."""
        version = self.get_version(version_id)
        if not version:
            return False

        version.soft_delete()
        return True

    def increment_version(self, current_version: str, increment_type: str = "patch") -> str:
        """Increment semantic version number."""
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
