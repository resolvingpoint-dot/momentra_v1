from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.domains.auth.models import AuthRefreshSessionModel


class RefreshSessionError(Exception):
    """Invalid, expired, revoked, or reused refresh token."""


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def mint_refresh_token() -> str:
    return secrets.token_urlsafe(48)


class RefreshSessionService:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def create_session(
        self,
        *,
        user_id: UUID,
        firebase_uid: str,
        family_id: UUID | None = None,
        user_agent: str | None = None,
        ip: str | None = None,
    ) -> tuple[str, AuthRefreshSessionModel]:
        plaintext = mint_refresh_token()
        now = datetime.now(timezone.utc)
        row = AuthRefreshSessionModel(
            id=uuid4(),
            user_id=user_id,
            firebase_uid=firebase_uid,
            token_hash=hash_refresh_token(plaintext),
            family_id=family_id or uuid4(),
            expires_at=now + timedelta(hours=settings.session_expire_hours),
            revoked_at=None,
            created_at=now,
            last_used_at=None,
            user_agent=(user_agent or "")[:512] or None,
            ip=(ip or "")[:64] or None,
        )
        self._db.add(row)
        await self._db.flush()
        return plaintext, row

    async def get_by_token(self, plaintext: str) -> AuthRefreshSessionModel | None:
        token_hash = hash_refresh_token(plaintext)
        result = await self._db.execute(
            select(AuthRefreshSessionModel).where(
                AuthRefreshSessionModel.token_hash == token_hash
            )
        )
        return result.scalar_one_or_none()

    async def rotate(
        self,
        plaintext: str,
        *,
        user_agent: str | None = None,
        ip: str | None = None,
    ) -> tuple[str, AuthRefreshSessionModel]:
        session = await self.get_by_token(plaintext)
        if session is None:
            raise RefreshSessionError("unknown refresh token")

        now = datetime.now(timezone.utc)
        if session.revoked_at is not None:
            # Reuse of a rotated token → revoke the whole family.
            await self.revoke_family(session.family_id)
            raise RefreshSessionError("refresh token reuse detected")

        expires = session.expires_at
        if expires.tzinfo is None:
            expires = expires.replace(tzinfo=timezone.utc)
        if expires <= now:
            session.revoked_at = now
            await self._db.flush()
            raise RefreshSessionError("refresh token expired")

        session.revoked_at = now
        session.last_used_at = now
        await self._db.flush()

        return await self.create_session(
            user_id=session.user_id,
            firebase_uid=session.firebase_uid,
            family_id=session.family_id,
            user_agent=user_agent,
            ip=ip,
        )

    async def revoke_token(self, plaintext: str) -> bool:
        session = await self.get_by_token(plaintext)
        if session is None:
            return False
        if session.revoked_at is None:
            session.revoked_at = datetime.now(timezone.utc)
            await self._db.flush()
        return True

    async def revoke_family(self, family_id: UUID) -> int:
        result = await self._db.execute(
            select(AuthRefreshSessionModel).where(
                AuthRefreshSessionModel.family_id == family_id
            )
        )
        rows = list(result.scalars().all())
        now = datetime.now(timezone.utc)
        count = 0
        for row in rows:
            if row.revoked_at is None:
                row.revoked_at = now
                count += 1
        await self._db.flush()
        return count

    async def revoke_all_for_user(self, user_id: UUID) -> int:
        result = await self._db.execute(
            select(AuthRefreshSessionModel).where(
                AuthRefreshSessionModel.user_id == user_id
            )
        )
        rows = list(result.scalars().all())
        now = datetime.now(timezone.utc)
        count = 0
        for row in rows:
            if row.revoked_at is None:
                row.revoked_at = now
                count += 1
        await self._db.flush()
        return count
