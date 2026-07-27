"""Structured logging for template/setup funnel analytics."""
from __future__ import annotations

import logging
from uuid import UUID

logger = logging.getLogger("template_analytics")


def log_setup_step(
    *,
    user_id: UUID,
    moment_id: UUID,
    moment_type_code: str,
    step: str,
    extra: dict | None = None,
) -> None:
    """Record a setup funnel step (draft, preview, commit, etc.)."""
    payload = {
        "event": "setup_step",
        "user_id": str(user_id),
        "moment_id": str(moment_id),
        "moment_type_code": moment_type_code,
        "step": step,
    }
    if extra:
        payload.update(extra)
    logger.info("setup_step %s", step, extra=payload)
