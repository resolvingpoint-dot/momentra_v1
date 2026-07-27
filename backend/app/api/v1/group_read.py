"""shared-purchase & shared-living read + quick-add router (mobile contract).

Live-hub / pulse / moments-view / quick-add hub + per-module quick-add context
(GET) and create (POST) endpoints for the two shared categories. Create
endpoints accept a lenient body and acknowledge (the client ignores the body).
Registered before the legacy ``group.router``.
"""
from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Body, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.dependencies.auth import get_current_user_id
from app.domains.group.read_service import GroupReadService

router = APIRouter(prefix="/group", tags=["group"])


def _service(db: AsyncSession) -> GroupReadService:
    return GroupReadService(db)


def _ack() -> dict:
    return {"status": "ok"}


# =========================================================================== #
# shared-purchase
# =========================================================================== #
_PP = "/shared-purchase/moments/{moment_id}"


@router.get(_PP + "/live-hub")
async def purchase_live_hub(moment_id: UUID, user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _service(db).purchase_live_hub(user_id, moment_id)


@router.get(_PP + "/pulse")
async def purchase_pulse(
    moment_id: UUID,
    force_refresh: bool = Query(False),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).purchase_pulse(user_id, moment_id, force_refresh=force_refresh)


@router.get(_PP + "/moments-view")
async def purchase_moments_view(
    moment_id: UUID,
    force_refresh: bool = Query(False),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).purchase_moments_view(
        user_id, moment_id, force_refresh=force_refresh
    )


@router.get(_PP + "/quick-add/hub")
async def purchase_quick_add_hub(moment_id: UUID, user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _service(db).purchase_quick_add_hub(user_id, moment_id)


@router.get(_PP + "/quick-add/vendors/context")
async def purchase_vendor_context(moment_id: UUID, user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _service(db).purchase_vendor_context(user_id, moment_id)


@router.post(_PP + "/quick-add/vendors", status_code=status.HTTP_201_CREATED)
async def purchase_create_vendor(moment_id: UUID, body: dict[str, Any] = Body(default={}), user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _service(db).purchase_quick_add_create(user_id, moment_id, "vendors", body)


@router.get(_PP + "/quick-add/updates/context")
async def purchase_update_context(moment_id: UUID, user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _service(db).purchase_update_context(user_id, moment_id)


@router.post(_PP + "/quick-add/updates", status_code=status.HTTP_201_CREATED)
async def purchase_create_update(moment_id: UUID, body: dict[str, Any] = Body(default={}), user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _service(db).purchase_quick_add_create(user_id, moment_id, "updates", body)


@router.get(_PP + "/quick-add/ownership/context")
async def purchase_ownership_context(moment_id: UUID, user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _service(db).purchase_ownership_context(user_id, moment_id)


@router.post(_PP + "/quick-add/ownership", status_code=status.HTTP_201_CREATED)
async def purchase_create_ownership(moment_id: UUID, body: dict[str, Any] = Body(default={}), user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _service(db).purchase_quick_add_create(user_id, moment_id, "ownership", body)


@router.get(_PP + "/quick-add/delivery/context")
async def purchase_delivery_context(moment_id: UUID, user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _service(db).purchase_delivery_context(user_id, moment_id)


@router.post(_PP + "/quick-add/delivery", status_code=status.HTTP_201_CREATED)
async def purchase_create_delivery(moment_id: UUID, body: dict[str, Any] = Body(default={}), user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _service(db).purchase_quick_add_create(user_id, moment_id, "delivery", body)


@router.get(_PP + "/quick-add/contributors/context")
async def purchase_contributor_context(moment_id: UUID, user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _service(db).purchase_contributor_context(user_id, moment_id)


@router.post(_PP + "/quick-add/contributors", status_code=status.HTTP_201_CREATED)
async def purchase_create_contributor(moment_id: UUID, body: dict[str, Any] = Body(default={}), user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _service(db).purchase_quick_add_create(user_id, moment_id, "contributors", body)


@router.get(_PP + "/quick-add/participants/context")
async def purchase_participants_context(moment_id: UUID, user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _service(db).purchase_participants_context(user_id, moment_id)


@router.post(_PP + "/quick-add/participants", status_code=status.HTTP_201_CREATED)
async def purchase_create_participants(moment_id: UUID, body: dict[str, Any] = Body(default={}), user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _service(db).purchase_quick_add_create(user_id, moment_id, "participants", body)


@router.get(_PP + "/quick-add/purchase-items/context")
async def purchase_item_context(moment_id: UUID, user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _service(db).purchase_item_context(user_id, moment_id)


@router.post(_PP + "/quick-add/purchase-items", status_code=status.HTTP_201_CREATED)
async def purchase_create_item(moment_id: UUID, body: dict[str, Any] = Body(default={}), user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _service(db).purchase_quick_add_create(user_id, moment_id, "purchase-items", body)


@router.get(_PP + "/quick-add/expenses/context")
async def purchase_expense_context(moment_id: UUID, user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _service(db).purchase_expense_context(user_id, moment_id)


@router.post(_PP + "/quick-add/expenses", status_code=status.HTTP_201_CREATED)
async def purchase_create_expense(moment_id: UUID, body: dict[str, Any] = Body(default={}), user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _service(db).purchase_quick_add_create(user_id, moment_id, "expenses", body)


@router.get(_PP + "/quick-add/polls/context")
async def purchase_poll_context(moment_id: UUID, user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _service(db).purchase_poll_context(user_id, moment_id)


@router.post(_PP + "/quick-add/polls", status_code=status.HTTP_201_CREATED)
async def purchase_create_poll(moment_id: UUID, body: dict[str, Any] = Body(default={}), user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _service(db).purchase_quick_add_create(user_id, moment_id, "polls", body)


@router.get(_PP + "/quick-add/memories/context")
async def purchase_memory_context(moment_id: UUID, user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _service(db).purchase_memory_context(user_id, moment_id)


@router.post(_PP + "/quick-add/memories", status_code=status.HTTP_201_CREATED)
async def purchase_create_memory(moment_id: UUID, body: dict[str, Any] = Body(default={}), user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _service(db).purchase_quick_add_create(user_id, moment_id, "memories", body)


# =========================================================================== #
# shared-living
# =========================================================================== #
_PL = "/shared-living/moments/{moment_id}"


@router.get(_PL + "/live-hub")
async def living_live_hub(moment_id: UUID, user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _service(db).living_live_hub(user_id, moment_id)


@router.get(_PL + "/pulse")
async def living_pulse(
    moment_id: UUID,
    force_refresh: bool = Query(False),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).living_pulse(user_id, moment_id, force_refresh=force_refresh)


@router.get(_PL + "/moments-view")
async def living_moments_view(
    moment_id: UUID,
    force_refresh: bool = Query(False),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).living_moments_view(
        user_id, moment_id, force_refresh=force_refresh
    )


@router.get(_PL + "/quick-add/hub")
async def living_quick_add_hub(moment_id: UUID, user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _service(db).living_quick_add_hub(user_id, moment_id)


@router.get(_PL + "/quick-add/residents/context")
async def living_resident_context(moment_id: UUID, user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _service(db).living_resident_context(user_id, moment_id)


@router.post(_PL + "/quick-add/residents", status_code=status.HTTP_201_CREATED)
async def living_create_resident(moment_id: UUID, body: dict[str, Any] = Body(default={}), user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _service(db).living_create_resident(user_id, moment_id, body)


@router.get(_PL + "/quick-add/expenses/context")
async def living_expense_context(moment_id: UUID, user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _service(db).living_expense_context(user_id, moment_id)


@router.post(_PL + "/quick-add/expenses", status_code=status.HTTP_201_CREATED)
async def living_create_expense(moment_id: UUID, body: dict[str, Any] = Body(default={}), user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _service(db).living_create_expense(user_id, moment_id, body)


@router.get(_PL + "/quick-add/contributions/context")
async def living_contribution_context(moment_id: UUID, user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _service(db).living_contribution_context(user_id, moment_id)


@router.post(_PL + "/quick-add/contributions", status_code=status.HTTP_201_CREATED)
async def living_create_contribution(moment_id: UUID, body: dict[str, Any] = Body(default={}), user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _service(db).living_quick_add_create(user_id, moment_id, "contributions", body)


@router.get(_PL + "/quick-add/tasks/context")
async def living_task_context(moment_id: UUID, user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _service(db).living_task_context(user_id, moment_id)


@router.post(_PL + "/quick-add/tasks", status_code=status.HTTP_201_CREATED)
async def living_create_task(moment_id: UUID, body: dict[str, Any] = Body(default={}), user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _service(db).living_quick_add_create(user_id, moment_id, "tasks", body)


@router.get(_PL + "/quick-add/rules/context")
async def living_rule_context(moment_id: UUID, user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _service(db).living_rule_context(user_id, moment_id)


@router.post(_PL + "/quick-add/rules", status_code=status.HTTP_201_CREATED)
async def living_create_rule(moment_id: UUID, body: dict[str, Any] = Body(default={}), user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _service(db).living_quick_add_create(user_id, moment_id, "rules", body)


@router.get(_PL + "/quick-add/assets/context")
async def living_asset_context(moment_id: UUID, user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _service(db).living_asset_context(user_id, moment_id)


@router.post(_PL + "/quick-add/assets", status_code=status.HTTP_201_CREATED)
async def living_create_asset(moment_id: UUID, body: dict[str, Any] = Body(default={}), user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _service(db).living_quick_add_create(user_id, moment_id, "assets", body)


@router.get(_PL + "/quick-add/maintenance/context")
async def living_maintenance_context(moment_id: UUID, user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _service(db).living_maintenance_context(user_id, moment_id)


@router.post(_PL + "/quick-add/maintenance", status_code=status.HTTP_201_CREATED)
async def living_create_maintenance(moment_id: UUID, body: dict[str, Any] = Body(default={}), user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _service(db).living_quick_add_create(user_id, moment_id, "maintenance", body)


@router.get(_PL + "/quick-add/updates/context")
async def living_update_context(moment_id: UUID, user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _service(db).living_update_context(user_id, moment_id)


@router.post(_PL + "/quick-add/updates", status_code=status.HTTP_201_CREATED)
async def living_create_update(moment_id: UUID, body: dict[str, Any] = Body(default={}), user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _service(db).living_quick_add_create(user_id, moment_id, "updates", body)


@router.get(_PL + "/quick-add/polls/context")
async def living_poll_context(moment_id: UUID, user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _service(db).living_poll_context(user_id, moment_id)


@router.post(_PL + "/quick-add/polls", status_code=status.HTTP_201_CREATED)
async def living_create_poll(moment_id: UUID, body: dict[str, Any] = Body(default={}), user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _service(db).living_quick_add_create(user_id, moment_id, "polls", body)


@router.get(_PL + "/quick-add/memories/context")
async def living_memory_context(moment_id: UUID, user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _service(db).living_memory_context(user_id, moment_id)


@router.post(_PL + "/quick-add/memories", status_code=status.HTTP_201_CREATED)
async def living_create_memory(moment_id: UUID, body: dict[str, Any] = Body(default={}), user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _service(db).living_quick_add_create(user_id, moment_id, "memories", body)


@router.get(_PL + "/activity")
async def living_list_activity(
    moment_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).living_list_activity(user_id, moment_id)


@router.get(_PL + "/activity/{event_id}")
async def living_get_activity(
    moment_id: UUID,
    event_id: str,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).living_get_activity(user_id, moment_id, event_id)


@router.patch(_PL + "/activity/{event_id}")
async def living_patch_activity(
    moment_id: UUID,
    event_id: str,
    body: dict[str, Any] = Body(default={}),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).living_patch_activity(user_id, moment_id, event_id, body)


@router.delete(_PL + "/activity/{event_id}")
async def living_delete_activity(
    moment_id: UUID,
    event_id: str,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).living_delete_activity(user_id, moment_id, event_id)
