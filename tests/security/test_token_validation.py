"""Regression coverage for signed API tokens."""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from curriculum.config import settings
from curriculum.routes.dependencies import get_current_user, user_service
from curriculum.routes.main import app
from curriculum.users.user import AuthenticationService


@pytest.fixture
def registered_user(monkeypatch):
    for name in ("_users", "_email_index", "_username_index"):
        monkeypatch.setattr(user_service, name, {})
    user, error = user_service.create_user(
        email=f"{uuid4()}@example.com",
        username=f"user{uuid4().hex[:12]}",
        full_name="Token Test",
        password="TokenTest123!",
    )
    assert error == ""
    assert user is not None
    return user


@pytest.mark.asyncio
async def test_signed_access_token_reaches_api(registered_user):
    auth = AuthenticationService(user_service)
    token = auth.create_access_token(registered_user.id)
    assert (await get_current_user(token)).id == registered_user.id
    assert auth.verify_token(token) == registered_user.id


@pytest.mark.asyncio
async def test_expired_access_token_rejected(registered_user):
    auth = AuthenticationService(user_service)
    token = auth.create_access_token(registered_user.id, timedelta(seconds=-1))
    assert auth.verify_token(token) is None
    with pytest.raises(HTTPException) as error:
        await get_current_user(token)
    assert error.value.status_code == 401


@pytest.mark.asyncio
@pytest.mark.parametrize("kind", ["tampered", "refresh", "invalid-subject", "missing-expiry"])
async def test_invalid_access_token_rejected(registered_user, kind):
    auth = AuthenticationService(user_service)
    if kind == "refresh":
        token = auth.create_refresh_token(registered_user.id)
    elif kind == "tampered":
        parts = auth.create_access_token(registered_user.id).split(".")
        parts[1] = parts[1][::-1]
        token = ".".join(parts)
    else:
        token = jwt.encode(
            (
                {"sub": str(registered_user.id), "token_type": "access"}
                if kind == "missing-expiry"
                else {
                    "sub": "invalid-uuid",
                    "token_type": "access",
                    "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
                }
            ),
            settings.secret_key,
            algorithm=settings.algorithm,
        )
    assert auth.verify_token(token) is None
    with pytest.raises(HTTPException) as error:
        await get_current_user(token)
    assert error.value.status_code == 401


@pytest.mark.parametrize(
    "kind, expected",
    [
        ("refresh", 200),
        ("access", 401),
        ("expired", 401),
        ("missing-expiry", 401),
    ],
)
def test_refresh_endpoint_enforces_token_purpose_and_expiry(registered_user, kind, expected):
    client = TestClient(app)
    response = client.post(
        "/api/v1/users/login",
        json={
            "username_or_email": registered_user.username,
            "password": "TokenTest123!",
        },
    )
    assert response.status_code == 200
    tokens = response.json()
    token = tokens["refresh_token"] if kind == "refresh" else tokens["access_token"]
    if kind in ("expired", "missing-expiry"):
        claims = {"sub": str(registered_user.id), "token_type": "refresh"}
        if kind == "expired":
            claims["exp"] = (datetime.now(timezone.utc) - timedelta(minutes=1)).timestamp()
        token = jwt.encode(claims, settings.secret_key, algorithm=settings.algorithm)
    refreshed = client.post("/api/v1/users/refresh", params={"refresh_token": token})
    assert refreshed.status_code == expected
    if expected == 200:
        auth = AuthenticationService(user_service)
        assert auth.verify_token(refreshed.json()["access_token"]) == registered_user.id
        assert auth.verify_refresh_token(refreshed.json()["refresh_token"]) == registered_user.id
