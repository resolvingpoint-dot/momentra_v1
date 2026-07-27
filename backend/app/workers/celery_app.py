"""Celery application (Redis broker + result backend).

No HTTP routes live here. The instance is discovered by the CLI via
``celery -A app.workers`` (see ``app/worker/__init__.py``).
"""
from __future__ import annotations

import logging

from celery import Celery
from celery.schedules import crontab

import app.core.base  # noqa: F401  # register the full ORM registry so cross-domain mappers resolve
from app.core.config import settings

logger = logging.getLogger(__name__)

celery_app = Celery("momentra")

celery_app.conf.update(
    broker_url=settings.effective_celery_broker or None,
    result_backend=settings.effective_celery_result_backend or None,
    # Serialization: JSON only (no pickle).
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    # Reliability: late acks + prefetch=1 so a dead worker's task is redelivered.
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    task_track_started=True,
    # Safety limits.
    task_soft_time_limit=300,
    task_time_limit=360,
    result_expires=3600,
    broker_connection_retry_on_startup=True,
    # Run inline when no broker is configured or explicitly requested (tests/local).
    task_always_eager=settings.celery_task_always_eager or not settings.effective_celery_broker,
    task_eager_propagates=True,
    # Dedicated queues per workload class.
    task_routes={
        "snapshots.*": {"queue": "refresh"},
        "memory.*": {"queue": "refresh"},
        "analytics.*": {"queue": "refresh"},
        "orchestration.*": {"queue": "refresh"},
        "projections.*": {"queue": "refresh"},
        "notifications.*": {"queue": "delivery"},
        "media.*": {"queue": "media"},
        "cleanup.*": {"queue": "maintenance"},
    },
    # Periodic schedule (celery beat).
    beat_schedule={
        "scan-orchestration-jobs-every-minute": {
            "task": "orchestration.scan_jobs",
            "schedule": 60.0,
        },
        "cleanup-nightly": {
            "task": "cleanup.run",
            "schedule": crontab(hour=3, minute=0),
        },
    },
)

# Import task modules so they register with the app. Kept at the bottom to avoid
# a circular import (task modules import ``celery_app`` from here).
from app.workers import tasks as _tasks  # noqa: E402,F401

# Mirror API lifespan registration: workers build personal pulse/moments/memory
# via TemplateProjectionRegistry, which is empty until handlers are registered.
from app.domains.personal.templates import (  # noqa: E402
    register_template_projection_handlers,
)
from app.domains.projections.handlers import register_projection_handlers  # noqa: E402

register_template_projection_handlers()
register_projection_handlers()

__all__ = ["celery_app"]
