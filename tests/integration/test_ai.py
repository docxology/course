"""Tests for AI module services."""

import pytest
from unittest.mock import Mock, patch
from uuid import uuid4

from curriculum.core.content import Content, ContentType, ContentFormat
from curriculum.core.user import User, UserRole


@pytest.mark.integration
class TestAIFeaturesService:
    """Tests for AIFeaturesService."""

    @pytest.fixture
    def ai_features_service(self):
        """Create AIFeaturesService instance."""
        from curriculum.ai.ai_features import AIFeaturesService
        return AIFeaturesService()


    def test_analyze_content_difficulty(self, ai_features_service, sample_content):
        """Test content difficulty analysis."""
        result = ai_features_service.analyze_content_difficulty(sample_content)

        assert result is not None
        assert isinstance(result, dict)
        assert "difficulty_level" in result
        assert "complexity_score" in result
        assert 0 <= result["complexity_score"] <= 1

    def test_recommend_next_content(self, ai_features_service, sample_user, sample_content):
        """Test content recommendation."""
        result = ai_features_service.generate_content_recommendations(sample_user.id, sample_content.id)

        assert result is not None
        assert isinstance(result, list)
        assert len(result) > 0

    def test_create_intelligent_tutor_session(self, ai_features_service, sample_user, sample_content):
        """Test intelligent tutor session creation."""
        result = ai_features_service.create_intelligent_tutor_session(
            sample_user.id, sample_content.id, "visual"
        )

        assert result is not None
        assert isinstance(result, dict)
        assert "id" in result
        assert "user_id" in result
        assert "content_id" in result

    def test_analyze_learning_style(self, ai_features_service, sample_user):
        """Test learning style analysis."""
        # Mock user activity data
        responses = [
            {"question_type": "multiple_choice", "time_to_answer": 30, "correct": True},
            {"question_type": "essay", "time_to_answer": 120, "correct": True},
            {"question_type": "coding", "time_to_answer": 300, "correct": False},
        ]

        result = ai_features_service.assess_learning_style(sample_user.id, responses)

        assert result is not None
        assert isinstance(result, dict)
        assert "primary_learning_style" in result
        assert "assessed_at" in result

    def test_generate_adaptive_content(self, ai_features_service, sample_user, sample_content):
        """Test adaptive content generation."""
        result = ai_features_service.generate_adaptive_content(
            sample_content.id, sample_user.id, "beginner"
        )

        assert result is not None
        assert isinstance(result, dict)
        assert "content_id" in result
        assert "user_id" in result
        assert "adapted_content" in result


@pytest.mark.integration
class TestContentCreationService:
    """Tests for ContentCreationService."""

    @pytest.fixture
    def content_creation_service(self):
        """Create ContentCreationService instance."""
        from curriculum.ai.content_creation import ContentCreationService
        return ContentCreationService()

    def test_create_content_from_template(self, content_creation_service, sample_user):
        """Test content creation from template."""
        template_id = "lesson_template"
        customizations = {
            "title": "Machine Learning Basics",
            "learning_objectives": ["Understand ML concepts", "Apply ML algorithms"],
            "main_content": "Detailed ML content"
        }

        result = content_creation_service.create_content_from_template(
            template_id, sample_user.id, customizations
        )

        assert result is not None
        assert "content" in result
        assert "template_id" in result

    def test_generate_quiz_from_content(self, content_creation_service, sample_content):
        """Test quiz generation from content."""
        question_count = 3

        result = content_creation_service.generate_quiz_from_content(sample_content.id, question_count)

        assert result is not None
        assert "quiz_id" in result
        assert "questions" in result
        assert len(result["questions"]) == question_count

    def test_generate_content_outline(self, content_creation_service):
        """Test content outline generation."""
        topic = "Machine Learning"
        sections = 5

        result = content_creation_service.generate_content_outline(topic, sections)

        assert result is not None
        assert "outline" in result
        assert "sections" in result
        assert len(result["sections"]) == sections

    def test_validate_content_structure(self, content_creation_service):
        """Test content structure validation."""
        content_data = {
            "title": "Test Content",
            "content_body": "Valid content body",
            "learning_objectives": ["Objective 1", "Objective 2"]
        }

        result = content_creation_service.validate_content_structure(content_data)

        assert result is not None
        assert "valid" in result
        assert "issues" in result

    def test_create_content_validator(self, content_creation_service):
        """Test content validator creation."""
        validator = content_creation_service.create_content_validator()

        assert validator is not None
        assert "validator_id" in validator


@pytest.mark.integration
class TestResearchToolsService:
    """Tests for ResearchToolsService."""

    @pytest.fixture
    def research_service(self):
        """Create ResearchToolsService instance."""
        from curriculum.ai.research import ResearchToolsService
        return ResearchToolsService()

    def test_create_citation(self, research_service, sample_user):
        """Test citation creation."""
        result = research_service.create_citation(
            user_id=sample_user.id,
            title="Python Programming Language",
            authors=["Guido van Rossum"],
            publication_year=1991,
            source_type="website",
            source_details={"url": "https://python.org"}
        )

        assert result is not None
        assert result["title"] == "Python Programming Language"
        assert result["authors"] == ["Guido van Rossum"]
        assert result["is_verified"] is False

    def test_search_citations(self, research_service, sample_user):
        """Test citation search."""
        # Create some test citations
        for i in range(3):
            research_service.create_citation(
                user_id=sample_user.id,
                title=f"Research Paper {i}",
                authors=[f"Author {i}"],
                publication_year=2020 + i,
                source_type="article",
                source_details={}
            )

        results = research_service.search_citations("Research")

        assert len(results) >= 3

    def test_format_citation_apa(self, research_service, sample_user):
        """Test APA citation formatting."""
        citation = research_service.create_citation(
            user_id=sample_user.id,
            title="Machine Learning",
            authors=["John Doe", "Jane Smith"],
            publication_year=2022,
            source_type="journal",
            source_details={"journal": "AI Journal"}
        )

        formatted = research_service.format_citation(citation["id"], "apa")

        assert formatted is not None
        assert "Doe" in formatted
        assert "2022" in formatted

    def test_format_citation_mla(self, research_service, sample_user):
        """Test MLA citation formatting."""
        citation = research_service.create_citation(
            user_id=sample_user.id,
            title="Deep Learning",
            authors=["Alice Johnson"],
            publication_year=2021,
            source_type="book",
            source_details={}
        )

        formatted = research_service.format_citation(citation["id"], "mla")

        assert formatted is not None
        assert "Johnson" in formatted

    def test_extract_citations_from_text(self, research_service):
        """Test citation extraction from text."""
        text = """
        This is based on research by Smith (2020) and Johnson et al. (2019).
        According to "Python Programming" by Guido van Rossum (1991).
        """

        citations = research_service.extract_citations_from_text(text)

        assert len(citations) > 0
        assert any("Smith" in c.get("authors", []) for c in citations)

    def test_validate_citation(self, research_service, sample_user):
        """Test citation validation."""
        citation = research_service.create_citation(
            user_id=sample_user.id,
            title="Test Paper",
            authors=["Test Author"],
            publication_year=2023,
            source_type="article",
            source_details={}
        )

        result = research_service.validate_citation(citation)

        assert result is not None
        assert "valid" in result
        assert "errors" in result
        assert "warnings" in result

    def test_create_bibliography(self, research_service, sample_user):
        """Test bibliography creation."""
        # Create multiple citations
        citations = []
        for i in range(3):
            citation = research_service.create_citation(
                user_id=sample_user.id,
                title=f"Paper {i}",
                authors=[f"Author {i}"],
                publication_year=2020 + i,
                source_type="article",
                source_details={}
            )
            citations.append(citation["id"])

        bibliography = research_service.create_bibliography(
            user_id=sample_user.id,
            title="Test Bibliography",
            citation_ids=citations,
            style="apa"
        )

        assert bibliography is not None
        assert len(bibliography["citation_ids"]) == 3

    def test_export_bibliography_ris(self, research_service, sample_user):
        """Test RIS bibliography export."""
        citations = []
        for i in range(2):
            citation = research_service.create_citation(
                user_id=sample_user.id,
                title=f"Research {i}",
                authors=[f"Researcher {i}"],
                publication_year=2021 + i,
                source_type="article",
                source_details={}
            )
            citations.append(citation["id"])

        # Create bibliography
        bib = research_service.create_bibliography(
            user_id=sample_user.id,
            title="Test Bibliography",
            citation_ids=citations,
            style="apa"
        )

        ris_export = research_service.export_bibliography(bib["id"], "ris")

        assert ris_export is not None
        assert "TY  - JOUR" in ris_export


@pytest.mark.integration
class TestAIIntegration:
    """Integration tests for AI module."""

    def test_ai_content_creation_workflow(self, content_creation_service, sample_user):
        """Test complete AI content creation workflow."""
        # Create content from template
        lesson = content_creation_service.create_content_from_template(
            "lesson_template", sample_user.id, {"title": "Machine Learning Basics"}
        )

        assert lesson is not None
        assert lesson["content"] is not None

        # Generate quiz from content
        quiz = content_creation_service.generate_quiz_from_content(
            lesson["content_id"], 3
        )

        assert quiz is not None
        assert len(quiz["questions"]) == 3

        # Validate content structure
        validation = content_creation_service.validate_content_structure(lesson)

        assert validation["valid"] is True

    def test_ai_features_personalization(self, ai_features_service, sample_user, sample_content):
        """Test AI personalization features."""
        # Analyze content difficulty
        difficulty = ai_features_service.analyze_content_difficulty(sample_content)

        assert difficulty is not None

        # Generate adaptive content based on user needs
        adapted_content = ai_features_service.generate_adaptive_content(
            sample_content.id, sample_user.id, "beginner"
        )

        assert adapted_content is not None
        assert adapted_content["content_id"] == str(sample_content.id)

        # Get content recommendations
        recommendations = ai_features_service.generate_content_recommendations(
            sample_user.id, sample_content.id
        )

        assert recommendations is not None
        assert isinstance(recommendations, list)

    def test_ai_service_error_handling(self, ai_features_service):
        """Test AI service error handling."""
        # Test with invalid data
        try:
            result = ai_features_service.analyze_content_difficulty(None)
            # Should handle gracefully
            assert result is not None
        except Exception:
            # Expected to handle errors gracefully
            pass

        # Should return fallback result or error indicator
        assert result is not None

    def test_ai_content_improvement(self, content_creation_service):
        """Test AI content improvement."""
        # Test content outline generation
        outline = content_creation_service.generate_content_outline("Machine Learning", 5)

        assert outline is not None
        assert "outline" in outline
        assert "sections" in outline
        assert len(outline["sections"]) == 5

    def test_research_tools_workflow(self, research_service):
        """Test complete research tools workflow."""
        # Extract citations from text
        text = "According to Smith (2020) and Johnson (2019), machine learning is important."
        citations = research_service.extract_citations_from_text(text)

        assert len(citations) > 0

        # Create formal citations
        citation_ids = []
        for citation in citations:
            formal_citation = research_service.create_citation(
                user_id=sample_user.id,
                title=citation["title"],
                authors=citation["authors"],
                publication_year=citation["publication_year"],
                source_type="article",
                source_details={}
            )
            citation_ids.append(formal_citation["id"])

        # Create bibliography
        bibliography = research_service.create_bibliography(
            user_id=sample_user.id,
            title="Test Bibliography",
            citation_ids=citation_ids,
            style="apa"
        )

        assert bibliography is not None
        assert len(bibliography["citation_ids"]) == len(citation_ids)
