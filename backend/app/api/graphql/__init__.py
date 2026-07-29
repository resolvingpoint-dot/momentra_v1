"""GraphQL read platform (Strawberry) — Phase 2."""
from __future__ import annotations

from app.api.graphql.schema import create_graphql_router, schema

__all__ = ["schema", "create_graphql_router"]
