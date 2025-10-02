"""Tests for Analytics Service."""

import pytest

from curriculum.core.analytics import ActivityVerb, EventType, DeviceType


class TestAnalyticsService:
    """Tests for AnalyticsService."""

    def test_track_event(self, analytics_service, sample_user, sample_content):
        """Test tracking a learning event."""
        event = analytics_service.track_event(
            user_id=sample_user.id,
            verb=ActivityVerb.VIEWED,
            event_type=EventType.CONTENT_VIEW,
            object_id=sample_content.id,
            object_type="content",
        )

        assert event is not None
        assert event.user_id == sample_user.id
        assert event.verb == ActivityVerb.VIEWED
        assert event.object_id == sample_content.id

    def test_track_content_view(self, analytics_service, sample_user, sample_content):
        """Test tracking content view."""
        event = analytics_service.track_content_view(
            user_id=sample_user.id,
            content_id=sample_content.id,
            duration=120,
            device_type=DeviceType.DESKTOP,
        )

        assert event is not None
        assert event.event_type == EventType.CONTENT_VIEW
        assert event.duration == 120
        assert event.device_type == DeviceType.DESKTOP

    def test_track_assessment_completion(
        self, analytics_service, sample_user, sample_assessment
    ):
        """Test tracking assessment completion."""
        event = analytics_service.track_assessment_completion(
            user_id=sample_user.id,
            assessment_id=sample_assessment.id,
            score=85.0,
            passed=True,
            duration=1800,
        )

        assert event is not None
        assert event.score == 85.0
        assert event.success is True
        assert event.duration == 1800

    def test_start_session(self, analytics_service, sample_user):
        """Test starting a user session."""
        session = analytics_service.start_session(
            user_id=sample_user.id,
            session_id="session123",
            device_type=DeviceType.MOBILE,
        )

        assert session is not None
        assert session.user_id == sample_user.id
        assert session.session_id == "session123"
        assert session.device_type == DeviceType.MOBILE

    def test_end_session(self, analytics_service, sample_user):
        """Test ending a user session."""
        session = analytics_service.start_session(
            sample_user.id,
            "session456",
        )

        ended = analytics_service.end_session("session456")

        assert ended is not None
        assert ended.ended_at is not None
        assert ended.duration is not None

    def test_get_content_analytics(self, analytics_service, sample_user, sample_content):
        """Test getting content analytics."""
        # Track some views
        analytics_service.track_content_view(sample_user.id, sample_content.id)
        analytics_service.track_content_view(sample_user.id, sample_content.id)

        analytics = analytics_service.get_content_analytics(sample_content.id)

        assert analytics is not None
        assert analytics.total_views >= 2

    def test_get_user_analytics(self, analytics_service, sample_user, sample_assessment):
        """Test getting user analytics."""
        # Track assessment
        analytics_service.track_assessment_completion(
            sample_user.id,
            sample_assessment.id,
            score=90.0,
            passed=True,
            duration=1200,
        )

        analytics = analytics_service.get_user_analytics(sample_user.id)

        assert analytics is not None
        assert analytics.assessments_attempted >= 1
        assert analytics.average_score is not None

    def test_get_events_by_user(self, analytics_service, sample_user, sample_content):
        """Test getting events for a user."""
        # Track multiple events
        for _ in range(5):
            analytics_service.track_content_view(sample_user.id, sample_content.id)

        events = analytics_service.get_events_by_user(sample_user.id)

        assert len(events) >= 5

    def test_get_events_by_content(self, analytics_service, sample_user, sample_content):
        """Test getting events for content."""
        analytics_service.track_content_view(sample_user.id, sample_content.id)

        events = analytics_service.get_events_by_content(sample_content.id)

        assert len(events) >= 1

    def test_generate_user_report(
        self, analytics_service, sample_user, sample_content, sample_assessment
    ):
        """Test generating user report."""
        # Create some activity
        analytics_service.track_content_view(sample_user.id, sample_content.id)
        analytics_service.track_assessment_completion(
            sample_user.id,
            sample_assessment.id,
            score=80.0,
            passed=True,
            duration=1000,
        )

        report = analytics_service.generate_user_report(sample_user.id)

        assert report is not None
        assert "total_events" in report
        assert "content_views" in report
        assert "assessments_taken" in report

    def test_generate_content_report(
        self, analytics_service, sample_user, sample_content
    ):
        """Test generating content report."""
        analytics_service.track_content_view(sample_user.id, sample_content.id)

        report = analytics_service.generate_content_report(sample_content.id)

        assert report is not None
        assert "total_views" in report
        assert "unique_viewers" in report
