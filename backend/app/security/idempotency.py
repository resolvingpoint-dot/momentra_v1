"""Redis-backed Idempotency-Key helper for opt-in mutating REST routes."""
from __future__ import annotations

import hashlib
import json
import logging
from typing import Any
from uuid import UUID

from app.core.cache import get_cached, set_cached
from app.core.errors import ConflictError

logger = logging.getLogger(__name__)

DEFAULT_TTL_SECONDS = 24 * 3600


class IdempotencyStore:
    """Store/replay JSON responses for ``Idempotency-Key`` on a given route."""

    def __init__(self, *, ttl_seconds: int = DEFAULT_TTL_SECONDS) -> None:
        self.ttl_seconds = ttl_seconds

    def _key(self, user_id: UUID, route: str, idempotency_key: str) -> str:
        digest = hashlib.sha256(
            f"{user_id}:{route}:{idempotency_key}".encode()
        ).hexdigest()[:40]
        return f"idempotency:{digest}"

    async def get_cached_response(
        self, user_id: UUID, route: str, idempotency_key: str
    ) -> dict[str, Any] | None:
        if not idempotency_key or not idempotency_key.strip():
            return None
        raw = await get_cached(self._key(user_id, route, idempotency_key.strip()))
        if isinstance(raw, dict):
            return raw
        return None

    async def put_response(
        self,
        user_id: UUID,
        route: str,
        idempotency_key: str,
        payload: dict[str, Any],
    ) -> None:
        if not idempotency_key or not idempotency_key.strip():
            return
        try:
            # Ensure JSON-serializable for Redis path inside set_cached.
            json.dumps(payload, default=str)
            await set_cached(
                self._key(user_id, route, idempotency_key.strip()),
                payload,
                ttl=self.ttl_seconds,
            )
        except Exception:  # noqa: BLE001
            logger.debug("idempotency put failed", exc_info=True)

    async def begin_or_replay(
        self,
        user_id: UUID,
        route: str,
        idempotency_key: str | None,
    ) -> dict[str, Any] | None:
        """Return a cached payload to replay, or None when the caller should proceed.

        Raises ConflictError when a marker indicates an in-flight duplicate.
        """
        if not idempotency_key or not idempotency_key.strip():
            return None
        existing = await self.get_cached_response(user_id, route, idempotency_key)
        if existing is None:
            return None
        if existing.get("_status") == "in_flight":
            raise ConflictError(
                "A request with this Idempotency-Key is already in progress",
                code="idempotency_in_flight",
            )
        return existing
