from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.domains.app_bootstrap.empty_state_config import (
    EMPTY_STATE_OVERRIDES,
)
from app.domains.module_states.service import ModuleStateService
from app.domains.users.service import UserService

router = APIRouter(prefix="/memory", tags=["memory"])


@router.get("/home")
async def memory_home(
    auth_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    user_service = UserService(db)
    user = await user_service.get_user(auth_user["uid"])
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    module_service = ModuleStateService(db)
    ms = await module_service.get_state(user.id, "MEMORY")
    state = ms.state if ms else "EMPTY"

    return {
        "module": "MEMORY",
        "state": state,
        "counts": {"memories": 0},
        "empty_state_override": EMPTY_STATE_OVERRIDES.get("MEMORY"),
    }
