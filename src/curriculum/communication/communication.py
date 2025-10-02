"""Communication service for forums, messaging, and announcements."""

from typing import Dict, List, Optional, Any
from uuid import UUID
from datetime import datetime

from curriculum.core.user import User


class CommunicationService:
    """Service for communication features."""

    def __init__(self) -> None:
        """Initialize communication service."""
        self._forums: dict[UUID, dict] = {}
        self._posts: dict[UUID, dict] = {}
        self._messages: dict[UUID, dict] = {}
        self._announcements: dict[UUID, dict] = {}

    def create_forum(
        self,
        course_id: UUID,
        title: str,
        description: str,
        moderator_id: UUID,
        is_public: bool = False,
    ) -> Dict[str, Any]:
        """Create a discussion forum."""
        forum_id = UUID(f"forum_{course_id}")

        forum = {
            "id": str(forum_id),
            "course_id": str(course_id),
            "title": title,
            "description": description,
            "moderator_id": str(moderator_id),
            "is_public": is_public,
            "is_active": True,
            "total_posts": 0,
            "total_participants": 0,
            "categories": [
                {"name": "General Discussion", "description": "General course discussions"},
                {"name": "Questions", "description": "Ask questions about course content"},
                {"name": "Study Groups", "description": "Form study groups"},
            ],
            "rules": [
                "Be respectful to other students",
                "Stay on topic",
                "No spam or promotional content",
            ],
            "created_at": "2024-01-01T00:00:00Z",
        }

        self._forums[forum_id] = forum
        return forum

    def create_post(
        self,
        forum_id: UUID,
        author_id: UUID,
        title: str,
        content: str,
        category: str = "General Discussion",
        tags: List[str] = None,
    ) -> Dict[str, Any]:
        """Create a forum post."""
        post_id = UUID(f"post_{len(self._posts)}")

        post = {
            "id": str(post_id),
            "forum_id": str(forum_id),
            "author_id": str(author_id),
            "title": title,
            "content": content,
            "category": category,
            "tags": tags or [],
            "is_pinned": False,
            "is_locked": False,
            "reply_count": 0,
            "view_count": 0,
            "like_count": 0,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
        }

        self._posts[post_id] = post

        # Update forum statistics
        forum = self._forums.get(forum_id)
        if forum:
            forum["total_posts"] += 1

        return post

    def create_reply(
        self,
        post_id: UUID,
        author_id: UUID,
        content: str,
    ) -> Dict[str, Any]:
        """Create a reply to a forum post."""
        reply_id = UUID(f"reply_{len(self._posts)}")

        reply = {
            "id": str(reply_id),
            "post_id": str(post_id),
            "author_id": str(author_id),
            "content": content,
            "is_solution": False,
            "like_count": 0,
            "created_at": "2024-01-01T00:00:00Z",
        }

        # Update post reply count
        post = self._posts.get(post_id)
        if post:
            post["reply_count"] += 1

        return reply

    def send_message(
        self,
        sender_id: UUID,
        recipient_id: UUID,
        subject: str,
        content: str,
    ) -> Dict[str, Any]:
        """Send a private message."""
        message_id = UUID(f"msg_{len(self._messages)}")

        message = {
            "id": str(message_id),
            "sender_id": str(sender_id),
            "recipient_id": str(recipient_id),
            "subject": subject,
            "content": content,
            "is_read": False,
            "is_archived": False,
            "created_at": "2024-01-01T00:00:00Z",
        }

        self._messages[message_id] = message
        return message

    def create_announcement(
        self,
        course_id: UUID,
        author_id: UUID,
        title: str,
        content: str,
        priority: str = "normal",
        expires_at: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a course announcement."""
        announcement_id = UUID(f"ann_{len(self._announcements)}")

        announcement = {
            "id": str(announcement_id),
            "course_id": str(course_id),
            "author_id": str(author_id),
            "title": title,
            "content": content,
            "priority": priority,  # normal, important, urgent
            "is_pinned": priority == "urgent",
            "expires_at": expires_at,
            "created_at": "2024-01-01T00:00:00Z",
        }

        self._announcements[announcement_id] = announcement
        return announcement

    def get_forum_posts(
        self,
        forum_id: UUID,
        category: Optional[str] = None,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Get posts from a forum."""
        posts = [
            post for post in self._posts.values()
            if post["forum_id"] == str(forum_id)
        ]

        if category:
            posts = [post for post in posts if post["category"] == category]

        # Sort by pinned status and creation time
        posts.sort(key=lambda p: (not p["is_pinned"], p["created_at"]), reverse=True)

        return posts[:limit]

    def get_user_messages(
        self,
        user_id: UUID,
        unread_only: bool = False,
    ) -> List[Dict[str, Any]]:
        """Get messages for a user."""
        messages = [
            msg for msg in self._messages.values()
            if msg["recipient_id"] == str(user_id)
        ]

        if unread_only:
            messages = [msg for msg in messages if not msg["is_read"]]

        return sorted(messages, key=lambda m: m["created_at"], reverse=True)

    def get_course_announcements(self, course_id: UUID) -> List[Dict[str, Any]]:
        """Get announcements for a course."""
        announcements = [
            ann for ann in self._announcements.values()
            if ann["course_id"] == str(course_id)
        ]

        # Filter out expired announcements
        current_time = "2024-01-01T00:00:00Z"  # Mock current time
        announcements = [
            ann for ann in announcements
            if not ann["expires_at"] or ann["expires_at"] > current_time
        ]

        return sorted(announcements, key=lambda a: (a["is_pinned"], a["created_at"]), reverse=True)

    def mark_message_read(self, message_id: UUID, user_id: UUID) -> bool:
        """Mark message as read."""
        message = self._messages.get(message_id)
        if message and message["recipient_id"] == str(user_id):
            message["is_read"] = True
            return True
        return False

    def pin_post(self, post_id: UUID, moderator_id: UUID) -> bool:
        """Pin a forum post."""
        post = self._posts.get(post_id)
        if post:
            post["is_pinned"] = True
            return True
        return False

    def lock_post(self, post_id: UUID, moderator_id: UUID) -> bool:
        """Lock a forum post."""
        post = self._posts.get(post_id)
        if post:
            post["is_locked"] = True
            return True
        return False

    def get_communication_statistics(self, course_id: UUID) -> Dict[str, Any]:
        """Get communication statistics for a course."""
        forum = next(
            (f for f in self._forums.values() if f["course_id"] == str(course_id)),
            None
        )

        if not forum:
            return {"error": "Forum not found"}

        forum_posts = [
            p for p in self._posts.values()
            if p["forum_id"] == forum["id"]
        ]

        return {
            "course_id": str(course_id),
            "forum_title": forum["title"],
            "total_posts": len(forum_posts),
            "total_replies": sum(p["reply_count"] for p in forum_posts),
            "total_participants": forum["total_participants"],
            "active_posts_last_week": len([
                p for p in forum_posts
                if p["created_at"] > "2023-12-25T00:00:00Z"  # Mock last week
            ]),
            "popular_categories": [
                {"name": "Questions", "post_count": 15},
                {"name": "General Discussion", "post_count": 8},
            ],
        }

    def moderate_content(
        self,
        content_id: UUID,
        moderator_id: UUID,
        action: str,  # approve, reject, edit, delete
        reason: str = "",
    ) -> Dict[str, Any]:
        """Moderate forum content."""
        # Find content (could be post or reply)
        post = self._posts.get(content_id)

        if not post:
            return {"error": "Content not found"}

        moderation = {
            "content_id": str(content_id),
            "moderator_id": str(moderator_id),
            "action": action,
            "reason": reason,
            "timestamp": "2024-01-01T00:00:00Z",
        }

        # Apply moderation action
        if action == "delete":
            post["is_deleted"] = True
        elif action == "edit":
            post["content"] = "[Moderated content]"
        elif action == "approve":
            post["is_approved"] = True
        elif action == "reject":
            post["is_rejected"] = True

        return moderation

    def create_study_group(
        self,
        course_id: UUID,
        organizer_id: UUID,
        title: str,
        description: str,
        max_members: int = 10,
    ) -> Dict[str, Any]:
        """Create a study group."""
        group_id = UUID(f"group_{course_id}")

        study_group = {
            "id": str(group_id),
            "course_id": str(course_id),
            "organizer_id": str(organizer_id),
            "title": title,
            "description": description,
            "max_members": max_members,
            "current_members": 1,
            "member_ids": [str(organizer_id)],
            "is_active": True,
            "meeting_schedule": "Weekly on Tuesdays",
            "communication_channel": "Discord",
            "created_at": "2024-01-01T00:00:00Z",
        }

        return study_group

    def get_user_conversations(self, user_id: UUID) -> List[Dict[str, Any]]:
        """Get user's message conversations."""
        user_messages = [
            msg for msg in self._messages.values()
            if msg["sender_id"] == str(user_id) or msg["recipient_id"] == str(user_id)
        ]

        # Group by conversation partner
        conversations = {}
        for message in user_messages:
            other_user = (
                message["recipient_id"] if message["sender_id"] == str(user_id)
                else message["sender_id"]
            )

            if other_user not in conversations:
                conversations[other_user] = {
                    "user_id": other_user,
                    "last_message": message,
                    "unread_count": 0 if message["is_read"] else 1,
                    "total_messages": 1,
                }
            else:
                conversations[other_user]["total_messages"] += 1
                if not message["is_read"]:
                    conversations[other_user]["unread_count"] += 1

        return list(conversations.values())

    def create_notification(
        self,
        user_id: UUID,
        title: str,
        message: str,
        notification_type: str = "info",
        action_url: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a notification for a user."""
        notification_id = UUID(f"notif_{len(self._messages)}")

        notification = {
            "id": str(notification_id),
            "user_id": str(user_id),
            "title": title,
            "message": message,
            "type": notification_type,  # info, warning, error, success
            "is_read": False,
            "action_url": action_url,
            "created_at": "2024-01-01T00:00:00Z",
        }

        return notification

    def get_user_notifications(
        self,
        user_id: UUID,
        unread_only: bool = False,
    ) -> List[Dict[str, Any]]:
        """Get notifications for a user."""
        # In production, this would query a notifications table
        notifications = [
            {
                "id": f"notif_{i}",
                "title": f"Notification {i+1}",
                "message": f"This is notification message {i+1}",
                "type": "info",
                "is_read": False,
                "created_at": "2024-01-01T00:00:00Z",
            }
            for i in range(5)  # Mock data
        ]

        if unread_only:
            notifications = [n for n in notifications if not n["is_read"]]

        return notifications
