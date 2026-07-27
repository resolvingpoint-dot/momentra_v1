from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.firebase import verify_firebase_token
from app.core.security import (
    access_token_ttl_seconds,
    create_access_token,
    create_refresh_token,
    create_session_token,
    decode_session_token,
    get_session_expires_at,
)
from app.dependencies.auth import get_current_user
from app.domains.module_states.service import ModuleStateService
from app.domains.preferences.service import UserPreferenceService
from app.domains.users.models import UserModel
from app.domains.users.schemas import (
    FirebaseExchangeRequest,
    FirebaseExchangeResponse,
    RefreshTokenRequest,
    TokenResponse,
    UserResponse,
)
from app.domains.users.service import UserService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])


class TestLoginRequest(BaseModel):
    """Deterministic identity for acceptance tests only."""

    firebase_uid: str = Field(min_length=3, max_length=128)
    email: str | None = None
    display_name: str | None = None


def _issue_tokens(firebase_uid: str) -> TokenResponse:
    return TokenResponse(
        access_token=create_access_token(firebase_uid),
        refresh_token=create_refresh_token(firebase_uid),
        token_type="bearer",
        expires_in=access_token_ttl_seconds(),
    )


async def _provision_user(db: AsyncSession, firebase_payload: dict) -> UserModel:
    user_service = UserService(db)
    user = await user_service.sync_user(firebase_payload)
    await UserPreferenceService(db).get_or_create(user.id)
    await ModuleStateService(db).ensure_defaults(user.id)
    return user


@router.post("/firebase/exchange")
async def firebase_exchange(
    body: FirebaseExchangeRequest,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Exchange a Firebase ID token (in the body) for app access/refresh tokens.

    This is the mobile clients' primary login endpoint; the token arrives in the
    request body (no ``Authorization`` header).
    """
    if not body.id_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing id_token",
        )
    try:
        decoded = verify_firebase_token(body.id_token)
    except Exception as exc:  # noqa: BLE001 - surfaced as 401 to the client
        logger.info("Firebase token verification failed: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Firebase token",
        ) from exc

    user = await _provision_user(db, decoded)
    response = FirebaseExchangeResponse(
        user=UserResponse.model_validate(user),
        tokens=_issue_tokens(user.firebase_uid),
    )
    return response.model_dump(mode="json")


@router.post("/refresh")
async def refresh_tokens(
    body: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
) -> dict:
    try:
        decoded = decode_session_token(body.refresh_token)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        ) from exc
    if decoded.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not a refresh token",
        )
    firebase_uid = decoded.get("sub")
    user = await UserService(db).get_user(firebase_uid)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return _issue_tokens(firebase_uid).model_dump(mode="json")


@router.post("/logout")
async def logout(
    _auth_user: dict[str, Any] = Depends(get_current_user),
) -> dict:
    """Stateless JWT logout — the client discards its stored tokens."""
    return {}


@router.post("/sync")
async def auth_sync(
    auth_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    if auth_user["type"] != "firebase":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sync requires a Firebase ID token",
        )
    user_service = UserService(db)
    user = await user_service.sync_user(auth_user["payload"])
    logger.info("Synced user: id=%s firebase_uid=%s", user.id, user.firebase_uid)

    pref_service = UserPreferenceService(db)
    pref = await pref_service.get_or_create(user.id)
    logger.info("User preference: id=%s user_id=%s", pref.id, pref.user_id)

    module_service = ModuleStateService(db)
    await module_service.ensure_defaults(user.id)

    return {
        "ok": True,
        "user": UserResponse.model_validate(user).model_dump(mode="json"),
        "preferences": {
            "selected_context": pref.selected_context,
        },
    }


@router.post("/exchange")
async def auth_exchange(
    auth_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    if auth_user["type"] != "firebase":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Exchange requires a Firebase ID token",
        )
    user_service = UserService(db)
    user = await user_service.sync_user(auth_user["payload"])

    pref_service = UserPreferenceService(db)
    await pref_service.get_or_create(user.id)

    module_service = ModuleStateService(db)
    await module_service.ensure_defaults(user.id)

    session_token = create_session_token(user.firebase_uid)
    expires_at = get_session_expires_at()
    return {
        "app_session_token": session_token,
        "token_type": "bearer",
        "expires_at": expires_at,
        "user": UserResponse.model_validate(user).model_dump(mode="json"),
    }


@router.post("/test/login", response_model=FirebaseExchangeResponse)
async def test_login(
    body: TestLoginRequest,
    db: AsyncSession = Depends(get_db),
) -> FirebaseExchangeResponse:
    """Mint a normal session for a synthetic Firebase UID (acceptance only).

    Requires ``ALLOW_TEST_AUTH=true`` and ``DEBUG=true``. Never mounts behavior
    in production; settings validator rejects ALLOW_TEST_AUTH when DEBUG=false.
    """
    if not (settings.debug and settings.allow_test_auth):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found",
        )
    if not body.firebase_uid.startswith("test:"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Test firebase_uid must start with 'test:'",
        )
    payload = {
        "uid": body.firebase_uid,
        "email": body.email or f"{body.firebase_uid.replace(':', '_')}@test.momentra.local",
        "name": body.display_name or body.firebase_uid,
    }
    user = await _provision_user(db, payload)
    tokens = _issue_tokens(user.firebase_uid)
    return FirebaseExchangeResponse(
        user=UserResponse.model_validate(user),
        tokens=tokens,
    )
