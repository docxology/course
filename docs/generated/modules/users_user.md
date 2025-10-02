# Module: users.user

**File:** `src/curriculum/users/user.py`

## Description

User management and authentication services.

## Classes

### `UserService`

Service for managing users.

**Methods:** 17


**Method List:**

- `__init__`: Initialize user service.

- `create_user`: Create a new user.

- `get_user`: Get user by ID.

- `get_user_by_email`: Get user by email.

- `get_user_by_username`: Get user by username.

- `update_user`: Update user profile.

- `change_password`: Change user password with current password verific

- `verify_password`: Verify user password.

- `add_role`: Add role to user.

- `remove_role`: Remove role from user.

- `deactivate_user`: Deactivate user account.

- `activate_user`: Activate user account.

- `record_login`: Record user login.

- `list_users`: List users with optional filtering.

- `has_permission`: Check if user has specific permission.

- `has_role`: Check if user has specific role.

- `_calculate_permissions`: Calculate permissions based on user roles.

### `AuthenticationService`

Service for authentication and authorization.

**Methods:** 7


**Method List:**

- `__init__`: Initialize authentication service.

- `authenticate_user`: Authenticate user with username/email and password

- `create_access_token`: Create simple access token (placeholder).

- `create_refresh_token`: Create simple refresh token (placeholder).

- `verify_token`: Verify token and return user ID (placeholder).

- `has_permission`: Check if user has a specific permission.

- `has_role`: Check if user has a specific role.
