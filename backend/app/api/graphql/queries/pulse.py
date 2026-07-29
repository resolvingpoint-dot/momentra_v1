"""pulse root query — PERSONAL / GROUP / BUSINESS landing."""
from __future__ import annotations

from enum import Enum
from uuid import UUID

import strawberry
from strawberry.types import Info

from app.api.graphql.context import GraphQLContext, GraphQLUnauthenticated
from app.api.graphql.errors import graphql_error_from_exception
from app.api.graphql.types.pulse import PulseResult, pulse_from_dto
from app.application.queries.pulse import PulseScope, get_pulse_landing
from app.core.errors import AppError, NotFoundError


@strawberry.enum
class PulseScopeGQL(Enum):
    PERSONAL = "PERSONAL"
    GROUP = "GROUP"
    BUSINESS = "BUSINESS"


@strawberry.type
class PulseQuery:
    @strawberry.field
    async def pulse(
        self,
        info: Info,
        scope: PulseScopeGQL,
        force_refresh: bool = False,
        moment_type: str | None = None,
        workspace_id: strawberry.ID | None = None,
    ) -> PulseResult:
        """Pulse tab landing for the authenticated principal.

        Reuses Personal / Group / Business app services (same as REST pulse endpoints).
        Moment-scoped active pulse is deferred to a later additive vertical.
        """
        ctx: GraphQLContext = info.context
        try:
            principal = ctx.require_principal()
            ws: UUID | None = None
            if workspace_id:
                try:
                    ws = UUID(str(workspace_id))
                except ValueError as exc:
                    raise NotFoundError("Workspace not found", code="not_found") from exc
            dto = await get_pulse_landing(
                ctx.db,
                principal,
                PulseScope(scope.value),
                force_refresh=force_refresh,
                moment_type_code=moment_type,
                workspace_id=ws,
            )
            return pulse_from_dto(dto)
        except GraphQLUnauthenticated as exc:
            raise graphql_error_from_exception(exc) from exc
        except AppError as exc:
            raise graphql_error_from_exception(exc) from exc
