from __future__ import annotations

import logging
import os

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import settings

logger = logging.getLogger(__name__)

_async_url: str | None = None
if settings.database_url:
    _async_url = settings.database_url.replace(
        "postgresql://", "postgresql+asyncpg://", 1
    )


def _use_null_pool() -> bool:
    """Avoid QueuePool across TestClient event-loop boundaries (Windows).

    Starlette's sync TestClient can open a new asyncio loop per request unless
    used as a context manager; pooled asyncpg connections then die with
    ``Event loop is closed`` / ``NoneType.send`` on checkout.
    """
    flag = os.environ.get("MOMENTRA_DB_NULL_POOL", "").lower()
    if flag in {"1", "true", "yes"}:
        return True
    # Acceptance runs set this before importing the app.
    if settings.acceptance_database_url.strip():
        return True
    if settings.allow_test_auth and settings.debug:
        return True
    return False


_engine_kwargs: dict = {
    "echo": settings.debug,
    "pool_pre_ping": True,
    # statement_cache_size=0: PgBouncer transaction pooling compat.
    # timeout / command_timeout: fail fast when Postgres or the path is dead
    # (otherwise Linux TCP can stall ~60s → ConnectionDoesNotExistError).
    "connect_args": {
        "statement_cache_size": 0,
        "timeout": max(1, int(settings.db_connect_timeout)),
        "command_timeout": max(1, int(settings.db_command_timeout)),
    },
}
if _use_null_pool():
    _engine_kwargs["poolclass"] = NullPool
else:
    _engine_kwargs.update(
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        pool_timeout=settings.db_pool_timeout,
        pool_recycle=settings.db_pool_recycle,
    )

engine = create_async_engine(_async_url, **_engine_kwargs) if _async_url else None

async_session_factory = (
    async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    if engine
    else None
)


async def get_db() -> AsyncSession:
    if async_session_factory is None:
        raise RuntimeError("DATABASE_URL not configured")
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def ping_db() -> bool:
    """Lightweight readiness check. Returns False if DB is unset/unreachable."""
    if engine is None:
        return False
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as exc:  # noqa: BLE001 - readiness must never raise
        logger.warning("Database ping failed: %s", exc)
        # Drop stale pooled sockets so the next request opens a fresh connection
        # instead of replaying ConnectionDoesNotExistError for ~60s each time.
        try:
            await engine.dispose()
        except Exception:  # noqa: BLE001
            logger.warning("Failed to dispose engine after ping failure", exc_info=True)
        return False


async def dispose_engine() -> None:
    """Dispose the connection pool on shutdown."""
    if engine is not None:
        await engine.dispose()
        logger.info("Database engine disposed")
