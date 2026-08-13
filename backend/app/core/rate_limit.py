from __future__ import annotations

import asyncio
import logging
import time
from collections import defaultdict
from typing import Callable

from fastapi import FastAPI, HTTPException, Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.config import settings

logger = logging.getLogger(__name__)

_in_memory: dict[str, list[float]] = defaultdict(list)
_lock = asyncio.Lock()

_redis_client = None
_redis_attempted = False

_RL_KEY_STATE = "rate_limit_key"
_RL_MEMBER_STATE = "rate_limit_member"
_RL_TS_STATE = "rate_limit_ts"


async def _get_redis():
    global _redis_client, _redis_attempted
    if _redis_client is not None:
        return _redis_client
    if _redis_attempted:
        return None
    _redis_attempted = True
    try:
        import redis.asyncio as aioredis

        if settings.redis_url:
            _redis_client = aioredis.from_url(
                settings.redis_url, decode_responses=True, socket_connect_timeout=2
            )
            await _redis_client.ping()
            return _redis_client
    except Exception:
        logger.warning("Redis unavailable for rate limiting, using in-memory")
    return None


def peek_bearer_uid(request: Request) -> str | None:
    """Best-effort identity for rate-limit keys before FastAPI auth deps run.

    Decodes Momentra session JWTs only. Firebase ID tokens are not peeked here
    (exchange is body-based; subsequent traffic uses session access tokens).
    """
    existing = getattr(request.state, "user_uid", None)
    if existing:
        return str(existing)
    auth = request.headers.get("authorization") or ""
    if not auth.lower().startswith("bearer "):
        return None
    token = auth[7:].strip()
    if not token:
        return None
    try:
        from app.core.security import decode_session_token

        decoded = decode_session_token(token)
    except Exception:
        return None
    if decoded.get("type") == "refresh":
        return None
    sub = decoded.get("sub")
    if not sub:
        return None
    request.state.user_uid = sub
    return str(sub)


def _rate_limit_key(request: Request) -> tuple[str, bool]:
    """Return (key, is_authenticated_key)."""
    uid = peek_bearer_uid(request) or getattr(request.state, "user_uid", None)
    if uid:
        return f"rl:{uid}", True
    forwarded = request.headers.get("x-forwarded-for", "")
    ip = forwarded.split(",")[0].strip() if forwarded else (
        request.client.host if request.client else "unknown"
    )
    return f"rl:{ip}:{request.url.path}", False


async def check_rate_limit(
    request: Request,
    max_requests: int = 60,
    window_seconds: int = 60,
) -> bool:
    key, _ = _rate_limit_key(request)
    now = time.time()
    # Unique member so concurrent requests can be refunded independently.
    member = f"{now:.6f}:{id(request)}"

    redis = await _get_redis()
    if redis:
        try:
            pipe = redis.pipeline()
            pipe.zremrangebyscore(key, 0, now - window_seconds)
            pipe.zcard(key)
            pipe.zadd(key, {member: now})
            pipe.expire(key, window_seconds)
            _, count, _, _ = await pipe.execute()
            setattr(request.state, _RL_KEY_STATE, key)
            setattr(request.state, _RL_MEMBER_STATE, member)
            return int(count) <= max_requests
        except Exception:
            pass

    async with _lock:
        timestamps = _in_memory[key]
        cutoff = now - window_seconds
        _in_memory[key] = [t for t in timestamps if t > cutoff]
        count = len(_in_memory[key])
        if count >= max_requests:
            return False
        _in_memory[key].append(now)
        setattr(request.state, _RL_KEY_STATE, key)
        setattr(request.state, _RL_TS_STATE, now)
        return True


async def refund_rate_limit(request: Request) -> None:
    """Undo a counted request (e.g. 401) so auth storms do not lock out the client."""
    key = getattr(request.state, _RL_KEY_STATE, None)
    if not key:
        return

    redis = await _get_redis()
    member = getattr(request.state, _RL_MEMBER_STATE, None)
    if redis and member:
        try:
            await redis.zrem(key, member)
            return
        except Exception:
            pass

    ts = getattr(request.state, _RL_TS_STATE, None)
    if ts is None:
        return
    async with _lock:
        stamps = _in_memory.get(key)
        if not stamps:
            return
        try:
            stamps.remove(ts)
        except ValueError:
            pass


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        max_requests: int = 300,
        window_seconds: int = 60,
        anon_max_requests: int | None = None,
        exclude_paths: tuple[str, ...] = (
            "/health",
            "/health/ready",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/metrics",
        ),
    ) -> None:
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.anon_max_requests = (
            anon_max_requests
            if anon_max_requests is not None
            else getattr(settings, "rate_limit_anon_max_requests", 60)
        )
        self.exclude_paths = exclude_paths

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.url.path in self.exclude_paths:
            return await call_next(request)

        window = self.window_seconds
        path = request.url.path or ""
        _, authed = _rate_limit_key(request)
        max_req = self.max_requests if authed else self.anon_max_requests
        # Stricter throttle for invite preview/accept (brute-force codes).
        if "/company-invites/" in path or path.startswith("/api/v1/invites/"):
            max_req = min(max_req, 20)
            window = min(window, 60)

        allowed = await check_rate_limit(request, max_req, window)
        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Too many requests",
                headers={"Retry-After": str(window)},
            )

        response = await call_next(request)
        # Invalid/expired sessions must not burn the bucket — otherwise a 401
        # fan-out locks the client into 429 until the window expires.
        if response.status_code == status.HTTP_401_UNAUTHORIZED:
            await refund_rate_limit(request)
        return response


def add_rate_limiting(
    app: FastAPI,
    max_requests: int = 300,
    window_seconds: int = 60,
    anon_max_requests: int | None = None,
) -> None:
    app.add_middleware(
        RateLimitMiddleware,
        max_requests=max_requests,
        window_seconds=window_seconds,
        anon_max_requests=anon_max_requests,
    )
