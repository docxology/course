"""User management and authentication services."""

import hashlib
import re
import secrets
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from uuid import UUID

import jwt

from curriculum.config import settings
from curriculum.core.user import ROLE_PERMISSIONS, User, UserPermission, UserRole

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
        salt = secrets.token_hex(16)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 260000)
        return f"hashed_pbkdf2_sha256$260000${salt}${digest.hex()}"

    def _verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify a salted password digest in constant time."""
        try:
            algorithm, iterations, salt, expected = hashed_password.split("$")
            if algorithm != "hashed_pbkdf2_sha256" or int(iterations) != 260000:
                return False
            actual = hashlib.pbkdf2_hmac(
                "sha256", password.encode(), bytes.fromhex(salt), int(iterations)
            ).hex()
            return secrets.compare_digest(actual, expected)
        except (ValueError, TypeError):
            return False

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
            custom_permissions=custom_permissions,
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
            True if password was changed successfully; False if the user is missing
            or the current password is incorrect
        """
        user = self.get_user(user_id)
        if not user:
            return False

        # Verify current password
        if not self.verify_password(user_id, current_password):
            return False

        if not self._validate_password_strength(new_password)[0]:
            return False
        user.hashed_password = self._hash_password(new_password)
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

        return self._verify_password(password, user.hashed_password)

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
        """Create a signed, expiring access token.

        Args:
            user_id: UUID of the user
            expires_delta: Optional token expiration time delta

        Returns:
            Access token string
        """
        expires = datetime.now(timezone.utc) + (
            expires_delta
            if expires_delta is not None
            else timedelta(minutes=settings.access_token_expire_minutes)
        )
        return jwt.encode(
            {"sub": str(user_id), "exp": expires, "token_type": "access"},
            settings.secret_key,
            algorithm=settings.algorithm,
        )

    def create_refresh_token(self, user_id: UUID) -> str:
        """Create a signed, expiring refresh token.

        Args:
            user_id: UUID of the user

        Returns:
            Refresh token string
        """
        return jwt.encode(
            {
                "sub": str(user_id),
                "exp": datetime.now(timezone.utc)
                + timedelta(days=settings.refresh_token_expire_days),
                "token_type": "refresh",
            },
            settings.secret_key,
            algorithm=settings.algorithm,
        )

    def verify_token(self, token: str) -> Optional[UUID]:
        """Verify an access token signature, expiry, and purpose.

        Args:
            token: Token string to verify

        Returns:
            User UUID if token is valid, None otherwise
        """
        return self._verify_token(token, "access")

    def verify_refresh_token(self, token: str) -> Optional[UUID]:
        """Verify a refresh token independently of access tokens."""
        return self._verify_token(token, "refresh")

    def _verify_token(self, token: str, expected_type: str) -> Optional[UUID]:
        """Require the signed token's expiry, subject, and intended purpose."""
        try:
            payload = jwt.decode(
                token,
                settings.secret_key,
                algorithms=[settings.algorithm],
                options={"require": ["exp", "sub", "token_type"]},
            )
            if payload["token_type"] != expected_type:
                return None
            return UUID(payload["sub"])
        except (jwt.InvalidTokenError, ValueError, KeyError):
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
