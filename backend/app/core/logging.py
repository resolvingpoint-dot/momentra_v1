from __future__ import annotations

import logging
from logging.config import dictConfig

_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_JSON_FORMAT = '{"timestamp":"%(asctime)s","level":"%(levelname)s","logger":"%(name)s","message":%(message)s}'
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

_configured = False


def configure_logging(debug: bool = False) -> None:
    """Configure application-wide logging once.

    Idempotent: safe to call multiple times (e.g. app import + lifespan).
    """
    global _configured
    if _configured:
        return

    level = "DEBUG" if debug else "INFO"

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": _LOG_FORMAT,
                    "datefmt": _DATE_FORMAT,
                },
                "json": {
                    "()": "app.core.logging.JsonLogFormatter",
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "json" if not debug else "default",
                    "level": level,
                },
            },
            "root": {
                "handlers": ["console"],
                "level": level,
            },
            "loggers": {
                "uvicorn": {"level": level, "handlers": ["console"], "propagate": False},
                "uvicorn.error": {"level": level, "handlers": ["console"], "propagate": False},
                "uvicorn.access": {"level": level, "handlers": ["console"], "propagate": False},
                # Keep SQLAlchemy engine chatter down unless explicitly debugging.
                "sqlalchemy.engine": {"level": "WARNING", "propagate": True},
            },
        }
    )

    _configured = True
    from app.core.log_context import install_request_context_log_filter

    install_request_context_log_filter()
    logging.getLogger(__name__).debug("Logging configured (level=%s)", level)


class JsonLogFormatter(logging.Formatter):
    """Emit structured JSON log lines for production observability."""

    def format(self, record: logging.LogRecord) -> str:
        import json

        payload = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for key in (
            "request_id",
            "correlation_id",
            "duration_ms",
            "cache_hit",
            "user_id",
            "context",
            "template",
        ):
            if hasattr(record, key):
                payload[key] = getattr(record, key)
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)
