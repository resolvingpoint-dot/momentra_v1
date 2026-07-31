"""Domain events for platform opaque invites (never include raw codes)."""
from __future__ import annotations

from typing import Any
from uuid import UUID

from app.shared.events.base import USER_SCOPED_MOMENT_ID, DomainEvent


def company_invite_created(
    *,
    user_id: UUID,
    invite_id: UUID,
    workspace_id: UUID,
    **payload: Any,
) -> DomainEvent:
    return DomainEvent(
        name="company_invite.created",
        user_id=user_id,
        context="BUSINESS",
        moment_id=USER_SCOPED_MOMENT_ID,
        payload={"invite_id": str(invite_id), "workspace_id": str(workspace_id), **payload},
    )


def company_invite_accepted(
    *,
    user_id: UUID,
    invite_id: UUID,
    workspace_id: UUID,
    result: str,
    **payload: Any,
) -> DomainEvent:
    return DomainEvent(
        name="company_invite.accepted",
        user_id=user_id,
        context="BUSINESS",
        moment_id=USER_SCOPED_MOMENT_ID,
        payload={
            "invite_id": str(invite_id),
            "workspace_id": str(workspace_id),
            "result": result,
            **payload,
        },
    )


def company_invite_declined(
    *,
    user_id: UUID,
    invite_id: UUID,
    workspace_id: UUID | None = None,
    **payload: Any,
) -> DomainEvent:
    return DomainEvent(
        name="company_invite.declined",
        user_id=user_id,
        context="BUSINESS",
        moment_id=USER_SCOPED_MOMENT_ID,
        payload={
            "invite_id": str(invite_id),
            "workspace_id": str(workspace_id) if workspace_id else None,
            **payload,
        },
    )


def company_invite_revoked(
    *,
    user_id: UUID,
    invite_id: UUID,
    workspace_id: UUID | None = None,
    **payload: Any,
) -> DomainEvent:
    return DomainEvent(
        name="company_invite.revoked",
        user_id=user_id,
        context="BUSINESS",
        moment_id=USER_SCOPED_MOMENT_ID,
        payload={
            "invite_id": str(invite_id),
            "workspace_id": str(workspace_id) if workspace_id else None,
            **payload,
        },
    )


def group_invite_created(
    *,
    user_id: UUID,
    invite_id: UUID,
    moment_id: UUID,
    **payload: Any,
) -> DomainEvent:
    return DomainEvent(
        name="group_invite.created",
        user_id=user_id,
        context="GROUP",
        moment_id=moment_id,
        payload={"invite_id": str(invite_id), **payload},
    )


def group_invite_accepted(
    *,
    user_id: UUID,
    invite_id: UUID,
    moment_id: UUID,
    result: str,
    **payload: Any,
) -> DomainEvent:
    return DomainEvent(
        name="group_invite.accepted",
        user_id=user_id,
        context="GROUP",
        moment_id=moment_id,
        payload={"invite_id": str(invite_id), "result": result, **payload},
    )
