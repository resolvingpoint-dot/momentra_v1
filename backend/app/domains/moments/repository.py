from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.moments.models import MomentModel


class MomentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        user_id: UUID,
        context_type: str,
        moment_type: str | None = None,
        title: str | None = None,
        description: str | None = None,
        status: str = "DRAFT",
        setup_state: str = "EMPTY",
    ) -> MomentModel:
        now = datetime.now(timezone.utc)
        moment = MomentModel(
            id=uuid4(),
            user_id=user_id,
            context_type=context_type,
            moment_type=moment_type,
            title=title,
            description=description,
            status=status,
            setup_state=setup_state,
            created_at=now,
            updated_at=now,
        )
        self.session.add(moment)
        return moment

    async def get_by_id(self, moment_id: UUID) -> MomentModel | None:
        stmt = select(MomentModel).where(MomentModel.id == moment_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_user_id(
        self, user_id: UUID, offset: int = 0, limit: int = 20
    ) -> list[MomentModel]:
        stmt = (
            select(MomentModel)
            .where(MomentModel.user_id == user_id)
            .order_by(MomentModel.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count_by_context(self, user_id: UUID) -> dict[str, int]:
        stmt = (
            select(MomentModel.context_type, func.count(MomentModel.id))
            .where(MomentModel.user_id == user_id)
            .group_by(MomentModel.context_type)
        )
        result = await self.session.execute(stmt)
        counts: dict[str, int] = {}
        for row in result:
            counts[row[0].lower()] = row[1]
        return counts

    async def total_count(self, user_id: UUID) -> int:
        stmt = select(func.count(MomentModel.id)).where(
            MomentModel.user_id == user_id
        )
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def count_by_context_type(self, user_id: UUID, context_type: str) -> int:
        stmt = select(func.count(MomentModel.id)).where(
            MomentModel.user_id == user_id,
            MomentModel.context_type == context_type,
        )
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def get_recent(self, user_id: UUID, limit: int = 5) -> list[MomentModel]:
        stmt = (
            select(MomentModel)
            .where(MomentModel.user_id == user_id)
            .order_by(MomentModel.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_user_and_id(self, user_id: UUID, moment_id: UUID) -> MomentModel | None:
        stmt = select(MomentModel).where(
            MomentModel.id == moment_id, MomentModel.user_id == user_id
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_context(
        self,
        user_id: UUID,
        context_type: str,
        status: str | None = None,
    ) -> list[MomentModel]:
        stmt = select(MomentModel).where(
            MomentModel.user_id == user_id,
            MomentModel.context_type == context_type,
        )
        if status is not None:
            stmt = stmt.where(MomentModel.status == status)
        stmt = stmt.order_by(MomentModel.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_by_context_type(
        self,
        context_type: str,
        status: str | None = None,
    ) -> list[MomentModel]:
        """All moments for a context (no owner filter). Used for membership scans."""
        stmt = select(MomentModel).where(MomentModel.context_type == context_type)
        if status is not None:
            stmt = stmt.where(MomentModel.status == status)
        stmt = stmt.order_by(MomentModel.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_group_accessible(self, user_id: UUID) -> list[MomentModel]:
        """Group inventory: owned moments ∪ invitee/member-accessible moments.

        Membership is resolved from:
        - ``group_moment_members`` (when a relational roster row exists), and/or
        - moment runtime store ``members`` (JWT invite accept path for shared moments).

        Cost is O(user inventory): roster moment IDs are batch-loaded; runtime-only
        members use a narrowed description contains query (never full GROUP scan).
        """
        from app.domains.group import moment_store as store
        from app.domains.group.models import GroupMomentMembers

        owned = await self.list_by_context(user_id, "GROUP")
        by_id: dict[UUID, MomentModel] = {m.id: m for m in owned}

        _blocked = frozenset({"LEFT", "REMOVED", "DECLINED"})
        try:
            result = await self.session.execute(
                select(GroupMomentMembers).where(
                    GroupMomentMembers.user_id == user_id,
                )
            )
            roster_rows = list(result.scalars().all())
        except Exception:
            roster_rows = []

        roster_ids = {
            row.moment_id
            for row in roster_rows
            if row.moment_id not in by_id
            and row.left_at is None
            and (row.status or "").upper() not in _blocked
        }
        if roster_ids:
            result = await self.session.execute(
                select(MomentModel).where(
                    MomentModel.id.in_(roster_ids),
                    MomentModel.context_type == "GROUP",
                )
            )
            for moment in result.scalars().all():
                by_id[moment.id] = moment

        # Compatibility path for legacy invite accepts that predate relational
        # roster rows. Filter candidates in SQL by the exact serialized user_id
        # token, then parse/verify them; never hydrate every GROUP moment.
        uid = str(user_id)
        runtime_member_token = f'"user_id": "{uid}"'
        legacy_stmt = select(MomentModel).where(
            MomentModel.context_type == "GROUP",
            MomentModel.description.contains(runtime_member_token),
        )
        if by_id:
            legacy_stmt = legacy_stmt.where(MomentModel.id.notin_(tuple(by_id)))
        result = await self.session.execute(legacy_stmt)
        for moment in result.scalars().all():
            if moment.id in by_id:
                continue
            for member in store.list_accepted_members(moment):
                if str(member.get("user_id") or "") == uid:
                    by_id[moment.id] = moment
                    break

        def _sort_key(m: MomentModel) -> datetime:
            created = m.created_at
            if created is None:
                return datetime(1970, 1, 1, tzinfo=timezone.utc)
            if created.tzinfo is None:
                return created.replace(tzinfo=timezone.utc)
            return created

        return sorted(by_id.values(), key=_sort_key, reverse=True)

    async def list_business_accessible(self, user_id: UUID) -> list[MomentModel]:
        """Business inventory: owned moments ∪ active/configured members.

        Membership is resolved from ``business_moment_members`` (invite accept
        and setup roster). Matches Group's ``list_group_accessible`` contract.
        """
        from app.domains.business.models import BusinessMomentMembers

        owned = await self.list_by_context(user_id, "BUSINESS")
        by_id: dict[UUID, MomentModel] = {m.id: m for m in owned}

        _allowed = frozenset({"active", "configured"})
        try:
            result = await self.session.execute(
                select(BusinessMomentMembers).where(
                    BusinessMomentMembers.user_id == user_id,
                )
            )
            roster_rows = list(result.scalars().all())
        except Exception:
            roster_rows = []

        for row in roster_rows:
            mid = row.moment_id
            if mid in by_id:
                continue
            status_val = (row.member_status or "").lower()
            if status_val not in _allowed:
                continue
            moment = await self.get_by_id(mid)
            if moment is None:
                continue
            if (moment.context_type or "").upper() != "BUSINESS":
                continue
            by_id[moment.id] = moment

        def _sort_key(m: MomentModel) -> datetime:
            created = m.created_at
            if created is None:
                return datetime(1970, 1, 1, tzinfo=timezone.utc)
            if created.tzinfo is None:
                return created.replace(tzinfo=timezone.utc)
            return created

        return sorted(by_id.values(), key=_sort_key, reverse=True)

    async def delete_owned(self, user_id: UUID, moment_id: UUID) -> bool:
        moment = await self.get_by_user_and_id(user_id, moment_id)
        if moment is None:
            return False
        await self.session.delete(moment)
        return True
