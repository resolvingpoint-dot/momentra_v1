from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError, ValidationError
from app.core.pagination import PageParams
from app.domains.moment_engine.engine import MomentEngine
from app.domains.moment_engine.registry import get_domain_registry
from app.domains.moments.models import MomentModel
from app.domains.moments.repository import MomentRepository
from app.domains.moments.schemas import (
    MomentHomeSchema,
    MomentSchema,
    MomentsCountsSchema,
    PaginatedMomentsResponse,
)


class MomentService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = MomentRepository(session)
        self.engine = MomentEngine()
        self.domains = get_domain_registry()

    def _adapter_for_context(self, context_type: str):
        try:
            return self.domains.adapter(self.session, context_type)
        except KeyError as exc:
            raise ValidationError(f"Unsupported context_type: {context_type}") from exc

    async def _load_owned(self, user_id: UUID, moment_id: UUID) -> MomentModel:
        moment = await self.repo.get_by_user_and_id(user_id, moment_id)
        if moment is None:
            raise NotFoundError("Moment not found")
        return moment

    async def create_moment(
        self,
        user_id: UUID,
        context_type: str,
        moment_type: str | None = None,
        title: str | None = None,
        description: str | None = None,
    ) -> MomentModel:
        adapter = self._adapter_for_context(context_type)
        ref = await self.engine.create(
            adapter,
            user_id,
            moment_type=moment_type,
            title=title,
            description=description,
        )
        return await adapter.get_model(user_id, ref.moment_id)

    async def get_moment(self, user_id: UUID, moment_id: UUID) -> MomentModel | None:
        return await self.repo.get_by_user_and_id(user_id, moment_id)

    async def update_moment(
        self,
        user_id: UUID,
        moment_id: UUID,
        *,
        title: str | None = None,
        description: str | None = None,
        moment_type: str | None = None,
    ) -> MomentModel:
        moment = await self._load_owned(user_id, moment_id)
        adapter = self.domains.adapter(self.session, moment.context_type)
        fields = {
            key: value
            for key, value in {
                "title": title,
                "description": description,
                "moment_type": moment_type,
            }.items()
            if value is not None
        }
        if not fields:
            return moment
        ref = await self.engine.update(adapter, user_id, moment_id, **fields)
        return await adapter.get_model(user_id, ref.moment_id)

    async def delete_moment(self, user_id: UUID, moment_id: UUID) -> None:
        moment = await self._load_owned(user_id, moment_id)
        adapter = self.domains.adapter(self.session, moment.context_type)
        await self.engine.delete(adapter, user_id, moment_id)

    async def activate_moment(self, user_id: UUID, moment_id: UUID) -> MomentModel:
        moment = await self._load_owned(user_id, moment_id)
        adapter = self.domains.adapter(self.session, moment.context_type)
        ref = await self.engine.activate(adapter, user_id, moment_id)
        return await adapter.get_model(user_id, ref.moment_id)

    async def complete_moment(self, user_id: UUID, moment_id: UUID) -> MomentModel:
        moment = await self._load_owned(user_id, moment_id)
        adapter = self.domains.adapter(self.session, moment.context_type)
        ref = await self.engine.complete(adapter, user_id, moment_id)
        return await adapter.get_model(user_id, ref.moment_id)

    async def archive_moment(self, user_id: UUID, moment_id: UUID) -> MomentModel:
        moment = await self._load_owned(user_id, moment_id)
        adapter = self.domains.adapter(self.session, moment.context_type)
        ref = await self.engine.archive(adapter, user_id, moment_id)
        return await adapter.get_model(user_id, ref.moment_id)

    async def home(self, user_id: UUID) -> MomentHomeSchema:
        total = await self.repo.total_count(user_id)
        context_counts = await self.repo.count_by_context(user_id)
        recent = await self.repo.get_recent(user_id, 5)

        state = "ACTIVE" if total > 0 else "EMPTY"
        counts = MomentsCountsSchema(
            total=total,
            my_money=context_counts.get("my_money", 0),
            group=context_counts.get("group", 0),
            business=context_counts.get("business", 0),
        )

        return MomentHomeSchema(
            state=state, counts=counts.model_dump(), recent=recent
        )

    async def home_paginated(
        self, user_id: UUID, params: PageParams
    ) -> PaginatedMomentsResponse:
        total = await self.repo.total_count(user_id)
        items = await self.repo.get_by_user_id(
            user_id, offset=params.offset, limit=params.limit
        )
        schemas = [MomentSchema.model_validate(m) for m in items]
        return PaginatedMomentsResponse.create(schemas, total, params)

    async def count_by_context_type(self, user_id: UUID, context_type: str) -> int:
        return await self.repo.count_by_context_type(user_id, context_type)
