"""Life GraphQL types."""
from __future__ import annotations

from typing import Annotated

import strawberry
from strawberry.scalars import JSON

from app.application.queries.life import LifeDTO, LifeScope


@strawberry.type
class PersonalLife:
    is_empty: bool
    active_moment_count: int
    date_range_label: str | None
    metrics: JSON | None
    payload: JSON

    @classmethod
    def from_dto(cls, dto: LifeDTO) -> PersonalLife:
        return cls(
            is_empty=dto.is_empty,
            active_moment_count=dto.active_moment_count,
            date_range_label=dto.date_range_label,
            metrics=dto.metrics,
            payload=dto.payload,
        )


@strawberry.type
class GroupLife:
    is_empty: bool
    active_moment_count: int
    date_range_label: str | None
    metrics: JSON | None
    payload: JSON

    @classmethod
    def from_dto(cls, dto: LifeDTO) -> GroupLife:
        return cls(
            is_empty=dto.is_empty,
            active_moment_count=dto.active_moment_count,
            date_range_label=dto.date_range_label,
            metrics=dto.metrics,
            payload=dto.payload,
        )


@strawberry.type
class BusinessLife:
    is_empty: bool
    active_moment_count: int
    date_range_label: str | None
    metrics: JSON | None
    payload: JSON

    @classmethod
    def from_dto(cls, dto: LifeDTO) -> BusinessLife:
        return cls(
            is_empty=dto.is_empty,
            active_moment_count=dto.active_moment_count,
            date_range_label=dto.date_range_label,
            metrics=dto.metrics,
            payload=dto.payload,
        )


LifeResult = Annotated[
    PersonalLife | GroupLife | BusinessLife,
    strawberry.union("LifeResult"),
]


def life_from_dto(dto: LifeDTO) -> PersonalLife | GroupLife | BusinessLife:
    if dto.scope is LifeScope.GROUP:
        return GroupLife.from_dto(dto)
    if dto.scope is LifeScope.BUSINESS:
        return BusinessLife.from_dto(dto)
    return PersonalLife.from_dto(dto)
