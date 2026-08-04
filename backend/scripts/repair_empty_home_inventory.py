"""One-shot repair: heal module_states + backfill orphan group_moments rows.

Usage (from backend/ with DATABASE_URL in .env):
  python scripts/repair_empty_home_inventory.py
  python scripts/repair_empty_home_inventory.py --apply
"""
from __future__ import annotations

import argparse
import asyncio
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine


def _load_db_url() -> str:
    env = Path(__file__).resolve().parents[1] / ".env"
    for line in env.read_text(encoding="utf-8").splitlines():
        if line.startswith("DATABASE_URL=") and not line.startswith("#"):
            url = line.split("=", 1)[1].strip().strip('"').strip("'")
            break
    else:
        raise SystemExit("DATABASE_URL missing")
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    return url


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


async def heal_modules(conn, apply: bool) -> list[str]:
    notes: list[str] = []
    users = await conn.execute(
        text(
            """
            SELECT user_id::text AS uid,
                   bool_or(context_type = 'MY_MONEY') AS has_personal,
                   bool_or(context_type = 'GROUP') AS has_group,
                   bool_or(context_type = 'BUSINESS') AS has_business
            FROM moments
            WHERE status = 'ACTIVE'
              AND context_type IN ('MY_MONEY', 'GROUP', 'BUSINESS')
            GROUP BY user_id
            """
        )
    )
    for row in users:
        uid = row.uid
        desired: dict[str, str] = {}
        if row.has_personal:
            desired.update(
                {
                    "MY_MONEY": "ACTIVE",
                    "MEMORY": "ACTIVE",
                }
            )
        if row.has_group:
            desired["GROUP"] = "ACTIVE"
        if row.has_business:
            desired["BUSINESS"] = "ACTIVE"
        if row.has_personal or row.has_group or row.has_business:
            desired["PULSE"] = "ACTIVE"
            desired["MOMENTS"] = "ACTIVE"

        existing = await conn.execute(
            text(
                "SELECT module_key, state FROM module_states WHERE user_id = :u"
            ),
            {"u": uid},
        )
        state_map = {r.module_key: r.state for r in existing}
        changed = {}
        for key, state in desired.items():
            if (state_map.get(key) or "").upper() == state:
                continue
            changed[key] = (state_map.get(key), state)
            if apply:
                if key in state_map:
                    await conn.execute(
                        text(
                            """
                            UPDATE module_states
                            SET state = :s, updated_at = :ts, reason = :reason
                            WHERE user_id = :u AND module_key = :k
                            """
                        ),
                        {
                            "u": uid,
                            "k": key,
                            "s": state,
                            "ts": _now(),
                            "reason": "repair_empty_home_inventory",
                        },
                    )
                else:
                    await conn.execute(
                        text(
                            """
                            INSERT INTO module_states (
                              id, user_id, module_key, state, reason, created_at, updated_at
                            ) VALUES (
                              :id, :u, :k, :s, :reason, :ts, :ts
                            )
                            """
                        ),
                        {
                            "id": uuid4(),
                            "u": uid,
                            "k": key,
                            "s": state,
                            "ts": _now(),
                            "reason": "repair_empty_home_inventory",
                        },
                    )
        if changed:
            notes.append(f"user={uid} heal={changed}")
    return notes


async def backfill_group_rows(conn, apply: bool) -> list[str]:
    notes: list[str] = []
    orphans = await conn.execute(
        text(
            """
            SELECT m.id, m.user_id, m.moment_type, m.title, m.status
            FROM moments m
            LEFT JOIN group_moments gm ON gm.moment_id = m.id
            WHERE m.context_type = 'GROUP'
              AND m.status IN ('ACTIVE', 'DRAFT')
              AND gm.moment_id IS NULL
            ORDER BY m.status, m.created_at DESC NULLS LAST
            """
        )
    )
    now = _now()
    for row in orphans:
        notes.append(
            f"orphan {row.id} status={row.status} type={row.moment_type} title={row.title!r}"
        )
        if not apply:
            continue
        status = row.status if row.status in {"DRAFT", "ACTIVE", "COMPLETED", "ARCHIVED"} else "DRAFT"
        activated_at = now if status == "ACTIVE" else None
        await conn.execute(
            text(
                """
                INSERT INTO group_moments (
                  moment_id, moment_type, moment_profile, moment_name, status, stage,
                  created_by, created_at, updated_at, activation_status, activated_at
                ) VALUES (
                  :id, :mtype, 'DEFAULT', :name, :status, 'CREATED',
                  :uid, :ts, :ts, :activation_status, :activated_at
                )
                ON CONFLICT (moment_id) DO NOTHING
                """
            ),
            {
                "id": row.id,
                "mtype": str(row.moment_type or "SHARED_EXPERIENCE"),
                "name": str(row.title or "Group moment"),
                "status": status,
                "uid": row.user_id,
                "ts": now,
                "activation_status": "ACTIVE" if status == "ACTIVE" else "PLANNING",
                "activated_at": activated_at,
            },
        )
        # Owner roster stub when missing
        mem = await conn.execute(
            text(
                """
                SELECT 1 FROM group_moment_members
                WHERE moment_id = :id AND user_id = :uid
                  AND left_at IS NULL
                  AND upper(coalesce(status,'')) NOT IN ('LEFT','REMOVED','DECLINED')
                LIMIT 1
                """
            ),
            {"id": row.id, "uid": row.user_id},
        )
        if mem.first() is None and row.user_id is not None:
            await conn.execute(
                text(
                    """
                    INSERT INTO group_moment_members (
                      member_id, moment_id, display_name, role_code, status,
                      created_at, joined_at, user_id
                    ) VALUES (
                      :mid, :id, 'You', 'ORGANIZER', 'ACTIVE', :ts, :ts, :uid
                    )
                    """
                ),
                {
                    "mid": uuid4(),
                    "id": row.id,
                    "uid": row.user_id,
                    "ts": now,
                },
            )
    return notes


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Commit repairs")
    args = parser.parse_args()
    eng = create_async_engine(_load_db_url(), connect_args={"statement_cache_size": 0})
    async with eng.begin() as conn:
        if not args.apply:
            # dry-run: use nested transaction that always rolls back
            pass
        heal_notes = await heal_modules(conn, args.apply)
        orphan_notes = await backfill_group_rows(conn, args.apply)
        if not args.apply:
            await conn.rollback()
    await eng.dispose()
    mode = "APPLY" if args.apply else "DRY-RUN"
    print(f"=== {mode} module heals ({len(heal_notes)}) ===")
    for n in heal_notes:
        print(n)
    print(f"=== {mode} group_moments orphans ({len(orphan_notes)}) ===")
    for n in orphan_notes:
        print(n)


if __name__ == "__main__":
    asyncio.run(main())
