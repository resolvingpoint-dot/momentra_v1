"""Shared SSE stream for Group moment projection invalidate push."""
from __future__ import annotations

import asyncio
import logging
from collections.abc import AsyncIterator
from uuid import UUID

from fastapi import Request
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import cache as core_cache
from app.domains.group.access import require_group_moment_access
from app.domains.group.group_moment_events import invalidate_channel

logger = logging.getLogger(__name__)

_SSE_HEARTBEAT_S = 15.0


async def group_moment_stream_response(
    *,
    moment_id: UUID,
    request: Request,
    user_id: UUID,
    db: AsyncSession,
) -> StreamingResponse:
    """SSE: projection invalidate push for any Group moment template.

    Auth via Bearer. If Redis is unavailable, keep heartbeat-only so clients
    can fall back to pull-to-refresh.
    """
    await require_group_moment_access(db, user_id, moment_id)
    channel = invalidate_channel(moment_id)

    async def event_gen() -> AsyncIterator[str]:
        redis = await core_cache.get_redis()
        if redis is None:
            logger.info(
                "group stream heartbeat-only (no Redis) moment=%s user=%s",
                moment_id,
                user_id,
            )
            try:
                while True:
                    if await request.is_disconnected():
                        break
                    yield ": ping\n\n"
                    await asyncio.sleep(_SSE_HEARTBEAT_S)
            except asyncio.CancelledError:
                pass
            return

        pubsub = redis.pubsub()
        try:
            await pubsub.subscribe(channel)
            while True:
                if await request.is_disconnected():
                    break
                message = await pubsub.get_message(
                    ignore_subscribe_messages=True,
                    timeout=_SSE_HEARTBEAT_S,
                )
                if message is None:
                    yield ": ping\n\n"
                    continue
                if message.get("type") != "message":
                    continue
                data = message.get("data")
                if data is None:
                    continue
                if isinstance(data, bytes):
                    data = data.decode("utf-8", errors="replace")
                yield f"event: invalidate\ndata: {data}\n\n"
        except asyncio.CancelledError:
            pass
        except Exception:
            logger.warning(
                "group stream error moment=%s user=%s",
                moment_id,
                user_id,
                exc_info=True,
            )
        finally:
            try:
                await pubsub.unsubscribe(channel)
                close = getattr(pubsub, "aclose", None) or getattr(pubsub, "close", None)
                if close is not None:
                    result = close()
                    if asyncio.iscoroutine(result):
                        await result
            except Exception:
                pass

    return StreamingResponse(
        event_gen(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
