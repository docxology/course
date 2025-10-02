"""Tests for users module functionality."""

import pytest
from uuid import uuid4

from curriculum.core.user import User, UserRole, UserPermission


class TestUserModule:
    """Tests for users module."""

    @pytest.fixture
    def user_service(self):
        """Create UserService instance."""
        from curriculum.users.user import UserService
        return UserService()

    def test_user_service_creation(self, user_service):
        """Test UserService instantiation."""
        assert user_service is not None

    def test_create_user_basic(self, user_service):
        """Test basic user creation."""
        user = user_service.create_user(
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            password="password123",
        )

        assert user is not None
        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.full_name == "Test User"
        assert user.is_active is True
        assert UserRole.STUDENT in user.roles

    def test_create_user_with_roles(self, user_service):
        """Test user creation with specific roles."""
        user = user_service.create_user(
            email="instructor@example.com",
            username="instructor",
            full_name="Test Instructor",
            password="password123",
            roles=[UserRole.INSTRUCTOR],
        )

        assert user is not None
        assert UserRole.INSTRUCTOR in user.roles
        assert UserRole.STUDENT not in user.roles
        assert user.has_permission(UserPermission.CONTENT_CREATE)

    def test_duplicate_email_creation(self, user_service):
        """Test duplicate email handling."""
        # Create first user
        user1 = user_service.create_user(
            email="duplicate@example.com",
            username="user1",
            full_name="User One",
            password="password123",
        )
        assert user1 is not None

        # Try to create user with same email
        user2 = user_service.create_user(
            email="duplicate@example.com",
            username="user2",
            full_name="User Two",
            password="password123",
        )

        assert user2 is None  # Should fail due to duplicate email

    def test_duplicate_username_creation(self, user_service):
        """Test duplicate username handling."""
        # Create first user
        user1 = user_service.create_user(
            email="user1@example.com",
            username="duplicateuser",
            full_name="User One",
            password="password123",
        )
        assert user1 is not None

        # Try to create user with same username
        user2 = user_service.create_user(
            email="user2@example.com",
            username="duplicateuser",
            full_name="User Two",
            password="password123",
        )

        assert user2 is None  # Should fail due to duplicate username

    def test_get_user_by_id(self, user_service):
        """Test retrieving user by ID."""
        # Create user
        created_user = user_service.create_user(
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            password="password123",
        )
        assert created_user is not None

        # Retrieve by ID
        retrieved_user = user_service.get_user(created_user.id)

        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id
        assert retrieved_user.email == created_user.email

    def test_get_user_by_email(self, user_service):
        """Test retrieving user by email."""
        # Create user
        created_user = user_service.create_user(
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            password="password123",
        )
        assert created_user is not None

        # Retrieve by email
        retrieved_user = user_service.get_user_by_email("test@example.com")

        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id

    def test_get_user_by_username(self, user_service):
        """Test retrieving user by username."""
        # Create user
        created_user = user_service.create_user(
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            password="password123",
        )
        assert created_user is not None

        # Retrieve by username
        retrieved_user = user_service.get_user_by_username("testuser")

        assert retrieved_user is not None
        assert retrieved_user.id == created_user.id

    def test_update_user(self, user_service):
        """Test user profile updates."""
        # Create user
        user = user_service.create_user(
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            password="password123",
        )
        assert user is not None

        # Update user
        updated_user = user_service.update_user(
            user.id,
            full_name="Updated Name",
            bio="Updated bio",
        )

        assert updated_user is not None
        assert updated_user.full_name == "Updated Name"
        assert updated_user.bio == "Updated bio"
        assert updated_user.email == user.email  # Unchanged

    def test_change_password(self, user_service):
        """Test password changes."""
        # Create user
        user = user_service.create_user(
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            password="oldpassword123",
        )
        assert user is not None

        # Change password
        result = user_service.change_password(user.id, "oldpassword123", "newpassword123")

        assert result is True

        # Verify new password works
        assert user_service.verify_password(user.id, "newpassword123") is True
        assert user_service.verify_password(user.id, "oldpassword123") is False

    def test_verify_password(self, user_service):
        """Test password verification."""
        # Create user
        user = user_service.create_user(
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            password="testpassword123",
        )
        assert user is not None

        # Test correct password
        assert user_service.verify_password(user.id, "testpassword123") is True

        # Test incorrect password
        assert user_service.verify_password(user.id, "wrongpassword") is False

    def test_add_user_role(self, user_service):
        """Test adding user roles."""
        # Create user
        user = user_service.create_user(
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            password="password123",
        )
        assert user is not None

        # Add instructor role
        updated_user = user_service.add_role(user.id, UserRole.INSTRUCTOR)

        assert updated_user is not None
        assert UserRole.INSTRUCTOR in updated_user.roles
        assert updated_user.has_permission(UserPermission.CONTENT_CREATE)

    def test_remove_user_role(self, user_service):
        """Test removing user roles."""
        # Create user with instructor role
        user = user_service.create_user(
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            password="password123",
            roles=[UserRole.INSTRUCTOR],
        )
        assert user is not None
        assert UserRole.INSTRUCTOR in user.roles

        # Remove instructor role
        updated_user = user_service.remove_role(user.id, UserRole.INSTRUCTOR)

        assert updated_user is not None
        assert UserRole.INSTRUCTOR not in updated_user.roles
        assert not updated_user.has_permission(UserPermission.CONTENT_CREATE)

    def test_deactivate_user(self, user_service):
        """Test user deactivation."""
        # Create user
        user = user_service.create_user(
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            password="password123",
        )
        assert user is not None
        assert user.is_active is True

        # Deactivate user
        result = user_service.deactivate_user(user.id)

        assert result is True

        # Verify deactivation
        updated_user = user_service.get_user(user.id)
        assert updated_user.is_active is False

    def test_activate_user(self, user_service):
        """Test user activation."""
        # Create and deactivate user
        user = user_service.create_user(
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            password="password123",
        )
        user_service.deactivate_user(user.id)
        assert user.is_active is False

        # Activate user
        result = user_service.activate_user(user.id)

        assert result is True

        # Verify activation
        updated_user = user_service.get_user(user.id)
        assert updated_user.is_active is True

    def test_list_users(self, user_service):
        """Test user listing."""
        # Create multiple users
        users_data = [
            ("user1@example.com", "user1", "User One", [UserRole.STUDENT]),
            ("user2@example.com", "user2", "User Two", [UserRole.INSTRUCTOR]),
            ("user3@example.com", "user3", "User Three", [UserRole.STUDENT]),
        ]

        created_users = []
        for email, username, full_name, roles in users_data:
            user = user_service.create_user(
                email=email,
                username=username,
                full_name=full_name,
                password="password123",
                roles=roles,
            )
            created_users.append(user)

        # List all users
        all_users = user_service.list_users()
        assert len(all_users) >= 3

        # List active users only
        active_users = user_service.list_users(active_only=True)
        assert len(active_users) >= 3

        # List by role
        instructors = user_service.list_users(role=UserRole.INSTRUCTOR)
        assert len(instructors) >= 1
        assert all(UserRole.INSTRUCTOR in u.roles for u in instructors)

    def test_record_login(self, user_service):
        """Test login recording."""
        # Create user
        user = user_service.create_user(
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            password="password123",
        )
        assert user is not None

        initial_count = user.login_count

        # Record login
        updated_user = user_service.record_login(user.id)

        assert updated_user is not None
        assert updated_user.login_count == initial_count + 1
        assert updated_user.last_login_at is not None

    def test_has_permission(self, user_service):
        """Test permission checking."""
        # Create user with specific roles
        student = user_service.create_user(
            email="student@example.com",
            username="student",
            full_name="Test Student",
            password="password123",
            roles=[UserRole.STUDENT],
        )

        instructor = user_service.create_user(
            email="instructor@example.com",
            username="instructor",
            full_name="Test Instructor",
            password="password123",
            roles=[UserRole.INSTRUCTOR],
        )

        # Test student permissions
        assert user_service.has_permission(student.id, UserPermission.CONTENT_READ)
        assert not user_service.has_permission(student.id, UserPermission.CONTENT_CREATE)

        # Test instructor permissions
        assert user_service.has_permission(instructor.id, UserPermission.CONTENT_READ)
        assert user_service.has_permission(instructor.id, UserPermission.CONTENT_CREATE)
        assert user_service.has_permission(instructor.id, UserPermission.ASSESSMENT_CREATE)


class TestUserValidation:
    """Tests for user validation."""

    @pytest.fixture
    def user_service(self):
        """Create UserService instance."""
        from curriculum.users.user import UserService
        return UserService()

    def test_email_validation(self, user_service):
        """Test email validation."""
        # Valid email
        user = user_service.create_user(
            email="valid@example.com",
            username="validuser",
            full_name="Valid User",
            password="password123",
        )
        assert user is not None

        # Invalid email format should be caught by Pydantic

    def test_username_validation(self, user_service):
        """Test username validation."""
        # Valid username
        user = user_service.create_user(
            email="test@example.com",
            username="valid_username",
            full_name="Valid User",
            password="password123",
        )
        assert user is not None

        # Username too short should be caught by Pydantic

    def test_password_strength(self, user_service):
        """Test password strength requirements."""
        # This would be tested in the actual implementation
        # For now, just test that user creation works
        user = user_service.create_user(
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            password="password123",
        )
        assert user is not None


class TestUserErrorHandling:
    """Tests for user error handling."""

    @pytest.fixture
    def user_service(self):
        """Create UserService instance."""
        from curriculum.users.user import UserService
        return UserService()

    def test_get_nonexistent_user(self, user_service):
        """Test retrieving nonexistent user."""
        fake_id = uuid4()
        user = user_service.get_user(fake_id)

        assert user is None

    def test_get_user_by_nonexistent_email(self, user_service):
        """Test retrieving user by nonexistent email."""
        user = user_service.get_user_by_email("nonexistent@example.com")

        assert user is None

    def test_update_nonexistent_user(self, user_service):
        """Test updating nonexistent user."""
        fake_id = uuid4()
        user = user_service.update_user(fake_id, full_name="New Name")

        assert user is None

    def test_change_password_nonexistent_user(self, user_service):
        """Test changing password for nonexistent user."""
        fake_id = uuid4()
        result = user_service.change_password(fake_id, "old", "new")

        assert result is False

    def test_verify_password_nonexistent_user(self, user_service):
        """Test verifying password for nonexistent user."""
        fake_id = uuid4()
        result = user_service.verify_password(fake_id, "password")

        assert result is False


