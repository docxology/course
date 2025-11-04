# AI Agents Guide - Mobile Module

## Overview

The mobile module provides mobile-optimized learning experiences and offline capabilities.

## Module Structure

```
mobile/
├── mobile.py      # Mobile optimization and PWA features
├── offline.py     # Offline content and sync capabilities
├── __init__.py    # Module exports
├── README.md      # Module documentation
└── AGENTS.md      # This file
```

## Development Guidelines

### When Working on Mobile Features

1. **Implement Progressive Web App features**:
```python
def generate_mobile_app_manifest(self, course_id: UUID, course_title: str):
    return {
        "name": course_title,
        "short_name": course_title[:12] + "..." if len(course_title) > 12 else course_title,
        "start_url": f"/courses/{course_id}/mobile",
        "display": "standalone",
        "theme_color": "#007bff",
        "icons": [
            {"src": "/icons/icon-192x192.png", "sizes": "192x192"},
            {"src": "/icons/icon-512x512.png", "sizes": "512x512"},
        ],
    }
```

2. **Optimize for mobile performance**:
```python
def optimize_content_for_mobile(self, content: Content, target_device: str):
    optimizations = []

    if len(content.content_body) > 10000:
        optimizations.append("content_chunking")

    if "video" in content.content_body.lower():
        optimizations.append("video_compression")

    return {
        "optimizations_applied": optimizations,
        "estimated_load_time": 2.5,
        "mobile_score": 85,
    }
```

3. **Implement offline capabilities**:
```python
def create_offline_package(self, course_id: UUID, content_ids: List[UUID]):
    return {
        "id": str(uuid4()),
        "course_id": str(course_id),
        "content_ids": [str(cid) for cid in content_ids],
        "format": "zip",
        "estimated_size": "150MB",
        "download_url": f"/api/offline/{package_id}/download",
    }
```

### Mobile Optimization

1. **Responsive design considerations**:
```python
def validate_mobile_compatibility(self, content: Content):
    issues = []

    if len(content.content_body) > 50000:
        issues.append("Content too long for mobile optimization")

    if "hover" in content.content_body:
        issues.append("Hover effects may not work on touch devices")

    return {
        "mobile_compatibility_score": max(0, 100 - len(issues) * 10),
        "issues": issues,
    }
```

2. **Touch-friendly interfaces**:
```python
def create_mobile_dashboard(self, user_id: UUID, course_id: UUID):
    return {
        "layout": "mobile_optimized",
        "widgets": [
            {"type": "progress_ring", "size": "large"},
            {"type": "quick_actions", "touch_targets": "44px"},
        ],
        "navigation": {"bottom_tabs": True},
    }
```

### Offline Features

1. **Content caching**:
```python
def cache_content_for_offline(self, content_id: UUID, user_id: UUID):
    cache_entry = {
        "content_id": str(content_id),
        "user_id": str(user_id),
        "cached_at": datetime.utcnow(),
        "expires_at": datetime.utcnow() + timedelta(hours=24),
        "is_compressed": True,
    }
    self._cached_content[str(uuid4())] = cache_entry
    return cache_entry
```

2. **Sync mechanisms**:
```python
def start_sync_session(self, user_id: UUID, device_id: str):
    session = {
        "id": str(uuid4()),
        "user_id": str(user_id),
        "device_id": device_id,
        "sync_direction": "bidirectional",
        "status": "syncing",
        "items_synced": 0,
    }
    return session
```

### Testing Requirements

- **Test mobile compatibility**
- **Test offline functionality**
- **Test PWA features**
- **Test sync mechanisms**

Example test:
```python
def test_mobile_optimization():
    content = Content(content_body="Long content" * 1000)
    result = mobile_service.optimize_content_for_mobile(content)

    assert "content_chunking" in result["optimizations_applied"]
    assert result["mobile_score"] > 70
```

### Performance Considerations

- **Lazy loading** for mobile performance
- **Image optimization** for bandwidth
- **Background sync** for offline functionality
- **Cache management** for storage optimization

### Common Patterns

#### Mobile Dashboard
```python
def create_mobile_dashboard(self, user_id: UUID, course_id: UUID):
    return {
        "user_id": str(user_id),
        "course_id": str(course_id),
        "layout": "mobile_optimized",
        "widgets": [
            {"type": "progress_ring", "value": progress_percentage},
            {"type": "quick_actions", "actions": quick_actions},
        ],
    }
```

#### Offline Package
```python
def create_offline_package(self, course_id: UUID, content_ids: List[UUID]):
    return {
        "course_id": str(course_id),
        "content_ids": [str(cid) for cid in content_ids],
        "estimated_size": self._estimate_package_size(content_ids),
        "validity_period": "30 days",
    }
```

### Extension Points

- Custom mobile themes
- Advanced offline sync
- Mobile-specific features
- Gesture-based navigation
- Voice interaction support

