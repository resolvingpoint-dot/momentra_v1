"""Fix business_operations snapshot refresh column names.

``sp_refresh_business_operations_snapshot`` (mom_07) INSERTed into
``business_operations_snapshots`` using legacy names that never existed on
that table (``monthly_operating_budget``, ``*_total``). Real columns are
``monthly_budget``, ``allocated_budget``, ``budget_used``, ``budget_remaining``.

Also align pulse/metrics procs that read those fields from the snapshot row.

Revision ID: mom_28_fix_ops_snapshot_cols
Revises: mom_27_ops_runtime

Revision id must stay <= 32 chars (alembic_version.version_num).
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "mom_28_fix_ops_snapshot_cols"
down_revision: Union[str, Sequence[str], None] = "mom_27_ops_runtime"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        sa.text(
            r"""
CREATE OR REPLACE FUNCTION sp_refresh_business_operations_snapshot(
    p_moment_id UUID
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
DECLARE
    v_monthly_budget NUMERIC(18,2) := 0;
    v_allocated_budget NUMERIC(18,2) := 0;
    v_budget_used NUMERIC(18,2) := 0;
    v_budget_remaining NUMERIC(18,2) := 0;
    v_budget_alert_count INTEGER := 0;

    v_vendor_activity_count INTEGER := 0;
    v_open_approval_count INTEGER := 0;
    v_active_issue_count INTEGER := 0;
    v_critical_issue_count INTEGER := 0;
    v_improvement_count INTEGER := 0;

    v_operations_health_status VARCHAR(50) := 'healthy';
    v_operating_currency VARCHAR(10) := 'INR';
BEGIN

    SELECT
        monthly_operating_budget,
        operating_currency
    INTO
        v_monthly_budget,
        v_operating_currency
    FROM business_operations_setup
    WHERE moment_id = p_moment_id;

    SELECT COALESCE(SUM(allocated_budget), 0)
    INTO v_allocated_budget
    FROM business_operations_budget_categories
    WHERE moment_id = p_moment_id
      AND category_status = 'active'
      AND archived_at IS NULL;

    SELECT COALESCE(SUM(amount_in_operating_currency), 0)
    INTO v_budget_used
    FROM operations_spend_entries
    WHERE moment_id = p_moment_id
      AND archived_at IS NULL
      AND approval_status IN ('not_required', 'approved');

    v_budget_remaining :=
        GREATEST(
            COALESCE(v_allocated_budget, 0) - COALESCE(v_budget_used, 0),
            0
        );

    SELECT COUNT(*)
    INTO v_budget_alert_count
    FROM business_operations_budget_categories bc
    WHERE bc.moment_id = p_moment_id
      AND bc.category_status = 'active'
      AND bc.archived_at IS NULL
      AND bc.allocated_budget > 0
      AND (
            (
                SELECT COALESCE(SUM(se.amount_in_operating_currency), 0)
                FROM operations_spend_entries se
                WHERE se.moment_id = bc.moment_id
                  AND se.budget_category_id = bc.budget_category_id
                  AND se.archived_at IS NULL
                  AND se.approval_status IN ('not_required', 'approved')
            ) / bc.allocated_budget
          ) * 100 >= bc.alert_threshold_percent;

    SELECT COUNT(*)
    INTO v_vendor_activity_count
    FROM operations_vendor_updates
    WHERE moment_id = p_moment_id
      AND archived_at IS NULL;

    SELECT COUNT(*)
    INTO v_open_approval_count
    FROM operations_approval_requests
    WHERE moment_id = p_moment_id
      AND approval_status = 'pending'
      AND archived_at IS NULL;

    SELECT COUNT(*)
    INTO v_active_issue_count
    FROM operations_issues
    WHERE moment_id = p_moment_id
      AND issue_status IN ('open', 'investigating')
      AND archived_at IS NULL;

    SELECT COUNT(*)
    INTO v_critical_issue_count
    FROM operations_issues
    WHERE moment_id = p_moment_id
      AND severity = 'critical'
      AND issue_status <> 'resolved'
      AND archived_at IS NULL;

    SELECT COUNT(*)
    INTO v_improvement_count
    FROM operations_improvements
    WHERE moment_id = p_moment_id
      AND archived_at IS NULL;

    IF v_critical_issue_count > 0
       OR v_budget_alert_count >= 2
    THEN
        v_operations_health_status := 'at_risk';

    ELSIF v_active_issue_count > 0
       OR v_open_approval_count > 0
       OR v_budget_alert_count = 1
    THEN
        v_operations_health_status := 'attention';

    ELSE
        v_operations_health_status := 'healthy';
    END IF;

    DELETE FROM business_operations_snapshots
    WHERE moment_id = p_moment_id
      AND snapshot_date = CURRENT_DATE;

    INSERT INTO business_operations_snapshots (
        moment_id,
        snapshot_date,
        monthly_budget,
        allocated_budget,
        budget_used,
        budget_remaining,
        budget_alert_count,
        vendor_activity_count,
        open_approval_count,
        active_issue_count,
        critical_issue_count,
        improvement_count,
        operations_health_status,
        operating_currency,
        generated_at
    )
    VALUES (
        p_moment_id,
        CURRENT_DATE,
        COALESCE(v_monthly_budget, 0),
        COALESCE(v_allocated_budget, 0),
        COALESCE(v_budget_used, 0),
        COALESCE(v_budget_remaining, 0),
        COALESCE(v_budget_alert_count, 0),
        COALESCE(v_vendor_activity_count, 0),
        COALESCE(v_open_approval_count, 0),
        COALESCE(v_active_issue_count, 0),
        COALESCE(v_critical_issue_count, 0),
        COALESCE(v_improvement_count, 0),
        v_operations_health_status,
        COALESCE(v_operating_currency, 'INR'),
        CURRENT_TIMESTAMP
    );

END;
$$;
            """
        )
    )

    # Patch dependent procs: replace wrong snapshot field names in-place.
    op.execute(
        sa.text(
            """
DO $$
DECLARE
    def text;
BEGIN
    SELECT pg_get_functiondef(p.oid) INTO def
    FROM pg_proc p
    JOIN pg_namespace n ON n.oid = p.pronamespace
    WHERE n.nspname = 'public'
      AND p.proname = 'sp_refresh_business_operations_pulse_snapshot';
    IF def IS NOT NULL THEN
        def := replace(def, 'v_snapshot.budget_used_total', 'v_snapshot.budget_used');
        def := replace(def, 'v_snapshot.budget_remaining_total', 'v_snapshot.budget_remaining');
        EXECUTE def;
    END IF;

    SELECT pg_get_functiondef(p.oid) INTO def
    FROM pg_proc p
    JOIN pg_namespace n ON n.oid = p.pronamespace
    WHERE n.nspname = 'public'
      AND p.proname = 'sp_refresh_business_operations_moment_metrics';
    IF def IS NOT NULL THEN
        def := replace(def, 'v_snapshot.budget_used_total', 'v_snapshot.budget_used');
        def := replace(def, 'v_snapshot.budget_remaining_total', 'v_snapshot.budget_remaining');
        EXECUTE def;
    END IF;
END $$;
            """
        )
    )


def downgrade() -> None:
    # Intentionally no-op: restoring the broken column names would re-break activate.
    pass
