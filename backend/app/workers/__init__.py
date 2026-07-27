"""Momentra background worker (Celery + Redis).

This package contains **no HTTP routes**. It exposes the Celery application and
idempotent background tasks (snapshot / memory / analytics refresh, orchestration
job processing, notification delivery, media processing and cleanup).

Run a worker:      celery -A app.workers worker --loglevel=info
Run the scheduler: celery -A app.workers beat --loglevel=info
"""
from __future__ import annotations

from app.workers.celery_app import celery_app

# Celery's ``-A app.workers`` entrypoint looks for an attribute named ``celery``
# or ``app``; expose both for convenience.
app = celery_app
celery = celery_app

__all__ = ["celery_app", "app", "celery"]
