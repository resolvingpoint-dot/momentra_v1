"""Celery task instrumentation: correlation propagation + duration metrics."""
from __future__ import annotations

import json
import logging
import time
from typing import Any

from celery import signals

from app.core.request_context import correlation_id_var, request_id_var

logger = logging.getLogger("momentra.celery")

_installed = False


def _headers(sender: Any, kwargs: dict[str, Any]) -> dict[str, Any]:
    req = kwargs.get("request")
    if req is not None and getattr(req, "headers", None):
        return dict(req.headers or {})
    return {}


@signals.task_prerun.connect
def _on_task_prerun(
    sender: Any = None,
    task_id: str | None = None,
    task: Any = None,
    args: Any = None,
    kwargs: Any = None,
    **extra: Any,
) -> None:
    headers = _headers(sender, extra)
    published_at = headers.get("published_at")
    queue_delay_ms: float | None = None
    if isinstance(published_at, (int, float)):
        queue_delay_ms = max(0.0, (time.time() - float(published_at)) * 1000)

    cid = headers.get("correlation_id")
    rid = headers.get("source_request_id")
    if cid:
        correlation_id_var.set(str(cid))
    if rid:
        request_id_var.set(str(rid))

    if task is not None:
        task.request.momentra_started_at = time.perf_counter()
        task.request.momentra_queue_delay_ms = queue_delay_ms

    logger.info(
        json.dumps(
            {
                "event": "celery_task_started",
                "task_name": getattr(sender, "name", None) or getattr(task, "name", None),
                "task_id": task_id,
                "correlation_id": cid,
                "source_request_id": rid,
                "source_event_type": headers.get("source_event_type"),
                "queue_delay_ms": round(queue_delay_ms, 2) if queue_delay_ms is not None else None,
            }
        )
    )


@signals.task_postrun.connect
def _on_task_postrun(
    sender: Any = None,
    task_id: str | None = None,
    task: Any = None,
    args: Any = None,
    kwargs: Any = None,
    retval: Any = None,
    state: str | None = None,
    **extra: Any,
) -> None:
    started = getattr(getattr(task, "request", None), "momentra_started_at", None)
    queue_delay_ms = getattr(getattr(task, "request", None), "momentra_queue_delay_ms", None)
    duration_ms = None
    if started is not None:
        duration_ms = (time.perf_counter() - started) * 1000

    task_name = (getattr(sender, "name", None) or "unknown")[:128]
    retries = getattr(getattr(task, "request", None), "retries", 0) or 0

    try:
        from app.core.metrics import record_celery_task

        record_celery_task(
            task_name=task_name,
            state=state or "UNKNOWN",
            duration_ms=duration_ms or 0.0,
            queue_delay_ms=queue_delay_ms,
            retries=int(retries),
        )
    except Exception:
        pass

    logger.info(
        json.dumps(
            {
                "event": "celery_task_finished",
                "task_name": task_name,
                "task_id": task_id,
                "state": state,
                "duration_ms": round(duration_ms, 2) if duration_ms is not None else None,
                "queue_delay_ms": round(queue_delay_ms, 2) if queue_delay_ms is not None else None,
                "retries": retries,
                "correlation_id": correlation_id_var.get(),
                "source_request_id": request_id_var.get(),
            }
        )
    )


def install_celery_instrumentation() -> None:
    global _installed
    if _installed:
        return
    _installed = True
    logger.info("Celery instrumentation signals connected")
