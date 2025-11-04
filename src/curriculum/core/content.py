"""Content models for educational materials."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import Field, HttpUrl

from curriculum.core.base import BaseEntity


class ContentStatus(str, Enum):
    """Content lifecycle status."""

    DRAFT = "draft"
    INTERNAL_REVIEW = "internal_review"
    EXTERNAL_REVIEW = "external_review"
    APPROVED = "approved"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class ContentFormat(str, Enum):
    """Supported content formats."""

    MARKDOWN = "markdown"
    HTML = "html"
    PDF = "pdf"
    SCORM = "scorm"
    XAPI = "xapi"
    H5P = "h5p"
    VIDEO = "video"
    AUDIO = "audio"
    LATEX = "latex"


class ContentType(str, Enum):
    """Type of educational content."""

    COURSE = "course"
    MODULE = "module"
    LESSON = "lesson"
    ASSESSMENT = "assessment"
    RESOURCE = "resource"
    MULTIMEDIA = "multimedia"


class Content(BaseEntity):
    """Educational content entity."""

    title: str = Field(min_length=1, max_length=500)
    description: Optional[str] = None
    content_type: ContentType
    format: ContentFormat
    status: ContentStatus = ContentStatus.DRAFT

    # Content data
    content_body: Optional[str] = None
    content_url: Optional[HttpUrl] = None
    file_path: Optional[str] = None

    # Organization
    parent_id: Optional[UUID] = None
    order_index: int = 0
    tags: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)

    # Authoring
    author_id: UUID
    contributors: List[UUID] = Field(default_factory=list)

    # Version control
    current_version: str = "1.0.0"
    version_history: List[UUID] = Field(default_factory=list)

    # Metadata
    metadata_id: Optional[UUID] = None
    custom_metadata: Dict[str, Any] = Field(default_factory=dict)

    # Access control
    is_public: bool = False
    access_groups: List[UUID] = Field(default_factory=list)

    # Analytics
    view_count: int = 0
    download_count: int = 0

    def increment_views(self) -> None:
        """Increment view count."""
        self.view_count += 1

    def increment_downloads(self) -> None:
        """Increment download count."""
        self.download_count += 1

    def can_transition_to(self, new_status: ContentStatus) -> bool:
        """Check if content can transition to new status."""
        transitions = {
            ContentStatus.DRAFT: [ContentStatus.INTERNAL_REVIEW],
            ContentStatus.INTERNAL_REVIEW: [ContentStatus.DRAFT, ContentStatus.EXTERNAL_REVIEW],
            ContentStatus.EXTERNAL_REVIEW: [ContentStatus.INTERNAL_REVIEW, ContentStatus.APPROVED],
            ContentStatus.APPROVED: [ContentStatus.PUBLISHED],
            ContentStatus.PUBLISHED: [ContentStatus.ARCHIVED],
            ContentStatus.ARCHIVED: [ContentStatus.DRAFT],
        }
        return new_status in transitions.get(self.status, [])

    def transition_to(self, new_status: ContentStatus) -> None:
        """Transition content to new status."""
        if not self.can_transition_to(new_status):
            raise ValueError(f"Cannot transition from {self.status} to {new_status}")
        self.status = new_status
        self.update_timestamp()


class ContentVersion(BaseEntity):
    """Version snapshot of content."""

    content_id: UUID
    version: str
    title: str
    description: Optional[str] = None
    content_body: Optional[str] = None
    content_url: Optional[HttpUrl] = None
    file_path: Optional[str] = None

    # Version metadata
    change_log: Optional[str] = None
    author_id: UUID
    committed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Snapshot of content at this version
    snapshot: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def create_from_content(
        cls, content: Content, change_log: Optional[str] = None
    ) -> "ContentVersion":
        """Create a version snapshot from content."""
        return cls(
            content_id=content.id,
            version=content.current_version,
            title=content.title,
            description=content.description,
            content_body=content.content_body,
            content_url=content.content_url,
            file_path=content.file_path,
            change_log=change_log,
            author_id=content.author_id,
            snapshot=content.model_dump(exclude={"version_history"}),
        )


class ContentRelation(BaseEntity):
    """Relationship between content items."""

    source_id: UUID
    target_id: UUID
    relation_type: str  # prerequisite, related, part_of, references
    order_index: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)
