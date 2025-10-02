"""Tests for core module models and functionality."""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from curriculum.core.base import BaseEntity, UUIDMixin, TimestampMixin, SoftDeleteMixin
from curriculum.core.content import Content, ContentStatus, ContentType, ContentFormat, ContentVersion
from curriculum.core.user import User, UserRole, UserPermission
from curriculum.core.metadata import Metadata, DublinCore, LRMIMetadata, ResourceType
from curriculum.core.analytics import LearningEvent, ActivityVerb, EventType, DeviceType
from curriculum.core.assessment import Assessment, Question, Submission, SubmissionResult, QuestionType, DifficultyLevel, GradingStatus


class TestBaseEntity:
    """Tests for BaseEntity and mixins."""

    def test_base_entity_creation(self):
        """Test BaseEntity creation with mixins."""
        class TestEntity(BaseEntity):
            name: str
            description: str = None

        entity = TestEntity(name="Test Entity")

        assert entity.id is not None
        assert isinstance(entity.id, str)  # UUID as string
        assert entity.created_at is not None
        assert entity.updated_at is not None
        assert entity.is_deleted is False
        assert entity.deleted_at is None

    def test_soft_delete_mixin(self):
        """Test soft delete functionality."""
        class TestEntity(BaseEntity, SoftDeleteMixin):
            name: str

        entity = TestEntity(name="Test Entity")

        # Initially not deleted
        assert not entity.is_deleted
        assert entity.deleted_at is None

        # Soft delete
        entity.soft_delete()
        assert entity.is_deleted is True
        assert entity.deleted_at is not None

        # Restore
        entity.restore()
        assert entity.is_deleted is False
        assert entity.deleted_at is None

    def test_timestamp_mixin(self):
        """Test timestamp updates."""
        class TestEntity(BaseEntity, TimestampMixin):
            name: str

        entity = TestEntity(name="Test Entity")
        original_updated = entity.updated_at

        # Update timestamp
        entity.update_timestamp()

        # Should be updated
        assert entity.updated_at >= original_updated


class TestContentModel:
    """Tests for Content model."""

    @pytest.fixture
    def sample_user(self):
        """Create sample user."""
        return User(
            email="author@example.com",
            username="author",
            full_name="Test Author",
            hashed_password="hashed",
            roles=[UserRole.CONTENT_CREATOR],
        )

    def test_content_creation(self, sample_user):
        """Test content creation."""
        content = Content(
            title="Introduction to Python",
            content_type=ContentType.LESSON,
            format=ContentFormat.MARKDOWN,
            author_id=sample_user.id,
            description="Learn Python basics",
            content_body="# Python Basics\n\nPython is a programming language.",
        )

        assert content.title == "Introduction to Python"
        assert content.content_type == ContentType.LESSON
        assert content.format == ContentFormat.MARKDOWN
        assert content.author_id == sample_user.id
        assert content.status == ContentStatus.DRAFT
        assert content.view_count == 0
        assert content.download_count == 0

    def test_content_status_transitions(self, sample_user):
        """Test content status transitions."""
        content = Content(
            title="Test Content",
            content_type=ContentType.LESSON,
            format=ContentFormat.MARKDOWN,
            author_id=sample_user.id,
        )

        # Valid transitions
        assert content.can_transition_to(ContentStatus.INTERNAL_REVIEW)
        content.transition_to(ContentStatus.INTERNAL_REVIEW)
        assert content.status == ContentStatus.INTERNAL_REVIEW

        assert content.can_transition_to(ContentStatus.EXTERNAL_REVIEW)
        content.transition_to(ContentStatus.EXTERNAL_REVIEW)
        assert content.status == ContentStatus.EXTERNAL_REVIEW

        assert content.can_transition_to(ContentStatus.APPROVED)
        content.transition_to(ContentStatus.APPROVED)
        assert content.status == ContentStatus.APPROVED

        # Invalid transition
        assert not content.can_transition_to(ContentStatus.DRAFT)  # Can't go back from APPROVED

    def test_content_tags(self, sample_user):
        """Test content tagging."""
        content = Content(
            title="Tagged Content",
            content_type=ContentType.LESSON,
            format=ContentFormat.MARKDOWN,
            author_id=sample_user.id,
            tags=["python", "programming", "beginner"],
        )

        assert "python" in content.tags
        assert "programming" in content.tags
        assert len(content.tags) == 3

    def test_content_hierarchy(self, sample_user):
        """Test content parent-child relationships."""
        parent = Content(
            title="Parent Course",
            content_type=ContentType.COURSE,
            format=ContentFormat.HTML,
            author_id=sample_user.id,
        )

        child = Content(
            title="Child Lesson",
            content_type=ContentType.LESSON,
            format=ContentFormat.MARKDOWN,
            author_id=sample_user.id,
            parent_id=parent.id,
        )

        assert child.parent_id == parent.id

    def test_content_versioning(self, sample_user):
        """Test content versioning."""
        content = Content(
            title="Versioned Content",
            content_type=ContentType.LESSON,
            format=ContentFormat.MARKDOWN,
            author_id=sample_user.id,
        )

        # Create version snapshot
        version = ContentVersion.from_content(content, "Initial version")

        assert version.content_id == content.id
        assert version.title == content.title
        assert version.content_body == content.content_body
        assert version.version == "1.0.0"

    def test_content_analytics(self, sample_user):
        """Test content analytics methods."""
        content = Content(
            title="Analytics Content",
            content_type=ContentType.LESSON,
            format=ContentFormat.MARKDOWN,
            author_id=sample_user.id,
        )

        # Test view and download tracking
        initial_views = content.view_count
        initial_downloads = content.download_count

        content.increment_views()
        content.increment_downloads()

        assert content.view_count == initial_views + 1
        assert content.download_count == initial_downloads + 1


class TestUserModel:
    """Tests for User model."""

    def test_user_creation(self):
        """Test user creation."""
        user = User(
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            hashed_password="hashed_password",
            roles=[UserRole.STUDENT],
        )

        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.full_name == "Test User"
        assert user.is_active is True
        assert user.is_verified is False
        assert UserRole.STUDENT in user.roles
        assert user.login_count == 0

    def test_user_permissions(self):
        """Test user permission system."""
        # Student user
        student = User(
            email="student@example.com",
            username="student",
            full_name="Test Student",
            hashed_password="hashed",
            roles=[UserRole.STUDENT],
        )

        # Instructor user
        instructor = User(
            email="instructor@example.com",
            username="instructor",
            full_name="Test Instructor",
            hashed_password="hashed",
            roles=[UserRole.INSTRUCTOR],
        )

        # Test student permissions
        assert student.has_permission(UserPermission.CONTENT_READ)
        assert not student.has_permission(UserPermission.CONTENT_CREATE)
        assert not student.has_permission(UserPermission.USER_UPDATE)

        # Test instructor permissions
        assert instructor.has_permission(UserPermission.CONTENT_READ)
        assert instructor.has_permission(UserPermission.CONTENT_CREATE)
        assert instructor.has_permission(UserPermission.ASSESSMENT_CREATE)

    def test_user_role_management(self):
        """Test user role management."""
        user = User(
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            hashed_password="hashed",
            roles=[UserRole.STUDENT],
        )

        # Add role
        user.add_role(UserRole.INSTRUCTOR)
        assert UserRole.INSTRUCTOR in user.roles
        assert user.has_permission(UserPermission.CONTENT_CREATE)

        # Remove role
        user.remove_role(UserRole.INSTRUCTOR)
        assert UserRole.INSTRUCTOR not in user.roles
        assert not user.has_permission(UserPermission.CONTENT_CREATE)

    def test_user_activity_tracking(self):
        """Test user activity tracking."""
        user = User(
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            hashed_password="hashed",
            roles=[UserRole.STUDENT],
        )

        # Record login
        user.record_login()
        assert user.last_login_at is not None
        assert user.login_count == 1

        # Record another login
        user.record_login()
        assert user.login_count == 2


class TestMetadataModel:
    """Tests for Metadata model."""

    @pytest.fixture
    def sample_content(self):
        """Create sample content."""
        return Content(
            title="Metadata Test",
            content_type=ContentType.LESSON,
            format=ContentFormat.MARKDOWN,
            author_id=uuid4(),
        )

    def test_dublin_core_creation(self):
        """Test Dublin Core metadata creation."""
        dublin_core = DublinCore(
            title="Sample Content",
            creator=["John Doe"],
            subject=["Education", "Programming"],
            description="Sample educational content",
            publisher="Test Publisher",
            contributor=["Jane Smith"],
            date=datetime.utcnow(),
            type=ResourceType.TEXT,
            format="text/markdown",
            identifier="content-123",
            source="Original source",
            language="en",
            relation="Related content",
            coverage="Global",
            rights="© 2023 Test Publisher",
        )

        assert dublin_core.title == "Sample Content"
        assert "John Doe" in dublin_core.creator
        assert "Education" in dublin_core.subject

    def test_lrmi_metadata_creation(self):
        """Test LRMI metadata creation."""
        lrmi = LRMIMetadata(
            educational_alignment=["CCSS.Math.Content.1.OA.A.1"],
            educational_use=["instruction", "assessment"],
            learning_resource_type=["lesson plan", "activity"],
            interactivity_type=["expositive"],
            typical_age_range=["13-15"],
            time_required=45,
            use_rights_url="https://example.com/rights",
        )

        assert "instruction" in lrmi.educational_use
        assert lrmi.time_required == 45
        assert lrmi.typical_age_range == ["13-15"]

    def test_metadata_creation(self, sample_content):
        """Test complete metadata creation."""
        dublin_core = DublinCore(
            title=sample_content.title,
            creator=["Test Author"],
            type=ResourceType.TEXT,
        )

        lrmi = LRMIMetadata(
            educational_use=["instruction"],
            time_required=30,
        )

        metadata = Metadata(
            content_id=sample_content.id,
            dublin_core=dublin_core,
            lrmi=lrmi,
        )

        assert metadata.content_id == sample_content.id
        assert metadata.dublin_core.title == sample_content.title
        assert metadata.lrmi.time_required == 30


class TestAnalyticsModel:
    """Tests for Analytics model."""

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
        )

    def test_learning_event_creation(self, sample_user, sample_content):
        """Test learning event creation."""
        event = LearningEvent(
            user_id=sample_user.id,
            verb=ActivityVerb.VIEWED,
            event_type=EventType.CONTENT,
            object_id=sample_content.id,
            object_type="content",
            success=True,
            score=85.0,
            duration=300,
        )

        assert event.user_id == sample_user.id
        assert event.verb == ActivityVerb.VIEWED
        assert event.object_id == sample_content.id
        assert event.success is True
        assert event.score == 85.0
        assert event.duration == 300

    def test_activity_verb_enum(self):
        """Test ActivityVerb enum values."""
        assert ActivityVerb.VIEWED.value == "viewed"
        assert ActivityVerb.COMPLETED.value == "completed"
        assert ActivityVerb.ASSESSED.value == "assessed"

    def test_event_type_enum(self):
        """Test EventType enum values."""
        assert EventType.CONTENT.value == "content"
        assert EventType.ASSESSMENT.value == "assessment"
        assert EventType.USER.value == "user"

    def test_device_type_enum(self):
        """Test DeviceType enum values."""
        assert DeviceType.DESKTOP.value == "desktop"
        assert DeviceType.MOBILE.value == "mobile"
        assert DeviceType.TABLET.value == "tablet"


class TestAssessmentModel:
    """Tests for Assessment model."""

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

    def test_question_creation(self):
        """Test question creation."""
        question = Question(
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

        assert question.title == "What is Python?"
        assert question.question_type == QuestionType.MULTIPLE_CHOICE
        assert question.points == 10.0
        assert question.correct_answer == "A high-level programming language"
        assert len(question.options) == 3

    def test_assessment_creation(self, sample_user):
        """Test assessment creation."""
        assessment = Assessment(
            title="Python Fundamentals Quiz",
            description="Test your Python knowledge",
            time_limit=30,
            passing_score=70.0,
            max_attempts=3,
            created_by=sample_user.id,
        )

        assert assessment.title == "Python Fundamentals Quiz"
        assert assessment.time_limit == 30
        assert assessment.passing_score == 70.0
        assert assessment.max_attempts == 3
        assert assessment.created_by == sample_user.id

    def test_submission_creation(self, sample_user):
        """Test submission creation."""
        assessment = Assessment(
            title="Test Assessment",
            description="Test assessment",
            time_limit=30,
            created_by=sample_user.id,
        )

        submission = Submission(
            assessment_id=assessment.id,
            user_id=sample_user.id,
            answers={"q1": "a", "q2": "b"},
            time_taken=25,
        )

        assert submission.assessment_id == assessment.id
        assert submission.user_id == sample_user.id
        assert submission.answers == {"q1": "a", "q2": "b"}
        assert submission.time_taken == 25
        assert submission.status == GradingStatus.PENDING

    def test_submission_grading(self, sample_user):
        """Test submission grading."""
        assessment = Assessment(
            title="Test Assessment",
            description="Test assessment",
            time_limit=30,
            created_by=sample_user.id,
        )

        submission = Submission(
            assessment_id=assessment.id,
            user_id=sample_user.id,
            answers={"q1": "correct", "q2": "wrong"},
            time_taken=25,
        )

        # Grade submission
        submission.grade_submission()

        assert submission.status == GradingStatus.GRADED
        assert submission.graded_at is not None
        assert submission.score is not None

    def test_submission_result(self, sample_user):
        """Test submission result creation."""
        assessment = Assessment(
            title="Test Assessment",
            description="Test assessment",
            time_limit=30,
            created_by=sample_user.id,
        )

        submission = Submission(
            assessment_id=assessment.id,
            user_id=sample_user.id,
            answers={},
        )

        result = SubmissionResult(
            submission_id=submission.id,
            score=85.0,
            max_score=100.0,
            passed=True,
            feedback="Good job!",
        )

        assert result.submission_id == submission.id
        assert result.score == 85.0
        assert result.max_score == 100.0
        assert result.passed is True
        assert result.feedback == "Good job!"


class TestModelValidation:
    """Tests for model validation."""

    def test_content_validation(self):
        """Test Content model validation."""
        # Valid content
        content = Content(
            title="Valid Content",
            content_type=ContentType.LESSON,
            format=ContentFormat.MARKDOWN,
            author_id=uuid4(),
        )
        assert content.title == "Valid Content"

        # Invalid content - missing required fields
        with pytest.raises(Exception):  # Pydantic validation error
            Content(
                title="",  # Empty title should fail
                content_type=ContentType.LESSON,
                format=ContentFormat.MARKDOWN,
                author_id=uuid4(),
            )

    def test_user_validation(self):
        """Test User model validation."""
        # Valid user
        user = User(
            email="valid@example.com",
            username="validuser",
            full_name="Valid User",
            hashed_password="hashed",
        )
        assert user.email == "valid@example.com"

        # Invalid email format should be caught by Pydantic EmailStr

    def test_assessment_validation(self):
        """Test Assessment model validation."""
        # Valid assessment
        assessment = Assessment(
            title="Valid Assessment",
            description="Valid description",
            time_limit=30,
            created_by=uuid4(),
        )
        assert assessment.title == "Valid Assessment"

    def test_question_validation(self):
        """Test Question model validation."""
        # Valid question
        question = Question(
            title="Valid Question",
            question_text="What is the answer?",
            question_type=QuestionType.MULTIPLE_CHOICE,
            points=10.0,
            correct_answer="Answer A",
            options=[{"id": "a", "text": "Answer A"}],
        )
        assert question.points == 10.0


class TestModelSerialization:
    """Tests for model serialization."""

    def test_content_serialization(self, sample_user):
        """Test Content model serialization."""
        content = Content(
            title="Serializable Content",
            content_type=ContentType.LESSON,
            format=ContentFormat.MARKDOWN,
            author_id=sample_user.id,
            tags=["test", "serialization"],
        )

        # Test model_dump
        data = content.model_dump()
        assert data["title"] == "Serializable Content"
        assert data["content_type"] == "lesson"
        assert "test" in data["tags"]

        # Test model_validate
        restored = Content.model_validate(data)
        assert restored.title == content.title
        assert restored.tags == content.tags

    def test_user_serialization(self):
        """Test User model serialization."""
        user = User(
            email="serializable@example.com",
            username="serializable",
            full_name="Serializable User",
            hashed_password="hashed",
            roles=[UserRole.STUDENT],
        )

        # Test serialization
        data = user.model_dump()
        assert data["email"] == "serializable@example.com"
        assert data["roles"] == ["student"]

        # Test deserialization
        restored = User.model_validate(data)
        assert restored.email == user.email
        assert restored.roles == user.roles

    def test_assessment_serialization(self, sample_user):
        """Test Assessment model serialization."""
        assessment = Assessment(
            title="Serializable Assessment",
            description="Test serialization",
            time_limit=30,
            created_by=sample_user.id,
        )

        data = assessment.model_dump()
        assert data["title"] == "Serializable Assessment"
        assert data["time_limit"] == 30

        restored = Assessment.model_validate(data)
        assert restored.title == assessment.title


class TestModelInheritance:
    """Tests for model inheritance patterns."""

    def test_base_entity_inheritance(self):
        """Test that all models inherit from BaseEntity."""
        # Content inherits from BaseEntity
        content = Content(
            title="Test",
            content_type=ContentType.LESSON,
            format=ContentFormat.MARKDOWN,
            author_id=uuid4(),
        )
        assert hasattr(content, 'id')
        assert hasattr(content, 'created_at')
        assert hasattr(content, 'updated_at')
        assert hasattr(content, 'is_deleted')

        # User inherits from BaseEntity
        user = User(
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            hashed_password="hashed",
        )
        assert hasattr(user, 'id')
        assert hasattr(user, 'created_at')

    def test_mixin_inheritance(self):
        """Test mixin inheritance."""
        # Content should have soft delete capability
        content = Content(
            title="Test",
            content_type=ContentType.LESSON,
            format=ContentFormat.MARKDOWN,
            author_id=uuid4(),
        )
        assert hasattr(content, 'soft_delete')
        assert hasattr(content, 'restore')

        # User should have timestamp updates
        user = User(
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            hashed_password="hashed",
        )
        assert hasattr(user, 'update_timestamp')


class TestModelBusinessLogic:
    """Tests for business logic in models."""

    def test_content_workflow_validation(self, sample_user):
        """Test content workflow business rules."""
        content = Content(
            title="Workflow Test",
            content_type=ContentType.LESSON,
            format=ContentFormat.MARKDOWN,
            author_id=sample_user.id,
        )

        # Should start as draft
        assert content.status == ContentStatus.DRAFT

        # Should be able to go to internal review
        assert content.can_transition_to(ContentStatus.INTERNAL_REVIEW)
        content.transition_to(ContentStatus.INTERNAL_REVIEW)
        assert content.status == ContentStatus.INTERNAL_REVIEW

        # Should not be able to skip to published
        assert not content.can_transition_to(ContentStatus.PUBLISHED)

    def test_user_role_permissions(self):
        """Test user role permission logic."""
        # Student should have limited permissions
        student = User(
            email="student@example.com",
            username="student",
            full_name="Test Student",
            hashed_password="hashed",
            roles=[UserRole.STUDENT],
        )

        assert student.has_role(UserRole.STUDENT)
        assert not student.has_role(UserRole.INSTRUCTOR)
        assert student.has_permission(UserPermission.CONTENT_READ)
        assert not student.has_permission(UserPermission.CONTENT_CREATE)

        # Instructor should have more permissions
        instructor = User(
            email="instructor@example.com",
            username="instructor",
            full_name="Test Instructor",
            hashed_password="hashed",
            roles=[UserRole.INSTRUCTOR],
        )

        assert instructor.has_role(UserRole.INSTRUCTOR)
        assert instructor.has_permission(UserPermission.CONTENT_CREATE)
        assert instructor.has_permission(UserPermission.ASSESSMENT_CREATE)

    def test_assessment_grading_logic(self, sample_user):
        """Test assessment grading business logic."""
        assessment = Assessment(
            title="Test Assessment",
            description="Test grading logic",
            time_limit=30,
            passing_score=70.0,
            created_by=sample_user.id,
        )

        submission = Submission(
            assessment_id=assessment.id,
            user_id=sample_user.id,
            answers={"q1": "correct"},
        )

        # Test grading calculation
        submission.grade_submission()
        assert submission.status == GradingStatus.GRADED
        assert submission.graded_at is not None


