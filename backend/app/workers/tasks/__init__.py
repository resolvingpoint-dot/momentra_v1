"""Task registration.

Importing this package imports every task module so the tasks bind to the Celery
app. ``celery_app`` imports this at the bottom of its module.
"""
from __future__ import annotations

from app.workers.tasks import (  # noqa: F401
    analytics,
    business_projections,
    cleanup,
    media,
    memory,
    notifications,
    orchestration,
    projections,
    snapshots,
)

__all__ = [
    "analytics",
    "business_projections",
    "cleanup",
    "media",
    "memory",
    "notifications",
    "orchestration",
    "projections",
    "snapshots",
]
