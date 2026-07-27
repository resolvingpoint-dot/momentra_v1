"""Life Operations template activity handler."""
from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.personal.catalog import normalize_moment_type_code
from app.domains.personal.quick_add.edit_service import PersonalQuickAddEditService
from app.domains.personal.templates.activity.common import (
    build_activity_detail,
    load_activity_list,
    require_owned_moment,
)

_LO = "LIFE_OPERATIONS"


class LifeOperationsActivityHandler:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self._edit = PersonalQuickAddEditService(session)

    async def list_activity(
        self,
        user_id: UUID,
        moment_id: str,
        *,
        cursor: str | None = None,
        limit: int = 50,
    ) -> dict[str, Any]:
        moment = await require_owned_moment(self.session, user_id, moment_id)
        code = normalize_moment_type_code(moment.moment_type or "")
        items = await load_activity_list(
            self.session,
            user_id,
            moment.id,
            moment_type_code=code if code == _LO else _LO,
            limit=limit,
        )
        return {
            "moment_id": str(moment.id),
            "moment_type_code": _LO,
            "items": items,
            "next_cursor": None,
        }

    async def get_activity(self, user_id: UUID, event_id: str) -> dict[str, Any]:
        return await build_activity_detail(
            self.session, user_id, event_id, moment_type_code=_LO
        )

    async def patch_activity(
        self, user_id: UUID, event_id: str, body: dict[str, Any]
    ) -> dict[str, Any]:
        result = await self._edit.patch(user_id, event_id, body)
        detail = await build_activity_detail(
            self.session, user_id, event_id, moment_type_code=_LO
        )
        return {**detail, "patch_result": result}

    async def delete_activity(self, user_id: UUID, event_id: str) -> dict[str, Any]:
        return await self._edit.delete(user_id, event_id)
