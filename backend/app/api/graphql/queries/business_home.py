"""businessHome root query."""
from __future__ import annotations

from uuid import UUID

import strawberry
from strawberry.types import Info

from app.api.graphql.context import GraphQLContext, GraphQLUnauthenticated
from app.api.graphql.errors import graphql_error_from_exception
from app.api.graphql.types.business_home import BusinessHome
from app.application.queries.business_home import get_business_home
from app.core.errors import AppError, NotFoundError


@strawberry.type
class BusinessHomeQuery:
    @strawberry.field
    async def business_home(
        self,
        info: Info,
        workspace_id: strawberry.ID | None = None,
    ) -> BusinessHome:
        """Business Moments Home — same as REST ``GET /business/moments/home``."""
        ctx: GraphQLContext = info.context
        try:
            principal = ctx.require_principal()
            ws: UUID | None = None
            if workspace_id:
                try:
                    ws = UUID(str(workspace_id))
                except ValueError as exc:
                    raise NotFoundError("Workspace not found", code="not_found") from exc
            dto = await get_business_home(ctx.db, principal, workspace_id=ws)
            return BusinessHome.from_dto(dto)
        except GraphQLUnauthenticated as exc:
            raise graphql_error_from_exception(exc) from exc
        except AppError as exc:
            raise graphql_error_from_exception(exc) from exc
