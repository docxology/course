# AI Agents Guide - Content Generation Module

## Overview

The content generation module provides automated tools for creating educational content using AI and structured templates.

## Module Structure

```
content_generation/
├── generator.py    # AI-powered content generation
├── workflow.py     # Workflow management
├── quality.py      # Quality assessment and improvement
├── README.md       # Module documentation
└── AGENTS.md       # Development guide
```

## Development Guidelines

### When Working on Content Generation

1. **Use structured templates** for consistent content:
```python
def generate_content_structure(self, content_type: str, topic: str):
    template = self._get_template(content_type)
    return {
        "title": f"{topic} - Complete Guide",
        "sections": [
            {"name": "introduction", "content": "..."},
            {"name": "main_content", "content": "..."},
            {"name": "examples", "content": "..."},
        ]
    }
```

2. **Implement quality validation**:
```python
def validate_generated_content(self, content: str, rules: Dict[str, Any]):
    issues = []

    if len(content.split()) < rules["min_words"]:
        issues.append("Content too short")

    if not any(section in content.lower() for section in rules["required_sections"]):
        issues.append("Missing required sections")

    return {"valid": len(issues) == 0, "issues": issues}
```

3. **Support workflow management**:
```python
def create_content_workflow(self, title: str, steps: List[Dict[str, Any]]):
    workflow = {
        "id": str(uuid4()),
        "title": title,
        "steps": steps,
        "assigned_users": [],
        "progress": 0,
    }
    return workflow
```

### Content Generation

1. **Support multiple content types**:
```python
def get_generation_templates(self) -> List[Dict[str, Any]]:
    return [
        {
            "id": "lesson",
            "name": "Standard Lesson",
            "structure": ["introduction", "objectives", "content", "examples", "exercises"],
        },
        {
            "id": "quiz",
            "name": "Interactive Quiz",
            "structure": ["introduction", "questions", "explanations"],
        },
    ]
```

2. **Implement AI integration**:
```python
def generate_with_ai(self, prompt: str, content_type: str):
    # Mock AI generation - in production use actual AI APIs
    return {
        "content": f"AI-generated content for {content_type}: {prompt}",
        "confidence": 0.85,
        "word_count": 250,
    }
```

### Quality Assessment

1. **Comprehensive quality metrics**:
```python
def assess_content_quality(self, content: Content) -> Dict[str, Any]:
    return {
        "overall_score": 82.5,
        "breakdown": {
            "length": {"score": 85, "issues": []},
            "structure": {"score": 90, "issues": []},
            "readability": {"score": 78, "issues": ["Long sentences"]},
            "technical": {"score": 88, "issues": []},
            "engagement": {"score": 75, "issues": ["Few examples"]},
        },
    }
```

2. **Provide actionable feedback**:
```python
def generate_recommendations(self, assessment: Dict[str, Any]) -> List[str]:
    recommendations = []

    if assessment["breakdown"]["readability"]["score"] < 80:
        recommendations.append("Simplify complex sentences")

    if assessment["breakdown"]["engagement"]["score"] < 80:
        recommendations.append("Add more examples and exercises")

    return recommendations
```

### Workflow Management

1. **Support collaborative workflows**:
```python
def assign_workflow_step(self, workflow_id: UUID, step_index: int, user_id: UUID):
    workflow = self._workflows[workflow_id]
    workflow["steps"][step_index]["assigned_to"] = str(user_id)
    workflow["steps"][step_index]["status"] = "assigned"
    return workflow["steps"][step_index]
```

2. **Track workflow progress**:
```python
def get_workflow_status(self, workflow_id: UUID) -> Dict[str, Any]:
    workflow = self._workflows[workflow_id]
    completed_steps = sum(1 for step in workflow["steps"] if step["status"] == "completed")
    progress = (completed_steps / len(workflow["steps"])) * 100
    return {"progress": progress, "current_step": workflow["current_step"]}
```

### Testing Requirements

- **Test content generation accuracy**
- **Test quality assessment algorithms**
- **Test workflow state management**
- **Test template customization**
- **Test collaborative features**

Example test:
```python
def test_content_generation():
    result = generator.generate_content(
        content_type="lesson",
        topic="Python Basics",
        difficulty="beginner"
    )

    assert "generated_content" in result
    assert result["content_type"] == "lesson"
    assert result["metadata"]["word_count"] > 0
```

### Performance Considerations

- **Efficient template processing**
- **Cached quality assessments**
- **Async workflow operations**
- **Batch content generation**

### Common Patterns

#### Template-Based Generation
```python
def generate_from_template(self, template_id: str, customizations: Dict[str, Any]):
    template = self._templates[template_id]
    content = template["structure"].copy()

    for key, value in customizations.items():
        if key in content:
            content[key] = value

    return self._render_template(content)
```

#### Quality Scoring
```python
def calculate_quality_score(self, content: Content, criteria: Dict[str, Any]):
    scores = {}

    for criterion, rules in criteria.items():
        scores[criterion] = self._assess_criterion(content, rules)

    return {
        "overall": sum(scores.values()) / len(scores),
        "breakdown": scores,
    }
```

### Extension Points

- Custom generation templates
- Advanced AI integration
- External quality assessment APIs
- Workflow automation
- Content personalization algorithms


