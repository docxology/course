# Module: integration.integration

**File:** `src/curriculum/integration/integration.py`

## Description

Integration service for LMS and external tools.

## Classes

### `IntegrationService`

Service for integrating with external systems.

**Methods:** 18


**Method List:**

- `__init__`: Initialize integration service.

- `connect_lms`: Connect to an external LMS.

- `sync_content_to_lms`: Sync content to external LMS.

- `register_external_tool`: Register an external tool for integration.

- `create_lti_launch`: Create LTI launch parameters.

- `create_api_integration`: Create API integration with external service.

- `import_content_from_lms`: Import content from external LMS.

- `sync_grades_to_lms`: Sync student grades to external LMS.

- `create_webhook_integration`: Create webhook integration.

- `get_supported_lms_types`: Get supported LMS types.

- `get_external_tools`: Get registered external tools.

- `validate_lti_launch`: Validate LTI launch request.

- `create_sso_integration`: Create SSO integration.

- `get_integration_health`: Get health status of integration.

- `create_content_embed`: Create embeddable content for external platforms.

- `_generate_embed_html`: Generate HTML for content embedding.

- `get_supported_integrations`: Get supported integration types.

- `monitor_integration_activity`: Monitor integration activity.
