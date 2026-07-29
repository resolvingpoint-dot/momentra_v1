"""personalHome root query."""
from __future__ import annotations

import strawberry
from strawberry.types import Info

from app.api.graphql.context import GraphQLContext, GraphQLUnauthenticated
from app.api.graphql.errors import graphql_error_from_exception
from app.api.graphql.types.personal_home import PersonalHome
from app.application.queries.personal_home import get_personal_home
from app.core.errors import AppError


@strawberry.type
class PersonalHomeQuery:
    @strawberry.field
    async def personal_home(
        self,
        info: Info,
        force_refresh: bool = False,
        moment_type: str | None = None,
    ) -> PersonalHome:
        """Personal Moments Home — same payload as REST ``GET /personal/moments/home``."""
        ctx: GraphQLContext = info.context
        try:
            principal = ctx.require_principal()
            dto = await get_personal_home(
                ctx.db,
                principal,
                force_refresh=force_refresh,
                moment_type_code=moment_type,
            )
            return PersonalHome.from_dto(dto)
        except GraphQLUnauthenticated as exc:
            raise graphql_error_from_exception(exc) from exc
        except AppError as exc:
            raise graphql_error_from_exception(exc) from exc
