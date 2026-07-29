"""groupHome root query."""
from __future__ import annotations

import strawberry
from strawberry.types import Info

from app.api.graphql.context import GraphQLContext, GraphQLUnauthenticated
from app.api.graphql.errors import graphql_error_from_exception
from app.api.graphql.types.group_home import GroupHome
from app.application.queries.group_home import get_group_home
from app.core.errors import AppError


@strawberry.type
class GroupHomeQuery:
    @strawberry.field
    async def group_home(self, info: Info) -> GroupHome:
        """Group Moments Home — same payload as REST ``GET /group/moments/home``."""
        ctx: GraphQLContext = info.context
        try:
            principal = ctx.require_principal()
            dto = await get_group_home(ctx.db, principal)
            return GroupHome.from_dto(dto)
        except GraphQLUnauthenticated as exc:
            raise graphql_error_from_exception(exc) from exc
        except AppError as exc:
            raise graphql_error_from_exception(exc) from exc
