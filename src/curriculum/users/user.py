"""User management and authentication services."""

from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID

# from passlib.context import CryptContext  # Commented out for now
# from jose import JWTError, jwt  # Commented out for now

from curriculum.config import settings
from curriculum.core.user import User, UserRole, UserPermission, ROLE_PERMISSIONS


# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")  # Commented out for now


class UserService:
    """Service for managing users."""

    def __init__(self) -> None:
        """Initialize user service."""
        self._users: dict[UUID, User] = {}
        self._email_index: dict[str, UUID] = {}
        self._username_index: dict[str, UUID] = {}

    def create_user(
        self,
        email: str,
        username: str,
        full_name: str,
        password: str,
        roles: Optional[List[UserRole]] = None,
    ) -> Optional[User]:
        """Create a new user."""
        # Check if email or username already exists
        if email in self._email_index:
            return None
        if username in self._username_index:
            return None

        # Simple password hashing for now (in production, use proper hashing)
        hashed_password = f"hashed_{password}"
        user_roles = roles or [UserRole.STUDENT]

        # Calculate permissions from roles
        custom_permissions = self._calculate_permissions(user_roles)

        user = User(
            email=email,
            username=username,
            full_name=full_name,
            hashed_password=hashed_password,
            roles=user_roles,
            custom_permissions=custom_permissions,
        )

        self._users[user.id] = user
        self._email_index[email] = user.id
        self._username_index[username] = user.id

        return user

    def get_user(self, user_id: UUID) -> Optional[User]:
        """Get user by ID."""
        return self._users.get(user_id)

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        user_id = self._email_index.get(email)
        return self._users.get(user_id) if user_id else None

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        user_id = self._username_index.get(username)
        return self._users.get(user_id) if user_id else None

    def update_user(
        self,
        user_id: UUID,
        full_name: Optional[str] = None,
        bio: Optional[str] = None,
        avatar_url: Optional[str] = None,
    ) -> Optional[User]:
        """Update user profile."""
        user = self.get_user(user_id)
        if not user:
            return None

        if full_name is not None:
            user.full_name = full_name
        if bio is not None:
            user.bio = bio
        if avatar_url is not None:
            user.avatar_url = avatar_url

        user.update_timestamp()
        return user

    def change_password(self, user_id: UUID, current_password: str, new_password: str) -> bool:
        """Change user password with current password verification."""
        user = self.get_user(user_id)
        if not user:
            return False

        # Verify current password
        if not self.verify_password(user_id, current_password):
            return False

        # Update password
        user.hashed_password = f"hashed_{new_password}"
        user.update_timestamp()
        return True

    def verify_password(self, user_id: UUID, password: str) -> bool:
        """Verify user password."""
        user = self.get_user(user_id)
        if not user:
            return False

        return user.hashed_password == f"hashed_{password}"

    def add_role(self, user_id: UUID, role: UserRole) -> Optional[User]:
        """Add role to user."""
        user = self.get_user(user_id)
        if not user:
            return None

        if role not in user.roles:
            user.roles.append(role)
            user.custom_permissions = self._calculate_permissions(user.roles)
            user.update_timestamp()

        return user

    def remove_role(self, user_id: UUID, role: UserRole) -> Optional[User]:
        """Remove role from user."""
        user = self.get_user(user_id)
        if not user:
            return None

        if role in user.roles:
            user.roles.remove(role)
            user.custom_permissions = self._calculate_permissions(user.roles)
            user.update_timestamp()

        return user

    def deactivate_user(self, user_id: UUID) -> bool:
        """Deactivate user account."""
        user = self.get_user(user_id)
        if user:
            user.is_active = False
            user.update_timestamp()
            return True
        return False

    def activate_user(self, user_id: UUID) -> bool:
        """Activate user account."""
        user = self.get_user(user_id)
        if user:
            user.is_active = True
            user.update_timestamp()
            return True
        return False

    def record_login(self, user_id: UUID) -> Optional[User]:
        """Record user login."""
        user = self.get_user(user_id)
        if user:
            user.record_login()
            return user
        return None

    def list_users(self, role: Optional[UserRole] = None, active_only: bool = True) -> List[User]:
        """List users with optional filtering."""
        users = list(self._users.values())

        if active_only:
            users = [u for u in users if u.is_active]

        if role:
            users = [u for u in users if role in u.roles]

        return users

    def has_permission(self, user_id: UUID, permission: UserPermission) -> bool:
        """Check if user has specific permission."""
        user = self.get_user(user_id)
        if not user:
            return False

        return permission in user.custom_permissions

    def has_role(self, user_id: UUID, role: UserRole) -> bool:
        """Check if user has specific role."""
        user = self.get_user(user_id)
        if not user:
            return False

        return role in user.roles

    def _calculate_permissions(self, roles: List[UserRole]) -> List[UserPermission]:
        """Calculate permissions based on user roles."""
        permissions = set()

        for role in roles:
            role_permissions = ROLE_PERMISSIONS.get(role, [])
            permissions.update(role_permissions)

        return list(permissions)


class AuthenticationService:
    """Service for authentication and authorization."""

    def __init__(self, user_service: UserService) -> None:
        """Initialize authentication service."""
        self.user_service = user_service

    def authenticate_user(self, username_or_email: str, password: str) -> Optional[User]:
        """Authenticate user with username/email and password."""
        # Try username first
        user = self.user_service.get_user_by_username(username_or_email)

        # Try email if username not found
        if not user:
            user = self.user_service.get_user_by_email(username_or_email)

        if not user:
            return None

        if not user.is_active:
            return None

        # Simple password verification for now
        if not self.user_service.verify_password(user.id, password):
            return None

        return user

    def create_access_token(self, user_id: UUID, expires_delta: Optional[timedelta] = None) -> str:
        """Create simple access token (placeholder)."""
        # In production, use proper JWT
        return f"access_token_{user_id}_{datetime.utcnow().isoformat()}"

    def create_refresh_token(self, user_id: UUID) -> str:
        """Create simple refresh token (placeholder)."""
        # In production, use proper JWT
        return f"refresh_token_{user_id}_{datetime.utcnow().isoformat()}"

    def verify_token(self, token: str) -> Optional[UUID]:
        """Verify token and return user ID (placeholder)."""
        # In production, use proper JWT verification
        try:
            if token.startswith("access_token_"):
                user_id_str = token.split("_")[2]
                return UUID(user_id_str)
        except (IndexError, ValueError):
            pass
        return None

    def has_permission(self, user_id: UUID, permission: UserPermission) -> bool:
        """Check if user has a specific permission."""
        user = self.user_service.get_user(user_id)
        if not user:
            return False
        return user.has_permission(permission)

    def has_role(self, user_id: UUID, role: UserRole) -> bool:
        """Check if user has a specific role."""
        user = self.user_service.get_user(user_id)
        if not user:
            return False
        return user.has_role(role)
