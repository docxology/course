"""Assessment models for quizzes and evaluations."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import Field

from curriculum.core.base import BaseEntity


class QuestionType(str, Enum):
    """Types of assessment questions."""

    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"
    ESSAY = "essay"
    CODING = "coding"
    FILE_UPLOAD = "file_upload"
    PEER_REVIEW = "peer_review"


class DifficultyLevel(str, Enum):
    """Difficulty levels for questions."""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
    EXPERT = "expert"


class GradingStatus(str, Enum):
    """Status of assessment grading."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FLAGGED = "flagged"


class Assessment(BaseEntity):
    """Assessment (quiz, exam, etc.) entity."""

    title: str = Field(min_length=1, max_length=500)
    description: Optional[str] = None
    instructions: Optional[str] = None

    # Content relationship
    content_id: Optional[UUID] = None

    # Assessment settings
    time_limit: Optional[int] = None  # minutes
    attempts_allowed: int = 1
    passing_score: float = 70.0  # percentage
    is_proctored: bool = False

    # Question management
    question_ids: List[UUID] = Field(default_factory=list)
    question_order: List[UUID] = Field(default_factory=list)
    total_points: float = 0.0

    # Availability
    is_available: bool = True
    available_from: Optional[datetime] = None
    available_until: Optional[datetime] = None

    # Settings
    show_results: bool = True
    allow_review: bool = True
    randomize_questions: bool = False

    def is_available_now(self) -> bool:
        """Check if assessment is currently available."""
        now = datetime.now(timezone.utc)
        if not self.is_available:
            return False
        if self.available_from and now < self.available_from:
            return False
        if self.available_until and now > self.available_until:
            return False
        return True


class Question(BaseEntity):
    """Assessment question entity."""

    title: str = Field(min_length=1, max_length=200)
    question_text: str = Field(min_length=1)
    question_type: QuestionType
    points: float = Field(gt=0)

    # Question content
    options: List[Dict[str, Any]] = Field(default_factory=list)  # For multiple choice
    correct_answer: Optional[Any] = None
    answer_explanation: Optional[str] = None

    # Question metadata
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM
    tags: List[str] = Field(default_factory=list)
    hints: List[str] = Field(default_factory=list)

    # Assessment relationship
    assessment_id: Optional[UUID] = None

    def calculate_score(self, submitted_answer: Any) -> float:
        """Calculate score for submitted answer."""
        if self.question_type == QuestionType.MULTIPLE_CHOICE:
            return self.points if submitted_answer == self.correct_answer else 0.0
        elif self.question_type == QuestionType.TRUE_FALSE:
            return self.points if submitted_answer == self.correct_answer else 0.0
        elif self.question_type == QuestionType.SHORT_ANSWER:
            # Simple string matching for demo - in production use NLP
            if isinstance(self.correct_answer, str) and isinstance(submitted_answer, str):
                return (
                    self.points
                    if submitted_answer.lower().strip() == self.correct_answer.lower().strip()
                    else 0.0
                )
            return 0.0
        elif self.question_type == QuestionType.CODING:
            # Placeholder for code evaluation
            return self._grade_coding_submission(submitted_answer)
        else:
            # Essay, file upload, peer review - manual grading required
            return 0.0

    def _grade_coding_submission(self, code: str) -> float:
        """Grade coding submission (placeholder)."""
        # In production, this would run tests, check for syntax, etc.
        # For now, just check if code contains expected elements
        expected_keywords = ["def", "function", "return", "print"]
        found_keywords = sum(1 for keyword in expected_keywords if keyword in code.lower())
        return self.points * (found_keywords / len(expected_keywords))


class Submission(BaseEntity):
    """Student submission for an assessment."""

    assessment_id: UUID
    user_id: UUID
    attempt_number: int = 1

    # Submission data
    answers: Dict[str, Any] = Field(default_factory=dict)  # question_id -> answer
    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    submitted_at: Optional[datetime] = None

    # Grading data
    score: Optional[float] = None
    max_score: Optional[float] = None
    percentage: Optional[float] = None
    passed: Optional[bool] = None
    question_results: Dict[str, Dict[str, Any]] = Field(default_factory=dict)

    # Grading workflow
    grading_status: GradingStatus = GradingStatus.PENDING
    graded_by: Optional[UUID] = None
    graded_at: Optional[datetime] = None

    # Submission metadata
    time_spent: Optional[int] = None  # seconds
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

    def submit(self) -> None:
        """Mark submission as submitted."""
        self.submitted_at = datetime.now(timezone.utc)

    def calculate_percentage(self) -> None:
        """Calculate percentage score."""
        if self.score is not None and self.max_score is not None and self.max_score > 0:
            self.percentage = (self.score / self.max_score) * 100

    def check_passed(self, passing_score: float) -> None:
        """Check if submission passed."""
        if self.percentage is not None:
            self.passed = self.percentage >= passing_score

    def grade_submission(self) -> None:
        """Mark submission as graded."""
        # Calculate score based on answers (simplified logic)
        if self.answers:
            # For demo purposes, assume 50% of questions are correct
            self.score = 50.0  # This would be calculated from actual answers
            self.max_score = 100.0
            self.calculate_percentage()

        self.grading_status = GradingStatus.COMPLETED
        self.graded_at = datetime.now(timezone.utc)


class SubmissionResult(BaseEntity):
    """Detailed result for a submission."""

    submission_id: UUID
    question_id: UUID

    # Result data
    submitted_answer: Any
    correct_answer: Any
    score: float
    max_score: float

    # Feedback
    feedback: Optional[str] = None
    hints_used: List[str] = Field(default_factory=list)
    time_spent: Optional[int] = None  # seconds

    # Auto-grading data
    is_auto_graded: bool = False
    grading_algorithm: Optional[str] = None
    confidence_score: Optional[float] = None
