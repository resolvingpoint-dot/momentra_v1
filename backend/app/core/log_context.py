"""Logging filter + helpers so structured logs inherit request/correlation ids."""
from __future__ import annotations

import logging

from app.core.request_context import correlation_id_var, request_id_var


class RequestContextLogFilter(logging.Filter):
    """Attach ``request_id`` / ``correlation_id`` from ContextVars onto log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "request_id") or getattr(record, "request_id") is None:
            rid = request_id_var.get()
            if rid:
                record.request_id = rid  # type: ignore[attr-defined]
        if not hasattr(record, "correlation_id") or getattr(record, "correlation_id") is None:
            cid = correlation_id_var.get()
            if cid:
                record.correlation_id = cid  # type: ignore[attr-defined]
        return True


def install_request_context_log_filter() -> None:
    filt = RequestContextLogFilter()
    root = logging.getLogger()
    for handler in root.handlers:
        handler.addFilter(filt)
    # Also attach to uvicorn loggers when present.
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access", "momentra.request"):
        for handler in logging.getLogger(name).handlers:
            handler.addFilter(filt)
