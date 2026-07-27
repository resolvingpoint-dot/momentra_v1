"""B.7A hardening: quick-add idempotency and domain event audit log.

Revision ID: mom_16_b7a_hardening
Revises: mom_15_personal_events_view

Adds client_request_id to personal_quick_add_events for idempotent submits.
Creates domain_event_log for published domain event audit trail.
"""
from typing import Sequence, Union

from alembic import op


revision: str = "mom_16_b7a_hardening"
down_revision: Union[str, Sequence[str], None] = "mom_15_personal_events_view"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE personal_quick_add_events
        ADD COLUMN IF NOT EXISTS client_request_id UUID NULL;
        """
    )
    op.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS uq_personal_quick_add_client_request_id
        ON personal_quick_add_events (client_request_id)
        WHERE client_request_id IS NOT NULL;
        """
    )
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS domain_event_log (
            event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name VARCHAR(120) NOT NULL,
            user_id UUID NOT NULL,
            moment_id UUID NOT NULL,
            context VARCHAR(50) NOT NULL,
            moment_type VARCHAR(50),
            payload JSONB NOT NULL DEFAULT '{}'::jsonb,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_domain_event_log_moment
        ON domain_event_log (moment_id);
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_domain_event_log_user
        ON domain_event_log (user_id);
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_domain_event_log_name
        ON domain_event_log (name);
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS domain_event_log CASCADE;")
    op.execute(
        """
        DROP INDEX IF EXISTS uq_personal_quick_add_client_request_id;
        """
    )
    op.execute(
        """
        ALTER TABLE personal_quick_add_events
        DROP COLUMN IF EXISTS client_request_id;
        """
    )
