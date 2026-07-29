"""Group Moments Home read for GraphQL."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.principal import Principal
from app.application.queries.pulse import (
    PulseEmptyItemDTO,
    PulseTypeCardDTO,
    _card_from_dict,
    _item_from_dict,
)


@dataclass
class GroupHomeDTO:
    is_empty: bool
    active_moment_count: int
    hero_title: str
    hero_subtitle: str
    cta_label: str
    cta_subtitle: str
    type_cards: list[PulseTypeCardDTO] = field(default_factory=list)
    how_it_works: list[PulseEmptyItemDTO] = field(default_factory=list)


def _from_dict(data: dict[str, Any]) -> GroupHomeDTO:
    return GroupHomeDTO(
        is_empty=bool(data.get("is_empty", True)),
        active_moment_count=int(data.get("active_moment_count") or 0),
        hero_title=str(data.get("hero_title") or ""),
        hero_subtitle=str(data.get("hero_subtitle") or ""),
        cta_label=str(data.get("cta_label") or ""),
        cta_subtitle=str(data.get("cta_subtitle") or ""),
        type_cards=[
            _card_from_dict(c) for c in (data.get("type_cards") or []) if isinstance(c, dict)
        ],
        how_it_works=[
            _item_from_dict(i) for i in (data.get("how_it_works") or []) if isinstance(i, dict)
        ],
    )


async def get_group_home(
    session: AsyncSession,
    principal: Principal,
) -> GroupHomeDTO:
    """Group Moments Home — AuthN only (same as REST GET /group/moments/home)."""
    from app.domains.group.app_service import GroupAppService

    payload = await GroupAppService(session).moments_home(principal.user_id)
    return _from_dict(payload if isinstance(payload, dict) else {})
