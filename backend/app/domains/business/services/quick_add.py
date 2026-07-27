"""Business Quick Add module: per-user quick-add drafts."""
from __future__ import annotations

from typing import Any, Mapping
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError, StateTransitionError
from app.core.service import Page
from app.domains.business import schemas as bs
from app.domains.business.repository import BusinessQuickAddDraftsRepository
from app.domains.business.services.base import BusinessModuleService, now_utc


class BusinessQuickAddModule(BusinessModuleService):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self.drafts_repo = BusinessQuickAddDraftsRepository(session)

    async def list_drafts(self, user_id: UUID, moment_id: UUID, *, page: int = 1, per_page: int = 20) -> Page:
        await self._access(user_id, moment_id)
        return await self._page(
            self.drafts_repo, bs.BusinessQuickAddDraftsSchema,
            filters={"moment_id": moment_id, "user_id": user_id}, order_by="-updated_at", page=page, per_page=per_page,
        )

    async def create_draft(
        self, user_id: UUID, moment_id: UUID, *, tab_type: str, draft_payload: Mapping[str, Any]
    ) -> bs.BusinessQuickAddDraftsSchema:
        await self._require_member(user_id, moment_id)
        schema = await self._created(
            self.drafts_repo, bs.BusinessQuickAddDraftsSchema,
            {
                "moment_id": moment_id,
                "user_id": user_id,
                "tab_type": tab_type,
                "draft_payload": dict(draft_payload),
                "draft_status": "active",
            },
        )
        await self.session.commit()
        return schema

    async def _owned_draft(self, user_id: UUID, moment_id: UUID, draft_id: UUID):
        draft = await self.drafts_repo.get_by_id(draft_id)
        if draft is None or draft.moment_id != moment_id or draft.user_id != user_id:
            raise NotFoundError("Draft not found")
        return draft

    async def _set_draft_status(self, user_id, moment_id, draft_id, to_status) -> bs.BusinessQuickAddDraftsSchema:
        await self._access(user_id, moment_id)
        draft = await self._owned_draft(user_id, moment_id, draft_id)
        if draft.draft_status != "active":
            raise StateTransitionError("Only active drafts can be updated")
        draft.draft_status = to_status
        draft.updated_at = now_utc()
        await self.session.flush()
        schema = bs.BusinessQuickAddDraftsSchema.model_validate(draft)
        await self.session.commit()
        return schema

    async def submit_draft(self, user_id: UUID, moment_id: UUID, draft_id: UUID) -> bs.BusinessQuickAddDraftsSchema:
        return await self._set_draft_status(user_id, moment_id, draft_id, "submitted")

    async def discard_draft(self, user_id: UUID, moment_id: UUID, draft_id: UUID) -> bs.BusinessQuickAddDraftsSchema:
        return await self._set_draft_status(user_id, moment_id, draft_id, "discarded")
