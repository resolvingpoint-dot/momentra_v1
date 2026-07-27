"""Business Active API — per-moment projection reads + activity CRUD.

Life/memory routes live at /business/life and /business/memory (plan contract).
Mounted under /api/v1 in main.py. Reuses same auth deps as existing business_app.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import get_current_user_id
from app.domains.business.active_service import BusinessActiveService
from app.domains.business.activity.schemas import CreateActivityRequest, PatchActivityRequest

router = APIRouter(tags=["business-active"])
active_router = APIRouter(prefix="/business/active")


def _svc(db: AsyncSession) -> BusinessActiveService:
    return BusinessActiveService(db)


@active_router.get("/{moment_id}/pulse")
async def get_pulse(
    moment_id: UUID,
    force_refresh: bool = Query(False),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _svc(db).get_pulse(user_id, moment_id, force_refresh=force_refresh)


@active_router.get("/{moment_id}/moments")
async def get_moments(
    moment_id: UUID,
    force_refresh: bool = Query(False),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _svc(db).get_moments(user_id, moment_id, force_refresh=force_refresh)


@active_router.get("/{moment_id}/quick-add")
async def get_quick_add(
    moment_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _svc(db).get_quick_add(user_id, moment_id)


@active_router.get("/{moment_id}/action-catalog")
async def get_action_catalog(
    moment_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Business Action Center catalog (categories + actions + members)."""
    return await _svc(db).get_action_catalog(user_id, moment_id)


@active_router.get("/{moment_id}/actions/{action_key}/renderer")
async def get_renderer_metadata(
    moment_id: UUID,
    action_key: str,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Field schema + validation for a dedicated Action Center renderer."""
    return await _svc(db).get_renderer_metadata(user_id, moment_id, action_key)


@active_router.get("/{moment_id}/activity")
async def list_activity(
    moment_id: UUID,
    action: str | None = Query(None, description="Comma-separated action_type filter"),
    member: UUID | None = Query(None, description="Filter by created_by member user id"),
    status: Literal["all", "active", "voided"] = Query("active"),
    date_from: datetime | None = Query(None, alias="from"),
    date_to: datetime | None = Query(None, alias="to"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort: Literal["newest", "oldest"] = Query("newest"),
    search: str | None = Query(None, alias="q"),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Server-filtered, paginated activity list. Clients forward query params only."""
    return await _svc(db).list_activity(
        user_id,
        moment_id,
        action=action,
        member_id=member,
        status_filter=status,
        date_from=date_from,
        date_to=date_to,
        search=search,
        sort=sort,
        page=page,
        page_size=page_size,
    )


@active_router.post("/{moment_id}/activity", status_code=201)
async def create_activity(
    moment_id: UUID,
    body: CreateActivityRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    result = await _svc(db).create_activity(
        user_id,
        moment_id,
        body.action_type,
        body.title,
        subtitle=body.subtitle,
        payload=body.payload,
        client_request_id=body.client_request_id,
        source=body.source,
    )
    await db.commit()
    return result


@active_router.get("/{moment_id}/activity/{event_id}")
async def get_activity(
    moment_id: UUID,
    event_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _svc(db).get_activity(user_id, moment_id, event_id)


@active_router.patch("/{moment_id}/activity/{event_id}")
async def patch_activity(
    moment_id: UUID,
    event_id: UUID,
    body: PatchActivityRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    patch_data: dict[str, Any] = body.model_dump(mode="json", exclude_none=True)
    result = await _svc(db).patch_activity(user_id, moment_id, event_id, patch_data)
    await db.commit()
    return result


@active_router.delete("/{moment_id}/activity/{event_id}")
async def delete_activity(
    moment_id: UUID,
    event_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    result = await _svc(db).delete_activity(user_id, moment_id, event_id)
    await db.commit()
    return result


@router.get("/business/life")
async def get_life(
    force_refresh: bool = Query(False),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _svc(db).get_life(user_id, force_refresh=force_refresh)


@router.get("/business/memory")
async def get_memory(
    force_refresh: bool = Query(False),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _svc(db).get_memory(user_id, force_refresh=force_refresh)


router.include_router(active_router)
