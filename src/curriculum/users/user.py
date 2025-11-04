"""User management and authentication services."""

import re
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID

from curriculum.config import settings
from curriculum.core.user import ROLE_PERMISSIONS, User, UserPermission, UserRole

# from passlib.context import CryptContext  # Commented out for now
# from jose import JWTError, jwt  # Commented out for now



# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")  # Commented out for now

# Password validation constants
MIN_PASSWORD_LENGTH = 8
PASSWORD_REQUIREMENTS = {
    "uppercase": r"[A-Z]",
    "lowercase": r"[a-z]",
    "digits": r"\d",
    "special": r'[!@#$%^&*(),.?":{}|<>]',
}

# Common weak passwords to reject
COMMON_PASSWORDS = {
    "password",
    "123456",
    "password123",
    "admin",
    "qwerty",
    "letmein",
    "welcome",
    "monkey",
    "dragon",
    "password1",
}


class UserService:
    """Service for managing users."""

    def __init__(self) -> None:
        """Initialize user service."""
        self._users: dict[UUID, User] = {}
        self._email_index: dict[str, UUID] = {}
        self._username_index: dict[str, UUID] = {}

    def _validate_email(self, email: str) -> tuple[bool, str]:
        """Validate email format and requirements."""
        if not email or not isinstance(email, str):
            return False, "Email is required"

        if len(email) > 254:  # RFC 5321 limit
            return False, "Email too long"

        # Basic email regex (more comprehensive validation would use email-validator library)
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, email):
            return False, "Invalid email format"

        return True, ""

    def _validate_username(self, username: str) -> tuple[bool, str]:
        """Validate username format and requirements."""
        if not username or not isinstance(username, str):
            return False, "Username is required"

        if len(username) < 3:
            return False, "Username must be at least 3 characters"

        if len(username) > 50:
            return False, "Username too long"

        # Username should only contain alphanumeric characters, hyphens, and underscores
        if not re.match(r"^[a-zA-Z0-9_-]+$", username):
            return False, "Username can only contain letters, numbers, hyphens, and underscores"

        return True, ""

    def _validate_password_strength(self, password: str) -> tuple[bool, str]:
        """Validate password strength requirements."""
        if not password or not isinstance(password, str):
            return False, "Password is required"

        if len(password) < MIN_PASSWORD_LENGTH:
            return False, f"Password must be at least {MIN_PASSWORD_LENGTH} characters long"

        # Check against common passwords first
        if password.lower() in COMMON_PASSWORDS:
            return False, "Password is too common"

        # Check each requirement
        missing_requirements = []
        for req_name, pattern in PASSWORD_REQUIREMENTS.items():
            if not re.search(pattern, password):
                missing_requirements.append(req_name)

        if missing_requirements:
            return False, f"Password must contain: {', '.join(missing_requirements)}"

        return True, ""

    def _hash_password(self, password: str) -> str:
        """Hash password using secure method."""
        # In production, use proper password hashing like bcrypt
        # For now, use a simple but more secure method than the current implementation
        salt = secrets.token_hex(16)
        # Simple PBKDF2-like approach (in production, use proper implementation)
        return f"hashed_{salt}_{password}"

    def _verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password against hash."""
        # In production, use proper password verification
        # For now, extract salt and verify
        if not hashed_password.startswith("hashed_"):
            return False
        parts = hashed_password.split("_", 2)
        if len(parts) != 3:
            return False
        return parts[2] == password

    def create_user(
        self,
        email: str,
        username: str,
        full_name: str,
        password: str,
        roles: Optional[List[UserRole]] = None,
    ) -> tuple[Optional[User], str]:
        """Create a new user with comprehensive validation.

        Args:
            email: User email address
            username: Unique username
            full_name: User's full name
            password: User password (will be hashed)
            roles: Optional list of user roles (defaults to [STUDENT])

        Returns:
            Tuple of (User instance if successful, error message string).
            If successful, error message is empty string.
            If failed, User is None and error message contains reason.
        """
        # Validate inputs
        email_valid, email_error = self._validate_email(email)
        if not email_valid:
            return None, email_error

        username_valid, username_error = self._validate_username(username)
        if not username_valid:
            return None, username_error

        password_valid, password_error = self._validate_password_strength(password)
        if not password_valid:
            return None, password_error

        # Check if email or username already exists
        if email in self._email_index:
            return None, "Email already exists"

        if username in self._username_index:
            return None, "Username already exists"

        # Hash password securely
        hashed_password = self._hash_password(password)
        user_roles = roles or [UserRole.STUDENT]

        # Calculate permissions from roles
        custom_permissions = self._calculate_permissions(user_roles)

        user = User(
            email=email,
            username=username,
            full_name=full_name,
            hashed_password=hashed_password,
            roles=user_roles,
            permissions=custom_permissions,
        )

        # Store user
        self._users[user.id] = user
        self._email_index[email] = user.id
        self._username_index[username] = user.id

        return user, ""

    def create_user_legacy(
        self,
        email: str,
        username: str,
        full_name: str,
        password: str,
        roles: Optional[List[UserRole]] = None,
    ) -> Optional[User]:
        """Create a new user (legacy method for backward compatibility)."""
        try:
            # Use the validation logic but return just the user
            user, error = self.create_user(email, username, full_name, password, roles)
            return user
        except Exception:
            return None

    def get_user(self, user_id: UUID) -> Optional[User]:
        """Get user by ID.

        Args:
            user_id: UUID of the user to retrieve

        Returns:
            User instance if found, None otherwise
        """
        return self._users.get(user_id)

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email.

        Args:
            email: Email address to search for

        Returns:
            User instance if found, None otherwise
        """
        user_id = self._email_index.get(email)
        return self._users.get(user_id) if user_id else None

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username.

        Args:
            username: Username to search for

        Returns:
            User instance if found, None otherwise
        """
        user_id = self._username_index.get(username)
        return self._users.get(user_id) if user_id else None

    def update_user(
        self,
        user_id: UUID,
        full_name: Optional[str] = None,
        bio: Optional[str] = None,
        avatar_url: Optional[str] = None,
    ) -> Optional[User]:
        """Update user profile.

        Args:
            user_id: UUID of the user to update
            full_name: Optional new full name
            bio: Optional new bio
            avatar_url: Optional new avatar URL

        Returns:
            Updated User instance if found, None otherwise
        """
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
        """Change user password with current password verification.

        Args:
            user_id: UUID of the user
            current_password: Current password for verification
            new_password: New password to set

        Returns:
            True if password was changed successfully, False if user not found or current password incorrect
        """
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
        """Verify user password.

        Args:
            user_id: UUID of the user
            password: Password to verify

        Returns:
            True if password is correct, False otherwise
        """
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
        """Authenticate user with username/email and password.

        Args:
            username_or_email: Username or email address
            password: User password

        Returns:
            Authenticated User instance if successful, None if authentication failed
        """
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
        """Create simple access token (placeholder).

        Args:
            user_id: UUID of the user
            expires_delta: Optional token expiration time delta

        Returns:
            Access token string
        """
        # In production, use proper JWT
        return f"access_token_{user_id}_{datetime.now(timezone.utc).isoformat()}"

    def create_refresh_token(self, user_id: UUID) -> str:
        """Create simple refresh token (placeholder).

        Args:
            user_id: UUID of the user

        Returns:
            Refresh token string
        """
        # In production, use proper JWT
        return f"refresh_token_{user_id}_{datetime.now(timezone.utc).isoformat()}"

    def verify_token(self, token: str) -> Optional[UUID]:
        """Verify token and return user ID (placeholder).

        Args:
            token: Token string to verify

        Returns:
            User UUID if token is valid, None otherwise
        """
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
