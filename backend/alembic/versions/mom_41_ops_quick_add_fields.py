"""Ops Quick Add fields: approver_ids + expanded enums.

Revision ID: mom_41_ops_quick_add_fields
Revises: mom_40_fix_ops_audit_columns

Note: asyncpg rejects multi-statement prepared SQL — one op.execute per statement.
"""
from typing import Sequence, Union

from alembic import op

revision: str = "mom_41_ops_quick_add_fields"
down_revision: Union[str, Sequence[str], None] = "mom_40_fix_ops_audit_columns"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE operations_approval_requests ADD COLUMN IF NOT EXISTS approver_ids JSONB"
    )
    op.execute(
        "ALTER TABLE operations_approval_requests ADD COLUMN IF NOT EXISTS due_date DATE"
    )

    op.execute(
        "ALTER TABLE operations_approval_requests DROP CONSTRAINT IF EXISTS chk_operations_approval_request_type"
    )
    op.execute(
        """
        ALTER TABLE operations_approval_requests
            ADD CONSTRAINT chk_operations_approval_request_type
            CHECK (
                request_type IN (
                    'expense_approval',
                    'vendor_approval',
                    'budget_change',
                    'policy_exception',
                    'operational_request',
                    'hiring',
                    'contract',
                    'purchase',
                    'other'
                )
            )
        """
    )

    op.execute(
        "ALTER TABLE operations_spend_entries DROP CONSTRAINT IF EXISTS chk_operations_spend_category"
    )
    op.execute(
        """
        ALTER TABLE operations_spend_entries
            ADD CONSTRAINT chk_operations_spend_category
            CHECK (
                spend_category IN (
                    'purchase',
                    'vendor_payment',
                    'staff_cost',
                    'utility_bill',
                    'maintenance',
                    'marketing_spend',
                    'inventory_refill',
                    'service_charge',
                    'travel_expense',
                    'rent',
                    'other'
                )
            )
        """
    )

    op.execute(
        "ALTER TABLE operations_vendor_updates DROP CONSTRAINT IF EXISTS chk_operations_vendor_event_type"
    )
    op.execute(
        """
        ALTER TABLE operations_vendor_updates
            ADD CONSTRAINT chk_operations_vendor_event_type
            CHECK (
                vendor_event_type IN (
                    'new_vendor',
                    'vendor_evaluation',
                    'vendor_issue',
                    'contract_renewal',
                    'payment_status',
                    'contract_change',
                    'vendor_suspension',
                    'vendor_reactivation',
                    'contact_update',
                    'other'
                )
            )
        """
    )

    op.execute(
        "ALTER TABLE operations_improvements DROP CONSTRAINT IF EXISTS chk_operations_improvement_expected_impact"
    )
    op.execute(
        """
        ALTER TABLE operations_improvements
            ADD CONSTRAINT chk_operations_improvement_expected_impact
            CHECK (
                expected_impact IN (
                    'reduce_cost',
                    'improve_speed',
                    'reduce_issues',
                    'improve_service',
                    'improve_control',
                    'improve_visibility',
                    'increase_revenue',
                    'other'
                )
            )
        """
    )

    op.execute(
        "ALTER TABLE operations_improvements DROP CONSTRAINT IF EXISTS chk_operations_improvement_type"
    )
    op.execute(
        """
        ALTER TABLE operations_improvements
            ADD CONSTRAINT chk_operations_improvement_type
            CHECK (
                improvement_type IN (
                    'process_improvement',
                    'budget_control_improvement',
                    'customer_experience_improvement',
                    'inventory_improvement',
                    'compliance_improvement',
                    'staffing_scheduling_improvement',
                    'approval_flow_improvement',
                    'service_quality_improvement',
                    'operational_control_improvement',
                    'vendor_experience_improvement',
                    'other'
                )
            )
        """
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE operations_approval_requests DROP COLUMN IF EXISTS due_date"
    )
    op.execute(
        "ALTER TABLE operations_approval_requests DROP COLUMN IF EXISTS approver_ids"
    )
