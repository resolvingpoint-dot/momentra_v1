"""Auth helpers for GraphQL resolvers — Principal + central AuthZ."""
from __future__ import annotations

from typing import Any
from uuid import UUID

from strawberry.types import Info

from app.api.graphql.context import GraphQLContext
from app.auth.principal import Principal
from app.authorization import ResourceRef, require
from app.authorization.require import GROUP_MOMENT_VIEW


def get_context(info: Info) -> GraphQLContext:
    return info.context


def require_principal(info: Info) -> Principal:
    return get_context(info).require_principal()


async def require_group_moment_view(info: Info, moment_id: UUID) -> Any:
    ctx = get_context(info)
    principal = ctx.require_principal()
    return await require(
        ctx.db,
        principal,
        GROUP_MOMENT_VIEW,
        ResourceRef(kind="group_moment", id=moment_id),
    )
