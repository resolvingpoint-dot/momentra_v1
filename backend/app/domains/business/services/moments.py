"""Business Moments module: moment listing / retrieval / creation.

A created moment auto-enrolls the caller as an active owner member so that
membership-scoped features work immediately.
"""
from __future__ import annotations

from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.service import Page
from app.domains.business import schemas as bs
from app.domains.business.services.base import BusinessModuleService

_DEFAULT_OWNER_ROLE = "Operations Owner"


class BusinessMomentsModule(BusinessModuleService):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def _accessible_moment_ids(self, user_id: UUID) -> list[UUID]:
        members = await self.members_repo.list(filters={"user_id": user_id}, limit=None)
        created = await self.moments_repo.list(filters={"created_by": user_id}, limit=None)
        ids = {m.moment_id for m in members} | {m.moment_id for m in created}
        return sorted(ids)

    async def list_moments(
        self,
        user_id: UUID,
        *,
        status: str | None = None,
        moment_type: str | None = None,
        workspace_id: UUID | None = None,
        page: int = 1,
        per_page: int = 20,
    ) -> Page:
        ids = await self._accessible_moment_ids(user_id)
        if not ids:
            return Page[bs.BusinessMomentsSchema](items=[], total=0, limit=per_page, offset=(page - 1) * per_page)
        filters: dict = {"moment_id__in": ids}
        if status:
            filters["status"] = status
        if moment_type:
            filters["moment_type"] = moment_type
        if workspace_id:
            filters["workspace_id"] = workspace_id
        return await self._page(
            self.moments_repo, bs.BusinessMomentsSchema,
            filters=filters, order_by="-created_at", page=page, per_page=per_page,
        )

    async def get_moment(self, user_id: UUID, moment_id: UUID) -> bs.BusinessMomentsSchema:
        moment, _member = await self._access(user_id, moment_id)
        return bs.BusinessMomentsSchema.model_validate(moment)

    async def create_moment(
        self,
        user_id: UUID,
        *,
        moment_type: str,
        moment_name: str,
        workspace_id: UUID | None = None,
        owner_name: str = "Owner",
        owner_role: str = _DEFAULT_OWNER_ROLE,
    ) -> bs.BusinessMomentsSchema:
        moment = await self.moments_repo.create(
            {
                "workspace_id": workspace_id or uuid4(),
                "moment_type": moment_type,
                "moment_name": moment_name,
                "status": "draft",
                "created_by": user_id,
            }
        )
        await self.session.refresh(moment)
        await self.members_repo.create(
            {
                "moment_id": moment.moment_id,
                "name": owner_name,
                "role": owner_role,
                "member_status": "active",
                "is_team_lead": True,
                "added_by": user_id,
                "user_id": user_id,
            }
        )
        schema = bs.BusinessMomentsSchema.model_validate(moment)
        await self.session.commit()
        return schema
