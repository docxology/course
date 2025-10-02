"""Tests for the main curriculum module."""

import pytest
from uuid import uuid4

from curriculum.core.content import Content, ContentType, ContentFormat, ContentStatus
from curriculum.core.user import User, UserRole
from curriculum.core.assessment import Assessment, Question, QuestionType


class TestCurriculumMain:
    """Tests for the main curriculum module functionality."""

    def test_import_all_services(self):
        """Test that all services can be imported from main module."""
        from curriculum import (
            ContentService,
            UserService,
            AuthenticationService,
            AssessmentService,
            AnalyticsService,
            TeacherService,
            ContentGeneratorService,
        )

        # Verify services are available
        assert ContentService is not None
        assert UserService is not None
        assert AuthenticationService is not None
        assert AssessmentService is not None
        assert AnalyticsService is not None
        assert TeacherService is not None
        assert ContentGeneratorService is not None

    def test_import_all_models(self):
        """Test that all models can be imported from main module."""
        from curriculum import (
            Content,
            User,
            Assessment,
            Question,
            LearningEvent,
            BaseEntity,
        )

        # Verify models are available
        assert Content is not None
        assert User is not None
        assert Assessment is not None
        assert Question is not None
        assert LearningEvent is not None
        assert BaseEntity is not None

    def test_import_all_enums(self):
        """Test that all enums can be imported from main module."""
        from curriculum import (
            ContentType,
            ContentFormat,
            ContentStatus,
            UserRole,
            QuestionType,
        )

        # Verify enums are available
        assert ContentType.LESSON is not None
        assert ContentFormat.MARKDOWN is not None
        assert ContentStatus.DRAFT is not None
        assert UserRole.STUDENT is not None
        assert QuestionType.MULTIPLE_CHOICE is not None

    def test_settings_import(self):
        """Test that settings can be imported."""
        from curriculum import settings

        assert settings is not None
        assert hasattr(settings, 'app_name')
        assert hasattr(settings, 'database_url')

    def test_version_info(self):
        """Test that version information is available."""
        from curriculum import __version__, __author__

        assert __version__ is not None
        assert __author__ is not None
        assert isinstance(__version__, str)
        assert isinstance(__author__, str)

    def test_basic_workflow(self):
        """Test a basic workflow using imported services."""
        from curriculum import ContentService, UserService, AssessmentService

        # Create services
        content_service = ContentService()
        user_service = UserService()

        # Create user
        user = user_service.create_user(
            email="workflow@example.com",
            username="workflowuser",
            full_name="Workflow User",
            password="password123",
        )

        assert user is not None

        # Create content
        content = content_service.create_content(
            title="Test Workflow Content",
            content_type=ContentType.LESSON,
            format=ContentFormat.MARKDOWN,
            author_id=user.id,
            content_body="# Test Content\nThis is a test.",
        )

        assert content is not None
        assert content.title == "Test Workflow Content"

    def test_orchestration_layer(self):
        """Test that orchestration layer can be imported and initialized."""
        from curriculum.orchestration import CurriculumOrchestrator

        orchestrator = CurriculumOrchestrator()

        # Verify orchestrator has all services
        assert hasattr(orchestrator, 'content')
        assert hasattr(orchestrator, 'users')
        assert hasattr(orchestrator, 'assessments')
        assert hasattr(orchestrator, 'analytics')

    def test_module_structure(self):
        """Test that all expected modules are available."""
        import curriculum

        # Check that all main modules are importable
        expected_modules = [
            'core', 'content', 'learning', 'users', 'ai', 'communication',
            'accessibility', 'mobile', 'integration', 'search', 'teachers',
            'content_generation', 'tools'
        ]

        for module_name in expected_modules:
            assert hasattr(curriculum, module_name), f"Module {module_name} not found"

    def test_cross_module_dependencies(self):
        """Test that cross-module dependencies work correctly."""
        from curriculum.core.content import Content, ContentType
        from curriculum.content.content import ContentService
        from curriculum.users.user import UserService

        # Test that services can be instantiated and work together
        content_service = ContentService()
        user_service = UserService()

        # Create user through user service
        user = user_service.create_user(
            email="cross@example.com",
            username="crossuser",
            full_name="Cross Module User",
            password="password123",
        )

        # Create content through content service
        content = content_service.create_content(
            title="Cross Module Content",
            content_type=ContentType.LESSON,
            format=ContentFormat.MARKDOWN,
            author_id=user.id,
        )

        # Verify both were created successfully
        assert user is not None
        assert content is not None
        assert content.author_id == user.id