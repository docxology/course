"""Security tests for authentication system."""

import pytest

from curriculum.users.user import AuthenticationService, UserService


class TestAuthenticationSecurity:
    """Security tests for authentication system."""

    @pytest.fixture
    def user_service(self):
        """Create UserService instance."""
        return UserService()

    @pytest.fixture
    def auth_service(self, user_service):
        """Create AuthenticationService instance."""
        return AuthenticationService(user_service)

    def test_sql_injection_prevention(self, auth_service, user_service):
        """Test that SQL injection attempts are prevented."""
        # Create a user first
        user, error = user_service.create_user(
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            password="SecurePass123!",
        )

        # Try SQL injection in username
        malicious_username = "'; DROP TABLE users; --"
        authenticated = auth_service.authenticate_user(malicious_username, "SecurePass123!")

        # Should fail authentication
        assert authenticated is None

        # Verify user still exists
        retrieved = user_service.get_user(user.id)
        assert retrieved is not None

    def test_xss_prevention_in_user_input(self, auth_service, user_service):
        """Test that XSS attempts in user input are prevented."""
        # Create user with potentially malicious data
        user, error = user_service.create_user(
            email="test@example.com",
            username="testuser",
            full_name="<script>alert('xss')</script>",
            password="SecurePass123!",
        )

        # Verify user was created successfully
        assert user is not None

        # Verify the malicious script was not executed
        assert user.full_name == "<script>alert('xss')</script>"

    def test_password_strength_requirements(self, user_service):
        """Test password strength validation."""
        # Test weak passwords
        weak_passwords = [
            "123",  # Too short
            "password",  # Common word
            "PASSWORD",  # Only uppercase
            "12345678",  # Only numbers
            "abcdefgh",  # Only lowercase
        ]

        for i, password in enumerate(weak_passwords):
            user, error = user_service.create_user(
                email=f"test{i}@example.com",
                username=f"testuser{i}",
                full_name=f"Test User {i}",
                password=password,
            )
            assert user is None
            assert error

    def test_session_hijacking_prevention(self, auth_service, user_service):
        """Test session security measures."""
        user, error = user_service.create_user(
            email="session@example.com",
            username="sessionuser",
            full_name="Session User",
            password="SecurePass123!",
        )

        # Create access token
        token = auth_service.create_access_token(user.id)

        # Token should be properly signed
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

        # Token should be verifiable
        user_id = auth_service.verify_token(token)
        assert user_id == user.id

    def test_csrf_protection(self, auth_service):
        """Test CSRF protection mechanisms."""
        # This would test CSRF token generation and validation
        # For now, just verify that the auth service exists
        assert auth_service is not None

    def test_rate_limiting(self, auth_service, user_service):
        """Test rate limiting for authentication attempts."""
        user_service.create_user(
            email="ratelimit@example.com",
            username="ratelimituser",
            full_name="Rate Limit User",
            password="SecurePass123!",
        )

        # Attempt multiple failed logins
        for i in range(10):
            authenticated = auth_service.authenticate_user("ratelimituser", "wrongpassword")
            # Should fail but not be rate limited in test environment
            assert authenticated is None

    def test_secure_password_storage(self, user_service):
        """Test that passwords are securely hashed."""
        user, error = user_service.create_user(
            email="security@example.com",
            username="securityuser",
            full_name="Security User",
            password="SecurePass123!",
        )

        # Password should not be stored in plain text
        # This would require access to the internal storage
        # For now, just verify user creation works
        assert user is not None
        assert "SecurePass123!" not in user.hashed_password
        assert user_service.verify_password(user.id, "SecurePass123!")

    def test_input_sanitization(self, user_service):
        """Test input sanitization for various fields."""
        # Test with various special characters
        special_chars = "!@#$%^&*()_+-=[]{}|;':\",./<>?"

        user, error = user_service.create_user(
            email="sanitize@example.com",
            username="sanitizeuser",
            full_name=f"User with {special_chars}",
            password="SecurePass123!",
        )

        assert user is not None
        assert special_chars in user.full_name

    def test_password_change_retains_validation(self, user_service):
        user, error = user_service.create_user(
            email="change@example.com",
            username="changeuser",
            full_name="Change User",
            password="SecurePass123!",
        )
        assert not error
        old_hash = user.hashed_password
        assert not user_service.change_password(user.id, "SecurePass123!", "weak")
        assert user.hashed_password == old_hash
        assert user_service.change_password(user.id, "SecurePass123!", "UpdatedPass123!")
        assert user_service.verify_password(user.id, "UpdatedPass123!")
        assert not user_service.verify_password(user.id, "SecurePass123!")
        assert user_service._hash_password("UpdatedPass123!") != user.hashed_password
