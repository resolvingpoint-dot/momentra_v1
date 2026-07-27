"""Business State Engine module.

Owns the business moment lifecycle state machine
(``draft -> configured -> active -> completed -> archived``) and the
orchestration job queue that downstream refresh workers consume.
"""
from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ValidationError
from app.core.service import Page
from app.domains.business import schemas as bs
from app.domains.business.repository import BusinessOrchestrationJobsRepository
from app.domains.business.services.base import BusinessModuleService, now_utc

# Allowed source states for each lifecycle target.
_TRANSITIONS: dict[str, set[str]] = {
    "configured": {"draft"},
    "active": {"draft", "configured"},
    "completed": {"active"},
    "archived": {"draft", "configured", "active", "completed"},
}


class BusinessStateEngineModule(BusinessModuleService):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self.jobs_repo = BusinessOrchestrationJobsRepository(session)

    # --------------------------- lifecycle --------------------------- #
    async def transition_moment(self, user_id: UUID, moment_id: UUID, to_status: str) -> bs.BusinessMomentsSchema:
        moment, _member = await self._access(user_id, moment_id)
        allowed_from = _TRANSITIONS.get(to_status)
        if allowed_from is None:
            raise ValidationError(f"Unknown target status {to_status!r}")
        extra = {}
        if to_status == "active" and moment.activated_at is None:
            extra["activated_at"] = now_utc()
        await self._apply_transition(
            moment, "status", to_status, allowed_from, extra=extra, label="business moment"
        )
        schema = bs.BusinessMomentsSchema.model_validate(moment)
        await self.session.commit()
        return schema

    async def configure(self, user_id: UUID, moment_id: UUID) -> bs.BusinessMomentsSchema:
        return await self.transition_moment(user_id, moment_id, "configured")

    async def activate(self, user_id: UUID, moment_id: UUID) -> bs.BusinessMomentsSchema:
        return await self.transition_moment(user_id, moment_id, "active")

    async def complete(self, user_id: UUID, moment_id: UUID) -> bs.BusinessMomentsSchema:
        return await self.transition_moment(user_id, moment_id, "completed")

    async def archive(self, user_id: UUID, moment_id: UUID) -> bs.BusinessMomentsSchema:
        return await self.transition_moment(user_id, moment_id, "archived")

    # ----------------------- orchestration jobs ---------------------- #
    async def list_jobs(
        self, user_id: UUID, moment_id: UUID, *, status: str | None = None, page: int = 1, per_page: int = 20
    ) -> Page:
        await self._access(user_id, moment_id)
        filters: dict = {"moment_id": moment_id}
        if status:
            filters["job_status"] = status
        return await self._page(
            self.jobs_repo, bs.BusinessOrchestrationJobsSchema,
            filters=filters, order_by="-queued_at", page=page, per_page=per_page,
        )

    async def enqueue_job(
        self,
        user_id: UUID,
        moment_id: UUID,
        *,
        job_type: str,
        orchestration_scope: str | None = None,
        priority: str = "medium",
    ) -> bs.BusinessOrchestrationJobsSchema:
        await self._require_member(user_id, moment_id)
        schema = await self._created(
            self.jobs_repo, bs.BusinessOrchestrationJobsSchema,
            {
                "moment_id": moment_id,
                "job_type": job_type,
                "job_status": "queued",
                "orchestration_scope": orchestration_scope,
                "priority": priority,
            },
        )
        await self.session.commit()
        return schema
