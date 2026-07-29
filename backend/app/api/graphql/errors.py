"""Map domain / AppError exceptions into GraphQL errors with REST-aligned codes."""
from __future__ import annotations

from graphql import GraphQLError

from app.api.graphql.context import GraphQLUnauthenticated
from app.core.errors import AppError


def graphql_error_from_exception(exc: BaseException) -> GraphQLError:
    if isinstance(exc, GraphQLUnauthenticated):
        return GraphQLError(
            str(exc) or "Authentication required",
            extensions={"code": "unauthenticated"},
        )
    if isinstance(exc, AppError):
        return GraphQLError(
            exc.message,
            extensions={
                "code": exc.code,
                "details": exc.details,
            },
        )
    if isinstance(exc, GraphQLError):
        return exc
    # Domain FastAPI HTTPException still appears from some services.
    from fastapi import HTTPException

    if isinstance(exc, HTTPException):
        detail = exc.detail
        code = "permission_denied" if exc.status_code == 403 else "app_error"
        message = detail if isinstance(detail, str) else str(detail)
        if isinstance(detail, dict):
            code = str(detail.get("code") or code)
            message = str(detail.get("message") or message)
        if exc.status_code == 404:
            code = "not_found"
        return GraphQLError(message, extensions={"code": code})
    return GraphQLError(str(exc) or "Internal error", extensions={"code": "internal"})
