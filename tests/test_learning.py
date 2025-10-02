"""Tests for learning module services."""

import pytest
from unittest.mock import Mock, patch
from uuid import uuid4
from datetime import datetime, timedelta

from curriculum.core.content import Content, ContentType, ContentFormat, ContentStatus
from curriculum.core.user import User, UserRole
from curriculum.core.assessment import Assessment, Question, Submission, QuestionType, GradingStatus
from curriculum.core.analytics import LearningEvent, ActivityVerb, EventType


class TestAnalyticsService:
    """Tests for AnalyticsService."""

    @pytest.fixture
    def analytics_service(self):
        """Create AnalyticsService instance."""
        from curriculum.learning.analytics import AnalyticsService
        return AnalyticsService()

    @pytest.fixture
    def sample_user(self):
        """Create sample user."""
        return User(
            email="student@example.com",
            username="student",
            full_name="Test Student",
            hashed_password="hashed",
            roles=[UserRole.STUDENT],
        )

    @pytest.fixture
    def sample_content(self, sample_user):
        """Create sample content."""
        return Content(
            title="Analytics Content",
            content_type=ContentType.LESSON,
            format=ContentFormat.MARKDOWN,
            author_id=sample_user.id,
            description="Content for analytics testing",
        )

    def test_track_content_view(self, analytics_service, sample_user, sample_content):
        """Test tracking content view event."""
        result = analytics_service.track_content_view(
            user_id=sample_user.id,
            content_id=sample_content.id,
            duration=300,
        )

        assert result is not None
        assert hasattr(result, 'id')
        assert str(result.id) is not None

    def test_track_assessment_completion(self, analytics_service, sample_user):
        """Test tracking assessment completion."""
        assessment = Assessment(
            title="Test Assessment",
            description="Test assessment",
            time_limit=30,
            created_by=sample_user.id,
        )

        result = analytics_service.track_assessment_completion(
            user_id=sample_user.id,
            assessment_id=assessment.id,
            score=85.0,
            time_taken=25,
        )

        assert result is not None
        assert hasattr(result, 'id')
        assert str(result.id) is not None

    def test_track_user_activity(self, analytics_service, sample_user):
        """Test tracking general user activity."""
        result = analytics_service.track_event(
            user_id=sample_user.id,
            verb=ActivityVerb.VIEWED,
            event_type=EventType.USER,
            object_id=sample_user.id,
            object_type="user",
            metadata={"activity_type": "login", "ip": "192.168.1.1"},
        )

        assert result is not None
        assert hasattr(result, 'id')

    def test_get_user_events(self, analytics_service, sample_user, sample_content):
        """Test retrieving user events."""
        # Track some events first
        analytics_service.track_content_view(sample_user.id, sample_content.id)
        analytics_service.track_event(sample_user.id, ActivityVerb.VIEWED, EventType.USER, sample_user.id, "user")

        events = analytics_service.get_events_by_user(sample_user.id, limit=10)

        assert len(events) >= 2
        assert all(event.user_id == sample_user.id for event in events)

    def test_get_content_events(self, analytics_service, sample_user, sample_content):
        """Test retrieving content events."""
        # Track content events
        analytics_service.track_content_view(sample_user.id, sample_content.id)

        events = analytics_service.get_events_by_content(sample_content.id, limit=10)

        assert len(events) >= 1
        assert all(event.object_id == sample_content.id for event in events)

    def test_generate_user_report(self, analytics_service, sample_user, sample_content):
        """Test user analytics report generation."""
        # Track some activities
        analytics_service.track_content_view(sample_user.id, sample_content.id, duration=300)
        analytics_service.track_event(sample_user.id, ActivityVerb.VIEWED, EventType.USER, sample_user.id, "user")

        report = analytics_service.generate_user_report(sample_user.id)

        assert report is not None
        assert "total_events" in report
        assert "content_views" in report
        assert "average_score" in report

    def test_generate_content_report(self, analytics_service, sample_user, sample_content):
        """Test content analytics report generation."""
        # Track content interactions
        analytics_service.track_content_view(sample_user.id, sample_content.id, duration=300)

        report = analytics_service.generate_content_report(sample_content.id)

        assert report is not None
        assert "total_events" in report
        assert "content_views" in report
        assert "average_score" in report

    def test_analyze_learning_patterns(self, analytics_service, sample_user):
        """Test learning pattern analysis."""
        # Mock user events
        analytics_service.track_content_view(sample_user.id, sample_content.id, duration=300)
        analytics_service.track_event(sample_user.id, ActivityVerb.VIEWED, EventType.USER, sample_user.id, "user")

        # Get user analytics
        user_analytics = analytics_service.get_user_analytics(sample_user.id)

        assert user_analytics is not None
        assert hasattr(user_analytics, 'total_time_spent')
        assert hasattr(user_analytics, 'average_score')

    def test_get_content_analytics(self, analytics_service, sample_user, sample_content):
        """Test content analytics retrieval."""
        # Track some content views
        analytics_service.track_content_view(sample_user.id, sample_content.id, duration=300)

        content_analytics = analytics_service.get_content_analytics(sample_content.id)

        assert content_analytics is not None
        assert hasattr(content_analytics, 'total_views')
        assert hasattr(content_analytics, 'average_time_spent')


class TestAssessmentService:
    """Tests for AssessmentService."""

    @pytest.fixture
    def assessment_service(self):
        """Create AssessmentService instance."""
        from curriculum.learning.assessment import AssessmentService
        return AssessmentService()

    @pytest.fixture
    def sample_user(self):
        """Create sample user."""
        return User(
            email="instructor@example.com",
            username="instructor",
            full_name="Test Instructor",
            hashed_password="hashed",
            roles=[UserRole.INSTRUCTOR],
        )

    def test_create_assessment(self, assessment_service, sample_user):
        """Test assessment creation."""
        assessment = assessment_service.create_assessment(
            title="Python Fundamentals Quiz",
            description="Test your Python knowledge",
            time_limit=30,
        )

        assert assessment is not None
        assert assessment.title == "Python Fundamentals Quiz"

    def test_create_question(self, assessment_service):
        """Test question creation."""
        question = assessment_service.create_question(
            title="What is Python?",
            question_text="Select the correct description.",
            question_type=QuestionType.MULTIPLE_CHOICE,
            points=10.0,
            correct_answer="A programming language",
            options=[
                {"id": "a", "text": "A programming language"},
                {"id": "b", "text": "A snake"},
            ],
        )

        assert question is not None
        assert question.title == "What is Python?"
        assert question.points == 10.0

    def test_add_question_to_assessment(self, assessment_service):
        """Test adding question to assessment."""
        # Create assessment and question
        assessment = assessment_service.create_assessment(
            title="Test Assessment",
            description="Test assessment",
            time_limit=30,
        )

        question = assessment_service.create_question(
            title="Test Question",
            question_text="What is 2+2?",
            question_type=QuestionType.MULTIPLE_CHOICE,
            points=5.0,
            correct_answer="4",
            options=[{"id": "a", "text": "4"}],
        )

        # Add question to assessment
        result = assessment_service.add_question_to_assessment(assessment.id, question.id)

        assert result is True

        # Verify question was added
        questions = assessment_service.get_assessment_questions(assessment.id)
        assert len(questions) == 1
        assert questions[0].id == question.id

    def test_remove_question_from_assessment(self, assessment_service):
        """Test removing question from assessment."""
        # Create assessment and question
        assessment = assessment_service.create_assessment(
            title="Test Assessment",
            description="Test assessment",
            time_limit=30,
        )

        question = assessment_service.create_question(
            title="Test Question",
            question_text="What is 2+2?",
            question_type=QuestionType.MULTIPLE_CHOICE,
            points=5.0,
            correct_answer="4",
            options=[{"id": "a", "text": "4"}],
        )

        # Add and then remove question
        assessment_service.add_question_to_assessment(assessment.id, question.id)
        result = assessment_service.remove_question_from_assessment(assessment.id, question.id)

        assert result is True

        # Verify question was removed
        questions = assessment_service.get_assessment_questions(assessment.id)
        assert len(questions) == 0

    def test_start_submission(self, assessment_service, sample_user):
        """Test starting assessment submission."""
        assessment = assessment_service.create_assessment(
            title="Test Assessment",
            description="Test assessment",
            time_limit=30,
        )

        submission = assessment_service.start_submission(assessment.id, sample_user.id)

        assert submission is not None
        assert submission.assessment_id == assessment.id
        assert submission.user_id == sample_user.id
        assert submission.started_at is not None

    def test_submit_answer(self, assessment_service, sample_user):
        """Test submitting answer to question."""
        # Create assessment with question
        assessment = assessment_service.create_assessment(
            title="Test Assessment",
            description="Test assessment",
            time_limit=30,
        )

        question = assessment_service.create_question(
            title="Test Question",
            question_text="What is 2+2?",
            question_type=QuestionType.MULTIPLE_CHOICE,
            points=5.0,
            correct_answer="4",
            options=[{"id": "a", "text": "4"}],
        )

        assessment_service.add_question_to_assessment(assessment.id, question.id)

        # Start submission
        submission = assessment_service.start_submission(assessment.id, sample_user.id)

        # Submit answer
        result = assessment_service.submit_answer(submission.id, question.id, "4")

        assert result is True

    def test_submit_assessment(self, assessment_service, sample_user):
        """Test submitting complete assessment."""
        # Create assessment with questions
        assessment = assessment_service.create_assessment(
            title="Test Assessment",
            description="Test assessment",
            time_limit=30,
            created_by=sample_user.id,
        )

        question1 = assessment_service.create_question(
            title="Question 1",
            question_text="What is 1+1?",
            question_type=QuestionType.MULTIPLE_CHOICE,
            points=5.0,
            correct_answer="2",
            options=[{"id": "a", "text": "2"}],
        )

        question2 = assessment_service.create_question(
            title="Question 2",
            question_text="What is 2+2?",
            question_type=QuestionType.MULTIPLE_CHOICE,
            points=5.0,
            correct_answer="4",
            options=[{"id": "a", "text": "4"}],
        )

        assessment_service.add_question_to_assessment(assessment.id, question1.id)
        assessment_service.add_question_to_assessment(assessment.id, question2.id)

        # Start and submit
        submission = assessment_service.start_submission(assessment.id, sample_user.id)

        # Submit answers
        assessment_service.submit_answer(submission.id, question1.id, "2")
        assessment_service.submit_answer(submission.id, question2.id, "4")

        # Submit assessment
        result = assessment_service.submit_assessment(submission.id)

        assert result is not None
        assert result.status == GradingStatus.PENDING

    def test_grade_submission(self, assessment_service, sample_user):
        """Test submission grading."""
        # Create and submit assessment
        assessment = assessment_service.create_assessment(
            title="Test Assessment",
            description="Test assessment",
            time_limit=30,
            created_by=sample_user.id,
        )

        question = assessment_service.create_question(
            title="Test Question",
            question_text="What is 2+2?",
            question_type=QuestionType.MULTIPLE_CHOICE,
            points=10.0,
            correct_answer="4",
            options=[{"id": "a", "text": "4"}],
        )

        assessment_service.add_question_to_assessment(assessment.id, question.id)

        submission = assessment_service.start_submission(assessment.id, sample_user.id)
        assessment_service.submit_answer(submission.id, question.id, "4")
        assessment_service.submit_assessment(submission.id)

        # Grade submission
        graded_submission = assessment_service.grade_submission(submission.id)

        assert graded_submission is not None
        assert graded_submission.status == GradingStatus.GRADED
        assert graded_submission.score is not None

    def test_get_user_submissions(self, assessment_service, sample_user):
        """Test retrieving user submissions."""
        assessment = assessment_service.create_assessment(
            title="Test Assessment",
            description="Test assessment",
            time_limit=30,
            created_by=sample_user.id,
        )

        # Create submission
        submission = assessment_service.start_submission(assessment.id, sample_user.id)

        # Get user submissions
        submissions = assessment_service.get_user_submissions(sample_user.id)

        assert len(submissions) >= 1
        assert all(s.user_id == sample_user.id for s in submissions)

    def test_get_assessment_statistics(self, assessment_service, sample_user):
        """Test assessment statistics."""
        assessment = assessment_service.create_assessment(
            title="Test Assessment",
            description="Test assessment",
            time_limit=30,
            created_by=sample_user.id,
        )

        # Create some submissions
        for i in range(3):
            student = User(
                email=f"student{i}@example.com",
                username=f"student{i}",
                full_name=f"Student {i}",
                hashed_password="hashed",
                roles=[UserRole.STUDENT],
            )

            submission = assessment_service.start_submission(assessment.id, student.id)

            # Submit with different scores
            if i == 0:
                assessment_service.submit_answer(submission.id, "q1", "correct")
            elif i == 1:
                assessment_service.submit_answer(submission.id, "q1", "wrong")

            assessment_service.submit_assessment(submission.id)

        # Get statistics
        stats = assessment_service.get_assessment_statistics(assessment.id)

        assert stats is not None
        assert "total_submissions" in stats
        assert "average_score" in stats
        assert "completion_rate" in stats


class TestProgressService:
    """Tests for ProgressService."""

    @pytest.fixture
    def progress_service(self):
        """Create ProgressService instance."""
        from curriculum.learning.progress import ProgressService
        return ProgressService()

    @pytest.fixture
    def sample_user(self):
        """Create sample user."""
        return User(
            email="student@example.com",
            username="student",
            full_name="Test Student",
            hashed_password="hashed",
            roles=[UserRole.STUDENT],
        )

    def test_track_content_progress(self, progress_service, sample_user):
        """Test content progress tracking."""
        content_id = uuid4()

        # Track progress
        progress_service.track_content_progress(
            user_id=sample_user.id,
            content_id=content_id,
            progress_percentage=50.0,
            time_spent=300,
        )

        # Get progress
        progress = progress_service.get_content_progress(sample_user.id, content_id)

        assert progress is not None
        assert progress["progress_percentage"] == 50.0
        assert progress["time_spent"] == 300

    def test_calculate_learning_path(self, progress_service, sample_user):
        """Test learning path calculation."""
        # Mock completed content
        completed_content = [uuid4(), uuid4()]

        # Mock available content
        available_content = [
            {"id": uuid4(), "difficulty": "beginner", "prerequisites": []},
            {"id": uuid4(), "difficulty": "intermediate", "prerequisites": [completed_content[0]]},
            {"id": uuid4(), "difficulty": "advanced", "prerequisites": completed_content},
        ]

        path = progress_service.calculate_learning_path(
            sample_user.id,
            completed_content,
            available_content
        )

        assert path is not None
        assert "recommended_order" in path
        assert "estimated_completion_time" in path

    def test_get_user_progress_summary(self, progress_service, sample_user):
        """Test user progress summary."""
        # Track some progress
        progress_service.track_content_progress(sample_user.id, uuid4(), 100.0, 600)
        progress_service.track_content_progress(sample_user.id, uuid4(), 75.0, 450)

        summary = progress_service.get_user_progress_summary(sample_user.id)

        assert summary is not None
        assert "total_content_completed" in summary
        assert "total_time_spent" in summary
        assert "average_progress" in summary

    def test_identify_learning_gaps(self, progress_service, sample_user):
        """Test learning gap identification."""
        # Mock user progress data
        progress_data = {
            "completed_topics": ["python_basics", "variables"],
            "weak_areas": ["functions", "classes"],
            "strong_areas": ["syntax", "data_types"],
        }

        gaps = progress_service.identify_learning_gaps(sample_user.id, progress_data)

        assert gaps is not None
        assert "gaps" in gaps
        assert "recommendations" in gaps
        assert len(gaps["gaps"]) > 0


class TestStudyToolsService:
    """Tests for StudyToolsService."""

    @pytest.fixture
    def study_tools_service(self):
        """Create StudyToolsService instance."""
        from curriculum.learning.study_tools import StudyToolsService
        return StudyToolsService()

    @pytest.fixture
    def sample_user(self):
        """Create sample user."""
        return User(
            email="student@example.com",
            username="student",
            full_name="Test Student",
            hashed_password="hashed",
            roles=[UserRole.STUDENT],
        )

    def test_generate_flashcards(self, study_tools_service, sample_user):
        """Test flashcard generation."""
        content = Content(
            title="Python Basics",
            content_type=ContentType.LESSON,
            format=ContentFormat.MARKDOWN,
            author_id=sample_user.id,
            content_body="# Python Basics\n\nVariables store data.\nFunctions are reusable code blocks.",
        )

        flashcards = study_tools_service.generate_flashcards(content.id, count=3)

        assert flashcards is not None
        assert "flashcards" in flashcards
        assert len(flashcards["flashcards"]) == 3
        assert all("question" in card and "answer" in card for card in flashcards["flashcards"])

    def test_create_study_plan(self, study_tools_service, sample_user):
        """Test study plan creation."""
        goals = ["Learn Python", "Build a web app", "Understand databases"]
        available_time = 10  # hours per week

        plan = study_tools_service.create_study_plan(
            sample_user.id,
            goals,
            available_time
        )

        assert plan is not None
        assert "daily_schedule" in plan
        assert "weekly_goals" in plan
        assert "milestones" in plan

    def test_generate_practice_exercises(self, study_tools_service):
        """Test practice exercise generation."""
        topic = "Python Functions"

        exercises = study_tools_service.generate_practice_exercises(topic, difficulty="beginner")

        assert exercises is not None
        assert "exercises" in exercises
        assert len(exercises["exercises"]) > 0
        assert all("problem" in ex and "solution" in ex for ex in exercises["exercises"])

    def test_analyze_study_effectiveness(self, study_tools_service, sample_user):
        """Test study effectiveness analysis."""
        # Mock study session data
        sessions = [
            {"date": datetime.utcnow(), "duration": 60, "content_completed": 2, "score": 85},
            {"date": datetime.utcnow() - timedelta(days=1), "duration": 45, "content_completed": 1, "score": 90},
        ]

        analysis = study_tools_service.analyze_study_effectiveness(sample_user.id, sessions)

        assert analysis is not None
        assert "effectiveness_score" in analysis
        assert "improvement_areas" in analysis
        assert "study_patterns" in analysis


class TestLearningIntegration:
    """Integration tests for learning module."""

    def test_complete_learning_workflow(self, analytics_service, assessment_service, progress_service, sample_user, sample_content):
        """Test complete learning workflow."""
        # 1. User views content
        analytics_service.track_content_view(sample_user.id, sample_content.id, duration=300)

        # 2. Track progress
        progress_service.track_content_progress(sample_user.id, sample_content.id, 100.0, 300)

        # 3. Create and take assessment
        assessment = assessment_service.create_assessment(
            title="Content Assessment",
            description="Test understanding of content",
            time_limit=30,
            created_by=sample_user.id,
        )

        submission = assessment_service.start_submission(assessment.id, sample_user.id)
        assessment_service.submit_assessment(submission.id)

        # 4. Generate reports
        user_report = analytics_service.generate_user_report(sample_user.id)
        content_report = analytics_service.generate_content_report(sample_content.id)

        assert user_report is not None
        assert content_report is not None

    def test_adaptive_learning_flow(self, analytics_service, progress_service, sample_user):
        """Test adaptive learning flow."""
        # Track user performance
        analytics_service.track_user_activity(sample_user.id, "quiz_completed", {"score": 75})

        # Analyze learning patterns
        patterns = analytics_service.analyze_learning_patterns(sample_user.id, [])

        # Generate adaptive path
        path = progress_service.calculate_learning_path(
            sample_user.id,
            [],  # No completed content yet
            []   # No available content yet
        )

        assert patterns is not None
        assert path is not None

    @patch('curriculum.learning.analytics.requests')
    def test_external_analytics_integration(self, mock_requests, analytics_service, sample_user):
        """Test external analytics service integration."""
        # Mock external API response
        mock_requests.post.return_value.json.return_value = {"status": "success"}

        # Send analytics data to external service
        result = analytics_service.send_to_external_analytics(
            sample_user.id,
            {"event": "content_viewed", "timestamp": datetime.utcnow()}
        )

        assert result is not None
        mock_requests.post.assert_called_once()

    def test_get_user_analytics(self, analytics_service, sample_user, sample_content):
        """Test user analytics retrieval."""
        # Track some events
        analytics_service.track_content_view(sample_user.id, sample_content.id, duration=300)

        user_analytics = analytics_service.get_user_analytics(sample_user.id)

        assert user_analytics is not None
        assert hasattr(user_analytics, 'total_time_spent')
        assert hasattr(user_analytics, 'average_score')

    def test_assessment_analytics_integration(self, analytics_service, assessment_service, sample_user):
        """Test assessment and analytics integration."""
        # Create assessment
        assessment = assessment_service.create_assessment(
            title="Integration Test",
            description="Test assessment-analytics integration",
            time_limit=30,
            created_by=sample_user.id,
        )

        # Track assessment completion
        analytics_service.track_assessment_completion(
            user_id=sample_user.id,
            assessment_id=assessment.id,
            score=85.0,
            passed=True
        )

        # Get analytics
        events = analytics_service.get_user_events(sample_user.id)

        assert len(events) > 0
        assessment_events = [e for e in events if e.object_id == assessment.id]
        assert len(assessment_events) > 0

