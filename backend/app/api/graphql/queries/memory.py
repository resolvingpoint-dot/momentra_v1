"""memory root query — PERSONAL / GROUP / BUSINESS."""
from __future__ import annotations

from enum import Enum

import strawberry
from strawberry.types import Info

from app.api.graphql.context import GraphQLContext, GraphQLUnauthenticated
from app.api.graphql.errors import graphql_error_from_exception
from app.api.graphql.types.memory import MemoryResult, memory_from_dto
from app.application.queries.memory import MemoryScope, get_memory
from app.core.errors import AppError


@strawberry.enum
class MemoryScopeGQL(Enum):
    PERSONAL = "PERSONAL"
    GROUP = "GROUP"
    BUSINESS = "BUSINESS"


@strawberry.type
class MemoryQuery:
    @strawberry.field
    async def memory(
        self,
        info: Info,
        scope: MemoryScopeGQL,
        force_refresh: bool = False,
        moment_type: str | None = None,
    ) -> MemoryResult:
        """Memory surface for the authenticated principal."""
        ctx: GraphQLContext = info.context
        try:
            principal = ctx.require_principal()
            dto = await get_memory(
                ctx.db,
                principal,
                MemoryScope(scope.value),
                force_refresh=force_refresh,
                moment_type_code=moment_type,
            )
            return memory_from_dto(dto)
        except GraphQLUnauthenticated as exc:
            raise graphql_error_from_exception(exc) from exc
        except AppError as exc:
            raise graphql_error_from_exception(exc) from exc
