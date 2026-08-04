"""SQLAlchemy query timing → request-scoped counters (and GraphQL telemetry)."""
from __future__ import annotations

import logging
import time
from typing import Any

from sqlalchemy import event
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)

_installed = False


def install_sql_timing(sync_engine: Engine | None = None) -> None:
    """Install before/after_cursor_execute listeners once.

    For async engines, pass ``engine.sync_engine``.
    """
    global _installed
    if _installed:
        return
    if sync_engine is None:
        try:
            from app.core.database import engine as async_engine

            if async_engine is None:
                return
            sync_engine = async_engine.sync_engine
        except Exception:
            logger.debug("SQL timing: engine unavailable", exc_info=True)
            return

    @event.listens_for(sync_engine, "before_cursor_execute")
    def _before_cursor_execute(
        conn: Any,
        cursor: Any,
        statement: Any,
        parameters: Any,
        context: Any,
        executemany: Any,
    ) -> None:
        conn.info["_momentra_sql_start"] = time.perf_counter()

    @event.listens_for(sync_engine, "after_cursor_execute")
    def _after_cursor_execute(
        conn: Any,
        cursor: Any,
        statement: Any,
        parameters: Any,
        context: Any,
        executemany: Any,
    ) -> None:
        start = conn.info.pop("_momentra_sql_start", None)
        if start is None:
            return
        duration_ms = (time.perf_counter() - start) * 1000
        try:
            from app.core.request_context import record_sql_timing

            record_sql_timing(duration_ms)
        except Exception:
            pass

    _installed = True
    logger.info("SQL timing listeners installed")
