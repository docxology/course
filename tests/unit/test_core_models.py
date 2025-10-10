"""Tests for data models."""

import pytest
from datetime import datetime
from uuid import UUID

from curriculum.core.content import Content, ContentStatus, ContentFormat, ContentType
from curriculum.core.user import User, UserRole, UserPermission
from curriculum.core.metadata import Metadata, DublinCore, ResourceType
from curriculum.core.assessment import Question, QuestionType, Assessment


@pytest.mark.unit
class TestContentModel:
    """Tests for Content model."""

    def test_content_creation(self):
        """Test creating a content instance."""
        author_id = UUID("12345678-1234-5678-1234-567812345678")
        content = Content(
            title="Test Content",
            content_type=ContentType.LESSON,
            format=ContentFormat.MARKDOWN,
            author_id=author_id,
        )

        assert content.title == "Test Content"
        assert content.content_type == ContentType.LESSON
        assert content.format == ContentFormat.MARKDOWN
        assert content.author_id == author_id
        assert content.status == ContentStatus.DRAFT
        assert isinstance(content.id, UUID)
        assert isinstance(content.created_at, datetime)

    def test_content_status_transition(self):
        """Test content status transitions."""
        author_id = UUID("12345678-1234-5678-1234-567812345678")
        content = Content(
            title="Test",
            content_type=ContentType.LESSON,
            format=ContentFormat.MARKDOWN,
            author_id=author_id,
        )

        # Valid transition
        assert content.can_transition_to(ContentStatus.INTERNAL_REVIEW)
        content.transition_to(ContentStatus.INTERNAL_REVIEW)
        assert content.status == ContentStatus.INTERNAL_REVIEW

        # Invalid transition
        with pytest.raises(ValueError):
            content.transition_to(ContentStatus.PUBLISHED)

    def test_increment_views(self):
        """Test incrementing view count."""
        author_id = UUID("12345678-1234-5678-1234-567812345678")
        content = Content(
            title="Test",
            content_type=ContentType.LESSON,
            format=ContentFormat.MARKDOWN,
            author_id=author_id,
        )

        assert content.view_count == 0
        content.increment_views()
        assert content.view_count == 1
        content.increment_views()
        assert content.view_count == 2


@pytest.mark.unit
class TestUserModel:
    """Tests for User model."""

    def test_user_creation(self):
        """Test creating a user instance."""
        user = User(
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            hashed_password="hashed_password",
        )

        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.full_name == "Test User"
        assert user.is_active is True
        assert user.is_verified is False
        assert UserRole.STUDENT in user.roles

    def test_user_permissions(self):
        """Test user permissions."""
        user = User(
            email="instructor@example.com",
            username="instructor",
            full_name="Instructor",
            hashed_password="hashed",
            roles=[UserRole.INSTRUCTOR],
        )

        permissions = user.get_permissions()
        assert UserPermission.CONTENT_READ in permissions
        assert UserPermission.CONTENT_CREATE in permissions
        assert user.has_permission(UserPermission.ASSESSMENT_GRADE)

    def test_add_remove_role(self):
        """Test adding and removing roles."""
        user = User(
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            hashed_password="hashed",
        )

        assert UserRole.INSTRUCTOR not in user.roles
        user.add_role(UserRole.INSTRUCTOR)
        assert UserRole.INSTRUCTOR in user.roles

        user.remove_role(UserRole.INSTRUCTOR)
        assert UserRole.INSTRUCTOR not in user.roles

    def test_record_login(self):
        """Test recording user login."""
        user = User(
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            hashed_password="hashed",
        )

        assert user.login_count == 0
        assert user.last_login_at is None

        user.record_login()

        assert user.login_count == 1
        assert user.last_login_at is not None
        assert user.last_activity_at is not None


@pytest.mark.unit
class TestMetadataModel:
    """Tests for Metadata models."""

    def test_dublin_core_creation(self):
        """Test creating Dublin Core metadata."""
        dc = DublinCore(
            title="Test Resource",
            description="A test educational resource",
            type=ResourceType.TEXT,
        )

        assert dc.title == "Test Resource"
        assert dc.description == "A test educational resource"
        assert dc.type == ResourceType.TEXT
        assert dc.language == "en"

    def test_metadata_creation(self):
        """Test creating comprehensive metadata."""
        content_id = UUID("12345678-1234-5678-1234-567812345678")
        metadata = Metadata.create_minimal(content_id, "Test Content")

        assert metadata.content_id == content_id
        assert metadata.dublin_core.title == "Test Content"
        assert isinstance(metadata.id, UUID)


@pytest.mark.unit
class TestAssessmentModels:
    """Tests for Assessment models."""

    def test_question_creation(self):
        """Test creating a question."""
        question = Question(
            title="Test Question",
            question_text="What is 2+2?",
            question_type=QuestionType.MULTIPLE_CHOICE,
            points=5.0,
            correct_answer="4",
        )

        assert question.title == "Test Question"
        assert question.points == 5.0
        assert question.question_type == QuestionType.MULTIPLE_CHOICE

    def test_question_scoring(self):
        """Test question scoring."""
        question = Question(
            title="Test",
            question_text="What is 2+2?",
            question_type=QuestionType.MULTIPLE_CHOICE,
            points=10.0,
            correct_answer="4",
        )

        assert question.calculate_score("4") == 10.0
        assert question.calculate_score("5") == 0.0

    def test_assessment_creation(self):
        """Test creating an assessment."""
        assessment = Assessment(
            title="Math Quiz",
            description="Test your math skills",
            time_limit=30,
        )

        assert assessment.title == "Math Quiz"
        assert assessment.time_limit == 30
        assert assessment.attempts_allowed == 1
