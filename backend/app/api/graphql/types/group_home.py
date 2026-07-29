"""Group Home GraphQL types."""
from __future__ import annotations

import strawberry

from app.api.graphql.types.pulse import PulseEmptyItem, PulseTypeCard
from app.application.queries.group_home import GroupHomeDTO


@strawberry.type
class GroupHome:
    is_empty: bool
    active_moment_count: int
    hero_title: str
    hero_subtitle: str
    cta_label: str
    cta_subtitle: str
    type_cards: list[PulseTypeCard]
    how_it_works: list[PulseEmptyItem]

    @classmethod
    def from_dto(cls, dto: GroupHomeDTO) -> GroupHome:
        return cls(
            is_empty=dto.is_empty,
            active_moment_count=dto.active_moment_count,
            hero_title=dto.hero_title,
            hero_subtitle=dto.hero_subtitle,
            cta_label=dto.cta_label,
            cta_subtitle=dto.cta_subtitle,
            type_cards=[PulseTypeCard.from_dto(c) for c in dto.type_cards],
            how_it_works=[PulseEmptyItem.from_dto(i) for i in dto.how_it_works],
        )
