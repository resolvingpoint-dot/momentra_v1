"""Add amount_minor to personal_money_events.

Revision ID: mom_12_money_minor
Revises: mom_11_reference_prefs
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "mom_12_money_minor"
down_revision: Union[str, Sequence[str], None] = "mom_11_reference_prefs"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "personal_money_events",
        sa.Column("amount_minor", sa.BigInteger(), nullable=False, server_default="0"),
    )
    op.add_column(
        "personal_money_events",
        sa.Column(
            "exchange_rate_to_user_currency",
            sa.Numeric(precision=18, scale=8),
            nullable=True,
        ),
    )
    op.add_column(
        "personal_money_events",
        sa.Column("amount_user_currency_minor", sa.BigInteger(), nullable=True),
    )
    # Backfill INR rows (minor_unit=2) from legacy amount column.
    op.execute(
        """
        UPDATE personal_money_events
        SET amount_minor = ROUND(amount * 100)::bigint
        WHERE amount_minor = 0 AND currency_code = 'INR'
        """
    )
    op.execute(
        """
        UPDATE personal_money_events
        SET amount_minor = ROUND(amount * 100)::bigint
        WHERE amount_minor = 0 AND currency_code NOT IN ('JPY', 'KWD')
        """
    )
    op.execute(
        """
        UPDATE personal_money_events
        SET amount_minor = ROUND(amount)::bigint
        WHERE amount_minor = 0 AND currency_code = 'JPY'
        """
    )


def downgrade() -> None:
    op.drop_column("personal_money_events", "amount_user_currency_minor")
    op.drop_column("personal_money_events", "exchange_rate_to_user_currency")
    op.drop_column("personal_money_events", "amount_minor")
