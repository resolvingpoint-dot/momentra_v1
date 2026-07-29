from __future__ import annotations

from typing import Generic, TypeVar

from fastapi import Query
from pydantic import BaseModel

T = TypeVar("T")


class PageParams(BaseModel):
    page: int = Query(1, ge=1, description="Page number (1-based)")
    per_page: int = Query(20, ge=1, le=100, description="Items per page")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.per_page

    @property
    def limit(self) -> int:
        return self.per_page


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    per_page: int
    total_pages: int

    @classmethod
    def create(cls, items: list[T], total: int, params: PageParams) -> PaginatedResponse[T]:
        return cls(
            items=items,
            total=total,
            page=params.page,
            per_page=params.per_page,
            total_pages=max(1, -(-total // params.per_page)),
        )


class CursorParams(BaseModel):
    """Cursor pagination params for new list endpoints (see BACKEND_API_STANDARDS)."""

    cursor: str | None = Query(None, description="Opaque cursor from a previous page")
    limit: int = Query(50, ge=1, le=100, description="Max items to return")


class CursorPage(BaseModel, Generic[T]):
    items: list[T]
    next_cursor: str | None = None
    has_more: bool = False

    @classmethod
    def create(
        cls,
        items: list[T],
        *,
        next_cursor: str | None = None,
        has_more: bool | None = None,
    ) -> CursorPage[T]:
        more = has_more if has_more is not None else next_cursor is not None
        return cls(items=items, next_cursor=next_cursor, has_more=more)
