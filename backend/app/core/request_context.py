"""Per-request context for observability (request id, cache hit, routing hints)."""
from __future__ import annotations

from contextvars import ContextVar
from typing import Any, Literal

request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)
correlation_id_var: ContextVar[str | None] = ContextVar("correlation_id", default=None)
cache_hit_var: ContextVar[bool | None] = ContextVar("cache_hit", default=None)
user_id_var: ContextVar[str | None] = ContextVar("user_id", default=None)
context_var: ContextVar[str | None] = ContextVar("context", default=None)
template_var: ContextVar[str | None] = ContextVar("template", default=None)
duration_ms_var: ContextVar[float | None] = ContextVar("duration_ms", default=None)
projection_build_ms_var: ContextVar[float | None] = ContextVar(
    "projection_build_ms", default=None
)
build_coalesced_var: ContextVar[bool | None] = ContextVar("build_coalesced", default=None)
projection_version_var: ContextVar[int | None] = ContextVar(
    "projection_version", default=None
)

ProjectionState = Literal["fresh", "stale", "miss"]
ProjectionLock = Literal["acquired", "contended", "none"]
RefreshReason = Literal["mutation", "sse", "manual", "cold_miss", "stale_serve"]

projection_state_var: ContextVar[str | None] = ContextVar("projection_state", default=None)
projection_lock_var: ContextVar[str | None] = ContextVar("projection_lock", default=None)
refresh_enqueued_var: ContextVar[bool | None] = ContextVar(
    "refresh_enqueued", default=None
)
refresh_reason_var: ContextVar[str | None] = ContextVar("refresh_reason", default=None)
db_query_count_var: ContextVar[int] = ContextVar("db_query_count", default=0)
db_total_ms_var: ContextVar[float] = ContextVar("db_total_ms", default=0.0)
redis_ms_var: ContextVar[float] = ContextVar("redis_ms", default=0.0)
auth_ms_var: ContextVar[float | None] = ContextVar("auth_ms", default=None)
serialization_ms_var: ContextVar[float | None] = ContextVar(
    "serialization_ms", default=None
)

# BaseHTTPMiddleware runs handlers in a child task — ContextVar updates do not
# propagate back to the middleware. Mirror telemetry on request_id for headers.
_request_telemetry: dict[str, dict[str, Any]] = {}

_TELEMETRY_KEYS = (
    "cache_hit",
    "projection_version",
    "projection_build_ms",
    "build_coalesced",
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


def _touch_telemetry() -> dict[str, Any] | None:
    rid = request_id_var.get()
    if not rid:
        return None
    return _request_telemetry.setdefault(rid, {})


def begin_request_telemetry(request_id: str) -> None:
    _request_telemetry[request_id] = {k: None for k in _TELEMETRY_KEYS}
    _request_telemetry[request_id]["db_query_count"] = 0
    _request_telemetry[request_id]["db_total_ms"] = 0.0
    _request_telemetry[request_id]["redis_ms"] = 0.0


def pop_request_telemetry(request_id: str) -> dict[str, Any]:
    return _request_telemetry.pop(request_id, {})


def get_request_context() -> dict[str, Any]:
    """Snapshot current request context for structured logging."""
    ctx: dict[str, Any] = {}
    if (rid := request_id_var.get()) is not None:
        ctx["request_id"] = rid
    if (cid := correlation_id_var.get()) is not None:
        ctx["correlation_id"] = cid
    if (hit := cache_hit_var.get()) is not None:
        ctx["cache_hit"] = hit
    if (uid := user_id_var.get()) is not None:
        ctx["user_id"] = uid
    if (c := context_var.get()) is not None:
        ctx["context"] = c
    if (t := template_var.get()) is not None:
        ctx["template"] = t
    if (d := duration_ms_var.get()) is not None:
        ctx["duration_ms"] = round(d, 2)
    if (pb := projection_build_ms_var.get()) is not None:
        ctx["projection_build_ms"] = round(pb, 2)
    if (bc := build_coalesced_var.get()) is not None:
        ctx["build_coalesced"] = bc
    if (pv := projection_version_var.get()) is not None:
        ctx["projection_version"] = pv
    if (ps := projection_state_var.get()) is not None:
        ctx["projection_state"] = ps
    if (pl := projection_lock_var.get()) is not None:
        ctx["projection_lock"] = pl
    if (re := refresh_enqueued_var.get()) is not None:
        ctx["refresh_enqueued"] = re
    if (rr := refresh_reason_var.get()) is not None:
        ctx["refresh_reason"] = rr
    db_count = db_query_count_var.get()
    if db_count:
        ctx["db_query_count"] = db_count
    db_ms = db_total_ms_var.get()
    if db_ms:
        ctx["db_total_ms"] = round(db_ms, 2)
    redis_ms = redis_ms_var.get()
    if redis_ms:
        ctx["redis_ms"] = round(redis_ms, 2)
    if (am := auth_ms_var.get()) is not None:
        ctx["auth_ms"] = round(am, 2)
    if (sm := serialization_ms_var.get()) is not None:
        ctx["serialization_ms"] = round(sm, 2)
    return ctx


def set_cache_hit(hit: bool) -> None:
    cache_hit_var.set(hit)
    if (entry := _touch_telemetry()) is not None:
        entry["cache_hit"] = hit


def set_projection_build_ms(ms: float) -> None:
    projection_build_ms_var.set(ms)
    if (entry := _touch_telemetry()) is not None:
        entry["projection_build_ms"] = ms


def set_build_coalesced(coalesced: bool) -> None:
    build_coalesced_var.set(coalesced)
    if (entry := _touch_telemetry()) is not None:
        entry["build_coalesced"] = coalesced


def set_projection_version(version: int) -> None:
    projection_version_var.set(version)
    if (entry := _touch_telemetry()) is not None:
        entry["projection_version"] = version


def set_projection_state(state: ProjectionState) -> None:
    projection_state_var.set(state)
    if (entry := _touch_telemetry()) is not None:
        entry["projection_state"] = state


def set_projection_lock(lock: ProjectionLock) -> None:
    projection_lock_var.set(lock)
    if (entry := _touch_telemetry()) is not None:
        entry["projection_lock"] = lock


def set_refresh_enqueued(enqueued: bool, *, reason: str | None = None) -> None:
    refresh_enqueued_var.set(enqueued)
    if reason is not None:
        refresh_reason_var.set(reason)
    if (entry := _touch_telemetry()) is not None:
        entry["refresh_enqueued"] = enqueued
        if reason is not None:
            entry["refresh_reason"] = reason


def add_db_query(duration_ms: float) -> None:
    count = db_query_count_var.get() + 1
    total = db_total_ms_var.get() + duration_ms
    db_query_count_var.set(count)
    db_total_ms_var.set(total)
    if (entry := _touch_telemetry()) is not None:
        entry["db_query_count"] = count
        entry["db_total_ms"] = total


def add_redis_ms(duration_ms: float) -> None:
    total = redis_ms_var.get() + duration_ms
    redis_ms_var.set(total)
    if (entry := _touch_telemetry()) is not None:
        entry["redis_ms"] = total


def set_auth_ms(ms: float) -> None:
    auth_ms_var.set(ms)
    if (entry := _touch_telemetry()) is not None:
        entry["auth_ms"] = ms


def set_serialization_ms(ms: float) -> None:
    serialization_ms_var.set(ms)
    if (entry := _touch_telemetry()) is not None:
        entry["serialization_ms"] = ms
