"""Personal Moments Home read for GraphQL."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.principal import Principal


@dataclass
class PersonalHomeCardDTO:
    moment_type_id: str
    moment_type_code: str
    moment_type_name: str
    description: str | None = None
    card_category_label: str | None = None
    theme_color: str | None = None
    icon_name: str | None = None
    display_order: int = 0
    linked_moment_id: str | None = None
    linked_moment_status: str | None = None
    moment_name: str | None = None
    current_runtime_state: str | None = None
    is_active: bool = False
    rhythm_state: str | None = None
    state_chip_label: str | None = None
    summary_text: str | None = None
    cover_image_url: str | None = None
    system_tag: str | None = None
    action_label: str | None = None


@dataclass
class PersonalHomeDTO:
    active_moment_count: int
    is_empty: bool
    subtitle: str
    cards: list[PersonalHomeCardDTO] = field(default_factory=list)
    hero_title: str | None = None
    hero_subtitle: str | None = None
    build_space_title: str | None = None
    build_space_body: str | None = None
    life_operations_detail: dict[str, Any] | None = None
    future_building_detail: dict[str, Any] | None = None
    lifestyle_detail: dict[str, Any] | None = None
    emotional_security_detail: dict[str, Any] | None = None


def _card_from_raw(raw: dict[str, Any]) -> PersonalHomeCardDTO:
    return PersonalHomeCardDTO(
        moment_type_id=str(raw.get("moment_type_id") or ""),
        moment_type_code=str(raw.get("moment_type_code") or ""),
        moment_type_name=str(raw.get("moment_type_name") or ""),
        description=raw.get("description"),
        card_category_label=raw.get("card_category_label"),
        theme_color=raw.get("theme_color"),
        icon_name=raw.get("icon_name"),
        display_order=int(raw.get("display_order") or 0),
        linked_moment_id=raw.get("linked_moment_id"),
        linked_moment_status=raw.get("linked_moment_status"),
        moment_name=raw.get("moment_name"),
        current_runtime_state=raw.get("current_runtime_state"),
        is_active=bool(raw.get("is_active")),
        rhythm_state=raw.get("rhythm_state"),
        state_chip_label=raw.get("state_chip_label"),
        summary_text=raw.get("summary_text"),
        cover_image_url=raw.get("cover_image_url"),
        system_tag=raw.get("system_tag"),
        action_label=raw.get("action_label"),
    )


def _from_model(payload: Any) -> PersonalHomeDTO:
    if hasattr(payload, "model_dump"):
        data = payload.model_dump(mode="json")
    elif isinstance(payload, dict):
        data = payload
    else:
        data = dict(payload)
    cards_raw = data.get("cards") or []
    return PersonalHomeDTO(
        active_moment_count=int(data.get("active_moment_count") or 0),
        is_empty=bool(data.get("is_empty", True)),
        subtitle=str(data.get("subtitle") or ""),
        cards=[_card_from_raw(c) for c in cards_raw if isinstance(c, dict)],
        hero_title=data.get("hero_title"),
        hero_subtitle=data.get("hero_subtitle"),
        build_space_title=data.get("build_space_title"),
        build_space_body=data.get("build_space_body"),
        life_operations_detail=data.get("life_operations_detail"),
        future_building_detail=data.get("future_building_detail"),
        lifestyle_detail=data.get("lifestyle_detail"),
        emotional_security_detail=data.get("emotional_security_detail"),
    )


async def get_personal_home(
    session: AsyncSession,
    principal: Principal,
    *,
    force_refresh: bool = False,
    moment_type_code: str | None = None,
) -> PersonalHomeDTO:
    """Personal Moments Home — AuthN principal only (same as REST /personal/moments/home)."""
    from app.domains.personal.app_service import PersonalAppService

    payload = await PersonalAppService(session).moments_home(
        principal.user_id,
        force_refresh=force_refresh,
        moment_type_code=moment_type_code,
    )
    return _from_model(payload)
