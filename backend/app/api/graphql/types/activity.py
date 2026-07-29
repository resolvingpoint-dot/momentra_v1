"""Activity GraphQL types — Unified personal + moment-scoped feeds."""
from __future__ import annotations

from typing import Annotated, Any

import strawberry
from strawberry.scalars import JSON

from app.application.queries.activity import (
    ActivityScope,
    MomentActivityDTO,
    PersonalActivityDTO,
)


@strawberry.type
class ActivityInsight:
    id: str
    kind: str
    title: str
    value: str | None = None

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> ActivityInsight:
        return cls(
            id=str(raw.get("id") or ""),
            kind=str(raw.get("kind") or ""),
            title=str(raw.get("title") or ""),
            value=str(raw["value"]) if raw.get("value") is not None else None,
        )


@strawberry.type
class PersonalActivitySnapshot:
    headline: str | None = None
    today_activity_count: int = 0
    today_amount_minor: int = 0
    today_mood_label: str | None = None
    today_domain_labels: list[str] | None = None
    raw: JSON | None = None

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> PersonalActivitySnapshot:
        labels = raw.get("today_domain_labels")
        return cls(
            headline=raw.get("headline"),
            today_activity_count=int(raw.get("today_activity_count") or 0),
            today_amount_minor=int(raw.get("today_amount_minor") or 0),
            today_mood_label=raw.get("today_mood_label"),
            today_domain_labels=[str(x) for x in labels] if isinstance(labels, list) else None,
            raw=raw,
        )


@strawberry.type
class PersonalActivityFeed:
    snapshot: PersonalActivitySnapshot
    insights: list[ActivityInsight]
    items: JSON
    next_cursor: str | None

    @classmethod
    def from_dto(cls, dto: PersonalActivityDTO) -> PersonalActivityFeed:
        return cls(
            snapshot=PersonalActivitySnapshot.from_dict(dto.snapshot),
            insights=[ActivityInsight.from_dict(i) for i in dto.insights],
            items=dto.items,
            next_cursor=dto.next_cursor,
        )


@strawberry.type
class GroupActivityFeed:
    moment_id: strawberry.ID
    total: int
    items: JSON
    summary: JSON | None
    payload: JSON

    @classmethod
    def from_dto(cls, dto: MomentActivityDTO) -> GroupActivityFeed:
        return cls(
            moment_id=strawberry.ID(str(dto.moment_id)),
            total=dto.total,
            items=dto.items,
            summary=dto.summary,
            payload=dto.payload,
        )


@strawberry.type
class BusinessActivityFeed:
    moment_id: strawberry.ID
    total: int
    page: int | None
    page_size: int | None
    items: JSON
    payload: JSON

    @classmethod
    def from_dto(cls, dto: MomentActivityDTO) -> BusinessActivityFeed:
        return cls(
            moment_id=strawberry.ID(str(dto.moment_id)),
            total=dto.total,
            page=dto.page,
            page_size=dto.page_size,
            items=dto.items,
            payload=dto.payload,
        )


ActivityResult = Annotated[
    PersonalActivityFeed | GroupActivityFeed | BusinessActivityFeed,
    strawberry.union("ActivityResult"),
]


def activity_from_dto(
    dto: Any,
) -> PersonalActivityFeed | GroupActivityFeed | BusinessActivityFeed:
    if isinstance(dto, PersonalActivityDTO):
        return PersonalActivityFeed.from_dto(dto)
    if isinstance(dto, MomentActivityDTO):
        if dto.scope is ActivityScope.BUSINESS:
            return BusinessActivityFeed.from_dto(dto)
        return GroupActivityFeed.from_dto(dto)
    raise TypeError(f"Unsupported activity DTO: {type(dto)!r}")
