"""Mobile support and responsive design service."""

from typing import Any, Dict, List, Optional
from uuid import UUID

from curriculum.core.content import Content


class MobileService:
    """Service for mobile optimization and responsive features."""

    def __init__(self) -> None:
        """Initialize mobile service."""
        self._mobile_configs: dict[UUID, dict] = {}
        self._responsive_templates: Dict[str, dict] = {
            "default": {
                "name": "Default Responsive",
                "breakpoints": {
                    "mobile": "576px",
                    "tablet": "768px",
                    "desktop": "992px",
                    "large": "1200px",
                },
                "features": ["touch_friendly", "swipe_navigation", "mobile_menu"],
            },
            "mobile_first": {
                "name": "Mobile First",
                "breakpoints": {
                    "mobile": "480px",
                    "tablet": "768px",
                    "desktop": "1024px",
                },
                "features": ["progressive_enhancement", "offline_first", "gesture_support"],
            },
        }

    def create_mobile_config(
        self,
        content_id: UUID,
        platform: str = "responsive",
        features: List[str] = None,
    ) -> Dict[str, Any]:
        """Create mobile configuration for content."""
        config_id = content_id  # Use the content_id directly

        config = {
            "id": str(config_id),
            "content_id": str(content_id),
            "platform": platform,
            "features": features
            or [
                "responsive_design",
                "touch_optimization",
                "mobile_navigation",
                "progressive_loading",
            ],
            "performance_settings": {
                "image_optimization": True,
                "lazy_loading": True,
                "compression": True,
                "caching": True,
            },
            "accessibility_mobile": {
                "touch_targets": "44px minimum",
                "gesture_support": True,
                "voice_control": False,
                "haptic_feedback": True,
            },
            "offline_capabilities": {
                "downloadable_content": True,
                "offline_reading": True,
                "sync_progress": True,
                "background_sync": False,
            },
            "created_at": "2024-01-01T00:00:00Z",
        }

        self._mobile_configs[config_id] = config
        return config

    def optimize_content_for_mobile(
        self,
        content: Content,
        target_device: str = "smartphone",
    ) -> Dict[str, Any]:
        """Optimize content for mobile devices."""
        optimizations = []

        # Content optimizations
        if len(content.content_body) > 10000:  # Long content
            optimizations.append("content_chunking")
            optimizations.append("progressive_loading")

        # Media optimizations
        if "video" in content.content_body.lower():
            optimizations.append("video_compression")
            optimizations.append("adaptive_bitrate")

        if "img" in content.content_body:
            optimizations.append("image_optimization")
            optimizations.append("responsive_images")

        # Navigation optimizations
        optimizations.append("mobile_navigation")
        optimizations.append("touch_friendly_interface")

        return {
            "content_id": str(content.id),
            "target_device": target_device,
            "optimizations_applied": optimizations,
            "estimated_load_time": 2.5,  # seconds
            "bandwidth_saved": 45,  # percentage
            "mobile_score": 85,  # out of 100
            "optimized_at": "2024-01-01T00:00:00Z",
        }

    def generate_mobile_app_manifest(
        self,
        course_id: UUID,
        course_title: str,
    ) -> Dict[str, Any]:
        """Generate Progressive Web App manifest."""
        return {
            "name": course_title,
            "short_name": course_title[:12] + "..." if len(course_title) > 12 else course_title,
            "description": f"Mobile learning app for {course_title}",
            "start_url": f"/courses/{course_id}/mobile",
            "display": "standalone",
            "background_color": "#ffffff",
            "theme_color": "#007bff",
            "orientation": "portrait-primary",
            "categories": ["education", "productivity"],
            "icons": [
                {
                    "src": "/icons/icon-192x192.png",
                    "sizes": "192x192",
                    "type": "image/png",
                    "purpose": "any maskable",
                },
                {
                    "src": "/icons/icon-512x512.png",
                    "sizes": "512x512",
                    "type": "image/png",
                    "purpose": "any maskable",
                },
            ],
            "shortcuts": [
                {
                    "name": "My Progress",
                    "short_name": "Progress",
                    "description": "View learning progress",
                    "url": f"/courses/{course_id}/progress",
                    "icons": [{"src": "/icons/progress.png", "sizes": "96x96"}],
                },
                {
                    "name": "Assignments",
                    "short_name": "Assignments",
                    "description": "View assignments",
                    "url": f"/courses/{course_id}/assignments",
                    "icons": [{"src": "/icons/assignments.png", "sizes": "96x96"}],
                },
            ],
        }

    def create_offline_package(
        self,
        content_id: UUID,
        include_media: bool = True,
        compression_level: str = "balanced",
    ) -> Dict[str, Any]:
        """Create offline downloadable package."""
        package_id = UUID(f"offline_{content_id}")

        package = {
            "id": str(package_id),
            "content_id": str(content_id),
            "format": "zip",
            "includes": [
                "content_html",
                "images" if include_media else None,
                "videos" if include_media else None,
                "assessments",
                "progress_tracking",
            ],
            "compression_level": compression_level,
            "estimated_size": "25MB" if include_media else "2MB",
            "validity_period": "30 days",
            "download_url": f"/api/offline/{package_id}/download",
            "created_at": "2024-01-01T00:00:00Z",
        }

        # Remove None values
        package["includes"] = [item for item in package["includes"] if item]

        return package

    def get_mobile_analytics(self, course_id: UUID) -> Dict[str, Any]:
        """Get mobile usage analytics."""
        return {
            "course_id": str(course_id),
            "total_mobile_users": 1250,
            "mobile_sessions": 3400,
            "average_session_duration": 18,  # minutes
            "top_mobile_features": [
                "video_lectures",
                "practice_quizzes",
                "progress_tracking",
                "offline_reading",
            ],
            "device_breakdown": {
                "smartphones": 65,  # percentage
                "tablets": 25,
                "other": 10,
            },
            "os_breakdown": {
                "ios": 45,
                "android": 50,
                "other": 5,
            },
            "generated_at": "2024-01-01T00:00:00Z",
        }

    def create_mobile_learning_path(
        self,
        course_id: UUID,
        user_id: UUID,
        commute_time: int = 30,  # minutes
    ) -> Dict[str, Any]:
        """Create mobile-optimized learning path."""
        path_id = UUID(f"mobile_path_{user_id}")

        # Suggest bite-sized lessons for mobile learning
        learning_path = {
            "id": str(path_id),
            "course_id": str(course_id),
            "user_id": str(user_id),
            "commute_time": commute_time,
            "suggested_lessons": [
                {
                    "id": "lesson_1",
                    "title": "Quick Review: Variables",
                    "duration": 15,  # minutes
                    "type": "review",
                    "mobile_optimized": True,
                },
                {
                    "id": "lesson_2",
                    "title": "Practice: Basic Operations",
                    "duration": 12,
                    "type": "practice",
                    "mobile_optimized": True,
                },
            ],
            "total_estimated_time": 27,  # minutes
            "completion_goal": "Complete 3 lessons per commute",
            "created_at": "2024-01-01T00:00:00Z",
        }

        return learning_path

    def generate_mobile_notifications(
        self,
        user_id: UUID,
        notification_type: str = "study_reminder",
    ) -> Dict[str, Any]:
        """Generate mobile push notifications."""
        notifications = {
            "study_reminder": {
                "title": "Time to Study!",
                "body": "You have 15 minutes of Python practice waiting for you.",
                "icon": "/icons/study.png",
                "badge": "/icons/badge.png",
                "actions": [
                    {"action": "open_app", "title": "Start Studying"},
                    {"action": "dismiss", "title": "Later"},
                ],
            },
            "assignment_due": {
                "title": "Assignment Due Soon",
                "body": "Your Functions assignment is due in 2 hours.",
                "icon": "/icons/assignment.png",
                "badge": "/icons/urgent.png",
                "actions": [
                    {"action": "view_assignment", "title": "View Assignment"},
                    {"action": "extend_deadline", "title": "Request Extension"},
                ],
            },
            "achievement": {
                "title": "🎉 Achievement Unlocked!",
                "body": "You've completed 5 lessons this week!",
                "icon": "/icons/achievement.png",
                "badge": "/icons/star.png",
                "actions": [
                    {"action": "view_achievements", "title": "View Achievements"},
                ],
            },
        }

        return notifications.get(notification_type, notifications["study_reminder"])

    def create_mobile_quiz(
        self,
        content_id: UUID,
        questions: List[Dict[str, Any]],
        time_limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Create a mobile-optimized quiz."""
        quiz_id = UUID(f"mobile_quiz_{content_id}")

        mobile_quiz = {
            "id": str(quiz_id),
            "content_id": str(content_id),
            "title": "Mobile Practice Quiz",
            "questions": questions,
            "mobile_optimizations": {
                "large_touch_targets": True,
                "swipe_navigation": True,
                "voice_responses": False,  # Future feature
                "haptic_feedback": True,
                "progressive_questions": True,
            },
            "time_limit": time_limit,
            "passing_score": 70,
            "attempts_allowed": 3,
            "created_at": "2024-01-01T00:00:00Z",
        }

        return mobile_quiz

    def get_mobile_features(self) -> List[Dict[str, Any]]:
        """Get available mobile features."""
        return [
            {
                "name": "Offline Learning",
                "description": "Download content for offline access",
                "platform": ["ios", "android", "web"],
                "status": "available",
            },
            {
                "name": "Push Notifications",
                "description": "Study reminders and updates",
                "platform": ["ios", "android"],
                "status": "available",
            },
            {
                "name": "Progressive Web App",
                "description": "Install as native-like app",
                "platform": ["web"],
                "status": "available",
            },
            {
                "name": "Voice Responses",
                "description": "Answer questions with voice",
                "platform": ["ios", "android"],
                "status": "planned",
            },
            {
                "name": "Gesture Navigation",
                "description": "Swipe and tap gestures",
                "platform": ["ios", "android", "web"],
                "status": "available",
            },
        ]

    def validate_mobile_compatibility(
        self,
        content: Content,
    ) -> Dict[str, Any]:
        """Validate content for mobile compatibility."""
        issues = []
        recommendations = []

        # Check content length
        if len(content.content_body) > 50000:
            issues.append("Content too long for mobile optimization")
            recommendations.append("Break into smaller chunks")

        # Check for unsupported media
        if "flash" in content.content_body.lower():
            issues.append("Flash content not supported on mobile")
            recommendations.append("Convert to HTML5 video")

        # Check for mobile-unfriendly elements
        if "hover" in content.content_body:
            issues.append("Hover effects may not work on touch devices")
            recommendations.append("Add touch event handlers")

        return {
            "content_id": str(content.id),
            "mobile_compatibility_score": max(0, 100 - len(issues) * 10),
            "issues": issues,
            "recommendations": recommendations,
            "supported_platforms": ["ios", "android", "web"],
            "validated_at": "2024-01-01T00:00:00Z",
        }

    def create_mobile_dashboard(
        self,
        user_id: UUID,
        course_id: UUID,
    ) -> Dict[str, Any]:
        """Create mobile-optimized dashboard."""
        return {
            "user_id": str(user_id),
            "course_id": str(course_id),
            "layout": "mobile_optimized",
            "widgets": [
                {
                    "type": "progress_ring",
                    "title": "Course Progress",
                    "value": 67,  # percentage
                    "color": "#28a745",
                },
                {
                    "type": "quick_actions",
                    "actions": [
                        {"name": "Continue Learning", "icon": "play", "url": "/lessons/current"},
                        {"name": "Practice Quiz", "icon": "quiz", "url": "/practice"},
                        {"name": "View Grades", "icon": "grades", "url": "/grades"},
                    ],
                },
                {
                    "type": "study_streak",
                    "current_streak": 7,
                    "best_streak": 14,
                    "unit": "days",
                },
                {
                    "type": "upcoming_deadlines",
                    "items": [
                        {"title": "Assignment 3", "due_in": "2 days"},
                        {"title": "Quiz 2", "due_in": "5 days"},
                    ],
                },
            ],
            "navigation": {
                "bottom_tabs": [
                    {"name": "Learn", "icon": "book", "active": True},
                    {"name": "Practice", "icon": "quiz", "active": False},
                    {"name": "Progress", "icon": "chart", "active": False},
                    {"name": "Profile", "icon": "user", "active": False},
                ],
            },
            "generated_at": "2024-01-01T00:00:00Z",
        }
