# AI Agents Guide - Communication Module

## Overview

The communication module handles all forms of interaction between users, including forums, messaging, and collaborative work.

## Module Structure

```
communication/
├── communication.py # Forums and messaging
├── collaboration.py  # Group work and peer review
├── __init__.py     # Module exports
├── README.md       # Module documentation
└── AGENTS.md       # This file
```

## Development Guidelines

### When Working on Communication Features

1. **Implement proper moderation**:
```python
def moderate_content(self, content_id: UUID, moderator_id: UUID, action: str):
    if action == "delete":
        content.is_deleted = True
    elif action == "edit":
        content.content = "[Moderated content]"
    elif action == "approve":
        content.is_approved = True
```

2. **Handle real-time features** (when implementing WebSocket support):
```python
async def handle_forum_post(self, post_data: Dict[str, Any]):
    post = self.create_post(**post_data)
    # Broadcast to connected users
    await self.websocket_manager.broadcast({
        "type": "new_post",
        "post": self._post_to_dict(post),
    })
```

3. **Implement notification system**:
```python
def send_notification(self, user_id: UUID, notification_type: str, message: str):
    notification = {
        "user_id": str(user_id),
        "type": notification_type,
        "message": message,
        "is_read": False,
        "created_at": datetime.utcnow(),
    }
    self._notifications.append(notification)
```

### Forum Management

1. **Create structured forums**:
```python
def create_forum(self, course_id: UUID, title: str, description: str):
    forum = {
        "id": str(uuid4()),
        "course_id": str(course_id),
        "title": title,
        "description": description,
        "categories": ["General", "Questions", "Study Groups"],
        "is_active": True,
    }
    self._forums[forum["id"]] = forum
    return forum
```

2. **Implement post threading**:
```python
def create_reply(self, post_id: UUID, author_id: UUID, content: str):
    reply = {
        "id": str(uuid4()),
        "post_id": str(post_id),
        "author_id": str(author_id),
        "content": content,
        "created_at": datetime.utcnow(),
    }

    # Update post reply count
    post = self._posts[post_id]
    post["reply_count"] += 1

    return reply
```

### Collaboration Features

1. **Group management**:
```python
def create_study_group(self, course_id: UUID, organizer_id: UUID, title: str):
    group = {
        "id": str(uuid4()),
        "course_id": str(course_id),
        "organizer_id": str(organizer_id),
        "title": title,
        "members": [str(organizer_id)],
        "max_members": 8,
    }
    return group
```

2. **Peer review workflow**:
```python
def submit_for_review(self, assignment_id: UUID, user_id: UUID, submission: str):
    submission_data = {
        "id": str(uuid4()),
        "assignment_id": str(assignment_id),
        "user_id": str(user_id),
        "content": submission,
        "status": "pending_review",
        "reviews": [],
    }
    self._submissions.append(submission_data)
    return submission_data
```

### Testing Requirements

- **Test forum creation and management**
- **Test messaging functionality**
- **Test group collaboration**
- **Test peer review workflows**
- **Test moderation features**

Example test:
```python
def test_forum_post_creation():
    forum = comm_service.create_forum(course_id, "Test Forum", "Description")

    post = comm_service.create_post(
        forum_id=forum["id"],
        author_id=user_id,
        title="Test Post",
        content="Test content",
    )

    assert post["forum_id"] == forum["id"]
    assert post["title"] == "Test Post"
```

### Performance Considerations

- **Pagination** for large forums
- **Caching** for frequently accessed content
- **Background processing** for heavy operations
- **Database optimization** for messaging

### Common Patterns

#### Content Moderation
```python
def moderate_content(self, content_id: UUID, action: str, reason: str = ""):
    content = self._posts.get(content_id) or self._replies.get(content_id)
    if not content:
        return {"error": "Content not found"}

    moderation = {
        "content_id": str(content_id),
        "action": action,
        "reason": reason,
        "moderator_id": moderator_id,
        "timestamp": datetime.utcnow(),
    }

    if action == "delete":
        content["is_deleted"] = True
    # ... other actions

    return moderation
```

#### Notification System
```python
def create_notification(self, user_id: UUID, type: str, message: str):
    notification = {
        "id": str(uuid4()),
        "user_id": str(user_id),
        "type": type,
        "message": message,
        "is_read": False,
        "created_at": datetime.utcnow(),
    }
    return notification
```

### Extension Points

- Real-time WebSocket integration
- Advanced moderation AI
- Custom notification types
- Integration with external communication platforms
- Advanced collaboration tools

