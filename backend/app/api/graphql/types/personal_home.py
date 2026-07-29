"""Personal Home GraphQL types."""
from __future__ import annotations

import strawberry
from strawberry.scalars import JSON

from app.application.queries.personal_home import PersonalHomeCardDTO, PersonalHomeDTO


@strawberry.type
class PersonalHomeCard:
    moment_type_id: strawberry.ID
    moment_type_code: str
    moment_type_name: str
    description: str | None = None
    card_category_label: str | None = None
    theme_color: str | None = None
    icon_name: str | None = None
    display_order: int = 0
    linked_moment_id: strawberry.ID | None = None
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

    @classmethod
    def from_dto(cls, dto: PersonalHomeCardDTO) -> PersonalHomeCard:
        return cls(
            moment_type_id=strawberry.ID(dto.moment_type_id),
            moment_type_code=dto.moment_type_code,
            moment_type_name=dto.moment_type_name,
            description=dto.description,
            card_category_label=dto.card_category_label,
            theme_color=dto.theme_color,
            icon_name=dto.icon_name,
            display_order=dto.display_order,
            linked_moment_id=(
                strawberry.ID(dto.linked_moment_id) if dto.linked_moment_id else None
            ),
            linked_moment_status=dto.linked_moment_status,
            moment_name=dto.moment_name,
            current_runtime_state=dto.current_runtime_state,
            is_active=dto.is_active,
            rhythm_state=dto.rhythm_state,
            state_chip_label=dto.state_chip_label,
            summary_text=dto.summary_text,
            cover_image_url=dto.cover_image_url,
            system_tag=dto.system_tag,
            action_label=dto.action_label,
        )


@strawberry.type
class PersonalHome:
    active_moment_count: int
    is_empty: bool
    subtitle: str
    cards: list[PersonalHomeCard]
    hero_title: str | None
    hero_subtitle: str | None
    build_space_title: str | None
    build_space_body: str | None
    life_operations_detail: JSON | None
    future_building_detail: JSON | None
    lifestyle_detail: JSON | None
    emotional_security_detail: JSON | None

    @classmethod
    def from_dto(cls, dto: PersonalHomeDTO) -> PersonalHome:
        return cls(
            active_moment_count=dto.active_moment_count,
            is_empty=dto.is_empty,
            subtitle=dto.subtitle,
            cards=[PersonalHomeCard.from_dto(c) for c in dto.cards],
            hero_title=dto.hero_title,
            hero_subtitle=dto.hero_subtitle,
            build_space_title=dto.build_space_title,
            build_space_body=dto.build_space_body,
            life_operations_detail=dto.life_operations_detail,
            future_building_detail=dto.future_building_detail,
            lifestyle_detail=dto.lifestyle_detail,
            emotional_security_detail=dto.emotional_security_detail,
        )
