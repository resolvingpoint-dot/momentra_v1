"""Thin wrappers over the existing SQL procedures.

All refresh work is delegated to procedures shipped in the migrations -- the
worker never recomputes scores in Python (no duplicate calculations). Procedure
names come from these fixed allowlists (never user input), so building the SQL
text dynamically is safe.

The procedures upsert into snapshot tables, which makes every refresh naturally
idempotent: running it twice yields the same row.
"""
from __future__ import annotations

import logging
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

# User-scoped snapshot procedures (all are PL/pgSQL PROCEDUREs -> CALL).
# Personal health/dimensions must run before aggregate; Life360 last.
USER_SNAPSHOT_PROCS: tuple[str, ...] = (
    "sp_refresh_personal_life_health",
    "sp_refresh_personal_life_dimensions",
    "sp_refresh_personal_life_snapshot",
    "sp_refresh_circle",
    "sp_refresh_life360_snapshots",
)

# (procedure, kind) per context. kind: "CALL" for PROCEDUREs, "SELECT" for FUNCTIONs.
MEMORY_PROCS: dict[str, tuple[str, str]] = {
    "personal": ("sp_refresh_personal_memory", "CALL"),
    "group": ("sp_refresh_group_memory_intelligence", "SELECT"),
    "business": ("sp_refresh_business_memory_patterns", "SELECT"),
}

ANALYTICS_PROCS: dict[str, tuple[str, str]] = {
    "personal": ("sp_run_personal_ai_refresh", "CALL"),  # 2nd arg (run_type) uses its default
    "group": ("sp_refresh_group_analytics", "SELECT"),
    "business": ("sp_refresh_business_orchestration", "SELECT"),
}


async def _exec_uuid(session: AsyncSession, proc: str, kind: str, value: UUID) -> None:
    verb = "CALL" if kind == "CALL" else "SELECT"
    await session.execute(text(f"{verb} {proc}((:v)::uuid)"), {"v": str(value)})


async def refresh_user_snapshots(session: AsyncSession, user_id: UUID) -> list[str]:
    for proc in USER_SNAPSHOT_PROCS:
        await _exec_uuid(session, proc, "CALL", user_id)
    return list(USER_SNAPSHOT_PROCS)


async def refresh_life360_snapshot(session: AsyncSession, user_id: UUID) -> str:
    await _exec_uuid(session, "sp_refresh_life360_snapshots", "CALL", user_id)
    return "sp_refresh_life360_snapshots"


async def refresh_memory(session: AsyncSession, context: str, moment_id: UUID) -> str:
    proc, kind = _lookup(MEMORY_PROCS, context, "memory")
    await _exec_uuid(session, proc, kind, moment_id)
    return proc


async def refresh_analytics(session: AsyncSession, context: str, moment_id: UUID) -> str:
    proc, kind = _lookup(ANALYTICS_PROCS, context, "analytics")
    await _exec_uuid(session, proc, kind, moment_id)
    return proc


async def refresh_personal_orchestration(session: AsyncSession, moment_id: UUID) -> str:
    proc = "sp_refresh_personal_orchestration"
    await _exec_uuid(session, proc, "CALL", moment_id)
    return proc


async def try_refresh_personal_orchestration(
    session: AsyncSession, moment_id: UUID
) -> bool:
    """Best-effort orchestration refresh that does not poison the outer transaction."""
    try:
        async with session.begin_nested():
            await refresh_personal_orchestration(session, moment_id)
        return True
    except Exception:
        logger.exception(
            "Personal orchestration refresh failed for moment=%s", moment_id
        )
        return False


async def process_orchestration_job(session: AsyncSession, job_id: UUID) -> None:
    await session.execute(
        text("SELECT sp_process_orchestration_job((:v)::uuid)"), {"v": str(job_id)}
    )


def _lookup(table: dict[str, tuple[str, str]], context: str, kind: str) -> tuple[str, str]:
    key = (context or "").lower()
    if key not in table:
        raise ValueError(f"Unknown {kind} context {context!r}; expected one of {sorted(table)}")
    return table[key]
