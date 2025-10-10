"""Tests for Content Creation Service."""

import pytest
from uuid import uuid4

from curriculum.ai.content_creation import ContentCreationService
from curriculum.core.content import ContentType, ContentFormat


@pytest.mark.integration
class TestContentCreationService:
    """Tests for ContentCreationService."""

    @pytest.fixture
    def content_creation_service(self):
        """Content creation service fixture."""
        return ContentCreationService()

    def test_get_available_templates(self, content_creation_service):
        """Test getting available templates."""
        templates = content_creation_service.get_available_templates()

        assert len(templates) > 0
        assert "lesson_template" in [t["id"] for t in templates]
        assert "quiz_template" in [t["id"] for t in templates]

    def test_create_content_from_template(self, content_creation_service, sample_user):
        """Test creating content from template."""
        content = content_creation_service.create_content_from_template(
            template_id="lesson_template",
            title="Test Lesson",
            author_id=sample_user.id,
        )

        assert content is not None
        assert content.title == "Test Lesson"
        assert content.content_type == ContentType.LESSON
        assert content.format == ContentFormat.MARKDOWN
        assert content.author_id == sample_user.id

    def test_generate_content_outline(self, content_creation_service):
        """Test generating content outline."""
        outline = content_creation_service.generate_content_outline(
            topic="Python Programming",
            content_type="lesson",
            estimated_duration=60,
        )

        assert outline["topic"] == "Python Programming"
        assert outline["content_type"] == "lesson"
        assert outline["estimated_duration"] == 60
        assert "sections" in outline
        assert "learning_objectives" in outline

    def test_create_custom_template(self, content_creation_service):
        """Test creating custom template."""
        template = content_creation_service.create_custom_template(
            name="Custom Quiz",
            description="A custom quiz template",
            structure={"questions": [], "answers": []},
            category="assessment",
        )

        assert template["name"] == "Custom Quiz"
        assert template["category"] == "assessment"
        assert template["is_custom"] is True

    def test_create_ai_assistant(self, content_creation_service):
        """Test creating AI assistant."""
        assistant = content_creation_service.create_ai_assistant(
            assistant_type="content_writer",
            configuration={
                "name": "Content Writer AI",
                "capabilities": ["text_generation", "content_suggestions"],
            },
        )

        assert assistant["type"] == "content_writer"
        assert assistant["name"] == "Content Writer AI"
        assert "text_generation" in assistant["capabilities"]

    def test_generate_content_with_ai(self, content_creation_service):
        """Test generating content with AI."""
        content = content_creation_service.generate_content_with_ai(
            assistant_id="ai_content_writer_0",
            prompt="Write a lesson about variables",
            content_type="lesson",
            length="medium",
        )

        assert content["prompt"] == "Write a lesson about variables"
        assert content["content_type"] == "lesson"
        assert "generated_content" in content
        assert content["word_count"] > 0

    def test_generate_quiz_from_content(self, content_creation_service, sample_content):
        """Test generating quiz from content."""
        quiz = content_creation_service.generate_quiz_from_content(
            content_id=sample_content.id,
            question_count=5,
            difficulty="intermediate",
        )

        assert quiz["content_id"] == str(sample_content.id)
        assert quiz["question_count"] == 5
        assert len(quiz["questions"]) == 5

        # Check question structure
        question = quiz["questions"][0]
        assert "question" in question
        assert "options" in question
        assert "correct_answer" in question

    def test_create_content_validator(self, content_creation_service):
        """Test creating content validator."""
        validator = content_creation_service.create_content_validator({
            "name": "Basic Validator",
            "rules": {
                "min_length": 100,
                "max_length": 10000,
                "required_sections": ["introduction", "main_content"],
            },
        })

        assert validator["name"] == "Basic Validator"
        assert validator["rules"]["min_length"] == 100

    def test_validate_content_structure(self, content_creation_service, sample_content):
        """Test validating content structure."""
        validator = content_creation_service.create_content_validator({
            "name": "Test Validator",
            "rules": {
                "min_length": 50,
                "max_length": 10000,
                "required_sections": ["introduction", "main_content"],
            },
        })

        validation = content_creation_service.validate_content_structure(
            content=sample_content,
            validator_id=validator["id"],
        )

        assert "content_id" in validation
        assert "is_valid" in validation
        assert "issues" in validation
        assert "warnings" in validation
        assert "score" in validation

    def test_get_content_creation_statistics(self, content_creation_service):
        """Test getting creation statistics."""
        stats = content_creation_service.get_content_creation_statistics()

        assert "total_templates" in stats
        assert "total_generators" in stats
        assert "total_ai_assistants" in stats
        assert "generation_success_rate" in stats

    def test_create_content_collaboration_space(self, content_creation_service, sample_content):
        """Test creating collaboration space."""
        collaborators = [uuid4(), uuid4()]
        permissions = {
            "user1": "edit",
            "user2": "view",
        }

        space = content_creation_service.create_content_collaboration_space(
            content_id=sample_content.id,
            collaborators=collaborators,
            permissions=permissions,
        )

        assert space["content_id"] == str(sample_content.id)
        assert len(space["collaborators"]) == 2
        assert "real_time_editing" in space["features"]

    def test_suggest_content_improvements(self, content_creation_service, sample_content):
        """Test suggesting content improvements."""
        feedback = [
            "The content is too long",
            "Some explanations are unclear",
            "The content is boring",
        ]

        suggestions = content_creation_service.suggest_content_improvements(
            content=sample_content,
            user_feedback=feedback,
        )

        assert suggestions["content_id"] == str(sample_content.id)
        assert len(suggestions["suggestions"]) > 0
        assert "improvement_score" in suggestions

    def test_create_content_library(self, content_creation_service):
        """Test creating content library."""
        library = content_creation_service.create_content_library(
            name="Programming Library",
            description="Library for programming content",
            content_types=["lesson", "quiz", "tutorial"],
        )

        assert library["name"] == "Programming Library"
        assert library["content_types"] == ["lesson", "quiz", "tutorial"]
        assert "is_public" in library
