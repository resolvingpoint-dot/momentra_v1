"""Shared helpers for activity typed handlers."""
from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.business.models import BusinessMomentMembers


def parse_date(raw: Any) -> date:
    if isinstance(raw, date) and not isinstance(raw, datetime):
        return raw
    if isinstance(raw, datetime):
        return raw.date()
    if isinstance(raw, str) and raw:
        try:
            return date.fromisoformat(raw[:10])
        except ValueError:
            pass
    return datetime.now(timezone.utc).date()


def minor_to_decimal(amount_minor: Any, *, currency: str = "INR") -> Decimal:
    """Convert minor units to major Decimal. Zero-decimal currencies (JPY, KWD use 3) handled simply."""
    minor = int(amount_minor or 0)
    code = (currency or "INR").upper()
    if code in {"JPY", "KRW", "VND"}:
        return Decimal(minor)
    if code in {"KWD", "BHD", "OMR"}:
        return Decimal(minor) / Decimal(1000)
    return Decimal(minor) / Decimal(100)


async def resolve_member_id(
    session: AsyncSession, moment_id: UUID, user_id: UUID | None
) -> UUID | None:
    if user_id is None:
        return None
    result = await session.execute(
        select(BusinessMomentMembers.member_id).where(
            BusinessMomentMembers.moment_id == moment_id,
            BusinessMomentMembers.user_id == user_id,
        )
    )
    return result.scalar_one_or_none()
