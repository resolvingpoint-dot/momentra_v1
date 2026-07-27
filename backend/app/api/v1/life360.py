from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import get_current_user, get_current_user_id
from app.domains.app_bootstrap.empty_state_config import (
    EMPTY_STATE_OVERRIDES,
)
from app.domains.life360.api_schemas import (
    Life360AnalyticsResponse,
    Life360RefreshResponse,
    Life360SummaryResponse,
)
from app.domains.life360.life360_service import Life360Service
from app.domains.life360.schemas import Life360SnapshotsSchema
from app.domains.users.service import UserService

router = APIRouter(prefix="/life360", tags=["life360"])


@router.get("/home", summary="Life360 module home / empty-state bootstrap")
async def life360_home(
    auth_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    user_service = UserService(db)
    user = await user_service.get_user(auth_user["uid"])
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    home = await Life360Service(db).home(user.id)
    return {
        "module": "LIFE360",
        "state": home["state"],
        "counts": home["counts"],
        "empty_state_override": EMPTY_STATE_OVERRIDES.get("LIFE360"),
    }


@router.post(
    "/refresh",
    response_model=Life360RefreshResponse,
    summary="Recompute the Life360 snapshot via sp_refresh_life360_snapshots",
    description="Runs the existing SQL procedure sp_refresh_life360_snapshots(user_id), "
    "which upserts today's row in life360_snapshots from the personal/group/business snapshots.",
)
async def refresh_life360(
    force: bool = Query(default=False),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> Life360RefreshResponse:
    return await Life360Service(db).refresh(user_id, force=force)


@router.get(
    "/read",
    response_model=Life360SnapshotsSchema,
    summary="Read the latest Life360 snapshot",
)
async def read_life360(
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> Life360SnapshotsSchema:
    return await Life360Service(db).read(user_id)


@router.get(
    "/analytics",
    response_model=Life360AnalyticsResponse,
    summary="Life360 analytics (dimensions, energy, momentum, trend) from the snapshot",
)
async def life360_analytics(
    trend_limit: int = Query(default=12, ge=1, le=60),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> Life360AnalyticsResponse:
    return await Life360Service(db).analytics(user_id, trend_limit=trend_limit)


@router.get(
    "/summary",
    response_model=Life360SummaryResponse,
    summary="Compact Life360 summary from the latest snapshot",
)
async def life360_summary(
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> Life360SummaryResponse:
    return await Life360Service(db).summary(user_id)
