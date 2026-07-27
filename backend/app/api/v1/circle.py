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
from app.domains.circle.api_schemas import (
    CircleAnalyticsResponse,
    CircleReadResponse,
    CircleRefreshResponse,
    CircleSummaryResponse,
)
from app.domains.circle.circle_service import CircleService
from app.domains.module_states.service import ModuleStateService
from app.domains.users.service import UserService

router = APIRouter(prefix="/circle", tags=["circle"])


@router.get("/home", summary="Circle context home / empty-state bootstrap")
async def circle_home(
    auth_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    user_service = UserService(db)
    user = await user_service.get_user(auth_user["uid"])
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    summary = await CircleService(db).summary(user.id)
    participant_count = summary.participant_count
    state = "EMPTY" if participant_count == 0 else "ACTIVE"
    ms = await ModuleStateService(db).get_state(user.id, "CIRCLE")
    if ms is not None and ms.state:
        # Prefer live participant count for EMPTY/ACTIVE; keep module state only when non-empty mismatch.
        if participant_count == 0:
            state = "EMPTY"
        elif ms.state.upper() in {"SETUP", "DRAFT"}:
            state = ms.state
        else:
            state = "ACTIVE"
    return {
        "context": "CIRCLE",
        "state": state,
        "counts": {
            "participants": participant_count,
            "active_participants": summary.active_participant_count,
            "suggestions": summary.suggestion_count,
        },
        "empty_state_override": EMPTY_STATE_OVERRIDES.get("CIRCLE"),
    }


@router.post(
    "/refresh",
    response_model=CircleRefreshResponse,
    summary="Recompute the circle via sp_refresh_circle",
    description="Runs the existing SQL procedure sp_refresh_circle(user_id), which "
    "rebuilds circle_participants, circle_participant_stats and circle_suggestions.",
)
async def refresh_circle(
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> CircleRefreshResponse:
    return await CircleService(db).refresh(user_id)


@router.get(
    "/read",
    response_model=CircleReadResponse,
    summary="Read the circle (participants + suggestions) from snapshot tables",
)
async def read_circle(
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> CircleReadResponse:
    return await CircleService(db).read(user_id)


@router.get(
    "/analytics",
    response_model=CircleAnalyticsResponse,
    summary="Circle analytics (counts + ranked participants) from snapshot tables",
)
async def circle_analytics(
    top_limit: int = Query(default=10, ge=1, le=50),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> CircleAnalyticsResponse:
    return await CircleService(db).analytics(user_id, top_limit=top_limit)


@router.get(
    "/summary",
    response_model=CircleSummaryResponse,
    summary="Compact circle summary from snapshot tables",
)
async def circle_summary(
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> CircleSummaryResponse:
    return await CircleService(db).summary(user_id)
