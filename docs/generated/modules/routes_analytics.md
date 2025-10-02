# Module: routes.analytics

**File:** `src/curriculum/routes/analytics.py`

## Description

Analytics API routes.

## Classes

### `TrackEventRequest`

Request model for tracking events.

**Inherits from:** BaseModel

**Methods:** 0

### `UserReportResponse`

Response model for user analytics report.

**Inherits from:** BaseModel

**Methods:** 0

### `ContentReportResponse`

Response model for content analytics report.

**Inherits from:** BaseModel

**Methods:** 0

### `EventResponse`

Response model for learning events.

**Inherits from:** BaseModel

**Methods:** 0

## Functions

### `track_event`

Track a learning event.

**Parameters:**

- `request: TrackEventRequest`

- `current_user: User`

### `track_content_view`

Track content view event.

**Parameters:**

- `content_id: UUID`

- `duration: Optional[int]`

- `current_user: User`

### `track_assessment_completion`

Track assessment completion event.

**Parameters:**

- `assessment_id: UUID`

- `score: float`

- `passed: bool`

- `duration: int`

- `current_user: User`

### `get_user_report`

Get analytics report for a user.

**Parameters:**

- `user_id: UUID`

- `current_user: User`

### `get_content_report`

Get analytics report for content.

**Parameters:**

- `content_id: UUID`

### `get_user_events`

Get events for a specific user.

**Parameters:**

- `user_id: UUID`

- `event_type: Optional[EventType]`

- `limit: int`

- `current_user: User`

### `get_content_events`

Get events for specific content.

**Parameters:**

- `content_id: UUID`

- `event_type: Optional[EventType]`

- `limit: int`

### `get_dashboard_overview`

Get dashboard overview statistics.

**Parameters:**

- `current_user: User`

### `export_analytics_report`

Export analytics report.

**Parameters:**

- `report_type: str`

- `format: str`

- `start_date: Optional[datetime]`

- `end_date: Optional[datetime]`

- `current_user: User`

### `_event_to_response`

Convert LearningEvent model to response model.

**Parameters:**

- `event: LearningEvent`
