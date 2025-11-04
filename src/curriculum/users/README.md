# Users Module

The users module handles user management, authentication, and authorization.

## Components

- `user.py`: User service for CRUD operations and user management

## Features

- User registration and profile management
- Role-based access control
- JWT authentication
- Password management
- Session tracking
- Permission system

## Usage

```python
from curriculum.users import UserService, AuthenticationService

# User management
user_service = UserService()
user, error = user_service.create_user(
    email="user@example.com",
    username="username",
    full_name="Full Name",
    password="secure_password"
)

if not user:
    raise ValueError(f"Failed to create user: {error}")

# Authentication
auth_service = AuthenticationService(user_service)
authenticated_user = auth_service.authenticate_user("username", "secure_password")
token = auth_service.create_access_token(user.id)
```

## Testing

```bash
pytest tests/integration/test_users_user_service.py
pytest tests/unit/test_users.py
```


