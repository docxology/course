"""Tests for mobile module services."""

import pytest
from uuid import uuid4

from curriculum.core.content import Content, ContentType, ContentFormat
from curriculum.mobile.mobile import MobileService


@pytest.mark.unit
class TestMobileService:
    """Tests for MobileService."""

    @pytest.fixture
    def mobile_service(self):
        """Create MobileService instance."""
        return MobileService()

    @pytest.fixture
    def sample_content(self):
        """Create sample content."""
        return Content(
            title="Mobile Test Content",
            content_type=ContentType.LESSON,
            format=ContentFormat.MARKDOWN,
            author_id=uuid4(),
            content_body="# Mobile Content\nThis is mobile-optimized content.",
        )

    def test_mobile_service_initialization(self, mobile_service):
        """Test MobileService initialization."""
        assert mobile_service is not None
        assert isinstance(mobile_service._mobile_configs, dict)
        assert isinstance(mobile_service._responsive_templates, dict)
        assert "default" in mobile_service._responsive_templates
        assert "mobile_first" in mobile_service._responsive_templates

    def test_create_mobile_config(self, mobile_service, sample_content):
        """Test mobile configuration creation."""
        features = ["touch_friendly", "swipe_navigation"]
        result = mobile_service.create_mobile_config(
            content_id=sample_content.id,
            platform="responsive",
            features=features,
        )

        assert result is not None
        assert isinstance(result, dict)
        assert "id" in result
        assert "content_id" in result
        assert "platform" in result
        assert "features" in result
        assert result["platform"] == "responsive"
        assert result["features"] == features

    def test_optimize_content_for_mobile(self, mobile_service, sample_content):
        """Test content optimization for mobile."""
        result = mobile_service.optimize_content_for_mobile(
            content=sample_content,
            target_device="mobile"
        )

        assert result is not None
        assert isinstance(result, dict)
        assert "optimizations_applied" in result
        assert "estimated_load_time" in result
        assert "mobile_score" in result
        assert isinstance(result["optimizations_applied"], list)
        assert isinstance(result["mobile_score"], (int, float))
        assert 0 <= result["mobile_score"] <= 100

    def test_validate_mobile_compatibility(self, mobile_service, sample_content):
        """Test mobile compatibility validation."""
        result = mobile_service.validate_mobile_compatibility(sample_content)

        assert result is not None
        assert isinstance(result, dict)
        assert "mobile_compatibility_score" in result
        assert "issues" in result
        assert isinstance(result["mobile_compatibility_score"], (int, float))
        assert isinstance(result["issues"], list)

    def test_generate_mobile_app_manifest(self, mobile_service):
        """Test mobile app manifest generation."""
        course_id = uuid4()
        course_title = "Advanced Python Programming"

        result = mobile_service.generate_mobile_app_manifest(course_id, course_title)

        assert result is not None
        assert isinstance(result, dict)
        assert "name" in result
        assert "short_name" in result
        assert "start_url" in result
        assert "display" in result
        assert "theme_color" in result
        assert "icons" in result
        assert result["name"] == course_title
        assert result["start_url"] == f"/courses/{course_id}/mobile"
        assert result["display"] == "standalone"

    def test_create_mobile_dashboard(self, mobile_service):
        """Test mobile dashboard creation."""
        user_id = uuid4()
        course_id = uuid4()

        result = mobile_service.create_mobile_dashboard(user_id, course_id)

        assert result is not None
        assert isinstance(result, dict)
        assert "layout" in result
        assert "widgets" in result
        assert "navigation" in result
        assert result["layout"] == "mobile_optimized"
        assert isinstance(result["widgets"], list)
        assert isinstance(result["navigation"], dict)

    def test_mobile_config_storage(self, mobile_service, sample_content):
        """Test mobile configuration storage and retrieval."""
        config = mobile_service.create_mobile_config(
            content_id=sample_content.id,
            platform="mobile_first"
        )

        # Config should be stored
        assert sample_content.id in mobile_service._mobile_configs

        # Test retrieval (this would typically be a separate method)
        stored_config = mobile_service._mobile_configs[sample_content.id]
        assert stored_config is not None
        assert stored_config["platform"] == "mobile_first"

    def test_responsive_template_access(self, mobile_service):
        """Test responsive template functionality."""
        default_template = mobile_service._responsive_templates["default"]

        assert default_template is not None
        assert isinstance(default_template, dict)
        assert "name" in default_template
        assert "breakpoints" in default_template
        assert "features" in default_template
        assert "Default Responsive" in default_template["name"]

        # Check breakpoints
        breakpoints = default_template["breakpoints"]
        assert "mobile" in breakpoints
        assert "tablet" in breakpoints
        assert "desktop" in breakpoints

        # Check features
        features = default_template["features"]
        assert isinstance(features, list)
        assert "touch_friendly" in features

    def test_mobile_features_list(self, mobile_service):
        """Test mobile features enumeration."""
        # Test that default features are available in templates
        default_template = mobile_service._responsive_templates["default"]
        features = default_template["features"]

        assert features is not None
        assert isinstance(features, list)
        assert len(features) > 0

        # Should include standard mobile features
        common_features = ["touch_friendly", "swipe_navigation", "mobile_menu"]
        for feature in common_features:
            assert feature in features, f"Feature {feature} not found in features list"

    def test_content_chunking_for_mobile(self, mobile_service):
        """Test content chunking for mobile optimization."""
        # Create large content
        large_content = Content(
            title="Large Content",
            content_type=ContentType.LESSON,
            format=ContentFormat.MARKDOWN,
            author_id=uuid4(),
            content_body="Long content " * 1000,  # Very long content
        )

        result = mobile_service.optimize_content_for_mobile(large_content, "mobile")

        # Should apply chunking for large content
        if len(large_content.content_body) > 10000:
            assert "content_chunking" in result["optimizations_applied"]

    def test_mobile_config_validation(self, mobile_service, sample_content):
        """Test mobile configuration validation."""
        # Test with invalid platform
        result = mobile_service.create_mobile_config(
            content_id=sample_content.id,
            platform="invalid_platform"
        )

        assert result is not None
        assert result["platform"] == "invalid_platform"  # Should still work

    def test_mobile_service_methods_exist(self, mobile_service):
        """Test that all expected methods exist."""
        required_methods = [
            "create_mobile_config",
            "optimize_content_for_mobile",
            "validate_mobile_compatibility",
            "generate_mobile_app_manifest",
            "create_mobile_dashboard",
        ]

        for method_name in required_methods:
            assert hasattr(mobile_service, method_name), f"Method {method_name} not found"
            assert callable(getattr(mobile_service, method_name)), f"Method {method_name} not callable"
