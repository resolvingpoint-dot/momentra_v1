from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from app.shared.events.base import DomainEvent


def moment_created(
    *,
    user_id: UUID,
    moment_id: UUID,
    context: str,
    moment_type: str | None = None,
    **payload: Any,
) -> DomainEvent:
    return DomainEvent(
        name="moment.created",
        user_id=user_id,
        moment_id=moment_id,
        context=context,
        moment_type=moment_type,
        payload=dict(payload),
    )


def moment_updated(
    *,
    user_id: UUID,
    moment_id: UUID,
    context: str,
    moment_type: str | None = None,
    **payload: Any,
) -> DomainEvent:
    return DomainEvent(
        name="moment.updated",
        user_id=user_id,
        moment_id=moment_id,
        context=context,
        moment_type=moment_type,
        payload=dict(payload),
    )


def moment_activated(
    *,
    user_id: UUID,
    moment_id: UUID,
    context: str,
    moment_type: str | None = None,
    activated_at: datetime | None = None,
    **payload: Any,
) -> DomainEvent:
    return DomainEvent(
        name="moment.activated",
        user_id=user_id,
        moment_id=moment_id,
        context=context,
        moment_type=moment_type,
        payload={"activated_at": (activated_at or datetime.now(timezone.utc)).isoformat(), **payload},
    )


def moment_paused(
    *,
    user_id: UUID,
    moment_id: UUID,
    context: str,
    moment_type: str | None = None,
    **payload: Any,
) -> DomainEvent:
    return DomainEvent(
        name="moment.paused",
        user_id=user_id,
        moment_id=moment_id,
        context=context,
        moment_type=moment_type,
        payload=dict(payload),
    )


def moment_completed(
    *,
    user_id: UUID,
    moment_id: UUID,
    context: str,
    moment_type: str | None = None,
    **payload: Any,
) -> DomainEvent:
    return DomainEvent(
        name="moment.completed",
        user_id=user_id,
        moment_id=moment_id,
        context=context,
        moment_type=moment_type,
        payload=dict(payload),
    )


def moment_archived(
    *,
    user_id: UUID,
    moment_id: UUID,
    context: str,
    moment_type: str | None = None,
    **payload: Any,
) -> DomainEvent:
    return DomainEvent(
        name="moment.archived",
        user_id=user_id,
        moment_id=moment_id,
        context=context,
        moment_type=moment_type,
        payload=dict(payload),
    )


def moment_deleted(
    *,
    user_id: UUID,
    moment_id: UUID,
    context: str,
    moment_type: str | None = None,
    **payload: Any,
) -> DomainEvent:
    return DomainEvent(
        name="moment.deleted",
        user_id=user_id,
        moment_id=moment_id,
        context=context,
        moment_type=moment_type,
        payload=dict(payload),
    )
