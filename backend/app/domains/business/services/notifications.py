"""Business Notifications module: per-recipient notification inbox."""
from __future__ import annotations

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import NotFoundError
from app.core.service import Page
from app.domains.business import schemas as bs
from app.domains.business.repository import BusinessNotificationsRepository
from app.domains.business.services.base import BusinessModuleService, now_utc


class BusinessNotificationsModule(BusinessModuleService):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
        self.notifications_repo = BusinessNotificationsRepository(session)

    async def list_notifications(
        self, user_id: UUID, moment_id: UUID, *, status: str | None = None, page: int = 1, per_page: int = 20
    ) -> Page:
        await self._access(user_id, moment_id)
        filters: dict = {"moment_id": moment_id, "recipient_user_id": user_id}
        if status:
            filters["notification_status"] = status
        return await self._page(
            self.notifications_repo, bs.BusinessNotificationsSchema,
            filters=filters, order_by="-created_at", page=page, per_page=per_page,
        )

    async def mark_read(self, user_id: UUID, moment_id: UUID, notification_id: UUID) -> bs.BusinessNotificationsSchema:
        await self._access(user_id, moment_id)
        note = await self.notifications_repo.get_by_id(notification_id)
        if note is None or note.moment_id != moment_id or note.recipient_user_id != user_id:
            raise NotFoundError("Notification not found")
        if note.notification_status != "read":
            note.notification_status = "read"
            note.read_at = now_utc()
            await self.session.flush()
        schema = bs.BusinessNotificationsSchema.model_validate(note)
        await self.session.commit()
        return schema

    async def mark_all_read(self, user_id: UUID, moment_id: UUID) -> int:
        await self._access(user_id, moment_id)
        updated = await self.notifications_repo.update_where(
            {"moment_id": moment_id, "recipient_user_id": user_id, "notification_status__in": ["queued", "sent"]},
            {"notification_status": "read", "read_at": now_utc()},
        )
        await self.session.commit()
        return updated
