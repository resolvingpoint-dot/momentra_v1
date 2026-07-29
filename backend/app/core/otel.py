"""Optional OpenTelemetry FastAPI instrumentation (off by default)."""
from __future__ import annotations

import logging

from fastapi import FastAPI

from app.core.config import settings

logger = logging.getLogger(__name__)


def maybe_instrument_otel(app: FastAPI) -> None:
    """Enable OTel FastAPI instrumentation when ``ENABLE_OTEL=true``.

    No collector is required in local compose; exporters follow env defaults.
    Missing packages are ignored so production images without OTel deps still boot.
    """
    if not settings.enable_otel:
        return
    try:
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    except ImportError:
        logger.warning(
            "ENABLE_OTEL=true but opentelemetry-instrumentation-fastapi is not installed"
        )
        return
    try:
        FastAPIInstrumentor.instrument_app(app)
        logger.info("OpenTelemetry FastAPI instrumentation enabled")
    except Exception:  # noqa: BLE001
        logger.exception("Failed to enable OpenTelemetry instrumentation")
