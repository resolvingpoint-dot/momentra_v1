"""Post-commit side effects: log, metric, and light retry without blocking the HTTP response."""
from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable
from typing import Any

from app.domains.projections.projection_metrics import (
    record_deferred_failure,
    record_deferred_retry,
    record_deferred_success,
)

logger = logging.getLogger(__name__)

CoroFactory = Callable[[], Awaitable[Any]]


async def run_deferred_side_effect(
    name: str,
    factory: CoroFactory,
    *,
    retries: int = 1,
    retry_delay_sec: float = 0.05,
    context: dict[str, Any] | None = None,
) -> bool:
    """Run a post-commit job. Returns True on success. Never raises to the caller."""
    ctx = context or {}
    attempts = max(0, retries) + 1
    for attempt in range(attempts):
        try:
            await factory()
            record_deferred_success(name)
            logger.info(
                "deferred_side_effect.ok name=%s attempt=%s context=%s",
                name,
                attempt + 1,
                ctx,
            )
            return True
        except Exception:
            record_deferred_failure(name)
            logger.exception(
                "deferred_side_effect.fail name=%s attempt=%s/%s context=%s",
                name,
                attempt + 1,
                attempts,
                ctx,
            )
            if attempt + 1 < attempts:
                record_deferred_retry(name)
                await asyncio.sleep(retry_delay_sec * (attempt + 1))
    return False


def schedule_deferred_side_effect(
    name: str,
    factory: CoroFactory,
    *,
    retries: int = 1,
    context: dict[str, Any] | None = None,
) -> asyncio.Task:
    """Fire-and-forget wrapper used on the mutation critical path after commit."""

    async def _runner() -> None:
        await run_deferred_side_effect(name, factory, retries=retries, context=context)

    return asyncio.create_task(_runner())
