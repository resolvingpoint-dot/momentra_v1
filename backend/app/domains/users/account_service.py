"""User account lifecycle — soft-delete / deactivate."""
from __future__ import annotations

import logging
from datetime import datetime, timezone

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.auth.refresh_sessions import RefreshSessionService
from app.domains.users.models import UserDeviceToken, UserModel
from app.domains.users.repository import UserRepository

logger = logging.getLogger(__name__)


class AccountDeletionService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = UserRepository(session)

    async def soft_delete(self, user: UserModel) -> None:
        """Mark user deleted, revoke sessions, clear device tokens, delete Firebase Auth.

        Personal/group/business rows are retained (orphaned by soft-delete) so
        historical data is not hard-purged in this release. Auth is blocked via
        ``deleted_at``; Firebase Auth is hard-deleted so the email can sign up again.
        """
        now = datetime.now(timezone.utc)
        user.deleted_at = now
        # Scrub PII on the user row while keeping the FK-stable id.
        user.email = None
        user.phone = None
        user.display_name = "Deleted User"
        user.photo_url = None
        user.updated_at = now

        await RefreshSessionService(self.session).revoke_all_for_user(user.id)
        await self.session.execute(
            delete(UserDeviceToken).where(UserDeviceToken.user_id == user.id)
        )

        firebase_uid = user.firebase_uid
        await self.session.flush()

        try:
            from app.core.firebase import delete_firebase_user

            delete_firebase_user(firebase_uid)
        except Exception:
            logger.exception(
                "Failed to delete Firebase user %s during account deletion",
                firebase_uid,
            )

        from app.domains.app_bootstrap.service import AppBootstrapService

        await AppBootstrapService(self.session).invalidate_cache(user.id)
