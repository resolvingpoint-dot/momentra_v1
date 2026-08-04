#!/usr/bin/env python3
"""Repair bookings stored 100× too high (web Quick Add double *100).

Run from backend root with DATABASE_URL set (same DB the ngrok host uses):

  python ..\\_pulse_kpi_fix_sync\\repair_inflated_booking_amounts_db.py \\
    --moment-id 75b96dd5-6953-4de4-b575-5f58c8be16bf

Prefer the HTTP endpoint after deploy:
  POST /api/v1/group/trips/{moment_id}/repair-inflated-booking-amounts
"""
from __future__ import annotations

import argparse
import asyncio
import os
from pathlib import Path
from uuid import UUID


def _load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--moment-id", required=True)
    parser.add_argument("--min-minor", type=int, default=100_000_000)
    parser.add_argument("--divisor", type=int, default=100)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    backend_root = Path(__file__).resolve().parents[1] / "backend"
    if not backend_root.exists():
        backend_root = Path.cwd()
    _load_dotenv(backend_root / ".env")
    os.environ.setdefault("MOMENTRA_DB_NULL_POOL", "1")

    import sys

    sys.path.insert(0, str(backend_root))

    from sqlalchemy import select

    from app.core.database import async_session_factory
    from app.domains.group import moment_store as store
    from app.domains.moments.models import MomentModel

    moment_id = UUID(args.moment_id)
    async with async_session_factory() as session:
        m = (await session.execute(select(MomentModel).where(MomentModel.id == moment_id))).scalar_one()
        repaired: list[dict] = []
        for row in list(store.list_items(m, "bookings")):
            if row.get("deleted"):
                continue
            amt = int(row.get("amount_minor") or 0)
            title = str(row.get("title") or row.get("provider") or "")
            print(f"booking {title!r} amount_minor={amt}")
            if amt < args.min_minor:
                continue
            new_amt = amt // args.divisor
            if args.dry_run:
                repaired.append({"title": title, "before": amt, "after": new_amt})
                continue
            store.update_item(m, "bookings", str(row["id"]), {"amount_minor": new_amt})
            repaired.append({"title": title, "before": amt, "after": new_amt})
        if not args.dry_run:
            await session.commit()
        print("repaired", repaired)
        booking_spend = sum(
            int(b.get("amount_minor") or 0)
            for b in store.list_items(m, "bookings")
            if not b.get("deleted")
        )
        _, exp_total = store.expense_summary(m)
        print("booking_spend", booking_spend, "exp_total", exp_total, "combined", exp_total + booking_spend)


if __name__ == "__main__":
    asyncio.run(main())
