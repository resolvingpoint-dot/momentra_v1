from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.firebase import verify_firebase_token
from app.core.security import (
    access_token_ttl_seconds,
    create_access_token,
    create_session_token,
    get_session_expires_at,
)
from app.dependencies.auth import get_current_user
from app.domains.auth.refresh_sessions import RefreshSessionError, RefreshSessionService
from app.domains.module_states.service import ModuleStateService
from app.domains.preferences.service import UserPreferenceService
from app.domains.users.models import UserModel
from app.domains.users.schemas import (
    FirebaseExchangeRequest,
    FirebaseExchangeResponse,
    LogoutRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserResponse,
)
from app.domains.users.service import UserService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])

REFRESH_COOKIE_NAME = "momentra_refresh"
REFRESH_COOKIE_PATH = "/api/v1/auth"
CLIENT_HEADER = "X-Momentra-Client"
WEB_CLIENT_VALUE = "web"


class TestLoginRequest(BaseModel):
    """Deterministic identity for acceptance tests only."""

    firebase_uid: str = Field(min_length=3, max_length=128)
    email: str | None = None
    display_name: str | None = None


def _client_ip(request: Request | None) -> str | None:
    if request is None:
        return None
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()[:64]
    if request.client:
        return (request.client.host or "")[:64] or None
    return None


def _is_web_client(request: Request) -> bool:
    return request.headers.get(CLIENT_HEADER, "").strip().lower() == WEB_CLIENT_VALUE


def _require_web_csrf_when_cookie(request: Request) -> None:
    """Cookie-bearing auth routes need a custom header (CSRF mitigation)."""
    if request.cookies.get(REFRESH_COOKIE_NAME) and not _is_web_client(request):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Missing or invalid client header for cookie auth",
        )


def _set_refresh_cookie(response: Response, token: str) -> None:
    max_age = settings.session_expire_hours * 3600
    # Cross-site web (app on momentra.tech → API on api.mallaapp.org) needs
    # SameSite=None; Secure. Local DEBUG uses Lax so http://localhost works.
    if settings.debug:
        response.set_cookie(
            key=REFRESH_COOKIE_NAME,
            value=token,
            max_age=max_age,
            httponly=True,
            secure=False,
            samesite="lax",
            path=REFRESH_COOKIE_PATH,
        )
    else:
        response.set_cookie(
            key=REFRESH_COOKIE_NAME,
            value=token,
            max_age=max_age,
            httponly=True,
            secure=True,
            samesite="none",
            path=REFRESH_COOKIE_PATH,
        )


def _clear_refresh_cookie(response: Response) -> None:
    response.delete_cookie(
        key=REFRESH_COOKIE_NAME,
        path=REFRESH_COOKIE_PATH,
        secure=not settings.debug,
        httponly=True,
        samesite="lax" if settings.debug else "none",
    )


def _resolve_refresh_plaintext(
    request: Request,
    body_token: str | None,
) -> str | None:
    if body_token and body_token.strip():
        return body_token.strip()
    cookie = request.cookies.get(REFRESH_COOKIE_NAME)
    if cookie and cookie.strip():
        return cookie.strip()
    return None


async def _issue_tokens(
    db: AsyncSession,
    user: UserModel,
    request: Request | None = None,
) -> TokenResponse:
    service = RefreshSessionService(db)
    plaintext, _session = await service.create_session(
        user_id=user.id,
        firebase_uid=user.firebase_uid,
        user_agent=request.headers.get("user-agent") if request else None,
        ip=_client_ip(request),
    )
    return TokenResponse(
        access_token=create_access_token(user.firebase_uid),
        refresh_token=plaintext,
        token_type="bearer",
        expires_in=access_token_ttl_seconds(),
    )


def _json_with_optional_refresh_cookie(
    request: Request,
    payload: dict,
    refresh_token: str,
) -> JSONResponse:
    response = JSONResponse(payload)
    if _is_web_client(request):
        _set_refresh_cookie(response, refresh_token)
    return response


async def _provision_user(db: AsyncSession, firebase_payload: dict) -> UserModel:
    user_service = UserService(db)
    user = await user_service.sync_user(firebase_payload)
    await UserPreferenceService(db).get_or_create(user.id)
    await ModuleStateService(db).ensure_defaults(user.id)
    return user


@router.post("/firebase/exchange")
async def firebase_exchange(
    body: FirebaseExchangeRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    """Exchange a Firebase ID token (in the body) for app access/refresh tokens.

    This is the mobile clients' primary login endpoint; the token arrives in the
    request body (no ``Authorization`` header). Web clients send
    ``X-Momentra-Client: web`` to receive an HttpOnly refresh cookie.
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
    tokens = await _issue_tokens(db, user, request)
    response = FirebaseExchangeResponse(
        user=UserResponse.model_validate(user),
        tokens=tokens,
    )
    return _json_with_optional_refresh_cookie(
        request,
        response.model_dump(mode="json"),
        tokens.refresh_token,
    )


@router.post("/refresh")
async def refresh_tokens(
    request: Request,
    body: RefreshTokenRequest | None = None,
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    _require_web_csrf_when_cookie(request)
    plaintext = _resolve_refresh_plaintext(
        request,
        body.refresh_token if body else None,
    )
    if not plaintext:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing refresh token",
        )

    service = RefreshSessionService(db)
    try:
        new_plaintext, session = await service.rotate(
            plaintext,
            user_agent=request.headers.get("user-agent"),
            ip=_client_ip(request),
        )
    except RefreshSessionError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        ) from exc

    tokens = TokenResponse(
        access_token=create_access_token(session.firebase_uid),
        refresh_token=new_plaintext,
        token_type="bearer",
        expires_in=access_token_ttl_seconds(),
    )
    return _json_with_optional_refresh_cookie(
        request,
        tokens.model_dump(mode="json"),
        new_plaintext,
    )


@router.post("/logout")
async def logout(
    request: Request,
    body: LogoutRequest | None = None,
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    """Revoke the current refresh session (body or cookie) and clear cookie."""
    _require_web_csrf_when_cookie(request)
    plaintext = _resolve_refresh_plaintext(
        request,
        body.refresh_token if body else None,
    )
    if plaintext:
        await RefreshSessionService(db).revoke_token(plaintext)

    response = JSONResponse({})
    _clear_refresh_cookie(response)
    return response


@router.post("/logout-all")
async def logout_all(
    request: Request,
    auth_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Revoke every refresh session for the authenticated user (all devices).

    Call this from settings “sign out all devices”, or after a password /
    security change on the Firebase side.
    """
    firebase_uid = auth_user.get("uid")
    if not firebase_uid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session",
        )
    user = await UserService(db).get_user(firebase_uid)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    revoked = await RefreshSessionService(db).revoke_all_for_user(user.id)
    # Also clear cookie if present (web).
    response_payload = {"revoked": revoked}
    # Prefer JSONResponse so we can clear cookie when web client hits this.
    if _is_web_client(request) or request.cookies.get(REFRESH_COOKIE_NAME):
        response = JSONResponse(response_payload)
        _clear_refresh_cookie(response)
        return response  # type: ignore[return-value]
    return response_payload


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
    request: Request,
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
    tokens = await _issue_tokens(db, user, request)
    return FirebaseExchangeResponse(
        user=UserResponse.model_validate(user),
        tokens=tokens,
    )
