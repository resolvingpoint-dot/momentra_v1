"""HTTP middleware for GraphQL body size limits and APQ document resolution."""
from __future__ import annotations

import json
import logging

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from graphql import GraphQLError
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.api.graphql.apq import resolve_query_document
from app.core.config import settings

logger = logging.getLogger(__name__)


def _error_payload(message: str, code: str, status_code: int = 200) -> JSONResponse:
    return JSONResponse(
        {
            "data": None,
            "errors": [{"message": message, "extensions": {"code": code}}],
        },
        status_code=status_code,
    )


class GraphQLHardeningMiddleware:
    """Pure ASGI middleware — safer than BaseHTTPMiddleware for body rewrite (APQ)."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        path = scope.get("path") or ""
        method = (scope.get("method") or "").upper()
        if path.rstrip("/") != "/graphql" or method != "POST":
            await self.app(scope, receive, send)
            return

        body = b""
        while True:
            message = await receive()
            if message["type"] != "http.request":
                continue
            body += message.get("body", b"")
            if not message.get("more_body"):
                break

        if len(body) > settings.graphql_max_body_bytes:
            response = _error_payload(
                f"Request body too large (max {settings.graphql_max_body_bytes} bytes)",
                "body_too_large",
                status_code=413,
            )
            await response(scope, receive, send)
            return

        try:
            payload = json.loads(body.decode("utf-8") or "{}")
        except Exception:
            response = _error_payload("Invalid JSON body", "invalid_json", status_code=400)
            await response(scope, receive, send)
            return

        if not isinstance(payload, dict):
            response = _error_payload(
                "Invalid GraphQL payload", "invalid_json", status_code=400
            )
            await response(scope, receive, send)
            return

        try:
            query, apq_status = await resolve_query_document(payload)
        except GraphQLError as exc:
            code = (exc.extensions or {}).get("code") or "persisted_query_error"
            response = _error_payload(str(exc.message), str(code))
            await response(scope, receive, send)
            return

        if query is None and settings.graphql_persisted_only:
            response = _error_payload(
                "Persisted queries are required",
                "persisted_query_required",
            )
            await response(scope, receive, send)
            return

        if query is not None:
            payload = {**payload, "query": query}

        new_body = json.dumps(payload).encode("utf-8")
        headers = [
            (k, v)
            for k, v in scope.get("headers", [])
            if k.lower() != b"content-length"
        ]
        headers.append((b"content-length", str(len(new_body)).encode("ascii")))
        new_scope: Scope = {**scope, "headers": headers}
        new_scope["graphql_apq_status"] = apq_status
        # Also mirror onto Starlette request.state when already present.
        state = new_scope.get("state")
        if isinstance(state, dict):
            state["apq_status"] = apq_status
        elif state is not None:
            try:
                state.apq_status = apq_status  # type: ignore[attr-defined]
            except Exception:  # noqa: BLE001
                pass
        else:
            new_scope["state"] = {"apq_status": apq_status}

        sent = False

        async def new_receive() -> Message:
            nonlocal sent
            if sent:
                return {"type": "http.disconnect"}
            sent = True
            return {"type": "http.request", "body": new_body, "more_body": False}

        await self.app(new_scope, new_receive, send)


def add_graphql_hardening(app: FastAPI) -> None:
    app.add_middleware(GraphQLHardeningMiddleware)
