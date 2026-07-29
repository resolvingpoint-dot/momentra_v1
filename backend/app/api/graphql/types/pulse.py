"""Pulse landing GraphQL types (PERSONAL / GROUP / BUSINESS)."""
from __future__ import annotations

from typing import Annotated, Any

import strawberry
from strawberry.scalars import JSON

from app.application.queries.pulse import (
    BusinessPulseDTO,
    GroupPulseDTO,
    PersonalPulseDTO,
    PulseEmptyItemDTO,
    PulseTypeCardDTO,
)


@strawberry.type
class PulseTypeCard:
    moment_type_id: strawberry.ID
    moment_type_code: str
    moment_type_name: str
    description: str | None = None
    create_tagline: str | None = None
    icon_name: str | None = None
    image_url: str | None = None
    accent_main: str | None = None
    accent_soft_tint: str | None = None
    display_order: int = 0
    linked_moment_id: strawberry.ID | None = None
    linked_moment_status: str | None = None
    action_label: str | None = None

    @classmethod
    def from_dto(cls, dto: PulseTypeCardDTO) -> PulseTypeCard:
        return cls(
            moment_type_id=strawberry.ID(dto.moment_type_id),
            moment_type_code=dto.moment_type_code,
            moment_type_name=dto.moment_type_name,
            description=dto.description,
            create_tagline=dto.create_tagline,
            icon_name=dto.icon_name,
            image_url=dto.image_url,
            accent_main=dto.accent_main,
            accent_soft_tint=dto.accent_soft_tint,
            display_order=dto.display_order,
            linked_moment_id=(
                strawberry.ID(dto.linked_moment_id) if dto.linked_moment_id else None
            ),
            linked_moment_status=dto.linked_moment_status,
            action_label=dto.action_label,
        )


@strawberry.type
class PulseEmptyItem:
    item_code: str
    item_kind: str
    title: str
    description: str | None = None
    icon_name: str | None = None
    image_url: str | None = None
    display_order: int = 0

    @classmethod
    def from_dto(cls, dto: PulseEmptyItemDTO) -> PulseEmptyItem:
        return cls(
            item_code=dto.item_code,
            item_kind=dto.item_kind,
            title=dto.title,
            description=dto.description,
            icon_name=dto.icon_name,
            image_url=dto.image_url,
            display_order=dto.display_order,
        )


@strawberry.type
class PersonalPulse:
    overall_rhythm_state: str
    active_moment_count: int
    is_empty: bool
    hero_image_url: str
    hero_title: str | None
    hero_subtitle: str | None
    journey_title: str | None
    journey_subtitle: str | None
    cta_label: str | None
    life_operations: JSON | None
    future_building: JSON | None
    lifestyle: JSON | None
    emotional_security: JSON | None

    @classmethod
    def from_dto(cls, dto: PersonalPulseDTO) -> PersonalPulse:
        return cls(
            overall_rhythm_state=dto.overall_rhythm_state,
            active_moment_count=dto.active_moment_count,
            is_empty=dto.is_empty,
            hero_image_url=dto.hero_image_url,
            hero_title=dto.hero_title,
            hero_subtitle=dto.hero_subtitle,
            journey_title=dto.journey_title,
            journey_subtitle=dto.journey_subtitle,
            cta_label=dto.cta_label,
            life_operations=dto.life_operations,
            future_building=dto.future_building,
            lifestyle=dto.lifestyle,
            emotional_security=dto.emotional_security,
        )


@strawberry.type
class GroupPulse:
    is_empty: bool
    active_moment_count: int
    hero_title: str
    hero_subtitle: str
    hero_image_url: str | None
    cta_label: str
    type_section_title: str
    type_section_subtitle: str
    type_cards: list[PulseTypeCard]
    why_groups: list[PulseEmptyItem]
    magic_intro: str
    magic_steps: list[PulseEmptyItem]

    @classmethod
    def from_dto(cls, dto: GroupPulseDTO) -> GroupPulse:
        return cls(
            is_empty=dto.is_empty,
            active_moment_count=dto.active_moment_count,
            hero_title=dto.hero_title,
            hero_subtitle=dto.hero_subtitle,
            hero_image_url=dto.hero_image_url,
            cta_label=dto.cta_label,
            type_section_title=dto.type_section_title,
            type_section_subtitle=dto.type_section_subtitle,
            type_cards=[PulseTypeCard.from_dto(c) for c in dto.type_cards],
            why_groups=[PulseEmptyItem.from_dto(i) for i in dto.why_groups],
            magic_intro=dto.magic_intro,
            magic_steps=[PulseEmptyItem.from_dto(i) for i in dto.magic_steps],
        )


@strawberry.type
class BusinessPulse:
    is_empty: bool
    active_moment_count: int
    hero_badge: str
    hero_title: str
    hero_title_accent: str | None
    hero_subtitle: str
    hero_illustration_url: str | None
    cta_label: str
    trust_line: str | None
    secondary_cta_label: str | None
    dimensions_section_title: str
    dimensions_section_subtitle: str | None
    explore_moments_label: str | None
    benefits_section_title: str
    benefits: list[PulseEmptyItem]
    dimension_cards: list[PulseTypeCard]
    avatar_image_url: str | None

    @classmethod
    def from_dto(cls, dto: BusinessPulseDTO) -> BusinessPulse:
        return cls(
            is_empty=dto.is_empty,
            active_moment_count=dto.active_moment_count,
            hero_badge=dto.hero_badge,
            hero_title=dto.hero_title,
            hero_title_accent=dto.hero_title_accent,
            hero_subtitle=dto.hero_subtitle,
            hero_illustration_url=dto.hero_illustration_url,
            cta_label=dto.cta_label,
            trust_line=dto.trust_line,
            secondary_cta_label=dto.secondary_cta_label,
            dimensions_section_title=dto.dimensions_section_title,
            dimensions_section_subtitle=dto.dimensions_section_subtitle,
            explore_moments_label=dto.explore_moments_label,
            benefits_section_title=dto.benefits_section_title,
            benefits=[PulseEmptyItem.from_dto(b) for b in dto.benefits],
            dimension_cards=[PulseTypeCard.from_dto(c) for c in dto.dimension_cards],
            avatar_image_url=dto.avatar_image_url,
        )


PulseResult = Annotated[
    PersonalPulse | GroupPulse | BusinessPulse,
    strawberry.union("PulseResult"),
]


def pulse_from_dto(dto: Any) -> PersonalPulse | GroupPulse | BusinessPulse:
    if isinstance(dto, PersonalPulseDTO):
        return PersonalPulse.from_dto(dto)
    if isinstance(dto, GroupPulseDTO):
        return GroupPulse.from_dto(dto)
    if isinstance(dto, BusinessPulseDTO):
        return BusinessPulse.from_dto(dto)
    raise TypeError(f"Unsupported pulse DTO: {type(dto)!r}")
