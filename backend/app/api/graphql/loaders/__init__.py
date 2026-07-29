"""Per-request DataLoaders with batch metrics."""
from __future__ import annotations

from typing import TYPE_CHECKING, Any
from uuid import UUID

from strawberry.dataloader import DataLoader

if TYPE_CHECKING:
    from app.api.graphql.context import GraphQLContext


class Loaders:
    def __init__(self, user_by_id: DataLoader[UUID, Any]) -> None:
        self.user_by_id = user_by_id


def build_loaders(ctx: GraphQLContext) -> Loaders:
    from app.api.graphql.loaders.users import create_user_by_id_loader

    return Loaders(user_by_id=create_user_by_id_loader(ctx))
