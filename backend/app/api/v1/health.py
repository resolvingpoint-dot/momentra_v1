"""Health probes (liveness + readiness).

These endpoints are intentionally mounted at the application root (``/health``,
``/health/ready``) rather than under ``/api/v1`` so infrastructure probes and
the rate-limit exclusion list keep hitting stable paths. ``main.py`` includes
this router without a prefix.
"""
from __future__ import annotations

import hashlib

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.core.cache import get_redis
from app.core.config import settings
from app.core.database import ping_db

router = APIRouter(tags=["health"])


def _session_secret_fp() -> str:
    """Non-secret fingerprint so ops can confirm which key the API is using."""
    raw = (settings.effective_session_secret or "").encode("utf-8")
    if not raw:
        return "missing"
    return hashlib.sha256(raw).hexdigest()[:12]


async def _ping_celery_broker() -> bool:
    try:
        from app.workers.celery_app import celery_app

        conn = celery_app.connection()
        conn.ensure_connection(max_retries=1)
        conn.release()
        return True
    except Exception:
        return False


@router.get("/health", summary="Liveness probe")
async def health() -> dict:
    """Liveness probe — no external dependencies."""
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": settings.app_version,
        "session_secret_fp": _session_secret_fp(),
        "session_secret_len": len(settings.effective_session_secret or ""),
    }


@router.get("/health/ready", summary="Readiness probe")
async def readiness() -> JSONResponse:
    """Readiness probe — reports database, Redis, and Celery broker connectivity.

    Returns HTTP 503 when any dependency is down so orchestrators stop routing
    traffic (``/health`` alone stays 200 and does not check the DB).
    """
    db_ok = await ping_db()
    redis = await get_redis()
    redis_ok = redis is not None
    celery_ok = await _ping_celery_broker()
    all_ok = db_ok and redis_ok and celery_ok
    payload = {
        "status": "ok" if all_ok else "degraded",
        "database": "up" if db_ok else "down",
        "redis": "up" if redis_ok else "down",
        "celery": "up" if celery_ok else "down",
    }
    return JSONResponse(payload, status_code=200 if all_ok else 503)
