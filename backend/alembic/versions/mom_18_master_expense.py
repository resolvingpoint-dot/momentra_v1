"""Master expense orchestrator parent table.

Revision ID: mom_18_master_expense
Revises: mom_17_projection_perf
"""
from typing import Sequence, Union

from alembic import op

revision: str = "mom_18_master_expense"
down_revision: Union[str, Sequence[str], None] = "mom_17_projection_perf"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS personal_master_expenses (
            master_expense_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL,
            title VARCHAR(200) NOT NULL,
            amount_minor BIGINT NOT NULL,
            currency_code VARCHAR(10) NOT NULL,
            account_id UUID NOT NULL REFERENCES personal_accounts(account_id),
            category_code VARCHAR(80) NOT NULL,
            occurred_at TIMESTAMP NOT NULL,
            feeling VARCHAR(40),
            meaningfulness VARCHAR(20),
            memorability VARCHAR(20),
            is_shared BOOLEAN NOT NULL DEFAULT false,
            shared_with JSONB NOT NULL DEFAULT '[]'::jsonb,
            relationship_impact JSONB NOT NULL DEFAULT '[]'::jsonb,
            context_reason VARCHAR(80),
            notes VARCHAR(200),
            client_request_id UUID,
            life_operations_event_id UUID REFERENCES personal_quick_add_events(quick_add_event_id),
            lifestyle_event_id UUID REFERENCES personal_quick_add_events(quick_add_event_id),
            relationships_event_id UUID REFERENCES personal_quick_add_events(quick_add_event_id),
            is_voided BOOLEAN NOT NULL DEFAULT false,
            deleted_at TIMESTAMP,
            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """
    )
    op.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS uq_personal_master_expense_client_request
        ON personal_master_expenses (user_id, client_request_id)
        WHERE client_request_id IS NOT NULL AND is_voided = false;
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_personal_master_expenses_user
        ON personal_master_expenses (user_id, occurred_at DESC);
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS personal_master_expenses CASCADE;")
