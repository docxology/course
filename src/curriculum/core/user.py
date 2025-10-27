"""User and authentication models."""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from uuid import UUID

from pydantic import Field
from typing import Optional

from curriculum.core.base import BaseEntity


class UserRole(str, Enum):
    """User roles in the system."""

    STUDENT = "student"
    INSTRUCTOR = "instructor"
    CONTENT_CREATOR = "content_creator"
    REVIEWER = "reviewer"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class UserPermission(str, Enum):
    """System permissions."""

    # Content permissions
    CONTENT_CREATE = "content:create"
    CONTENT_READ = "content:read"
    CONTENT_UPDATE = "content:update"
    CONTENT_DELETE = "content:delete"
    CONTENT_PUBLISH = "content:publish"

    # User management
    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"

    # Assessment permissions
    ASSESSMENT_CREATE = "assessment:create"
    ASSESSMENT_GRADE = "assessment:grade"

    # Analytics
    ANALYTICS_VIEW = "analytics:view"
    ANALYTICS_EXPORT = "analytics:export"

    # System administration
    SYSTEM_CONFIG = "system:config"
    SYSTEM_AUDIT = "system:audit"


# Role to permissions mapping
ROLE_PERMISSIONS: Dict[UserRole, List[UserPermission]] = {
    UserRole.STUDENT: [
        UserPermission.CONTENT_READ,
    ],
    UserRole.INSTRUCTOR: [
        UserPermission.CONTENT_READ,
        UserPermission.CONTENT_CREATE,
        UserPermission.CONTENT_UPDATE,
        UserPermission.ASSESSMENT_CREATE,
        UserPermission.ASSESSMENT_GRADE,
        UserPermission.ANALYTICS_VIEW,
    ],
    UserRole.CONTENT_CREATOR: [
        UserPermission.CONTENT_CREATE,
        UserPermission.CONTENT_READ,
        UserPermission.CONTENT_UPDATE,
    ],
    UserRole.REVIEWER: [
        UserPermission.CONTENT_READ,
        UserPermission.CONTENT_UPDATE,
        UserPermission.CONTENT_PUBLISH,
    ],
    UserRole.ADMIN: [p for p in UserPermission if p != UserPermission.SYSTEM_CONFIG],
    UserRole.SUPER_ADMIN: [p for p in UserPermission],
}


class User(BaseEntity):
    """User entity."""

    # Basic information
    email: str
    username: str = Field(min_length=3, max_length=50)
    full_name: str = Field(min_length=1, max_length=200)

    # Authentication
    hashed_password: str
    is_active: bool = True
    is_verified: bool = False
    email_verified_at: Optional[datetime] = None

    # Roles and permissions
    roles: List[UserRole] = Field(default_factory=lambda: [UserRole.STUDENT])
    custom_permissions: List[UserPermission] = Field(default_factory=list)

    # Profile
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    timezone: str = "UTC"
    language: str = "en"

    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)

    # Activity tracking
    last_login_at: Optional[datetime] = None
    last_activity_at: Optional[datetime] = None
    login_count: int = 0

    def get_permissions(self) -> List[UserPermission]:
        """Get all permissions for this user."""
        permissions = set(self.custom_permissions)
        for role in self.roles:
            permissions.update(ROLE_PERMISSIONS.get(role, []))
        return list(permissions)

    def has_permission(self, permission: UserPermission) -> bool:
        """Check if user has a specific permission."""
        return permission in self.get_permissions()

    def has_role(self, role: UserRole) -> bool:
        """Check if user has a specific role."""
        return role in self.roles

    def add_role(self, role: UserRole) -> None:
        """Add a role to the user."""
        if role not in self.roles:
            self.roles.append(role)
            self.update_timestamp()

    def remove_role(self, role: UserRole) -> None:
        """Remove a role from the user."""
        if role in self.roles:
            self.roles.remove(role)
            self.update_timestamp()

    def record_login(self) -> None:
        """Record a user login."""
        self.last_login_at = datetime.now(timezone.utc)
        self.last_activity_at = datetime.now(timezone.utc)
        self.login_count += 1

    def update_activity(self) -> None:
        """Update last activity timestamp."""
        self.last_activity_at = datetime.now(timezone.utc)


class UserGroup(BaseEntity):
    """User group for access control."""

    name: str = Field(min_length=1, max_length=100)
    description: Optional[str] = None
    owner_id: UUID
    members: List[UUID] = Field(default_factory=list)
    permissions: List[UserPermission] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def add_member(self, user_id: UUID) -> None:
        """Add a member to the group."""
        if user_id not in self.members:
            self.members.append(user_id)
            self.update_timestamp()

    def remove_member(self, user_id: UUID) -> None:
        """Remove a member from the group."""
        if user_id in self.members:
            self.members.remove(user_id)
            self.update_timestamp()

    def has_member(self, user_id: UUID) -> bool:
        """Check if user is a member."""
        return user_id in self.members
