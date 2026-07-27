"""Extend runway specialty tables with activity event bridge columns.

Revision ID: mom_26_business_runway_runtime
Revises: mom_25_team_operations_runtime
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "mom_26_business_runway_runtime"
down_revision: Union[str, Sequence[str], None] = "mom_25_team_operations_runtime"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_TABLES = (
    "runway_cash_inflows",
    "runway_expense_burns",
    "runway_financial_updates",
    "runway_risks",
    "runway_strategic_decisions",
)


def upgrade() -> None:
    for table in _TABLES:
        op.add_column(table, sa.Column("event_id", sa.Uuid(), nullable=True))
        op.add_column(table, sa.Column("amount_minor", sa.BigInteger(), nullable=True))
        op.add_column(
            table,
            sa.Column("currency_code", sa.String(10), nullable=True),
        )
        op.add_column(
            table,
            sa.Column("is_voided", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        )
        op.create_foreign_key(
            f"fk_{table}_event",
            table,
            "business_activity_events",
            ["event_id"],
            ["event_id"],
        )
        op.create_index(f"idx_{table}_event", table, ["event_id"])


def downgrade() -> None:
    for table in reversed(_TABLES):
        op.drop_index(f"idx_{table}_event", table_name=table)
        op.drop_constraint(f"fk_{table}_event", table, type_="foreignkey")
        op.drop_column(table, "is_voided")
        op.drop_column(table, "currency_code")
        op.drop_column(table, "amount_minor")
        op.drop_column(table, "event_id")
