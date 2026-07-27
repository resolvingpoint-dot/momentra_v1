"""003 Group + Shared-experience domain tables

Revision ID: mom_03_group
Revises: mom_02_personal

Auto-generated from the Momentra SQL design documents. The SQL is preserved
verbatim in the sibling ``sql/mom_03_group.up.sql`` / ``sql/mom_03_group.down.sql`` files
(statements separated by a sentinel so dollar-quoted bodies stay intact).

Execution is resilient: each statement runs inside a SAVEPOINT. If a statement
fails (e.g. a source-doc reference to a column/table that does not exist, or a
cross-object ordering dependency) it is recorded in ``mom_migration_skips``
instead of aborting the whole migration. ``mom_09_seed_data`` retries every
recorded statement once at the end (after all objects exist), so ordering-only
failures are recovered; whatever remains in ``mom_migration_skips`` afterwards
is a genuine source-SQL defect to review.
"""
from __future__ import annotations

import logging
import os

import sqlalchemy as sa
from alembic import op

revision = "mom_03_group"
down_revision = "mom_02_personal"
branch_labels = None
depends_on = None

_SPLIT = "\n-- >>>STMT<<<\n"
_log = logging.getLogger("alembic.momentra")


def _statements(fname: str) -> list[str]:
    path = os.path.join(os.path.dirname(__file__), "sql", fname)
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8") as fh:
        content = fh.read()
    return [s.strip() for s in content.split(_SPLIT) if s.strip()]


def _record_skip(bind, seq: int, err: Exception, stmt: str) -> None:
    sp = bind.begin_nested()
    try:
        bind.execute(
            sa.text(
                "INSERT INTO mom_migration_skips (migration, seq, error, sql) "
                "VALUES (:m, :s, :e, :q)"
            ),
            {"m": revision, "s": seq, "e": str(err)[:1000], "q": stmt},
        )
        sp.commit()
    except Exception:  # pragma: no cover - best effort bookkeeping
        sp.rollback()


def _run(fname: str, record: bool) -> None:
    bind = op.get_bind()
    for i, stmt in enumerate(_statements(fname)):
        sp = bind.begin_nested()
        try:
            bind.exec_driver_sql(stmt)
            sp.commit()
        except Exception as exc:  # noqa: BLE001 - resilient application
            sp.rollback()
            if record:
                _record_skip(bind, i, exc, stmt)
                _log.warning("[%s] skipped statement #%s: %s", revision, i, str(exc)[:200])


def upgrade() -> None:
    _run("mom_03_group.up.sql", record=True)


def downgrade() -> None:
    _run("mom_03_group.down.sql", record=False)
