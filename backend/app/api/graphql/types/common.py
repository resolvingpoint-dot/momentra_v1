"""Cursor connection helpers for GraphQL list fields."""
from __future__ import annotations

import base64
from typing import Generic, TypeVar

import strawberry

T = TypeVar("T")


def encode_cursor(index: int) -> str:
    return base64.urlsafe_b64encode(f"idx:{index}".encode()).decode().rstrip("=")


def decode_cursor(cursor: str | None) -> int:
    if not cursor:
        return -1
    try:
        pad = "=" * (-len(cursor) % 4)
        raw = base64.urlsafe_b64decode(cursor + pad).decode()
        if raw.startswith("idx:"):
            return int(raw.split(":", 1)[1])
    except Exception:
        return -1
    return -1


@strawberry.type
class PageInfo:
    has_next_page: bool
    end_cursor: str | None = None


@strawberry.type
class Connection(Generic[T]):
    edges: list["Edge[T]"]
    nodes: list[T]
    page_info: PageInfo


@strawberry.type
class Edge(Generic[T]):
    cursor: str
    node: T


def paginate_list(
    items: list[T],
    *,
    first: int = 20,
    after: str | None = None,
) -> Connection[T]:
    from app.core.config import settings

    ceiling = max(1, int(settings.graphql_max_page_size))
    first = max(1, min(int(first or 20), ceiling))
    start = decode_cursor(after) + 1
    if start < 0:
        start = 0
    window = items[start : start + first]
    edges = [
        Edge(cursor=encode_cursor(start + i), node=node)
        for i, node in enumerate(window)
    ]
    end_cursor = edges[-1].cursor if edges else None
    has_next = (start + first) < len(items)
    return Connection(
        edges=edges,
        nodes=window,
        page_info=PageInfo(has_next_page=has_next, end_cursor=end_cursor),
    )
