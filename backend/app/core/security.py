from __future__ import annotations

from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import settings


def create_session_token(firebase_uid: str) -> str:
    now = datetime.now(timezone.utc)
    expires_in = timedelta(minutes=settings.app_session_expires_minutes)
    payload = {
        "sub": firebase_uid,
        "iat": now,
        "exp": now + expires_in,
        "type": "session",
    }
    return jwt.encode(
        payload,
        settings.effective_session_secret,
        algorithm=settings.session_algorithm,
    )


def decode_session_token(token: str) -> dict:
    return jwt.decode(
        token,
        settings.effective_session_secret,
        algorithms=[settings.session_algorithm],
    )


def get_session_expires_at() -> str:
    return (
        datetime.now(timezone.utc)
        + timedelta(minutes=settings.app_session_expires_minutes)
    ).isoformat()


def access_token_ttl_seconds() -> int:
    """Lifetime, in seconds, of an access token (mobile ``expires_in``)."""
    return settings.app_session_expires_minutes * 60


def create_access_token(firebase_uid: str) -> str:
    """Bearer access token consumed by the mobile clients.

    Uses ``type=session`` so it is accepted by ``get_current_user`` alongside
    the legacy ``/auth/exchange`` session token.
    """
    return create_session_token(firebase_uid)


def create_refresh_token(firebase_uid: str) -> str:
    """Long-lived token used only by ``POST /auth/refresh``."""
    now = datetime.now(timezone.utc)
    expires_in = timedelta(hours=settings.session_expire_hours)
    payload = {
        "sub": firebase_uid,
        "iat": now,
        "exp": now + expires_in,
        "type": "refresh",
    }
    return jwt.encode(
        payload,
        settings.effective_session_secret,
        algorithm=settings.session_algorithm,
    )


_INVITE_TTL_HOURS = 24 * 14


def create_invite_token(
    moment_id: str,
    email: str | None = None,
    *,
    participant_id: str | None = None,
    invite_id: str | None = None,
) -> str:
    """Signed invite token embedding moment (+ optional participant / invite id).

    Encoded into shareable/email invite links; ``POST /invites/{token}/accept``
    decodes it. Persistence of invite rows lives in moment runtime store.
    """
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(moment_id),
        "email": email,
        "iat": now,
        "exp": now + timedelta(hours=_INVITE_TTL_HOURS),
        "type": "invite",
    }
    if participant_id:
        payload["participant_id"] = str(participant_id)
    if invite_id:
        payload["invite_id"] = str(invite_id)
    return jwt.encode(
        payload,
        settings.effective_session_secret,
        algorithm=settings.session_algorithm,
    )


def decode_invite_token(token: str) -> dict:
    payload = jwt.decode(
        token,
        settings.effective_session_secret,
        algorithms=[settings.session_algorithm],
    )
    if payload.get("type") != "invite":
        raise jwt.InvalidTokenError("not an invite token")
    return payload


def invite_expires_at() -> str:
    return (
        datetime.now(timezone.utc) + timedelta(hours=_INVITE_TTL_HOURS)
    ).isoformat()
