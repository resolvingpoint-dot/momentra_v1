"""HTTP security headers middleware."""
from __future__ import annotations

from collections.abc import Callable

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.config import settings


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault(
            "Permissions-Policy",
            "geolocation=(), microphone=(), camera=()",
        )
        # API responses should not be cached by shared proxies by default.
        response.headers.setdefault("Cache-Control", "no-store")
        if settings.is_production and not settings.debug:
            response.headers.setdefault(
                "Strict-Transport-Security",
                "max-age=31536000; includeSubDomains",
            )
        # Avoid leaking framework fingerprinting where safe.
        if "server" in response.headers:
            del response.headers["server"]
        return response


def add_security_headers(app: FastAPI) -> None:
    app.add_middleware(SecurityHeadersMiddleware)
