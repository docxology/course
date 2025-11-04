# AI Agents Guide - Integration Module

## Overview

The integration module handles connections with external systems including LMS platforms, content distribution, and gamification.

## Module Structure

```
integration/
├── integration.py # LMS and external tool integration
├── distribution.py # Content distribution and CDN
├── export.py      # Multi-format export capabilities
├── gamification.py # Points, badges, and rewards
├── __init__.py    # Module exports
├── README.md      # Module documentation
└── AGENTS.md      # This file
```

## Development Guidelines

### When Working on Integrations

1. **Use standard protocols**:
```python
def create_lti_launch(self, tool_id: UUID, user_id: UUID, content_id: UUID):
    lti_params = {
        "lti_version": "LTI-1.3",
        "lti_message_type": "LtiResourceLinkRequest",
        "iss": "https://curriculum.edu",
        "aud": tool["client_id"],
        "sub": str(user_id),
    }
    return lti_params
```

2. **Implement proper error handling** for external services:
```python
async def sync_content_to_lms(self, lms_connection_id: str, content_ids: List[UUID]):
    try:
        # Attempt sync
        result = await self._lms_api.sync_content(content_ids)
        return {"status": "success", "synced": len(content_ids)}
    except Exception as e:
        return {"status": "error", "error": str(e)}
```

3. **Handle rate limiting**:
```python
def create_api_integration(self, service_name: str, configuration: Dict[str, Any]):
    integration = {
        "name": service_name,
        "rate_limits": {
            "requests_per_minute": 60,
            "requests_per_hour": 1000,
        },
        "retry_policy": {
            "max_retries": 3,
            "backoff_multiplier": 2,
        },
    }
    return integration
```

### LMS Integration

1. **Support multiple LMS platforms**:
```python
def get_supported_lms_types(self) -> List[str]:
    return [
        "canvas", "moodle", "blackboard",
        "schoology", "google_classroom", "microsoft_teams"
    ]
```

2. **Implement content synchronization**:
```python
async def sync_content_to_lms(self, lms_connection_id: str, content_ids: List[UUID]):
    connection = self._lms_connections.get(lms_connection_id)
    if not connection:
        return {"error": "LMS connection not found"}

    for content_id in content_ids:
        # Get content
        content = await self.content_service.get_content(content_id)

        # Sync to LMS
        lms_id = await self._lms_api.create_module(content)

        # Update mapping
        self._content_mapping[content_id] = lms_id

    return {"synced": len(content_ids)}
```

### Export Services

1. **Support multiple export formats**:
```python
def get_supported_formats(self) -> List[str]:
    return ["pdf", "html", "markdown", "epub", "docx", "scorm", "qti"]
```

2. **Implement format validation**:
```python
def validate_export_options(self, format: str, options: Dict[str, Any]):
    format_options = {
        "pdf": {
            "page_size": ["A4", "Letter", "Legal"],
            "orientation": ["portrait", "landscape"],
        },
        "scorm": {
            "version": ["1.2", "2004"],
            "include_assessments": [True, False],
        },
    }

    valid_options = format_options.get(format, {})
    for key, value in options.items():
        if key not in valid_options:
            return False
        if value not in valid_options[key]:
            return False

    return True
```

### Gamification Features

1. **Implement point system**:
```python
def award_points(self, user_id: UUID, points: int, reason: str):
    current_points = self._user_points.get(user_id, 0)
    new_total = current_points + points

    self._user_points[user_id] = new_total

    # Check for badge eligibility
    badges_earned = self._check_badge_eligibility(user_id, reason)

    return {
        "points_awarded": points,
        "new_total": new_total,
        "badges_earned": badges_earned,
    }
```

2. **Create leaderboards**:
```python
def get_leaderboard(self, category: str = "points", limit: int = 10):
    if category == "points":
        users = sorted(
            self._user_points.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return [{"user_id": uid, "points": points} for uid, points in users[:limit]]
```

### Testing Requirements

- **Test external service integrations** (mock external APIs)
- **Test export functionality**
- **Test gamification features**
- **Test error scenarios**

Example test:
```python
def test_lms_integration(mock_lms_api):
    with patch('integration.lms_api') as mock_api:
        mock_api.sync_content.return_value = {"status": "success"}

        result = integration_service.sync_content_to_lms(
            "canvas_connection",
            [content_id]
        )

        assert result["status"] == "success"
        mock_api.sync_content.assert_called_once()
```

### Performance Considerations

- **Implement caching** for external API responses
- **Use async processing** for heavy operations
- **Add retry logic** for external service calls
- **Monitor API usage** and costs

### Common Patterns

#### External API Integration
```python
async def call_external_api(self, endpoint: str, data: Dict[str, Any]):
    try:
        response = await self._http_client.post(endpoint, json=data)
        return response.json()
    except Exception as e:
        self._logger.error(f"API call failed: {e}")
        return {"error": str(e)}
```

#### Export Processing
```python
def export_content(self, content_id: UUID, format: str):
    content = self.content_service.get_content(content_id)

    if format == "pdf":
        return self._generate_pdf(content)
    elif format == "scorm":
        return self._generate_scorm_package(content)
    # ... other formats
```

### Extension Points

- Custom LMS integrations
- Additional export formats
- Advanced gamification features
- External tool integrations
- API rate limiting strategies

