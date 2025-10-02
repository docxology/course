# Teachers Module

The teachers module provides instructor-specific functionality for course management, student oversight, and educational administration.

## Services

- `TeacherService`: Core teacher functionality and dashboard
- `CourseManagementService`: Course creation, content management, and scheduling
- `StudentManagementService`: Student enrollment, grading, and progress tracking

## Features

- Course creation and management
- Student enrollment and oversight
- Grade management and reporting
- Student progress tracking
- Course analytics and insights
- Communication with students
- Assignment and assessment management

## Usage

```python
from curriculum.teachers import TeacherService, CourseManagementService

teacher_service = TeacherService()
course_service = CourseManagementService()

# Get teacher's courses
courses = teacher_service.get_teacher_courses(teacher_id)

# Create course structure
course = course_service.create_course_structure(
    teacher_id=teacher_id,
    title="Python Programming",
    description="Learn Python from basics to advanced",
    modules=[module_data]
)

# Enroll students
enrollment = student_service.enroll_student(
    teacher_id=teacher_id,
    course_id=course_id,
    student_id=student_id
)
```

## Testing

```bash
pytest tests/test_teachers/
```


