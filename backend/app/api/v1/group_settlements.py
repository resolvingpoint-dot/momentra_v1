"""Group settlement routes (moment_store runtime, all group moment types)."""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import get_current_user_id
from app.domains.group.settlements.schemas import SettlementCreateRequest, SettlementPatchRequest
from app.domains.group.settlements.service import SettlementService

router = APIRouter(prefix="/group", tags=["group-settlements"])


def _service(db: AsyncSession) -> SettlementService:
    return SettlementService(db)


_BASE = "/moments/{moment_id}/settlements"


@router.get(_BASE + "/preview")
async def settlement_preview(
    moment_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).preview(user_id, moment_id)


@router.get(_BASE)
async def list_settlements(
    moment_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).list_settlements(user_id, moment_id)


@router.post(_BASE, status_code=status.HTTP_201_CREATED)
async def create_settlement(
    moment_id: UUID,
    body: SettlementCreateRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).create(user_id, moment_id, body)


@router.patch(_BASE + "/{settlement_id}")
async def patch_settlement(
    moment_id: UUID,
    settlement_id: str,
    body: SettlementPatchRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).patch(user_id, moment_id, settlement_id, body)


@router.post(_BASE + "/{settlement_id}/mark-settled")
async def mark_settlement_settled(
    moment_id: UUID,
    settlement_id: str,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).mark_settled(user_id, moment_id, settlement_id)


@router.delete(_BASE + "/{settlement_id}")
async def delete_settlement(
    moment_id: UUID,
    settlement_id: str,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).delete(user_id, moment_id, settlement_id)
