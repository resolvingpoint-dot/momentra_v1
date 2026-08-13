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
    auth_ms_var,
    begin_request_telemetry,
    build_coalesced_var,
    cache_hit_var,
    context_var,
    correlation_id_var,
    db_query_count_var,
    db_total_ms_var,
    pop_request_telemetry,
    projection_build_ms_var,
    projection_lock_var,
    projection_state_var,
    projection_version_var,
    redis_ms_var,
    refresh_enqueued_var,
    refresh_reason_var,
    request_id_var,
    serialization_ms_var,
    template_var,
    user_id_var,
)

logger = logging.getLogger("momentra.request")

_OBS_MIRROR_KEYS = (
    "cache_hit",
    "projection_build_ms",
    "build_coalesced",
    "projection_version",
    "projection_state",
    "projection_lock",
    "refresh_enqueued",
    "refresh_reason",
    "db_query_count",
    "db_total_ms",
    "redis_ms",
    "auth_ms",
    "serialization_ms",
)


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


def _mirror_obs(obs: dict) -> None:
    if obs.get("projection_build_ms") is not None:
        projection_build_ms_var.set(obs["projection_build_ms"])
    if obs.get("build_coalesced") is not None:
        build_coalesced_var.set(obs["build_coalesced"])
    if obs.get("projection_version") is not None:
        projection_version_var.set(obs["projection_version"])
    if obs.get("projection_state") is not None:
        projection_state_var.set(obs["projection_state"])
    if obs.get("projection_lock") is not None:
        projection_lock_var.set(obs["projection_lock"])
    if obs.get("refresh_enqueued") is not None:
        refresh_enqueued_var.set(obs["refresh_enqueued"])
    if obs.get("refresh_reason") is not None:
        refresh_reason_var.set(obs["refresh_reason"])
    if obs.get("db_query_count") is not None:
        db_query_count_var.set(int(obs["db_query_count"] or 0))
    if obs.get("db_total_ms") is not None:
        db_total_ms_var.set(float(obs["db_total_ms"] or 0))
    if obs.get("redis_ms") is not None:
        redis_ms_var.set(float(obs["redis_ms"] or 0))
    if obs.get("auth_ms") is not None:
        auth_ms_var.set(obs["auth_ms"])
    if obs.get("serialization_ms") is not None:
        serialization_ms_var.set(obs["serialization_ms"])


def _append_optional_log_fields(log_entry: dict, obs: dict) -> None:
    if (ps := obs.get("projection_state") or projection_state_var.get()) is not None:
        log_entry["projection_state"] = ps
    if (pl := obs.get("projection_lock") or projection_lock_var.get()) is not None:
        log_entry["projection_lock"] = pl
    re = obs.get("refresh_enqueued")
    if re is None:
        re = refresh_enqueued_var.get()
    if re is not None:
        log_entry["refresh_enqueued"] = re
    if (rr := obs.get("refresh_reason") or refresh_reason_var.get()) is not None:
        log_entry["refresh_reason"] = rr
    db_count = obs.get("db_query_count")
    if db_count is None:
        db_count = db_query_count_var.get()
    if db_count:
        log_entry["db_query_count"] = int(db_count)
    db_ms = obs.get("db_total_ms")
    if db_ms is None:
        db_ms = db_total_ms_var.get()
    if db_ms:
        log_entry["db_total_ms"] = round(float(db_ms), 2)
    redis_ms = obs.get("redis_ms")
    if redis_ms is None:
        redis_ms = redis_ms_var.get()
    if redis_ms:
        log_entry["redis_ms"] = round(float(redis_ms), 2)
    if (pb := obs.get("projection_build_ms") or projection_build_ms_var.get()) is not None:
        log_entry["projection_build_ms"] = round(float(pb), 2)
    if (am := obs.get("auth_ms") or auth_ms_var.get()) is not None:
        log_entry["auth_ms"] = round(float(am), 2)
    if (sm := obs.get("serialization_ms") or serialization_ms_var.get()) is not None:
        log_entry["serialization_ms"] = round(float(sm), 2)
    if (bc := obs.get("build_coalesced") or build_coalesced_var.get()) is not None:
        log_entry["build_coalesced"] = bc
    if (pv := obs.get("projection_version") or projection_version_var.get()) is not None:
        log_entry["projection_version"] = pv


def _build_server_timing(duration_ms: float, cache_hit: bool | None, obs: dict) -> str:
    timing_parts = [f"total;dur={round(duration_ms, 2)}"]
    if cache_hit is not None:
        timing_parts.append(f'cache;desc="{"hit" if cache_hit else "miss"}"')
    if (ps := obs.get("projection_state") or projection_state_var.get()) is not None:
        timing_parts.append(f'proj_state;desc="{ps}"')
    if (pl := obs.get("projection_lock") or projection_lock_var.get()) is not None:
        timing_parts.append(f'proj_lock;desc="{pl}"')
    if (pb := obs.get("projection_build_ms") or projection_build_ms_var.get()) is not None:
        timing_parts.append(f"projection;dur={round(float(pb), 2)}")
    db_ms = obs.get("db_total_ms")
    if db_ms is None:
        db_ms = db_total_ms_var.get()
    if db_ms:
        timing_parts.append(f"db;dur={round(float(db_ms), 2)}")
    redis_ms = obs.get("redis_ms")
    if redis_ms is None:
        redis_ms = redis_ms_var.get()
    if redis_ms:
        timing_parts.append(f"redis;dur={round(float(redis_ms), 2)}")
    if (am := obs.get("auth_ms") or auth_ms_var.get()) is not None:
        timing_parts.append(f"auth;dur={round(float(am), 2)}")
    return ", ".join(timing_parts)


async def observability_middleware(request: Request, call_next: Callable) -> Response:
    """Function middleware so ContextVar telemetry survives into route handlers."""
    rid = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    cid = request.headers.get("X-Correlation-ID") or rid
    request.state.request_id = rid
    request.state.correlation_id = cid
    request_id_var.set(rid)
    correlation_id_var.set(cid)
    begin_request_telemetry(rid)
    cache_hit_var.set(False)
    user_id_var.set(None)
    context_var.set(None)
    template_var.set(None)
    projection_state_var.set(None)
    projection_lock_var.set(None)
    refresh_enqueued_var.set(None)
    refresh_reason_var.set(None)
    db_query_count_var.set(0)
    db_total_ms_var.set(0.0)
    redis_ms_var.set(0.0)
    auth_ms_var.set(None)
    serialization_ms_var.set(None)
    projection_build_ms_var.set(None)
    build_coalesced_var.set(None)
    projection_version_var.set(None)

    _extract_routing_hints(request)
    if request.query_params.get("force_refresh", "").lower() in {"1", "true", "yes"}:
        logger.warning(
            json.dumps(
                {
                    "event": "force_refresh_query",
                    "request_id": rid,
                    "path": request.url.path,
                    "note": "clients should soft-revalidate; server will SWR-serve stale",
                }
            )
        )

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
                    "total_ms": round(duration_ms, 2),
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
    _mirror_obs(obs)

    log_entry = {
        "request_id": rid,
        "correlation_id": cid,
        "method": request.method,
        "path": request.url.path,
        "status": response.status_code,
        "duration_ms": round(duration_ms, 2),
        "total_ms": round(duration_ms, 2),
        "cache_hit": cache_hit,
        "user_id": user_id_var.get(),
        "context": context_var.get(),
        "template": template_var.get(),
        "outcome": "ok" if response.status_code < 400 else "client_error",
    }
    _append_optional_log_fields(log_entry, obs)
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
    if (ps := obs.get("projection_state") or projection_state_var.get()) is not None:
        response.headers["X-Projection-State"] = str(ps)

    server_timing = _build_server_timing(duration_ms, cache_hit, obs)
    response.headers["Server-Timing"] = server_timing

    if (pv := obs.get("projection_version") or projection_version_var.get()) is not None:
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
                    "X-Projection-State": response.headers.get("X-Projection-State", ""),
                    "Server-Timing": server_timing,
                },
            )
    return response
