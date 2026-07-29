"""Composed Group Moment read for GraphQL — AuthZ once, then domain services."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.principal import Principal
from app.authorization import ResourceRef, require
from app.authorization.require import GROUP_MOMENT_VIEW
from app.domains.group import moment_store as store
from app.domains.group.activity.engine import GroupActivityEngine
from app.domains.group.settlements.service import SettlementService
from app.domains.moments.models import MomentModel


@dataclass
class GroupMomentMemberDTO:
    id: str
    display_name: str
    role: str
    user_id: str | None = None


@dataclass
class GroupMomentBalanceDTO:
    member_id: str
    net_amount: int  # minor units
    currency_code: str = "INR"
    display_name: str = ""


@dataclass
class GroupMomentExpenseDTO:
    id: str
    amount: int  # minor units
    currency_code: str = "INR"
    title: str | None = None
    paid_by_id: str | None = None


@dataclass
class GroupMomentActivityDTO:
    id: str
    title: str
    occurred_at: str | None = None


@dataclass
class GroupMomentDetailDTO:
    id: UUID
    title: str | None
    status: str
    members: list[GroupMomentMemberDTO] = field(default_factory=list)
    balances: list[GroupMomentBalanceDTO] = field(default_factory=list)
    expenses: list[GroupMomentExpenseDTO] = field(default_factory=list)
    recent_activity: list[GroupMomentActivityDTO] = field(default_factory=list)


def _expense_from_row(row: dict[str, Any]) -> GroupMomentExpenseDTO:
    paid_by = str(
        row.get("paid_by_participant_id")
        or row.get("paid_by_user_id")
        or row.get("paid_by")
        or ""
    ) or None
    return GroupMomentExpenseDTO(
        id=str(row.get("id") or ""),
        amount=int(row.get("amount_minor") or 0),
        currency_code=str(row.get("currency_code") or "INR"),
        title=str(row.get("title") or row.get("description") or "") or None,
        paid_by_id=paid_by,
    )


def _activity_from_row(row: dict[str, Any]) -> GroupMomentActivityDTO:
    return GroupMomentActivityDTO(
        id=str(row.get("id") or row.get("activity_id") or ""),
        title=str(
            row.get("title") or row.get("summary") or row.get("kind") or "Activity"
        ),
        occurred_at=str(
            row.get("occurred_at") or row.get("created_at") or row.get("at") or ""
        )
        or None,
    )


async def get_group_moment_detail(
    session: AsyncSession,
    principal: Principal,
    moment_id: UUID,
) -> GroupMomentDetailDTO:
    """Load a composed Group Moment view for GraphQL resolvers."""
    moment: MomentModel = await require(
        session,
        principal,
        GROUP_MOMENT_VIEW,
        ResourceRef(kind="group_moment", id=moment_id),
    )

    members_raw = store.list_accepted_members(moment)
    members = [
        GroupMomentMemberDTO(
            id=str(m.get("id") or m.get("member_id") or ""),
            display_name=str(m.get("display_name") or "Member"),
            role=str(m.get("role_code") or m.get("role") or "PARTICIPANT"),
            user_id=str(m.get("user_id") or "") or None,
        )
        for m in members_raw
        if m.get("id") or m.get("member_id")
    ]

    balances: list[GroupMomentBalanceDTO] = []
    try:
        preview = await SettlementService(session).preview(principal.user_id, moment_id)
        for bal in preview.get("member_balances") or []:
            balances.append(
                GroupMomentBalanceDTO(
                    member_id=str(bal.get("member_id") or ""),
                    net_amount=int(bal.get("net_minor") or 0),
                    currency_code=str(bal.get("currency_code") or "INR"),
                    display_name=str(bal.get("display_name") or ""),
                )
            )
    except Exception:
        # Settlement preview may fail for moments without expense payload; still return shell.
        balances = []

    expenses = [
        _expense_from_row(row)
        for row in store.list_items(moment, "expenses")
        if not row.get("deleted")
    ]
    # Newest first when timestamps present.
    expenses.sort(key=lambda e: e.id, reverse=True)

    try:
        timeline = await GroupActivityEngine(session).list_timeline(
            principal.user_id, moment_id
        )
    except Exception:
        timeline = [a for a in store.list_activities(moment) if not a.get("deleted")]
    activities = [_activity_from_row(row) for row in timeline]

    return GroupMomentDetailDTO(
        id=moment.id,
        title=moment.title,
        status=str(moment.status or ""),
        members=members,
        balances=balances,
        expenses=expenses,
        recent_activity=activities,
    )
