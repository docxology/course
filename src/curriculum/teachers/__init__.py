"""Teachers module for instructor-specific functionality."""

from curriculum.teachers.teacher import TeacherService
from curriculum.teachers.course_management import CourseManagementService
from curriculum.teachers.student_management import StudentManagementService

__all__ = [
    "TeacherService",
    "CourseManagementService",
    "StudentManagementService",
]


