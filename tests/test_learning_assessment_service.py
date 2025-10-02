"""Tests for Assessment Service."""

import pytest
from uuid import uuid4

from curriculum.core.assessment import QuestionType, GradingStatus


class TestAssessmentService:
    """Tests for AssessmentService."""

    def test_create_assessment(self, assessment_service):
        """Test creating an assessment."""
        assessment = assessment_service.create_assessment(
            title="Math Test",
            description="Test your math skills",
            time_limit=60,
        )

        assert assessment is not None
        assert assessment.title == "Math Test"
        assert assessment.time_limit == 60

    def test_get_assessment(self, assessment_service, sample_assessment):
        """Test retrieving an assessment."""
        retrieved = assessment_service.get_assessment(sample_assessment.id)

        assert retrieved is not None
        assert retrieved.id == sample_assessment.id

    def test_create_question(self, assessment_service):
        """Test creating a question."""
        question = assessment_service.create_question(
            title="Basic Math",
            question_text="What is 5 + 3?",
            question_type=QuestionType.MULTIPLE_CHOICE,
            points=5.0,
            correct_answer="8",
            options=[
                {"id": "a", "text": "7"},
                {"id": "b", "text": "8"},
                {"id": "c", "text": "9"},
            ],
        )

        assert question is not None
        assert question.points == 5.0
        assert question.correct_answer == "8"

    def test_add_question_to_assessment(
        self, assessment_service, sample_assessment, sample_question
    ):
        """Test adding a question to an assessment."""
        updated = assessment_service.add_question_to_assessment(
            sample_assessment.id,
            sample_question.id,
        )

        assert updated is not None
        assert sample_question.id in updated.question_ids
        assert updated.total_points >= sample_question.points

    def test_remove_question_from_assessment(
        self, assessment_service, sample_assessment, sample_question
    ):
        """Test removing a question from an assessment."""
        # First add the question
        assessment_service.add_question_to_assessment(
            sample_assessment.id,
            sample_question.id,
        )

        # Then remove it
        updated = assessment_service.remove_question_from_assessment(
            sample_assessment.id,
            sample_question.id,
        )

        assert updated is not None
        assert sample_question.id not in updated.question_ids

    def test_start_submission(self, assessment_service, sample_assessment, sample_user):
        """Test starting a submission."""
        submission = assessment_service.start_submission(
            sample_assessment.id,
            sample_user.id,
            attempt_number=1,
        )

        assert submission is not None
        assert submission.assessment_id == sample_assessment.id
        assert submission.user_id == sample_user.id
        assert submission.attempt_number == 1

    def test_submit_answer(self, assessment_service, sample_assessment, sample_user, sample_question):
        """Test submitting an answer."""
        submission = assessment_service.start_submission(
            sample_assessment.id,
            sample_user.id,
        )

        updated = assessment_service.submit_answer(
            submission.id,
            sample_question.id,
            "A high-level programming language",
        )

        assert updated is not None
        assert str(sample_question.id) in updated.answers

    def test_submit_assessment(
        self, assessment_service, sample_assessment, sample_user
    ):
        """Test submitting complete assessment."""
        submission = assessment_service.start_submission(
            sample_assessment.id,
            sample_user.id,
        )

        updated = assessment_service.submit_assessment(submission.id)

        assert updated is not None
        assert updated.submitted_at is not None
        assert updated.grading_status == GradingStatus.PENDING

    def test_grade_submission(
        self, assessment_service, sample_assessment, sample_user, sample_question
    ):
        """Test grading a submission."""
        # Add question to assessment
        assessment_service.add_question_to_assessment(
            sample_assessment.id,
            sample_question.id,
        )

        # Start and submit
        submission = assessment_service.start_submission(
            sample_assessment.id,
            sample_user.id,
        )
        assessment_service.submit_answer(
            submission.id,
            sample_question.id,
            "A high-level programming language",
        )
        assessment_service.submit_assessment(submission.id)

        # Grade
        grader_id = uuid4()
        graded = assessment_service.grade_submission(submission.id, grader_id)

        assert graded is not None
        assert graded.score is not None
        assert graded.grading_status == GradingStatus.COMPLETED
        assert graded.graded_by == grader_id

    def test_get_user_submissions(
        self, assessment_service, sample_assessment, sample_user
    ):
        """Test getting user submissions."""
        # Create multiple submissions
        for i in range(3):
            assessment_service.start_submission(
                sample_assessment.id,
                sample_user.id,
                attempt_number=i + 1,
            )

        submissions = assessment_service.get_user_submissions(sample_user.id)

        assert len(submissions) >= 3

    def test_get_assessment_statistics(
        self, assessment_service, sample_assessment, sample_user, sample_question
    ):
        """Test getting assessment statistics."""
        # Add question
        assessment_service.add_question_to_assessment(
            sample_assessment.id,
            sample_question.id,
        )

        # Create and grade submission
        submission = assessment_service.start_submission(
            sample_assessment.id,
            sample_user.id,
        )
        assessment_service.submit_answer(
            submission.id,
            sample_question.id,
            "A high-level programming language",
        )
        assessment_service.submit_assessment(submission.id)
        assessment_service.grade_submission(submission.id, uuid4())

        stats = assessment_service.get_assessment_statistics(sample_assessment.id)

        assert stats["total_submissions"] >= 1
        assert "average_score" in stats
        assert "pass_rate" in stats
