"""Memory reads for GraphQL — PERSONAL / GROUP / BUSINESS."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.principal import Principal


class MemoryScope(str, Enum):
    PERSONAL = "PERSONAL"
    GROUP = "GROUP"
    BUSINESS = "BUSINESS"


@dataclass
class MemoryDTO:
    scope: MemoryScope
    is_empty: bool
    active_moment_count: int = 0
    pattern_insight_count: int = 0
    hero_title: str | None = None
    hero_subtitle: str | None = None
    hero_badge: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)


def _from_dict(scope: MemoryScope, data: dict[str, Any]) -> MemoryDTO:
    return MemoryDTO(
        scope=scope,
        is_empty=bool(data.get("is_empty", True)),
        active_moment_count=int(data.get("active_moment_count") or 0),
        pattern_insight_count=int(data.get("pattern_insight_count") or 0),
        hero_title=data.get("hero_title"),
        hero_subtitle=data.get("hero_subtitle"),
        hero_badge=data.get("hero_badge"),
        payload=data,
    )


async def get_memory(
    session: AsyncSession,
    principal: Principal,
    scope: MemoryScope | str,
    *,
    force_refresh: bool = False,
    moment_type_code: str | None = None,
) -> MemoryDTO:
    """Return Memory surface for PERSONAL / GROUP / BUSINESS (AuthN only)."""
    scope_val = MemoryScope(scope) if not isinstance(scope, MemoryScope) else scope
    user_id = principal.user_id

    if scope_val is MemoryScope.PERSONAL:
        from app.domains.personal.app_service import PersonalAppService

        data = await PersonalAppService(session).memory(
            user_id,
            force_refresh=force_refresh,
            moment_type_code=moment_type_code,
        )
        if hasattr(data, "model_dump"):
            data = data.model_dump(mode="json")
        return _from_dict(scope_val, data if isinstance(data, dict) else {})

    if scope_val is MemoryScope.GROUP:
        from app.domains.group.app_service import GroupAppService

        data = await GroupAppService(session).memory(user_id)
        return _from_dict(scope_val, data if isinstance(data, dict) else {})

    if scope_val is MemoryScope.BUSINESS:
        from app.domains.business.active_service import BusinessActiveService

        data = await BusinessActiveService(session).get_memory(
            user_id, force_refresh=force_refresh
        )
        return _from_dict(scope_val, data if isinstance(data, dict) else {})

    raise ValueError(f"Unsupported memory scope: {scope_val}")
