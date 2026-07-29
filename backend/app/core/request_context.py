"""Per-request context for observability (request id, cache hit, routing hints)."""
from __future__ import annotations

from contextvars import ContextVar
from typing import Any

request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)
correlation_id_var: ContextVar[str | None] = ContextVar("correlation_id", default=None)
cache_hit_var: ContextVar[bool | None] = ContextVar("cache_hit", default=None)
user_id_var: ContextVar[str | None] = ContextVar("user_id", default=None)
context_var: ContextVar[str | None] = ContextVar("context", default=None)
template_var: ContextVar[str | None] = ContextVar("template", default=None)
duration_ms_var: ContextVar[float | None] = ContextVar("duration_ms", default=None)
projection_build_ms_var: ContextVar[float | None] = ContextVar("projection_build_ms", default=None)
build_coalesced_var: ContextVar[bool | None] = ContextVar("build_coalesced", default=None)
projection_version_var: ContextVar[int | None] = ContextVar("projection_version", default=None)

# BaseHTTPMiddleware runs handlers in a child task — ContextVar updates do not
# propagate back to the middleware. Mirror telemetry on request_id for headers.
_request_telemetry: dict[str, dict[str, Any]] = {}


def _touch_telemetry() -> dict[str, Any] | None:
    rid = request_id_var.get()
    if not rid:
        return None
    return _request_telemetry.setdefault(rid, {})


def begin_request_telemetry(request_id: str) -> None:
    _request_telemetry[request_id] = {
        "cache_hit": None,
        "projection_version": None,
        "projection_build_ms": None,
        "build_coalesced": None,
    }


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
