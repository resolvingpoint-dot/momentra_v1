"""Business Approvals module: operations approval requests + team approval requests.

Operations approvals store the actor as ``user_id`` (requested_by/decided_by);
team approvals reference ``member_id`` (requested_by/approver_id), so the caller
is resolved to their member for team requests.
"""
from __future__ import annotations

from decimal import Decimal
from typing import Literal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError, PermissionDeniedError
from app.core.service import Page
from app.domains.business import schemas as bs
from app.domains.business.permissions import can_approve, get_active_member, is_privileged_member
from app.domains.business.repository import (
    OperationsApprovalRequestsRepository,
    TeamApprovalRequestsRepository,
)
from app.domains.business.services.base import BusinessModuleService, now_utc

Decision = Literal["approved", "rejected"]


class BusinessApprovalsModule(BusinessModuleService):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self.ops_repo = OperationsApprovalRequestsRepository(session)
        self.team_repo = TeamApprovalRequestsRepository(session)

    # --------------------------- operations -------------------------- #
    async def list_operations_approvals(
        self, user_id: UUID, moment_id: UUID, *, status: str | None = None, page: int = 1, per_page: int = 20
    ) -> Page:
        await self._access(user_id, moment_id)
        filters: dict = {"moment_id": moment_id}
        if status:
            filters["approval_status"] = status
        return await self._page(
            self.ops_repo, bs.OperationsApprovalRequestsSchema,
            filters=filters, order_by="-created_at", page=page, per_page=per_page,
        )

    async def create_operations_approval(
        self,
        user_id: UUID,
        moment_id: UUID,
        *,
        request_type: str,
        request_title: str,
        description: str,
        priority: str = "medium",
        amount: Decimal | None = None,
        currency: str | None = None,
        linked_spend_entry_id: UUID | None = None,
    ) -> bs.OperationsApprovalRequestsSchema:
        await self._require_member(user_id, moment_id)
        schema = await self._created(
            self.ops_repo, bs.OperationsApprovalRequestsSchema,
            {
                "moment_id": moment_id,
                "request_type": request_type,
                "request_title": request_title,
                "description": description,
                "priority": priority,
                "amount": amount,
                "currency": currency,
                "linked_spend_entry_id": linked_spend_entry_id,
                "approval_status": "pending",
                "requested_by": user_id,
            },
        )
        await self.session.commit()
        return schema

    async def decide_operations_approval(
        self, user_id: UUID, moment_id: UUID, approval_id: UUID, decision: Decision, note: str | None = None
    ) -> bs.OperationsApprovalRequestsSchema:
        await can_approve(self.session, moment_id, user_id)
        approval = await self.ops_repo.get_by_id(approval_id)
        if approval is None or approval.moment_id != moment_id:
            raise NotFoundError("Operations approval not found in this moment")
        await self._apply_transition(
            approval, "approval_status", decision, {"pending"},
            extra={"decided_by": user_id, "decided_at": now_utc(), "decision_note": note},
            label="operations approval",
        )
        schema = bs.OperationsApprovalRequestsSchema.model_validate(approval)
        await self.session.commit()
        return schema

    # ----------------------------- team ------------------------------ #
    async def list_team_approvals(
        self, user_id: UUID, moment_id: UUID, *, status: str | None = None, page: int = 1, per_page: int = 20
    ) -> Page:
        await self._access(user_id, moment_id)
        filters: dict = {"moment_id": moment_id}
        if status:
            filters["approval_status"] = status
        return await self._page(
            self.team_repo, bs.TeamApprovalRequestsSchema,
            filters=filters, order_by="-created_at", page=page, per_page=per_page,
        )

    async def create_team_approval(
        self,
        user_id: UUID,
        moment_id: UUID,
        *,
        request_title: str,
        amount: Decimal,
        approval_type: str,
        reason: str,
        approver_id: UUID,
        priority: str = "normal",
    ) -> bs.TeamApprovalRequestsSchema:
        requester_member_id = await self._resolve_member_id(user_id, moment_id)
        schema = await self._created(
            self.team_repo, bs.TeamApprovalRequestsSchema,
            {
                "moment_id": moment_id,
                "request_title": request_title,
                "amount": amount,
                "approval_type": approval_type,
                "reason": reason,
                "priority": priority,
                "requested_by": requester_member_id,
                "approver_id": approver_id,
                "approval_status": "pending",
            },
        )
        await self.session.commit()
        return schema

    async def decide_team_approval(
        self, user_id: UUID, moment_id: UUID, approval_id: UUID, decision: Decision, note: str | None = None
    ) -> bs.TeamApprovalRequestsSchema:
        await can_approve(self.session, moment_id, user_id)
        approval = await self.team_repo.get_by_id(approval_id)
        if approval is None or approval.moment_id != moment_id:
            raise NotFoundError("Team approval not found in this moment")
        actor = await get_active_member(self.session, moment_id, user_id)
        if (
            actor is not None
            and approval.approver_id is not None
            and actor.member_id != approval.approver_id
            and not is_privileged_member(actor)
        ):
            raise PermissionDeniedError("Only the designated approver can decide this request")
        await self._apply_transition(
            approval, "approval_status", decision, {"pending"},
            extra={"decided_by": user_id, "decided_at": now_utc(), "decision_note": note},
            label="team approval",
        )
        schema = bs.TeamApprovalRequestsSchema.model_validate(approval)
        await self.session.commit()
        return schema
