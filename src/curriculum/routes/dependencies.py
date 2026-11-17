"""Shared dependencies for API routes."""

from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from curriculum.config import settings
from curriculum.core.user import User
from curriculum.users.user import UserService

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/users/login")

# Service instance
user_service = UserService()


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Get current user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
            options={"require": ["exp", "sub", "token_type"]},
        )
        user_id = payload.get("sub")
        if not isinstance(user_id, str) or payload.get("token_type") != "access":
            raise credentials_exception
        parsed_id = UUID(user_id)
    except (jwt.InvalidTokenError, ValueError):
        raise credentials_exception

    user = user_service.get_user(parsed_id)
    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
        )

    return user
