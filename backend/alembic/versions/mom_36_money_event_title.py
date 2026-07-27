"""Add title to personal_money_events.

Revision ID: mom_36_money_event_title
Revises: mom_35_fix_highlight_order_by
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "mom_36_money_event_title"
down_revision: Union[str, Sequence[str], None] = "mom_35_fix_highlight_order_by"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "personal_money_events",
        sa.Column("title", sa.String(length=150), nullable=True),
    )
    op.execute(
        """
        UPDATE personal_money_events m
        SET title = LEFT(COALESCE(t.display_title, 'Money entry'), 150)
        FROM personal_activity_timeline t
        WHERE t.quick_add_event_id = m.quick_add_event_id
          AND t.is_voided IS FALSE
          AND (m.title IS NULL OR btrim(m.title) = '')
        """
    )
    op.execute(
        """
        UPDATE personal_money_events
        SET title = 'Money entry'
        WHERE title IS NULL OR btrim(title) = ''
        """
    )
    op.alter_column(
        "personal_money_events",
        "title",
        existing_type=sa.String(length=150),
        nullable=False,
        server_default="",
    )


def downgrade() -> None:
    op.drop_column("personal_money_events", "title")
