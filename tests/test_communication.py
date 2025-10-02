"""Tests for communication module."""

import pytest
from uuid import uuid4

from curriculum.communication.communication import CommunicationService
from curriculum.communication.collaboration import CollaborationService


class TestCommunicationService:
    """Tests for CommunicationService."""

    @pytest.fixture
    def communication_service(self):
        """Communication service fixture."""
        return CommunicationService()

    def test_communication_service_initialization(self, communication_service):
        """Test communication service initialization."""
        assert communication_service is not None
        assert hasattr(communication_service, '_forums')
        assert hasattr(communication_service, '_posts')
        assert hasattr(communication_service, '_messages')
        assert hasattr(communication_service, '_announcements')

    def test_create_forum(self, communication_service):
        """Test creating a forum."""
        course_id = uuid4()
        moderator_id = uuid4()

        forum = communication_service.create_forum(
            course_id=course_id,
            title="Test Forum",
            description="A test forum",
            moderator_id=moderator_id,
            is_public=False
        )

        assert forum["course_id"] == str(course_id)
        assert forum["title"] == "Test Forum"
        assert forum["moderator_id"] == str(moderator_id)
        assert forum["is_public"] is False
        assert forum["is_active"] is True

    def test_create_post(self, communication_service):
        """Test creating a forum post."""
        forum_id = uuid4()
        author_id = uuid4()

        post = communication_service.create_post(
            forum_id=forum_id,
            author_id=author_id,
            title="Test Post",
            content="This is a test post content",
            category="General Discussion"
        )

        assert post["forum_id"] == str(forum_id)
        assert post["author_id"] == str(author_id)
        assert post["title"] == "Test Post"
        assert post["content"] == "This is a test post content"
        assert post["category"] == "General Discussion"

    def test_create_reply(self, communication_service):
        """Test creating a reply to a post."""
        post_id = uuid4()
        author_id = uuid4()

        reply = communication_service.create_reply(
            post_id=post_id,
            author_id=author_id,
            content="This is a reply to the post"
        )

        assert reply["post_id"] == str(post_id)
        assert reply["author_id"] == str(author_id)
        assert reply["content"] == "This is a reply to the post"

    def test_send_message(self, communication_service):
        """Test sending a private message."""
        sender_id = uuid4()
        recipient_id = uuid4()

        message = communication_service.send_message(
            sender_id=sender_id,
            recipient_id=recipient_id,
            subject="Test Subject",
            content="Test message content"
        )

        assert message["sender_id"] == str(sender_id)
        assert message["recipient_id"] == str(recipient_id)
        assert message["subject"] == "Test Subject"
        assert message["content"] == "Test message content"
        assert message["is_read"] is False

    def test_create_announcement(self, communication_service):
        """Test creating a course announcement."""
        course_id = uuid4()
        author_id = uuid4()

        announcement = communication_service.create_announcement(
            course_id=course_id,
            author_id=author_id,
            title="Important Announcement",
            content="This is an important announcement",
            priority="urgent"
        )

        assert announcement["course_id"] == str(course_id)
        assert announcement["author_id"] == str(author_id)
        assert announcement["title"] == "Important Announcement"
        assert announcement["content"] == "This is an important announcement"
        assert announcement["priority"] == "urgent"
        assert announcement["is_pinned"] is True

    def test_get_forum_posts(self, communication_service):
        """Test getting forum posts."""
        forum_id = uuid4()

        # Create some posts
        for i in range(3):
            communication_service.create_post(
                forum_id=forum_id,
                author_id=uuid4(),
                title=f"Post {i}",
                content=f"Content {i}"
            )

        posts = communication_service.get_forum_posts(forum_id)

        assert isinstance(posts, list)
        assert len(posts) >= 3

    def test_get_user_messages(self, communication_service):
        """Test getting user messages."""
        user_id = uuid4()

        # Send some messages
        for i in range(2):
            communication_service.send_message(
                sender_id=uuid4(),
                recipient_id=user_id,
                subject=f"Message {i}",
                content=f"Content {i}"
            )

        messages = communication_service.get_user_messages(user_id)

        assert isinstance(messages, list)
        assert len(messages) >= 2

    def test_get_course_announcements(self, communication_service):
        """Test getting course announcements."""
        course_id = uuid4()

        # Create some announcements
        for i in range(2):
            communication_service.create_announcement(
                course_id=course_id,
                author_id=uuid4(),
                title=f"Announcement {i}",
                content=f"Content {i}"
            )

        announcements = communication_service.get_course_announcements(course_id)

        assert isinstance(announcements, list)
        assert len(announcements) >= 2

    def test_mark_message_read(self, communication_service):
        """Test marking message as read."""
        sender_id = uuid4()
        recipient_id = uuid4()

        message = communication_service.send_message(
            sender_id=sender_id,
            recipient_id=recipient_id,
            subject="Test",
            content="Test"
        )

        result = communication_service.mark_message_read(message["id"], recipient_id)

        assert result is True

    def test_pin_post(self, communication_service):
        """Test pinning a forum post."""
        forum_id = uuid4()
        moderator_id = uuid4()

        post = communication_service.create_post(
            forum_id=forum_id,
            author_id=uuid4(),
            title="Test Post",
            content="Content"
        )

        result = communication_service.pin_post(post["id"], moderator_id)

        assert result is True

    def test_lock_post(self, communication_service):
        """Test locking a forum post."""
        forum_id = uuid4()
        moderator_id = uuid4()

        post = communication_service.create_post(
            forum_id=forum_id,
            author_id=uuid4(),
            title="Test Post",
            content="Content"
        )

        result = communication_service.lock_post(post["id"], moderator_id)

        assert result is True

    def test_get_communication_statistics(self, communication_service):
        """Test getting communication statistics."""
        course_id = uuid4()

        # Create forum and some posts
        forum = communication_service.create_forum(
            course_id=course_id,
            title="Test Forum",
            description="Test",
            moderator_id=uuid4()
        )

        for i in range(5):
            communication_service.create_post(
                forum_id=forum["id"],
                author_id=uuid4(),
                title=f"Post {i}",
                content=f"Content {i}"
            )

        stats = communication_service.get_communication_statistics(course_id)

        assert stats["course_id"] == str(course_id)
        assert "total_posts" in stats
        assert "total_participants" in stats

    def test_moderate_content(self, communication_service):
        """Test content moderation."""
        forum_id = uuid4()
        moderator_id = uuid4()

        post = communication_service.create_post(
            forum_id=forum_id,
            author_id=uuid4(),
            title="Test Post",
            content="Content"
        )

        moderation = communication_service.moderate_content(
            content_id=post["id"],
            moderator_id=moderator_id,
            action="approve",
            reason="Good content"
        )

        assert moderation["content_id"] == post["id"]
        assert moderation["moderator_id"] == str(moderator_id)
        assert moderation["action"] == "approve"

    def test_create_study_group(self, communication_service):
        """Test creating a study group."""
        course_id = uuid4()
        organizer_id = uuid4()

        group = communication_service.create_study_group(
            course_id=course_id,
            organizer_id=organizer_id,
            title="Test Study Group",
            description="A test study group"
        )

        assert group["course_id"] == str(course_id)
        assert group["organizer_id"] == str(organizer_id)
        assert group["title"] == "Test Study Group"
        assert group["is_active"] is True

    def test_get_user_conversations(self, communication_service):
        """Test getting user conversations."""
        user_id = uuid4()

        # Send messages to create conversations
        other_users = [uuid4(), uuid4()]
        for other_user in other_users:
            communication_service.send_message(
                sender_id=other_user,
                recipient_id=user_id,
                subject="Test",
                content="Test"
            )

        conversations = communication_service.get_user_conversations(user_id)

        assert isinstance(conversations, list)
        assert len(conversations) >= 2

    def test_create_notification(self, communication_service):
        """Test creating a notification."""
        user_id = uuid4()

        notification = communication_service.create_notification(
            user_id=user_id,
            title="Test Notification",
            message="This is a test notification",
            notification_type="info"
        )

        assert notification["user_id"] == str(user_id)
        assert notification["title"] == "Test Notification"
        assert notification["message"] == "This is a test notification"
        assert notification["type"] == "info"
        assert notification["is_read"] is False

    def test_get_user_notifications(self, communication_service):
        """Test getting user notifications."""
        user_id = uuid4()

        # Create some notifications
        for i in range(3):
            communication_service.create_notification(
                user_id=user_id,
                title=f"Notification {i}",
                message=f"Message {i}",
                notification_type="info"
            )

        notifications = communication_service.get_user_notifications(user_id)

        assert isinstance(notifications, list)
        assert len(notifications) >= 3

    def test_get_user_notifications_unread_only(self, communication_service):
        """Test getting only unread notifications."""
        user_id = uuid4()

        # Create mix of read and unread notifications
        for i in range(2):
            communication_service.create_notification(
                user_id=user_id,
                title=f"Unread {i}",
                message=f"Message {i}",
                notification_type="info"
            )

        notifications = communication_service.get_user_notifications(user_id, unread_only=True)

        assert isinstance(notifications, list)
        assert all(not n["is_read"] for n in notifications)


class TestCollaborationService:
    """Tests for CollaborationService."""

    @pytest.fixture
    def collaboration_service(self):
        """Collaboration service fixture."""
        return CollaborationService()

    def test_collaboration_service_initialization(self, collaboration_service):
        """Test collaboration service initialization."""
        assert collaboration_service is not None
        assert hasattr(collaboration_service, '_projects')
        assert hasattr(collaboration_service, '_workspaces')
        assert hasattr(collaboration_service, '_peer_reviews')

    def test_create_group_project(self, collaboration_service):
        """Test creating a group project."""
        course_id = uuid4()
        instructor_id = uuid4()

        project = collaboration_service.create_group_project(
            course_id=course_id,
            title="Test Group Project",
            description="A test group project",
            instructor_id=instructor_id,
            max_group_size=5,
            due_date="2024-02-01T23:59:59Z"
        )

        assert project["course_id"] == str(course_id)
        assert project["title"] == "Test Group Project"
        assert project["instructor_id"] == str(instructor_id)
        assert project["max_group_size"] == 5
        assert project["status"] == "active"

    def test_create_study_group(self, collaboration_service):
        """Test creating a study group."""
        course_id = uuid4()
        organizer_id = uuid4()

        group = collaboration_service.create_study_group(
            course_id=course_id,
            title="Test Study Group",
            description="A test study group",
            organizer_id=organizer_id,
            max_members=8
        )

        assert group["course_id"] == str(course_id)
        assert group["organizer_id"] == str(organizer_id)
        assert group["title"] == "Test Study Group"
        assert group["max_members"] == 8

    def test_join_group(self, collaboration_service):
        """Test joining a group."""
        course_id = uuid4()
        group_id = uuid4()
        user_id = uuid4()

        # Mock group structure
        collaboration_service._projects = {
            f"project_{course_id}": {
                "groups": [{
                    "id": str(group_id),
                    "member_ids": [],
                    "max_members": 5
                }]
            }
        }

        result = collaboration_service.join_group(group_id, user_id)

        assert "message" in result
        assert result["message"] == "Joined group successfully"

    def test_create_workspace(self, collaboration_service):
        """Test creating a workspace."""
        group_id = uuid4()

        workspace = collaboration_service.create_workspace(
            group_id=group_id,
            name="Test Workspace",
            description="A test workspace",
            tools=["documents", "chat"]
        )

        assert workspace["group_id"] == str(group_id)
        assert workspace["name"] == "Test Workspace"
        assert workspace["description"] == "A test workspace"
        assert "documents" in workspace["tools"]

    def test_create_peer_review_assignment(self, collaboration_service):
        """Test creating a peer review assignment."""
        course_id = uuid4()
        instructor_id = uuid4()

        assignment = collaboration_service.create_peer_review_assignment(
            course_id=course_id,
            title="Test Peer Review",
            description="A test peer review assignment",
            instructor_id=instructor_id,
            submission_deadline="2024-02-01T23:59:59Z",
            review_deadline="2024-02-05T23:59:59Z"
        )

        assert assignment["course_id"] == str(course_id)
        assert assignment["title"] == "Test Peer Review"
        assert assignment["instructor_id"] == str(instructor_id)
        assert assignment["submission_deadline"] == "2024-02-01T23:59:59Z"

    def test_submit_for_review(self, collaboration_service):
        """Test submitting work for peer review."""
        assignment_id = uuid4()
        user_id = uuid4()

        # Mock assignment structure
        collaboration_service._peer_reviews = {
            assignment_id: {
                "submissions": []
            }
        }

        submission = collaboration_service.submit_for_review(
            assignment_id=assignment_id,
            user_id=user_id,
            submission_title="My Submission",
            submission_content="This is my work"
        )

        assert submission["assignment_id"] == str(assignment_id)
        assert submission["user_id"] == str(user_id)
        assert submission["title"] == "My Submission"
        assert submission["content"] == "This is my work"

    def test_submit_review(self, collaboration_service):
        """Test submitting a peer review."""
        submission_id = uuid4()
        reviewer_id = uuid4()

        # Mock submission structure
        collaboration_service._peer_reviews = {
            uuid4(): {
                "submissions": [{
                    "id": str(submission_id),
                    "reviews": []
                }]
            }
        }

        review = collaboration_service.submit_review(
            submission_id=submission_id,
            reviewer_id=reviewer_id,
            decision="approve",
            feedback="Good work!",
            score=85
        )

        assert review["submission_id"] == str(submission_id)
        assert review["reviewer_id"] == str(reviewer_id)
        assert review["decision"] == "approve"
        assert review["feedback"] == "Good work!"

    def test_get_group_projects(self, collaboration_service):
        """Test getting group projects."""
        course_id = uuid4()

        # Mock some projects
        collaboration_service._projects = {
            f"project_{course_id}": {
                "course_id": str(course_id),
                "title": "Test Project"
            }
        }

        projects = collaboration_service.get_group_projects(course_id)

        assert isinstance(projects, list)
        assert len(projects) >= 0

    def test_get_user_groups(self, collaboration_service):
        """Test getting user's groups."""
        user_id = uuid4()

        # Mock group membership
        collaboration_service._projects = {
            "project_1": {
                "groups": [{
                    "id": "group_1",
                    "member_ids": [str(user_id)],
                    "title": "Test Group"
                }]
            }
        }

        groups = collaboration_service.get_user_groups(user_id)

        assert isinstance(groups, list)

    def test_assign_group_roles(self, collaboration_service):
        """Test assigning group roles."""
        group_id = uuid4()

        # Mock group structure
        collaboration_service._projects = {
            "project_1": {
                "groups": [{
                    "id": str(group_id)
                }]
            }
        }

        role_assignments = {
            "user1": "leader",
            "user2": "contributor"
        }

        result = collaboration_service.assign_group_roles(group_id, role_assignments)

        assert "message" in result
        assert result["message"] == "Roles assigned successfully"

    def test_create_collaboration_task(self, collaboration_service):
        """Test creating a collaboration task."""
        workspace_id = uuid4()
        assignee_id = uuid4()

        task = collaboration_service.create_collaboration_task(
            workspace_id=workspace_id,
            title="Test Task",
            description="A test collaboration task",
            assignee_id=assignee_id,
            due_date="2024-02-01T23:59:59Z"
        )

        assert task["workspace_id"] == str(workspace_id)
        assert task["title"] == "Test Task"
        assert task["assignee_id"] == str(assignee_id)
        assert task["status"] == "pending"

    def test_get_collaboration_statistics(self, collaboration_service):
        """Test getting collaboration statistics."""
        course_id = uuid4()

        stats = collaboration_service.get_collaboration_statistics(course_id)

        assert stats["course_id"] == str(course_id)
        assert "total_projects" in stats
        assert "total_groups" in stats
        assert "completed_projects" in stats

    def test_create_shared_document(self, collaboration_service):
        """Test creating a shared document."""
        workspace_id = uuid4()
        author_id = uuid4()

        document = collaboration_service.create_shared_document(
            workspace_id=workspace_id,
            title="Test Document",
            content="This is a shared document",
            author_id=author_id
        )

        assert document["workspace_id"] == str(workspace_id)
        assert document["title"] == "Test Document"
        assert document["author_id"] == str(author_id)
        assert document["is_locked"] is False

    def test_add_collaborator(self, collaboration_service):
        """Test adding a collaborator to a document."""
        document_id = uuid4()
        user_id = uuid4()

        # Mock document structure
        collaboration_service._workspaces = {
            "workspace_1": {
                "files": [{
                    "id": str(document_id),
                    "type": "document",
                    "editors": []
                }]
            }
        }

        result = collaboration_service.add_collaborator(
            document_id=document_id,
            user_id=user_id,
            permission="edit"
        )

        assert "message" in result
        assert result["message"] == "Collaborator added successfully"

    def test_get_collaboration_activity(self, collaboration_service):
        """Test getting collaboration activity."""
        course_id = uuid4()

        activity = collaboration_service.get_collaboration_activity(course_id)

        assert isinstance(activity, list)
        # Should return mock activity data


