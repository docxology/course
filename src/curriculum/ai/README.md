# AI Module

The AI module provides intelligent features for content creation, tutoring, and personalized learning experiences.

## Services

- `AIFeaturesService`: Intelligent tutoring and recommendations
- `ContentCreationService`: AI-assisted content generation
- `ResearchToolsService`: Citation and bibliography management

## Features

- Content difficulty analysis
- Personalized learning recommendations
- AI-assisted content generation
- Automated grading and feedback
- Research citation management
- Learning style assessment

## Usage

```python
from curriculum.ai import AIFeaturesService, ContentCreationService

ai_service = AIFeaturesService()
content_creation = ContentCreationService()

# Analyze content difficulty
analysis = ai_service.analyze_content_difficulty(content)

# Generate content with AI
generated = content_creation.generate_content_with_ai(
    assistant_id="content_writer",
    prompt="Write a lesson about variables",
)
```

## Testing

```bash
pytest tests/integration/test_ai.py
pytest tests/integration/test_ai_content_creation_service.py
```

