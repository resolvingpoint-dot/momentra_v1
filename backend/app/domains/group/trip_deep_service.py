"""Contract-first service for the trips *deep* modules.

Backs live-workspace, corpus, settlements, approvals, plans, contributions,
expenses, quick-add contexts, guests, attachments and trip-creation-options.
Reads return schema-valid empty/seeded shapes; writes echo the submitted values
into a valid response (no Postgres-only trip tables required, so it works under
the test ``MockSession``).
"""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.storage import build_storage_path, build_upload_url
from app.domains.group import moment_store as store
from app.domains.group.activity.engine import GroupActivityEngine
from app.domains.group.activity.types import ActivityType
from app.domains.group.settlements.service import SettlementService, cheap_life_preview
from app.domains.group import trip_deep_schemas as d
from app.domains.group.read_schemas import QuickAddOption
from app.domains.moments.models import MomentModel
from app.domains.moments.repository import MomentRepository


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _opts(*pairs: tuple[str, str]) -> list[QuickAddOption]:
    return [QuickAddOption(id=i, label=l) for i, l in pairs]


def _to_minor(value, default: int = 0) -> int:
    if value in (None, ""):
        return default
    try:
        return int(round(float(str(value)) * 100))
    except (ValueError, TypeError):
        return default


class TripDeepService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.moments = MomentRepository(session)
        self.activity_engine = GroupActivityEngine(session)

    async def _require(self, user_id: UUID, moment_id: UUID) -> MomentModel:
        from app.domains.group.access import require_group_moment_access

        return await require_group_moment_access(self.session, user_id, moment_id)

    @staticmethod
    def _name(moment: MomentModel) -> str:
        return moment.title or "Your Trip"

    # ----- live-workspace ------------------------------------------------ #
    async def live_workspace(self, user_id: UUID, moment_id: UUID) -> dict:
        m = await self._require(user_id, moment_id)
        name = self._name(m)
        is_active = (m.status or "DRAFT") == "ACTIVE"
        return d.TripLiveWorkspace(
            moment_id=str(m.id),
            header=d.LiveWorkspaceHeader(
                moment_name=name,
                status_line="Everything happening in this trip.",
                stage_label="Live" if is_active else "Setup",
            ),
            hero=d.LiveWorkspaceHero(title=name, subtitle="The shared workspace for your trip."),
            filter_chips=[
                {"id": "all", "label": "All"},
                {"id": "plans", "label": "Plans"},
                {"id": "expenses", "label": "Expenses"},
            ],
        ).model_dump(mode="json")

    # ----- corpus -------------------------------------------------------- #
    async def corpus(self, user_id: UUID, moment_id: UUID) -> dict:
        m = await self._require(user_id, moment_id)
        return d.TripCorpusSummary(moment_id=str(m.id), trip_name=self._name(m)).model_dump(mode="json")

    async def set_custodian(self, user_id: UUID, moment_id: UUID, body: dict) -> dict:
        m = await self._require(user_id, moment_id)
        return d.TripCorpusSummary(
            moment_id=str(m.id),
            trip_name=self._name(m),
            custodian_user_id=str(body.get("custodian_user_id") or "") or None,
        ).model_dump(mode="json")

    # ----- settlements --------------------------------------------------- #
    async def settlements(self, user_id: UUID, moment_id: UUID) -> dict:
        m = await self._require(user_id, moment_id)
        svc = SettlementService(self.session)
        preview = svc.preview_for_moment(m)
        life = cheap_life_preview(m) or {}
        pending = [s.model_dump(mode="json") for s in preview.suggestions]
        members = store.guest_summaries(m)
        status_line = (
            "All balances are settled."
            if not pending
            else f"{len(pending)} settlement suggestion{'s' if len(pending) != 1 else ''} ready."
        )
        return d.TripSettlementContext(
            moment_id=str(m.id),
            trip_name=self._name(m),
            status_line=status_line,
            balance_sync_percent=100.0 if not pending else max(0.0, 100.0 - len(pending) * 15.0),
            balance_insight=str(
                life.get("balance_insight")
                or preview.balance_insight
                or "Nobody owes anything yet — log an expense to get started."
            ),
            harmony_label=str(life.get("harmony_label") or preview.harmony_label or "In harmony"),
            pending_balances=pending,
            participants=members,
            guests=members,
        ).model_dump(mode="json")

    async def restore_balance(self, user_id: UUID, moment_id: UUID) -> dict:
        return await self.settlements(user_id, moment_id)

    # ----- approvals ----------------------------------------------------- #
    async def approvals(self, user_id: UUID, moment_id: UUID) -> dict:
        m = await self._require(user_id, moment_id)
        return d.TripApprovalContext(
            moment_id=str(m.id),
            trip_name=self._name(m),
            status_line="No decisions pending.",
            sync_insight="Start a poll to align the group on a decision.",
            selected_decision_slug="",
        ).model_dump(mode="json")

    async def cast_vote(self, user_id: UUID, moment_id: UUID, decision_id: str, body: dict) -> dict:
        await self._require(user_id, moment_id)
        return d.TripApprovalDecisionDetail(
            id=decision_id,
            slug=decision_id,
            title="Decision",
            current_user_vote_status=str(body.get("status") or "yes"),
        ).model_dump(mode="json")

    async def request_approval(self, user_id: UUID, moment_id: UUID, decision_id: str) -> dict:
        return await self.approvals(user_id, moment_id)

    async def create_poll(self, user_id: UUID, moment_id: UUID, body: dict) -> dict:
        options = body.get("options") or []
        allow_multiple = body.get("allow_multiple_answers")
        if allow_multiple is None:
            poll_type = str(body.get("poll_type") or "single").lower()
            allow_multiple = poll_type in {
                "multiple",
                "multi",
                "multi_choice",
                "multiple_choice",
            }
        else:
            allow_multiple = bool(allow_multiple)
        poll_type = "multiple" if allow_multiple else "single"
        row = await self.activity_engine.write(
            user_id,
            moment_id,
            ActivityType.POLL,
            {
                "question": str(body.get("question") or "Poll"),
                "options": options,
                "status": "open",
                "allow_multiple_answers": allow_multiple,
                "poll_type": poll_type,
            },
        )
        return d.TripApprovalPollCard(
            id=row["id"],
            question=str(row.get("question") or "Poll"),
            status="open",
            options=[{"id": uuid4().hex, "label": str(o), "vote_count": 0, "percent": 0.0} for o in options],
        ).model_dump(mode="json")

    async def cast_poll_vote(self, user_id: UUID, moment_id: UUID, poll_id: str, body: dict) -> dict:
        await self._require(user_id, moment_id)
        return d.TripApprovalPollCard(
            id=poll_id,
            question="Poll",
            status="open",
            total_votes=1,
        ).model_dump(mode="json")

    # ----- plans --------------------------------------------------------- #
    async def plan_context(self, user_id: UUID, moment_id: UUID, category: str) -> dict:
        m = await self._require(user_id, moment_id)
        return d.TripPlanContext(
            moment_id=str(m.id),
            trip_name=self._name(m),
            status_line="Build your trip plan.",
            selected_category=category,
            categories=[
                {"id": "stay", "label": "Stay", "icon": "hotel", "item_count": 0},
                {"id": "travel", "label": "Travel", "icon": "flight", "item_count": 0},
                {"id": "activities", "label": "Activities", "icon": "hiking", "item_count": 0},
            ],
            ai_insight="Add your first plan item to start coordinating.",
        ).model_dump(mode="json")

    async def create_plan(self, user_id: UUID, moment_id: UUID, body: dict) -> dict:
        m = await self._require(user_id, moment_id)
        row = await self.activity_engine.write(
            user_id,
            moment_id,
            ActivityType.PLANNING_ITEM,
            {
                "category": str(body.get("category") or "stay"),
                "title": str(body.get("title") or "Plan item"),
                "details": body.get("details") or {},
                "needs_coordination": bool(body.get("needs_coordination") or False),
                "participant_user_ids": [str(x) for x in (body.get("participant_user_ids") or [])],
            },
        )
        return d.GroupTripPlanResponse(
            id=row["id"],
            moment_id=str(m.id),
            category=str(row.get("category") or "stay"),
            title=str(row.get("title") or "Plan item"),
            details=row.get("details") or {},
            needs_coordination=bool(row.get("needs_coordination") or False),
            participant_user_ids=list(row.get("participant_user_ids") or []),
        ).model_dump(mode="json")

    # ----- contributions ------------------------------------------------- #
    async def contribution_context(self, user_id: UUID, moment_id: UUID, pool: str) -> dict:
        m = await self._require(user_id, moment_id)
        return d.TripContributionContext(
            moment_id=str(m.id),
            trip_name=self._name(m),
            pools=[{"id": pool, "label": pool.title(), "icon": "wallet", "raised_minor": 0}],
            ai_insight="Invite the group to start contributing.",
            status_line="No contributions yet.",
        ).model_dump(mode="json")

    async def create_contribution(self, user_id: UUID, moment_id: UUID, body: dict) -> dict:
        m = await self._require(user_id, moment_id)
        row = await self.activity_engine.write(
            user_id,
            moment_id,
            ActivityType.CONTRIBUTION,
            {
                "contributor_user_id": str(body.get("contributor_user_id") or user_id),
                "amount_minor": int(body.get("amount_minor") or 0),
                "currency_code": str(body.get("currency_code") or "INR"),
                "title": body.get("title"),
                "allocation_category": body.get("allocation_category"),
            },
        )
        return d.GroupContributionResponse(
            id=row["id"],
            moment_id=str(m.id),
            contributor_user_id=row["contributor_user_id"],
            amount_minor=row["amount_minor"],
            currency_code=row["currency_code"],
            title=row.get("title"),
            allocation_category=row.get("allocation_category"),
        ).model_dump(mode="json")

    # ----- expenses ------------------------------------------------------ #
    def _expense_response(self, moment: MomentModel, row: dict) -> dict:
        title = str(row.get("title") or row.get("description") or "Expense")
        paid_by = str(row.get("paid_by_participant_id") or row.get("paid_by_user_id") or "")
        occurred = str(row.get("occurred_at") or row.get("expense_date") or row.get("created_at") or _now_iso())
        split_style = str(row.get("split_style") or row.get("split_type") or "EQUAL").upper()
        return d.GroupExpenseResponse(
            id=str(row.get("id") or ""),
            moment_id=str(moment.id),
            paid_by_user_id=paid_by,
            paid_by_participant_id=paid_by or None,
            amount_minor=int(row.get("amount_minor") or 0),
            currency_code=str(row.get("currency_code") or "INR"),
            title=title,
            description=title,
            category=row.get("category") or row.get("category_code"),
            category_code=row.get("category_code") or row.get("category"),
            subcategory_code=row.get("subcategory_code"),
            split_type=str(row.get("split_type") or split_style.lower()),
            split_style=split_style,
            expense_date=occurred,
            occurred_at=occurred,
            participant_ids=list(row.get("participant_ids") or []),
            split_details=row.get("split_details"),
            notes=row.get("notes"),
            client_request_id=row.get("client_request_id"),
            is_settled=bool(row.get("is_settled")),
            shares=list(row.get("shares") or []),
        ).model_dump(mode="json")

    async def _ensure_members(self, user_id: UUID, moment: MomentModel) -> list[dict]:
        members = store.list_accepted_members(moment)
        owner_id = str(getattr(moment, "user_id", None) or user_id)
        if owner_id and not any(
            str(m.get("user_id") or m.get("id") or "") == owner_id for m in members
        ):
            display_name = "You"
            try:
                from sqlalchemy import select
                from app.domains.users.models import UserModel

                result = await self.session.execute(
                    select(UserModel).where(UserModel.id == moment.user_id)
                )
                user = result.scalar_one_or_none()
                if user and getattr(user, "display_name", None):
                    display_name = str(user.display_name)
            except Exception:
                pass
            store.ensure_creator_organizer(moment, moment.user_id or user_id, display_name=display_name)
            await self.session.flush()
            members = store.list_accepted_members(moment)
        return members

    async def _user_default_currency(self, user_id: UUID) -> str | None:
        try:
            from app.domains.preferences.repository import UserPreferenceRepository

            pref = await UserPreferenceRepository(self.session).get_by_user_id(user_id)
            if pref and pref.default_currency_code:
                return str(pref.default_currency_code)
        except Exception:
            pass
        return None

    async def list_expenses(self, user_id: UUID, moment_id: UUID) -> list[dict]:
        m = await self._require(user_id, moment_id)
        await self._ensure_members(user_id, m)
        return [
            self._expense_response(m, row)
            for row in store.list_items(m, "expenses")
            if not row.get("deleted")
        ]

    async def create_expense(self, user_id: UUID, moment_id: UUID, body: dict) -> dict:
        from app.domains.group import expense_contract as ec

        m = await self._require(user_id, moment_id)
        members = await self._ensure_members(user_id, m)
        state = store.read_state(m)
        payload = state.get("payload") or {}
        user_default = await self._user_default_currency(user_id)
        default_currency = ec.resolve_group_default_currency(payload, user_default=user_default)
        multi = ec.allow_multi_currency(payload)

        client_request_id = body.get("client_request_id")
        existing = store.find_by_client_request_id(m, "expenses", client_request_id)
        if existing is not None:
            return self._expense_response(m, existing)

        # Soft-compat: legacy posts without title still accepted via description.
        if not body.get("title") and body.get("description"):
            body = {**body, "title": body.get("description")}

        normalized = ec.normalize_expense_write(
            body,
            user_id=str(user_id),
            members=members,
            default_currency=default_currency,
            multi_currency=multi,
            soft_default_participants=True,
            guests=store.guest_summaries(m),
        )
        if not normalized.get("expense_date"):
            normalized["expense_date"] = _now_iso()
            normalized["occurred_at"] = normalized["expense_date"]

        row = await self.activity_engine.write(
            user_id,
            moment_id,
            ActivityType.EXPENSE,
            normalized,
        )
        return self._expense_response(m, row)

    async def update_expense(
        self, user_id: UUID, moment_id: UUID, expense_id: str, body: dict
    ) -> dict:
        from app.domains.group import expense_contract as ec
        from app.domains.group.projection_cache import invalidate_group_projections

        m = await self._require(user_id, moment_id)
        members = await self._ensure_members(user_id, m)
        current = next(
            (
                row
                for row in store.list_items(m, "expenses")
                if str(row.get("id")) == str(expense_id) and not row.get("deleted")
            ),
            None,
        )
        if current is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")

        merged = {**current, **(body or {})}
        if not merged.get("title") and merged.get("description"):
            merged["title"] = merged.get("description")
        state = store.read_state(m)
        payload = state.get("payload") or {}
        user_default = await self._user_default_currency(user_id)
        default_currency = ec.resolve_group_default_currency(payload, user_default=user_default)
        multi = ec.allow_multi_currency(payload)
        normalized = ec.normalize_expense_write(
            merged,
            user_id=str(user_id),
            members=members,
            default_currency=default_currency,
            multi_currency=multi,
            soft_default_participants=True,
            guests=store.guest_summaries(m),
        )
        if not normalized.get("expense_date"):
            normalized["expense_date"] = current.get("expense_date") or _now_iso()
            normalized["occurred_at"] = normalized["expense_date"]
        # Preserve identity fields
        normalized["id"] = current["id"]
        normalized["created_at"] = current.get("created_at")
        normalized["client_request_id"] = current.get("client_request_id") or normalized.get(
            "client_request_id"
        )

        updated = store.update_item(m, "expenses", expense_id, normalized)
        if updated is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
        await self.session.flush()
        await invalidate_group_projections(
            user_id,
            moment_id,
            moment_type=m.moment_type or "SHARED_EXPERIENCE",
            reason="expense:update",
        )
        return self._expense_response(m, updated)

    async def delete_expense(self, user_id: UUID, moment_id: UUID, expense_id: str) -> dict:
        from app.domains.group.projection_cache import invalidate_group_projections

        m = await self._require(user_id, moment_id)
        deleted = store.soft_delete_item(m, "expenses", expense_id)
        if deleted is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
        await self.session.flush()
        await invalidate_group_projections(
            user_id,
            moment_id,
            moment_type=m.moment_type or "SHARED_EXPERIENCE",
            reason="expense:delete",
        )
        return {"status": "deleted", "expense_id": expense_id}

    async def split_expense(self, user_id: UUID, moment_id: UUID, expense_id: str, body: dict) -> dict:
        # Prefer real patch when body carries split fields; keep echo for empty legacy clients.
        if body and any(
            k in body
            for k in (
                "split_style",
                "split_type",
                "split_details",
                "splits",
                "participant_ids",
                "amount_minor",
            )
        ):
            return await self.update_expense(user_id, moment_id, expense_id, body)
        m = await self._require(user_id, moment_id)
        return d.GroupExpenseResponse(
            id=expense_id,
            moment_id=str(m.id),
            paid_by_user_id=str(body.get("paid_by_user_id") or user_id),
            amount_minor=int(body.get("amount_minor") or 0),
            currency_code=str(body.get("currency_code") or "INR"),
            description=str(body.get("description") or body.get("title") or "Expense"),
            title=str(body.get("title") or body.get("description") or "Expense"),
            split_type=str(body.get("split_type") or "equal"),
            expense_date=str(body.get("expense_date") or _now_iso()),
        ).model_dump(mode="json")

    # ----- quick-add contexts -------------------------------------------- #
    async def participant_context(self, user_id: UUID, moment_id: UUID) -> dict:
        m = await self._require(user_id, moment_id)
        name = self._name(m)
        return d.ParticipantQuickAddContext(
            moment_id=str(m.id),
            trip_name=name,
            status_line="Add a participant.",
            relationship_types=_opts(("friend", "Friend"), ("family", "Family"), ("colleague", "Colleague")),
            statuses=_opts(("confirmed", "Confirmed"), ("invited", "Invited")),
            guests=store.guest_summaries(m),
            invite=d.InviteQuickAddContextOut(share_message=f"Join {name} on Momentra."),
        ).model_dump(mode="json")

    async def booking_context(self, user_id: UUID, moment_id: UUID) -> dict:
        m = await self._require(user_id, moment_id)
        return d.BookingQuickAddContext(
            moment_id=str(m.id),
            trip_name=self._name(m),
            status_line="Add a booking.",
            booking_types=_opts(("stay", "Stay"), ("travel", "Travel"), ("activity", "Activity")),
            booking_statuses=_opts(("planned", "Planned"), ("confirmed", "Confirmed")),
        ).model_dump(mode="json")

    async def planning_item_context(self, user_id: UUID, moment_id: UUID) -> dict:
        m = await self._require(user_id, moment_id)
        return d.PlanningItemQuickAddContext(
            moment_id=str(m.id),
            trip_name=self._name(m),
            status_line="Add a planning item.",
            planning_categories=_opts(("stay", "Stay"), ("travel", "Travel"), ("activities", "Activities")),
            planning_statuses=_opts(("idea", "Idea"), ("booked", "Booked")),
        ).model_dump(mode="json")

    async def expense_context(self, user_id: UUID, moment_id: UUID) -> dict:
        from app.domains.group import expense_contract as ec

        m = await self._require(user_id, moment_id)
        members = await self._ensure_members(user_id, m)
        guests = store.guest_summaries(m)
        payers = [
            {"id": str(mem["id"]), "display_name": mem["display_name"], "role_code": mem.get("role_code")}
            for mem in members
        ]
        # Guests as supplemental payers when not already in members
        seen = {p["id"] for p in payers}
        for guest in guests:
            gid = str(guest.get("id") or "")
            if not gid or gid in seen:
                continue
            seen.add(gid)
            payers.append(
                {
                    "id": gid,
                    "display_name": str(guest.get("full_name") or "Guest").strip() or "Guest",
                }
            )
        state = store.read_state(m)
        payload = state.get("payload") or {}
        user_default = await self._user_default_currency(user_id)
        default_currency = ec.resolve_group_default_currency(payload, user_default=user_default)
        multi = ec.allow_multi_currency(payload)
        currencies = [
            QuickAddOption(
                id=str(c["code"]),
                label=f"{c['code']} — {c.get('label') or c['code']}",
            )
            for c in ec.active_currencies()
        ]
        default_payer = ec.resolve_default_payer(members, str(user_id))
        participant_rows = [
            {
                "id": str(mem["id"]),
                "display_name": mem["display_name"],
                "role_code": mem.get("role_code"),
                "user_id": mem.get("user_id"),
            }
            for mem in members
        ]
        from app.domains.reference_data.catalog import get_reference_catalog

        catalog = get_reference_catalog()
        expense_cat_opts = [
            {
                "id": item["code"],
                "code": item["code"],
                "label": item["label"],
                "children": [
                    {
                        "id": c["code"],
                        "code": c["code"],
                        "label": c["label"],
                    }
                    for c in (item.get("children") or [])
                    if c.get("is_active", True)
                ],
            }
            for item in catalog.get("expense_categories", active_only=True)
        ]
        return d.ExpenseQuickAddContext(
            moment_id=str(m.id),
            trip_name=self._name(m),
            status_line="Log a trip expense.",
            expense_categories=expense_cat_opts,
            currencies=currencies,
            split_types=_opts(
                ("EQUAL", "Equal"),
                ("EXACT", "Exact"),
                ("PERCENTAGE", "Percentage"),
                ("SHARES", "Shares"),
            ),
            guests=guests,
            payers=payers,
            participants=participant_rows,
            members=participant_rows,
            default_currency_code=default_currency,
            allow_multi_currency=multi,
            default_paid_by_participant_id=default_payer,
        ).model_dump(mode="json")

    async def _expense_payers(
        self, user_id: UUID, moment_id: UUID, guests: list[dict]
    ) -> list[dict]:
        """Build Paid-by options from accepted members + guest roster."""
        m = await self._require(user_id, moment_id)
        members = await self._ensure_members(user_id, m)
        payers: list[dict] = []
        seen: set[str] = set()
        for member in members:
            uid = str(member.get("id") or "")
            if not uid or uid in seen:
                continue
            seen.add(uid)
            payers.append(
                {
                    "id": uid,
                    "display_name": member.get("display_name") or "Member",
                }
            )
        for guest in guests:
            gid = str(guest.get("id") or "")
            if not gid or gid in seen:
                continue
            seen.add(gid)
            payers.append(
                {
                    "id": gid,
                    "display_name": str(guest.get("full_name") or "Guest").strip() or "Guest",
                }
            )
        return payers

    async def memory_context(self, user_id: UUID, moment_id: UUID) -> dict:
        m = await self._require(user_id, moment_id)
        return d.MemoryQuickAddContext(
            moment_id=str(m.id),
            trip_name=self._name(m),
            status_line="Capture a memory.",
            memory_categories=_opts(("moment", "Moment"), ("highlight", "Highlight")),
            memory_formats=_opts(
                ("photo", "Photo"),
                ("video", "Video"),
                ("pdf", "PDF"),
                ("note", "Note"),
            ),
            upload_requirements={"max_files": 10, "max_bytes": 10485760},
        ).model_dump(mode="json")

    async def poll_context(self, user_id: UUID, moment_id: UUID) -> dict:
        m = await self._require(user_id, moment_id)
        return d.PollQuickAddContext(
            moment_id=str(m.id),
            trip_name=self._name(m),
            status_line="Start a poll.",
            poll_types=_opts(("single", "Single choice"), ("multiple", "Multiple choice")),
            category_tags=_opts(("stay", "Stay"), ("food", "Food"), ("activity", "Activity")),
        ).model_dump(mode="json")

    async def attendance_context(self, user_id: UUID, moment_id: UUID) -> dict:
        m = await self._require(user_id, moment_id)
        return d.AttendanceQuickAddContext(
            moment_id=str(m.id),
            trip_name=self._name(m),
            status_line="Mark attendance.",
            attendance_types=_opts(("full", "Full trip"), ("partial", "Partial")),
            statuses=_opts(("confirmed", "Confirmed"), ("tentative", "Tentative")),
        ).model_dump(mode="json")

    async def create_attendance(self, user_id: UUID, moment_id: UUID, body: dict) -> dict:
        m = await self._require(user_id, moment_id)
        row = await self.activity_engine.write(
            user_id,
            moment_id,
            ActivityType.ATTENDANCE,
            {
                "member_id": str(body.get("member_id") or user_id),
                "attendance_type": str(body.get("attendance_type") or "full"),
                "status": str(body.get("status") or "CONFIRMED"),
                "notes": body.get("notes"),
                "label": str(body.get("label") or "Attendance"),
            },
        )
        return d.AttendanceResponse(
            id=row["id"],
            moment_id=str(m.id),
            member_id=row["member_id"],
            attendance_type=row["attendance_type"],
            status=row["status"],
            notes=row.get("notes"),
        ).model_dump(mode="json")

    async def vendor_context(self, user_id: UUID, moment_id: UUID) -> dict:
        m = await self._require(user_id, moment_id)
        return d.VendorQuickAddContext(
            moment_id=str(m.id),
            trip_name=self._name(m),
            status_line="Add a vendor or contact.",
            vendor_types=_opts(("service", "Service"), ("venue", "Venue"), ("transport", "Transport"), ("custom", "Custom")),
        ).model_dump(mode="json")

    async def update_context(self, user_id: UUID, moment_id: UUID) -> dict:
        m = await self._require(user_id, moment_id)
        return d.UpdateQuickAddContext(
            moment_id=str(m.id),
            trip_name=self._name(m),
            status_line="Share an update with the group.",
            update_types=_opts(("announcement", "Announcement"), ("reminder", "Reminder"), ("milestone", "Milestone")),
            visibility_options=_opts(("everyone", "Everyone"), ("organizers", "Organizers only")),
        ).model_dump(mode="json")

    async def create_booking(self, user_id: UUID, moment_id: UUID, body: dict) -> dict:
        m = await self._require(user_id, moment_id)
        booking_status = str(body.get("booking_status") or body.get("status") or "confirmed")
        row = await self.activity_engine.write(
            user_id,
            moment_id,
            ActivityType.BOOKING,
            {
                "booking_type": str(body.get("booking_type") or "stay"),
                "provider": body.get("provider"),
                # Dual-write: pulse counters historically read `status`.
                "booking_status": booking_status,
                "status": booking_status,
                "amount_minor": int(body.get("amount_minor") or 0),
                "description": body.get("description"),
                "title": str(body.get("title") or body.get("provider") or "Booking"),
            },
        )
        return d.BookingResponse(
            id=row["id"],
            moment_id=str(m.id),
            booking_type=str(row.get("booking_type") or "stay"),
            provider=row.get("provider"),
            booking_status=str(row.get("booking_status") or row.get("status") or "confirmed"),
            amount_minor=int(row.get("amount_minor") or 0),
            description=row.get("description"),
        ).model_dump(mode="json")

    async def repair_inflated_booking_amounts(
        self,
        user_id: UUID,
        moment_id: UUID,
        *,
        divisor: int = 100,
        min_minor: int = 100_000_000,
    ) -> dict:
        """Undo web Quick Add double *100 on booking amounts (₹3.5Cr → ₹3.5L).

        Only touches non-deleted bookings with amount_minor >= min_minor (default ₹10L),
        which matches double-converted entries of ₹10k+ and leaves normal amounts alone.
        """
        if divisor < 2:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="divisor must be >= 2")
        m = await self._require(user_id, moment_id)
        repaired: list[dict] = []
        for row in store.list_items(m, "bookings"):
            if row.get("deleted"):
                continue
            try:
                amt = int(row.get("amount_minor") or 0)
            except (TypeError, ValueError):
                continue
            if amt < min_minor:
                continue
            new_amt = amt // divisor
            updated = store.update_item(m, "bookings", str(row["id"]), {"amount_minor": new_amt})
            if updated:
                repaired.append(
                    {
                        "id": str(row["id"]),
                        "title": str(row.get("title") or row.get("provider") or ""),
                        "amount_minor_before": amt,
                        "amount_minor_after": new_amt,
                    }
                )
        await self.session.flush()
        from app.domains.group.projection_cache import invalidate_group_projections

        await invalidate_group_projections(
            user_id,
            moment_id,
            moment_type=m.moment_type or "SHARED_EXPERIENCE",
            reason="repair:inflated_booking_amounts",
        )
        return {
            "moment_id": str(m.id),
            "repaired_count": len(repaired),
            "repaired": repaired,
        }

    async def create_vendor(self, user_id: UUID, moment_id: UUID, body: dict) -> dict:
        m = await self._require(user_id, moment_id)
        row = await self.activity_engine.write(
            user_id,
            moment_id,
            ActivityType.VENDOR,
            {
                "vendor_name": str(body.get("vendor_name") or body.get("name") or "Vendor"),
                "vendor_type": body.get("vendor_type"),
                "contact": body.get("contact"),
                "notes": body.get("notes"),
                "name": str(body.get("vendor_name") or body.get("name") or "Vendor"),
            },
        )
        return d.VendorResponse(
            id=row["id"],
            moment_id=str(m.id),
            vendor_name=str(row.get("vendor_name") or row.get("name") or "Vendor"),
            vendor_type=row.get("vendor_type"),
            contact=row.get("contact"),
            notes=row.get("notes"),
        ).model_dump(mode="json")

    async def create_update(self, user_id: UUID, moment_id: UUID, body: dict) -> dict:
        m = await self._require(user_id, moment_id)
        title = str(body.get("title") or "Update")
        row = await self.activity_engine.write(
            user_id,
            moment_id,
            ActivityType.UPDATE,
            {
                "title": title,
                "body": body.get("body") or body.get("message"),
                "update_type": body.get("update_type"),
                "visibility": body.get("visibility"),
                "message": body.get("body") or body.get("message"),
            },
        )
        return d.UpdateResponse(
            id=row["id"],
            moment_id=str(m.id),
            title=title,
            body=row.get("body") or row.get("message"),
            update_type=row.get("update_type"),
            visibility=row.get("visibility"),
        ).model_dump(mode="json")

    async def create_poll_quick_add(self, user_id: UUID, moment_id: UUID, body: dict) -> dict:
        return await self.create_poll(user_id, moment_id, body)

    async def budget_context(self, user_id: UUID, moment_id: UUID) -> dict:
        m = await self._require(user_id, moment_id)
        members = store.list_accepted_members(m)
        participant_count = max(1, len(members))
        existing = None
        for row in reversed(store.list_items(m, "budget_plans")):
            if not row.get("deleted"):
                existing = row
                break
        return d.BudgetQuickAddContext(
            moment_id=str(m.id),
            trip_name=self._name(m),
            status_line="Plan expected costs and contribution requirements.",
            templates=_opts(
                ("weekend", "Weekend getaway"),
                ("adventure", "Adventure trip"),
                ("custom", "Custom"),
            ),
            categories=_opts(
                ("stay", "Stay"),
                ("travel", "Travel"),
                ("food", "Food"),
                ("activities", "Activities"),
            ),
            participant_count=participant_count,
            existing_plan_id=str(existing["id"]) if existing else None,
            default_currency_code="INR",
        ).model_dump(mode="json")

    async def create_budget_plan(self, user_id: UUID, moment_id: UUID, body: dict) -> dict:
        m = await self._require(user_id, moment_id)
        members = store.list_accepted_members(m)
        participant_count = int(body.get("participant_count") or max(1, len(members)) or 1)
        if participant_count < 1:
            participant_count = 1

        if body.get("total_amount_minor") is not None:
            total_minor = int(body.get("total_amount_minor") or 0)
        else:
            total_minor = _to_minor(body.get("total_amount_major"))

        currency = str(body.get("currency_code") or "INR").upper()
        template_id = str(body.get("template_id") or "custom")
        split_method = str(body.get("split_method") or "EQUAL").upper()
        if split_method not in {"EQUAL", "CONTRIBUTION_BASED", "CUSTOM"}:
            split_method = "EQUAL"
        notes = body.get("notes")

        raw_allocs = body.get("allocations") or []
        allocations: list[dict] = []
        if isinstance(raw_allocs, list):
            for item in raw_allocs:
                if not isinstance(item, dict):
                    continue
                code = str(item.get("category_code") or item.get("category") or "").strip().lower()
                if not code:
                    continue
                if item.get("amount_minor") is not None:
                    amt = int(item.get("amount_minor") or 0)
                else:
                    amt = _to_minor(item.get("amount_major") or item.get("amount"))
                pct = item.get("percent")
                try:
                    pct_f = float(pct) if pct is not None and pct != "" else None
                except (TypeError, ValueError):
                    pct_f = None
                allocations.append(
                    {
                        "category_code": code,
                        "amount_minor": amt,
                        "percent": pct_f,
                    }
                )

        # If no allocations provided, equal-split categories from context defaults
        if not allocations and total_minor > 0:
            cats = ["stay", "travel", "food", "activities"]
            base = total_minor // len(cats)
            rem = total_minor - base * len(cats)
            for i, code in enumerate(cats):
                allocations.append(
                    {
                        "category_code": code,
                        "amount_minor": base + (rem if i == 0 else 0),
                        "percent": round(100.0 / len(cats), 2),
                    }
                )

        per_person = None
        if split_method == "EQUAL" and participant_count > 0:
            per_person = total_minor // participant_count

        row = {
            "id": store.new_id(),
            "moment_id": str(m.id),
            "template_id": template_id,
            "total_amount_minor": total_minor,
            "currency_code": currency,
            "allocations": allocations,
            "split_method": split_method,
            "participant_count": participant_count,
            "contribution_per_person_minor": per_person,
            "notes": str(notes).strip() if notes else None,
            "created_at": _now_iso(),
            "updated_at": _now_iso(),
            "created_by": str(user_id),
        }
        store.append_item(m, "budget_plans", row)
        store.append_item(
            m,
            "activities",
            {
                "id": store.new_id(),
                "type": "BUDGET_PLAN",
                "title": "Budget Plan Created",
                "created_at": _now_iso(),
                "ref_id": row["id"],
            },
        )

        return d.BudgetPlanResponse(
            id=row["id"],
            moment_id=str(m.id),
            template_id=template_id,
            total_amount_minor=total_minor,
            currency_code=currency,
            allocations=[d.BudgetAllocationItem(**a) for a in allocations],
            split_method=split_method,
            participant_count=participant_count,
            contribution_per_person_minor=per_person,
            notes=row.get("notes"),
            created_at=row["created_at"],
        ).model_dump(mode="json")

    # ----- guests -------------------------------------------------------- #
    async def create_guest(self, user_id: UUID, moment_id: UUID, body: dict) -> dict:
        m = await self._require(user_id, moment_id)
        full_name = str(
            body.get("full_name") or body.get("display_name") or body.get("name") or "Guest"
        ).strip() or "Guest"
        linked_user = str(body.get("user_id") or body.get("linked_user_id") or "").strip() or None
        guest_payload: dict = {
            "full_name": full_name,
            "phone": body.get("phone"),
            "email": body.get("email"),
            "relationship_type": str(body.get("relationship_type") or "friend"),
            "assigned_role": body.get("assigned_role"),
            "status": str(body.get("status") or "active"),
            "notes": body.get("notes"),
        }
        if linked_user:
            # Stable id for expenses/settlements when guest is a linked Momentra user.
            guest_payload["id"] = linked_user
            guest_payload["user_id"] = linked_user
        row = await self.activity_engine.write(
            user_id,
            moment_id,
            ActivityType.PARTICIPANT,
            guest_payload,
        )
        if linked_user:
            # Settlements prefer runtime.members when any exist (owner is added on
            # activate). Linked guests must be members or they are invisible there.
            state = store.read_state(m)
            rt = state.setdefault("runtime", {})
            members = rt.setdefault("members", [])
            if not any(
                not mem.get("deleted")
                and str(mem.get("user_id") or mem.get("id") or "") == linked_user
                for mem in members
            ):
                members.append(
                    {
                        "id": linked_user,
                        "member_id": linked_user,
                        "user_id": linked_user,
                        "display_name": full_name,
                        "role_code": str(body.get("assigned_role") or "PARTICIPANT").upper(),
                        "status": "ACTIVE",
                        "created_at": store.now_iso(),
                    }
                )
                store.write_state(m, state)
                await self.session.flush()
        return d.GroupMomentGuestResponse(
            id=row["id"],
            moment_id=str(m.id),
            full_name=str(row.get("full_name") or full_name),
            phone=row.get("phone"),
            email=row.get("email"),
            relationship_type=str(row.get("relationship_type") or "friend"),
            assigned_role=row.get("assigned_role"),
            status=str(row.get("status") or "active"),
            created_at=row["created_at"],
        ).model_dump(mode="json")

    # ----- attachments --------------------------------------------------- #
    async def attachment_upload_url(self, user_id: UUID, moment_id: UUID, body: dict) -> dict:
        from fastapi import HTTPException, status

        from app.core.storage import assert_attachment_upload

        m = await self._require(user_id, moment_id)
        try:
            content_type = assert_attachment_upload(
                content_type=body.get("content_type"),
                byte_size=body.get("byte_size"),
                purpose=body.get("purpose"),
            )
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
            ) from exc
        path = build_storage_path(f"trip-attachments/{m.id}", content_type)
        return d.AttachmentUploadUrlResponse(
            upload_url=build_upload_url(path),
            storage_path=path,
        ).model_dump(mode="json")

    async def attachment_confirm(self, user_id: UUID, moment_id: UUID, body: dict) -> dict:
        from app.core.storage import assert_storage_path_under

        m = await self._require(user_id, moment_id)
        raw = str(body.get("storage_path") or "")
        try:
            path = assert_storage_path_under(raw, f"trip-attachments/{m.id}")
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
            ) from exc
        return d.AttachmentConfirmResponse(storage_path=path).model_dump(mode="json")

    # ----- trip-creation-options ----------------------------------------- #
    async def creation_options(self) -> dict:
        return d.TripCreationOptions(
            hero_image_url=(settings.storage_public_base_url.rstrip("/") + "/trips/hero.jpg") if settings.storage_public_base_url else "",
            vibes=[
                d.TripOptionItem(id="chill", label="Chill", icon="beach_access"),
                d.TripOptionItem(id="adventure", label="Adventure", icon="hiking"),
                d.TripOptionItem(id="party", label="Party", icon="celebration"),
                d.TripOptionItem(id="culture", label="Culture", icon="museum"),
            ],
            budget_moods=[
                d.TripOptionItem(id="budget", label="Budget", icon="savings"),
                d.TripOptionItem(id="balanced", label="Balanced", icon="balance"),
                d.TripOptionItem(id="premium", label="Premium", icon="diamond"),
            ],
        ).model_dump(mode="json")
