"""Business Risks module: runway risks + team issue risks."""
from __future__ import annotations

from typing import Any, Mapping
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError
from app.core.service import Page
from app.domains.business import schemas as bs
from app.domains.business.repository import RunwayRisksRepository, TeamIssueRisksRepository
from app.domains.business.services.base import BusinessModuleService, now_utc


class BusinessRisksModule(BusinessModuleService):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self.runway_repo = RunwayRisksRepository(session)
        self.team_repo = TeamIssueRisksRepository(session)

    # -------------------------- runway risks ------------------------- #
    async def list_runway_risks(
        self, user_id: UUID, moment_id: UUID, *, status: str | None = None, page: int = 1, per_page: int = 20
    ) -> Page:
        await self._access(user_id, moment_id)
        filters: dict = {"moment_id": moment_id}
        if status:
            filters["risk_status"] = status
        return await self._page(
            self.runway_repo, bs.RunwayRisksSchema,
            filters=filters, order_by="-created_at", page=page, per_page=per_page,
        )

    async def create_runway_risk(self, user_id: UUID, moment_id: UUID, data: Mapping[str, Any]) -> bs.RunwayRisksSchema:
        await self._require_member(user_id, moment_id)
        schema = await self._created(
            self.runway_repo, bs.RunwayRisksSchema,
            {**dict(data), "moment_id": moment_id, "risk_status": "open", "created_by": user_id},
        )
        await self.session.commit()
        return schema

    async def resolve_runway_risk(self, user_id: UUID, moment_id: UUID, risk_id: UUID) -> bs.RunwayRisksSchema:
        await self._require_member(user_id, moment_id)
        risk = await self.runway_repo.get_by_id(risk_id)
        if risk is None or risk.moment_id != moment_id:
            raise NotFoundError("Runway risk not found in this moment")
        await self._apply_transition(
            risk, "risk_status", "resolved", {"open", "investigating"},
            extra={"resolved_at": now_utc()}, label="runway risk",
        )
        schema = bs.RunwayRisksSchema.model_validate(risk)
        await self.session.commit()
        return schema

    # ------------------------ team issue risks ----------------------- #
    async def list_team_issues(
        self, user_id: UUID, moment_id: UUID, *, status: str | None = None, page: int = 1, per_page: int = 20
    ) -> Page:
        await self._access(user_id, moment_id)
        filters: dict = {"moment_id": moment_id}
        if status:
            filters["resolution_status"] = status
        return await self._page(
            self.team_repo, bs.TeamIssueRisksSchema,
            filters=filters, order_by="-created_at", page=page, per_page=per_page,
        )

    async def create_team_issue(self, user_id: UUID, moment_id: UUID, data: Mapping[str, Any]) -> bs.TeamIssueRisksSchema:
        await self._require_member(user_id, moment_id)
        schema = await self._created(
            self.team_repo, bs.TeamIssueRisksSchema,
            {**dict(data), "moment_id": moment_id, "resolution_status": "open", "created_by": user_id},
        )
        await self.session.commit()
        return schema

    async def resolve_team_issue(self, user_id: UUID, moment_id: UUID, issue_id: UUID) -> bs.TeamIssueRisksSchema:
        await self._require_member(user_id, moment_id)
        issue = await self.team_repo.get_by_id(issue_id)
        if issue is None or issue.moment_id != moment_id:
            raise NotFoundError("Team issue not found in this moment")
        await self._apply_transition(
            issue, "resolution_status", "resolved", {"open", "investigating"},
            extra={"resolved_at": now_utc()}, label="team issue",
        )
        schema = bs.TeamIssueRisksSchema.model_validate(issue)
        await self.session.commit()
        return schema
