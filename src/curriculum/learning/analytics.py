"""Analytics and tracking service."""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from curriculum.core.analytics import (
    LearningEvent,
    ActivityVerb,
    EventType,
    DeviceType,
    ContentAnalytics,
    UserAnalytics,
    SessionAnalytics,
)


class AnalyticsService:
    """Service for learning analytics and tracking."""

    def __init__(self) -> None:
        """Initialize analytics service."""
        self._events: List[LearningEvent] = []
        self._content_analytics: dict[UUID, ContentAnalytics] = {}
        self._user_analytics: dict[UUID, UserAnalytics] = {}
        self._sessions: dict[str, SessionAnalytics] = {}

    def track_event(
        self,
        user_id: UUID,
        verb: ActivityVerb,
        event_type: EventType,
        object_id: UUID,
        object_type: str,
        success: Optional[bool] = None,
        score: Optional[float] = None,
        duration: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> LearningEvent:
        """Track a learning event."""
        event = LearningEvent(
            user_id=user_id,
            verb=verb,
            event_type=event_type,
            object_id=object_id,
            object_type=object_type,
            success=success,
            score=score,
            duration=duration,
            metadata=metadata or {},
        )
        self._events.append(event)
        return event

    def track_content_view(
        self,
        user_id: UUID,
        content_id: UUID,
        duration: Optional[int] = None,
        device_type: DeviceType = DeviceType.UNKNOWN,
    ) -> LearningEvent:
        """Track content view event."""
        event = self.track_event(
            user_id=user_id,
            verb=ActivityVerb.VIEWED,
            event_type=EventType.CONTENT_VIEW,
            object_id=content_id,
            object_type="content",
            duration=duration,
        )
        event.device_type = device_type

        # Update content analytics
        self._update_content_analytics(content_id, user_id)

        return event

    def track_assessment_completion(
        self,
        user_id: UUID,
        assessment_id: UUID,
        score: float,
        passed: bool,
        duration: int,
    ) -> LearningEvent:
        """Track assessment completion event."""
        event = self.track_event(
            user_id=user_id,
            verb=ActivityVerb.COMPLETED,
            event_type=EventType.ASSESSMENT_SUBMIT,
            object_id=assessment_id,
            object_type="assessment",
            success=passed,
            score=score,
            duration=duration,
        )

        # Update user analytics
        self._update_user_analytics(user_id, assessment_passed=passed, score=score)

        return event

    def start_session(
        self,
        user_id: UUID,
        session_id: str,
        device_type: DeviceType = DeviceType.UNKNOWN,
    ) -> SessionAnalytics:
        """Start a new user session."""
        session = SessionAnalytics(
            user_id=user_id,
            session_id=session_id,
            device_type=device_type,
        )
        self._sessions[session_id] = session
        return session

    def end_session(self, session_id: str) -> Optional[SessionAnalytics]:
        """End a user session."""
        session = self._sessions.get(session_id)
        if session:
            session.end_session()
        return session

    def get_content_analytics(self, content_id: UUID) -> Optional[ContentAnalytics]:
        """Get analytics for specific content."""
        return self._content_analytics.get(content_id)

    def get_user_analytics(self, user_id: UUID) -> Optional[UserAnalytics]:
        """Get analytics for specific user."""
        return self._user_analytics.get(user_id)

    def get_events_by_user(
        self,
        user_id: UUID,
        event_type: Optional[EventType] = None,
        limit: int = 100,
    ) -> List[LearningEvent]:
        """Get events for a specific user."""
        events = [e for e in self._events if e.user_id == user_id]

        if event_type:
            events = [e for e in events if e.event_type == event_type]

        # Sort by created_at descending (BaseEntity field)
        events.sort(key=lambda e: e.created_at, reverse=True)

        return events[:limit]

    def get_events_by_content(
        self,
        content_id: UUID,
        event_type: Optional[EventType] = None,
        limit: int = 100,
    ) -> List[LearningEvent]:
        """Get events for specific content."""
        events = [e for e in self._events if e.object_id == content_id]

        if event_type:
            events = [e for e in events if e.event_type == event_type]

        events.sort(key=lambda e: e.timestamp, reverse=True)

        return events[:limit]

    def _update_content_analytics(self, content_id: UUID, user_id: UUID) -> None:
        """Update content analytics after a view event."""
        if content_id not in self._content_analytics:
            self._content_analytics[content_id] = ContentAnalytics(content_id=content_id)

        analytics = self._content_analytics[content_id]
        analytics.total_views += 1
        analytics.update_timestamp()

    def _update_user_analytics(
        self, user_id: UUID, assessment_passed: bool = False, score: Optional[float] = None
    ) -> None:
        """Update user analytics after an event."""
        if user_id not in self._user_analytics:
            self._user_analytics[user_id] = UserAnalytics(user_id=user_id)

        analytics = self._user_analytics[user_id]
        analytics.assessments_attempted += 1

        if assessment_passed:
            analytics.assessments_passed += 1
            analytics.assessments_completed += 1

        if score is not None:
            # Update average score
            if analytics.average_score is None:
                analytics.average_score = score
            else:
                total_score = analytics.average_score * (analytics.assessments_attempted - 1)
                analytics.average_score = (total_score + score) / analytics.assessments_attempted

        analytics.last_active_at = datetime.now(timezone.utc)
        analytics.update_timestamp()

    def generate_user_report(self, user_id: UUID) -> Dict[str, Any]:
        """Generate comprehensive analytics report for a user."""
        analytics = self.get_user_analytics(user_id)
        events = self.get_events_by_user(user_id, limit=1000)

        content_views = len([e for e in events if e.event_type == EventType.CONTENT_VIEW])
        assessments_taken = len([e for e in events if e.event_type == EventType.ASSESSMENT_SUBMIT])

        return {
            "user_id": str(user_id),
            "total_events": len(events),
            "content_views": content_views,
            "assessments_taken": assessments_taken,
            "total_time_spent": analytics.total_time_spent if analytics else 0,
            "average_score": analytics.average_score if analytics else None,
            "completion_rate": analytics.completion_rate if analytics else None,
            "last_active": analytics.last_active_at if analytics else None,
        }

    def generate_content_report(self, content_id: UUID) -> Dict[str, Any]:
        """Generate analytics report for content."""
        analytics = self.get_content_analytics(content_id)
        events = self.get_events_by_content(content_id, limit=1000)

        unique_users = len(set(e.user_id for e in events))

        return {
            "content_id": str(content_id),
            "total_views": analytics.total_views if analytics else 0,
            "unique_viewers": unique_users,
            "total_events": len(events),
            "completion_rate": analytics.completion_rate if analytics else None,
            "average_view_duration": analytics.average_view_duration if analytics else None,
        }
