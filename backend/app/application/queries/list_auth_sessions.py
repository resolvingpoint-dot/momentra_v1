"""Sample application query — list auth sessions for the current user.

Proves the application-layer pattern without relocating domain services:
router / command → use-case → RefreshSessionService (domain).
"""
from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.auth.refresh_sessions import RefreshSessionService


@dataclass(frozen=True, slots=True)
class AuthSessionView:
    id: UUID
    user_agent: str | None
    ip: str | None
    created_at: str
    last_used_at: str | None
    expires_at: str


async def list_auth_sessions(
    session: AsyncSession, user_id: UUID
) -> list[AuthSessionView]:
    """Application query wrapping session listing for device management."""
    rows = await RefreshSessionService(session).list_active_for_user(user_id)
    return [
        AuthSessionView(
            id=row.id,
            user_agent=row.user_agent,
            ip=row.ip,
            created_at=row.created_at.isoformat(),
            last_used_at=row.last_used_at.isoformat() if row.last_used_at else None,
            expires_at=row.expires_at.isoformat(),
        )
        for row in rows
    ]
