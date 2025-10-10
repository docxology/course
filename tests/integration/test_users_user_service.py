"""Tests for User and Authentication Services."""

import pytest
from uuid import uuid4

from curriculum.core.user import UserRole, UserPermission


@pytest.mark.integration
class TestUserService:
    """Tests for UserService."""

    def test_create_user(self, user_service):
        """Test creating a user."""
        user = user_service.create_user_legacy(
            email="new@example.com",
            username="newuser",
            full_name="New User",
            password="StrongPassword123!",
        )

        assert user is not None
        assert user.email == "new@example.com"
        assert user.username == "newuser"
        assert user.is_active is True
        assert UserRole.STUDENT in user.roles

    def test_duplicate_email(self, user_service):
        """Test creating user with duplicate email."""
        # Create first user
        first_user = user_service.create_user_legacy(
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            password="StrongPassword123!",
        )
        assert first_user is not None
        
        # Try to create duplicate with same email
        duplicate = user_service.create_user_legacy(
            email="test@example.com",
            username="different",
            full_name="Different User",
            password="password",
        )

        assert duplicate is None

    def test_duplicate_username(self, user_service):
        """Test creating user with duplicate username."""
        # Create first user
        first_user = user_service.create_user_legacy(
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            password="StrongPassword123!",
        )
        assert first_user is not None
        
        # Try to create duplicate with same username
        duplicate = user_service.create_user_legacy(
            email="different@example.com",
            username="testuser",
            full_name="Different User",
            password="password",
        )

        assert duplicate is None

    def test_get_user_by_email(self, user_service):
        """Test retrieving user by email."""
        # Create a user first
        created_user = user_service.create_user_legacy(
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            password="StrongPassword123!",
        )
        assert created_user is not None
        
        # Retrieve by email
        retrieved = user_service.get_user_by_email("test@example.com")

        assert retrieved is not None
        assert retrieved.id == created_user.id
        assert retrieved.email == "test@example.com"

    def test_get_user_by_username(self, user_service):
        """Test retrieving user by username."""
        # Create a user first
        created_user = user_service.create_user_legacy(
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            password="StrongPassword123!",
        )
        assert created_user is not None
        
        # Retrieve by username
        retrieved = user_service.get_user_by_username("testuser")

        assert retrieved is not None
        assert retrieved.id == created_user.id
        assert retrieved.username == "testuser"

    def test_update_user(self, user_service):
        """Test updating user profile."""
        # Create a user first
        user = user_service.create_user_legacy(
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            password="StrongPassword123!",
        )
        assert user is not None
        
        # Update the user
        updated = user_service.update_user(
            user.id,
            full_name="Updated Name",
            bio="New bio",
        )

        assert updated is not None
        assert updated.full_name == "Updated Name"
        assert updated.bio == "New bio"

    def test_change_password(self, user_service):
        """Test changing user password."""
        # Create a user first
        user = user_service.create_user_legacy(
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            password="StrongPassword123!",
        )
        assert user is not None
        
        # Change password
        result = user_service.change_password(user.id, "StrongPassword123!", "newStrongPassword123!")

        assert result is True

    def test_verify_password(self, user_service):
        """Test verifying user password."""
        # Create a user with known password
        user = user_service.create_user_legacy(
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            password="StrongPassword123!",
        )
        assert user is not None
        
        # Verify correct and incorrect passwords
        assert user_service.verify_password(user.id, "StrongPassword123!") is True
        assert user_service.verify_password(user.id, "wrongpassword") is False

    def test_add_remove_role(self, user_service):
        """Test adding and removing user roles."""
        # Create a user first
        user = user_service.create_user_legacy(
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            password="StrongPassword123!",
        )
        assert user is not None
        
        # Add instructor role
        updated = user_service.add_role(user.id, UserRole.INSTRUCTOR)
        assert UserRole.INSTRUCTOR in updated.roles

        # Remove instructor role
        updated = user_service.remove_role(user.id, UserRole.INSTRUCTOR)
        assert UserRole.INSTRUCTOR not in updated.roles

    def test_deactivate_user(self, user_service):
        """Test deactivating user account."""
        # Create a user first
        user = user_service.create_user_legacy(
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            password="StrongPassword123!",
        )
        assert user is not None
        assert user.is_active is True
        
        # Deactivate the user
        result = user_service.deactivate_user(user.id)

        assert result is True
        # Retrieve to check
        updated_user = user_service.get_user(user.id)
        assert updated_user.is_active is False

    def test_activate_user(self, user_service):
        """Test activating user account."""
        # Create and deactivate a user
        user = user_service.create_user_legacy(
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            password="StrongPassword123!",
        )
        assert user is not None
        user_service.deactivate_user(user.id)
        
        # Activate the user
        result = user_service.activate_user(user.id)

        assert result is True
        # Retrieve to check
        updated_user = user_service.get_user(user.id)
        assert updated_user.is_active is True

    def test_record_login(self, user_service):
        """Test recording user login."""
        # Create a user
        user = user_service.create_user_legacy(
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            password="StrongPassword123!",
        )
        assert user is not None
        initial_count = user.login_count

        # Record login
        updated = user_service.record_login(user.id)

        assert updated is not None
        assert updated.login_count == initial_count + 1
        assert updated.last_login_at is not None

    def test_list_users(self, user_service):
        """Test listing users with filters."""
        # Create multiple users
        user1 = user_service.create_user_legacy(
            email="student@example.com",
            username="student1",
            full_name="Student One",
            password="StrongPassword123!",
        )
        user2 = user_service.create_user_legacy(
            email="instructor@example.com",
            username="instructor1",
            full_name="Instructor One",
            password="StrongPassword123!",
        )
        # Add instructor role to user2
        user_service.add_role(user2.id, UserRole.INSTRUCTOR)
        
        # List all active users
        users = user_service.list_users(active_only=True)
        assert len(users) >= 2

        # List instructors only
        instructors = user_service.list_users(role=UserRole.INSTRUCTOR)
        assert len(instructors) >= 1
        assert all(UserRole.INSTRUCTOR in u.roles for u in instructors)


@pytest.mark.integration
class TestAuthenticationService:
    """Tests for AuthenticationService."""

    def test_authenticate_user_with_username(self, auth_service, user_service):
        """Test authenticating user with username."""
        user = user_service.create_user_legacy(
            email="auth@example.com",
            username="authuser",
            full_name="Auth User",
            password="StrongPassword123!",
        )

        authenticated = auth_service.authenticate_user("authuser", "StrongPassword123!")

        assert authenticated is not None
        assert authenticated.id == user.id

    def test_authenticate_user_with_email(self, auth_service, user_service):
        """Test authenticating user with email."""
        user = user_service.create_user_legacy(
            email="auth2@example.com",
            username="authuser2",
            full_name="Auth User 2",
            password="StrongPassword123!",
        )

        authenticated = auth_service.authenticate_user("auth2@example.com", "StrongPassword123!")

        assert authenticated is not None
        assert authenticated.id == user.id

    def test_authenticate_wrong_password(self, auth_service, user_service):
        """Test authentication with wrong password."""
        # Create a user first
        user = user_service.create_user_legacy(
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            password="StrongPassword123!",
        )
        assert user is not None
        
        # Try with wrong password
        authenticated = auth_service.authenticate_user("testuser", "wrongpassword")

        assert authenticated is None

    def test_authenticate_inactive_user(self, auth_service, user_service):
        """Test authenticating inactive user."""
        # Create a user and deactivate
        user = user_service.create_user_legacy(
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            password="StrongPassword123!",
        )
        assert user is not None
        user_service.deactivate_user(user.id)

        # Try to authenticate
        authenticated = auth_service.authenticate_user("testuser", "StrongPassword123!")

        assert authenticated is None

    def test_create_access_token(self, auth_service, user_service):
        """Test creating access token."""
        # Create a user first
        user = user_service.create_user_legacy(
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            password="StrongPassword123!",
        )
        assert user is not None
        
        # Create access token
        token = auth_service.create_access_token(user.id)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_refresh_token(self, auth_service, user_service):
        """Test creating refresh token."""
        # Create a user first
        user = user_service.create_user_legacy(
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            password="StrongPassword123!",
        )
        assert user is not None
        
        # Create refresh token
        token = auth_service.create_refresh_token(user.id)

        assert token is not None
        assert isinstance(token, str)

    def test_verify_token(self, auth_service, user_service):
        """Test verifying JWT token."""
        # Create a user first
        user = user_service.create_user_legacy(
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            password="StrongPassword123!",
        )
        assert user is not None
        
        # Create and verify token
        token = auth_service.create_access_token(user.id)
        user_id = auth_service.verify_token(token)

        assert user_id is not None
        assert user_id == user.id

    def test_verify_invalid_token(self, auth_service):
        """Test verifying invalid token."""
        user_id = auth_service.verify_token("invalid.token.here")

        assert user_id is None

    def test_has_permission(self, auth_service, user_service):
        """Test checking user permissions."""
        # Create an instructor user
        instructor = user_service.create_user_legacy(
            email="instructor@example.com",
            username="instructor",
            full_name="Instructor User",
            password="StrongPassword123!",
        )
        assert instructor is not None
        # Add instructor role
        instructor = user_service.add_role(instructor.id, UserRole.INSTRUCTOR)
        
        # Check permission
        has_perm = auth_service.has_permission(
            instructor.id,
            UserPermission.CONTENT_CREATE
        )

        assert has_perm is True

    def test_has_role(self, auth_service, user_service):
        """Test checking user roles."""
        # Create an instructor user
        instructor = user_service.create_user_legacy(
            email="instructor@example.com",
            username="instructor",
            full_name="Instructor User",
            password="StrongPassword123!",
        )
        assert instructor is not None
        # Add instructor role
        instructor = user_service.add_role(instructor.id, UserRole.INSTRUCTOR)
        
        # Check role
        has_role = auth_service.has_role(instructor.id, UserRole.INSTRUCTOR)

        assert has_role is True
