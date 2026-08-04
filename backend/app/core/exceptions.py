from __future__ import annotations

import logging

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.errors import AppError

logger = logging.getLogger(__name__)


def _error_body(code: str, message: str, details: object | None = None) -> dict:
    body: dict = {"error": {"code": code, "message": message}}
    if details is not None:
        body["error"]["details"] = details
    return body


def _cors_headers(request: Request) -> dict[str, str] | None:
    """Ensure browser clients can read error bodies (ngrok + localhost)."""
    origin = request.headers.get("origin")
    if not origin:
        return None
    return {
        "Access-Control-Allow-Origin": origin,
        "Vary": "Origin",
    }


def register_exception_handlers(app: FastAPI) -> None:
    """Attach global exception handlers for consistent JSON error responses."""

    @app.exception_handler(AppError)
    async def _handle_app_error(request: Request, exc: AppError) -> JSONResponse:
        logger.info("AppError [%s]: %s", exc.code, exc.message)
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_body(exc.code, exc.message, getattr(exc, "details", None)),
            headers=_cors_headers(request),
        )

    @app.exception_handler(StarletteHTTPException)
    async def _handle_http_exception(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        headers = dict(getattr(exc, "headers", None) or {})
        extra = _cors_headers(request)
        if extra:
            headers.update(extra)
        detail = exc.detail
        if isinstance(detail, dict):
            code = str(detail.get("code") or detail.get("denial_reason") or "http_error")
            message = str(detail.get("message") or detail.get("detail") or "HTTP error")
            body = _error_body(code, message, detail)
        elif isinstance(detail, str):
            body = _error_body("http_error", detail)
        else:
            body = _error_body("http_error", "HTTP error", jsonable_encoder(detail))
        return JSONResponse(
            status_code=exc.status_code,
            content=body,
            headers=headers or None,
        )

    @app.exception_handler(RequestValidationError)
    async def _handle_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=_error_body(
                "validation_error",
                "Request validation failed",
                jsonable_encoder(exc.errors()),
            ),
            headers=_cors_headers(request),
        )

    @app.exception_handler(Exception)
    async def _handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        # Middleware / ASGI edge cases can surface HTTPException as a bare Exception.
        if isinstance(exc, StarletteHTTPException):
            return await _handle_http_exception(request, exc)
        logger.exception("Unhandled error on %s %s", request.method, request.url.path)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_error_body("internal_error", "Internal server error"),
            headers=_cors_headers(request),
        )
