"""Dispatch template activity by moment type."""
from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError, ValidationError
from app.domains.personal.catalog import normalize_moment_type_code
from app.domains.personal.templates.activity.life_operations import (
    LifeOperationsActivityHandler,
)
from app.domains.personal.templates.activity.future_building import (
    FutureBuildingActivityHandler,
)
from app.domains.personal.templates.activity.lifestyle import (
    LifestyleActivityHandler,
)
from app.domains.personal.templates.activity.relationships import (
    RelationshipsActivityHandler,
)

_SUPPORTED = {
    "LIFE_OPERATIONS": LifeOperationsActivityHandler,
    "FUTURE_BUILDING": FutureBuildingActivityHandler,
    "LIFESTYLE": LifestyleActivityHandler,
    "RELATIONSHIPS": RelationshipsActivityHandler,
}


class TemplateActivityService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _handler(self, moment_type: str):
        code = normalize_moment_type_code(moment_type)
        cls = _SUPPORTED.get(code)
        if cls is None:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail=f"Activity is not implemented for {code or moment_type}",
            )
        return cls(self.session)

    async def list_activity(
        self,
        user_id: UUID,
        moment_type: str,
        *,
        moment_id: str | None = None,
        cursor: str | None = None,
        limit: int = 50,
    ) -> dict[str, Any]:
        if not moment_id:
            raise ValidationError("moment_id is required")
        return await self._handler(moment_type).list_activity(
            user_id, moment_id, cursor=cursor, limit=limit
        )

    async def get_activity(
        self, user_id: UUID, moment_type: str, event_id: str
    ) -> dict[str, Any]:
        return await self._handler(moment_type).get_activity(user_id, event_id)

    async def patch_activity(
        self,
        user_id: UUID,
        moment_type: str,
        event_id: str,
        body: dict[str, Any],
    ) -> dict[str, Any]:
        return await self._handler(moment_type).patch_activity(
            user_id, event_id, body
        )

    async def delete_activity(
        self, user_id: UUID, moment_type: str, event_id: str
    ) -> dict[str, Any]:
        try:
            return await self._handler(moment_type).delete_activity(
                user_id, event_id
            )
        except NotFoundError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Activity not found",
            ) from None
