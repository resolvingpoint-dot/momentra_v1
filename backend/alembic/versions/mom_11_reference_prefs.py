"""Add locale/currency columns to user_preferences

Revision ID: mom_11_reference_prefs
Revises: mom_10_fixes
Create Date: 2026-07-06

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "mom_11_reference_prefs"
down_revision: Union[str, Sequence[str], None] = "mom_10_fixes"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "user_preferences",
        sa.Column(
            "default_currency_code",
            sa.String(length=3),
            nullable=False,
            server_default="INR",
        ),
    )
    op.add_column(
        "user_preferences",
        sa.Column(
            "locale",
            sa.String(length=16),
            nullable=False,
            server_default="en-IN",
        ),
    )
    op.add_column(
        "user_preferences",
        sa.Column(
            "country_code",
            sa.String(length=2),
            nullable=False,
            server_default="IN",
        ),
    )
    op.add_column(
        "user_preferences",
        sa.Column(
            "timezone",
            sa.String(length=64),
            nullable=False,
            server_default="Asia/Kolkata",
        ),
    )


def downgrade() -> None:
    op.drop_column("user_preferences", "timezone")
    op.drop_column("user_preferences", "country_code")
    op.drop_column("user_preferences", "locale")
    op.drop_column("user_preferences", "default_currency_code")
