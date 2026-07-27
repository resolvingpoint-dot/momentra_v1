"""Async DB access for Celery tasks.

Celery workers are synchronous processes, while the app is fully async
(asyncpg). Each task therefore runs its coroutine via :func:`run_async` on a
fresh event loop and gets a task-local engine using ``NullPool`` -- this avoids
reusing asyncpg connections across event loops (a common source of
"attached to a different loop" errors) and keeps every job self-contained.
"""
from __future__ import annotations

import asyncio
from collections.abc import Awaitable
from contextlib import asynccontextmanager
from typing import TypeVar

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import settings

T = TypeVar("T")


def _async_url() -> str:
    if not settings.database_url:
        raise RuntimeError("DATABASE_URL not configured")
    return settings.database_url.replace("postgresql://", "postgresql+asyncpg://", 1)


@asynccontextmanager
async def worker_session() -> AsyncSession:
    """Yield an ``AsyncSession`` backed by a disposable NullPool engine."""
    engine = create_async_engine(
        _async_url(),
        poolclass=NullPool,
        connect_args={"statement_cache_size": 0},  # PgBouncer / pooled Postgres compat
    )
    try:
        factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        async with factory() as session:
            yield session
    finally:
        await engine.dispose()


def run_async(coro: Awaitable[T]) -> T:
    """Execute an awaitable to completion from synchronous Celery task code."""
    return asyncio.run(coro)
