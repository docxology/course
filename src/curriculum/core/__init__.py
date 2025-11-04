"""Core models and base classes for the Curriculum Repository System."""

from curriculum.core.analytics import (
    ActivityVerb,
    AnalyticsReport,
    ContentAnalytics,
    DeviceType,
    EventType,
    LearningEvent,
    SessionAnalytics,
    UserAnalytics,
)
from curriculum.core.assessment import (
    Assessment,
    DifficultyLevel,
    GradingStatus,
    Question,
    QuestionType,
    Submission,
    SubmissionResult,
)
from curriculum.core.base import (
    BaseEntity,
    PagedResponse,
    SoftDeleteMixin,
    TimestampMixin,
    UUIDMixin,
)
from curriculum.core.content import (
    Content,
    ContentFormat,
    ContentStatus,
    ContentType,
    ContentVersion,
)
from curriculum.core.metadata import DublinCore, LRMIMetadata, Metadata, ResourceType
from curriculum.core.user import User, UserPermission, UserRole

__all__ = [
    "BaseEntity",
    "PagedResponse",
    "TimestampMixin",
    "UUIDMixin",
    "SoftDeleteMixin",
    "Content",
    "ContentVersion",
    "ContentStatus",
    "ContentFormat",
    "ContentType",
    "Metadata",
    "DublinCore",
    "LRMIMetadata",
    "ResourceType",
    "User",
    "UserRole",
    "UserPermission",
    "LearningEvent",
    "AnalyticsReport",
    "ActivityVerb",
    "EventType",
    "DeviceType",
    "ContentAnalytics",
    "UserAnalytics",
    "SessionAnalytics",
    "Assessment",
    "Question",
    "Submission",
    "SubmissionResult",
    "QuestionType",
    "DifficultyLevel",
    "GradingStatus",
]
