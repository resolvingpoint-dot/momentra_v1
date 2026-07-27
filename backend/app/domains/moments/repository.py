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

    async def delete_owned(self, user_id: UUID, moment_id: UUID) -> bool:
        moment = await self.get_by_user_and_id(user_id, moment_id)
        if moment is None:
            return False
        await self.session.delete(moment)
        return True
