"""Assessment API routes."""

from typing import List, Optional, Dict, Any
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends, Query, Path, status
from pydantic import BaseModel

from curriculum.core.assessment import (
    Assessment,
    Question,
    Submission,
    SubmissionResult,
    QuestionType,
    DifficultyLevel,
    GradingStatus,
)
from curriculum.learning.assessment import AssessmentService
from curriculum.core.user import User, UserPermission
from curriculum.routes.dependencies import get_current_user


router = APIRouter()

# Service instance
assessment_service = AssessmentService()


# Request/Response models
class CreateAssessmentRequest(BaseModel):
    """Request model for creating assessment."""
    title: str
    description: Optional[str] = None
    instructions: Optional[str] = None
    content_id: Optional[UUID] = None
    time_limit: Optional[int] = None
    attempts_allowed: int = 1


class CreateQuestionRequest(BaseModel):
    """Request model for creating question."""
    title: str
    question_text: str
    question_type: QuestionType
    points: float
    difficulty: DifficultyLevel = DifficultyLevel.MEDIUM
    correct_answer: Optional[Any] = None
    options: List[Dict[str, Any]] = []
    explanation: Optional[str] = None


class SubmitAnswerRequest(BaseModel):
    """Request model for submitting answer."""
    question_id: UUID
    answer: Any


class AssessmentResponse(BaseModel):
    """Response model for assessment."""
    id: str
    title: str
    description: Optional[str] = None
    instructions: Optional[str] = None
    content_id: Optional[str] = None
    time_limit: Optional[int] = None
    attempts_allowed: int
    total_points: float
    passing_score: float
    question_count: int
    created_at: str


class QuestionResponse(BaseModel):
    """Response model for question."""
    id: str
    title: str
    question_text: str
    question_type: str
    points: float
    difficulty: str
    options: List[Dict[str, Any]]
    explanation: Optional[str] = None


class SubmissionResponse(BaseModel):
    """Response model for submission."""
    id: str
    assessment_id: str
    user_id: str
    attempt_number: int
    score: Optional[float] = None
    max_score: Optional[float] = None
    percentage: Optional[float] = None
    passed: Optional[bool] = None
    grading_status: str
    started_at: str
    submitted_at: Optional[str] = None


# Assessment routes
@router.post("/", response_model=AssessmentResponse)
async def create_assessment(
    request: CreateAssessmentRequest,
    current_user: User = Depends(get_current_user),
):
    """Create a new assessment."""
    if not current_user.has_permission(UserPermission.ASSESSMENT_CREATE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    assessment = assessment_service.create_assessment(
        title=request.title,
        description=request.description,
        content_id=request.content_id,
        time_limit=request.time_limit,
    )

    if request.attempts_allowed != 1:
        assessment.attempts_allowed = request.attempts_allowed

    return _assessment_to_response(assessment)


@router.get("/{assessment_id}", response_model=AssessmentResponse)
async def get_assessment(assessment_id: UUID):
    """Get assessment by ID."""
    assessment = assessment_service.get_assessment(assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    return _assessment_to_response(assessment)


@router.get("/", response_model=List[AssessmentResponse])
async def list_assessments(
    content_id: Optional[UUID] = Query(None, description="Filter by content"),
    current_user: User = Depends(get_current_user),
):
    """List assessments."""
    # In a real implementation, this would query from database
    # For now, return empty list as we don't have persistent storage
    return []


# Question routes
@router.post("/{assessment_id}/questions", response_model=QuestionResponse)
async def create_question(
    assessment_id: UUID,
    request: CreateQuestionRequest,
    current_user: User = Depends(get_current_user),
):
    """Create a new question for assessment."""
    if not current_user.has_permission(UserPermission.ASSESSMENT_CREATE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    question = assessment_service.create_question(
        title=request.title,
        question_text=request.question_text,
        question_type=request.question_type,
        points=request.points,
        correct_answer=request.correct_answer,
        options=request.options,
    )

    # Add to assessment
    assessment_service.add_question_to_assessment(assessment_id, question.id)

    return _question_to_response(question)


@router.get("/{assessment_id}/questions", response_model=List[QuestionResponse])
async def get_assessment_questions(assessment_id: UUID):
    """Get questions for assessment."""
    assessment = assessment_service.get_assessment(assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")

    questions = []
    for question_id in assessment.question_ids:
        question = assessment_service.get_question(question_id)
        if question:
            questions.append(_question_to_response(question))

    return questions


# Submission routes
@router.post("/{assessment_id}/submissions", response_model=SubmissionResponse)
async def start_submission(
    assessment_id: UUID,
    attempt_number: int = 1,
    current_user: User = Depends(get_current_user),
):
    """Start a new submission."""
    submission = assessment_service.start_submission(
        assessment_id,
        current_user.id,
        attempt_number,
    )

    if not submission:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot start submission",
        )

    return _submission_to_response(submission)


@router.post("/submissions/{submission_id}/answers")
async def submit_answer(
    submission_id: UUID,
    request: SubmitAnswerRequest,
    current_user: User = Depends(get_current_user),
):
    """Submit answer for a question."""
    submission = assessment_service.get_submission(submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    if submission.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not your submission",
        )

    updated_submission = assessment_service.submit_answer(
        submission_id,
        request.question_id,
        request.answer,
    )

    if not updated_submission:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to submit answer",
        )

    return {"message": "Answer submitted successfully"}


@router.post("/submissions/{submission_id}/submit")
async def submit_assessment(
    submission_id: UUID,
    current_user: User = Depends(get_current_user),
):
    """Submit the complete assessment."""
    submission = assessment_service.get_submission(submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    if submission.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not your submission",
        )

    updated_submission = assessment_service.submit_assessment(submission_id)
    if not updated_submission:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to submit assessment",
        )

    # Auto-grade if possible
    assessment_service.grade_submission(submission_id, current_user.id)

    return {"message": "Assessment submitted successfully"}


@router.get("/submissions/{submission_id}", response_model=SubmissionResponse)
async def get_submission(
    submission_id: UUID,
    current_user: User = Depends(get_current_user),
):
    """Get submission details."""
    submission = assessment_service.get_submission(submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    if submission.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not your submission",
        )

    return _submission_to_response(submission)


@router.get("/users/{user_id}/submissions", response_model=List[SubmissionResponse])
async def get_user_submissions(
    user_id: UUID,
    assessment_id: Optional[UUID] = Query(None, description="Filter by assessment"),
    current_user: User = Depends(get_current_user),
):
    """Get submissions for a user."""
    if user_id != current_user.id and not current_user.has_permission(UserPermission.ASSESSMENT_GRADE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    submissions = assessment_service.get_user_submissions(user_id, assessment_id)

    return [_submission_to_response(s) for s in submissions]


@router.get("/{assessment_id}/statistics", response_model=Dict[str, Any])
async def get_assessment_statistics(assessment_id: UUID):
    """Get assessment statistics."""
    stats = assessment_service.get_assessment_statistics(assessment_id)

    return stats


# Helper functions
def _assessment_to_response(assessment: Assessment) -> AssessmentResponse:
    """Convert Assessment model to response model."""
    return AssessmentResponse(
        id=str(assessment.id),
        title=assessment.title,
        description=assessment.description,
        instructions=assessment.instructions,
        content_id=str(assessment.content_id) if assessment.content_id else None,
        time_limit=assessment.time_limit,
        attempts_allowed=assessment.attempts_allowed,
        total_points=assessment.total_points,
        passing_score=assessment.passing_score,
        question_count=len(assessment.question_ids),
        created_at=assessment.created_at.isoformat(),
    )


def _question_to_response(question: Question) -> QuestionResponse:
    """Convert Question model to response model."""
    return QuestionResponse(
        id=str(question.id),
        title=question.title,
        question_text=question.question_text,
        question_type=question.question_type.value,
        points=question.points,
        difficulty=question.difficulty.value,
        options=question.options,
        explanation=question.answer_explanation,
    )


def _submission_to_response(submission: Submission) -> SubmissionResponse:
    """Convert Submission model to response model."""
    return SubmissionResponse(
        id=str(submission.id),
        assessment_id=str(submission.assessment_id),
        user_id=str(submission.user_id),
        attempt_number=submission.attempt_number,
        score=submission.score,
        max_score=submission.max_score,
        percentage=submission.percentage,
        passed=submission.passed,
        grading_status=submission.grading_status.value,
        started_at=submission.started_at.isoformat(),
        submitted_at=submission.submitted_at.isoformat() if submission.submitted_at else None,
    )
