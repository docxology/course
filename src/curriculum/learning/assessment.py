"""Assessment and evaluation service."""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID

from curriculum.core.assessment import (
    Assessment,
    Question,
    Submission,
    SubmissionResult,
    QuestionType,
    GradingStatus,
)


class AssessmentService:
    """Service for managing assessments and evaluations."""

    def __init__(self) -> None:
        """Initialize assessment service."""
        self._assessments: dict[UUID, Assessment] = {}
        self._questions: dict[UUID, Question] = {}
        self._submissions: dict[UUID, Submission] = {}

    def create_assessment(
        self,
        title: str,
        description: Optional[str] = None,
        content_id: Optional[UUID] = None,
        time_limit: Optional[int] = None,
    ) -> Assessment:
        """Create a new assessment."""
        assessment = Assessment(
            title=title,
            description=description,
            content_id=content_id,
            time_limit=time_limit,
        )
        self._assessments[assessment.id] = assessment
        return assessment

    def get_assessment(self, assessment_id: UUID) -> Optional[Assessment]:
        """Get assessment by ID."""
        return self._assessments.get(assessment_id)

    def create_question(
        self,
        title: str,
        question_text: str,
        question_type: QuestionType,
        points: float,
        correct_answer: Optional[Any] = None,
        options: Optional[List[Dict[str, Any]]] = None,
    ) -> Question:
        """Create a new question."""
        question = Question(
            title=title,
            question_text=question_text,
            question_type=question_type,
            points=points,
            correct_answer=correct_answer,
            options=options or [],
        )
        self._questions[question.id] = question
        return question

    def get_question(self, question_id: UUID) -> Optional[Question]:
        """Get question by ID."""
        return self._questions.get(question_id)

    def add_question_to_assessment(
        self, assessment_id: UUID, question_id: UUID
    ) -> Optional[Assessment]:
        """Add a question to an assessment."""
        assessment = self.get_assessment(assessment_id)
        question = self.get_question(question_id)

        if not assessment or not question:
            return None

        if question_id not in assessment.question_ids:
            assessment.question_ids.append(question_id)
            assessment.question_order.append(question_id)
            assessment.total_points += question.points
            assessment.update_timestamp()

        return assessment

    def remove_question_from_assessment(
        self, assessment_id: UUID, question_id: UUID
    ) -> Optional[Assessment]:
        """Remove a question from an assessment."""
        assessment = self.get_assessment(assessment_id)
        question = self.get_question(question_id)

        if not assessment or not question:
            return None

        if question_id in assessment.question_ids:
            assessment.question_ids.remove(question_id)
            assessment.question_order.remove(question_id)
            assessment.total_points -= question.points
            assessment.update_timestamp()

        return assessment

    def start_submission(
        self, assessment_id: UUID, user_id: UUID, attempt_number: int = 1
    ) -> Optional[Submission]:
        """Start a new submission for an assessment."""
        assessment = self.get_assessment(assessment_id)
        if not assessment:
            return None

        if not assessment.is_available():
            return None

        submission = Submission(
            assessment_id=assessment_id,
            user_id=user_id,
            attempt_number=attempt_number,
            max_score=assessment.total_points,
        )
        self._submissions[submission.id] = submission
        return submission

    def get_submission(self, submission_id: UUID) -> Optional[Submission]:
        """Get submission by ID."""
        return self._submissions.get(submission_id)

    def submit_answer(
        self, submission_id: UUID, question_id: UUID, answer: Any
    ) -> Optional[Submission]:
        """Submit an answer for a question."""
        submission = self.get_submission(submission_id)
        if not submission:
            return None

        submission.answers[str(question_id)] = answer
        return submission

    def submit_assessment(self, submission_id: UUID) -> Optional[Submission]:
        """Submit the complete assessment."""
        submission = self.get_submission(submission_id)
        if not submission:
            return None

        submission.submit()
        submission.grading_status = GradingStatus.PENDING
        return submission

    def grade_submission(self, submission_id: UUID, grader_id: UUID) -> Optional[Submission]:
        """Grade a submission (auto-grade when possible)."""
        submission = self.get_submission(submission_id)
        if not submission:
            return None

        assessment = self.get_assessment(submission.assessment_id)
        if not assessment:
            return None

        total_score = 0.0
        question_results = {}

        for question_id in assessment.question_ids:
            question = self.get_question(question_id)
            if not question:
                continue

            answer = submission.answers.get(str(question_id))
            score = question.calculate_score(answer)
            total_score += score

            question_results[str(question_id)] = {
                "score": score,
                "max_score": question.points,
                "answer": answer,
                "correct_answer": question.correct_answer,
            }

        submission.score = total_score
        submission.question_results = question_results
        submission.calculate_percentage()
        submission.check_passed(assessment.passing_score)
        submission.grading_status = GradingStatus.COMPLETED
        submission.graded_by = grader_id
        submission.graded_at = datetime.now(timezone.utc)

        return submission

    def get_user_submissions(
        self, user_id: UUID, assessment_id: Optional[UUID] = None
    ) -> List[Submission]:
        """Get all submissions for a user."""
        submissions = [s for s in self._submissions.values() if s.user_id == user_id]

        if assessment_id:
            submissions = [s for s in submissions if s.assessment_id == assessment_id]

        return submissions

    def get_assessment_statistics(self, assessment_id: UUID) -> Dict[str, Any]:
        """Get statistics for an assessment."""
        submissions = [
            s for s in self._submissions.values()
            if s.assessment_id == assessment_id and s.grading_status == GradingStatus.COMPLETED
        ]

        if not submissions:
            return {"total_submissions": 0}

        scores = [s.percentage for s in submissions if s.percentage is not None]
        passed_count = sum(1 for s in submissions if s.passed)

        return {
            "total_submissions": len(submissions),
            "average_score": sum(scores) / len(scores) if scores else 0.0,
            "pass_rate": (passed_count / len(submissions) * 100) if submissions else 0.0,
            "min_score": min(scores) if scores else 0.0,
            "max_score": max(scores) if scores else 0.0,
        }
