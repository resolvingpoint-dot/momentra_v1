"""Harden personal life aggregate snapshot + bootstrap for Life360.

``sp_refresh_personal_life_snapshot`` inserted NULL life_health / dimension
scores when upstream health/dimension rows were missing, violating NOT NULL
columns. Life360 then rolled up with confidence 0 and stayed EMPTY despite
active personal moments.

This revision:
- COALESCE required numerics (and compute life_health from pillars when missing)
- Early-return when the user has no personal moments
- Leaves call-order fixes to Python (health → dimensions → aggregate → Life360)

Revision ID: mom_33_harden_personal_life_snap
Revises: mom_32_fix_life360_snapshots
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "mom_33_harden_personal_life_snap"
down_revision: Union[str, Sequence[str], None] = "mom_32_fix_life360_snapshots"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_PERSONAL_LIFE_SNAPSHOT_PROC = r"""
CREATE OR REPLACE PROCEDURE sp_refresh_personal_life_snapshot(
    p_user_id UUID
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_life_health DECIMAL(5,2);
    v_stress DECIMAL(5,2);
    v_capacity DECIMAL(5,2);
    v_growth_dimension DECIMAL(5,2);
    v_fulfillment_dimension DECIMAL(5,2);
    v_stability DECIMAL(5,2);
    v_growth DECIMAL(5,2);
    v_fulfillment DECIMAL(5,2);
    v_relationship DECIMAL(5,2);
    v_dominant_emotion VARCHAR(50);
    v_dominant_emotion_pct DECIMAL(5,2);
    v_drift_score DECIMAL(5,2);
    v_drift_status VARCHAR(50);
    v_happiness_driver VARCHAR(100);
    v_happiness_driver_score DECIMAL(8,2);
    v_leverage_area VARCHAR(100);
    v_leverage_score DECIMAL(8,2);
    v_life_stage VARCHAR(100);
    v_life_summary TEXT;
    v_moment_count INTEGER;
BEGIN
    SELECT COUNT(*)
    INTO v_moment_count
    FROM personal_moments
    WHERE user_id = p_user_id;

    IF v_moment_count = 0 THEN
        RETURN;
    END IF;

    SELECT life_health_score
    INTO v_life_health
    FROM personal_life_health_snapshots
    WHERE user_id = p_user_id
      AND is_current = TRUE
    ORDER BY created_at DESC
    LIMIT 1;

    SELECT dimension_score
    INTO v_stress
    FROM personal_life_dimension_scores
    WHERE user_id = p_user_id
      AND dimension_code = 'STRESS'
      AND is_current = TRUE
    ORDER BY created_at DESC
    LIMIT 1;

    SELECT dimension_score
    INTO v_capacity
    FROM personal_life_dimension_scores
    WHERE user_id = p_user_id
      AND dimension_code = 'CAPACITY'
      AND is_current = TRUE
    ORDER BY created_at DESC
    LIMIT 1;

    SELECT dimension_score
    INTO v_growth_dimension
    FROM personal_life_dimension_scores
    WHERE user_id = p_user_id
      AND dimension_code = 'GROWTH'
      AND is_current = TRUE
    ORDER BY created_at DESC
    LIMIT 1;

    SELECT dimension_score
    INTO v_fulfillment_dimension
    FROM personal_life_dimension_scores
    WHERE user_id = p_user_id
      AND dimension_code = 'FULFILLMENT'
      AND is_current = TRUE
    ORDER BY created_at DESC
    LIMIT 1;

    SELECT COALESCE(AVG(primary_score), 70)
    INTO v_stability
    FROM personal_runtime_snapshots prs
    JOIN personal_moments pm ON pm.moment_id = prs.moment_id
    JOIN personal_moment_types mt ON mt.moment_type_id = pm.moment_type_id
    WHERE pm.user_id = p_user_id
      AND mt.moment_type_code = 'LIFE_OPERATIONS';

    SELECT COALESCE(AVG(primary_score), 70)
    INTO v_growth
    FROM personal_runtime_snapshots prs
    JOIN personal_moments pm ON pm.moment_id = prs.moment_id
    JOIN personal_moment_types mt ON mt.moment_type_id = pm.moment_type_id
    WHERE pm.user_id = p_user_id
      AND mt.moment_type_code = 'FUTURE_BUILDING';

    SELECT COALESCE(AVG(primary_score), 70)
    INTO v_fulfillment
    FROM personal_runtime_snapshots prs
    JOIN personal_moments pm ON pm.moment_id = prs.moment_id
    JOIN personal_moment_types mt ON mt.moment_type_id = pm.moment_type_id
    WHERE pm.user_id = p_user_id
      AND mt.moment_type_code = 'LIFESTYLE';

    SELECT COALESCE(AVG(primary_score), 70)
    INTO v_relationship
    FROM personal_runtime_snapshots prs
    JOIN personal_moments pm ON pm.moment_id = prs.moment_id
    JOIN personal_moment_types mt ON mt.moment_type_id = pm.moment_type_id
    WHERE pm.user_id = p_user_id
      AND mt.moment_type_code = 'RELATIONSHIPS';

    v_stability := COALESCE(v_stability, 70);
    v_growth := COALESCE(v_growth, 70);
    v_fulfillment := COALESCE(v_fulfillment, 70);
    v_relationship := COALESCE(v_relationship, 70);

    v_life_health := COALESCE(
        v_life_health,
        fn_personal_life_health_score(
            v_stability,
            v_growth,
            v_fulfillment,
            v_relationship
        ),
        70
    );

    v_stress := COALESCE(v_stress, 50);
    v_capacity := COALESCE(v_capacity, 50);
    v_growth_dimension := COALESCE(v_growth_dimension, 50);
    v_fulfillment_dimension := COALESCE(v_fulfillment_dimension, 50);

    SELECT emotion_name, emotion_pct
    INTO v_dominant_emotion, v_dominant_emotion_pct
    FROM personal_memory_emotional_dna
    WHERE user_id = p_user_id
      AND is_current = TRUE
    ORDER BY emotion_pct DESC
    LIMIT 1;

    v_drift_score := fn_personal_life_drift_score(
        v_stability,
        v_growth,
        v_fulfillment,
        v_relationship
    );

    v_drift_status := fn_personal_life_drift_status(v_drift_score);

    SELECT driver_name, COALESCE(impact_pct, 0)
    INTO v_happiness_driver, v_happiness_driver_score
    FROM personal_memory_driver_rankings
    WHERE user_id = p_user_id
      AND driver_category IN (
          'FULFILLMENT_DRIVER',
          'POSITIVE',
          'HIGHEST_RETURN'
      )
      AND is_current = TRUE
    ORDER BY impact_pct DESC
    LIMIT 1;

    SELECT current_stage
    INTO v_life_stage
    FROM personal_memory_evolution_snapshots
    WHERE user_id = p_user_id
      AND is_current = TRUE
    ORDER BY created_at DESC
    LIMIT 1;

    IF v_stability <= v_growth
       AND v_stability <= v_fulfillment
       AND v_stability <= v_relationship THEN
        v_leverage_area := 'Life Operations';
        v_leverage_score := 100 - v_stability;
    ELSIF v_growth <= v_fulfillment
       AND v_growth <= v_relationship THEN
        v_leverage_area := 'Future Building';
        v_leverage_score := 100 - v_growth;
    ELSIF v_fulfillment <= v_relationship THEN
        v_leverage_area := 'Lifestyle';
        v_leverage_score := 100 - v_fulfillment;
    ELSE
        v_leverage_area := 'Relationships';
        v_leverage_score := 100 - v_relationship;
    END IF;

    v_life_summary := CONCAT(
        'Life Health: ',
        ROUND(v_life_health, 0),
        '. Dominant Emotion: ',
        COALESCE(v_dominant_emotion, 'Balanced'),
        '. Strongest Driver: ',
        COALESCE(v_happiness_driver, 'Growth'),
        '. Highest Leverage Area: ',
        COALESCE(v_leverage_area, 'Life Operations'),
        '.'
    );

    UPDATE personal_life_aggregate_snapshots
    SET
        is_current = FALSE,
        updated_at = CURRENT_TIMESTAMP
    WHERE user_id = p_user_id
      AND is_current = TRUE;

    INSERT INTO personal_life_aggregate_snapshots
    (
        user_id,
        snapshot_date,
        snapshot_month,
        life_health_score,
        stability_score,
        growth_score,
        fulfillment_score,
        relationship_health_score,
        stress_score,
        capacity_score,
        growth_dimension_score,
        fulfillment_dimension_score,
        dominant_emotion,
        dominant_emotion_pct,
        emotional_momentum_score,
        drift_score,
        drift_status,
        leverage_score,
        leverage_area,
        happiness_driver,
        happiness_driver_score,
        life_stage,
        life_intelligence_summary,
        is_current
    )
    VALUES
    (
        p_user_id,
        CURRENT_DATE,
        DATE_TRUNC('month', CURRENT_DATE)::DATE,
        v_life_health,
        v_stability,
        v_growth,
        v_fulfillment,
        v_relationship,
        v_stress,
        v_capacity,
        v_growth_dimension,
        v_fulfillment_dimension,
        v_dominant_emotion,
        v_dominant_emotion_pct,
        0,
        v_drift_score,
        v_drift_status,
        v_leverage_score,
        v_leverage_area,
        v_happiness_driver,
        v_happiness_driver_score,
        v_life_stage,
        v_life_summary,
        TRUE
    );

END;
$$;
"""


def upgrade() -> None:
    op.execute(sa.text(_PERSONAL_LIFE_SNAPSHOT_PROC))


def downgrade() -> None:
    pass
