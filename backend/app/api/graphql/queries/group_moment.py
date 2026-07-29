"""groupMoment root query."""
from __future__ import annotations

from uuid import UUID

import strawberry
from graphql import GraphQLError
from strawberry.types import Info

from app.api.graphql.context import GraphQLContext, GraphQLUnauthenticated
from app.api.graphql.directives import require_permission
from app.api.graphql.errors import graphql_error_from_exception
from app.api.graphql.types.group_moment import GroupMoment
from app.application.queries.group_moment_detail import get_group_moment_detail
from app.authorization.require import GROUP_MOMENT_VIEW
from app.core.errors import AppError, NotFoundError


def _parse_moment_id(raw: strawberry.ID) -> UUID:
    try:
        return UUID(str(raw))
    except ValueError as exc:
        raise NotFoundError("Moment not found", code="not_found") from exc


@strawberry.type
class GroupMomentQuery:
    @strawberry.field(extensions=[require_permission(GROUP_MOMENT_VIEW, id_arg="id")])
    async def group_moment(
        self,
        info: Info,
        id: strawberry.ID,
    ) -> GroupMoment | None:
        ctx: GraphQLContext = info.context
        try:
            principal = ctx.require_principal()
            moment_id = _parse_moment_id(id)
            detail = await get_group_moment_detail(ctx.db, principal, moment_id)
        except GraphQLUnauthenticated as exc:
            raise graphql_error_from_exception(exc) from exc
        except AppError as exc:
            if exc.code == "not_found" or getattr(exc, "status_code", None) == 404:
                return None
            raise graphql_error_from_exception(exc) from exc
        except GraphQLError:
            raise
        except Exception as exc:  # noqa: BLE001
            raise graphql_error_from_exception(exc) from exc
        return GroupMoment.from_dto(detail)
