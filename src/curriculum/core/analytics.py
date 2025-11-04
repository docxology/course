"""Analytics models for learning event tracking."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import Field

from curriculum.core.base import BaseEntity


class ActivityVerb(str, Enum):
    """xAPI activity verbs."""

    VIEWED = "viewed"
    COMPLETED = "completed"
    ASSESSED = "assessed"
    STARTED = "started"
    ATTEMPTED = "attempted"
    PASSED = "passed"
    FAILED = "failed"
    SUBMITTED = "submitted"
    GRADED = "graded"
    DOWNLOADED = "downloaded"
    SHARED = "shared"


class EventType(str, Enum):
    """Learning event types."""

    CONTENT = "content"
    ASSESSMENT = "assessment"
    USER = "user"


class DeviceType(str, Enum):
    """Device types for analytics."""

    DESKTOP = "desktop"
    MOBILE = "mobile"
    TABLET = "tablet"
    UNKNOWN = "unknown"


class LearningEvent(BaseEntity):
    """xAPI-compliant learning event."""

    user_id: UUID
    verb: ActivityVerb
    event_type: EventType
    object_id: UUID
    object_type: str  # content, assessment, lesson, etc.

    # Event context
    session_id: Optional[str] = None
    device_type: DeviceType = DeviceType.UNKNOWN
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

    # Result data
    success: Optional[bool] = None
    score: Optional[float] = None
    duration: Optional[int] = None  # seconds
    completion: Optional[float] = None  # percentage

    # Additional metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AnalyticsReport(BaseEntity):
    """Analytics report for users or content."""

    report_type: str  # user, content, course, system
    target_id: UUID  # ID of the target being reported on
    report_data: Dict[str, Any]

    # Report metadata
    generated_by: UUID
    parameters: Dict[str, Any] = Field(default_factory=dict)
    is_public: bool = False


class ContentAnalytics(BaseEntity):
    """Analytics data for content items."""

    content_id: UUID

    # Engagement metrics
    total_views: int = 0
    unique_viewers: int = 0
    average_view_duration: Optional[int] = None  # seconds
    completion_rate: Optional[float] = None  # percentage

    # Social metrics
    total_shares: int = 0
    total_downloads: int = 0
    total_likes: int = 0

    # Performance metrics
    average_score: Optional[float] = None
    pass_rate: Optional[float] = None

    # Time-based metrics
    last_viewed_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class UserAnalytics(BaseEntity):
    """Analytics data for users."""

    user_id: UUID

    # Learning metrics
    total_study_time: int = 0  # minutes
    lessons_completed: int = 0
    assessments_attempted: int = 0
    assessments_passed: int = 0
    assessments_completed: int = 0
    average_score: Optional[float] = None

    # Engagement metrics
    login_streak: int = 0
    last_active_at: Optional[datetime] = None
    total_sessions: int = 0
    average_session_duration: Optional[int] = None  # minutes

    # Achievement metrics
    badges_earned: int = 0
    certificates_earned: int = 0
    points_earned: int = 0

    # Performance trends
    completion_rate: Optional[float] = None
    improvement_rate: Optional[float] = None  # percentage per week

    def update_timestamp(self) -> None:
        """Update timestamp and last active."""
        super().update_timestamp()
        self.last_active_at = datetime.now(timezone.utc)


class SessionAnalytics(BaseEntity):
    """Analytics for user sessions."""

    user_id: UUID
    session_id: str
    device_type: DeviceType = DeviceType.UNKNOWN

    # Session timing
    start_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    end_time: Optional[datetime] = None
    duration: Optional[int] = None  # seconds

    # Session activity
    content_views: int = 0
    assessments_taken: int = 0
    total_events: int = 0

    # Session quality
    focus_score: Optional[float] = None  # 0-1
    productivity_rating: Optional[str] = None

    def end_session(self) -> None:
        """End the session and calculate duration."""
        if self.end_time is None:
            self.end_time = datetime.now(timezone.utc)
            if self.start_time:
                self.duration = int((self.end_time - self.start_time).total_seconds())
