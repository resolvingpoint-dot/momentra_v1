"""Group module service (business logic + orchestration).

Group data is authorized by *membership* (not by a user-owned column): a user
may act on a moment's data when they hold an active ``group_moment_members`` row
for it (the creator is auto-enrolled as an organizer on creation). Child records
reference ``member_id``, so this service resolves the caller to their member row
and passes it through.

It orchestrates the shared ``AsyncRepository`` instances (group + life360 shared
tables) and returns generated Pydantic schemas / composite responses -- never
SQLAlchemy models, and with no HTTP concerns. Repositories/schemas/``Page`` are
reused rather than duplicated.
"""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Mapping, Sequence
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError, PermissionDeniedError, StateTransitionError, ValidationError
from app.core.repository import AsyncRepository
from app.core.service import Page
from app.domains.group import repository as grepo
from app.domains.group import schemas as gs
from app.domains.group.api_schemas import (
    GroupAnalyticsCounts,
    GroupAnalyticsResponse,
    GroupMemoryOverviewResponse,
    GroupPollDetail,
)
from app.domains.life360 import repository as lrepo
from app.domains.life360 import schemas as ls

_ACTIVE_MEMBER_BLOCK = {"LEFT", "REMOVED", "DECLINED"}


def _now() -> datetime:
    return datetime.now(timezone.utc)


class GroupService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.moments_repo = grepo.GroupMomentsRepository(session)
        self.members_repo = grepo.GroupMomentMembersRepository(session)
        self.roles_repo = grepo.GroupMomentRolesRepository(session)
        self.expenses_repo = grepo.GroupExpensesRepository(session)
        self.expense_splits_repo = grepo.GroupExpenseSplitsRepository(session)
        self.polls_repo = grepo.GroupPollsRepository(session)
        self.poll_options_repo = grepo.GroupPollOptionsRepository(session)
        self.poll_votes_repo = grepo.GroupPollVotesRepository(session)
        self.work_items_repo = grepo.GroupMomentWorkItemsRepository(session)
        self.live_feed_repo = grepo.GroupLiveFeedRepository(session)
        self.quick_add_repo = grepo.GroupQuickAddEventsRepository(session)
        self.pulse_repo = grepo.GroupPulseSnapshotsRepository(session)
        self.memory_entries_repo = grepo.GroupMemoryEntriesRepository(session)
        self.memory_patterns_repo = grepo.GroupMemoryPatternsRepository(session)
        self.memory_snapshots_repo = grepo.GroupMemorySnapshotsRepository(session)
        self.insights_repo = grepo.GroupAiInsightsRepository(session)
        self.health_repo = grepo.GroupHealthSnapshotsRepository(session)
        self.recommendations_repo = grepo.GroupRecommendationsRepository(session)
        self.impact_repo = grepo.GroupPeopleImpactScoresRepository(session)
        self.purchase_items_repo = lrepo.SharedPurchaseItemsRepository(session)
        self.living_tasks_repo = lrepo.SharedLivingTasksRepository(session)

    # ================================================================== #
    # shared helpers (reused by every feature)
    # ================================================================== #
    async def _created(self, repo: AsyncRepository, schema_cls, data: Mapping[str, Any]):
        obj = await repo.create(data)
        await self.session.refresh(obj)  # populate server defaults for the schema
        return schema_cls.model_validate(obj)

    async def _page(
        self,
        repo: AsyncRepository,
        schema_cls,
        *,
        filters: Mapping[str, Any] | None,
        order_by: str | None,
        page: int,
        per_page: int,
    ) -> Page:
        limit, offset = per_page, (page - 1) * per_page
        total = await repo.count(filters=filters)
        items = await repo.list(filters=filters, order_by=order_by, limit=limit, offset=offset)
        return Page[schema_cls](
            items=[schema_cls.model_validate(o) for o in items], total=total, limit=limit, offset=offset
        )

    async def _list(self, repo: AsyncRepository, schema_cls, *, filters, order_by=None, limit=50):
        items = await repo.list(filters=filters, order_by=order_by, limit=limit)
        return [schema_cls.model_validate(o) for o in items]

    async def _access(self, user_id: UUID, moment_id: UUID):
        """Return the caller's member row for a moment (None if they are the
        creator without a member row). Raises if the moment is missing or the
        caller has no access."""
        moment = await self.moments_repo.get_by_id(moment_id)
        if moment is None:
            raise NotFoundError("Group moment not found")
        member = await self.members_repo.get_by(moment_id=moment_id, user_id=user_id)
        if member is not None and member.left_at is None and member.status not in _ACTIVE_MEMBER_BLOCK:
            return moment, member
        if moment.created_by == user_id:
            return moment, None
        raise PermissionDeniedError("You are not a member of this group moment")

    async def _require_member(self, user_id: UUID, moment_id: UUID):
        _moment, member = await self._access(user_id, moment_id)
        if member is None:
            raise PermissionDeniedError("An active membership is required for this action")
        return member

    async def _resolve_member_id(self, user_id: UUID, moment_id: UUID, provided: UUID | None) -> UUID:
        member = await self._require_member(user_id, moment_id)
        return provided or member.member_id

    # ================================================================== #
    # moments
    # ================================================================== #
    async def list_moments(
        self, user_id: UUID, *, status: str | None = None, page: int = 1, per_page: int = 20
    ) -> Page:
        member_rows = await self.members_repo.list(filters={"user_id": user_id}, limit=None)
        moment_ids = sorted({m.moment_id for m in member_rows})
        if not moment_ids:
            return Page[gs.GroupMomentsSchema](items=[], total=0, limit=per_page, offset=(page - 1) * per_page)
        filters: dict[str, Any] = {"moment_id__in": moment_ids}
        if status:
            filters["status"] = status
        return await self._page(
            self.moments_repo, gs.GroupMomentsSchema,
            filters=filters, order_by="-created_at", page=page, per_page=per_page,
        )

    async def get_moment(self, user_id: UUID, moment_id: UUID) -> gs.GroupMomentsSchema:
        moment, _member = await self._access(user_id, moment_id)
        return gs.GroupMomentsSchema.model_validate(moment)

    async def create_moment(
        self,
        user_id: UUID,
        *,
        moment_type: str,
        moment_profile: str,
        moment_name: str,
        currency_code: str = "INR",
        experience_subtype: str | None = None,
        organizer_display_name: str = "Organizer",
    ) -> gs.GroupMomentsSchema:
        role = await self.roles_repo.get_by(moment_type=moment_type, is_default=True)
        if role is None:
            role = await self.roles_repo.get_by(moment_type=moment_type, is_active=True)
        if role is None:
            raise ValidationError(f"No roles are configured for moment type {moment_type!r}")
        moment = await self.moments_repo.create(
            {
                "moment_type": moment_type,
                "moment_profile": moment_profile,
                "moment_name": moment_name,
                "currency_code": currency_code,
                "experience_subtype": experience_subtype,
                "status": "DRAFT",
                "created_by": user_id,
            }
        )
        await self.session.refresh(moment)
        await self.members_repo.create(
            {
                "moment_id": moment.moment_id,
                "user_id": user_id,
                "display_name": organizer_display_name,
                "role_code": role.role_code,
                "status": "ACTIVE",
                "joined_at": _now(),
            }
        )
        schema = gs.GroupMomentsSchema.model_validate(moment)
        await self.session.commit()
        return schema

    async def _transition_moment(
        self, user_id: UUID, moment_id: UUID, to_status: str, allowed_from: set[str], set_activated: bool = False
    ) -> gs.GroupMomentsSchema:
        moment, _member = await self._access(user_id, moment_id)
        if moment.status not in allowed_from:
            raise StateTransitionError(f"Cannot move a group moment from {moment.status} to {to_status}")
        now = _now()
        moment.status = to_status
        moment.updated_at = now
        if set_activated and moment.activated_at is None:
            moment.activated_at = now
        await self.session.flush()
        schema = gs.GroupMomentsSchema.model_validate(moment)
        await self.session.commit()
        return schema

    async def activate_moment(self, user_id: UUID, moment_id: UUID) -> gs.GroupMomentsSchema:
        return await self._transition_moment(user_id, moment_id, "ACTIVE", {"DRAFT"}, set_activated=True)

    async def complete_moment(self, user_id: UUID, moment_id: UUID) -> gs.GroupMomentsSchema:
        return await self._transition_moment(user_id, moment_id, "COMPLETED", {"ACTIVE"})

    async def archive_moment(self, user_id: UUID, moment_id: UUID) -> gs.GroupMomentsSchema:
        return await self._transition_moment(user_id, moment_id, "ARCHIVED", {"DRAFT", "ACTIVE", "COMPLETED"})

    # ================================================================== #
    # members / invitations
    # ================================================================== #
    async def list_members(self, user_id: UUID, moment_id: UUID, *, page: int = 1, per_page: int = 50) -> Page:
        await self._access(user_id, moment_id)
        return await self._page(
            self.members_repo, gs.GroupMomentMembersSchema,
            filters={"moment_id": moment_id}, order_by="created_at", page=page, per_page=per_page,
        )

    async def invite_member(
        self,
        user_id: UUID,
        moment_id: UUID,
        *,
        display_name: str,
        role_code: str,
        contact_email: str | None = None,
        contact_phone: str | None = None,
    ) -> gs.GroupMomentMembersSchema:
        await self._require_member(user_id, moment_id)
        if await self.roles_repo.get_by_id(role_code) is None:
            raise ValidationError(f"Unknown role_code {role_code!r}")
        schema = await self._created(
            self.members_repo, gs.GroupMomentMembersSchema,
            {
                "moment_id": moment_id,
                "display_name": display_name,
                "role_code": role_code,
                "status": "INVITED",
                "contact_email": contact_email,
                "contact_phone": contact_phone,
                "invite_token": uuid4(),
                "invite_sent_at": _now(),
            },
        )
        await self.session.commit()
        return schema

    async def _member_in_moment(self, moment_id: UUID, member_id: UUID):
        member = await self.members_repo.get_by_id(member_id)
        if member is None or member.moment_id != moment_id:
            raise NotFoundError("Member not found in this moment")
        return member

    async def accept_invitation(
        self,
        user_id: UUID,
        moment_id: UUID,
        member_id: UUID,
        *,
        invite_token: UUID,
    ) -> gs.GroupMomentMembersSchema:
        member = await self._member_in_moment(moment_id, member_id)
        if member.status != "INVITED":
            raise StateTransitionError("Invitation is not in an INVITED state")
        if member.invite_token is None or member.invite_token != invite_token:
            raise PermissionDeniedError("Invalid invite token")
        if member.user_id is not None and member.user_id != user_id:
            raise PermissionDeniedError("This invitation belongs to another user")
        member.user_id = user_id
        member.status = "ACTIVE"
        member.joined_at = _now()
        # One-time use: clear token after successful claim.
        member.invite_token = None
        await self.session.flush()
        schema = gs.GroupMomentMembersSchema.model_validate(member)
        await self.session.commit()
        return schema

    async def decline_invitation(
        self,
        user_id: UUID,
        moment_id: UUID,
        member_id: UUID,
        *,
        invite_token: UUID,
    ) -> gs.GroupMomentMembersSchema:
        member = await self._member_in_moment(moment_id, member_id)
        if member.status != "INVITED":
            raise StateTransitionError("Invitation is not in an INVITED state")
        if member.invite_token is None or member.invite_token != invite_token:
            raise PermissionDeniedError("Invalid invite token")
        if member.user_id is not None and member.user_id != user_id:
            raise PermissionDeniedError("This invitation belongs to another user")
        member.status = "DECLINED"
        member.left_at = _now()
        member.invite_token = None
        await self.session.flush()
        schema = gs.GroupMomentMembersSchema.model_validate(member)
        await self.session.commit()
        return schema

    async def remove_member(self, user_id: UUID, moment_id: UUID, member_id: UUID) -> gs.GroupMomentMembersSchema:
        await self._require_member(user_id, moment_id)
        member = await self._member_in_moment(moment_id, member_id)
        member.status = "REMOVED"
        member.left_at = _now()
        await self.session.flush()
        schema = gs.GroupMomentMembersSchema.model_validate(member)
        await self.session.commit()
        return schema

    # ================================================================== #
    # expenses
    # ================================================================== #
    async def list_expenses(self, user_id: UUID, moment_id: UUID, *, page: int = 1, per_page: int = 20) -> Page:
        await self._access(user_id, moment_id)
        return await self._page(
            self.expenses_repo, gs.GroupExpensesSchema,
            filters={"moment_id": moment_id}, order_by="-expense_date", page=page, per_page=per_page,
        )

    async def create_expense(
        self,
        user_id: UUID,
        moment_id: UUID,
        *,
        module_context: str,
        category: str,
        expense_name: str,
        amount: Decimal,
        expense_date,
        paid_by_member_id: UUID | None = None,
        notes: str | None = None,
        splits: Sequence[Mapping[str, Any]] = (),
    ) -> gs.GroupExpensesSchema:
        payer_id = await self._resolve_member_id(user_id, moment_id, paid_by_member_id)
        expense = await self.expenses_repo.create(
            {
                "moment_id": moment_id,
                "module_context": module_context,
                "category": category,
                "expense_name": expense_name,
                "amount": amount,
                "expense_date": expense_date,
                "paid_by_member_id": payer_id,
                "status": "RECORDED",
                "notes": notes,
            }
        )
        await self.session.refresh(expense)
        for split in splits:
            await self.expense_splits_repo.create({**dict(split), "expense_id": expense.expense_id})
        schema = gs.GroupExpensesSchema.model_validate(expense)
        await self.session.commit()
        return schema

    # ================================================================== #
    # purchases (life360 shared_purchase_items)
    # ================================================================== #
    async def list_purchases(self, user_id: UUID, moment_id: UUID, *, page: int = 1, per_page: int = 20) -> Page:
        await self._access(user_id, moment_id)
        return await self._page(
            self.purchase_items_repo, ls.SharedPurchaseItemsSchema,
            filters={"moment_id": moment_id}, order_by="-created_at", page=page, per_page=per_page,
        )

    async def create_purchase(
        self, user_id: UUID, moment_id: UUID, *, data: Mapping[str, Any]
    ) -> ls.SharedPurchaseItemsSchema:
        member_id = await self._resolve_member_id(user_id, moment_id, None)
        schema = await self._created(
            self.purchase_items_repo, ls.SharedPurchaseItemsSchema,
            {**dict(data), "moment_id": moment_id, "status": "PROPOSED", "created_by": member_id},
        )
        await self.session.commit()
        return schema

    # ================================================================== #
    # shared living (life360 shared_living_tasks)
    # ================================================================== #
    async def list_shared_living_tasks(self, user_id: UUID, moment_id: UUID, *, page: int = 1, per_page: int = 20) -> Page:
        await self._access(user_id, moment_id)
        return await self._page(
            self.living_tasks_repo, ls.SharedLivingTasksSchema,
            filters={"moment_id": moment_id}, order_by="due_date", page=page, per_page=per_page,
        )

    async def create_shared_living_task(
        self, user_id: UUID, moment_id: UUID, *, data: Mapping[str, Any]
    ) -> ls.SharedLivingTasksSchema:
        await self._require_member(user_id, moment_id)
        schema = await self._created(
            self.living_tasks_repo, ls.SharedLivingTasksSchema,
            {**dict(data), "moment_id": moment_id, "status": "TO_DO"},
        )
        await self.session.commit()
        return schema

    # ================================================================== #
    # events (group work items of type EVENT)
    # ================================================================== #
    async def list_events(self, user_id: UUID, moment_id: UUID, *, page: int = 1, per_page: int = 20) -> Page:
        await self._access(user_id, moment_id)
        return await self._page(
            self.work_items_repo, gs.GroupMomentWorkItemsSchema,
            filters={"moment_id": moment_id, "work_item_type": "EVENT"},
            order_by="-created_at", page=page, per_page=per_page,
        )

    async def create_event(
        self, user_id: UUID, moment_id: UUID, *, data: Mapping[str, Any]
    ) -> gs.GroupMomentWorkItemsSchema:
        member_id = await self._resolve_member_id(user_id, moment_id, None)
        payload = dict(data)
        payload.update(
            {
                "moment_id": moment_id,
                "work_item_type": "EVENT",
                "status": "OPEN",
                "created_by": member_id,
            }
        )
        schema = await self._created(self.work_items_repo, gs.GroupMomentWorkItemsSchema, payload)
        await self.session.commit()
        return schema

    # ================================================================== #
    # polls
    # ================================================================== #
    async def list_polls(self, user_id: UUID, moment_id: UUID, *, page: int = 1, per_page: int = 20) -> Page:
        await self._access(user_id, moment_id)
        return await self._page(
            self.polls_repo, gs.GroupPollsSchema,
            filters={"moment_id": moment_id}, order_by="-created_at", page=page, per_page=per_page,
        )

    async def create_poll(
        self,
        user_id: UUID,
        moment_id: UUID,
        *,
        category: str,
        question: str,
        poll_type: str,
        is_anonymous: bool,
        allow_multiple_votes: bool,
        end_date,
        options: Sequence[Mapping[str, Any]],
    ) -> GroupPollDetail:
        member_id = await self._resolve_member_id(user_id, moment_id, None)
        poll = await self.polls_repo.create(
            {
                "moment_id": moment_id,
                "category": category,
                "question": question,
                "poll_type": poll_type,
                "is_anonymous": is_anonymous,
                "allow_multiple_votes": allow_multiple_votes,
                "status": "OPEN",
                "created_by": member_id,
                "end_date": end_date,
            }
        )
        await self.session.refresh(poll)
        option_objs = []
        for idx, opt in enumerate(options, start=1):
            option_objs.append(
                await self.poll_options_repo.create(
                    {
                        "poll_id": poll.poll_id,
                        "option_text": opt["option_text"],
                        "sort_order": opt.get("sort_order") or idx,
                    }
                )
            )
        for obj in option_objs:
            await self.session.refresh(obj)
        detail = GroupPollDetail(
            poll=gs.GroupPollsSchema.model_validate(poll),
            options=[gs.GroupPollOptionsSchema.model_validate(o) for o in option_objs],
            tally={str(o.option_id): 0 for o in option_objs},
        )
        await self.session.commit()
        return detail

    async def get_poll(self, user_id: UUID, moment_id: UUID, poll_id: UUID) -> GroupPollDetail:
        await self._access(user_id, moment_id)
        poll = await self.polls_repo.get_by_id(poll_id)
        if poll is None or poll.moment_id != moment_id:
            raise NotFoundError("Poll not found in this moment")
        options = await self.poll_options_repo.list(filters={"poll_id": poll_id}, order_by="sort_order", limit=None)
        votes = await self.poll_votes_repo.list(filters={"poll_id": poll_id}, limit=None)
        tally: dict[str, int] = {str(o.option_id): 0 for o in options}
        for v in votes:
            tally[str(v.option_id)] = tally.get(str(v.option_id), 0) + 1
        return GroupPollDetail(
            poll=gs.GroupPollsSchema.model_validate(poll),
            options=[gs.GroupPollOptionsSchema.model_validate(o) for o in options],
            tally=tally,
        )

    async def vote_poll(self, user_id: UUID, moment_id: UUID, poll_id: UUID, option_id: UUID) -> gs.GroupPollVotesSchema:
        member_id = await self._resolve_member_id(user_id, moment_id, None)
        poll = await self.polls_repo.get_by_id(poll_id)
        if poll is None or poll.moment_id != moment_id:
            raise NotFoundError("Poll not found in this moment")
        if poll.status != "OPEN":
            raise StateTransitionError("Poll is not open for voting")
        option = await self.poll_options_repo.get_by_id(option_id)
        if option is None or option.poll_id != poll_id:
            raise ValidationError("option_id does not belong to this poll")
        if not poll.allow_multiple_votes and await self.poll_votes_repo.exists(
            poll_id=poll_id, voter_member_id=member_id
        ):
            raise ValidationError("You have already voted in this poll")
        schema = await self._created(
            self.poll_votes_repo, gs.GroupPollVotesSchema,
            {"poll_id": poll_id, "option_id": option_id, "voter_member_id": member_id},
        )
        await self.session.commit()
        return schema

    async def close_poll(self, user_id: UUID, moment_id: UUID, poll_id: UUID) -> gs.GroupPollsSchema:
        await self._require_member(user_id, moment_id)
        poll = await self.polls_repo.get_by_id(poll_id)
        if poll is None or poll.moment_id != moment_id:
            raise NotFoundError("Poll not found in this moment")
        if poll.status != "OPEN":
            raise StateTransitionError("Only OPEN polls can be closed")
        poll.status = "CLOSED"
        poll.updated_at = _now()
        await self.session.flush()
        schema = gs.GroupPollsSchema.model_validate(poll)
        await self.session.commit()
        return schema

    # ================================================================== #
    # activities / quick add / pulse
    # ================================================================== #
    async def list_activities(self, user_id: UUID, moment_id: UUID, *, page: int = 1, per_page: int = 20) -> Page:
        await self._access(user_id, moment_id)
        return await self._page(
            self.live_feed_repo, gs.GroupLiveFeedSchema,
            filters={"moment_id": moment_id, "is_hidden": False}, order_by="-created_at", page=page, per_page=per_page,
        )

    async def quick_add(
        self,
        user_id: UUID,
        moment_id: UUID,
        *,
        module_code: str,
        event_ref_table: str,
        event_ref_id: UUID,
        event_action: str = "CREATED",
        event_payload_json: Mapping[str, Any] | None = None,
    ) -> gs.GroupQuickAddEventsSchema:
        member_id = await self._resolve_member_id(user_id, moment_id, None)
        schema = await self._created(
            self.quick_add_repo, gs.GroupQuickAddEventsSchema,
            {
                "moment_id": moment_id,
                "module_code": module_code,
                "event_ref_table": event_ref_table,
                "event_ref_id": event_ref_id,
                "event_action": event_action,
                "created_by": member_id,
                "event_payload_json": dict(event_payload_json) if event_payload_json is not None else None,
            },
        )
        await self.session.commit()
        return schema

    async def get_pulse(self, user_id: UUID, moment_id: UUID, *, limit: int = 20) -> list[gs.GroupPulseSnapshotsSchema]:
        await self._access(user_id, moment_id)
        return await self._list(
            self.pulse_repo, gs.GroupPulseSnapshotsSchema,
            filters={"moment_id": moment_id}, order_by="-snapshot_date", limit=limit,
        )

    # ================================================================== #
    # memory / analytics
    # ================================================================== #
    async def memory_overview(self, user_id: UUID, moment_id: UUID) -> GroupMemoryOverviewResponse:
        await self._access(user_id, moment_id)
        f = {"moment_id": moment_id}
        return GroupMemoryOverviewResponse(
            entries=await self._list(self.memory_entries_repo, gs.GroupMemoryEntriesSchema, filters=f, order_by="-memory_date", limit=25),
            patterns=await self._list(self.memory_patterns_repo, gs.GroupMemoryPatternsSchema, filters={**f, "status": "ACTIVE"}, order_by="-confidence_score", limit=25),
            snapshots=await self._list(self.memory_snapshots_repo, gs.GroupMemorySnapshotsSchema, filters=f, order_by="-snapshot_date", limit=10),
        )

    async def analytics(self, user_id: UUID, moment_id: UUID) -> GroupAnalyticsResponse:
        await self._access(user_id, moment_id)
        f = {"moment_id": moment_id}
        counts = GroupAnalyticsCounts(
            members=await self.members_repo.count(filters=f),
            active_members=await self.members_repo.count(filters={**f, "status": "ACTIVE"}),
            expenses=await self.expenses_repo.count(filters=f),
            open_events=await self.work_items_repo.count(filters={**f, "work_item_type": "EVENT", "status": "OPEN"}),
            open_polls=await self.polls_repo.count(filters={**f, "status": "OPEN"}),
            memories=await self.memory_entries_repo.count(filters=f),
        )
        return GroupAnalyticsResponse(
            counts=counts,
            insights=await self._list(self.insights_repo, gs.GroupAiInsightsSchema, filters={**f, "is_active": True}, order_by="-generated_at", limit=10),
            recommendations=await self._list(self.recommendations_repo, gs.GroupRecommendationsSchema, filters={**f, "status": "OPEN"}, order_by="-impact_score", limit=10),
            health=await self._list(self.health_repo, gs.GroupHealthSnapshotsSchema, filters=f, order_by="-snapshot_date", limit=5),
            people_impact=await self._list(self.impact_repo, gs.GroupPeopleImpactScoresSchema, filters=f, order_by="rank_no", limit=10),
        )
