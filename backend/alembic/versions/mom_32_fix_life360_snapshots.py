"""Fix Life360 snapshot refresh procedure column names and group master wiring.

``sp_refresh_life360_snapshots`` referenced non-existent columns
(personal_life_snapshot_id, group_life_snapshot_id, business_life_snapshot_id)
and filtered business_life_snapshots by user_id instead of workspace membership.

Also ensures ``sp_refresh_group_analytics`` refreshes group_life_master_snapshots
so Life360 can read group domain scores after moment activation.

Revision ID: mom_32_fix_life360_snapshots
Revises: mom_31_business_workspaces
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "mom_32_fix_life360_snapshots"
down_revision: Union[str, Sequence[str], None] = "mom_31_business_workspaces"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_LIFE360_PROC = r"""
CREATE OR REPLACE PROCEDURE sp_refresh_life360_snapshots(p_user_id UUID)
LANGUAGE plpgsql
AS $$
DECLARE
    v_personal_score NUMERIC(5,2);
    v_group_score NUMERIC(5,2);
    v_business_score NUMERIC(5,2);

    v_personal_snapshot_id UUID;
    v_group_snapshot_id UUID;
    v_business_snapshot_id UUID;

    v_weight_total NUMERIC(6,2) := 0;
    v_alignment NUMERIC(5,2) := 0;

    v_prev_alignment NUMERIC(5,2);
    v_momentum NUMERIC(6,2);

    v_money NUMERIC(5,2);
    v_relationship NUMERIC(5,2);
    v_execution NUMERIC(5,2);
    v_growth NUMERIC(5,2);

    v_active_dims INTEGER := 0;
BEGIN

    SELECT life_aggregate_snapshot_id, life_health_score
    INTO v_personal_snapshot_id, v_personal_score
    FROM personal_life_aggregate_snapshots
    WHERE user_id = p_user_id
    ORDER BY snapshot_date DESC, created_at DESC
    LIMIT 1;

    SELECT master_snapshot_id, group_life_score
    INTO v_group_snapshot_id, v_group_score
    FROM group_life_master_snapshots
    WHERE user_id = p_user_id
    ORDER BY snapshot_date DESC, created_at DESC
    LIMIT 1;

    SELECT bls.snapshot_id, bls.life_score
    INTO v_business_snapshot_id, v_business_score
    FROM business_life_snapshots bls
    JOIN business_workspace_members bwm
      ON bwm.workspace_id = bls.workspace_id
    WHERE bwm.user_id = p_user_id
      AND bwm.status = 'ACTIVE'
    ORDER BY bls.generated_at DESC
    LIMIT 1;

    IF v_personal_score IS NOT NULL THEN
        v_alignment := v_alignment + (v_personal_score * 0.40);
        v_weight_total := v_weight_total + 0.40;
    END IF;

    IF v_group_score IS NOT NULL THEN
        v_alignment := v_alignment + (v_group_score * 0.30);
        v_weight_total := v_weight_total + 0.30;
    END IF;

    IF v_business_score IS NOT NULL THEN
        v_alignment := v_alignment + (v_business_score * 0.30);
        v_weight_total := v_weight_total + 0.30;
    END IF;

    IF v_weight_total > 0 THEN
        v_alignment := ROUND(v_alignment / v_weight_total, 2);
    ELSE
        v_alignment := 0;
    END IF;

    v_money := ROUND((
        COALESCE(v_personal_score, 0) * 0.55 +
        COALESCE(v_business_score, 0) * 0.45
    ) / NULLIF(
        CASE WHEN v_personal_score IS NOT NULL THEN 0.55 ELSE 0 END +
        CASE WHEN v_business_score IS NOT NULL THEN 0.45 ELSE 0 END,
        0
    ), 2);

    v_relationship := ROUND(v_group_score, 2);

    v_execution := ROUND((
        COALESCE(v_business_score, 0) * 0.65 +
        COALESCE(v_group_score, 0) * 0.35
    ) / NULLIF(
        CASE WHEN v_business_score IS NOT NULL THEN 0.65 ELSE 0 END +
        CASE WHEN v_group_score IS NOT NULL THEN 0.35 ELSE 0 END,
        0
    ), 2);

    v_growth := ROUND((
        COALESCE(v_personal_score, 0) * 0.50 +
        COALESCE(v_business_score, 0) * 0.50
    ) / NULLIF(
        CASE WHEN v_personal_score IS NOT NULL THEN 0.50 ELSE 0 END +
        CASE WHEN v_business_score IS NOT NULL THEN 0.50 ELSE 0 END,
        0
    ), 2);

    IF v_money IS NOT NULL THEN v_active_dims := v_active_dims + 1; END IF;
    IF v_relationship IS NOT NULL THEN v_active_dims := v_active_dims + 1; END IF;
    IF v_execution IS NOT NULL THEN v_active_dims := v_active_dims + 1; END IF;
    IF v_growth IS NOT NULL THEN v_active_dims := v_active_dims + 1; END IF;

    SELECT life_alignment_score
    INTO v_prev_alignment
    FROM life360_snapshots
    WHERE user_id = p_user_id
      AND snapshot_date < CURRENT_DATE
    ORDER BY snapshot_date DESC
    LIMIT 1;

    v_momentum := ROUND(v_alignment - COALESCE(v_prev_alignment, v_alignment), 2);

    INSERT INTO life360_snapshots (
        user_id,
        snapshot_date,
        snapshot_month,
        source_personal_snapshot_id,
        source_group_snapshot_id,
        source_business_snapshot_id,
        personal_score,
        group_score,
        business_score,
        life_alignment_score,
        life_phase,
        money_score,
        relationship_score,
        execution_score,
        growth_score,
        personal_energy_pct,
        group_energy_pct,
        business_energy_pct,
        momentum_score,
        momentum_status,
        strongest_driver,
        biggest_tension,
        money_status,
        relationship_status,
        execution_status,
        growth_status,
        reflection_summary,
        active_dimensions_count,
        signal_confidence_score,
        updated_at
    )
    VALUES (
        p_user_id,
        CURRENT_DATE,
        DATE_TRUNC('month', CURRENT_DATE)::DATE,
        v_personal_snapshot_id,
        v_group_snapshot_id,
        v_business_snapshot_id,
        v_personal_score,
        v_group_score,
        v_business_score,
        v_alignment,
        CASE
            WHEN v_alignment >= 80 THEN 'Balanced Growth'
            WHEN v_alignment >= 65 THEN 'Stable Direction'
            WHEN v_alignment >= 50 THEN 'Needs Attention'
            ELSE 'Learning Your Life'
        END,
        v_money,
        v_relationship,
        v_execution,
        v_growth,
        CASE WHEN v_personal_score IS NOT NULL THEN 32 ELSE 0 END,
        CASE WHEN v_group_score IS NOT NULL THEN 22 ELSE 0 END,
        CASE WHEN v_business_score IS NOT NULL THEN 46 ELSE 0 END,
        v_momentum,
        CASE
            WHEN v_momentum >= 5 THEN 'Improving'
            WHEN v_momentum BETWEEN -4.99 AND 4.99 THEN 'Stable'
            ELSE 'Drifting'
        END,
        CASE
            WHEN v_business_score >= GREATEST(COALESCE(v_personal_score,0), COALESCE(v_group_score,0)) THEN 'Business Execution'
            WHEN v_group_score >= GREATEST(COALESCE(v_personal_score,0), COALESCE(v_business_score,0)) THEN 'Group Participation'
            ELSE 'Personal Rhythm'
        END,
        CASE
            WHEN v_relationship IS NOT NULL AND v_execution IS NOT NULL AND v_execution - v_relationship >= 10
                THEN 'Relationships vs Execution'
            WHEN v_money IS NOT NULL AND v_growth IS NOT NULL AND v_money - v_growth >= 10
                THEN 'Money vs Growth'
            ELSE 'No major tension'
        END,
        CASE WHEN v_money IS NULL THEN NULL WHEN v_money >= 80 THEN 'Stable' WHEN v_money >= 65 THEN 'Watch' ELSE 'Needs Attention' END,
        CASE WHEN v_relationship IS NULL THEN NULL WHEN v_relationship >= 80 THEN 'Strong' WHEN v_relationship >= 65 THEN 'Stable' ELSE 'Needs Attention' END,
        CASE WHEN v_execution IS NULL THEN NULL WHEN v_execution >= 80 THEN 'Strong' WHEN v_execution >= 65 THEN 'Stable' ELSE 'Needs Attention' END,
        CASE WHEN v_growth IS NULL THEN NULL WHEN v_growth >= 80 THEN 'Rising' WHEN v_growth >= 65 THEN 'Stable' ELSE 'Needs Attention' END,
        CASE
            WHEN v_alignment >= 80 THEN
                'Your life is moving in a balanced direction. Your active moments show strong progress with manageable pressure.'
            WHEN v_alignment >= 65 THEN
                'Your life rhythm is steady. A few areas may need attention as your moments continue to evolve.'
            ELSE
                'Momentra is still learning from your active moments. Create more moments to unlock a fuller Life 360 view.'
        END,
        v_active_dims,
        ROUND((v_active_dims::NUMERIC / 4) * 100, 2),
        CURRENT_TIMESTAMP
    )
    ON CONFLICT (user_id, snapshot_date)
    DO UPDATE SET
        source_personal_snapshot_id = EXCLUDED.source_personal_snapshot_id,
        source_group_snapshot_id = EXCLUDED.source_group_snapshot_id,
        source_business_snapshot_id = EXCLUDED.source_business_snapshot_id,
        personal_score = EXCLUDED.personal_score,
        group_score = EXCLUDED.group_score,
        business_score = EXCLUDED.business_score,
        life_alignment_score = EXCLUDED.life_alignment_score,
        life_phase = EXCLUDED.life_phase,
        money_score = EXCLUDED.money_score,
        relationship_score = EXCLUDED.relationship_score,
        execution_score = EXCLUDED.execution_score,
        growth_score = EXCLUDED.growth_score,
        personal_energy_pct = EXCLUDED.personal_energy_pct,
        group_energy_pct = EXCLUDED.group_energy_pct,
        business_energy_pct = EXCLUDED.business_energy_pct,
        momentum_score = EXCLUDED.momentum_score,
        momentum_status = EXCLUDED.momentum_status,
        strongest_driver = EXCLUDED.strongest_driver,
        biggest_tension = EXCLUDED.biggest_tension,
        money_status = EXCLUDED.money_status,
        relationship_status = EXCLUDED.relationship_status,
        execution_status = EXCLUDED.execution_status,
        growth_status = EXCLUDED.growth_status,
        reflection_summary = EXCLUDED.reflection_summary,
        active_dimensions_count = EXCLUDED.active_dimensions_count,
        signal_confidence_score = EXCLUDED.signal_confidence_score,
        updated_at = CURRENT_TIMESTAMP;

END;
$$;
"""

_GROUP_ANALYTICS_FN = r"""
CREATE OR REPLACE FUNCTION sp_refresh_group_analytics(
    p_moment_id UUID
)
RETURNS VOID AS $$
DECLARE
    v_life_space UUID;
BEGIN
    PERFORM sp_refresh_group_pulse_snapshot(
        p_moment_id
    );

    PERFORM sp_refresh_group_people_impact(
        p_moment_id
    );

    PERFORM sp_refresh_group_memory_snapshot(
        p_moment_id
    );

    SELECT group_life_space_id
    INTO v_life_space
    FROM group_moments
    WHERE moment_id = p_moment_id;

    IF v_life_space IS NOT NULL THEN
        PERFORM sp_refresh_group_life_snapshot(
            v_life_space
        );

        PERFORM sp_refresh_group_life_master_snapshot(
            v_life_space
        );
    END IF;

END;
$$ LANGUAGE plpgsql;
"""


def upgrade() -> None:
    op.execute(sa.text(_LIFE360_PROC))
    op.execute(sa.text(_GROUP_ANALYTICS_FN))


def downgrade() -> None:
    pass
