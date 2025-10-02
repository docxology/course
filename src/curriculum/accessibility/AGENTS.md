# AI Agents Guide - Accessibility Module

## Overview

The accessibility module ensures inclusive learning experiences for all users.

## Module Structure

```
accessibility/
├── accessibility.py # WCAG compliance and accessibility features
└── README.md        # Module documentation
```

## Development Guidelines

### When Working on Accessibility Features

1. **Follow WCAG 2.1 guidelines**:
```python
def analyze_content_accessibility(self, content: Content) -> Dict[str, Any]:
    issues = []

    # Check for alt text
    if "<img" in content.content_body and "alt=" not in content.content_body:
        issues.append("Missing alt text for images")

    # Check heading structure
    if not any(h in content.content_body for h in ["<h1", "<h2", "<h3"]):
        issues.append("Missing heading structure")

    return {
        "compliance_level": "WCAG 2.1 AA" if len(issues) == 0 else "Needs improvement",
        "issues": issues,
    }
```

2. **Implement screen reader support**:
```python
def generate_screen_reader_content(self, content: Content, user_profile: Dict[str, Any]):
    return f"""
Course: {content.title}
Content Type: {content.content_type.value}

Main Content:
{content.content_body}

Navigation: Use arrow keys to navigate sections.
"""
```

3. **Add keyboard navigation**:
```python
def validate_keyboard_navigation(self, html_content: str) -> Dict[str, Any]:
    issues = []

    if "tabindex" not in html_content:
        issues.append("Missing tabindex attributes")

    if "<a href=\"#main\"" not in html_content:
        issues.append("Missing skip navigation links")

    return {"valid": len(issues) == 0, "issues": issues}
```

### Accessibility Standards

1. **WCAG 2.1 compliance**:
```python
def get_accessibility_guidelines(self, standard: str = "wcag"):
    if standard == "wcag":
        return {
            "principles": [
                {
                    "name": "Perceivable",
                    "guidelines": [
                        "Provide text alternatives for images",
                        "Provide captions for multimedia",
                        "Use sufficient color contrast",
                    ],
                },
                {
                    "name": "Operable",
                    "guidelines": [
                        "Make functionality keyboard accessible",
                        "Provide sufficient time limits",
                    ],
                },
                # ... other principles
            ],
        }
```

2. **User preferences**:
```python
def create_accessibility_profile(self, user_id: UUID, preferences: Dict[str, Any]):
    return {
        "user_id": str(user_id),
        "visual_preferences": {
            "font_size": preferences.get("font_size", "medium"),
            "high_contrast": preferences.get("high_contrast", False),
        },
        "audio_preferences": {
            "screen_reader": preferences.get("screen_reader", False),
            "speech_rate": preferences.get("speech_rate", 1.0),
        },
    }
```

### Testing Requirements

- **Test WCAG compliance**
- **Test screen reader compatibility**
- **Test keyboard navigation**
- **Test with assistive technologies**

Example test:
```python
def test_accessibility_analysis():
    content = Content(content_body="<img src='test.jpg'>No alt text</img>")

    analysis = accessibility_service.analyze_content_accessibility(content)

    assert "Missing alt text" in analysis["issues"]
    assert analysis["compliance_level"] == "Needs improvement"
```

### Performance Considerations

- **Lightweight accessibility checks**
- **Cached analysis results**
- **Async processing** for heavy analysis
- **Minimal impact** on user experience

### Common Patterns

#### Content Analysis
```python
def analyze_content_accessibility(self, content: Content) -> Dict[str, Any]:
    issues = []

    # Check various accessibility criteria
    if not self._has_alt_text(content.content_body):
        issues.append("Missing alt text")

    if not self._has_proper_headings(content.content_body):
        issues.append("Missing heading structure")

    return {
        "issues": issues,
        "score": max(0, 100 - len(issues) * 10),
    }
```

#### User Profiles
```python
def create_accessibility_profile(self, user_id: UUID, preferences: Dict[str, Any]):
    profile = {
        "visual": preferences.get("visual", {}),
        "audio": preferences.get("audio", {}),
        "motor": preferences.get("motor", {}),
        "cognitive": preferences.get("cognitive", {}),
    }
    return profile
```

### Extension Points

- Custom accessibility standards
- Advanced screen reader support
- Sign language integration
- Braille output support
- Cognitive accessibility features

