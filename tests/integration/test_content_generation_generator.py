"""Tests for Content Generation Service."""

import pytest
from uuid import uuid4

from curriculum.content_generation.generator import ContentGeneratorService


@pytest.mark.integration
class TestContentGeneratorService:
    """Tests for ContentGeneratorService."""

    @pytest.fixture
    def generator_service(self):
        """Content generator service fixture."""
        return ContentGeneratorService()

    def test_generate_content_lesson(self, generator_service):
        """Test generating lesson content."""
        result = generator_service.generate_content(
            content_type="lesson",
            topic="Python Programming",
            target_audience="college_students",
            difficulty="intermediate"
        )

        assert result["content_type"] == "lesson"
        assert result["topic"] == "Python Programming"
        assert "generated_content" in result
        assert "content_structure" in result
        assert "metadata" in result
        assert result["metadata"]["word_count"] > 0

    def test_generate_content_quiz(self, generator_service):
        """Test generating quiz content."""
        result = generator_service.generate_content(
            content_type="quiz",
            topic="Data Structures",
            target_audience="university_students",
            difficulty="advanced"
        )

        assert result["content_type"] == "quiz"
        assert result["topic"] == "Data Structures"
        assert "generated_content" in result

    def test_generate_content_tutorial(self, generator_service):
        """Test generating tutorial content."""
        result = generator_service.generate_content(
            content_type="tutorial",
            topic="Machine Learning",
            target_audience="graduate_students",
            difficulty="advanced"
        )

        assert result["content_type"] == "tutorial"
        assert result["topic"] == "Machine Learning"
        assert "generated_content" in result

    def test_get_generation_templates(self, generator_service):
        """Test getting available templates."""
        templates = generator_service.get_generation_templates()

        assert isinstance(templates, list)
        assert len(templates) > 0

        for template in templates:
            assert "id" in template
            assert "name" in template
            assert "structure" in template

    def test_create_content_from_generation(self, generator_service):
        """Test creating content from generation result."""
        # Generate content first
        generation_result = generator_service.generate_content(
            content_type="lesson",
            topic="Test Topic",
            target_audience="students"
        )

        # Create content object
        content = generator_service.create_content_from_generation(
            generation_result=generation_result,
            author_id=uuid4()
        )

        assert content.title == generation_result["content_structure"]["title"]
        assert content.content_type == "lesson"
        assert content.content_body == generation_result["generated_content"]

    def test_analyze_content_patterns(self, generator_service):
        """Test analyzing content patterns."""
        content_samples = [
            "This is a sample lesson about programming.",
            "Another lesson with different content structure.",
            "Third lesson focusing on algorithms."
        ]

        patterns = generator_service.analyze_content_patterns(content_samples)

        assert "common_phrases" in patterns
        assert "typical_structure" in patterns
        assert "average_word_count" in patterns
        assert isinstance(patterns["common_phrases"], list)

    def test_improve_content_quality(self, generator_service):
        """Test improving content quality."""
        content = "This is some basic content that needs improvement."
        improvements = ["Add more examples", "Improve clarity"]

        result = generator_service.improve_content_quality(content, improvements)

        assert "original_content" in result
        assert "improved_content" in result
        assert "improvements_applied" in result
        assert result["improvements_applied"] == improvements

    def test_generate_content_variations(self, generator_service):
        """Test generating content variations."""
        base_content = "This is the base content for variations."
        variations = ["beginner", "intermediate", "advanced"]

        variation_results = generator_service.generate_content_variations(
            base_content, variations
        )

        assert len(variation_results) == len(variations)

        for variation in variation_results:
            assert "type" in variation
            assert "content" in variation
            assert "target_audience" in variation

    def test_create_content_series(self, generator_service):
        """Test creating content series."""
        series_title = "Python Programming Series"
        topics = ["Variables", "Functions", "Classes", "Modules"]

        series = generator_service.create_content_series(
            series_title=series_title,
            topics=topics,
            content_type="lesson"
        )

        assert series["title"] == series_title
        assert series["topics"] == topics
        assert series["content_type"] == "lesson"
        assert series["total_parts"] == len(topics)

    def test_generate_next_in_series(self, generator_service):
        """Test generating next part in series."""
        series_id = "test_series"
        previous_content = [
            {"title": "Part 1", "content": "First part content"},
            {"title": "Part 2", "content": "Second part content"}
        ]

        next_part = generator_service.generate_next_in_series(
            series_id=series_id,
            previous_content=previous_content
        )

        assert next_part["series_id"] == series_id
        assert next_part["part_number"] == 3
        assert "title" in next_part
        assert "content" in next_part

    def test_validate_generated_content(self, generator_service):
        """Test validating generated content."""
        content = "This is a sample content for validation testing."
        rules = {
            "min_words": 5,
            "max_words": 100,
            "required_sections": ["introduction", "main_content"]
        }

        validation = generator_service.validate_generated_content(content, rules)

        assert "valid" in validation
        assert "issues" in validation
        assert "word_count" in validation
        assert validation["word_count"] == len(content.split())

    def test_get_generation_statistics(self, generator_service):
        """Test getting generation statistics."""
        stats = generator_service.get_generation_statistics()

        assert "total_generations" in stats
        assert "templates_used" in stats
        assert "average_quality_score" in stats
        assert "generation_success_rate" in stats

    def test_export_generation_template(self, generator_service):
        """Test exporting generation template."""
        template_id = "lesson"

        exported = generator_service.export_generation_template(template_id, "json")

        assert "name" in exported
        assert "structure" in exported
        assert "estimated_time" in exported

    def test_export_template_yaml_format(self, generator_service):
        """Test exporting template in YAML format."""
        template_id = "lesson"

        exported = generator_service.export_generation_template(template_id, "yaml")

        assert "template" in exported
        assert "format" in exported
        assert exported["format"] == "yaml"


