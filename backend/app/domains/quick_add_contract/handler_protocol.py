"""Handler lifecycle interface for Quick Add v1."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass
class HandlerResult:
    persisted_id: str | None = None
    response: dict[str, Any] = field(default_factory=dict)
    events: list[str] = field(default_factory=list)
    projections: list[str] = field(default_factory=list)
    idempotent_replay: bool = False
    handler_version: str = "v1"
    projection_version: str = "v1"
    contract_version: str = "v1"


class QuickAddHandlerLifecycle(Protocol):
    """Every handler: validate → normalize → persist → publish → invalidate → response."""

    handler_id: str
    handler_version: str

    def validate(self, payload: dict[str, Any]) -> None: ...

    def normalize(self, payload: dict[str, Any]) -> dict[str, Any]: ...

    async def persist(self, payload: dict[str, Any]) -> HandlerResult: ...

    async def publish(self, result: HandlerResult, payload: dict[str, Any]) -> None: ...

    async def invalidate(self, result: HandlerResult, payload: dict[str, Any]) -> None: ...

    def response(self, result: HandlerResult) -> dict[str, Any]: ...


async def run_handler_lifecycle(
    handler: QuickAddHandlerLifecycle,
    payload: dict[str, Any],
) -> dict[str, Any]:
    handler.validate(payload)
    normalized = handler.normalize(payload)
    result = await handler.persist(normalized)
    await handler.publish(result, normalized)
    await handler.invalidate(result, normalized)
    body = handler.response(result)
    body.setdefault("contract_version", "v1")
    body.setdefault("handler_version", getattr(handler, "handler_version", "v1"))
    body.setdefault("projection_version", result.projection_version)
    return body
