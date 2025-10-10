"""Integration tests for the Curriculum Repository System."""

import pytest
from uuid import uuid4

from curriculum.content.content import ContentService
from curriculum.users.user import UserService, AuthenticationService
from curriculum.learning.assessment import AssessmentService
from curriculum.learning.analytics import AnalyticsService
from curriculum.core.content import ContentType, ContentFormat, ContentStatus
from curriculum.core.user import UserRole
from curriculum.core.assessment import QuestionType


@pytest.mark.integration
class TestIntegration:
    """Integration tests for the entire system."""

    @pytest.fixture
    def services(self):
        """Initialize core services for integration testing."""
        user_service = UserService()
        auth_service = AuthenticationService(user_service)
        content_service = ContentService()
        assessment_service = AssessmentService()
        analytics_service = AnalyticsService()

        return {
            "user": user_service,
            "auth": auth_service,
            "content": content_service,
            "assessment": assessment_service,
            "analytics": analytics_service,
        }

    def test_complete_user_journey(self, services):
        """Test complete user journey from registration to content consumption."""
        # 1. Create user
        user = services["user"].create_user(
            email="journey@example.com",
            username="journeyuser",
            full_name="Journey User",
            password="password123",
        )
        assert user is not None
        assert user.email == "journey@example.com"

        # 2. Authenticate user
        authenticated = services["auth"].authenticate_user("journeyuser", "password123")
        assert authenticated is not None
        assert authenticated.id == user.id

        # 3. Create instructor
        instructor = services["user"].create_user(
            email="instructor@example.com",
            username="instructor",
            full_name="Test Instructor",
            password="password123",
            roles=[UserRole.INSTRUCTOR],
        )
        assert instructor is not None
        assert UserRole.INSTRUCTOR in instructor.roles

        # 4. Create content
        content = services["content"].create_content(
            title="Python Tutorial",
            content_type=ContentType.LESSON,
            format=ContentFormat.MARKDOWN,
            author_id=instructor.id,
            description="Learn Python programming",
            content_body="# Python Basics\n\nThis is a tutorial.",
        )
        assert content is not None
        assert content.status == ContentStatus.DRAFT

        # 5. Track analytics
        view_event = services["analytics"].track_content_view(
            user_id=user.id,
            content_id=content.id,
        )
        assert view_event is not None
        assert hasattr(view_event, 'id')

    def test_content_lifecycle(self, services):
        """Test content creation and lifecycle management."""
        # Create author
        author = services["user"].create_user(
            email="author@example.com",
            username="author",
            full_name="Content Author",
            password="password123",
            roles=[UserRole.CONTENT_CREATOR],
        )
        assert author is not None

        # Create content
        content = services["content"].create_content(
            title="Test Content",
            content_type=ContentType.LESSON,
            format=ContentFormat.MARKDOWN,
            author_id=author.id,
            description="Test content lifecycle",
            content_body="# Test\n\nContent body.",
        )
        assert content is not None
        assert content.status == ContentStatus.DRAFT

        # Update content
        updated = services["content"].update_content(
            content_id=content.id,
            title="Updated Test Content",
        )
        assert updated is not None
        assert updated.title == "Updated Test Content"

        # Get content
        retrieved = services["content"].get_content(content.id)
        assert retrieved is not None
        assert retrieved.id == content.id

    def test_assessment_workflow(self, services):
        """Test assessment creation and submission workflow."""
        # Create instructor
        instructor = services["user"].create_user(
            email="instructor2@example.com",
            username="instructor2",
            full_name="Instructor Two",
            password="password123",
            roles=[UserRole.INSTRUCTOR],
        )
        assert instructor is not None

        # Create assessment
        assessment = services["assessment"].create_assessment(
            title="Python Quiz",
            description="Test your Python knowledge",
            time_limit=30,
        )
        assert assessment is not None
        assert assessment.title == "Python Quiz"

        # Create question
        question = services["assessment"].create_question(
            title="What is Python?",
            question_text="What is Python?",
            question_type=QuestionType.MULTIPLE_CHOICE,
            points=10.0,
            correct_answer="A programming language",
            options=[
                {"id": "a", "text": "A programming language"},
                {"id": "b", "text": "A snake"},
            ],
        )
        assert question is not None

        # Verify assessment and question created
        assert assessment.id is not None
        assert question.id is not None

    def test_analytics_tracking(self, services):
        """Test analytics event tracking."""
        # Create user
        user = services["user"].create_user(
            email="analytics@example.com",
            username="analyticsuser",
            full_name="Analytics User",
            password="password123",
        )
        assert user is not None

        # Create content
        author = services["user"].create_user(
            email="author2@example.com",
            username="author2",
            full_name="Author Two",
            password="password123",
        )
        
        content = services["content"].create_content(
            title="Analytics Content",
            content_type=ContentType.LESSON,
            format=ContentFormat.MARKDOWN,
            author_id=author.id,
            content_body="Content for analytics.",
        )

        # Track events
        view_event = services["analytics"].track_content_view(
            user_id=user.id,
            content_id=content.id,
        )
        assert view_event is not None

        # Get user events
        events = services["analytics"].get_events_by_user(user.id)
        assert len(events) >= 1

    def test_permission_system(self, services):
        """Test user permission system."""
        # Create users with different roles
        student = services["user"].create_user(
            email="student@example.com",
            username="student",
            full_name="Student User",
            password="password123",
            roles=[UserRole.STUDENT],
        )
        assert student is not None

        instructor = services["user"].create_user(
            email="instructor3@example.com",
            username="instructor3",
            full_name="Instructor Three",
            password="password123",
            roles=[UserRole.INSTRUCTOR],
        )
        assert instructor is not None

        admin = services["user"].create_user(
            email="admin@example.com",
            username="admin",
            full_name="Admin User",
            password="password123",
            roles=[UserRole.ADMIN],
        )
        assert admin is not None

        # Verify role assignments
        assert UserRole.STUDENT in student.roles
        assert UserRole.INSTRUCTOR in instructor.roles
        assert UserRole.ADMIN in admin.roles
