"""Teachers module for instructor-specific functionality."""

from curriculum.teachers.course_management import CourseManagementService
from curriculum.teachers.student_management import StudentManagementService
from curriculum.teachers.teacher import TeacherService

__all__ = [
    "TeacherService",
    "CourseManagementService",
    "StudentManagementService",
]
