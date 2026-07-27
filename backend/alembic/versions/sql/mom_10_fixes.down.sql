DROP VIEW IF EXISTS vw_group_memory_widgets CASCADE
-- >>>STMT<<<
DROP VIEW IF EXISTS vw_group_life_intelligence CASCADE
-- >>>STMT<<<
DROP VIEW IF EXISTS vw_business_memory_v2 CASCADE
-- >>>STMT<<<
DROP VIEW IF EXISTS vw_business_memory360_export CASCADE
-- >>>STMT<<<
DROP TABLE IF EXISTS circle_participant_stats CASCADE
-- >>>STMT<<<
DROP TABLE IF EXISTS circle_participant_sources CASCADE
-- >>>STMT<<<
DROP TABLE IF EXISTS circle_participants CASCADE
-- >>>STMT<<<
ALTER TABLE group_ai_insights DROP CONSTRAINT IF EXISTS fk_gai_life_space_v2
-- >>>STMT<<<
ALTER TABLE group_ai_insights DROP CONSTRAINT IF EXISTS chk_gai_confidence_v2
-- >>>STMT<<<
ALTER TABLE group_ai_insights DROP CONSTRAINT IF EXISTS chk_gai_layer_v2
-- >>>STMT<<<
ALTER TABLE group_ai_insights
    DROP COLUMN IF EXISTS related_life_space_id,
    DROP COLUMN IF EXISTS insight_layer,
    DROP COLUMN IF EXISTS insight_body,
    DROP COLUMN IF EXISTS confidence_level,
    DROP COLUMN IF EXISTS supporting_metrics_json,
    DROP COLUMN IF EXISTS display_order,
    DROP COLUMN IF EXISTS is_active,
    DROP COLUMN IF EXISTS created_at,
    DROP COLUMN IF EXISTS updated_at
-- >>>STMT<<<
ALTER TABLE business_memory_snapshots
    DROP COLUMN IF EXISTS success_count,
    DROP COLUMN IF EXISTS wisdom_count
-- >>>STMT<<<
ALTER TABLE business_operations_budget_categories DROP COLUMN IF EXISTS alert_threshold_percent
-- >>>STMT<<<
DROP FUNCTION IF EXISTS fn_validate_driver_weights()
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_validate_driver_weights()
RETURNS TABLE(
    moment_type TEXT,
    total_weight NUMERIC
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        b.moment_type::TEXT,
        SUM(b.driver_weight)
    FROM business_driver_formula_registry b
    GROUP BY b.moment_type;
END;
$$
