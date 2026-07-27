from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.domains.app_bootstrap.empty_state_config import (
    EMPTY_STATE_OVERRIDES,
)
from app.domains.moments.service import MomentService
from app.domains.module_states.service import ModuleStateService
from app.domains.users.service import UserService

router = APIRouter(prefix="/my-money", tags=["my-money"])


@router.get("/home")
async def my_money_home(
    auth_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    user_service = UserService(db)
    user = await user_service.get_user(auth_user["uid"])
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    moment_service = MomentService(db)
    count = await moment_service.count_by_context_type(user.id, "MY_MONEY")

    module_service = ModuleStateService(db)
    ms = await module_service.get_state(user.id, "MY_MONEY")
    state = ms.state if ms else "EMPTY"

    primary_cta = (
        {"label": "Create your first moment", "action": "CREATE_PERSONAL_MOMENT"}
        if state == "EMPTY"
        else {"label": "Add a moment", "action": "CREATE_PERSONAL_MOMENT"}
    )

    return {
        "context": "MY_MONEY",
        "state": state,
        "counts": {"moments": count},
        "empty_state_override": EMPTY_STATE_OVERRIDES.get("MY_MONEY"),
        "primary_cta": primary_cta,
    }
