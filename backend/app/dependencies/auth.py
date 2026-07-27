from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.request_context import user_id_var
from app.core.firebase import verify_firebase_token
from app.core.security import decode_session_token
from app.domains.users.service import UserService

logger = logging.getLogger(__name__)

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
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
        return {"type": "firebase", "uid": decoded["uid"], "payload": decoded}
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

    return {
        "type": "session",
        "uid": decoded["sub"],
        "payload": decoded,
    }


async def get_current_user_id(
    auth_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UUID:
    """Resolve the authenticated caller to their internal Momentra user id.

    Reused by domain routers that scope data by owner. Depends on ``get_db`` so
    it shares the request-scoped session (and transaction) with the endpoint.
    """
    user = await UserService(db).get_user(auth_user["uid"])
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user_id_var.set(str(user.id))
    return user.id
