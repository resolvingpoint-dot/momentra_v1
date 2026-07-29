"""FastAPI dependencies for typed Principal."""
from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import Depends, Request

from app.auth.principal import Principal, principal_from_auth
from app.dependencies.auth import get_current_user, get_current_user_id


async def get_current_principal(
    request: Request,
    auth_user: dict[str, Any] = Depends(get_current_user),
    user_id: UUID = Depends(get_current_user_id),
) -> Principal:
    """Resolve the authenticated caller to a typed Principal.

    Existing routes using ``get_current_user_id`` are unchanged. New code and
    AuthZ call sites should prefer this dependency.
    """
    firebase_uid = str(auth_user.get("uid") or "")
    if firebase_uid:
        request.state.user_uid = firebase_uid
    request.state.user_id = str(user_id)

    principal = principal_from_auth(user_id=user_id, auth_user=auth_user)
    request.state.principal = principal
    return principal
