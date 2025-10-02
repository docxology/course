"""Content management service."""

from typing import List, Optional
from uuid import UUID

from curriculum.core.content import Content, ContentStatus, ContentVersion, ContentFormat
from curriculum.core.base import PagedResponse


class ContentService:
    """Service for managing educational content."""

    def __init__(self) -> None:
        """Initialize content service."""
        self._content_store: dict[UUID, Content] = {}
        self._version_store: dict[UUID, ContentVersion] = {}

    def create_content(
        self,
        title: str,
        content_type: str,
        format: ContentFormat,
        author_id: UUID,
        description: Optional[str] = None,
        content_body: Optional[str] = None,
    ) -> Content:
        """Create new content."""
        content = Content(
            title=title,
            description=description,
            content_type=content_type,
            format=format,
            author_id=author_id,
            content_body=content_body,
            status=ContentStatus.DRAFT,
        )
        self._content_store[content.id] = content
        return content

    def get_content(self, content_id: UUID) -> Optional[Content]:
        """Retrieve content by ID."""
        return self._content_store.get(content_id)

    def update_content(
        self,
        content_id: UUID,
        title: Optional[str] = None,
        description: Optional[str] = None,
        content_body: Optional[str] = None,
    ) -> Optional[Content]:
        """Update content fields."""
        content = self.get_content(content_id)
        if not content:
            return None

        if title is not None:
            content.title = title
        if description is not None:
            content.description = description
        if content_body is not None:
            content.content_body = content_body

        content.update_timestamp()
        return content

    def delete_content(self, content_id: UUID) -> bool:
        """Soft delete content."""
        content = self.get_content(content_id)
        if not content:
            return False

        content.soft_delete()
        return True

    def publish_content(self, content_id: UUID) -> Optional[Content]:
        """Publish content (change status to published)."""
        content = self.get_content(content_id)
        if not content:
            return None

        # Ensure content goes through proper workflow
        if content.status == ContentStatus.APPROVED:
            content.transition_to(ContentStatus.PUBLISHED)
            return content
        return None

    def transition_status(self, content_id: UUID, new_status: ContentStatus) -> Optional[Content]:
        """Transition content to a new status."""
        content = self.get_content(content_id)
        if not content:
            return None

        try:
            content.transition_to(new_status)
            return content
        except ValueError:
            return None

    def list_content(
        self,
        page: int = 1,
        page_size: int = 20,
        status: Optional[ContentStatus] = None,
        author_id: Optional[UUID] = None,
    ) -> PagedResponse:
        """List content with pagination and filtering."""
        contents = list(self._content_store.values())

        # Filter by status
        if status:
            contents = [c for c in contents if c.status == status]

        # Filter by author
        if author_id:
            contents = [c for c in contents if c.author_id == author_id]

        # Filter out deleted
        contents = [c for c in contents if not c.is_deleted]

        # Pagination
        total = len(contents)
        start = (page - 1) * page_size
        end = start + page_size
        items = contents[start:end]

        return PagedResponse.create(items=items, total=total, page=page, page_size=page_size)

    def search_content(self, query: str, limit: int = 20) -> List[Content]:
        """Search content by title and description."""
        query_lower = query.lower()
        results = []

        for content in self._content_store.values():
            if content.is_deleted:
                continue

            if query_lower in content.title.lower():
                results.append(content)
            elif content.description and query_lower in content.description.lower():
                results.append(content)
            elif any(query_lower in tag.lower() for tag in content.tags):
                results.append(content)

            if len(results) >= limit:
                break

        return results

    def add_tag(self, content_id: UUID, tag: str) -> Optional[Content]:
        """Add a tag to content."""
        content = self.get_content(content_id)
        if not content:
            return None

        if tag not in content.tags:
            content.tags.append(tag)
            content.update_timestamp()

        return content

    def remove_tag(self, content_id: UUID, tag: str) -> Optional[Content]:
        """Remove a tag from content."""
        content = self.get_content(content_id)
        if not content:
            return None

        if tag in content.tags:
            content.tags.remove(tag)
            content.update_timestamp()

        return content

    def get_children(self, parent_id: UUID) -> List[Content]:
        """Get all child content of a parent."""
        return [
            content
            for content in self._content_store.values()
            if content.parent_id == parent_id and not content.is_deleted
        ]

    def increment_views(self, content_id: UUID) -> Optional[Content]:
        """Increment view count for content."""
        content = self.get_content(content_id)
        if content:
            content.increment_views()
            return content
        return None

    def increment_downloads(self, content_id: UUID) -> Optional[Content]:
        """Increment download count for content."""
        content = self.get_content(content_id)
        if content:
            content.increment_downloads()
            return content
        return None

    def get_content_count(self) -> int:
        """Get total count of non-deleted content."""
        return sum(1 for c in self._content_store.values() if not c.is_deleted)
