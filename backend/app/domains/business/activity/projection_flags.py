"""Attach is_editable / is_deletable to projection activity dicts for pulse/moments."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.business.activity.engine import _auth_flags
from app.domains.business.permissions import get_active_member


def _parse_uuid(value: Any) -> UUID | None:
    if value is None or value == "":
        return None
    if isinstance(value, UUID):
        return value
    try:
        return UUID(str(value))
    except (TypeError, ValueError):
        return None


def apply_edit_flags_to_activities(
    activities: list[dict[str, Any]],
    *,
    viewer_id: UUID,
    member,
) -> list[dict[str, Any]]:
    """Mutate and return activities with server-owned is_editable / is_deletable."""
    for row in activities:
        event = SimpleNamespace(
            action_type=row.get("action_type") or "",
            created_by=_parse_uuid(row.get("created_by")),
            is_voided=bool(row.get("is_voided", False)),
        )
        is_editable, is_deletable, _ = _auth_flags(
            event, viewer_id=viewer_id, member=member
        )
        row["is_editable"] = is_editable
        row["is_deletable"] = is_deletable
    return activities


async def enrich_activities_for_viewer(
    session: AsyncSession,
    moment_id: UUID,
    viewer_id: UUID,
    activities: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    member = await get_active_member(session, moment_id, viewer_id)
    return apply_edit_flags_to_activities(
        activities, viewer_id=viewer_id, member=member
    )
