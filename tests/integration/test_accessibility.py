"""Tests for accessibility module."""

import pytest
from uuid import uuid4

from curriculum.core.content import Content, ContentType
from curriculum.accessibility.accessibility import AccessibilityService


@pytest.mark.integration
class TestAccessibilityService:
    """Tests for AccessibilityService."""

    @pytest.fixture
    def accessibility_service(self):
        """Accessibility service fixture."""
        return AccessibilityService()

    def test_accessibility_service_initialization(self, accessibility_service):
        """Test accessibility service initialization."""
        assert accessibility_service is not None
        assert hasattr(accessibility_service, '_accessibility_profiles')
        assert hasattr(accessibility_service, '_content_accessibility')

    def test_create_accessibility_profile(self, accessibility_service):
        """Test creating accessibility profile."""
        user_id = uuid4()
        preferences = {
            "font_size": "large",
            "high_contrast": True,
            "screen_reader": True,
        }

        profile = accessibility_service.create_accessibility_profile(user_id, preferences)

        assert profile["user_id"] == str(user_id)
        assert profile["visual_preferences"]["font_size"] == "large"
        assert profile["visual_preferences"]["high_contrast"] is True
        assert profile["audio_preferences"]["screen_reader"] is True

    def test_analyze_content_accessibility(self, accessibility_service):
        """Test content accessibility analysis."""
        content = Content(
            title="Test Content",
            content_type=ContentType.LESSON,
            format="markdown",
            author_id=uuid4(),
            content_body="<img src='test.jpg'>No alt text</img><h1>Title</h1>",
        )

        analysis = accessibility_service.analyze_content_accessibility(content)

        assert analysis["content_id"] == str(content.id)
        assert "issues" in analysis
        assert "recommendations" in analysis
        assert "score" in analysis
        assert analysis["score"] >= 0 and analysis["score"] <= 100

    def test_generate_alt_text(self, accessibility_service):
        """Test alt text generation."""
        image_description = "A diagram showing data flow"

        alt_text = accessibility_service.generate_alt_text(image_description)

        assert "Image showing:" in alt_text
        assert image_description in alt_text

    def test_create_accessible_version(self, accessibility_service):
        """Test creating accessible version."""
        content_id = uuid4()
        accessibility_features = {
            "screen_reader": True,
            "high_contrast": True,
        }

        accessible_content = accessibility_service.create_accessible_version(
            content_id, accessibility_features
        )

        assert accessible_content["content_id"] == str(content_id)
        assert accessible_content["original_content_id"] == str(content_id)
        assert "accessibility_features" in accessible_content
        assert "modifications" in accessible_content

    def test_validate_keyboard_navigation(self, accessibility_service):
        """Test keyboard navigation validation."""
        html_content = '<button onclick="alert()">Click me</button><a href="#main">Skip to main</a>'

        validation = accessibility_service.validate_keyboard_navigation(html_content)

        assert "valid" in validation
        assert "issues" in validation
        assert "recommendations" in validation

    def test_generate_screen_reader_content(self, accessibility_service):
        """Test screen reader content generation."""
        content = Content(
            title="Screen Reader Test",
            content_type=ContentType.LESSON,
            format="markdown",
            author_id=uuid4(),
            content_body="This is content for screen readers.",
        )

        user_profile = {"screen_reader": True}
        screen_content = accessibility_service.generate_screen_reader_content(content, user_profile)

        assert "Course:" in screen_content
        assert "Content Type:" in screen_content
        assert "Main Content:" in screen_content
        assert content.content_body in screen_content

    def test_create_sign_language_video(self, accessibility_service):
        """Test sign language video creation."""
        content_id = uuid4()
        text_content = "This is content for sign language."

        video = accessibility_service.create_sign_language_video(content_id, text_content)

        assert video["content_id"] == str(content_id)
        assert "video_url" in video
        assert "duration" in video
        assert "language" in video

    def test_get_accessibility_guidelines(self, accessibility_service):
        """Test getting accessibility guidelines."""
        guidelines = accessibility_service.get_accessibility_guidelines("wcag")

        assert guidelines["standard"] == "WCAG 2.1"
        assert "principles" in guidelines
        assert len(guidelines["principles"]) == 4

        # Check each principle
        for principle in guidelines["principles"]:
            assert "name" in principle
            assert "guidelines" in principle

    def test_audit_course_accessibility(self, accessibility_service):
        """Test course accessibility audit."""
        course_id = uuid4()

        audit = accessibility_service.audit_course_accessibility(course_id)

        assert audit["course_id"] == str(course_id)
        assert "overall_score" in audit
        assert "compliance_level" in audit
        assert "issues_found" in audit
        assert "recommendations" in audit

    def test_create_accessibility_report(self, accessibility_service):
        """Test creating accessibility report."""
        user_id = uuid4()
        content_id = uuid4()
        issues = [
            {"severity": "major", "description": "Missing alt text"},
            {"severity": "minor", "description": "Color contrast issue"},
        ]

        report = accessibility_service.create_accessibility_report(user_id, content_id, issues)

        assert report["user_id"] == str(user_id)
        assert report["content_id"] == str(content_id)
        assert report["issues"] == issues
        assert "priority_levels" in report

    def test_get_supported_languages(self, accessibility_service):
        """Test getting supported languages."""
        languages = accessibility_service.get_supported_languages()

        assert isinstance(languages, list)
        assert "en" in languages
        assert "es" in languages
        assert "fr" in languages

    def test_translate_for_accessibility(self, accessibility_service):
        """Test accessibility translation."""
        text = "Hello world"
        translated = accessibility_service.translate_for_accessibility(text, "es", "general")

        assert isinstance(translated, str)
        assert len(translated) > 0

    def test_create_braille_version(self, accessibility_service):
        """Test braille version creation."""
        content_id = uuid4()
        content = "This is content for braille conversion."

        braille = accessibility_service.create_braille_version(content_id, content)

        assert braille["content_id"] == str(content_id)
        assert "braille_content" in braille
        assert "grade" in braille
        assert "pages" in braille

    def test_get_accessibility_tools(self, accessibility_service):
        """Test getting accessibility tools."""
        tools = accessibility_service.get_accessibility_tools()

        assert isinstance(tools, list)
        assert len(tools) > 0

        for tool in tools:
            assert "name" in tool
            assert "description" in tool
            assert "type" in tool
            assert "status" in tool

    def test_accessibility_analysis_with_good_content(self, accessibility_service):
        """Test accessibility analysis with well-formed content."""
        content = Content(
            title="Well-formed Content",
            content_type=ContentType.LESSON,
            format="html",
            author_id=uuid4(),
            content_body='<img src="test.jpg" alt="Test image"><h1>Title</h1><p>Content</p>',
        )

        analysis = accessibility_service.analyze_content_accessibility(content)

        # Should have fewer issues with well-formed content
        assert analysis["score"] >= 70  # Should be reasonably good

    def test_accessibility_analysis_with_poor_content(self, accessibility_service):
        """Test accessibility analysis with poorly formed content."""
        content = Content(
            title="Poor Content",
            content_type=ContentType.LESSON,
            format="html",
            author_id=uuid4(),
            content_body='<img src="test.jpg"><div style="color: white; background: black;">Hidden text</div>',
        )

        analysis = accessibility_service.analyze_content_accessibility(content)

        # Should have multiple issues
        assert len(analysis["issues"]) > 0
        assert analysis["score"] < 80  # Should be lower score


