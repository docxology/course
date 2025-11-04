# Mobile Module

The mobile module provides mobile-optimized learning experiences and offline capabilities.

## Services

- `MobileService`: Mobile optimization and PWA features
- `OfflineService`: Offline content and sync capabilities

## Features

- Progressive Web App (PWA) support
- Mobile-optimized dashboards
- Offline content access
- Push notifications
- Responsive design
- Gesture-based navigation

## Usage

```python
from curriculum.mobile import MobileService, OfflineService

mobile = MobileService()
offline = OfflineService()

# Create mobile dashboard
dashboard = mobile.create_mobile_dashboard(user_id, course_id)

# Create offline package
offline_package = offline.create_offline_package(
    course_id=course_id,
    content_ids=[content_id],
    include_media=True,
)
```

## Testing

```bash
pytest tests/unit/test_mobile.py
```

