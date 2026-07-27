"""Add subcategory_code to personal money + master expenses.

Revision ID: mom_20_expense_subcategory
Revises: mom_19_fix_moment_type_code
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "mom_20_expense_subcategory"
down_revision: Union[str, Sequence[str], None] = "mom_19_fix_moment_type_code"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "personal_money_events",
        sa.Column("subcategory_code", sa.String(length=80), nullable=True),
    )
    op.add_column(
        "personal_master_expenses",
        sa.Column("subcategory_code", sa.String(length=80), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("personal_master_expenses", "subcategory_code")
    op.drop_column("personal_money_events", "subcategory_code")
