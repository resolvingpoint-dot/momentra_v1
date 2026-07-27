"""Thin facade over BusinessActivityEngine."""
from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.business.activity.engine import BusinessActivityEngine


class BusinessActivityService:
    def __init__(self, session: AsyncSession) -> None:
        self.engine = BusinessActivityEngine(session)

    async def create(
        self,
        user_id: UUID,
        moment_id: UUID,
        action_type: str,
        title: str,
        *,
        subtitle: str | None = None,
        payload: dict[str, Any] | None = None,
        client_request_id: str | None = None,
        source: str = "quick_add",
        actor_name: str = "You",
    ) -> dict:
        return await self.engine.create(
            user_id,
            moment_id,
            action_type,
            title,
            subtitle=subtitle,
            payload=payload,
            client_request_id=client_request_id,
            source=source,
            actor_name=actor_name,
        )

    async def get(self, user_id: UUID, moment_id: UUID, event_id: UUID) -> dict:
        return await self.engine.get(user_id, moment_id, event_id)

    async def list(
        self,
        user_id: UUID,
        moment_id: UUID,
        *,
        action: str | None = None,
        member_id: UUID | None = None,
        status_filter: str = "active",
        date_from: Any | None = None,
        date_to: Any | None = None,
        search: str | None = None,
        sort: str = "newest",
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        return await self.engine.list(
            user_id,
            moment_id,
            action=action,
            member_id=member_id,
            status_filter=status_filter,
            date_from=date_from,
            date_to=date_to,
            search=search,
            sort=sort,
            page=page,
            page_size=page_size,
        )

    async def patch(
        self,
        user_id: UUID,
        moment_id: UUID,
        event_id: UUID,
        patch_data: dict[str, Any],
        *,
        actor_name: str = "You",
    ) -> dict:
        return await self.engine.patch(
            user_id, moment_id, event_id, patch_data, actor_name=actor_name
        )

    async def delete_soft(
        self,
        user_id: UUID,
        moment_id: UUID,
        event_id: UUID,
        *,
        actor_name: str = "You",
    ) -> dict:
        return await self.engine.delete_soft(
            user_id, moment_id, event_id, actor_name=actor_name
        )
