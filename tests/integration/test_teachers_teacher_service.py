"""Tests for Teacher Service."""

import pytest
from uuid import uuid4

from curriculum.teachers.teacher import TeacherService


@pytest.mark.integration
class TestTeacherService:
    """Tests for TeacherService."""

    @pytest.fixture
    def teacher_service(self):
        """Teacher service fixture."""
        return TeacherService()

    def test_get_teacher_courses(self, teacher_service):
        """Test getting teacher's courses."""
        teacher_id = uuid4()
        courses = teacher_service.get_teacher_courses(teacher_id)

        assert isinstance(courses, list)
        assert len(courses) >= 0

        if courses:
            course = courses[0]
            assert "id" in course
            assert "title" in course
            assert "enrolled_students" in course

    def test_get_course_students(self, teacher_service):
        """Test getting course students."""
        teacher_id = uuid4()
        course_id = uuid4()
        students = teacher_service.get_course_students(teacher_id, course_id)

        assert isinstance(students, list)

        if students:
            student = students[0]
            assert "id" in student
            assert "name" in student
            assert "email" in student
            assert "progress" in student

    def test_get_student_progress(self, teacher_service):
        """Test getting student progress."""
        teacher_id = uuid4()
        course_id = uuid4()
        student_id = uuid4()

        progress = teacher_service.get_student_progress(teacher_id, course_id, student_id)

        assert "student_id" in progress
        assert "course_id" in progress
        assert "overall_progress" in progress
        assert "completed_lessons" in progress
        assert "quiz_scores" in progress

    def test_create_course_announcement(self, teacher_service):
        """Test creating course announcement."""
        teacher_id = uuid4()
        course_id = uuid4()

        announcement = teacher_service.create_course_announcement(
            teacher_id=teacher_id,
            course_id=course_id,
            title="Test Announcement",
            content="This is a test announcement",
            priority="normal"
        )

        assert announcement["teacher_id"] == str(teacher_id)
        assert announcement["course_id"] == str(course_id)
        assert announcement["title"] == "Test Announcement"
        assert announcement["content"] == "This is a test announcement"
        assert announcement["priority"] == "normal"

    def test_schedule_office_hours(self, teacher_service):
        """Test scheduling office hours."""
        teacher_id = uuid4()
        course_id = uuid4()

        schedule = {
            "day": "Monday",
            "start_time": "14:00",
            "end_time": "16:00",
            "location": "Virtual",
            "is_recurring": True,
            "max_students": 10
        }

        office_hours = teacher_service.schedule_office_hours(
            teacher_id=teacher_id,
            course_id=course_id,
            schedule=schedule
        )

        assert office_hours["teacher_id"] == str(teacher_id)
        assert office_hours["course_id"] == str(course_id)
        assert office_hours["schedule"] == schedule

    def test_get_pending_submissions(self, teacher_service):
        """Test getting pending submissions."""
        teacher_id = uuid4()
        course_id = uuid4()

        submissions = teacher_service.get_pending_submissions(teacher_id, course_id)

        assert isinstance(submissions, list)

        for submission in submissions:
            assert "id" in submission
            assert "student_name" in submission
            assert "assignment_title" in submission
            assert "submitted_at" in submission

    def test_get_course_analytics(self, teacher_service):
        """Test getting course analytics."""
        teacher_id = uuid4()
        course_id = uuid4()

        analytics = teacher_service.get_course_analytics(teacher_id, course_id)

        assert "course_id" in analytics
        assert "total_students" in analytics
        assert "completion_rate" in analytics
        assert "average_score" in analytics
        assert "engagement_metrics" in analytics

    def test_send_message_to_student(self, teacher_service):
        """Test sending message to student."""
        teacher_id = uuid4()
        student_id = uuid4()

        message = teacher_service.send_message_to_student(
            teacher_id=teacher_id,
            student_id=student_id,
            subject="Test Subject",
            message="Test message content"
        )

        assert message["sender_id"] == str(teacher_id)
        assert message["recipient_id"] == str(student_id)
        assert message["subject"] == "Test Subject"
        assert message["content"] == "Test message content"

    def test_create_assignment_rubric(self, teacher_service):
        """Test creating assignment rubric."""
        teacher_id = uuid4()
        course_id = uuid4()

        criteria = [
            {"name": "Correctness", "points": 40, "description": "Technical accuracy"},
            {"name": "Clarity", "points": 30, "description": "Clear presentation"},
            {"name": "Completeness", "points": 30, "description": "Complete solution"}
        ]

        rubric = teacher_service.create_assignment_rubric(
            teacher_id=teacher_id,
            course_id=course_id,
            title="Test Rubric",
            criteria=criteria
        )

        assert rubric["teacher_id"] == str(teacher_id)
        assert rubric["course_id"] == str(course_id)
        assert rubric["title"] == "Test Rubric"
        assert rubric["criteria"] == criteria
        assert rubric["total_points"] == 100

    def test_generate_grade_report(self, teacher_service):
        """Test generating grade report."""
        teacher_id = uuid4()
        course_id = uuid4()

        report = teacher_service.generate_grade_report(
            teacher_id=teacher_id,
            course_id=course_id,
            format="pdf"
        )

        assert report["teacher_id"] == str(teacher_id)
        assert report["course_id"] == str(course_id)
        assert report["format"] == "pdf"
        assert "download_url" in report

    def test_get_teacher_dashboard(self, teacher_service):
        """Test getting teacher dashboard."""
        teacher_id = uuid4()

        dashboard = teacher_service.get_teacher_dashboard(teacher_id)

        assert dashboard["teacher_id"] == str(teacher_id)
        assert "courses_count" in dashboard
        assert "total_students" in dashboard
        assert "pending_gradings" in dashboard
        assert "upcoming_deadlines" in dashboard

    def test_moderate_discussion_post(self, teacher_service):
        """Test moderating discussion post."""
        teacher_id = uuid4()
        post_id = "test_post_123"

        moderation = teacher_service.moderate_discussion_post(
            teacher_id=teacher_id,
            post_id=post_id,
            action="approve",
            reason="Good content"
        )

        assert moderation["post_id"] == post_id
        assert moderation["teacher_id"] == str(teacher_id)
        assert moderation["action"] == "approve"
        assert moderation["reason"] == "Good content"

    def test_create_course_calendar(self, teacher_service):
        """Test creating course calendar."""
        teacher_id = uuid4()
        course_id = uuid4()

        events = [
            {"title": "Week 1", "date": "2024-01-15T09:00:00Z", "type": "lesson"},
            {"title": "Assignment 1", "date": "2024-01-22T23:59:59Z", "type": "deadline"}
        ]

        calendar = teacher_service.create_course_calendar(
            teacher_id=teacher_id,
            course_id=course_id,
            events=events
        )

        assert calendar["teacher_id"] == str(teacher_id)
        assert calendar["course_id"] == str(course_id)
        assert calendar["events"] == events

    def test_get_student_analytics(self, teacher_service):
        """Test getting student analytics."""
        teacher_id = uuid4()
        course_id = uuid4()
        student_id = uuid4()

        analytics = teacher_service.get_student_analytics(teacher_id, course_id, student_id)

        assert analytics["student_id"] == str(student_id)
        assert analytics["course_id"] == str(course_id)
        assert "engagement_score" in analytics
        assert "study_patterns" in analytics
        assert "performance_trends" in analytics

    def test_export_course_data(self, teacher_service):
        """Test exporting course data."""
        teacher_id = uuid4()
        course_id = uuid4()

        export_data = teacher_service.export_course_data(
            teacher_id=teacher_id,
            course_id=course_id,
            export_type="complete"
        )

        assert export_data["teacher_id"] == str(teacher_id)
        assert export_data["course_id"] == str(course_id)
        assert export_data["export_type"] == "complete"
        assert "download_url" in export_data


