from __future__ import annotations

import logging
import time
from typing import Any
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.request_context import user_id_var
from app.core.firebase import verify_firebase_token
from app.core.security import decode_session_token
from app.domains.users.service import UserService

logger = logging.getLogger(__name__)

bearer_scheme = HTTPBearer(auto_error=False)

# Short-lived firebase_uid → internal user_id (membership not cached).
_UID_CACHE_TTL_SEC = 30.0
_uid_to_user_id: dict[str, tuple[UUID, float]] = {}


async def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict[str, Any]:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
        )

    token = credentials.credentials
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is empty",
        )

    # Try Firebase ID token first
    try:
        decoded = verify_firebase_token(token)
        uid = decoded["uid"]
        request.state.user_uid = uid
        return {"type": "firebase", "uid": uid, "payload": decoded}
    except Exception:
        pass

    # Fallback to session token
    try:
        decoded = decode_session_token(token)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        ) from exc

    # Refresh tokens are only valid at POST /auth/refresh, never as bearer auth.
    if decoded.get("type") == "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token cannot be used for authentication",
        )

    uid = decoded["sub"]
    request.state.user_uid = uid
    return {
        "type": "session",
        "uid": uid,
        "payload": decoded,
    }


async def get_current_user_id(
    request: Request,
    auth_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UUID:
    """Resolve the authenticated caller to their internal Momentra user id.

    Reused by domain routers that scope data by owner. Depends on ``get_db`` so
    it shares the request-scoped session (and transaction) with the endpoint.
    """
    uid = auth_user["uid"]
    now = time.monotonic()
    cached = _uid_to_user_id.get(uid)
    if cached and (now - cached[1]) < _UID_CACHE_TTL_SEC:
        user_id = cached[0]
        user_id_var.set(str(user_id))
        request.state.user_id = str(user_id)
        request.state.user_uid = uid
        return user_id

    user = await UserService(db).get_user(uid)
    if user is None:
        _uid_to_user_id.pop(uid, None)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    _uid_to_user_id[uid] = (user.id, now)
    user_id_var.set(str(user.id))
    request.state.user_id = str(user.id)
    request.state.user_uid = uid
    return user.id
