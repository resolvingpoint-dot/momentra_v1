"""Declarative field-level authorization for Strawberry resolvers.

Usage::

    @strawberry.field(extensions=[require_permission(\"group.moment.view\")])
    async def group_moment(self, info: Info, id: strawberry.ID) -> ...:
        ...

Nested fields on an already-authorized parent can pass ``from_parent=True``
and ``parent_id_attr=\"_moment_id\"`` (or reuse the parent's moment id).
"""
from __future__ import annotations

from typing import Any
from uuid import UUID

from graphql import GraphQLError
from strawberry.extensions import FieldExtension
from strawberry.types import Info

from app.api.graphql.context import GraphQLUnauthenticated
from app.api.graphql.errors import graphql_error_from_exception
from app.authorization import ResourceRef, require
from app.core.errors import AppError


class RequirePermissionExtension(FieldExtension):
    def __init__(
        self,
        action: str,
        *,
        resource_kind: str = "group_moment",
        id_arg: str = "id",
        from_parent: bool = False,
        parent_id_attr: str = "id",
    ) -> None:
        self.action = action
        self.resource_kind = resource_kind
        self.id_arg = id_arg
        self.from_parent = from_parent
        self.parent_id_attr = parent_id_attr

    def _resolve_resource_id(self, source: Any, kwargs: dict[str, Any]) -> UUID:
        raw: Any
        if self.from_parent:
            raw = getattr(source, self.parent_id_attr, None)
            if raw is None and hasattr(source, "_detail"):
                raw = getattr(source._detail, "id", None)
        else:
            raw = kwargs.get(self.id_arg)
        if raw is None:
            raise GraphQLError(
                f"Missing resource id for permission {self.action}",
                extensions={"code": "authz_missing_resource"},
            )
        try:
            return UUID(str(raw))
        except ValueError as exc:
            raise GraphQLError(
                "Invalid resource id",
                extensions={"code": "not_found"},
            ) from exc

    async def resolve_async(self, next_, source, info: Info, **kwargs):  # type: ignore[no-untyped-def]
        from app.api.graphql.context import GraphQLContext

        ctx: GraphQLContext = info.context
        try:
            principal = ctx.require_principal()
            resource_id = self._resolve_resource_id(source, kwargs)
            await require(
                ctx.db,
                principal,
                self.action,
                ResourceRef(kind=self.resource_kind, id=resource_id),
            )
            return await next_(source, info, **kwargs)
        except GraphQLUnauthenticated as exc:
            raise graphql_error_from_exception(exc) from exc
        except AppError as exc:
            raise graphql_error_from_exception(exc) from exc

    def resolve(self, next_, source, info: Info, **kwargs):  # type: ignore[no-untyped-def]
        # Sync path not used by Momentra GraphQL resolvers.
        raise NotImplementedError("Use async resolvers with require_permission")


def require_permission(
    action: str,
    *,
    resource_kind: str = "group_moment",
    id_arg: str = "id",
    from_parent: bool = False,
    parent_id_attr: str = "id",
) -> RequirePermissionExtension:
    """Build a Strawberry field extension enforcing central AuthZ."""
    return RequirePermissionExtension(
        action,
        resource_kind=resource_kind,
        id_arg=id_arg,
        from_parent=from_parent,
        parent_id_attr=parent_id_attr,
    )
