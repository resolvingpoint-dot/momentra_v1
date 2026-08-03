"""HTTP observability middleware — request IDs, timing, response headers."""
from __future__ import annotations

import json
import logging
import time
from typing import Callable

from starlette.requests import Request
from starlette.responses import Response

from app.core.correlation import resolve_correlation_id, resolve_request_id
from app.core.request_context import (
    begin_request_telemetry,
    build_coalesced_var,
    cache_hit_var,
    context_var,
    correlation_id_var,
    pop_request_telemetry,
    projection_build_ms_var,
    projection_version_var,
    request_id_var,
    template_var,
    user_id_var,
)

logger = logging.getLogger("momentra.request")


def _extract_routing_hints(request: Request) -> None:
    """Populate context/template from query params when present."""
    moment_type = request.query_params.get("moment_type_code")
    if moment_type:
        template_var.set(moment_type.upper())
    ctx = request.query_params.get("context")
    if ctx:
        context_var.set(ctx.upper())
    path = request.url.path
    if "/personal/" in path:
        context_var.set(context_var.get() or "MY_MONEY")
    elif "/group/" in path:
        context_var.set(context_var.get() or "GROUP")
    elif "/business/" in path:
        context_var.set(context_var.get() or "BUSINESS")


async def observability_middleware(request: Request, call_next: Callable) -> Response:
    """Function middleware so ContextVar telemetry survives into route handlers."""
    rid = resolve_request_id(request.headers.get("X-Request-ID"))
    cid = resolve_correlation_id(request.headers.get("X-Correlation-ID"), fallback=rid)
    request.state.request_id = rid
    request.state.correlation_id = cid
    request_id_var.set(rid)
    correlation_id_var.set(cid)
    begin_request_telemetry(rid)
    cache_hit_var.set(False)
    user_id_var.set(None)
    context_var.set(None)
    template_var.set(None)

    _extract_routing_hints(request)
    start = time.perf_counter()

    try:
        response = await call_next(request)
    except Exception:
        duration_ms = (time.perf_counter() - start) * 1000
        logger.error(
            json.dumps(
                {
                    "request_id": rid,
                    "correlation_id": cid,
                    "method": request.method,
                    "path": request.url.path,
                    "duration_ms": round(duration_ms, 2),
                    "cache_hit": cache_hit_var.get(),
                    "user_id": user_id_var.get(),
                    "context": context_var.get(),
                    "template": template_var.get(),
                    "outcome": "error",
                }
            )
        )
        from app.core.metrics import record_request

        record_request(request.method, request.url.path, 500, duration_ms)
        raise

    duration_ms = (time.perf_counter() - start) * 1000
    obs = pop_request_telemetry(rid)
    cache_hit = obs.get("cache_hit")
    if cache_hit is None:
        cache_hit = cache_hit_var.get()
    if obs.get("projection_build_ms") is not None:
        projection_build_ms_var.set(obs["projection_build_ms"])
    if obs.get("build_coalesced") is not None:
        build_coalesced_var.set(obs["build_coalesced"])
    if obs.get("projection_version") is not None:
        projection_version_var.set(obs["projection_version"])
    user_id = (
        obs.get("user_id")
        or user_id_var.get()
        or getattr(request.state, "user_id", None)
        or getattr(request.state, "user_uid", None)
    )
    log_entry = {
        "request_id": rid,
        "correlation_id": cid,
        "method": request.method,
        "path": request.url.path,
        "status": response.status_code,
        "duration_ms": round(duration_ms, 2),
        "cache_hit": cache_hit,
        "user_id": user_id,
        "context": context_var.get(),
        "template": template_var.get(),
        "outcome": "ok" if response.status_code < 400 else "client_error",
    }
    if (pb := projection_build_ms_var.get()) is not None:
        log_entry["projection_build_ms"] = round(pb, 2)
    if (bc := build_coalesced_var.get()) is not None:
        log_entry["build_coalesced"] = bc
    if (pv := projection_version_var.get()) is not None:
        log_entry["projection_version"] = pv
    if response.status_code >= 500:
        log_entry["outcome"] = "server_error"
        logger.error(json.dumps(log_entry))
    elif duration_ms > 1000:
        logger.warning(json.dumps(log_entry))
    else:
        logger.info(json.dumps(log_entry))

    from app.core.metrics import record_request

    record_request(request.method, request.url.path, response.status_code, duration_ms)

    response.headers["X-Request-ID"] = rid
    response.headers["X-Correlation-ID"] = cid
    response.headers["X-Duration-Ms"] = str(round(duration_ms, 2))
    if cache_hit is not None:
        response.headers["X-Cache-Hit"] = "true" if cache_hit else "false"

    timing_parts = [f"total;dur={round(duration_ms, 2)}"]
    if cache_hit is not None:
        timing_parts.append(f'cache;desc="{"hit" if cache_hit else "miss"}"')
    if (pb := projection_build_ms_var.get()) is not None:
        timing_parts.append(f"projection;dur={round(pb, 2)}")
    response.headers["Server-Timing"] = ", ".join(timing_parts)

    if (pv := projection_version_var.get()) is not None:
        response.headers["X-Projection-Version"] = str(pv)
        etag = f'"proj-{pv}"'
        response.headers["ETag"] = etag
        inm = request.headers.get("if-none-match")
        if (
            inm is not None
            and response.status_code == 200
            and request.method in ("GET", "HEAD")
            and inm.strip() == etag
        ):
            return Response(
                status_code=304,
                headers={
                    "ETag": etag,
                    "X-Request-ID": rid,
                    "X-Correlation-ID": cid,
                    "X-Duration-Ms": str(round(duration_ms, 2)),
                    "X-Projection-Version": str(pv),
                    "X-Cache-Hit": "true" if cache_hit else "false",
                    "Server-Timing": response.headers["Server-Timing"],
                },
            )
    return response
