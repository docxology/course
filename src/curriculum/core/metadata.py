"""Metadata models following Dublin Core and LRMI standards."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import Field, HttpUrl

from curriculum.core.base import BaseEntity


class ResourceType(str, Enum):
    """Dublin Core resource types."""

    TEXT = "Text"
    IMAGE = "Image"
    SOUND = "Sound"
    VIDEO = "MovingImage"
    DATASET = "Dataset"
    SOFTWARE = "Software"
    INTERACTIVE = "InteractiveResource"
    EVENT = "Event"
    COLLECTION = "Collection"


class EducationalUse(str, Enum):
    """LRMI educational use types."""

    ASSIGNMENT = "assignment"
    ASSESSMENT = "assessment"
    LECTURE = "lecture"
    ACTIVITY = "activity"
    LAB = "lab"
    LESSON_PLAN = "lessonPlan"
    READING = "reading"


class InteractivityType(str, Enum):
    """LRMI interactivity types."""

    ACTIVE = "active"
    EXPOSITIVE = "expositive"
    MIXED = "mixed"


class LearningResourceType(str, Enum):
    """LRMI learning resource types."""

    COURSE = "course"
    MODULE = "module"
    UNIT = "unit"
    LESSON = "lesson"
    ASSESSMENT = "assessment"
    PRESENTATION = "presentation"
    SIMULATION = "simulation"


class DublinCore(BaseEntity):
    """Dublin Core 15-element metadata schema."""

    # Core elements
    title: str = Field(min_length=1, max_length=500)
    creator: List[str] = Field(default_factory=list)
    subject: List[str] = Field(default_factory=list)
    description: Optional[str] = None
    publisher: Optional[str] = None
    contributor: List[str] = Field(default_factory=list)
    date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    type: ResourceType = ResourceType.TEXT
    format: Optional[str] = None  # MIME type
    identifier: Optional[str] = None  # URI or unique identifier
    source: Optional[HttpUrl] = None
    language: str = "en"
    relation: List[str] = Field(default_factory=list)  # Related resources
    coverage: Optional[str] = None  # Spatial or temporal
    rights: Optional[str] = None  # Rights statement


class LRMIMetadata(BaseEntity):
    """Learning Resource Metadata Initiative (LRMI) extensions."""

    # Educational properties
    educational_alignment: List[str] = Field(default_factory=list)  # Standards
    educational_use: List[EducationalUse] = Field(default_factory=list)
    interactivity_type: InteractivityType = InteractivityType.MIXED
    learning_resource_type: List[LearningResourceType] = Field(default_factory=list)

    # Audience
    typical_age_range: Optional[str] = None  # e.g., "18-25"
    audience_type: List[str] = Field(default_factory=list)  # e.g., ["student", "teacher"]

    # Time and difficulty
    time_required: Optional[int] = None  # Minutes
    difficulty_level: Optional[str] = None  # Easy, Medium, Hard
    educational_level: List[str] = Field(default_factory=list)  # Grade levels

    # Prerequisites
    competency_required: List[str] = Field(default_factory=list)
    accessibility_features: List[str] = Field(default_factory=list)
    accessibility_hazards: List[str] = Field(default_factory=list)

    # Additional metadata
    keywords: List[str] = Field(default_factory=list)
    in_language: List[str] = Field(default_factory=list)


class Metadata(BaseEntity):
    """Comprehensive metadata combining Dublin Core and LRMI."""

    content_id: UUID

    # Dublin Core
    dublin_core: DublinCore

    # LRMI extensions
    lrmi: Optional[LRMIMetadata] = None

    # Custom taxonomies
    custom_tags: List[str] = Field(default_factory=list)
    categories: List[str] = Field(default_factory=list)
    topics: List[str] = Field(default_factory=list)

    # Technical metadata
    file_size: Optional[int] = None  # Bytes
    checksum: Optional[str] = None  # SHA-256 hash
    encoding: Optional[str] = None

    # SEO
    seo_title: Optional[str] = None
    seo_description: Optional[str] = None
    seo_keywords: List[str] = Field(default_factory=list)

    # Custom fields
    custom_fields: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def create_minimal(cls, content_id: UUID, title: str) -> "Metadata":
        """Create metadata with minimal required fields."""
        dublin_core = DublinCore(title=title)
        return cls(content_id=content_id, dublin_core=dublin_core)


class Taxonomy(BaseEntity):
    """Custom taxonomy for content classification."""

    name: str = Field(min_length=1, max_length=100)
    description: Optional[str] = None
    parent_id: Optional[UUID] = None
    path: str  # Hierarchical path like "/sciences/physics/mechanics"
    level: int = 0
    order_index: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Tag(BaseEntity):
    """Content tag."""

    name: str = Field(min_length=1, max_length=50)
    slug: str = Field(min_length=1, max_length=50)
    description: Optional[str] = None
    usage_count: int = 0
    color: Optional[str] = None  # Hex color for UI

    def increment_usage(self) -> None:
        """Increment tag usage count."""
        self.usage_count += 1

    def decrement_usage(self) -> None:
        """Decrement tag usage count."""
        if self.usage_count > 0:
            self.usage_count -= 1
