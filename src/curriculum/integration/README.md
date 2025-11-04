# Integration Module

The integration module handles connections with external systems and services.

## Services

- `IntegrationService`: LMS and external tool integration
- `DistributionService`: Content distribution and CDN
- `ExportService`: Multi-format export capabilities
- `GamificationService`: Points, badges, and rewards

## Features

- LMS integration (Canvas, Moodle, Blackboard)
- LTI 1.3 support
- SSO integration
- API integrations
- Content distribution
- Export formats (PDF, SCORM, EPUB)
- Gamification systems

## Usage

```python
from curriculum.integration import IntegrationService, ExportService

integration = IntegrationService()
export = ExportService()

# Connect to LMS
lms_connection = integration.connect_lms(
    lms_type="canvas",
    credentials={"api_key": "key"},
    settings={"auto_sync": True},
)

# Export content
export_result = export.export_content(content_id, "scorm")
```

## Testing

```bash
pytest tests/integration/test_integration.py
pytest tests/integration/test_integration_distribution_service.py
```

