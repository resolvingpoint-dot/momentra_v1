"""User account lifecycle — soft-delete / deactivate."""
from __future__ import annotations

import logging
from datetime import datetime, timezone

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.auth.refresh_sessions import RefreshSessionService
from app.domains.group import moment_store as store
from app.domains.group.models import GroupMomentMembers
from app.domains.moments.repository import MomentRepository
from app.domains.users.models import UserDeviceToken, UserModel
from app.domains.users.repository import UserRepository

logger = logging.getLogger(__name__)

_BLOCKED_MEMBER_STATUS = frozenset({"LEFT", "REMOVED", "DECLINED"})


class AccountDeletionService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = UserRepository(session)

    async def soft_delete(self, user: UserModel) -> None:
        """Mark user deleted, detach group access, revoke sessions, delete Firebase Auth.

        Personal/business rows stay orphaned (not hard-purged). Group access is
        detached so a re-signup with the same email cannot inherit inventory via
        leftover memberships or a still-valid access JWT on the old user.
        """
        now = datetime.now(timezone.utc)
        user.deleted_at = now
        # Scrub PII on the user row while keeping the FK-stable id.
        user.email = None
        user.phone = None
        user.display_name = "Deleted User"
        user.photo_url = None
        user.updated_at = now

        await self._detach_group_access(user.id, now)

        await RefreshSessionService(self.session).revoke_all_for_user(user.id)
        await self.session.execute(
            delete(UserDeviceToken).where(UserDeviceToken.user_id == user.id)
        )

        firebase_uid = user.firebase_uid
        await self.session.flush()

        try:
            from app.dependencies.auth import invalidate_uid_cache

            invalidate_uid_cache(firebase_uid)
        except Exception:
            logger.exception("Failed to invalidate uid cache during account deletion")

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

    async def _detach_group_access(self, user_id, now: datetime) -> None:
        """Archive owned GROUP moments and leave all group memberships."""
        moments_repo = MomentRepository(self.session)
        owned = await moments_repo.list_by_context(user_id, "GROUP")
        for moment in owned:
            if (moment.status or "").upper() == "ARCHIVED":
                continue
            moment.status = "ARCHIVED"
            moment.updated_at = now

        result = await self.session.execute(
            select(GroupMomentMembers).where(GroupMomentMembers.user_id == user_id)
        )
        for row in result.scalars().all():
            status_val = (row.status or "").upper()
            if row.left_at is not None or status_val in _BLOCKED_MEMBER_STATUS:
                continue
            row.status = "LEFT"
            row.left_at = now

        uid = str(user_id)
        # Detach runtime-store memberships on moments this user does not own
        # (JWT invite accept path). Owned moments are already archived above.
        try:
            group_moments = await moments_repo.list_by_context_type("GROUP")
        except Exception:
            logger.exception("Failed listing GROUP moments during membership detach")
            return

        for moment in group_moments:
            if moment.user_id == user_id:
                continue
            state = store.read_state(moment)
            members = state.get("runtime", {}).get("members") or []
            changed = False
            for member in members:
                if member.get("deleted"):
                    continue
                member_uid = str(member.get("user_id") or member.get("id") or "")
                if member_uid != uid:
                    continue
                member["status"] = "LEFT"
                member["deleted"] = True
                member["left_at"] = now.isoformat()
                member["updated_at"] = store.now_iso()
                changed = True
            if changed:
                store.write_state(moment, state)
