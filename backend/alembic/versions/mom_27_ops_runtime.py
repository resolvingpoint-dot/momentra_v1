"""Extend operations specialty tables with activity event bridge columns.

Revision ID: mom_27_ops_runtime
Revises: mom_26_business_runway_runtime

Idempotent: ``idx_operations_vendor_updates_event`` already indexes
``vendor_event_type`` (mom_04). Activity-event indexes use
``idx_*_activity_event`` to avoid that name clash.

Revision id must stay <= 32 chars (alembic_version.version_num).
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "mom_27_ops_runtime"
down_revision: Union[str, Sequence[str], None] = "mom_26_business_runway_runtime"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_TABLES = (
    "operations_spend_entries",
    "operations_vendor_updates",
    "operations_approval_requests",
    "operations_issues",
    "operations_improvements",
)


def _add_column_if_missing(table: str, column: str, coltype_sql: str) -> None:
    op.execute(
        sa.text(f"ALTER TABLE {table} ADD COLUMN IF NOT EXISTS {column} {coltype_sql}")
    )


def upgrade() -> None:
    for table in _TABLES:
        _add_column_if_missing(table, "event_id", "UUID")
        _add_column_if_missing(table, "amount_minor", "BIGINT")
        _add_column_if_missing(
            table, "is_voided", "BOOLEAN NOT NULL DEFAULT false"
        )
        op.execute(
            sa.text(
                f"""
                DO $$ BEGIN
                    ALTER TABLE {table}
                        ADD CONSTRAINT fk_{table}_event
                        FOREIGN KEY (event_id)
                        REFERENCES business_activity_events(event_id);
                EXCEPTION
                    WHEN duplicate_object THEN NULL;
                END $$;
                """
            )
        )
        # Do not reuse idx_*_event — vendor_updates already uses that name
        # for vendor_event_type.
        op.execute(
            sa.text(
                f"CREATE INDEX IF NOT EXISTS idx_{table}_activity_event "
                f"ON {table} (event_id)"
            )
        )


def downgrade() -> None:
    for table in reversed(_TABLES):
        op.execute(sa.text(f"DROP INDEX IF EXISTS idx_{table}_activity_event"))
        op.execute(
            sa.text(f"ALTER TABLE {table} DROP CONSTRAINT IF EXISTS fk_{table}_event")
        )
        op.drop_column(table, "is_voided")
        op.drop_column(table, "amount_minor")
        op.drop_column(table, "event_id")
