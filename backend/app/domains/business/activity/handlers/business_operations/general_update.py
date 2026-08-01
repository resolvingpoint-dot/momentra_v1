"""Handler: OPS_GENERAL_UPDATE — event payload only (no specialty table)."""
from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.business.models import BusinessActivityEvents


async def handle(session: AsyncSession, event: BusinessActivityEvents, payload: dict[str, Any]) -> UUID:
    return event.event_id
