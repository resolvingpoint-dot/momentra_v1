"""GroupMoment GraphQL types — thin field resolvers over application DTO."""
from __future__ import annotations

from uuid import UUID

import strawberry
from strawberry.types import Info

from app.api.graphql.types.common import Connection, Edge, PageInfo, paginate_list
from app.application.queries.group_moment_detail import (
    GroupMomentActivityDTO,
    GroupMomentBalanceDTO,
    GroupMomentDetailDTO,
    GroupMomentExpenseDTO,
    GroupMomentMemberDTO,
)


@strawberry.type
class GroupMomentMember:
    id: strawberry.ID
    display_name: str
    role: str
    user_id: strawberry.ID | None = None

    @classmethod
    def from_dto(cls, dto: GroupMomentMemberDTO) -> GroupMomentMember:
        return cls(
            id=strawberry.ID(dto.id),
            display_name=dto.display_name,
            role=dto.role,
            user_id=strawberry.ID(dto.user_id) if dto.user_id else None,
        )


@strawberry.type
class GroupMomentBalance:
    member_id: strawberry.ID
    net_amount: int
    currency_code: str
    display_name: str

    @classmethod
    def from_dto(cls, dto: GroupMomentBalanceDTO) -> GroupMomentBalance:
        return cls(
            member_id=strawberry.ID(dto.member_id),
            net_amount=dto.net_amount,
            currency_code=dto.currency_code,
            display_name=dto.display_name,
        )


@strawberry.type
class GroupExpensePaidBy:
    id: strawberry.ID


@strawberry.type
class GroupExpense:
    id: strawberry.ID
    amount: int
    currency_code: str
    title: str | None
    _paid_by_id: strawberry.Private[str | None]

    @strawberry.field
    def paid_by(self) -> GroupExpensePaidBy | None:
        if not self._paid_by_id:
            return None
        return GroupExpensePaidBy(id=strawberry.ID(self._paid_by_id))

    @classmethod
    def from_dto(cls, dto: GroupMomentExpenseDTO) -> GroupExpense:
        return cls(
            id=strawberry.ID(dto.id),
            amount=dto.amount,
            currency_code=dto.currency_code,
            title=dto.title,
            _paid_by_id=dto.paid_by_id,
        )


@strawberry.type
class GroupActivity:
    id: strawberry.ID
    title: str
    occurred_at: str | None

    @classmethod
    def from_dto(cls, dto: GroupMomentActivityDTO) -> GroupActivity:
        return cls(
            id=strawberry.ID(dto.id),
            title=dto.title,
            occurred_at=dto.occurred_at,
        )


@strawberry.type
class GroupExpenseConnection:
    edges: list[Edge[GroupExpense]]
    nodes: list[GroupExpense]
    page_info: PageInfo


@strawberry.type
class GroupActivityConnection:
    edges: list[Edge[GroupActivity]]
    nodes: list[GroupActivity]
    page_info: PageInfo


@strawberry.type
class GroupMoment:
    id: strawberry.ID
    title: str | None
    status: str
    _detail: strawberry.Private[GroupMomentDetailDTO]

    @strawberry.field
    def members(self) -> list[GroupMomentMember]:
        return [GroupMomentMember.from_dto(m) for m in self._detail.members]

    @strawberry.field
    def balances(self) -> list[GroupMomentBalance]:
        return [GroupMomentBalance.from_dto(b) for b in self._detail.balances]

    @strawberry.field
    def expenses(
        self,
        first: int = 20,
        after: str | None = None,
    ) -> GroupExpenseConnection:
        nodes = [GroupExpense.from_dto(e) for e in self._detail.expenses]
        conn = paginate_list(nodes, first=first, after=after)
        return GroupExpenseConnection(
            edges=conn.edges,
            nodes=conn.nodes,
            page_info=conn.page_info,
        )

    @strawberry.field
    def recent_activity(
        self,
        first: int = 10,
        after: str | None = None,
    ) -> GroupActivityConnection:
        nodes = [GroupActivity.from_dto(a) for a in self._detail.recent_activity]
        conn = paginate_list(nodes, first=first, after=after)
        return GroupActivityConnection(
            edges=conn.edges,
            nodes=conn.nodes,
            page_info=conn.page_info,
        )

    @classmethod
    def from_dto(cls, dto: GroupMomentDetailDTO) -> GroupMoment:
        return cls(
            id=strawberry.ID(str(dto.id)),
            title=dto.title,
            status=dto.status,
            _detail=dto,
        )
