# Module: core.user

**File:** `src/curriculum/core/user.py`

## Description

User and authentication models.

## Classes

### `UserRole`

User roles in the system.

**Inherits from:** str, Enum

**Methods:** 0

### `UserPermission`

System permissions.

**Inherits from:** str, Enum

**Methods:** 0

### `User`

User entity.

**Inherits from:** BaseEntity

**Methods:** 7


**Method List:**

- `get_permissions`: Get all permissions for this user.

- `has_permission`: Check if user has a specific permission.

- `has_role`: Check if user has a specific role.

- `add_role`: Add a role to the user.

- `remove_role`: Remove a role from the user.

- `record_login`: Record a user login.

- `update_activity`: Update last activity timestamp.

### `UserGroup`

User group for access control.

**Inherits from:** BaseEntity

**Methods:** 3


**Method List:**

- `add_member`: Add a member to the group.

- `remove_member`: Remove a member from the group.

- `has_member`: Check if user is a member.
