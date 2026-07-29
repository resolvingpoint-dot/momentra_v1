"""life root query — PERSONAL / GROUP / BUSINESS command centers."""
from __future__ import annotations

from enum import Enum

import strawberry
from strawberry.types import Info

from app.api.graphql.context import GraphQLContext, GraphQLUnauthenticated
from app.api.graphql.errors import graphql_error_from_exception
from app.api.graphql.types.life import LifeResult, life_from_dto
from app.application.queries.life import LifeScope, get_life
from app.core.errors import AppError


@strawberry.enum
class LifeScopeGQL(Enum):
    PERSONAL = "PERSONAL"
    GROUP = "GROUP"
    BUSINESS = "BUSINESS"


@strawberry.type
class LifeQuery:
    @strawberry.field
    async def life(
        self,
        info: Info,
        scope: LifeScopeGQL,
        force_refresh: bool = False,
    ) -> LifeResult:
        """Life Timeline / command-center for the authenticated principal."""
        ctx: GraphQLContext = info.context
        try:
            principal = ctx.require_principal()
            dto = await get_life(
                ctx.db,
                principal,
                LifeScope(scope.value),
                force_refresh=force_refresh,
            )
            return life_from_dto(dto)
        except GraphQLUnauthenticated as exc:
            raise graphql_error_from_exception(exc) from exc
        except AppError as exc:
            raise graphql_error_from_exception(exc) from exc
