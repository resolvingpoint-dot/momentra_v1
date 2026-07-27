from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.module_states.models import ModuleStateModel


class ModuleStateRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_user_and_module(
        self, user_id, module_key: str
    ) -> ModuleStateModel | None:
        stmt = select(ModuleStateModel).where(
            ModuleStateModel.user_id == user_id,
            ModuleStateModel.module_key == module_key,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_for_user(self, user_id) -> list[ModuleStateModel]:
        stmt = (
            select(ModuleStateModel)
            .where(ModuleStateModel.user_id == user_id)
            .order_by(ModuleStateModel.module_key)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(
        self, user_id, module_key: str, state: str = "EMPTY", reason: str | None = None
    ) -> ModuleStateModel:
        now = datetime.now(timezone.utc)
        ms = ModuleStateModel(
            id=uuid4(),
            user_id=user_id,
            module_key=module_key,
            state=state,
            reason=reason,
            created_at=now,
            updated_at=now,
        )
        self.session.add(ms)
        return ms

    async def upsert_state(
        self, user_id, module_key: str, state: str, reason: str | None = None
    ) -> ModuleStateModel:
        existing = await self.get_by_user_and_module(user_id, module_key)
        if existing:
            existing.state = state
            if reason:
                existing.reason = reason
            return existing
        return await self.create(user_id, module_key, state, reason)
