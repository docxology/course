# API Module

The API module provides REST endpoints for the entire curriculum system.

## Components

- `main.py`: FastAPI application setup
- `content.py`: Content management endpoints
- `users.py`: User management and authentication
- `assessments.py`: Assessment and grading endpoints
- `analytics.py`: Analytics and reporting endpoints

## Features

- RESTful API design
- JWT authentication
- Request validation
- Error handling
- CORS support
- Rate limiting (planned)

## Usage

```python
# Start API server
uvicorn curriculum.routes.main:app --reload

# API endpoints available at:
# - /api/v1/content/* - Content operations
# - /api/v1/users/* - User management
# - /api/v1/assessments/* - Assessment operations
# - /api/v1/analytics/* - Analytics and reporting
# - /health - Health check
```

## Testing

```bash
pytest tests/test_api/
```

