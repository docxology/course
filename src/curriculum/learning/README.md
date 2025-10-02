# Learning Module

The learning module encompasses all aspects of the learning experience, including assessments, analytics, progress tracking, and study tools.

## Services

- `AssessmentService`: Quiz and exam management
- `AnalyticsService`: Learning event tracking and reporting
- `ProgressService`: Learning progress and paths
- `StudyToolsService`: Notes, flashcards, and practice

## Features

- Multiple question types (MCQ, True/False, Essay, Coding)
- xAPI-compliant learning event tracking
- Adaptive learning paths
- Progress visualization
- Study session tracking
- Flashcard spaced repetition

## Usage

```python
from curriculum.learning import AssessmentService, AnalyticsService

assessment_service = AssessmentService()
analytics_service = AnalyticsService()

# Create assessment
assessment = assessment_service.create_assessment(
    title="Python Quiz",
    content_id=content_id,
)

# Track learning event
analytics_service.track_content_view(user_id, content_id, duration=300)
```

## Testing

```bash
pytest tests/test_learning/
```

