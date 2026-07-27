from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Protocol
from uuid import UUID

from app.core.errors import NotFoundError
from app.domains.moments.models import MomentModel
from app.domains.moments.repository import MomentRepository


@dataclass(slots=True)
class MomentRef:
    """Lightweight moment handle returned by the engine (no ORM leakage)."""

    moment_id: UUID
    user_id: UUID
    context: str
    moment_type: str | None
    status: str
    setup_state: str | None = None
    title: str | None = None
    description: str | None = None


class MomentAdapter(Protocol):
    """Persistence port implemented per storage backend / context."""

    context: str

    async def create(
        self,
        user_id: UUID,
        *,
        moment_type: str | None,
        title: str | None = None,
        description: str | None = None,
        status: str = "DRAFT",
        setup_state: str = "EMPTY",
        **extra: Any,
    ) -> MomentRef: ...

    async def get_owned(self, user_id: UUID, moment_id: UUID) -> MomentRef: ...

    async def get_model(self, user_id: UUID, moment_id: UUID) -> MomentModel: ...

    async def update_fields(self, user_id: UUID, moment_id: UUID, **fields: Any) -> MomentRef: ...

    async def delete(self, user_id: UUID, moment_id: UUID) -> None: ...


def _ref_from_model(moment: MomentModel) -> MomentRef:
    return MomentRef(
        moment_id=moment.id,
        user_id=moment.user_id,
        context=moment.context_type,
        moment_type=moment.moment_type,
        status=moment.status,
        setup_state=moment.setup_state,
        title=moment.title,
        description=moment.description,
    )


class SharedMomentsAdapter:
    """Adapter for the shared ``moments`` table (Personal / My Money / bootstrap)."""

    def __init__(self, session, *, context: str) -> None:
        self.context = context
        self._session = session
        self._repo = MomentRepository(session)

    @property
    def session(self):
        return self._session

    async def create(
        self,
        user_id: UUID,
        *,
        moment_type: str | None,
        title: str | None = None,
        description: str | None = None,
        status: str = "DRAFT",
        setup_state: str = "EMPTY",
        **extra: Any,
    ) -> MomentRef:
        moment = await self._repo.create(
            user_id=user_id,
            context_type=self.context,
            moment_type=moment_type,
            title=title,
            description=description,
            status=status,
            setup_state=setup_state,
        )
        return _ref_from_model(moment)

    async def get_owned(self, user_id: UUID, moment_id: UUID) -> MomentRef:
        moment = await self._repo.get_by_user_and_id(user_id, moment_id)
        if moment is None or moment.context_type != self.context:
            raise NotFoundError("Moment not found")
        return _ref_from_model(moment)

    async def get_model(self, user_id: UUID, moment_id: UUID) -> MomentModel:
        moment = await self._repo.get_by_user_and_id(user_id, moment_id)
        if moment is None or moment.context_type != self.context:
            raise NotFoundError("Moment not found")
        return moment

    async def update_fields(self, user_id: UUID, moment_id: UUID, **fields: Any) -> MomentRef:
        moment = await self.get_model(user_id, moment_id)
        for key, value in fields.items():
            if hasattr(moment, key):
                setattr(moment, key, value)
        moment.updated_at = datetime.now(timezone.utc)
        return _ref_from_model(moment)

    async def delete(self, user_id: UUID, moment_id: UUID) -> None:
        moment = await self.get_model(user_id, moment_id)
        await self._session.delete(moment)
