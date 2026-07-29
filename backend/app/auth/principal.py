"""Typed authenticated principal for REST, future GraphQL, and workers."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID


@dataclass(frozen=True, slots=True)
class Principal:
    """Authenticated caller shared across transports.

    ``session_id`` / ``device_id`` are optional until access tokens embed them
    or the caller loads them from refresh-session metadata.
    """

    user_id: UUID
    firebase_uid: str
    auth_type: str  # "firebase" | "session"
    session_id: UUID | None = None
    device_id: str | None = None
    auth_strength: str = "password"
    scopes: frozenset[str] = field(default_factory=lambda: frozenset({"momentra:user"}))
    claims: dict[str, Any] = field(default_factory=dict)


def principal_from_auth(
    *,
    user_id: UUID,
    auth_user: dict[str, Any],
    session_id: UUID | None = None,
    device_id: str | None = None,
) -> Principal:
    """Build a Principal from ``get_current_user`` output + resolved user id."""
    payload = auth_user.get("payload") or {}
    auth_type = str(auth_user.get("type") or "session")
    firebase_uid = str(auth_user.get("uid") or payload.get("sub") or "")
    strength = "firebase" if auth_type == "firebase" else "session"
    sid = session_id
    if sid is None:
        raw_sid = payload.get("sid") or payload.get("session_id")
        if raw_sid:
            try:
                sid = UUID(str(raw_sid))
            except ValueError:
                sid = None
    did = device_id or payload.get("device_id") or payload.get("did")
    return Principal(
        user_id=user_id,
        firebase_uid=firebase_uid,
        auth_type=auth_type,
        session_id=sid,
        device_id=str(did) if did else None,
        auth_strength=strength,
        scopes=frozenset({"momentra:user"}),
        claims=dict(payload) if isinstance(payload, dict) else {},
    )
