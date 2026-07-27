"""Shared task options.

``RETRY_OPTS`` centralises the retry policy so every task gets automatic,
exponentially-backed-off retries with jitter. ``acks_late`` +
``reject_on_worker_lost`` ensure a job is re-queued if a worker dies mid-task
(safe because all tasks are idempotent).
"""
from __future__ import annotations

from app.core.config import settings

RETRY_OPTS: dict = {
    "autoretry_for": (Exception,),
    "max_retries": settings.celery_max_retries,
    "retry_backoff": True,
    "retry_backoff_max": settings.celery_retry_backoff_max,
    "retry_jitter": True,
    "acks_late": True,
    "reject_on_worker_lost": True,
    "track_started": True,
}
