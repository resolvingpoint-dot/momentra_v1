"""Business Home GraphQL types."""
from __future__ import annotations

import strawberry
from strawberry.scalars import JSON

from app.api.graphql.types.pulse import PulseTypeCard
from app.application.queries.business_home import BusinessHomeDTO


@strawberry.type
class BusinessHome:
    is_empty: bool
    active_moment_count: int
    hero_title: str
    hero_subtitle: str
    cta_label: str
    avatar_image_url: str | None
    avatar_editable: bool
    info_card_title: str | None
    info_card_footnote: str | None
    cards: list[PulseTypeCard]
    info_card_items: JSON
    avatar_requirements: JSON | None
    cover_requirements: JSON | None
    footer_band: JSON | None

    @classmethod
    def from_dto(cls, dto: BusinessHomeDTO) -> BusinessHome:
        return cls(
            is_empty=dto.is_empty,
            active_moment_count=dto.active_moment_count,
            hero_title=dto.hero_title,
            hero_subtitle=dto.hero_subtitle,
            cta_label=dto.cta_label,
            avatar_image_url=dto.avatar_image_url,
            avatar_editable=dto.avatar_editable,
            info_card_title=dto.info_card_title,
            info_card_footnote=dto.info_card_footnote,
            cards=[PulseTypeCard.from_dto(c) for c in dto.cards],
            info_card_items=dto.info_card_items,
            avatar_requirements=dto.avatar_requirements,
            cover_requirements=dto.cover_requirements,
            footer_band=dto.footer_band,
        )
