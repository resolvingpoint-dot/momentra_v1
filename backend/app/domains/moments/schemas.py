from __future__ import annotations

from datetime import datetime
from typing import Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, field_validator

from app.core.pagination import PageParams

VALID_CONTEXTS = {"MY_MONEY", "GROUP", "BUSINESS"}
MomentT = TypeVar("MomentT")


class MomentCreateSchema(BaseModel):
    context_type: str
    moment_type: str | None = None
    title: str | None = None
    description: str | None = None

    @field_validator("context_type")
    @classmethod
    def validate_context(cls, v: str) -> str:
        if v not in VALID_CONTEXTS:
            raise ValueError(
                f"Invalid context_type: {v}. CIRCLE moments cannot be created directly."
            )
        return v


class MomentUpdateSchema(BaseModel):
    title: str | None = None
    description: str | None = None
    moment_type: str | None = None


class MomentSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    context_type: str
    moment_type: str | None = None
    title: str | None = None
    description: str | None = None
    status: str = "DRAFT"
    setup_state: str = "EMPTY"
    created_at: datetime
    updated_at: datetime


class MomentHomeSchema(BaseModel):
    state: str = "EMPTY"
    counts: dict[str, int]
    recent: list[MomentSchema] = []


class MomentsCountsSchema(BaseModel):
    total: int = 0
    my_money: int = 0
    group: int = 0
    business: int = 0


class PaginatedMomentsResponse(BaseModel, Generic[MomentT]):
    items: list[MomentSchema]
    total: int
    page: int
    per_page: int
    total_pages: int

    @classmethod
    def create(
        cls, items: list[MomentSchema], total: int, params: PageParams
    ) -> PaginatedMomentsResponse:
        return cls(
            items=items,
            total=total,
            page=params.page,
            per_page=params.per_page,
            total_pages=max(1, -(-total // params.per_page)),
        )
