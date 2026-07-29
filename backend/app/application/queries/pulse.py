"""Composed Pulse landing reads for GraphQL — AuthN principal, reuse domain app services."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.principal import Principal


class PulseScope(str, Enum):
    PERSONAL = "PERSONAL"
    GROUP = "GROUP"
    BUSINESS = "BUSINESS"


@dataclass
class PulseTypeCardDTO:
    moment_type_id: str
    moment_type_code: str
    moment_type_name: str
    description: str | None = None
    create_tagline: str | None = None
    icon_name: str | None = None
    image_url: str | None = None
    accent_main: str | None = None
    accent_soft_tint: str | None = None
    display_order: int = 0
    linked_moment_id: str | None = None
    linked_moment_status: str | None = None
    action_label: str | None = None


@dataclass
class PulseEmptyItemDTO:
    item_code: str
    item_kind: str
    title: str
    description: str | None = None
    icon_name: str | None = None
    image_url: str | None = None
    display_order: int = 0


@dataclass
class PersonalPulseDTO:
    overall_rhythm_state: str
    active_moment_count: int
    is_empty: bool
    hero_image_url: str = ""
    hero_title: str | None = None
    hero_subtitle: str | None = None
    journey_title: str | None = None
    journey_subtitle: str | None = None
    cta_label: str | None = None
    life_operations: dict[str, Any] | None = None
    future_building: dict[str, Any] | None = None
    lifestyle: dict[str, Any] | None = None
    emotional_security: dict[str, Any] | None = None


@dataclass
class GroupPulseDTO:
    is_empty: bool
    active_moment_count: int
    hero_title: str
    hero_subtitle: str
    hero_image_url: str | None = None
    cta_label: str = "Start a group moment"
    type_section_title: str = "What will you build together?"
    type_section_subtitle: str = ""
    type_cards: list[PulseTypeCardDTO] = field(default_factory=list)
    why_groups: list[PulseEmptyItemDTO] = field(default_factory=list)
    magic_intro: str = ""
    magic_steps: list[PulseEmptyItemDTO] = field(default_factory=list)


@dataclass
class BusinessPulseDTO:
    is_empty: bool
    active_moment_count: int
    hero_badge: str = ""
    hero_title: str = ""
    hero_title_accent: str | None = None
    hero_subtitle: str = ""
    hero_illustration_url: str | None = None
    cta_label: str = ""
    trust_line: str | None = None
    secondary_cta_label: str | None = None
    dimensions_section_title: str = ""
    dimensions_section_subtitle: str | None = None
    explore_moments_label: str | None = None
    benefits_section_title: str = ""
    benefits: list[PulseEmptyItemDTO] = field(default_factory=list)
    dimension_cards: list[PulseTypeCardDTO] = field(default_factory=list)
    avatar_image_url: str | None = None


PulseLandingDTO = PersonalPulseDTO | GroupPulseDTO | BusinessPulseDTO


def _card_from_dict(raw: dict[str, Any]) -> PulseTypeCardDTO:
    return PulseTypeCardDTO(
        moment_type_id=str(raw.get("moment_type_id") or ""),
        moment_type_code=str(raw.get("moment_type_code") or ""),
        moment_type_name=str(raw.get("moment_type_name") or ""),
        description=raw.get("description"),
        create_tagline=raw.get("create_tagline"),
        icon_name=raw.get("icon_name"),
        image_url=raw.get("image_url") or raw.get("cover_image_url"),
        accent_main=raw.get("accent_main"),
        accent_soft_tint=raw.get("accent_soft_tint"),
        display_order=int(raw.get("display_order") or 0),
        linked_moment_id=raw.get("linked_moment_id"),
        linked_moment_status=raw.get("linked_moment_status"),
        action_label=raw.get("action_label") or raw.get("badge_label"),
    )


def _item_from_dict(raw: dict[str, Any]) -> PulseEmptyItemDTO:
    return PulseEmptyItemDTO(
        item_code=str(raw.get("item_code") or raw.get("benefit_code") or ""),
        item_kind=str(raw.get("item_kind") or "item"),
        title=str(raw.get("title") or ""),
        description=raw.get("description"),
        icon_name=raw.get("icon_name"),
        image_url=raw.get("image_url"),
        display_order=int(raw.get("display_order") or 0),
    )


def _personal_from_model(payload: Any) -> PersonalPulseDTO:
    if hasattr(payload, "model_dump"):
        data = payload.model_dump(mode="json")
    elif isinstance(payload, dict):
        data = payload
    else:
        data = dict(payload)
    return PersonalPulseDTO(
        overall_rhythm_state=str(data.get("overall_rhythm_state") or "EMPTY"),
        active_moment_count=int(data.get("active_moment_count") or 0),
        is_empty=bool(data.get("is_empty", True)),
        hero_image_url=str(data.get("hero_image_url") or ""),
        hero_title=data.get("hero_title"),
        hero_subtitle=data.get("hero_subtitle"),
        journey_title=data.get("journey_title"),
        journey_subtitle=data.get("journey_subtitle"),
        cta_label=data.get("cta_label"),
        life_operations=data.get("life_operations"),
        future_building=data.get("future_building"),
        lifestyle=data.get("lifestyle"),
        emotional_security=data.get("emotional_security"),
    )


def _group_from_dict(data: dict[str, Any]) -> GroupPulseDTO:
    return GroupPulseDTO(
        is_empty=bool(data.get("is_empty", True)),
        active_moment_count=int(data.get("active_moment_count") or 0),
        hero_title=str(data.get("hero_title") or ""),
        hero_subtitle=str(data.get("hero_subtitle") or ""),
        hero_image_url=data.get("hero_image_url"),
        cta_label=str(data.get("cta_label") or "Start a group moment"),
        type_section_title=str(data.get("type_section_title") or ""),
        type_section_subtitle=str(data.get("type_section_subtitle") or ""),
        type_cards=[_card_from_dict(c) for c in (data.get("type_cards") or []) if isinstance(c, dict)],
        why_groups=[_item_from_dict(i) for i in (data.get("why_groups") or []) if isinstance(i, dict)],
        magic_intro=str(data.get("magic_intro") or ""),
        magic_steps=[_item_from_dict(i) for i in (data.get("magic_steps") or []) if isinstance(i, dict)],
    )


def _business_from_dict(data: dict[str, Any]) -> BusinessPulseDTO:
    benefits_raw = data.get("benefits") or []
    benefits: list[PulseEmptyItemDTO] = []
    for b in benefits_raw:
        if not isinstance(b, dict):
            continue
        benefits.append(
            PulseEmptyItemDTO(
                item_code=str(b.get("benefit_code") or b.get("item_code") or ""),
                item_kind="benefit",
                title=str(b.get("title") or ""),
                description=b.get("description"),
                icon_name=b.get("icon_name"),
                image_url=b.get("image_url"),
                display_order=int(b.get("display_order") or 0),
            )
        )
    return BusinessPulseDTO(
        is_empty=bool(data.get("is_empty", True)),
        active_moment_count=int(data.get("active_moment_count") or 0),
        hero_badge=str(data.get("hero_badge") or ""),
        hero_title=str(data.get("hero_title") or ""),
        hero_title_accent=data.get("hero_title_accent"),
        hero_subtitle=str(data.get("hero_subtitle") or ""),
        hero_illustration_url=data.get("hero_illustration_url"),
        cta_label=str(data.get("cta_label") or ""),
        trust_line=data.get("trust_line"),
        secondary_cta_label=data.get("secondary_cta_label"),
        dimensions_section_title=str(data.get("dimensions_section_title") or ""),
        dimensions_section_subtitle=data.get("dimensions_section_subtitle"),
        explore_moments_label=data.get("explore_moments_label"),
        benefits_section_title=str(data.get("benefits_section_title") or ""),
        benefits=benefits,
        dimension_cards=[
            _card_from_dict(c)
            for c in (data.get("dimension_cards") or [])
            if isinstance(c, dict)
        ],
        avatar_image_url=data.get("avatar_image_url"),
    )


async def get_pulse_landing(
    session: AsyncSession,
    principal: Principal,
    scope: PulseScope | str,
    *,
    force_refresh: bool = False,
    moment_type_code: str | None = None,
    workspace_id: UUID | None = None,
) -> PulseLandingDTO:
    """Return the Pulse tab landing for PERSONAL / GROUP / BUSINESS.

    Matches REST inventory Pulse endpoints. Authenticated principal only —
    no moment-scoped AuthZ (that belongs to active pulse in a later vertical).
    """
    scope_val = PulseScope(scope) if not isinstance(scope, PulseScope) else scope
    user_id = principal.user_id

    if scope_val is PulseScope.PERSONAL:
        from app.domains.personal.app_service import PersonalAppService

        payload = await PersonalAppService(session).pulse(
            user_id,
            force_refresh=force_refresh,
            moment_type_code=moment_type_code,
        )
        return _personal_from_model(payload)

    if scope_val is PulseScope.GROUP:
        from app.domains.group.app_service import GroupAppService

        payload = await GroupAppService(session).pulse(user_id)
        return _group_from_dict(payload)

    if scope_val is PulseScope.BUSINESS:
        from app.domains.business.app_service import BusinessAppService

        payload = await BusinessAppService(session).pulse(
            user_id, workspace_id=workspace_id
        )
        return _business_from_dict(payload)

    raise ValueError(f"Unsupported pulse scope: {scope_val}")
