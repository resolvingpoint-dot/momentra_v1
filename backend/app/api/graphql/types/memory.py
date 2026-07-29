"""Memory GraphQL types."""
from __future__ import annotations

from typing import Annotated

import strawberry
from strawberry.scalars import JSON

from app.application.queries.memory import MemoryDTO, MemoryScope


@strawberry.type
class PersonalMemory:
    is_empty: bool
    pattern_insight_count: int
    hero_badge: str | None
    hero_title: str | None
    hero_subtitle: str | None
    payload: JSON

    @classmethod
    def from_dto(cls, dto: MemoryDTO) -> PersonalMemory:
        return cls(
            is_empty=dto.is_empty,
            pattern_insight_count=dto.pattern_insight_count,
            hero_badge=dto.hero_badge,
            hero_title=dto.hero_title,
            hero_subtitle=dto.hero_subtitle,
            payload=dto.payload,
        )


@strawberry.type
class GroupMemory:
    is_empty: bool
    active_moment_count: int
    hero_title: str | None
    hero_subtitle: str | None
    payload: JSON

    @classmethod
    def from_dto(cls, dto: MemoryDTO) -> GroupMemory:
        return cls(
            is_empty=dto.is_empty,
            active_moment_count=dto.active_moment_count,
            hero_title=dto.hero_title,
            hero_subtitle=dto.hero_subtitle,
            payload=dto.payload,
        )


@strawberry.type
class BusinessMemory:
    is_empty: bool
    active_moment_count: int
    hero_title: str | None
    hero_subtitle: str | None
    payload: JSON

    @classmethod
    def from_dto(cls, dto: MemoryDTO) -> BusinessMemory:
        return cls(
            is_empty=dto.is_empty,
            active_moment_count=dto.active_moment_count,
            hero_title=dto.hero_title,
            hero_subtitle=dto.hero_subtitle,
            payload=dto.payload,
        )


MemoryResult = Annotated[
    PersonalMemory | GroupMemory | BusinessMemory,
    strawberry.union("MemoryResult"),
]


def memory_from_dto(dto: MemoryDTO) -> PersonalMemory | GroupMemory | BusinessMemory:
    if dto.scope is MemoryScope.GROUP:
        return GroupMemory.from_dto(dto)
    if dto.scope is MemoryScope.BUSINESS:
        return BusinessMemory.from_dto(dto)
    return PersonalMemory.from_dto(dto)
