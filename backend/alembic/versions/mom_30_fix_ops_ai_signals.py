"""Fix ops AI signals column names against ai_signals.

``sp_refresh_operations_ai_signals`` used ``signal_source`` / ``signal_score``,
but ``ai_signals`` columns are ``signal_scope`` / ``confidence_score``.

Revision ID: mom_30_fix_ops_ai_signals
Revises: mom_29_fix_ops_memory_patterns

Revision id must stay <= 32 chars (alembic_version.version_num).
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "mom_30_fix_ops_ai_signals"
down_revision: Union[str, Sequence[str], None] = "mom_29_fix_ops_memory_patterns"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        sa.text(
            r"""
CREATE OR REPLACE FUNCTION sp_refresh_operations_ai_signals(
    p_moment_id UUID
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
DECLARE
    v_vendor_evaluations INTEGER;
    v_improvement_count INTEGER;
    v_issue_resolved_count INTEGER;
    v_current_health VARCHAR(50);
BEGIN

    DELETE FROM ai_signals
    WHERE moment_id = p_moment_id
      AND signal_scope = 'business_operations';

    SELECT COUNT(*)
    INTO v_vendor_evaluations
    FROM operations_vendor_updates
    WHERE moment_id = p_moment_id
      AND vendor_event_type = 'vendor_evaluation'
      AND created_at >= CURRENT_DATE - INTERVAL '30 day'
      AND archived_at IS NULL;

    IF v_vendor_evaluations > 0 THEN
        INSERT INTO ai_signals (
            moment_id,
            signal_scope,
            signal_type,
            signal_title,
            signal_message,
            confidence_score,
            generated_at
        )
        VALUES (
            p_moment_id,
            'business_operations',
            'vendor_activity',
            'Vendor Evaluations Increasing',
            CONCAT(
                v_vendor_evaluations,
                ' vendor evaluation activities recorded recently.'
            ),
            82,
            CURRENT_TIMESTAMP
        );
    END IF;

    SELECT COUNT(*)
    INTO v_improvement_count
    FROM operations_improvements
    WHERE moment_id = p_moment_id
      AND created_at >= CURRENT_DATE - INTERVAL '30 day'
      AND archived_at IS NULL;

    IF v_improvement_count > 0 THEN
        INSERT INTO ai_signals (
            moment_id,
            signal_scope,
            signal_type,
            signal_title,
            signal_message,
            confidence_score,
            generated_at
        )
        VALUES (
            p_moment_id,
            'business_operations',
            'improvement_momentum',
            'Operational Improvements Recorded',
            CONCAT(
                v_improvement_count,
                ' improvement initiatives were recorded recently.'
            ),
            84,
            CURRENT_TIMESTAMP
        );
    END IF;

    SELECT COUNT(*)
    INTO v_issue_resolved_count
    FROM operations_issues
    WHERE moment_id = p_moment_id
      AND issue_status = 'resolved'
      AND resolved_at >= CURRENT_DATE - INTERVAL '30 day'
      AND archived_at IS NULL;

    IF v_issue_resolved_count > 0 THEN
        INSERT INTO ai_signals (
            moment_id,
            signal_scope,
            signal_type,
            signal_title,
            signal_message,
            confidence_score,
            generated_at
        )
        VALUES (
            p_moment_id,
            'business_operations',
            'resolution_velocity',
            'Issue Resolution Improving',
            CONCAT(
                v_issue_resolved_count,
                ' operational issues resolved recently.'
            ),
            86,
            CURRENT_TIMESTAMP
        );
    END IF;

    SELECT operations_health_status
    INTO v_current_health
    FROM business_operations_snapshots
    WHERE moment_id = p_moment_id
    ORDER BY snapshot_date DESC
    LIMIT 1;

    IF v_current_health = 'healthy' THEN
        INSERT INTO ai_signals (
            moment_id,
            signal_scope,
            signal_type,
            signal_title,
            signal_message,
            confidence_score,
            generated_at
        )
        VALUES (
            p_moment_id,
            'business_operations',
            'operations_health',
            'Operational Health Stable',
            'Operations currently remain healthy and under control.',
            88,
            CURRENT_TIMESTAMP
        );
    END IF;

END;
$$;
            """
        )
    )


def downgrade() -> None:
    pass
