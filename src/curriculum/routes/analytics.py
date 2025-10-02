"""Analytics API routes."""

from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Query, Path, status
from pydantic import BaseModel

from curriculum.core.analytics import LearningEvent, EventType, ActivityVerb
from curriculum.learning.analytics import AnalyticsService
from curriculum.core.user import User, UserPermission
from curriculum.routes.dependencies import get_current_user


router = APIRouter()

# Service instance
analytics_service = AnalyticsService()


# Request/Response models
class TrackEventRequest(BaseModel):
    """Request model for tracking events."""
    verb: ActivityVerb
    event_type: EventType
    object_id: UUID
    object_type: str
    success: Optional[bool] = None
    score: Optional[float] = None
    duration: Optional[int] = None
    metadata: Dict[str, Any] = {}


class UserReportResponse(BaseModel):
    """Response model for user analytics report."""
    user_id: str
    total_events: int
    content_views: int
    assessments_taken: int
    total_time_spent: int
    average_score: Optional[float] = None
    completion_rate: Optional[float] = None
    last_active: Optional[str] = None


class ContentReportResponse(BaseModel):
    """Response model for content analytics report."""
    content_id: str
    total_views: int
    unique_viewers: int
    total_events: int
    completion_rate: Optional[float] = None
    average_view_duration: Optional[float] = None


class EventResponse(BaseModel):
    """Response model for learning events."""
    id: str
    user_id: str
    verb: str
    event_type: str
    object_id: str
    object_type: str
    success: Optional[bool] = None
    score: Optional[float] = None
    duration: Optional[int] = None
    timestamp: str


# Analytics routes
@router.post("/events", response_model=EventResponse)
async def track_event(
    request: TrackEventRequest,
    current_user: User = Depends(get_current_user),
):
    """Track a learning event."""
    event = analytics_service.track_event(
        user_id=current_user.id,
        verb=request.verb,
        event_type=request.event_type,
        object_id=request.object_id,
        object_type=request.object_type,
        success=request.success,
        score=request.score,
        duration=request.duration,
        metadata=request.metadata,
    )

    return _event_to_response(event)


@router.post("/events/content-view")
async def track_content_view(
    content_id: UUID,
    duration: Optional[int] = None,
    current_user: User = Depends(get_current_user),
):
    """Track content view event."""
    event = analytics_service.track_content_view(
        user_id=current_user.id,
        content_id=content_id,
        duration=duration,
    )

    return _event_to_response(event)


@router.post("/events/assessment-completion")
async def track_assessment_completion(
    assessment_id: UUID,
    score: float,
    passed: bool,
    duration: int,
    current_user: User = Depends(get_current_user),
):
    """Track assessment completion event."""
    event = analytics_service.track_assessment_completion(
        user_id=current_user.id,
        assessment_id=assessment_id,
        score=score,
        passed=passed,
        duration=duration,
    )

    return _event_to_response(event)


@router.get("/users/{user_id}/report", response_model=UserReportResponse)
async def get_user_report(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
):
    """Get analytics report for a user."""
    if user_id != current_user.id and not current_user.has_permission(UserPermission.ANALYTICS_VIEW):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    report = analytics_service.generate_user_report(user_id)

    return UserReportResponse(
        user_id=report["user_id"],
        total_events=report["total_events"],
        content_views=report["content_views"],
        assessments_taken=report["assessments_taken"],
        total_time_spent=report["total_time_spent"],
        average_score=report["average_score"],
        completion_rate=report["completion_rate"],
        last_active=report["last_active"].isoformat() if report["last_active"] else None,
    )


@router.get("/content/{content_id}/report", response_model=ContentReportResponse)
async def get_content_report(content_id: UUID):
    """Get analytics report for content."""
    report = analytics_service.generate_content_report(content_id)

    return ContentReportResponse(
        content_id=report["content_id"],
        total_views=report["total_views"],
        unique_viewers=report["unique_viewers"],
        total_events=report["total_events"],
        completion_rate=report["completion_rate"],
        average_view_duration=report["average_view_duration"],
    )


@router.get("/users/{user_id}/events", response_model=List[EventResponse])
async def get_user_events(
    user_id: UUID,
    event_type: Optional[EventType] = Query(None, description="Filter by event type"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of events"),
    current_user: User = Depends(get_current_user),
):
    """Get events for a specific user."""
    if user_id != current_user.id and not current_user.has_permission(UserPermission.ANALYTICS_VIEW):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    events = analytics_service.get_events_by_user(user_id, event_type, limit)

    return [_event_to_response(e) for e in events]


@router.get("/content/{content_id}/events", response_model=List[EventResponse])
async def get_content_events(
    content_id: UUID,
    event_type: Optional[EventType] = Query(None, description="Filter by event type"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of events"),
):
    """Get events for specific content."""
    events = analytics_service.get_events_by_content(content_id, event_type, limit)

    return [_event_to_response(e) for e in events]


@router.get("/dashboard/overview", response_model=Dict[str, Any])
async def get_dashboard_overview(current_user: User = Depends(get_current_user)):
    """Get dashboard overview statistics."""
    if not current_user.has_permission(UserPermission.ANALYTICS_VIEW):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    # In a real implementation, this would aggregate data from database
    return {
        "total_users": 0,
        "total_content": 0,
        "total_views": 0,
        "total_assessments": 0,
        "average_completion_rate": 0.0,
        "top_content": [],
        "recent_activity": [],
    }


@router.get("/reports/export")
async def export_analytics_report(
    report_type: str = Query(..., description="Type of report"),
    format: str = Query("json", description="Export format"),
    start_date: Optional[datetime] = Query(None, description="Start date"),
    end_date: Optional[datetime] = Query(None, description="End date"),
    current_user: User = Depends(get_current_user),
):
    """Export analytics report."""
    if not current_user.has_permission(UserPermission.ANALYTICS_EXPORT):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    # In a real implementation, this would generate and return a file
    return {
        "message": "Report export functionality not yet implemented",
        "report_type": report_type,
        "format": format,
        "start_date": start_date,
        "end_date": end_date,
    }


# Helper functions
def _event_to_response(event: LearningEvent) -> EventResponse:
    """Convert LearningEvent model to response model."""
    return EventResponse(
        id=str(event.id),
        user_id=str(event.user_id),
        verb=event.verb.value,
        event_type=event.event_type.value,
        object_id=str(event.object_id),
        object_type=event.object_type,
        success=event.success,
        score=event.score,
        duration=event.duration,
        timestamp=event.timestamp.isoformat(),
    )
