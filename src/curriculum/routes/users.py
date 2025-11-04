"""User API routes."""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel

from curriculum.config import settings
from curriculum.core.user import User, UserPermission, UserRole
from curriculum.routes.dependencies import get_current_user as get_user_dependency
from curriculum.users.user import AuthenticationService, UserService

router = APIRouter()

# Service instances
user_service = UserService()
auth_service = AuthenticationService(user_service)

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Request/Response models
class CreateUserRequest(BaseModel):
    """Request model for creating user."""

    email: str
    username: str
    full_name: str
    password: str
    roles: List[UserRole] = [UserRole.STUDENT]


class UpdateUserRequest(BaseModel):
    """Request model for updating user."""

    full_name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None


class LoginRequest(BaseModel):
    """Request model for user login."""

    username_or_email: str
    password: str


class TokenResponse(BaseModel):
    """Response model for authentication tokens."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = settings.access_token_expire_minutes * 60


class UserResponse(BaseModel):
    """Response model for user."""

    id: str
    email: str
    username: str
    full_name: str
    roles: List[str]
    permissions: List[str]
    is_active: bool
    is_verified: bool
    created_at: str
    last_login_at: Optional[str] = None


# Authentication routes
@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """Authenticate user and return tokens."""
    user = auth_service.authenticate_user(
        request.username_or_email,
        request.password,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Record login
    user_service.record_login(user.id)

    # Generate tokens
    access_token = auth_service.create_access_token(user.id)
    refresh_token = auth_service.create_refresh_token(user.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str):
    """Refresh access token using refresh token."""
    user_id = auth_service.verify_token(refresh_token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    # Generate new tokens
    access_token = auth_service.create_access_token(user_id)
    new_refresh_token = auth_service.create_refresh_token(user_id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        expires_in=settings.access_token_expire_minutes * 60,
    )


# User management routes
@router.post("/", response_model=UserResponse)
async def create_user(request: CreateUserRequest):
    """Create a new user."""
    # Check if user already exists
    existing_user = user_service.get_user_by_email(request.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    existing_user = user_service.get_user_by_username(request.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken",
        )

    # Create user
    user, error_message = user_service.create_user(
        email=request.email,
        username=request.username,
        full_name=request.full_name,
        password=request.password,
        roles=request.roles,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message or "Failed to create user",
        )

    return _user_to_response(user)


@router.get("/me", response_model=UserResponse)
async def get_current_user(current_user: User = Depends(get_user_dependency)):
    """Get current user profile."""
    return _user_to_response(current_user)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: UUID = Path(..., description="User ID")):
    """Get user by ID."""
    user = user_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return _user_to_response(user)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    request: UpdateUserRequest,
    current_user: User = Depends(get_user_dependency),
):
    """Update user profile."""
    # Check permissions
    if current_user.id != user_id and not current_user.has_permission(UserPermission.USER_UPDATE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    user = user_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    updated_user = user_service.update_user(
        user_id,
        full_name=request.full_name,
        bio=request.bio,
        avatar_url=request.avatar_url,
    )

    if not updated_user:
        raise HTTPException(status_code=400, detail="Failed to update user")

    return _user_to_response(updated_user)


@router.post("/{user_id}/change-password")
async def change_password(
    user_id: UUID,
    current_password: str,
    new_password: str,
    current_user: User = Depends(get_user_dependency),
):
    """Change user password."""
    # Check permissions
    if current_user.id != user_id and not current_user.has_permission(UserPermission.USER_UPDATE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    user = user_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Verify current password
    if not user_service.verify_password(user_id, current_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    # Change password
    success = user_service.change_password(user_id, current_password, new_password)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to change password",
        )

    return {"message": "Password changed successfully"}


@router.post("/{user_id}/activate")
async def activate_user(user_id: UUID, current_user: User = Depends(get_user_dependency)):
    """Activate user account."""
    if not current_user.has_permission(UserPermission.USER_UPDATE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    success = user_service.activate_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": "User activated successfully"}


@router.post("/{user_id}/deactivate")
async def deactivate_user(user_id: UUID, current_user: User = Depends(get_user_dependency)):
    """Deactivate user account."""
    if not current_user.has_permission(UserPermission.USER_UPDATE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    success = user_service.deactivate_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": "User deactivated successfully"}


@router.get("/", response_model=List[UserResponse])
async def list_users(
    role: Optional[UserRole] = Query(None, description="Filter by role"),
    active_only: bool = Query(True, description="Show only active users"),
    current_user: User = Depends(get_user_dependency),
):
    """List users with optional filtering."""
    if not current_user.has_permission(UserPermission.USER_READ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    users = user_service.list_users(role=role, active_only=active_only)

    return [_user_to_response(u) for u in users]


@router.post("/{user_id}/roles/{role}")
async def add_user_role(
    user_id: UUID,
    role: UserRole,
    current_user: User = Depends(get_user_dependency),
):
    """Add role to user."""
    if not current_user.has_permission(UserPermission.USER_UPDATE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    user = user_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    updated_user = user_service.add_role(user_id, role)
    if not updated_user:
        raise HTTPException(status_code=400, detail="Failed to add role")

    return {"message": f"Role {role} added to user"}


@router.delete("/{user_id}/roles/{role}")
async def remove_user_role(
    user_id: UUID,
    role: UserRole,
    current_user: User = Depends(get_user_dependency),
):
    """Remove role from user."""
    if not current_user.has_permission(UserPermission.USER_UPDATE):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    user = user_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    updated_user = user_service.remove_role(user_id, role)
    if not updated_user:
        raise HTTPException(status_code=400, detail="Failed to remove role")

    return {"message": f"Role {role} removed from user"}


# Helper functions
def _user_to_response(user: User) -> UserResponse:
    """Convert User model to response model."""
    return UserResponse(
        id=str(user.id),
        email=user.email,
        username=user.username,
        full_name=user.full_name,
        roles=[r.value for r in user.roles],
        permissions=[p.value for p in user.get_permissions()],
        is_active=user.is_active,
        is_verified=user.is_verified,
        created_at=user.created_at.isoformat(),
        last_login_at=user.last_login_at.isoformat() if user.last_login_at else None,
    )
