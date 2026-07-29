"""activity root query — Unified personal + moment-scoped GROUP/BUSINESS feeds."""
from __future__ import annotations

from enum import Enum
from uuid import UUID

import strawberry
from strawberry.types import Info

from app.api.graphql.context import GraphQLContext, GraphQLUnauthenticated
from app.api.graphql.errors import graphql_error_from_exception
from app.api.graphql.types.activity import ActivityResult, activity_from_dto
from app.application.queries.activity import ActivityScope, get_activity
from app.core.errors import AppError, NotFoundError


@strawberry.enum
class ActivityScopeGQL(Enum):
    PERSONAL = "PERSONAL"
    GROUP = "GROUP"
    BUSINESS = "BUSINESS"


@strawberry.type
class ActivityQuery:
    @strawberry.field
    async def activity(
        self,
        info: Info,
        scope: ActivityScopeGQL,
        moment_id: strawberry.ID | None = None,
        range: str = "all",
        domain: str = "all",
        kind: str = "all",
        q: str | None = None,
        first: int = 50,
        after: str | None = None,
        page: int = 1,
        status: str = "active",
    ) -> ActivityResult | None:
        """Unified Activity (PERSONAL) or moment-scoped GROUP/BUSINESS activity.

        GROUP/BUSINESS require ``momentId``. Missing/unauthorized → null (IDOR-safe).
        """
        ctx: GraphQLContext = info.context
        try:
            principal = ctx.require_principal()
            mid: UUID | None = None
            if moment_id:
                try:
                    mid = UUID(str(moment_id))
                except ValueError as exc:
                    raise NotFoundError("Moment not found", code="not_found") from exc
            dto = await get_activity(
                ctx.db,
                principal,
                ActivityScope(scope.value),
                moment_id=mid,
                range=range,
                domain=domain,
                kind=kind,
                q=q,
                after=after,
                first=first,
                page=page,
                status_filter=status,
            )
            return activity_from_dto(dto)
        except GraphQLUnauthenticated as exc:
            raise graphql_error_from_exception(exc) from exc
        except NotFoundError:
            return None
        except AppError as exc:
            if exc.code == "not_found" or getattr(exc, "status_code", None) == 404:
                return None
            raise graphql_error_from_exception(exc) from exc
