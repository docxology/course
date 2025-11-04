# AI Agents Guide - Teachers Module

## Overview

The teachers module provides instructor-specific functionality for course management, student oversight, and educational administration.

## Module Structure

```
teachers/
├── teacher.py          # Core teacher functionality
├── course_management.py # Course creation and management
├── student_management.py # Student enrollment and oversight
├── README.md           # Module documentation
└── AGENTS.md           # Development guide
```

## Development Guidelines

### When Working on Teacher Services

1. **Follow educational best practices**:
```python
def create_course_structure(self, teacher_id: UUID, title: str, modules: List[Dict]):
    course = {
        "id": str(uuid4()),
        "teacher_id": str(teacher_id),
        "title": title,
        "modules": modules,
        "learning_objectives": [
            "Understand core concepts",
            "Apply knowledge in practice",
            "Demonstrate mastery",
        ],
    }
    return course
```

2. **Implement proper student management**:
```python
def enroll_student(self, teacher_id: UUID, course_id: UUID, student_id: UUID):
    enrollment = {
        "student_id": str(student_id),
        "course_id": str(course_id),
        "enrolled_at": datetime.utcnow(),
        "status": "active",
    }

    # Add to course roster
    if course_id not in self._enrollments:
        self._enrollments[course_id] = []
    self._enrollments[course_id].append(student_id)

    return enrollment
```

3. **Provide comprehensive analytics**:
```python
def get_course_analytics(self, teacher_id: UUID, course_id: UUID):
    return {
        "total_students": 45,
        "completion_rate": 67.5,
        "average_score": 78.2,
        "engagement_metrics": {
            "daily_active_users": 32,
            "average_session_duration": 45,
        },
    }
```

### Course Management

1. **Support different course formats**:
```python
def create_course_structure(self, teacher_id: UUID, title: str, format: str):
    if format == "traditional":
        return self._create_traditional_course(teacher_id, title)
    elif format == "project_based":
        return self._create_project_course(teacher_id, title)
    elif format == "flipped_classroom":
        return self._create_flipped_course(teacher_id, title)
```

2. **Implement flexible scheduling**:
```python
def set_course_schedule(self, teacher_id: UUID, course_id: UUID, schedule: List[Dict]):
    return {
        "course_id": str(course_id),
        "schedule": schedule,
        "academic_calendar": "Spring Semester",  # Example academic term
        "time_zone": "UTC",
    }
```

### Student Management

1. **Track student progress comprehensively**:
```python
def get_student_progress(self, teacher_id: UUID, course_id: UUID, student_id: UUID):
    return {
        "overall_progress": 72.5,
        "completed_lessons": 8,
        "quiz_scores": [85, 92, 78, 88],
        "areas_for_improvement": ["Data structures"],
        "strengths": ["Python fundamentals"],
    }
```

2. **Implement early warning systems**:
```python
def get_students_needing_help(self, teacher_id: UUID, course_id: UUID):
    roster = self.get_course_roster(teacher_id, course_id)

    return [
        student for student in roster
        if student["progress"] < 50 or student["grade"] in ["D", "F"]
    ]
```

### Testing Requirements

- **Test course creation and management**
- **Test student enrollment workflows**
- **Test grade management**
- **Test analytics and reporting**
- **Test communication features**

Example test:
```python
def test_course_creation():
    course = course_service.create_course_structure(
        teacher_id=teacher_id,
        title="Data Science Fundamentals",
        modules=[module_data]
    )

    assert course["title"] == "Data Science Fundamentals"
    assert course["total_modules"] == len(module_data)
    assert course["teacher_id"] == str(teacher_id)
```

### Performance Considerations

- **Efficient roster management** for large classes
- **Cached analytics** for dashboard performance
- **Background processing** for heavy operations
- **Database optimization** for grade management

### Common Patterns

#### Student Progress Tracking
```python
def track_student_progress(self, student_id: UUID, progress_data: Dict[str, Any]):
    key = f"{student_id}_progress"
    self._student_progress[key] = {
        "overall_progress": progress_data["overall"],
        "last_updated": datetime.utcnow(),
        "risk_level": self._calculate_risk_level(progress_data),
    }
```

#### Grade Management
```python
def update_student_grade(self, student_id: UUID, assessment_id: str, grade: float):
    if student_id not in self._student_grades:
        self._student_grades[student_id] = {}

    self._student_grades[student_id][assessment_id] = {
        "grade": grade,
        "graded_at": datetime.utcnow(),
        "grade_letter": self._calculate_letter_grade(grade),
    }
```

### Extension Points

- Custom course templates
- Advanced analytics algorithms
- Integration with external grading systems
- Automated intervention systems
- Custom reporting formats


