"""Core models and base classes for the Curriculum Repository System."""

from curriculum.core.base import BaseEntity, PagedResponse, TimestampMixin, UUIDMixin, SoftDeleteMixin
from curriculum.core.content import Content, ContentVersion, ContentStatus, ContentFormat, ContentType
from curriculum.core.metadata import Metadata, DublinCore, LRMIMetadata, ResourceType
from curriculum.core.user import User, UserRole, UserPermission
from curriculum.core.analytics import LearningEvent, AnalyticsReport, ActivityVerb, EventType, DeviceType, ContentAnalytics, UserAnalytics, SessionAnalytics
from curriculum.core.assessment import Assessment, Question, Submission, SubmissionResult, QuestionType, DifficultyLevel, GradingStatus

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
