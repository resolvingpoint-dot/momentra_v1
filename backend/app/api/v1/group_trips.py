"""Group *trips* router (mobile contract).

Full trip surface the Android client calls: core screens (live-hub / pulse /
moments-view / memories) plus the deep modules (live-workspace, expenses,
contributions, corpus, plans, approvals, settlements, quick-add contexts,
guests, attachments) and ``/group/trip-creation-options``. Read endpoints return
schema-valid empty/seeded shapes; write endpoints echo submitted values into a
valid response. Registered before the legacy ``group.router``.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any, AsyncIterator
from uuid import UUID

from fastapi import APIRouter, Body, Depends, Query, Request, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import cache as core_cache
from app.core.database import get_db
from app.dependencies.auth import get_current_user_id
from app.domains.group import trip_schemas as t
from app.domains.group.group_moment_events import invalidate_channel
from app.domains.group.trip_service import TripService
from app.domains.group.trip_deep_service import TripDeepService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/group/trips", tags=["group"])
options_router = APIRouter(prefix="/group", tags=["group"])

_SSE_HEARTBEAT_S = 15.0


def _service(db: AsyncSession) -> TripService:
    return TripService(db)


def _deep(db: AsyncSession) -> TripDeepService:
    return TripDeepService(db)


@router.get("/{moment_id}/stream")
async def trip_moment_stream(
    moment_id: UUID,
    request: Request,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> StreamingResponse:
    """SSE: projection invalidate push for a trip moment.

    Auth via Bearer (same as other routes). If Redis is unavailable, keep
    heartbeat-only so clients can fall back to pull-to-refresh.
    """
    await _service(db).assert_access(user_id, moment_id)
    channel = invalidate_channel(moment_id)

    async def event_gen() -> AsyncIterator[str]:
        redis = await core_cache.get_redis()
        if redis is None:
            logger.info(
                "trip stream heartbeat-only (no Redis) moment=%s user=%s",
                moment_id,
                user_id,
            )
            try:
                while True:
                    if await request.is_disconnected():
                        break
                    yield ": ping\n\n"
                    await asyncio.sleep(_SSE_HEARTBEAT_S)
            except asyncio.CancelledError:
                pass
            return

        pubsub = redis.pubsub()
        try:
            await pubsub.subscribe(channel)
            while True:
                if await request.is_disconnected():
                    break
                message = await pubsub.get_message(
                    ignore_subscribe_messages=True,
                    timeout=_SSE_HEARTBEAT_S,
                )
                if message is None:
                    yield ": ping\n\n"
                    continue
                if message.get("type") != "message":
                    continue
                data = message.get("data")
                if data is None:
                    continue
                if isinstance(data, bytes):
                    data = data.decode("utf-8", errors="replace")
                yield f"event: invalidate\ndata: {data}\n\n"
        except asyncio.CancelledError:
            pass
        except Exception:
            logger.warning(
                "trip stream error moment=%s user=%s",
                moment_id,
                user_id,
                exc_info=True,
            )
        finally:
            try:
                await pubsub.unsubscribe(channel)
                close = getattr(pubsub, "aclose", None) or getattr(pubsub, "close", None)
                if close is not None:
                    result = close()
                    if asyncio.iscoroutine(result):
                        await result
            except Exception:
                pass

    return StreamingResponse(
        event_gen(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/{moment_id}/live-hub")
async def trip_live_hub(
    moment_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).live_hub(user_id, moment_id)


@router.get("/{moment_id}/pulse")
async def trip_pulse(
    moment_id: UUID,
    force_refresh: bool = Query(False),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).pulse(user_id, moment_id, force_refresh=force_refresh)


@router.get("/{moment_id}/moments-view")
async def trip_moments_view(
    moment_id: UUID,
    force_refresh: bool = Query(False),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).moments_view(user_id, moment_id, force_refresh=force_refresh)


@router.get("/{moment_id}/memories")
async def trip_memories(
    moment_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    return await _service(db).list_memories(user_id, moment_id)


@router.post("/{moment_id}/memories", status_code=status.HTTP_201_CREATED)
async def create_trip_memory(
    moment_id: UUID,
    body: t.GroupMomentMemoryCreateRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).create_memory(user_id, moment_id, body)


@router.get("/{moment_id}/activity")
async def trip_list_activity(
    moment_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).list_activity(user_id, moment_id)


@router.get("/{moment_id}/activity/{event_id}")
async def trip_get_activity(
    moment_id: UUID,
    event_id: str,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).get_activity(user_id, moment_id, event_id)


@router.patch("/{moment_id}/activity/{event_id}")
async def trip_patch_activity(
    moment_id: UUID,
    event_id: str,
    body: dict[str, Any] = Body(default={}),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).patch_activity(user_id, moment_id, event_id, body)


@router.delete("/{moment_id}/activity/{event_id}")
async def trip_delete_activity(
    moment_id: UUID,
    event_id: str,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _service(db).delete_activity(user_id, moment_id, event_id)


# =========================================================================== #
# deep modules
# =========================================================================== #
@router.get("/{moment_id}/live-workspace")
async def trip_live_workspace(moment_id: UUID, user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _deep(db).live_workspace(user_id, moment_id)


@router.get("/{moment_id}/expenses")
async def trip_expenses(moment_id: UUID, user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> list[dict]:
    return await _deep(db).list_expenses(user_id, moment_id)


@router.post("/{moment_id}/expenses", status_code=status.HTTP_201_CREATED)
async def create_trip_expense(moment_id: UUID, body: dict[str, Any] = Body(default={}), user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _deep(db).create_expense(user_id, moment_id, body)


@router.patch("/{moment_id}/expenses/{expense_id}")
async def update_trip_expense(
    moment_id: UUID,
    expense_id: str,
    body: dict[str, Any] = Body(default={}),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _deep(db).update_expense(user_id, moment_id, expense_id, body)


@router.delete("/{moment_id}/expenses/{expense_id}", status_code=status.HTTP_200_OK)
async def delete_trip_expense(
    moment_id: UUID,
    expense_id: str,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    return await _deep(db).delete_expense(user_id, moment_id, expense_id)


@router.patch("/{moment_id}/expenses/{expense_id}/split")
async def split_trip_expense(moment_id: UUID, expense_id: str, body: dict[str, Any] = Body(default={}), user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _deep(db).split_expense(user_id, moment_id, expense_id, body)


@router.get("/{moment_id}/contributions/context")
async def trip_contribution_context(moment_id: UUID, pool: str = Query("stay"), user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _deep(db).contribution_context(user_id, moment_id, pool)


@router.post("/{moment_id}/contributions", status_code=status.HTTP_201_CREATED)
async def create_trip_contribution(moment_id: UUID, body: dict[str, Any] = Body(default={}), user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _deep(db).create_contribution(user_id, moment_id, body)


@router.get("/{moment_id}/corpus")
async def trip_corpus(moment_id: UUID, user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _deep(db).corpus(user_id, moment_id)


@router.patch("/{moment_id}/corpus/custodian")
async def trip_set_custodian(moment_id: UUID, body: dict[str, Any] = Body(default={}), user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _deep(db).set_custodian(user_id, moment_id, body)


@router.get("/{moment_id}/plans/context")
async def trip_plan_context(moment_id: UUID, category: str = Query("stay"), user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _deep(db).plan_context(user_id, moment_id, category)


@router.post("/{moment_id}/plans", status_code=status.HTTP_201_CREATED)
async def create_trip_plan(moment_id: UUID, body: dict[str, Any] = Body(default={}), user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _deep(db).create_plan(user_id, moment_id, body)


@router.get("/{moment_id}/approvals/context")
async def trip_approval_context(moment_id: UUID, decision: str | None = Query(None), user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _deep(db).approvals(user_id, moment_id)


@router.post("/{moment_id}/approvals/decisions/{decision_id}/votes")
async def cast_trip_vote(moment_id: UUID, decision_id: str, body: dict[str, Any] = Body(default={}), user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _deep(db).cast_vote(user_id, moment_id, decision_id, body)


@router.post("/{moment_id}/approvals/decisions/{decision_id}/request")
async def request_trip_approval(moment_id: UUID, decision_id: str, user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _deep(db).request_approval(user_id, moment_id, decision_id)


@router.post("/{moment_id}/approvals/polls", status_code=status.HTTP_201_CREATED)
async def create_trip_approval_poll(moment_id: UUID, body: dict[str, Any] = Body(default={}), user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _deep(db).create_poll(user_id, moment_id, body)


@router.post("/{moment_id}/approvals/polls/{poll_id}/votes")
async def cast_trip_poll_vote(moment_id: UUID, poll_id: str, body: dict[str, Any] = Body(default={}), user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _deep(db).cast_poll_vote(user_id, moment_id, poll_id, body)


@router.get("/{moment_id}/settlements/context")
async def trip_settlement_context(moment_id: UUID, user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _deep(db).settlements(user_id, moment_id)


@router.post("/{moment_id}/settlements/restore")
async def restore_trip_balance(moment_id: UUID, user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _deep(db).restore_balance(user_id, moment_id)


# ----- quick-add contexts ------------------------------------------------- #
@router.get("/{moment_id}/quick-add/participant/context")
async def trip_participant_context(moment_id: UUID, user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _deep(db).participant_context(user_id, moment_id)


@router.get("/{moment_id}/quick-add/booking/context")
async def trip_booking_context(moment_id: UUID, user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _deep(db).booking_context(user_id, moment_id)


@router.get("/{moment_id}/quick-add/planning-item/context")
async def trip_planning_item_context(moment_id: UUID, user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _deep(db).planning_item_context(user_id, moment_id)


@router.get("/{moment_id}/quick-add/expense/context")
async def trip_expense_context(moment_id: UUID, user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _deep(db).expense_context(user_id, moment_id)


@router.get("/{moment_id}/quick-add/memory/context")
async def trip_memory_context(moment_id: UUID, user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _deep(db).memory_context(user_id, moment_id)


@router.get("/{moment_id}/quick-add/poll/context")
async def trip_poll_context(moment_id: UUID, user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _deep(db).poll_context(user_id, moment_id)


@router.get("/{moment_id}/quick-add/attendance/context")
async def trip_attendance_context(moment_id: UUID, user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _deep(db).attendance_context(user_id, moment_id)


@router.post("/{moment_id}/quick-add/attendance", status_code=status.HTTP_201_CREATED)
async def create_trip_attendance(moment_id: UUID, body: dict[str, Any] = Body(default={}), user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _deep(db).create_attendance(user_id, moment_id, body)


@router.get("/{moment_id}/quick-add/vendor/context")
async def trip_vendor_context(moment_id: UUID, user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _deep(db).vendor_context(user_id, moment_id)


@router.post("/{moment_id}/quick-add/vendor", status_code=status.HTTP_201_CREATED)
async def create_trip_vendor(moment_id: UUID, body: dict[str, Any] = Body(default={}), user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _deep(db).create_vendor(user_id, moment_id, body)


@router.get("/{moment_id}/quick-add/update/context")
async def trip_update_context(moment_id: UUID, user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _deep(db).update_context(user_id, moment_id)


@router.post("/{moment_id}/quick-add/update", status_code=status.HTTP_201_CREATED)
async def create_trip_update(moment_id: UUID, body: dict[str, Any] = Body(default={}), user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _deep(db).create_update(user_id, moment_id, body)


@router.post("/{moment_id}/quick-add/booking", status_code=status.HTTP_201_CREATED)
async def create_trip_booking(moment_id: UUID, body: dict[str, Any] = Body(default={}), user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _deep(db).create_booking(user_id, moment_id, body)


@router.post("/{moment_id}/repair-inflated-booking-amounts")
async def repair_inflated_booking_amounts(
    moment_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """One-shot fix for bookings stored 100× too high (web Quick Add double convert)."""
    return await _deep(db).repair_inflated_booking_amounts(user_id, moment_id)


@router.post("/{moment_id}/quick-add/poll", status_code=status.HTTP_201_CREATED)
async def create_trip_poll_quick_add(moment_id: UUID, body: dict[str, Any] = Body(default={}), user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _deep(db).create_poll_quick_add(user_id, moment_id, body)


@router.get("/{moment_id}/quick-add/budget/context")
async def trip_budget_context(moment_id: UUID, user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _deep(db).budget_context(user_id, moment_id)


@router.post("/{moment_id}/quick-add/budget/plans", status_code=status.HTTP_201_CREATED)
async def create_trip_budget_plan(moment_id: UUID, body: dict[str, Any] = Body(default={}), user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _deep(db).create_budget_plan(user_id, moment_id, body)


# ----- guests & attachments ----------------------------------------------- #
@router.post("/{moment_id}/guests", status_code=status.HTTP_201_CREATED)
async def create_trip_guest(moment_id: UUID, body: dict[str, Any] = Body(default={}), user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _deep(db).create_guest(user_id, moment_id, body)


@router.post("/{moment_id}/attachments/upload-url", status_code=status.HTTP_201_CREATED)
async def trip_attachment_upload_url(moment_id: UUID, body: dict[str, Any] = Body(default={}), user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _deep(db).attachment_upload_url(user_id, moment_id, body)


@router.post("/{moment_id}/attachments/confirm")
async def trip_attachment_confirm(moment_id: UUID, body: dict[str, Any] = Body(default={}), user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _deep(db).attachment_confirm(user_id, moment_id, body)


# ----- trip-creation-options (top-level under /group) --------------------- #
@options_router.get("/trip-creation-options")
async def trip_creation_options(user_id: UUID = Depends(get_current_user_id), db: AsyncSession = Depends(get_db)) -> dict:
    return await _deep(db).creation_options()
