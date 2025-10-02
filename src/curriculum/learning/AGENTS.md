# AI Agents Guide - Learning Module

## Overview

The learning module encompasses all aspects of the learning experience, including assessments, analytics, progress tracking, and study tools.

## Module Structure

```
learning/
├── analytics.py    # Learning analytics and xAPI
├── assessment.py  # Assessment management
├── progress.py     # Progress tracking and paths
├── study_tools.py  # Notes, flashcards, practice
└── README.md       # Module documentation
```

## Development Guidelines

### When Working on Learning Services

1. **Follow xAPI standards** for learning events:
```python
from curriculum.core import LearningEvent, ActivityVerb, EventType

event = LearningEvent(
    user_id=user_id,
    verb=ActivityVerb.VIEWED,
    event_type=EventType.CONTENT_VIEW,
    object_id=content_id,
    object_type="content",
    success=True,
    duration=300,
)
```

2. **Implement proper assessment grading**:
```python
def grade_submission(self, submission_id: UUID, grader_id: UUID) -> Optional[Submission]:
    submission = self.get_submission(submission_id)
    if not submission:
        return None

    # Calculate scores
    total_score = 0.0
    for question_id in submission.answers:
        answer = submission.answers[question_id]
        question = self.get_question(question_id)
        score = question.calculate_score(answer)
        total_score += score

    submission.score = total_score
    submission.calculate_percentage()
    submission.graded_by = grader_id
    return submission
```

3. **Use adaptive learning algorithms**:
```python
def generate_adaptive_path(self, user_id: UUID, course_id: UUID) -> Dict[str, Any]:
    # Analyze user performance
    user_analytics = self.analytics.get_user_analytics(user_id)

    # Generate personalized path
    if user_analytics.average_score > 85:
        difficulty = "advanced"
    elif user_analytics.average_score > 70:
        difficulty = "intermediate"
    else:
        difficulty = "remedial"

    return self._create_path_for_difficulty(difficulty)
```

### Assessment Management

1. **Support multiple question types**:
```python
class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"
    ESSAY = "essay"
    CODING = "coding"
```

2. **Implement auto-grading**:
```python
def calculate_score(self, submitted_answer: Any) -> float:
    if self.question_type == QuestionType.MULTIPLE_CHOICE:
        return self.points if submitted_answer == self.correct_answer else 0.0
    elif self.question_type == QuestionType.CODING:
        return self._grade_coding_submission(submitted_answer)
```

### Analytics and Tracking

1. **Implement xAPI-compliant events**:
```python
def track_learning_event(self, user_id: UUID, event_data: Dict[str, Any]) -> LearningEvent:
    event = LearningEvent(
        user_id=user_id,
        verb=event_data["verb"],
        event_type=event_data["event_type"],
        object_id=event_data["object_id"],
        object_type=event_data["object_type"],
        success=event_data.get("success"),
        score=event_data.get("score"),
        duration=event_data.get("duration"),
    )
    self._events.append(event)
    return event
```

2. **Generate comprehensive reports**:
```python
def generate_user_report(self, user_id: UUID) -> Dict[str, Any]:
    events = self.get_events_by_user(user_id)
    analytics = self.get_user_analytics(user_id)

    return {
        "total_events": len(events),
        "content_views": len([e for e in events if e.event_type == EventType.CONTENT_VIEW]),
        "average_score": analytics.average_score if analytics else None,
        "total_time_spent": analytics.total_time_spent if analytics else 0,
    }
```

### Testing Requirements

- **Test all assessment types**
- **Test analytics calculations**
- **Test progress tracking**
- **Test adaptive algorithms**

Example test:
```python
def test_assessment_grading():
    # Create multiple choice question
    question = Question(
        title="Test Question",
        question_text="What is 2+2?",
        question_type=QuestionType.MULTIPLE_CHOICE,
        points=10.0,
        correct_answer="4",
    )

    # Test correct answer
    assert question.calculate_score("4") == 10.0

    # Test incorrect answer
    assert question.calculate_score("5") == 0.0
```

### Performance Considerations

- **Batch process analytics** for large datasets
- **Cache frequently accessed user data**
- **Use async processing** for heavy calculations
- **Implement pagination** for large result sets

### Common Patterns

#### Progress Tracking
```python
def track_content_progress(self, user_id: UUID, content_id: UUID, progress: float):
    key = f"{user_id}_{content_id}"
    self._user_progress[key] = {
        "progress_percentage": progress,
        "last_updated": datetime.utcnow(),
    }
```

#### Learning Analytics
```python
def get_learning_insights(self, user_id: UUID) -> List[str]:
    analytics = self.get_user_analytics(user_id)
    insights = []

    if analytics.average_score < 70:
        insights.append("Consider reviewing fundamental concepts")
    if analytics.total_time_spent < 100:
        insights.append("Try to spend more time on practice exercises")

    return insights
```

### Extension Points

- Custom assessment types
- Advanced analytics algorithms
- Personalized learning paths
- Study habit analysis
- Performance prediction models

