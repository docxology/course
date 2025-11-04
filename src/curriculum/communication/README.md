# Communication Module

The communication module handles all forms of interaction between users, including forums, messaging, and announcements.

## Services

- `CommunicationService`: Forums, messaging, and announcements
- `CollaborationService`: Group work and peer review

## Features

- Discussion forums with categories
- Private messaging system
- Course announcements
- Study group coordination
- Peer review workflows
- Real-time collaboration

## Usage

```python
from curriculum.communication import CommunicationService

comm_service = CommunicationService()

# Create forum
forum = comm_service.create_forum(
    course_id=course_id,
    title="General Discussion",
    description="Course discussion forum",
    moderator_id=instructor_id,
)

# Send message
message = comm_service.send_message(
    sender_id=user_id,
    recipient_id=other_user_id,
    subject="Question about homework",
    content="I need help with...",
)
```

## Testing

```bash
pytest tests/integration/test_communication.py
```

