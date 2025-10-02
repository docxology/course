# Module: core.analytics

**File:** `src/curriculum/core/analytics.py`

## Description

Analytics models for learning event tracking.

## Classes

### `ActivityVerb`

xAPI activity verbs.

**Inherits from:** str, Enum

**Methods:** 0

### `EventType`

Learning event types.

**Inherits from:** str, Enum

**Methods:** 0

### `DeviceType`

Device types for analytics.

**Inherits from:** str, Enum

**Methods:** 0

### `LearningEvent`

xAPI-compliant learning event.

**Inherits from:** BaseEntity

**Methods:** 0

### `AnalyticsReport`

Analytics report for users or content.

**Inherits from:** BaseEntity

**Methods:** 0

### `ContentAnalytics`

Analytics data for content items.

**Inherits from:** BaseEntity

**Methods:** 0

### `UserAnalytics`

Analytics data for users.

**Inherits from:** BaseEntity

**Methods:** 1


**Method List:**

- `update_timestamp`: Update timestamp and last active.

### `SessionAnalytics`

Analytics for user sessions.

**Inherits from:** BaseEntity

**Methods:** 1


**Method List:**

- `end_session`: End the session and calculate duration.
