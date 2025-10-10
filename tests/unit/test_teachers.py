"""Tests for teachers module services."""

import pytest
from uuid import uuid4

from curriculum.core.user import User, UserRole
from curriculum.teachers.teacher import TeacherService


@pytest.mark.unit
class TestTeacherService:
    """Tests for TeacherService."""

    @pytest.fixture
    def teacher_service(self):
        """Create TeacherService instance."""
        return TeacherService()

    @pytest.fixture
    def sample_teacher(self):
        """Create sample teacher."""
        return User(
            email="teacher@example.com",
            username="teacher",
            full_name="Test Teacher",
            hashed_password="hashed",
            roles=[UserRole.INSTRUCTOR],
        )

    @pytest.fixture
    def sample_student(self):
        """Create sample student."""
        return User(
            email="student@example.com",
            username="student",
            full_name="Test Student",
            hashed_password="hashed",
            roles=[UserRole.STUDENT],
        )

    def test_teacher_service_initialization(self, teacher_service):
        """Test TeacherService initialization."""
        assert teacher_service is not None
        assert isinstance(teacher_service._teacher_courses, dict)
        assert isinstance(teacher_service._course_students, dict)
        assert isinstance(teacher_service._gradebook, dict)

    def test_get_teacher_courses_empty(self, teacher_service, sample_teacher):
        """Test getting courses for teacher with no courses."""
        courses = teacher_service.get_teacher_courses(sample_teacher.id)

        assert courses is not None
        assert isinstance(courses, list)
        assert len(courses) == 0  # No courses assigned yet

    def test_get_course_students_unauthorized(self, teacher_service, sample_teacher, sample_student):
        """Test getting students for course teacher doesn't teach."""
        course_id = uuid4()
        students = teacher_service.get_course_students(sample_teacher.id, course_id)

        assert students is not None
        assert isinstance(students, list)
        assert len(students) == 0  # Teacher doesn't teach this course

    def test_get_student_progress_no_data(self, teacher_service, sample_teacher):
        """Test getting student progress with no data."""
        course_id = uuid4()
        student_id = uuid4()

        # Mock course-student relationship
        if course_id not in teacher_service._course_students:
            teacher_service._course_students[course_id] = []

        progress = teacher_service.get_student_progress(sample_teacher.id, course_id, student_id)

        assert progress is not None
        assert isinstance(progress, dict)
        assert "overall_progress" in progress
        assert "completed_lessons" in progress

    def test_create_course_announcement(self, teacher_service, sample_teacher):
        """Test creating course announcement."""
        course_id = uuid4()
        title = "Important Update"
        content = "Class is cancelled tomorrow"

        # Mock course-teacher relationship
        if course_id not in teacher_service._teacher_courses:
            teacher_service._teacher_courses[sample_teacher.id] = [course_id]

        result = teacher_service.create_course_announcement(
            teacher_id=sample_teacher.id,
            course_id=course_id,
            title=title,
            content=content
        )

        assert result is not None
        assert isinstance(result, dict)
        assert "id" in result
        assert "title" in result
        assert "content" in result
        assert result["title"] == title
        assert result["content"] == content

    def test_teacher_service_methods_exist(self, teacher_service):
        """Test that all expected methods exist."""
        required_methods = [
            "get_teacher_courses",
            "get_course_students",
            "get_student_progress",
            "create_course_announcement",
        ]

        for method_name in required_methods:
            assert hasattr(teacher_service, method_name), f"Method {method_name} not found"
            assert callable(getattr(teacher_service, method_name)), f"Method {method_name} not callable"

    def test_teacher_data_storage(self, teacher_service, sample_teacher):
        """Test teacher data storage functionality."""
        course_id = uuid4()

        # Mock course-teacher relationship
        if course_id not in teacher_service._teacher_courses:
            teacher_service._teacher_courses[sample_teacher.id] = [course_id]

        # Check that data is stored
        assert sample_teacher.id in teacher_service._teacher_courses
        assert course_id in teacher_service._teacher_courses[sample_teacher.id]

        # Test getting courses
        courses = teacher_service.get_teacher_courses(sample_teacher.id)
        assert isinstance(courses, list)
        assert len(courses) == 1  # One course assigned
