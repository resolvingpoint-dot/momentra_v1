"""Group module API router.

Router -> Service -> Repository -> Model. Handlers resolve the caller via
dependency injection and delegate every decision to :class:`GroupService`;
domain errors it raises (NotFound / Permission / Validation / StateTransition)
are rendered as JSON by the global exception handlers. Group access is
membership-based, enforced inside the service.
"""
from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.service import Page
from app.dependencies.auth import get_current_user, get_current_user_id
from app.domains.app_bootstrap.empty_state_config import EMPTY_STATE_OVERRIDES
from app.domains.group.api_schemas import (
    GroupAnalyticsResponse,
    GroupEventCreateRequest,
    GroupExpenseCreateRequest,
    GroupInviteAcceptRequest,
    GroupInviteRequest,
    GroupLivingTaskCreateRequest,
    GroupMemoryOverviewResponse,
    GroupPollCreateRequest,
    GroupPollDetail,
    GroupPollVoteRequest,
    GroupPurchaseItemCreateRequest,
    GroupQuickAddRequest,
)
from app.domains.group.group_service import GroupService
from app.domains.group.schemas import (
    GroupExpensesSchema,
    GroupLiveFeedSchema,
    GroupMomentMembersSchema,
    GroupMomentsSchema,
    GroupMomentWorkItemsSchema,
    GroupPollsSchema,
    GroupPollVotesSchema,
    GroupPulseSnapshotsSchema,
    GroupQuickAddEventsSchema,
)
from app.domains.life360.schemas import SharedLivingTasksSchema, SharedPurchaseItemsSchema
from app.domains.moments.service import MomentService
from app.domains.module_states.service import ModuleStateService
from app.domains.users.service import UserService

router = APIRouter(prefix="/group", tags=["group"])


# --------------------------------------------------------------------------- #
# home (context landing)
# --------------------------------------------------------------------------- #
@router.get("/home", summary="Group context landing state")
async def group_home(
    auth_user: dict[str, Any] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    user_service = UserService(db)
    user = await user_service.get_user(auth_user["uid"])
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    moment_service = MomentService(db)
    count = await moment_service.count_by_context_type(user.id, "GROUP")

    module_service = ModuleStateService(db)
    ms = await module_service.get_state(user.id, "GROUP")
    state = ms.state if ms else "EMPTY"

    return {
        "context": "GROUP",
        "state": state,
        "counts": {"moments": count},
        "empty_state_override": EMPTY_STATE_OVERRIDES.get("GROUP"),
    }


# --------------------------------------------------------------------------- #
# moments
# --------------------------------------------------------------------------- #
@router.get("/moments", response_model=Page[GroupMomentsSchema], summary="List group moments the caller belongs to")
async def list_moments(
    status_filter: str | None = Query(None, alias="status", description="Filter by status: DRAFT/ACTIVE/COMPLETED/ARCHIVED"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> Page[GroupMomentsSchema]:
    return await GroupService(db).list_moments(user_id, status=status_filter, page=page, per_page=per_page)


# NOTE: ``POST /group/moments`` is served by the mobile-contract router
# (``group_app``), which is registered first in ``main.py`` and wins the path.
# The typed create handler is intentionally not defined here to avoid a shadowed
# (unreachable) route and a duplicate OpenAPI operation.


@router.get("/moments/{moment_id}", response_model=GroupMomentsSchema, summary="Get a group moment")
async def get_moment(
    moment_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> GroupMomentsSchema:
    return await GroupService(db).get_moment(user_id, moment_id)


@router.post("/moments/{moment_id}/activate", response_model=GroupMomentsSchema, summary="Activate a group moment (DRAFT -> ACTIVE)")
async def activate_moment(
    moment_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> GroupMomentsSchema:
    return await GroupService(db).activate_moment(user_id, moment_id)


@router.post("/moments/{moment_id}/complete", response_model=GroupMomentsSchema, summary="Complete a group moment (ACTIVE -> COMPLETED)")
async def complete_moment(
    moment_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> GroupMomentsSchema:
    return await GroupService(db).complete_moment(user_id, moment_id)


@router.post("/moments/{moment_id}/archive", response_model=GroupMomentsSchema, summary="Archive a group moment")
async def archive_moment(
    moment_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> GroupMomentsSchema:
    return await GroupService(db).archive_moment(user_id, moment_id)


# --------------------------------------------------------------------------- #
# members / invitations
# --------------------------------------------------------------------------- #
@router.get(
    "/moments/{moment_id}/members",
    response_model=Page[GroupMomentMembersSchema],
    summary="List members of a group moment",
)
async def list_members(
    moment_id: UUID,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> Page[GroupMomentMembersSchema]:
    return await GroupService(db).list_members(user_id, moment_id, page=page, per_page=per_page)


@router.post(
    "/moments/{moment_id}/invitations",
    response_model=GroupMomentMembersSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Invite a member to a group moment",
)
async def invite_member(
    moment_id: UUID,
    body: GroupInviteRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> GroupMomentMembersSchema:
    return await GroupService(db).invite_member(
        user_id,
        moment_id,
        display_name=body.display_name,
        role_code=body.role_code,
        contact_email=body.contact_email,
        contact_phone=body.contact_phone,
    )


@router.post(
    "/moments/{moment_id}/invitations/{member_id}/accept",
    response_model=GroupMomentMembersSchema,
    summary="Accept an invitation (INVITED -> ACTIVE)",
)
async def accept_invitation(
    moment_id: UUID,
    member_id: UUID,
    body: GroupInviteAcceptRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> GroupMomentMembersSchema:
    return await GroupService(db).accept_invitation(
        user_id, moment_id, member_id, invite_token=body.invite_token
    )


@router.post(
    "/moments/{moment_id}/invitations/{member_id}/decline",
    response_model=GroupMomentMembersSchema,
    summary="Decline an invitation (INVITED -> DECLINED)",
)
async def decline_invitation(
    moment_id: UUID,
    member_id: UUID,
    body: GroupInviteAcceptRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> GroupMomentMembersSchema:
    return await GroupService(db).decline_invitation(
        user_id, moment_id, member_id, invite_token=body.invite_token
    )


@router.delete(
    "/moments/{moment_id}/members/{member_id}",
    response_model=GroupMomentMembersSchema,
    summary="Remove a member from a group moment",
)
async def remove_member(
    moment_id: UUID,
    member_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> GroupMomentMembersSchema:
    return await GroupService(db).remove_member(user_id, moment_id, member_id)


# --------------------------------------------------------------------------- #
# expenses
# --------------------------------------------------------------------------- #
@router.get("/moments/{moment_id}/expenses", response_model=Page[GroupExpensesSchema], summary="List group expenses")
async def list_expenses(
    moment_id: UUID,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> Page[GroupExpensesSchema]:
    return await GroupService(db).list_expenses(user_id, moment_id, page=page, per_page=per_page)


@router.post(
    "/moments/{moment_id}/expenses",
    response_model=GroupExpensesSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Record a group expense (with optional splits)",
)
async def create_expense(
    moment_id: UUID,
    body: GroupExpenseCreateRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> GroupExpensesSchema:
    return await GroupService(db).create_expense(
        user_id,
        moment_id,
        module_context=body.module_context,
        category=body.category,
        expense_name=body.expense_name,
        amount=body.amount,
        expense_date=body.expense_date,
        paid_by_member_id=body.paid_by_member_id,
        notes=body.notes,
        splits=[s.model_dump() for s in body.splits],
    )


# --------------------------------------------------------------------------- #
# purchases (shared purchase items)
# --------------------------------------------------------------------------- #
@router.get("/moments/{moment_id}/purchases", response_model=Page[SharedPurchaseItemsSchema], summary="List shared purchase items")
async def list_purchases(
    moment_id: UUID,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> Page[SharedPurchaseItemsSchema]:
    return await GroupService(db).list_purchases(user_id, moment_id, page=page, per_page=per_page)


@router.post(
    "/moments/{moment_id}/purchases",
    response_model=SharedPurchaseItemsSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Propose a shared purchase item",
)
async def create_purchase(
    moment_id: UUID,
    body: GroupPurchaseItemCreateRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> SharedPurchaseItemsSchema:
    return await GroupService(db).create_purchase(user_id, moment_id, data=body.model_dump())


# --------------------------------------------------------------------------- #
# shared living (tasks)
# --------------------------------------------------------------------------- #
@router.get(
    "/moments/{moment_id}/shared-living/tasks",
    response_model=Page[SharedLivingTasksSchema],
    summary="List shared-living tasks",
)
async def list_shared_living_tasks(
    moment_id: UUID,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> Page[SharedLivingTasksSchema]:
    return await GroupService(db).list_shared_living_tasks(user_id, moment_id, page=page, per_page=per_page)


@router.post(
    "/moments/{moment_id}/shared-living/tasks",
    response_model=SharedLivingTasksSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create a shared-living task",
)
async def create_shared_living_task(
    moment_id: UUID,
    body: GroupLivingTaskCreateRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> SharedLivingTasksSchema:
    return await GroupService(db).create_shared_living_task(user_id, moment_id, data=body.model_dump())


# --------------------------------------------------------------------------- #
# events (work items of type EVENT)
# --------------------------------------------------------------------------- #
@router.get("/moments/{moment_id}/events", response_model=Page[GroupMomentWorkItemsSchema], summary="List group events")
async def list_events(
    moment_id: UUID,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> Page[GroupMomentWorkItemsSchema]:
    return await GroupService(db).list_events(user_id, moment_id, page=page, per_page=per_page)


@router.post(
    "/moments/{moment_id}/events",
    response_model=GroupMomentWorkItemsSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Create a group event",
)
async def create_event(
    moment_id: UUID,
    body: GroupEventCreateRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> GroupMomentWorkItemsSchema:
    return await GroupService(db).create_event(user_id, moment_id, data=body.model_dump())


# --------------------------------------------------------------------------- #
# polls
# --------------------------------------------------------------------------- #
@router.get("/moments/{moment_id}/polls", response_model=Page[GroupPollsSchema], summary="List polls")
async def list_polls(
    moment_id: UUID,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> Page[GroupPollsSchema]:
    return await GroupService(db).list_polls(user_id, moment_id, page=page, per_page=per_page)


@router.post(
    "/moments/{moment_id}/polls",
    response_model=GroupPollDetail,
    status_code=status.HTTP_201_CREATED,
    summary="Create a poll with options",
)
async def create_poll(
    moment_id: UUID,
    body: GroupPollCreateRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> GroupPollDetail:
    return await GroupService(db).create_poll(
        user_id,
        moment_id,
        category=body.category,
        question=body.question,
        poll_type=body.poll_type,
        is_anonymous=body.is_anonymous,
        allow_multiple_votes=body.allow_multiple_votes,
        end_date=body.end_date,
        options=[o.model_dump() for o in body.options],
    )


@router.get(
    "/moments/{moment_id}/polls/{poll_id}",
    response_model=GroupPollDetail,
    summary="Get a poll with options and vote tally",
)
async def get_poll(
    moment_id: UUID,
    poll_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> GroupPollDetail:
    return await GroupService(db).get_poll(user_id, moment_id, poll_id)


@router.post(
    "/moments/{moment_id}/polls/{poll_id}/vote",
    response_model=GroupPollVotesSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Cast a vote in a poll",
)
async def vote_poll(
    moment_id: UUID,
    poll_id: UUID,
    body: GroupPollVoteRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> GroupPollVotesSchema:
    return await GroupService(db).vote_poll(user_id, moment_id, poll_id, body.option_id)


@router.post(
    "/moments/{moment_id}/polls/{poll_id}/close",
    response_model=GroupPollsSchema,
    summary="Close a poll (OPEN -> CLOSED)",
)
async def close_poll(
    moment_id: UUID,
    poll_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> GroupPollsSchema:
    return await GroupService(db).close_poll(user_id, moment_id, poll_id)


# --------------------------------------------------------------------------- #
# activities (live feed)
# --------------------------------------------------------------------------- #
@router.get("/moments/{moment_id}/activities", response_model=Page[GroupLiveFeedSchema], summary="List the moment activity feed")
async def list_activities(
    moment_id: UUID,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> Page[GroupLiveFeedSchema]:
    return await GroupService(db).list_activities(user_id, moment_id, page=page, per_page=per_page)


# --------------------------------------------------------------------------- #
# quick add
# --------------------------------------------------------------------------- #
@router.post(
    "/moments/{moment_id}/quick-add",
    response_model=GroupQuickAddEventsSchema,
    status_code=status.HTTP_201_CREATED,
    summary="Record a quick-add event",
)
async def quick_add(
    moment_id: UUID,
    body: GroupQuickAddRequest,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> GroupQuickAddEventsSchema:
    return await GroupService(db).quick_add(
        user_id,
        moment_id,
        module_code=body.module_code,
        event_ref_table=body.event_ref_table,
        event_ref_id=body.event_ref_id,
        event_action=body.event_action,
        event_payload_json=body.event_payload_json,
    )


# --------------------------------------------------------------------------- #
# pulse
# --------------------------------------------------------------------------- #
@router.get(
    "/moments/{moment_id}/pulse",
    response_model=list[GroupPulseSnapshotsSchema],
    summary="Get recent pulse snapshots",
)
async def get_pulse(
    moment_id: UUID,
    limit: int = Query(20, ge=1, le=100),
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> list[GroupPulseSnapshotsSchema]:
    return await GroupService(db).get_pulse(user_id, moment_id, limit=limit)


# --------------------------------------------------------------------------- #
# memory
# --------------------------------------------------------------------------- #
@router.get(
    "/moments/{moment_id}/memory",
    response_model=GroupMemoryOverviewResponse,
    summary="Group memory overview (entries, patterns, snapshots)",
)
async def memory_overview(
    moment_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> GroupMemoryOverviewResponse:
    return await GroupService(db).memory_overview(user_id, moment_id)


# --------------------------------------------------------------------------- #
# analytics
# --------------------------------------------------------------------------- #
@router.get(
    "/moments/{moment_id}/analytics",
    response_model=GroupAnalyticsResponse,
    summary="Group analytics (counts, insights, recommendations, health, impact)",
)
async def analytics(
    moment_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
) -> GroupAnalyticsResponse:
    return await GroupService(db).analytics(user_id, moment_id)
