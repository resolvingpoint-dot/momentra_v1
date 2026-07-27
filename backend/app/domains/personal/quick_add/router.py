"""Dispatch personal quick-add by moment template."""
from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError, ValidationError
from app.domains.moments.models import MomentModel
from app.domains.moments.repository import MomentRepository
from app.domains.personal.catalog import normalize_moment_type_code
from app.domains.personal.future_building.quick_add.service import (
    FutureBuildingQuickAddService,
)
from app.domains.personal.life_operations.quick_add.service import LifeOpsQuickAddService
from app.domains.personal.lifestyle.quick_add.service import LifestyleQuickAddService
from app.domains.personal.quick_add.edit_service import PersonalQuickAddEditService
from app.domains.personal.relationships.quick_add.service import (
    RelationshipsQuickAddService,
)

_SUPPORTED = {
    "LIFE_OPERATIONS",
    "FUTURE_BUILDING",
    "LIFESTYLE",
    "RELATIONSHIPS",
}


class PersonalQuickAddRouter:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self._moments = MomentRepository(session)
        self._services = {
            "LIFE_OPERATIONS": LifeOpsQuickAddService(session),
            "FUTURE_BUILDING": FutureBuildingQuickAddService(session),
            "LIFESTYLE": LifestyleQuickAddService(session),
            "RELATIONSHIPS": RelationshipsQuickAddService(session),
        }

    def _service_for_code(self, code: str):
        service = self._services.get(code)
        if service is None:
            raise ValidationError(f"Unsupported moment type for quick-add: {code}")
        return service

    async def _resolve_moment(
        self, user_id: UUID, moments: list[MomentModel], moment_id: UUID
    ) -> MomentModel:
        for moment in moments:
            if moment.id == moment_id:
                return moment
        moment = await self._moments.get_by_user_and_id(user_id, moment_id)
        if moment is None:
            raise NotFoundError("Moment not found")
        return moment

    async def options(
        self,
        user_id: UUID,
        moments: list[MomentModel],
        *,
        moment_id: UUID | None = None,
    ) -> dict[str, Any]:
        if moment_id is not None:
            moment = await self._resolve_moment(user_id, moments, moment_id)
            code = normalize_moment_type_code(moment.moment_type or "")
            if code not in _SUPPORTED:
                raise ValidationError(
                    f"Quick-add options are not available for {code or 'unknown'}"
                )
            return await self._service_for_code(code).options(user_id, moments)

        return await self._services["LIFE_OPERATIONS"].options(user_id, moments)

    async def submit(
        self,
        user_id: UUID,
        moment: MomentModel,
        body: dict[str, Any],
    ) -> dict[str, Any]:
        code = normalize_moment_type_code(moment.moment_type or "")
        if code not in _SUPPORTED:
            raise ValidationError(
                f"Quick add is not supported for {code or 'unknown'} moments"
            )
        return await self._service_for_code(code).submit(user_id, moment, body)

    async def detail(self, user_id: UUID, event_id: str) -> dict[str, Any]:
        return await PersonalQuickAddEditService(self.session).detail(
            user_id, event_id
        )

    async def patch(
        self, user_id: UUID, event_id: str, body: dict[str, Any]
    ) -> dict[str, Any]:
        return await PersonalQuickAddEditService(self.session).patch(
            user_id, event_id, body
        )
