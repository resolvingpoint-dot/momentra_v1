from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import get_current_user
from app.domains.app_bootstrap.service import AppBootstrapService
from app.domains.preferences.schemas import PreferenceUpdateSchema, UserPreferenceSchema
from app.domains.preferences.service import UserPreferenceService
from app.domains.users.service import UserService

router = APIRouter(prefix="/app", tags=["app"])


@router.get("/bootstrap")
async def get_bootstrap(
    auth_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    service = AppBootstrapService(db)
    bootstrap = await service.get_bootstrap(auth_user["uid"])
    return bootstrap.model_dump(mode="json")


@router.patch("/preferences")
async def update_preferences(
    body: PreferenceUpdateSchema,
    auth_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    user_service = UserService(db)
    user = await user_service.get_user(auth_user["uid"])
    if user is None:
        return {"ok": False, "error": "User not found"}

    pref_service = UserPreferenceService(db)
    updated = await pref_service.update_preferences_and_notify(user.id, body)
    await db.commit()

    cache_service = AppBootstrapService(db)
    await cache_service.invalidate_cache(user.id)

    return UserPreferenceSchema.model_validate(updated).model_dump(mode="json")
