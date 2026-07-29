"""Shared ports (Protocols) for application use-cases."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Protocol
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.shared.events.base import DomainEvent


class Clock(Protocol):
    def now(self) -> datetime: ...


class SessionFactory(Protocol):
    def __call__(self) -> Any:
        """Return an async context manager yielding ``AsyncSession``."""
        ...


class IdempotencyPort(Protocol):
    async def get_cached_response(
        self, user_id: UUID, route: str, idempotency_key: str
    ) -> dict[str, Any] | None: ...

    async def put_response(
        self,
        user_id: UUID,
        route: str,
        idempotency_key: str,
        payload: dict[str, Any],
    ) -> None: ...


class EventPublisher(Protocol):
    async def publish(self, event: DomainEvent) -> None: ...


class UnitOfWork(Protocol):
    @property
    def session(self) -> AsyncSession: ...

    async def commit(self) -> None: ...

    async def rollback(self) -> None: ...
