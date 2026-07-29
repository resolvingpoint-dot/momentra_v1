"""Batch load users by id for displayName / paidBy fields."""
from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import select
from strawberry.dataloader import DataLoader

from app.domains.users.models import UserModel

if TYPE_CHECKING:
    from app.api.graphql.context import GraphQLContext


def create_user_by_id_loader(ctx: GraphQLContext) -> DataLoader[UUID, UserModel | None]:
    async def load_fn(keys: list[UUID]) -> list[UserModel | None]:
        tel = getattr(ctx, "telemetry", None)
        if tel is not None:
            tel.dataloader_batches += 1
        if not keys:
            return []
        result = await ctx.db.execute(select(UserModel).where(UserModel.id.in_(keys)))
        rows = list(result.scalars().all())
        by_id = {row.id: row for row in rows}
        return [by_id.get(key) for key in keys]

    return DataLoader(load_fn=load_fn)
