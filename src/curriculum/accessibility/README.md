# Accessibility Module

The accessibility module ensures inclusive learning experiences for all users.

## Services

- `AccessibilityService`: WCAG compliance and accessibility features

## Features

- WCAG 2.1 compliance checking
- Screen reader support
- Keyboard navigation validation
- High contrast mode support
- Audio descriptions
- Sign language support (planned)
- Braille output (planned)

## Usage

```python
from curriculum.accessibility import AccessibilityService

accessibility = AccessibilityService()

# Analyze content accessibility
analysis = accessibility.analyze_content_accessibility(content)

# Create accessible version
accessible_content = accessibility.create_accessible_version(
    content_id=content.id,
    accessibility_features=user_preferences,
)
```

## Testing

```bash
pytest tests/integration/test_accessibility.py
```

