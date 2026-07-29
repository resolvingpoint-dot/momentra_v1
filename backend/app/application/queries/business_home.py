"""Business Moments Home read for GraphQL."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.principal import Principal
from app.application.queries.pulse import PulseTypeCardDTO, _card_from_dict


@dataclass
class BusinessHomeDTO:
    is_empty: bool
    active_moment_count: int
    hero_title: str
    hero_subtitle: str
    cta_label: str
    avatar_image_url: str | None = None
    avatar_editable: bool = True
    info_card_title: str | None = None
    info_card_footnote: str | None = None
    cards: list[PulseTypeCardDTO] = field(default_factory=list)
    info_card_items: list[dict[str, Any]] = field(default_factory=list)
    avatar_requirements: dict[str, Any] | None = None
    cover_requirements: dict[str, Any] | None = None
    footer_band: dict[str, Any] | None = None


def _from_dict(data: dict[str, Any]) -> BusinessHomeDTO:
    cards_key = data.get("cards") or data.get("dimension_cards") or []
    return BusinessHomeDTO(
        is_empty=bool(data.get("is_empty", True)),
        active_moment_count=int(data.get("active_moment_count") or 0),
        hero_title=str(data.get("hero_title") or ""),
        hero_subtitle=str(data.get("hero_subtitle") or ""),
        cta_label=str(data.get("cta_label") or ""),
        avatar_image_url=data.get("avatar_image_url"),
        avatar_editable=bool(data.get("avatar_editable", True)),
        info_card_title=data.get("info_card_title"),
        info_card_footnote=data.get("info_card_footnote"),
        cards=[_card_from_dict(c) for c in cards_key if isinstance(c, dict)],
        info_card_items=[
            i for i in (data.get("info_card_items") or []) if isinstance(i, dict)
        ],
        avatar_requirements=(
            data.get("avatar_requirements")
            if isinstance(data.get("avatar_requirements"), dict)
            else None
        ),
        cover_requirements=(
            data.get("cover_requirements")
            if isinstance(data.get("cover_requirements"), dict)
            else None
        ),
        footer_band=(
            data.get("footer_band") if isinstance(data.get("footer_band"), dict) else None
        ),
    )


async def get_business_home(
    session: AsyncSession,
    principal: Principal,
    *,
    workspace_id: UUID | None = None,
) -> BusinessHomeDTO:
    """Business Moments Home — AuthN only (REST GET /business/moments/home)."""
    from app.domains.business.app_service import BusinessAppService

    payload = await BusinessAppService(session).moments_home(
        principal.user_id, workspace_id=workspace_id
    )
    return _from_dict(payload if isinstance(payload, dict) else {})
