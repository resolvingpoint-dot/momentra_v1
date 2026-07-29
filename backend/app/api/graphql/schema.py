"""Root GraphQL schema — reads only."""
from __future__ import annotations

import strawberry
from strawberry.fastapi import GraphQLRouter

from app.api.graphql.context import get_graphql_context
from app.api.graphql.extensions import build_extensions
from app.api.graphql.queries.activity import ActivityQuery
from app.api.graphql.queries.group_home import GroupHomeQuery
from app.api.graphql.queries.group_moment import GroupMomentQuery
from app.api.graphql.queries.personal_home import PersonalHomeQuery
from app.api.graphql.queries.pulse import PulseQuery
from app.core.config import settings


@strawberry.type
class Query(
    GroupMomentQuery, PulseQuery, ActivityQuery, PersonalHomeQuery, GroupHomeQuery
):
    """Root query type. Mutations are intentionally omitted (REST = commands)."""

    @strawberry.field
    def health(self) -> str:
        """Liveness probe for the GraphQL schema (no AuthN)."""
        return "ok"


schema = strawberry.Schema(
    query=Query,
    extensions=build_extensions(),
)


def create_graphql_router() -> GraphQLRouter:
    graphql_ide = "graphiql" if settings.debug and not settings.is_production else None
    return GraphQLRouter(
        schema,
        path="/graphql",
        context_getter=get_graphql_context,
        graphql_ide=graphql_ide,
    )
