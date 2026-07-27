"""Bridge shared ``moments`` rows to ``personal_moments`` for personal_* FK tables."""
from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.moments.models import MomentModel
from app.domains.personal.catalog import moment_type_name, normalize_moment_type_code
from app.domains.personal.models import PersonalMomentTypes, PersonalMoments

_ACTIVE = "ACTIVE"
_SHARED_TO_PERSONAL_STATUS = {
    "DRAFT": "DRAFT",
    "SETUP": "DRAFT",
    "ACTIVE": "ACTIVE",
    "PAUSED": "PAUSED",
    "ARCHIVED": "ARCHIVED",
}


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


async def _resolve_moment_type_id(
    session: AsyncSession, moment_type_code: str
) -> UUID | None:
    code = normalize_moment_type_code(moment_type_code)
    result = await session.execute(
        select(PersonalMomentTypes.moment_type_id).where(
            PersonalMomentTypes.moment_type_code == code
        )
    )
    row = result.scalar_one_or_none()
    return row


async def ensure_personal_moment(
    session: AsyncSession, shared_moment: MomentModel
) -> UUID:
    """Upsert ``personal_moments`` using the same id as the shared moment."""
    code = normalize_moment_type_code(shared_moment.moment_type or "")
    type_id = await _resolve_moment_type_id(session, code)
    if type_id is None:
        raise ValueError(f"Unknown personal moment type code: {code}")

    moment_id = shared_moment.id
    result = await session.execute(
        select(PersonalMoments).where(PersonalMoments.moment_id == moment_id)
    )
    existing = result.scalar_one_or_none()
    now = _now()
    personal_status = _SHARED_TO_PERSONAL_STATUS.get(
        shared_moment.status or "DRAFT", "DRAFT"
    )
    name = (
        shared_moment.title
        or moment_type_name(code)
        or "Untitled"
    )

    if existing is None:
        activated_at = now if personal_status == _ACTIVE else None
        row = PersonalMoments(
            moment_id=moment_id,
            user_id=shared_moment.user_id,
            moment_type_id=type_id,
            moment_name=name[:150],
            status=personal_status,
            activated_at=activated_at,
            last_activity_at=now,
            created_at=now,
            updated_at=now,
        )
        session.add(row)
        await session.flush()
        return moment_id

    existing.moment_type_id = type_id
    existing.moment_name = name[:150]
    existing.status = personal_status
    existing.updated_at = now
    if personal_status == _ACTIVE and existing.activated_at is None:
        existing.activated_at = now
    await session.flush()
    return moment_id


async def try_ensure_personal_moment(
    session: AsyncSession, shared_moment: MomentModel
) -> bool:
    """Best-effort sync; returns False when personal tables are unavailable."""
    try:
        await ensure_personal_moment(session, shared_moment)
        return True
    except Exception:
        return False
