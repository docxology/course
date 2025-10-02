"""Tests for mobile module."""

import pytest
from uuid import uuid4

from curriculum.core.content import Content, ContentType
from curriculum.mobile.mobile import MobileService
from curriculum.mobile.offline import OfflineService


class TestMobileService:
    """Tests for MobileService."""

    @pytest.fixture
    def mobile_service(self):
        """Mobile service fixture."""
        return MobileService()

    def test_mobile_service_initialization(self, mobile_service):
        """Test mobile service initialization."""
        assert mobile_service is not None
        assert hasattr(mobile_service, '_mobile_configs')
        assert hasattr(mobile_service, '_responsive_templates')

    def test_create_mobile_config(self, mobile_service):
        """Test creating mobile configuration."""
        content_id = uuid4()

        config = mobile_service.create_mobile_config(
            content_id=content_id,
            platform="responsive",
            features=["touch_friendly", "swipe_navigation"]
        )

        assert config["content_id"] == str(content_id)
        assert config["platform"] == "responsive"
        assert "touch_friendly" in config["features"]
        assert "responsive_design" in config["features"]

    def test_optimize_content_for_mobile(self, mobile_service):
        """Test content optimization for mobile."""
        content = Content(
            title="Test Content",
            content_type=ContentType.LESSON,
            format="html",
            author_id=uuid4(),
            content_body="<p>Long content</p>" * 100  # Make it long
        )

        optimization = mobile_service.optimize_content_for_mobile(
            content=content,
            target_device="smartphone"
        )

        assert optimization["content_id"] == str(content.id)
        assert optimization["target_device"] == "smartphone"
        assert "optimizations_applied" in optimization
        assert optimization["mobile_score"] >= 0
        assert optimization["mobile_score"] <= 100

    def test_generate_mobile_app_manifest(self, mobile_service):
        """Test generating mobile app manifest."""
        course_id = uuid4()
        course_title = "Test Course"

        manifest = mobile_service.generate_mobile_app_manifest(
            course_id=course_id,
            course_title=course_title
        )

        assert manifest["name"] == course_title
        assert "short_name" in manifest
        assert manifest["display"] == "standalone"
        assert "icons" in manifest
        assert len(manifest["icons"]) >= 2

    def test_create_offline_package(self, mobile_service):
        """Test creating offline package."""
        content_id = uuid4()

        package = mobile_service.create_offline_package(
            content_id=content_id,
            include_media=True,
            compression_level="balanced"
        )

        assert package["content_id"] == str(content_id)
        assert package["format"] == "zip"
        assert package["include_media"] is True
        assert "download_url" in package
        assert "estimated_size" in package

    def test_get_mobile_analytics(self, mobile_service):
        """Test getting mobile analytics."""
        course_id = uuid4()

        analytics = mobile_service.get_mobile_analytics(course_id)

        assert analytics["course_id"] == str(course_id)
        assert "total_mobile_users" in analytics
        assert "mobile_sessions" in analytics
        assert "device_breakdown" in analytics
        assert "os_breakdown" in analytics

    def test_create_mobile_learning_path(self, mobile_service):
        """Test creating mobile learning path."""
        course_id = uuid4()
        user_id = uuid4()

        path = mobile_service.create_mobile_learning_path(
            course_id=course_id,
            user_id=user_id,
            commute_time=30
        )

        assert path["course_id"] == str(course_id)
        assert path["user_id"] == str(user_id)
        assert path["commute_time"] == 30
        assert "suggested_lessons" in path
        assert len(path["suggested_lessons"]) > 0

    def test_generate_mobile_notifications(self, mobile_service):
        """Test generating mobile notifications."""
        user_id = uuid4()

        notification = mobile_service.generate_mobile_notifications(
            user_id=user_id,
            notification_type="study_reminder"
        )

        assert "title" in notification
        assert "body" in notification
        assert "icon" in notification
        assert "actions" in notification

    def test_create_mobile_quiz(self, mobile_service):
        """Test creating mobile quiz."""
        content_id = uuid4()
        questions = [
            {"id": "q1", "question": "Test?", "options": ["A", "B"]},
            {"id": "q2", "question": "Another?", "options": ["C", "D"]},
        ]

        quiz = mobile_service.create_mobile_quiz(
            content_id=content_id,
            questions=questions,
            time_limit=15
        )

        assert quiz["content_id"] == str(content_id)
        assert quiz["title"] == "Mobile Practice Quiz"
        assert len(quiz["questions"]) == 2
        assert quiz["mobile_optimizations"]["large_touch_targets"] is True

    def test_get_mobile_features(self, mobile_service):
        """Test getting mobile features."""
        features = mobile_service.get_mobile_features()

        assert isinstance(features, list)
        assert len(features) > 0

        for feature in features:
            assert "name" in feature
            assert "description" in feature
            assert "platform" in feature
            assert "status" in feature

    def test_validate_mobile_compatibility(self, mobile_service):
        """Test mobile compatibility validation."""
        content = Content(
            title="Test Content",
            content_type=ContentType.LESSON,
            format="html",
            author_id=uuid4(),
            content_body="<p>Content</p>" * 1000  # Long content
        )

        validation = mobile_service.validate_mobile_compatibility(content)

        assert validation["content_id"] == str(content.id)
        assert "mobile_compatibility_score" in validation
        assert validation["mobile_compatibility_score"] >= 0
        assert validation["mobile_compatibility_score"] <= 100

    def test_create_mobile_dashboard(self, mobile_service):
        """Test creating mobile dashboard."""
        user_id = uuid4()
        course_id = uuid4()

        dashboard = mobile_service.create_mobile_dashboard(
            user_id=user_id,
            course_id=course_id
        )

        assert dashboard["user_id"] == str(user_id)
        assert dashboard["course_id"] == str(course_id)
        assert dashboard["layout"] == "mobile_optimized"
        assert "widgets" in dashboard
        assert "navigation" in dashboard


class TestOfflineService:
    """Tests for OfflineService."""

    @pytest.fixture
    def offline_service(self):
        """Offline service fixture."""
        return OfflineService()

    def test_offline_service_initialization(self, offline_service):
        """Test offline service initialization."""
        assert offline_service is not None
        assert hasattr(offline_service, '_offline_packages')
        assert hasattr(offline_service, '_sync_sessions')
        assert hasattr(offline_service, '_cached_content')

    def test_create_offline_package(self, offline_service):
        """Test creating offline package."""
        course_id = uuid4()
        content_ids = [uuid4(), uuid4(), uuid4()]

        package = offline_service.create_offline_package(
            course_id=course_id,
            content_ids=content_ids,
            include_media=True,
            compression_level="high"
        )

        assert package["course_id"] == str(course_id)
        assert len(package["content_ids"]) == 3
        assert package["include_media"] is True
        assert package["compression_level"] == "high"
        assert "download_url" in package

    def test_get_offline_package(self, offline_service):
        """Test getting offline package details."""
        course_id = uuid4()

        # Create a package first
        package = offline_service.create_offline_package(course_id, [uuid4()])

        # Retrieve it
        retrieved = offline_service.get_offline_package(package["id"])

        assert retrieved is not None
        assert retrieved["id"] == package["id"]

    def test_cache_content_for_offline(self, offline_service):
        """Test caching content for offline access."""
        content_id = uuid4()
        user_id = uuid4()

        cache_entry = offline_service.cache_content_for_offline(
            content_id=content_id,
            user_id=user_id,
            cache_duration=24
        )

        assert cache_entry["content_id"] == str(content_id)
        assert cache_entry["user_id"] == str(user_id)
        assert "cached_at" in cache_entry
        assert "expires_at" in cache_entry

    def test_start_sync_session(self, offline_service):
        """Test starting sync session."""
        user_id = uuid4()
        device_id = "device_123"

        session = offline_service.start_sync_session(
            user_id=user_id,
            device_id=device_id,
            sync_direction="bidirectional"
        )

        assert session["user_id"] == str(user_id)
        assert session["device_id"] == device_id
        assert session["sync_direction"] == "bidirectional"
        assert session["status"] == "syncing"

    def test_sync_progress_offline(self, offline_service):
        """Test syncing progress from offline."""
        session_id = uuid4()
        progress_data = {
            "lessons_completed": [uuid4(), uuid4()],
            "notes": ["Note 1", "Note 2"]
        }

        # Mock session
        offline_service._sync_sessions = {
            session_id: {"items_synced": 0, "status": "syncing"}
        }

        sync_result = offline_service.sync_progress_offline(session_id, progress_data)

        assert sync_result["session_id"] == str(session_id)
        assert "items_synced" in sync_result
        assert "sync_summary" in sync_result

    def test_get_offline_content_list(self, offline_service):
        """Test getting offline content list."""
        user_id = uuid4()

        # Create some cache entries
        for i in range(3):
            offline_service.cache_content_for_offline(uuid4(), user_id)

        content_list = offline_service.get_offline_content_list(user_id)

        assert isinstance(content_list, list)
        assert len(content_list) >= 3

    def test_create_offline_study_plan(self, offline_service):
        """Test creating offline study plan."""
        user_id = uuid4()
        course_id = uuid4()

        plan = offline_service.create_offline_study_plan(
            user_id=user_id,
            course_id=course_id,
            available_offline_time=120
        )

        assert plan["user_id"] == str(user_id)
        assert plan["course_id"] == str(course_id)
        assert plan["available_time"] == 120
        assert "suggested_content" in plan

    def test_generate_offline_manifest(self, offline_service):
        """Test generating offline manifest."""
        package_id = uuid4()
        content_structure = {
            "lessons": 5,
            "quizzes": 2,
            "files": ["lesson1.html", "quiz1.html"]
        }

        manifest = offline_service.generate_offline_manifest(package_id, content_structure)

        assert str(package_id) in manifest
        assert "content_structure" in manifest
        assert "requirements" in manifest

    def test_validate_offline_package(self, offline_service):
        """Test validating offline package."""
        package_id = uuid4()
        checksum = "abc123"

        # Create package first
        offline_service.create_offline_package(uuid4(), [uuid4()])

        validation = offline_service.validate_offline_package(package_id, checksum)

        assert "package_id" in validation
        assert "is_valid" in validation
        assert "file_count" in validation

    def test_get_offline_usage_statistics(self, offline_service):
        """Test getting offline usage statistics."""
        user_id = uuid4()

        # Create some cache entries
        for i in range(3):
            offline_service.cache_content_for_offline(uuid4(), user_id)

        stats = offline_service.get_offline_usage_statistics(user_id)

        assert stats["user_id"] == str(user_id)
        assert "cached_content_count" in stats
        assert "total_cache_size" in stats
        assert "offline_sessions" in stats

    def test_create_offline_notification(self, offline_service):
        """Test creating offline notification."""
        user_id = uuid4()

        notification = offline_service.create_offline_notification(
            user_id=user_id,
            notification_type="sync_reminder",
            message="Remember to sync your progress"
        )

        assert notification["user_id"] == str(user_id)
        assert notification["type"] == "sync_reminder"
        assert notification["message"] == "Remember to sync your progress"

    def test_get_offline_capabilities(self, offline_service):
        """Test getting offline capabilities."""
        capabilities = offline_service.get_offline_capabilities()

        assert "supported_features" in capabilities
        assert "storage_requirements" in capabilities
        assert "supported_platforms" in capabilities
        assert "sync_methods" in capabilities
        assert "content_types" in capabilities

    def test_estimate_offline_storage(self, offline_service):
        """Test estimating offline storage requirements."""
        content_ids = [uuid4(), uuid4(), uuid4()]

        estimate = offline_service.estimate_offline_storage(
            content_ids=content_ids,
            include_media=True
        )

        assert estimate["content_count"] == 3
        assert estimate["include_media"] is True
        assert "estimated_size" in estimate
        assert "breakdown" in estimate

    def test_create_offline_backup(self, offline_service):
        """Test creating offline backup."""
        user_id = uuid4()

        backup = offline_service.create_offline_backup(
            user_id=user_id,
            backup_type="full"
        )

        assert backup["user_id"] == str(user_id)
        assert backup["type"] == "full"
        assert "includes" in backup
        assert "download_url" in backup

    def test_restore_from_backup(self, offline_service):
        """Test restoring from backup."""
        user_id = uuid4()
        backup_id = uuid4()

        # Mock backup
        offline_service._offline_packages = {
            backup_id: {"id": str(backup_id)}
        }

        restore_options = {"merge": True}

        restore_result = offline_service.restore_from_backup(
            user_id=user_id,
            backup_id=backup_id,
            restore_options=restore_options
        )

        assert restore_result["user_id"] == str(user_id)
        assert restore_result["backup_id"] == str(backup_id)
        assert "restored_items" in restore_result


