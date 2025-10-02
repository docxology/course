"""Tests for teachers module services."""

import pytest
from uuid import uuid4

from curriculum.core.content import Content, ContentType, ContentFormat, ContentStatus
from curriculum.core.user import User, UserRole
from curriculum.core.assessment import Assessment, Question, Submission, QuestionType, GradingStatus


class TestTeacherService:
    """Tests for TeacherService."""

    @pytest.fixture
    def teacher_service(self):
        """Create TeacherService instance."""
        from curriculum.teachers.teacher import TeacherService
        return TeacherService()

    @pytest.fixture
    def sample_instructor(self):
        """Create sample instructor."""
        return User(
            email="instructor@example.com",
            username="instructor",
            full_name="Test Instructor",
            hashed_password="hashed",
            roles=[UserRole.INSTRUCTOR],
        )

    def test_get_teacher_courses(self, teacher_service, sample_instructor):
        """Test getting teacher courses."""
        # Mock having courses
        teacher_service._teacher_courses[sample_instructor.id] = [uuid4(), uuid4()]

        courses = teacher_service.get_teacher_courses(sample_instructor.id)

        assert courses is not None
        assert len(courses) >= 2


    def test_get_course_students(self, teacher_service, sample_instructor):
        """Test getting course students."""
        course_id = uuid4()
        student_id = uuid4()

        # Mock having students
        teacher_service._course_students[course_id] = [student_id]

        students = teacher_service.get_course_students(sample_instructor.id, course_id)

        assert students is not None
        assert isinstance(students, list)


    def test_get_student_progress(self, teacher_service, sample_instructor):
        """Test getting student progress."""
        course_id = uuid4()
        student_id = uuid4()

        progress = teacher_service.get_student_progress(
            sample_instructor.id, course_id, student_id
        )

        assert progress is not None
        assert "overall_progress" in progress
        assert "quiz_scores" in progress



class TestCourseManagementService:
    """Tests for CourseManagementService."""

    @pytest.fixture
    def course_management_service(self):
        """Create CourseManagementService instance."""
        from curriculum.teachers.course_management import CourseManagementService
        return CourseManagementService()

    @pytest.fixture
    def sample_instructor(self):
        """Create sample instructor."""
        return User(
            email="instructor@example.com",
            username="instructor",
            full_name="Test Instructor",
            hashed_password="hashed",
            roles=[UserRole.INSTRUCTOR],
        )

    def test_create_course_structure(self, course_management_service, sample_instructor):
        """Test creating course structure."""
        modules = [
            {
                "title": "Module 1: Advanced Functions",
                "description": "Higher-order functions and decorators",
                "estimated_hours": 8,
                "lessons": [
                    {"title": "Lambda Functions", "content": "Lambda content"},
                    {"title": "Decorators", "content": "Decorator content"},
                ]
            },
            {
                "title": "Module 2: OOP",
                "description": "Object-oriented programming",
                "estimated_hours": 10,
                "lessons": [
                    {"title": "Classes and Objects", "content": "OOP content"},
                    {"title": "Inheritance", "content": "Inheritance content"},
                ]
            }
        ]

        structure = course_management_service.create_course_structure(
            teacher_id=sample_instructor.id,
            title="Advanced Python Course",
            description="Advanced Python concepts",
            modules=modules
        )

        assert structure is not None
        assert structure["title"] == "Advanced Python Course"
        assert len(structure["modules"]) == 2
        assert structure["total_modules"] == 2

    def test_update_course_settings(self, course_management_service, sample_instructor):
        """Test updating course settings."""
        course_id = "test_course_id"

        settings = {
            "allow_self_enrollment": True,
            "require_approval": False,
            "max_students": 25,
            "grading_scale": "letter",
            "late_submission_policy": "strict",
        }

        updated_course = course_management_service.update_course_settings(
            sample_instructor.id, course_id, settings
        )

        assert updated_course is not None
        assert updated_course["allow_self_enrollment"] is True
        assert updated_course["max_students"] == 25

    def test_get_course_content(self, course_management_service, sample_instructor):
        """Test getting course content."""
        course_id = "test_course"
        content_id = "test_content"

        # Mock having content
        course_management_service._course_content[course_id] = [content_id]

        content = course_management_service.get_course_content(sample_instructor.id, course_id)

        assert content is not None
        assert isinstance(content, list)

    def test_generate_course_report(self, course_management_service, sample_instructor):
        """Test course report generation."""
        course_id = "test_course"

        report = course_management_service.generate_course_report(
            teacher_id=sample_instructor.id,
            course_id=course_id
        )

        assert report is not None
        assert "course_id" in report
        assert "sections" in report



class TestStudentManagementService:
    """Tests for StudentManagementService."""

    @pytest.fixture
    def student_management_service(self):
        """Create StudentManagementService instance."""
        from curriculum.teachers.student_management import StudentManagementService
        return StudentManagementService()

    @pytest.fixture
    def sample_instructor(self):
        """Create sample instructor."""
        return User(
            email="instructor@example.com",
            username="instructor",
            full_name="Test Instructor",
            hashed_password="hashed",
            roles=[UserRole.INSTRUCTOR],
        )

    def test_enroll_student(self, student_management_service, sample_instructor):
        """Test student enrollment."""
        course_id = uuid4()
        student_id = uuid4()

        result = student_management_service.enroll_student(
            teacher_id=sample_instructor.id,
            course_id=course_id,
            student_id=student_id
        )

        assert result is not None
        assert result["enrollment_status"] == "active"

    def test_unenroll_student(self, student_management_service, sample_instructor):
        """Test student unenrollment."""
        course_id = uuid4()
        student_id = uuid4()

        # Enroll then unenroll
        student_management_service.enroll_student(
            teacher_id=sample_instructor.id,
            course_id=course_id,
            student_id=student_id
        )

        result = student_management_service.unenroll_student(
            teacher_id=sample_instructor.id,
            course_id=course_id,
            student_id=student_id,
            reason="Test unenrollment"
        )

        assert result is not None
        assert result["reason"] == "Test unenrollment"

    def test_get_course_roster(self, student_management_service, sample_instructor):
        """Test getting course roster."""
        course_id = uuid4()
        student_id = uuid4()

        # Mock enrollment
        student_management_service._enrollments[course_id] = [student_id]

        roster = student_management_service.get_course_roster(sample_instructor.id, course_id)

        assert roster is not None
        assert isinstance(roster, list)

    def test_track_student_engagement(self, student_management_service, sample_instructor):
        """Test student engagement tracking."""
        course_id = uuid4()
        student_id = uuid4()

        # Track engagement metrics
        result1 = student_management_service.track_student_engagement(
            sample_instructor.id, course_id, student_id
        )

        assert result1 is not None
        assert "engagement_score" in result1

    def test_identify_at_risk_students(self, student_management_service, sample_instructor):
        """Test at-risk student identification."""
        course_id = uuid4()

        # Create students with different engagement levels
        low_engagement_students = []
        for i in range(2):
            student_id = uuid4()
            low_engagement_students.append(student_id)
            student_management_service._enrollments[course_id] = [student_id]

        high_engagement_students = []
        for i in range(3):
            student_id = uuid4()
            high_engagement_students.append(student_id)
            student_management_service._enrollments[course_id] = [student_id]

        at_risk = student_management_service.get_students_needing_help(sample_instructor.id, course_id)

        assert at_risk is not None
        assert isinstance(at_risk, list)

    def test_generate_student_report(self, student_management_service, sample_instructor):
        """Test student report generation."""
        course_id = uuid4()
        student_id = uuid4()

        student_management_service._enrollments[course_id] = [student_id]

        report = student_management_service.generate_student_report(
            teacher_id=sample_instructor.id,
            course_id=course_id,
            student_id=student_id,
            report_type="comprehensive"
        )

        assert report is not None
        assert "student_id" in report
        assert "report_type" in report




