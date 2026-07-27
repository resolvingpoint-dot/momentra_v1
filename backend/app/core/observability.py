"""HTTP observability middleware — request IDs, timing, response headers."""
from __future__ import annotations

import json
import logging
import time
import uuid
from typing import Callable

from starlette.requests import Request
from starlette.responses import Response

from app.core.request_context import (
    begin_request_telemetry,
    build_coalesced_var,
    cache_hit_var,
    context_var,
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
    rid = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    request.state.request_id = rid
    request_id_var.set(rid)
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
    log_entry = {
        "request_id": rid,
        "method": request.method,
        "path": request.url.path,
        "status": response.status_code,
        "duration_ms": round(duration_ms, 2),
        "cache_hit": cache_hit,
        "user_id": user_id_var.get(),
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

    response.headers["X-Request-ID"] = rid
    response.headers["X-Duration-Ms"] = str(round(duration_ms, 2))
    if cache_hit is not None:
        response.headers["X-Cache-Hit"] = "true" if cache_hit else "false"
    if (pv := projection_version_var.get()) is not None:
        response.headers["X-Projection-Version"] = str(pv)
    return response
