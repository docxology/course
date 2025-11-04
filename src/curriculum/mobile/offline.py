"""Offline support service for downloadable content."""

from typing import Any, Dict, List, Optional
from uuid import UUID

from curriculum.core.content import Content


class OfflineService:
    """Service for offline content and sync capabilities."""

    def __init__(self) -> None:
        """Initialize offline service."""
        self._offline_packages: dict[UUID, dict] = {}
        self._sync_sessions: dict[UUID, dict] = {}
        self._cached_content: dict[UUID, dict] = {}

    def create_offline_package(
        self,
        course_id: UUID,
        content_ids: List[UUID],
        include_media: bool = True,
        compression_level: str = "balanced",
    ) -> Dict[str, Any]:
        """Create an offline package for download."""
        package_id = UUID(f"offline_{course_id}")

        package = {
            "id": str(package_id),
            "course_id": str(course_id),
            "content_ids": [str(cid) for cid in content_ids],
            "format": "zip",
            "include_media": include_media,
            "compression_level": compression_level,
            "estimated_size": "150MB" if include_media else "45MB",
            "validity_period": "30 days",
            "download_url": f"/api/offline/{package_id}/download",
            "manifest": {
                "version": "1.0",
                "created_at": "2024-01-01T00:00:00Z",
                "content_items": len(content_ids),
                "media_files": 25 if include_media else 0,
                "total_size": "150MB" if include_media else "45MB",
            },
            "features": [
                "offline_reading",
                "progress_sync",
                "note_taking",
                "bookmarking",
                "search",
            ],
            "created_at": "2024-01-01T00:00:00Z",
        }

        self._offline_packages[package_id] = package
        return package

    def get_offline_package(self, package_id: UUID) -> Optional[Dict[str, Any]]:
        """Get offline package details."""
        return self._offline_packages.get(package_id)

    def cache_content_for_offline(
        self,
        content_id: UUID,
        user_id: UUID,
        cache_duration: int = 24,  # hours
    ) -> Dict[str, Any]:
        """Cache content for offline access."""
        cache_id = UUID(f"cache_{content_id}_{user_id}")

        cache_entry = {
            "id": str(cache_id),
            "content_id": str(content_id),
            "user_id": str(user_id),
            "cached_at": "2024-01-01T00:00:00Z",
            "expires_at": f"2024-01-0{cache_duration + 1}T00:00:00Z",
            "size": "2.5MB",  # Mock size
            "is_compressed": True,
            "version": "1.0",
        }

        self._cached_content[cache_id] = cache_entry
        return cache_entry

    def start_sync_session(
        self,
        user_id: UUID,
        device_id: str,
        sync_direction: str = "bidirectional",
    ) -> Dict[str, Any]:
        """Start an offline sync session."""
        session_id = UUID(f"sync_{user_id}_{device_id}")

        session = {
            "id": str(session_id),
            "user_id": str(user_id),
            "device_id": device_id,
            "sync_direction": sync_direction,
            "start_time": "2024-01-01T00:00:00Z",
            "status": "syncing",
            "items_synced": 0,
            "total_items": 0,
            "errors": [],
        }

        self._sync_sessions[session_id] = session
        return session

    def sync_progress_offline(
        self,
        session_id: UUID,
        progress_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Sync progress data from offline session."""
        session = self._sync_sessions.get(session_id)
        if not session:
            return {"error": "Sync session not found"}

        # Mock sync process
        synced_items = len(progress_data.get("lessons_completed", []))
        session["items_synced"] += synced_items
        session["status"] = "completed"

        return {
            "session_id": str(session_id),
            "items_synced": synced_items,
            "sync_summary": {
                "lessons_completed": len(progress_data.get("lessons_completed", [])),
                "notes_synced": len(progress_data.get("notes", [])),
                "bookmarks_synced": len(progress_data.get("bookmarks", [])),
            },
            "synced_at": "2024-01-01T00:00:00Z",
        }

    def get_offline_content_list(self, user_id: UUID) -> List[Dict[str, Any]]:
        """Get list of content available offline."""
        user_cache = [
            cache for cache in self._cached_content.values() if cache["user_id"] == str(user_id)
        ]

        return [
            {
                "content_id": cache["content_id"],
                "cached_at": cache["cached_at"],
                "expires_at": cache["expires_at"],
                "size": cache["size"],
                "is_expired": False,  # Would check actual expiration
            }
            for cache in user_cache
        ]

    def create_offline_study_plan(
        self,
        user_id: UUID,
        course_id: UUID,
        available_offline_time: int,  # minutes
    ) -> Dict[str, Any]:
        """Create an offline study plan."""
        plan_id = UUID(f"offline_plan_{user_id}")

        study_plan = {
            "id": str(plan_id),
            "user_id": str(user_id),
            "course_id": str(course_id),
            "available_time": available_offline_time,
            "suggested_content": [
                {
                    "content_id": "content_1",
                    "title": "Offline Lesson 1",
                    "estimated_time": 25,
                    "priority": "high",
                },
                {
                    "content_id": "content_2",
                    "title": "Offline Lesson 2",
                    "estimated_time": 20,
                    "priority": "medium",
                },
            ],
            "total_estimated_time": 45,
            "created_at": "2024-01-01T00:00:00Z",
        }

        return study_plan

    def generate_offline_manifest(
        self,
        package_id: UUID,
        content_structure: Dict[str, Any],
    ) -> str:
        """Generate manifest file for offline package."""
        manifest = {
            "package_id": str(package_id),
            "version": "1.0",
            "created_at": "2024-01-01T00:00:00Z",
            "content_structure": content_structure,
            "metadata": {
                "title": "Offline Learning Package",
                "description": "Downloadable course content",
                "author": "Curriculum System",
            },
            "requirements": {
                "min_storage": "200MB",
                "supported_platforms": ["ios", "android", "windows", "macos"],
            },
        }

        return str(manifest)  # In production, this would be JSON

    def validate_offline_package(
        self,
        package_id: UUID,
        checksum: str,
    ) -> Dict[str, Any]:
        """Validate offline package integrity."""
        package = self.get_offline_package(package_id)
        if not package:
            return {"error": "Package not found"}

        # Mock validation
        is_valid = True  # Would check actual checksum

        return {
            "package_id": str(package_id),
            "is_valid": is_valid,
            "file_count": 25,
            "total_size": "150MB",
            "validation_errors": [] if is_valid else ["Checksum mismatch"],
            "validated_at": "2024-01-01T00:00:00Z",
        }

    def get_offline_usage_statistics(self, user_id: UUID) -> Dict[str, Any]:
        """Get offline usage statistics."""
        user_cache = self.get_offline_content_list(user_id)

        return {
            "user_id": str(user_id),
            "cached_content_count": len(user_cache),
            "total_cache_size": "75MB",  # Sum of all cached content
            "offline_sessions": 12,  # Mock count
            "average_session_duration": 45,  # minutes
            "most_accessed_offline": [
                {"content_id": "content_1", "access_count": 15},
                {"content_id": "content_2", "access_count": 10},
            ],
            "last_sync": "2024-01-01T00:00:00Z",
        }

    def create_offline_notification(
        self,
        user_id: UUID,
        notification_type: str,
        message: str,
    ) -> Dict[str, Any]:
        """Create offline notification for sync."""
        notification_id = UUID(f"offline_notif_{len(self._sync_sessions)}")

        notification = {
            "id": str(notification_id),
            "user_id": str(user_id),
            "type": notification_type,
            "message": message,
            "priority": "normal",
            "is_read": False,
            "created_at": "2024-01-01T00:00:00Z",
        }

        return notification

    def get_offline_capabilities(self) -> Dict[str, Any]:
        """Get offline capabilities and features."""
        return {
            "supported_features": [
                "content_download",
                "progress_tracking",
                "note_taking",
                "bookmarking",
                "search",
                "quiz_practice",
            ],
            "storage_requirements": {
                "minimum": "200MB",
                "recommended": "1GB",
            },
            "supported_platforms": [
                "iOS",
                "Android",
                "Windows",
                "macOS",
                "Linux",
            ],
            "sync_methods": [
                "wifi_sync",
                "cellular_sync",
                "manual_sync",
            ],
            "content_types": [
                "lessons",
                "assessments",
                "videos",
                "documents",
                "interactive_content",
            ],
        }

    def estimate_offline_storage(
        self,
        content_ids: List[UUID],
        include_media: bool = True,
    ) -> Dict[str, Any]:
        """Estimate storage requirements for offline content."""
        # Mock size calculation
        base_size_per_content = 2048  # KB
        media_size_per_content = 5120  # KB

        total_base = len(content_ids) * base_size_per_content
        total_media = len(content_ids) * media_size_per_content if include_media else 0
        total_size = total_base + total_media

        return {
            "content_count": len(content_ids),
            "include_media": include_media,
            "estimated_size": f"{total_size / 1024:.1f} MB",
            "breakdown": {
                "content": f"{total_base / 1024:.1f} MB",
                "media": f"{total_media / 1024:.1f} MB" if include_media else "0 MB",
            },
            "compression_ratio": 0.7,  # Mock compression
        }

    def create_offline_backup(
        self,
        user_id: UUID,
        backup_type: str = "full",
    ) -> Dict[str, Any]:
        """Create offline backup of user data."""
        backup_id = UUID(f"backup_{user_id}")

        backup = {
            "id": str(backup_id),
            "user_id": str(user_id),
            "type": backup_type,
            "includes": (
                [
                    "progress_data",
                    "notes",
                    "bookmarks",
                    "settings",
                    "achievements",
                ]
                if backup_type == "full"
                else ["progress_data", "notes"]
            ),
            "estimated_size": "5MB",
            "created_at": "2024-01-01T00:00:00Z",
            "download_url": f"/api/backups/{backup_id}/download",
        }

        return backup

    def restore_from_backup(
        self,
        user_id: UUID,
        backup_id: UUID,
        restore_options: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Restore user data from backup."""
        backup = self._offline_packages.get(backup_id)  # Mock lookup

        if not backup:
            return {"error": "Backup not found"}

        return {
            "user_id": str(user_id),
            "backup_id": str(backup_id),
            "restored_items": [
                "Progress: 15 lessons completed",
                "Notes: 23 notes restored",
                "Bookmarks: 8 bookmarks restored",
                "Settings: Preferences restored",
            ],
            "restored_at": "2024-01-01T00:00:00Z",
        }
