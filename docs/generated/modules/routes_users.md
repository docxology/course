# Module: routes.users

**File:** `src/curriculum/routes/users.py`

## Description

User API routes.

## Classes

### `CreateUserRequest`

Request model for creating user.

**Inherits from:** BaseModel

**Methods:** 0

### `UpdateUserRequest`

Request model for updating user.

**Inherits from:** BaseModel

**Methods:** 0

### `LoginRequest`

Request model for user login.

**Inherits from:** BaseModel

**Methods:** 0

### `TokenResponse`

Response model for authentication tokens.

**Inherits from:** BaseModel

**Methods:** 0

### `UserResponse`

Response model for user.

**Inherits from:** BaseModel

**Methods:** 0

## Functions

### `login`

Authenticate user and return tokens.

**Parameters:**

- `request: LoginRequest`

### `refresh_token`

Refresh access token using refresh token.

**Parameters:**

- `refresh_token: str`

### `create_user`

Create a new user.

**Parameters:**

- `request: CreateUserRequest`

### `get_current_user`

Get current user profile.

**Parameters:**

- `current_user: User`

### `get_user`

Get user by ID.

**Parameters:**

- `user_id: UUID`

### `update_user`

Update user profile.

**Parameters:**

- `user_id: UUID`

- `request: UpdateUserRequest`

- `current_user: User`

### `change_password`

Change user password.

**Parameters:**

- `user_id: UUID`

- `current_password: str`

- `new_password: str`

- `current_user: User`

### `activate_user`

Activate user account.

**Parameters:**

- `user_id: UUID`

- `current_user: User`

### `deactivate_user`

Deactivate user account.

**Parameters:**

- `user_id: UUID`

- `current_user: User`

### `list_users`

List users with optional filtering.

**Parameters:**

- `role: Optional[UserRole]`

- `active_only: bool`

- `current_user: User`

### `add_user_role`

Add role to user.

**Parameters:**

- `user_id: UUID`

- `role: UserRole`

- `current_user: User`

### `remove_user_role`

Remove role from user.

**Parameters:**

- `user_id: UUID`

- `role: UserRole`

- `current_user: User`

### `_user_to_response`

Convert User model to response model.

**Parameters:**

- `user: User`
