"""Pytest configuration and fixtures."""

import pytest

from curriculum.content.content import ContentService
from curriculum.core.assessment import QuestionType
from curriculum.core.content import Content, ContentFormat, ContentType
from curriculum.core.user import User, UserRole
from curriculum.learning.analytics import AnalyticsService
from curriculum.learning.assessment import AssessmentService
from curriculum.users.user import UserService


@pytest.fixture
def sample_user():
    """Create a sample user."""
    return User(
        email="test@example.com",
        username="testuser",
        full_name="Test User",
        hashed_password="hashed_password",
        roles=[UserRole.STUDENT],
    )


@pytest.fixture
def sample_instructor():
    """Create a sample instructor."""
    return User(
        email="instructor@example.com",
        username="instructor",
        full_name="Test Instructor",
        hashed_password="hashed_password",
        roles=[UserRole.INSTRUCTOR],
    )


@pytest.fixture
def sample_content(sample_instructor):
    """Create sample content."""
    return Content(
        title="Introduction to Python",
        content_type=ContentType.LESSON,
        format=ContentFormat.MARKDOWN,
        author_id=sample_instructor.id,
        description="Learn Python basics",
        content_body="# Python Basics\n\nPython is a programming language.",
    )


@pytest.fixture
def sample_assessment(assessment_service):
    """Create sample assessment."""
    return assessment_service.create_assessment(
        title="Python Quiz",
        description="Test your Python knowledge",
        time_limit=30,
    )


@pytest.fixture
def sample_question(assessment_service):
    """Create sample question."""
    return assessment_service.create_question(
        title="What is Python?",
        question_text="Select the correct description of Python.",
        question_type=QuestionType.MULTIPLE_CHOICE,
        points=10.0,
        correct_answer="A high-level programming language",
        options=[
            {"id": "a", "text": "A high-level programming language"},
            {"id": "b", "text": "A snake species"},
            {"id": "c", "text": "A web browser"},
        ],
    )


# Service fixtures
@pytest.fixture
def content_service():
    """Create a ContentService instance."""
    return ContentService()


@pytest.fixture
def analytics_service():
    """Create an AnalyticsService instance."""
    return AnalyticsService()


@pytest.fixture
def assessment_service():
    """Create an AssessmentService instance."""
    return AssessmentService()


@pytest.fixture
def user_service():
    """Create a UserService instance."""
    return UserService()


@pytest.fixture
def auth_service(user_service):
    """Create an AuthenticationService instance."""
    from curriculum.users.user import AuthenticationService

    return AuthenticationService(user_service)


@pytest.fixture(autouse=True)
def offline_documentation_provider(request, monkeypatch):
    """Exercise the offline fallback without depending on a developer's Ollama."""
    if "documentation" not in request.path.name:
        return
    import subprocess

    import requests

    original_post = requests.post
    original_run = subprocess.run

    def post(url, *args, **kwargs):
        if url == "http://localhost:11434/api/generate":
            raise requests.ConnectionError("Ollama is offline in the test environment")
        return original_post(url, *args, **kwargs)

    def run(args, *positional, **kwargs):
        if args and args[0] == "ollama":
            raise FileNotFoundError("Ollama is offline in the test environment")
        return original_run(args, *positional, **kwargs)

    monkeypatch.setattr(requests, "post", post)
    monkeypatch.setattr(subprocess, "run", run)
