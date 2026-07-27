"""Business Workspace module: the moment's setup / structure / governance config.

Each of these is 1:1 with a moment (unique ``moment_id``), so writes are
idempotent upserts.
"""
from __future__ import annotations

from typing import Any, Mapping
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.business import schemas as bs
from app.domains.business.api_schemas import BusinessWorkspaceResponse
from app.domains.business.repository import (
    BusinessMomentGovernanceRepository,
    BusinessMomentSetupRepository,
    BusinessMomentStructureRepository,
)
from app.domains.business.services.base import BusinessModuleService


class BusinessWorkspaceModule(BusinessModuleService):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self.setup_repo = BusinessMomentSetupRepository(session)
        self.structure_repo = BusinessMomentStructureRepository(session)
        self.governance_repo = BusinessMomentGovernanceRepository(session)

    async def _upsert(self, repo, schema_cls, moment_id: UUID, data: Mapping[str, Any]):
        existing = await repo.get_by(moment_id=moment_id)
        if existing is None:
            obj = await repo.create({**dict(data), "moment_id": moment_id})
        else:
            for key, value in data.items():
                setattr(existing, key, value)
            obj = existing
            await self.session.flush()
        await self.session.refresh(obj)
        schema = schema_cls.model_validate(obj)
        await self.session.commit()
        return schema

    async def get_workspace(self, user_id: UUID, moment_id: UUID) -> BusinessWorkspaceResponse:
        await self._access(user_id, moment_id)
        setup = await self.setup_repo.get_by(moment_id=moment_id)
        structure = await self.structure_repo.get_by(moment_id=moment_id)
        governance = await self.governance_repo.get_by(moment_id=moment_id)
        return BusinessWorkspaceResponse(
            setup=bs.BusinessMomentSetupSchema.model_validate(setup) if setup else None,
            structure=bs.BusinessMomentStructureSchema.model_validate(structure) if structure else None,
            governance=bs.BusinessMomentGovernanceSchema.model_validate(governance) if governance else None,
        )

    async def upsert_setup(self, user_id: UUID, moment_id: UUID, data: Mapping[str, Any]) -> bs.BusinessMomentSetupSchema:
        await self._require_member(user_id, moment_id)
        payload = dict(data)
        payload.setdefault("team_owner_user_id", user_id)
        return await self._upsert(self.setup_repo, bs.BusinessMomentSetupSchema, moment_id, payload)

    async def upsert_structure(self, user_id: UUID, moment_id: UUID, data: Mapping[str, Any]) -> bs.BusinessMomentStructureSchema:
        await self._require_member(user_id, moment_id)
        return await self._upsert(self.structure_repo, bs.BusinessMomentStructureSchema, moment_id, data)

    async def upsert_governance(self, user_id: UUID, moment_id: UUID, data: Mapping[str, Any]) -> bs.BusinessMomentGovernanceSchema:
        await self._require_member(user_id, moment_id)
        return await self._upsert(self.governance_repo, bs.BusinessMomentGovernanceSchema, moment_id, data)
