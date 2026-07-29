"""GraphQL request context — Principal, DB session, loaders, correlation ids."""
from __future__ import annotations

import inspect
from typing import Any

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.fastapi import BaseContext

from app.auth.principal import Principal, principal_from_auth
from app.core.database import async_session_factory, get_db
from app.core.firebase import verify_firebase_token
from app.core.request_context import correlation_id_var, request_id_var, user_id_var
from app.core.security import decode_session_token
from app.domains.users.service import UserService
from app.api.graphql.observability import GraphQLTelemetry


class GraphQLUnauthenticated(Exception):
    """Raised when Bearer AuthN fails for a GraphQL operation."""

    code = "unauthenticated"


class GraphQLContext(BaseContext):
    """Per-request GraphQL context (must subclass strawberry BaseContext)."""

    def __init__(
        self,
        *,
        db: AsyncSession,
        principal: Principal | None,
        request_id: str | None = None,
        correlation_id: str | None = None,
        loaders: Any = None,
        owns_session: bool = True,
        auth_error: str | None = None,
    ) -> None:
        super().__init__()
        self.db = db
        self.principal = principal
        self.request_id = request_id
        self.correlation_id = correlation_id
        self.loaders = loaders
        self.owns_session = owns_session
        self._auth_error = auth_error
        self.telemetry = GraphQLTelemetry()

    def require_principal(self) -> Principal:
        if self.principal is None:
            raise GraphQLUnauthenticated(self._auth_error or "Authentication required")
        return self.principal


async def _resolve_auth_user(request: Request) -> dict[str, Any] | None:
    auth = request.headers.get("authorization") or ""
    if not auth.lower().startswith("bearer "):
        return None
    token = auth[7:].strip()
    if not token:
        return None
    try:
        decoded = verify_firebase_token(token)
        uid = decoded["uid"]
        request.state.user_uid = uid
        return {"type": "firebase", "uid": uid, "payload": decoded}
    except Exception:
        pass
    try:
        decoded = decode_session_token(token)
    except Exception:
        return None
    if decoded.get("type") == "refresh":
        return None
    uid = decoded["sub"]
    request.state.user_uid = uid
    return {"type": "session", "uid": uid, "payload": decoded}


async def _acquire_session(request: Request) -> tuple[AsyncSession, bool]:
    """Return (session, owns_session). Honors FastAPI get_db overrides (tests)."""
    override = request.app.dependency_overrides.get(get_db)
    if override is not None:
        result = override()
        if inspect.isasyncgen(result):
            session = await result.__anext__()
            return session, True
        if inspect.isgenerator(result):
            session = next(result)
            return session, False
        return result, False

    if async_session_factory is None:
        raise RuntimeError("DATABASE_URL not configured")
    return async_session_factory(), True


async def get_graphql_context(request: Request) -> GraphQLContext:
    """Strawberry context_getter (FastAPI Depends) — returns BaseContext subclass."""
    rid = getattr(request.state, "request_id", None) or request_id_var.get()
    cid = getattr(request.state, "correlation_id", None) or correlation_id_var.get() or rid

    session, owns_session = await _acquire_session(request)
    principal: Principal | None = None
    auth_error: str | None = None

    auth_user = await _resolve_auth_user(request)
    if auth_user is not None:
        user = await UserService(session).get_user(auth_user["uid"])
        if user is None:
            auth_error = "User not found"
        else:
            user_id_var.set(str(user.id))
            request.state.user_id = str(user.id)
            principal = principal_from_auth(user_id=user.id, auth_user=auth_user)
    else:
        auth_error = "Missing or invalid Authorization header"

    from app.api.graphql.loaders import build_loaders

    ctx = GraphQLContext(
        db=session,
        principal=principal,
        request_id=rid,
        correlation_id=cid,
        owns_session=owns_session,
        auth_error=auth_error,
    )
    ctx.telemetry.apq_status = (
        getattr(request.state, "apq_status", None)
        or request.scope.get("graphql_apq_status")
        or "bypass"
    )
    if principal is not None:
        ctx.telemetry.principal_id = str(principal.user_id)
    ctx.loaders = build_loaders(ctx)
    return ctx


async def cleanup_graphql_context(ctx: GraphQLContext) -> None:
    """Commit/rollback and close when this context owns the session."""
    if not ctx.owns_session:
        return
    try:
        await ctx.db.commit()
    except Exception:
        await ctx.db.rollback()
        raise
    finally:
        await ctx.db.close()
