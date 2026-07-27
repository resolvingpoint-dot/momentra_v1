"""Persist Lifestyle setup drafts on moment media rows."""
from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.moments.models import MomentMediaModel

_SETUP_DRAFT_TYPE = "setup_draft"


async def load_setup_draft(
    session: AsyncSession, moment_id: UUID
) -> dict[str, Any] | None:
    result = await session.execute(
        select(MomentMediaModel).where(
            MomentMediaModel.moment_id == moment_id,
            MomentMediaModel.media_type == _SETUP_DRAFT_TYPE,
        )
    )
    row = result.scalar_one_or_none()
    if row is None or not row.media_metadata:
        return None
    draft = row.media_metadata.get("setup_draft")
    return draft if isinstance(draft, dict) else None


async def save_setup_draft(
    session: AsyncSession,
    user_id: UUID,
    moment_id: UUID,
    answers: dict[str, Any],
) -> None:
    result = await session.execute(
        select(MomentMediaModel).where(
            MomentMediaModel.moment_id == moment_id,
            MomentMediaModel.media_type == _SETUP_DRAFT_TYPE,
        )
    )
    row = result.scalar_one_or_none()
    payload = {"setup_draft": answers}
    if row is None:
        row = MomentMediaModel(
            user_id=user_id,
            moment_id=moment_id,
            storage_path=f"setup-draft/{moment_id}",
            media_type=_SETUP_DRAFT_TYPE,
            media_metadata=payload,
        )
        session.add(row)
    else:
        row.media_metadata = payload
    await session.flush()
