from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.module_states.models import ModuleStateModel
from app.domains.module_states.repository import ModuleStateRepository

DEFAULT_MODULES = [
    "MY_MONEY",
    "GROUP",
    "BUSINESS",
    "CIRCLE",
    "LIFE360",
    "MEMORY",
    "PULSE",
]


class ModuleStateService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = ModuleStateRepository(session)

    async def ensure_defaults(self, user_id) -> list[ModuleStateModel]:
        """Ensure default modules exist with one read + batched inserts."""
        existing = await self.repo.get_all_for_user(user_id)
        by_key = {row.module_key: row for row in existing}
        results: list[ModuleStateModel] = []
        created = False
        for key in DEFAULT_MODULES:
            row = by_key.get(key)
            if row is not None:
                results.append(row)
                continue
            results.append(await self.repo.create(user_id, key))
            created = True
        if created:
            await self.repo.session.flush()
        return results

    async def get_all_for_user(self, user_id) -> list[ModuleStateModel]:
        return await self.repo.get_all_for_user(user_id)

    async def get_state(self, user_id, module_key: str) -> ModuleStateModel | None:
        return await self.repo.get_by_user_and_module(user_id, module_key)

    async def set_state(self, user_id, module_key: str, state: str, reason: str | None = None) -> ModuleStateModel:
        return await self.repo.upsert_state(user_id, module_key, state, reason)
