"""Group ``shared-*`` setup router (mobile contract).

Dedicated setup surface the Android client calls (no mock fallback) for the three
shared-moment categories: ``shared-experience``, ``shared-purchase`` and
``shared-living``. Each exposes: profiles, draft create, setup state, draft save,
preview and activate. Registered before the legacy ``group.router``.
"""
from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Body, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import get_current_user_id
from app.domains.group import shared_catalog as cat
from app.domains.group import shared_schemas as s
from app.domains.group.shared_service import SharedGroupService

router = APIRouter(prefix="/group", tags=["group"])


def _service(db: AsyncSession) -> SharedGroupService:
    return SharedGroupService(db)


# --------------------------------------------------------------------------- #
# shared-experience
# --------------------------------------------------------------------------- #
@router.get("/shared-experience/profiles")
async def experience_profiles(
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).profiles(cat.EXPERIENCE)


@router.post("/shared-experience/moments", status_code=status.HTTP_201_CREATED)
async def experience_create(
    body: s.ExperienceDraftCreateRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).create_draft(user_id, cat.EXPERIENCE, body.experience_profile)


@router.get("/shared-experience/moments/{moment_id}/setup")
async def experience_setup(
    moment_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).get_setup(user_id, cat.EXPERIENCE, moment_id)


@router.put("/shared-experience/moments/{moment_id}/setup/draft")
async def experience_save_draft(
    moment_id: UUID,
    body: dict[str, Any] = Body(default={}),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).save_draft(user_id, cat.EXPERIENCE, moment_id, body)


@router.get("/shared-experience/moments/{moment_id}/setup/preview")
async def experience_preview(
    moment_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).preview(user_id, cat.EXPERIENCE, moment_id)


@router.post("/shared-experience/moments/{moment_id}/setup/activate")
async def experience_activate(
    moment_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).activate(user_id, cat.EXPERIENCE, moment_id)


# --------------------------------------------------------------------------- #
# shared-purchase
# --------------------------------------------------------------------------- #
@router.get("/shared-purchase/profiles")
async def purchase_profiles(
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).profiles(cat.PURCHASE)


@router.post("/shared-purchase/moments", status_code=status.HTTP_201_CREATED)
async def purchase_create(
    body: s.PurchaseDraftCreateRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).create_draft(user_id, cat.PURCHASE, body.purchase_profile)


@router.get("/shared-purchase/moments/{moment_id}/setup")
async def purchase_setup(
    moment_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).get_setup(user_id, cat.PURCHASE, moment_id)


@router.put("/shared-purchase/moments/{moment_id}/setup/draft")
async def purchase_save_draft(
    moment_id: UUID,
    body: dict[str, Any] = Body(default={}),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).save_draft(user_id, cat.PURCHASE, moment_id, body)


@router.get("/shared-purchase/moments/{moment_id}/setup/preview")
async def purchase_preview(
    moment_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).preview(user_id, cat.PURCHASE, moment_id)


@router.post("/shared-purchase/moments/{moment_id}/setup/activate")
async def purchase_activate(
    moment_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).activate(user_id, cat.PURCHASE, moment_id)


# --------------------------------------------------------------------------- #
# shared-living
# --------------------------------------------------------------------------- #
@router.get("/shared-living/profiles")
async def living_profiles(
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).profiles(cat.LIVING)


@router.post("/shared-living/moments", status_code=status.HTTP_201_CREATED)
async def living_create(
    body: s.LivingDraftCreateRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).create_draft(user_id, cat.LIVING, body.living_type)


@router.get("/shared-living/moments/{moment_id}/setup")
async def living_setup(
    moment_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).get_setup(user_id, cat.LIVING, moment_id)


@router.put("/shared-living/moments/{moment_id}/setup/draft")
async def living_save_draft(
    moment_id: UUID,
    body: dict[str, Any] = Body(default={}),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).save_draft(user_id, cat.LIVING, moment_id, body)


@router.get("/shared-living/moments/{moment_id}/setup/preview")
async def living_preview(
    moment_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).preview(user_id, cat.LIVING, moment_id)


@router.post("/shared-living/moments/{moment_id}/setup/activate")
async def living_activate(
    moment_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).activate(user_id, cat.LIVING, moment_id)
