"""Projection read path indexes for memberships, money events, and group expenses.

Revision ID: mom_37_projection_read_indexes
Revises: mom_42_user_deleted_at

Note: numbered mom_37 historically, but chains after mom_42 so it does not
fork alongside mom_38 (which already revises mom_36).
"""
from typing import Sequence, Union

from alembic import op

revision: str = "mom_37_projection_read_indexes"
down_revision: Union[str, Sequence[str], None] = "mom_42_user_deleted_at"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # IF NOT EXISTS keeps this safe on environments that already have equivalents.
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_workspace_memberships_user_status
        ON business_workspace_members (user_id, status)
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_business_moments_workspace_status_updated
        ON business_moments (workspace_id, status, updated_at DESC)
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_moments_user_context_status_updated
        ON moments (user_id, context_type, status, updated_at DESC)
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_money_events_user_event_date
        ON personal_money_events (user_id, event_date DESC)
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_money_events_moment_event_date
        ON personal_money_events (moment_id, event_date DESC)
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_group_expenses_moment_created
        ON group_expenses (moment_id, created_at DESC)
        """
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_group_expenses_moment_created")
    op.execute("DROP INDEX IF EXISTS idx_money_events_moment_event_date")
    op.execute("DROP INDEX IF EXISTS idx_money_events_user_event_date")
    op.execute("DROP INDEX IF EXISTS idx_moments_user_context_status_updated")
    op.execute("DROP INDEX IF EXISTS idx_business_moments_workspace_status_updated")
    op.execute("DROP INDEX IF EXISTS idx_workspace_memberships_user_status")
