# AI Agents Guide - Users Module

## Overview

The users module provides comprehensive user management, authentication, and authorization functionality for the Curriculum Repository System. It implements role-based access control, secure password management, and JWT-based authentication following industry best practices.

## Module Structure

```
users/
├── user.py         # User service and authentication service
└── README.md       # Module documentation
```

## User Management Architecture

### User Model Design

1. **Core User Entity**:
```python
class User(BaseEntity):
    """Core user model with comprehensive fields."""

    email: EmailStr = Field(..., unique=True, index=True)
    username: str = Field(..., min_length=3, max_length=50, unique=True, index=True)
    full_name: str = Field(..., min_length=1, max_length=100)
    hashed_password: str = Field(...)
    bio: Optional[str] = Field(None, max_length=500)
    avatar_url: Optional[str] = None
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)
    roles: List[UserRole] = Field(default_factory=lambda: [UserRole.STUDENT])
    permissions: List[UserPermission] = Field(default_factory=list)
    last_login_at: Optional[datetime] = None
    login_count: int = Field(default=0)
    failed_login_attempts: int = Field(default=0)
    locked_until: Optional[datetime] = None
    preferences: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
```

2. **Role and Permission System**:
```python
class UserRole(str, Enum):
    """User roles in the system."""
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    INSTRUCTOR = "instructor"
    CONTENT_CREATOR = "content_creator"
    REVIEWER = "reviewer"
    STUDENT = "student"

class UserPermission(str, Enum):
    """Granular permissions for fine-grained access control."""
    # User management
    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"

    # Content management
    CONTENT_CREATE = "content:create"
    CONTENT_READ = "content:read"
    CONTENT_UPDATE = "content:update"
    CONTENT_DELETE = "content:delete"
    CONTENT_PUBLISH = "content:publish"

    # Assessment management
    ASSESSMENT_CREATE = "assessment:create"
    ASSESSMENT_READ = "assessment:read"
    ASSESSMENT_UPDATE = "assessment:update"
    ASSESSMENT_DELETE = "assessment:delete"
    ASSESSMENT_GRADE = "assessment:grade"

    # Analytics and reporting
    ANALYTICS_READ = "analytics:read"
    ANALYTICS_EXPORT = "analytics:export"
    ANALYTICS_VIEW_ALL = "analytics:view_all"
```

3. **Role-Based Permissions**:
```python
ROLE_PERMISSIONS = {
    UserRole.SUPER_ADMIN: [perm for perm in UserPermission],
    UserRole.ADMIN: [
        UserPermission.USER_CREATE, UserPermission.USER_READ, UserPermission.USER_UPDATE,
        UserPermission.CONTENT_CREATE, UserPermission.CONTENT_READ, UserPermission.CONTENT_UPDATE,
        UserPermission.CONTENT_PUBLISH, UserPermission.ASSESSMENT_CREATE,
        UserPermission.ASSESSMENT_READ, UserPermission.ASSESSMENT_UPDATE,
        UserPermission.ANALYTICS_READ, UserPermission.ANALYTICS_EXPORT
    ],
    UserRole.INSTRUCTOR: [
        UserPermission.CONTENT_CREATE, UserPermission.CONTENT_READ, UserPermission.CONTENT_UPDATE,
        UserPermission.ASSESSMENT_CREATE, UserPermission.ASSESSMENT_READ,
        UserPermission.ASSESSMENT_UPDATE, UserPermission.ASSESSMENT_GRADE,
        UserPermission.ANALYTICS_READ
    ],
    UserRole.CONTENT_CREATOR: [
        UserPermission.CONTENT_CREATE, UserPermission.CONTENT_READ, UserPermission.CONTENT_UPDATE
    ],
    UserRole.REVIEWER: [
        UserPermission.CONTENT_READ, UserPermission.CONTENT_UPDATE,
        UserPermission.ASSESSMENT_READ, UserPermission.ASSESSMENT_UPDATE
    ],
    UserRole.STUDENT: [
        UserPermission.CONTENT_READ, UserPermission.ASSESSMENT_READ
    ]
}
```

## Authentication Service

### JWT Token Management

1. **Token Generation**:
```python
class AuthenticationService:
    """Handles user authentication and JWT token management."""

    def __init__(self, user_service: UserService):
        self.user_service = user_service

    def create_access_token(self, user_id: UUID, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token."""
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))

        to_encode = {
            "sub": str(user_id),
            "type": "access",
            "exp": expire,
            "iat": datetime.utcnow(),
            "iss": settings.app_name,
            "aud": settings.allowed_audiences
        }

        return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

    def create_refresh_token(self, user_id: UUID) -> str:
        """Create JWT refresh token with longer expiration."""
        expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)

        to_encode = {
            "sub": str(user_id),
            "type": "refresh",
            "exp": expire,
            "iat": datetime.utcnow()
        }

        return jwt.encode(to_encode, settings.refresh_key, algorithm=settings.algorithm)
```

2. **Token Verification**:
```python
def verify_token(self, token: str, expected_type: str = "access") -> Optional[UUID]:
    """Verify JWT token and extract user ID."""
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
            audience=settings.allowed_audiences
        )

        # Validate token type
        token_type = payload.get("type")
        if token_type != expected_type:
            return None

        # Extract user ID
        user_id_str = payload.get("sub")
        if not user_id_str:
            return None

        return UUID(user_id_str)

    except JWTError as e:
        logger.warning(f"Token verification failed: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error during token verification: {e}")
        return None
```

3. **User Authentication**:
```python
def authenticate_user(self, username_or_email: str, password: str) -> Optional[User]:
    """Authenticate user with username/email and password."""
    # Find user by username or email
    user = None
    if "@" in username_or_email:
        user = self.user_service.get_user_by_email(username_or_email)
    else:
        user = self.user_service.get_user_by_username(username_or_email)

    if not user:
        return None

    # Check if account is locked
    if user.locked_until and user.locked_until > datetime.utcnow():
        return None

    # Verify password
    if not self.user_service.verify_password(user.id, password):
        # Record failed attempt
        self.user_service.record_failed_login(user.id)

        # Lock account if too many failures
        if user.failed_login_attempts >= settings.max_login_attempts:
            self.user_service.lock_user(user.id)

        return None

    # Successful authentication
    self.user_service.record_successful_login(user.id)
    return user
```

## User Service Operations

### User Lifecycle Management

1. **User Creation**:
```python
def create_user(
    self,
    email: str,
    username: str,
    full_name: str,
    password: str,
    roles: List[UserRole] = None,
    is_verified: bool = False
) -> Optional[User]:
    """Create new user with validation."""
    # Validate email format and uniqueness
    if not validate_email(email):
        return None

    existing_user = self.get_user_by_email(email)
    if existing_user:
        return None

    # Validate username format and uniqueness
    if not validate_username(username):
        return None

    existing_user = self.get_user_by_username(username)
    if existing_user:
        return None

    # Hash password
    hashed_password = hash_password(password)

    # Set default roles
    user_roles = roles or [UserRole.STUDENT]

    # Create user
    user = User(
        email=email,
        username=username,
        full_name=full_name,
        hashed_password=hashed_password,
        roles=user_roles,
        is_verified=is_verified,
        permissions=self._calculate_permissions(user_roles)
    )

    # Persist user
    self._users[user.id] = user
    return user
```

2. **Password Management**:
```python
def change_password(self, user_id: UUID, current_password: str, new_password: str) -> bool:
    """Change user password with validation."""
    user = self.get_user(user_id)
    if not user:
        return False

    # Verify current password
    if not self.verify_password(user_id, current_password):
        return False

    # Validate new password strength
    if not validate_password_strength(new_password):
        return False

    # Hash new password
    new_hashed = hash_password(new_password)
    user.hashed_password = new_hashed
    user.update_timestamp()

    return True

def reset_password(self, user_id: UUID, reset_token: str, new_password: str) -> bool:
    """Reset password using reset token."""
    # Verify reset token
    if not self.verify_password_reset_token(user_id, reset_token):
        return False

    # Validate new password
    if not validate_password_strength(new_password):
        return False

    # Update password
    user = self.get_user(user_id)
    if not user:
        return False

    user.hashed_password = hash_password(new_password)
    user.update_timestamp()

    return True
```

3. **Role and Permission Management**:
```python
def add_role(self, user_id: UUID, role: UserRole) -> Optional[User]:
    """Add role to user."""
    user = self.get_user(user_id)
    if not user:
        return None

    if role not in user.roles:
        user.roles.append(role)
        user.permissions = self._calculate_permissions(user.roles)
        user.update_timestamp()

    return user

def remove_role(self, user_id: UUID, role: UserRole) -> Optional[User]:
    """Remove role from user."""
    user = self.get_user(user_id)
    if not user:
        return None

    if role in user.roles:
        user.roles.remove(role)
        user.permissions = self._calculate_permissions(user.roles)
        user.update_timestamp()

    return user

def has_permission(self, user_id: UUID, permission: UserPermission) -> bool:
    """Check if user has specific permission."""
    user = self.get_user(user_id)
    if not user:
        return False

    return permission in user.permissions

def _calculate_permissions(self, roles: List[UserRole]) -> List[UserPermission]:
    """Calculate permissions based on user roles."""
    permissions = set()

    for role in roles:
        role_permissions = ROLE_PERMISSIONS.get(role, [])
        permissions.update(role_permissions)

    return list(permissions)
```

## Session Management

### Login Tracking

1. **Login Recording**:
```python
def record_login(self, user_id: UUID) -> Optional[User]:
    """Record successful user login."""
    user = self.get_user(user_id)
    if not user:
        return None

    user.last_login_at = datetime.utcnow()
    user.login_count += 1
    user.failed_login_attempts = 0  # Reset failed attempts
    user.locked_until = None  # Unlock if locked

    return user

def record_failed_login(self, user_id: UUID) -> None:
    """Record failed login attempt."""
    user = self.get_user(user_id)
    if not user:
        return

    user.failed_login_attempts += 1

    # Lock account after max attempts
    if user.failed_login_attempts >= settings.max_login_attempts:
        user.locked_until = datetime.utcnow() + timedelta(minutes=settings.lockout_duration_minutes)
```

2. **Session Analytics**:
```python
def get_user_sessions(self, user_id: UUID, days: int = 30) -> List[Dict[str, Any]]:
    """Get user session information."""
    # This would typically query a sessions table
    # For now, return mock data based on login tracking
    user = self.get_user(user_id)
    if not user:
        return []

    sessions = []
    current_date = datetime.utcnow()

    for i in range(min(user.login_count, days)):
        session_date = current_date - timedelta(days=i)
        sessions.append({
            "date": session_date.date(),
            "login_time": session_date,
            "ip_address": "192.168.1.100",  # Would be stored in real implementation
            "user_agent": "Mozilla/5.0...",  # Would be stored in real implementation
            "duration": 3600  # Would be calculated from real session data
        })

    return sessions
```

## Development Patterns

### User Validation Pipeline

1. **Multi-Layer Validation**:
```python
def validate_user_data(self, user_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Comprehensive user data validation."""
    errors = []

    # Basic field validation
    if not user_data.get('email'):
        errors.append("Email is required")
    elif not validate_email(user_data['email']):
        errors.append("Invalid email format")

    if not user_data.get('username'):
        errors.append("Username is required")
    elif not validate_username(user_data['username']):
        errors.append("Invalid username format")

    # Password validation
    password = user_data.get('password')
    if password:
        password_errors = validate_password_strength(password)
        errors.extend(password_errors)

    # Role validation
    roles = user_data.get('roles', [])
    valid_roles = [role.value for role in UserRole]
    for role in roles:
        if role not in valid_roles:
            errors.append(f"Invalid role: {role}")

    return len(errors) == 0, errors
```

2. **Password Strength Validation**:
```python
def validate_password_strength(password: str) -> List[str]:
    """Validate password strength requirements."""
    errors = []

    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")

    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")

    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")

    if not re.search(r'\d', password):
        errors.append("Password must contain at least one digit")

    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("Password must contain at least one special character")

    # Check against common passwords
    if password.lower() in COMMON_PASSWORDS:
        errors.append("Password is too common")

    return errors
```

### Security Best Practices

1. **Password Hashing**:
```python
def hash_password(password: str) -> str:
    """Hash password using bcrypt with salt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

# Password reset token generation
def generate_password_reset_token(user_id: UUID, expires_in: int = 3600) -> str:
    """Generate secure password reset token."""
    token_data = {
        "user_id": str(user_id),
        "type": "password_reset",
        "exp": datetime.utcnow() + timedelta(seconds=expires_in),
        "iat": datetime.utcnow()
    }

    return jwt.encode(token_data, settings.secret_key, algorithm="HS256")
```

2. **Account Security**:
```python
def check_account_security(self, user_id: UUID) -> Dict[str, Any]:
    """Check user account security status."""
    user = self.get_user(user_id)
    if not user:
        return {"secure": False, "issues": ["User not found"]}

    issues = []
    recommendations = []

    # Check password age
    if user.updated_at and (datetime.utcnow() - user.updated_at).days > 90:
        issues.append("Password is older than 90 days")
        recommendations.append("Consider updating your password")

    # Check for suspicious activity
    if user.failed_login_attempts > 5:
        issues.append("Multiple failed login attempts detected")
        recommendations.append("Review recent login activity")

    # Check session activity
    if user.last_login_at and (datetime.utcnow() - user.last_login_at).days > 30:
        recommendations.append("Account has been inactive for over 30 days")

    return {
        "secure": len(issues) == 0,
        "issues": issues,
        "recommendations": recommendations,
        "last_login": user.last_login_at,
        "failed_attempts": user.failed_login_attempts
    }
```

## Testing Guidelines

### User Service Tests

1. **Authentication Testing**:
```python
class TestAuthenticationService:
    def test_successful_authentication(self, auth_service, user_service):
        # Create test user
        user = user_service.create_user(
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            password="secure_password123"
        )

        # Test successful authentication
        authenticated = auth_service.authenticate_user("testuser", "secure_password123")
        assert authenticated is not None
        assert authenticated.id == user.id

    def test_failed_authentication(self, auth_service, user_service):
        user = user_service.create_user(
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            password="secure_password123"
        )

        # Test wrong password
        authenticated = auth_service.authenticate_user("testuser", "wrong_password")
        assert authenticated is None

    def test_account_lockout(self, auth_service, user_service):
        user = user_service.create_user(
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            password="secure_password123"
        )

        # Simulate multiple failed attempts
        for _ in range(settings.max_login_attempts):
            auth_service.authenticate_user("testuser", "wrong_password")

        # Account should be locked
        assert user.locked_until is not None
        authenticated = auth_service.authenticate_user("testuser", "secure_password123")
        assert authenticated is None
```

2. **Permission Testing**:
```python
class TestUserPermissions:
    def test_role_permissions(self, user_service):
        # Create instructor user
        instructor = user_service.create_user(
            email="instructor@example.com",
            username="instructor",
            full_name="Test Instructor",
            password="password123"
        )
        user_service.add_role(instructor.id, UserRole.INSTRUCTOR)

        # Check permissions
        assert user_service.has_permission(instructor.id, UserPermission.CONTENT_CREATE)
        assert user_service.has_permission(instructor.id, UserPermission.ASSESSMENT_CREATE)
        assert not user_service.has_permission(instructor.id, UserPermission.USER_DELETE)

    def test_permission_inheritance(self, user_service):
        # Create admin user
        admin = user_service.create_user(
            email="admin@example.com",
            username="admin",
            full_name="Test Admin",
            password="password123"
        )
        user_service.add_role(admin.id, UserRole.ADMIN)

        # Admin should have all permissions
        all_permissions = [perm for perm in UserPermission]
        for permission in all_permissions:
            assert user_service.has_permission(admin.id, permission)
```

### Integration Tests

1. **End-to-End Authentication Flow**:
```python
@pytest.mark.integration
async def test_complete_authentication_flow(self, client: TestClient):
    # Register new user
    register_data = {
        "email": "newuser@example.com",
        "username": "newuser",
        "full_name": "New User",
        "password": "secure_password123"
    }

    response = client.post("/api/v1/users/register", json=register_data)
    assert response.status_code == 201

    # Login
    login_data = {
        "username_or_email": "newuser",
        "password": "secure_password123"
    }

    response = client.post("/api/v1/users/login", json=login_data)
    assert response.status_code == 200

    tokens = response.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens

    # Access protected endpoint
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    response = client.get("/api/v1/users/me", headers=headers)
    assert response.status_code == 200

    user_data = response.json()
    assert user_data["username"] == "newuser"
```

2. **Role-Based Access Control Testing**:
```python
@pytest.mark.integration
async def test_rbac_enforcement(self, client: TestClient):
    # Create student user
    student_data = {
        "email": "student@example.com",
        "username": "student",
        "full_name": "Test Student",
        "password": "password123"
    }

    response = client.post("/api/v1/users/register", json=student_data)
    student_tokens = response.json()

    # Student should not be able to access admin endpoints
    headers = {"Authorization": f"Bearer {student_tokens['access_token']}"}
    response = client.get("/api/v1/users/", headers=headers)
    assert response.status_code == 403  # Forbidden

    # Create admin user
    admin_data = {
        "email": "admin@example.com",
        "username": "admin",
        "full_name": "Test Admin",
        "password": "password123"
    }

    # Simulate admin creation (normally done by super admin)
    # This would typically require different endpoint or special handling

    # Admin should be able to access admin endpoints
    # admin_headers = {"Authorization": f"Bearer {admin_tokens['access_token']}"}
    # response = client.get("/api/v1/users/", headers=admin_headers)
    # assert response.status_code == 200
```

## Security Considerations

### Password Security

1. **Strong Hashing**:
```python
# Use bcrypt with proper salt rounds
def hash_password(password: str) -> str:
    # bcrypt automatically generates salt
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=12)).decode('utf-8')

# Password policy enforcement
PASSWORD_POLICY = {
    "min_length": 8,
    "require_uppercase": True,
    "require_lowercase": True,
    "require_digits": True,
    "require_special": True,
    "max_age_days": 90,
    "prevent_reuse": 5  # Don't allow last 5 passwords
}
```

2. **Account Protection**:
```python
def implement_account_lockout(self, user_id: UUID) -> None:
    """Implement progressive account lockout."""
    user = self.get_user(user_id)
    if not user:
        return

    # Progressive lockout duration
    attempts = user.failed_login_attempts
    if attempts >= 5:
        lockout_minutes = min(attempts * 2, 1440)  # Max 24 hours
        user.locked_until = datetime.utcnow() + timedelta(minutes=lockout_minutes)

def check_suspicious_activity(self, user_id: UUID, login_ip: str, user_agent: str) -> bool:
    """Check for suspicious login activity."""
    user = self.get_user(user_id)
    if not user:
        return False

    # Check for login from new location
    if user.last_login_ip and user.last_login_ip != login_ip:
        # Could implement geolocation check here
        pass

    # Check for unusual user agent
    if user.last_user_agent and user.last_user_agent != user_agent:
        # Could flag for review
        pass

    # Update login tracking
    user.last_login_ip = login_ip
    user.last_user_agent = user_agent

    return True
```

### Token Security

1. **Token Best Practices**:
```python
# Short-lived access tokens
ACCESS_TOKEN_EXPIRE_MINUTES = 15

# Longer-lived refresh tokens
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Include audience and issuer claims
def create_access_token(self, user_id: UUID) -> str:
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {
        "sub": str(user_id),
        "type": "access",
        "exp": expire,
        "iat": datetime.utcnow(),
        "iss": "curriculum-repository",
        "aud": ["curriculum-api", "curriculum-web"]
    }

    return jwt.encode(to_encode, settings.secret_key, algorithm="HS256")
```

2. **Token Revocation**:
```python
def revoke_user_tokens(self, user_id: UUID) -> None:
    """Revoke all tokens for user (logout everywhere)."""
    # In a real implementation, this would:
    # 1. Add user_id to a revocation list in Redis/database
    # 2. Set short expiration on existing tokens
    # 3. Force re-authentication on next request

    # For now, we'll implement a simple version
    revocation_key = f"token_revoked:{user_id}"
    redis_client.set(revocation_key, "true", ex=3600)  # Revoke for 1 hour

def is_token_revoked(self, user_id: UUID) -> bool:
    """Check if user tokens have been revoked."""
    revocation_key = f"token_revoked:{user_id}"
    return redis_client.exists(revocation_key)
```

## Performance Optimization

### User Lookup Optimization

1. **Efficient Queries**:
```python
def get_user_by_email_optimized(self, email: str) -> Optional[User]:
    """Optimized user lookup by email."""
    # Use direct dictionary lookup instead of iteration
    # In real implementation, this would use database indexes
    for user in self._users.values():
        if user.email == email and not user.is_deleted:
            return user
    return None

def bulk_user_lookup(self, user_ids: List[UUID]) -> Dict[UUID, User]:
    """Bulk lookup users by IDs."""
    users = {}
    for user_id in user_ids:
        user = self.get_user(user_id)
        if user:
            users[user_id] = user
    return users
```

2. **Caching Strategy**:
```python
@functools.lru_cache(maxsize=1000)
def get_user_cached(self, user_id: UUID) -> Optional[User]:
    """Cache user lookups for performance."""
    return self._users.get(user_id)

def invalidate_user_cache(self, user_id: UUID) -> None:
    """Invalidate user cache when user data changes."""
    self.get_user_cached.cache_remove(user_id)
```

### Authentication Performance

1. **Connection Pooling**:
```python
# Database connection pooling for user lookups
def __init__(self):
    self.user_db_pool = self._create_connection_pool()

def _create_connection_pool(self):
    return AsyncIOMotorClient(
        settings.mongodb_url,
        maxPoolSize=20,
        minPoolSize=5,
        maxIdleTimeMS=30000
    )
```

2. **Batch Operations**:
```python
async def bulk_verify_users(self, user_ids: List[UUID]) -> Dict[UUID, bool]:
    """Verify multiple users in batch."""
    # Use single query for multiple users
    query = {"_id": {"$in": user_ids}, "is_active": True}
    users = await self.user_collection.find(query).to_list(None)

    verified_users = {UUID(str(user["_id"])) for user in users}
    return {user_id: user_id in verified_users for user_id in user_ids}
```

## Error Handling

### Comprehensive Error Responses

1. **Authentication Errors**:
```python
class AuthenticationError(HTTPException):
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )

class AuthorizationError(HTTPException):
    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )
```

2. **Validation Errors**:
```python
class UserValidationError(ValueError):
    """Custom exception for user validation errors."""
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}")

def handle_user_validation_error(error: UserValidationError) -> Dict[str, Any]:
    """Convert validation error to API response."""
    return {
        "error": "validation_error",
        "field": error.field,
        "message": error.message,
        "suggestion": get_field_suggestion(error.field)
    }
```

## Best Practices

### User Experience

1. **Clear Error Messages**:
```python
def get_friendly_error_message(error_code: str) -> str:
    """Get user-friendly error messages."""
    messages = {
        "invalid_credentials": "The username/email or password you entered is incorrect.",
        "account_locked": "Your account has been temporarily locked due to multiple failed login attempts. Please try again later.",
        "account_disabled": "Your account has been disabled. Please contact support.",
        "email_not_verified": "Please verify your email address before logging in.",
        "password_expired": "Your password has expired. Please reset it to continue."
    }
    return messages.get(error_code, "An error occurred. Please try again.")
```

2. **Security vs. Usability**:
```python
def balance_security_usability(self, action: str) -> Dict[str, Any]:
    """Balance security requirements with user experience."""
    security_level = self._get_security_level(action)

    if security_level == "high":
        return {
            "require_mfa": True,
            "require_captcha": True,
            "rate_limit": "strict",
            "session_timeout": 15  # minutes
        }
    elif security_level == "medium":
        return {
            "require_mfa": False,
            "require_captcha": True,
            "rate_limit": "moderate",
            "session_timeout": 60
        }
    else:
        return {
            "require_mfa": False,
            "require_captcha": False,
            "rate_limit": "lenient",
            "session_timeout": 480  # 8 hours
        }
```

### Data Privacy

1. **GDPR Compliance**:
```python
def export_user_data(self, user_id: UUID) -> Dict[str, Any]:
    """Export all user data for GDPR compliance."""
    user = self.get_user(user_id)
    if not user:
        return {}

    return {
        "personal_data": {
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "bio": user.bio,
            "avatar_url": user.avatar_url
        },
        "account_data": {
            "created_at": user.created_at,
            "last_login": user.last_login_at,
            "login_count": user.login_count,
            "roles": [role.value for role in user.roles],
            "is_active": user.is_active,
            "is_verified": user.is_verified
        },
        "activity_data": self._get_user_activity_data(user_id),
        "preferences": user.preferences,
        "exported_at": datetime.utcnow()
    }

def delete_user_data(self, user_id: UUID) -> bool:
    """Delete all user data for GDPR compliance."""
    # Soft delete user record
    user = self.get_user(user_id)
    if not user:
        return False

    user.soft_delete()

    # Delete associated data
    self._delete_user_activity_data(user_id)
    self._delete_user_preferences(user_id)

    return True
```

## Extension Points

### Custom Authentication Methods

1. **OAuth Integration**:
```python
def authenticate_with_oauth(self, provider: str, token: str) -> Optional[User]:
    """Authenticate user via OAuth provider."""
    # Validate OAuth token
    user_info = self._validate_oauth_token(provider, token)
    if not user_info:
        return None

    # Find or create user
    user = self.user_service.get_user_by_email(user_info["email"])
    if not user:
        user = self.user_service.create_user(
            email=user_info["email"],
            username=user_info["username"],
            full_name=user_info["name"],
            password=generate_random_password(),
            is_verified=True  # OAuth users are pre-verified
        )

    return user
```

2. **Multi-Factor Authentication**:
```python
def enable_mfa(self, user_id: UUID, mfa_type: str = "totp") -> Dict[str, Any]:
    """Enable multi-factor authentication for user."""
    user = self.get_user(user_id)
    if not user:
        return {"success": False, "error": "User not found"}

    if mfa_type == "totp":
        # Generate TOTP secret
        secret = pyotp.random_base32()
        user.mfa_secret = secret
        user.mfa_enabled = True

        # Generate QR code for setup
        qr_code = self._generate_totp_qr_code(user.email, secret)

        return {
            "success": True,
            "mfa_type": "totp",
            "secret": secret,
            "qr_code": qr_code
        }

    return {"success": False, "error": "Unsupported MFA type"}

def verify_mfa_token(self, user_id: UUID, token: str) -> bool:
    """Verify MFA token for user."""
    user = self.get_user(user_id)
    if not user or not user.mfa_enabled or not user.mfa_secret:
        return False

    totp = pyotp.TOTP(user.mfa_secret)
    return totp.verify(token)
```

### Advanced Authorization

1. **Attribute-Based Access Control**:
```python
def check_attribute_access(self, user_id: UUID, resource: str, action: str, attributes: Dict) -> bool:
    """Check access based on resource attributes."""
    user = self.get_user(user_id)
    if not user:
        return False

    # Example: Students can only access content from their enrolled courses
    if action == "content:read" and user.has_role(UserRole.STUDENT):
        content_course_id = attributes.get("course_id")
        user_enrolled_courses = self._get_user_enrolled_courses(user_id)

        return content_course_id in user_enrolled_courses

    # Example: Instructors can only modify content they created
    if action == "content:update" and user.has_role(UserRole.INSTRUCTOR):
        content_author_id = attributes.get("author_id")
        return content_author_id == user_id

    return True
```

2. **Time-Based Access**:
```python
def check_time_based_access(self, user_id: UUID, resource: str) -> bool:
    """Check time-based access restrictions."""
    user = self.get_user(user_id)
    if not user:
        return False

    current_time = datetime.utcnow().time()

    # Example: Students can only access system during business hours
    if user.has_role(UserRole.STUDENT):
        business_start = time(8, 0)  # 8 AM
        business_end = time(18, 0)   # 6 PM

        if not (business_start <= current_time <= business_end):
            return False

    # Example: Weekend restrictions
    if datetime.utcnow().weekday() >= 5:  # Saturday or Sunday
        if user.has_role(UserRole.STUDENT):
            return False  # Students can't access on weekends

    return True
```

## Questions to Ask

Before implementing user-related features:

1. **Security**: Does this feature handle sensitive user data? Are there security implications?
2. **Privacy**: Does this comply with data protection regulations (GDPR, CCPA)?
3. **Scalability**: How will this perform with thousands of users?
4. **Authentication**: What authentication methods should be supported?
5. **Authorization**: What roles and permissions are needed?
6. **Testing**: Are there comprehensive tests for authentication and authorization?

## Resources

### Internal Documentation
- `README.md`: Module overview and setup
- `tests/test_users_user_service.py`: Comprehensive user management tests

### External References
- [JWT RFC 7519](https://tools.ietf.org/html/rfc7519)
- [OAuth 2.0](https://tools.ietf.org/html/rfc6749)
- [bcrypt Password Hashing](https://en.wikipedia.org/wiki/Bcrypt)
- [RBAC](https://en.wikipedia.org/wiki/Role-based_access_control)

---

**Last Updated**: September 2025

**For Questions**: Consult the user service tests for usage examples and security patterns


