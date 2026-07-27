-- DEFECT: ALTER targeted a non-existent table 'operations_budget_categories'.
-- FIX: correct the name to 'business_operations_budget_categories'.
ALTER TABLE business_operations_budget_categories
    ADD COLUMN IF NOT EXISTS alert_threshold_percent NUMERIC(5,2) DEFAULT 80
-- >>>STMT<<<
-- DEFECT: the rich second definition of group_ai_insights (with insight_layer,
-- insight_body, confidence_level, related_life_space_id, display_order, is_active,
-- created_at ...) was skipped because the minimal first definition already existed
-- (CREATE TABLE IF NOT EXISTS). Several group views need those columns.
-- FIX: additively enrich the table to the intended schema.
ALTER TABLE group_ai_insights
    ADD COLUMN IF NOT EXISTS related_life_space_id UUID,
    ADD COLUMN IF NOT EXISTS insight_layer VARCHAR(50) NOT NULL DEFAULT 'PULSE',
    ADD COLUMN IF NOT EXISTS insight_body TEXT NOT NULL DEFAULT '',
    ADD COLUMN IF NOT EXISTS confidence_level VARCHAR(30),
    ADD COLUMN IF NOT EXISTS supporting_metrics_json JSONB,
    ADD COLUMN IF NOT EXISTS display_order INTEGER,
    ADD COLUMN IF NOT EXISTS is_active BOOLEAN NOT NULL DEFAULT TRUE,
    ADD COLUMN IF NOT EXISTS created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP
-- >>>STMT<<<
DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_gai_layer_v2') THEN
    ALTER TABLE group_ai_insights ADD CONSTRAINT chk_gai_layer_v2
      CHECK (insight_layer IN ('PULSE','MOMENTS','MEMORY','LIFE'));
  END IF;
END $$
-- >>>STMT<<<
DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'chk_gai_confidence_v2') THEN
    ALTER TABLE group_ai_insights ADD CONSTRAINT chk_gai_confidence_v2
      CHECK (confidence_level IS NULL OR confidence_level IN ('LOW','MEDIUM','HIGH'));
  END IF;
END $$
-- >>>STMT<<<
DO $$ BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_gai_life_space_v2') THEN
    ALTER TABLE group_ai_insights ADD CONSTRAINT fk_gai_life_space_v2
      FOREIGN KEY (related_life_space_id) REFERENCES group_life_spaces(life_space_id);
  END IF;
END $$
-- >>>STMT<<<
-- DEFECT: business_memory_snapshots lacked success_count / wisdom_count that
-- vw_business_memory_v2 and vw_business_memory360_export select.
-- FIX: add the missing count columns (consistent with the other *_count columns).
ALTER TABLE business_memory_snapshots
    ADD COLUMN IF NOT EXISTS success_count INTEGER DEFAULT 0,
    ADD COLUMN IF NOT EXISTS wisdom_count INTEGER DEFAULT 0
-- >>>STMT<<<
-- DEFECT: two fn_validate_driver_weights() definitions with different return
-- types; the richer one (adds validation_result) could not replace the first.
-- FIX: drop then create the intended richer version.
DROP FUNCTION IF EXISTS fn_validate_driver_weights()
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_validate_driver_weights()
RETURNS TABLE (
    moment_type TEXT,
    total_weight NUMERIC,
    validation_result TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        r.moment_type::TEXT,
        SUM(r.driver_weight),
        CASE
            WHEN SUM(r.driver_weight) = 100 THEN 'PASS'
            ELSE 'FAIL'
        END
    FROM business_driver_formula_registry r
    WHERE r.active_flag = TRUE
    GROUP BY r.moment_type;
END;
$$
-- >>>STMT<<<
-- DEFECT: table-level UNIQUE(user_id, participant_name, COALESCE(...), COALESCE(...))
-- is illegal (a UNIQUE constraint cannot contain expressions).
-- FIX: create the table without that constraint and express the same rule as a
-- unique expression index (also matches the ON CONFLICT clause used by
-- sp_refresh_circle_participants).
CREATE TABLE IF NOT EXISTS circle_participants (
    circle_participant_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    participant_user_id UUID,
    participant_name VARCHAR(200) NOT NULL,
    participant_phone VARCHAR(30),
    participant_email VARCHAR(200),
    first_seen_date DATE,
    last_seen_date DATE,
    is_active BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
-- >>>STMT<<<
CREATE UNIQUE INDEX IF NOT EXISTS uq_circle_participant
    ON circle_participants (
        user_id,
        participant_name,
        COALESCE(participant_phone, ''),
        COALESCE(participant_email, '')
    )
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS circle_participant_sources (
    source_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    circle_participant_id UUID NOT NULL REFERENCES circle_participants(circle_participant_id) ON DELETE CASCADE,
    user_id UUID NOT NULL,

    source_type VARCHAR(30) NOT NULL, -- GROUP / BUSINESS
    source_moment_id UUID NOT NULL,
    source_moment_name VARCHAR(250),
    source_moment_type VARCHAR(100),

    participation_date DATE,
    is_active_source BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_circle_source UNIQUE (
        circle_participant_id,
        source_type,
        source_moment_id
    )
);
-- >>>STMT<<<
CREATE TABLE IF NOT EXISTS circle_participant_stats (
    stats_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    circle_participant_id UUID NOT NULL REFERENCES circle_participants(circle_participant_id) ON DELETE CASCADE,
    user_id UUID NOT NULL,

    shared_moment_count INTEGER DEFAULT 0,
    active_moment_count INTEGER DEFAULT 0,
    recent_activity_count INTEGER DEFAULT 0,

    participation_score NUMERIC(5,2) DEFAULT 0,
    rank_order INTEGER,

    last_activity_date DATE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_circle_stats UNIQUE (circle_participant_id)
);
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_group_memory_widgets AS
																SELECT
																    gm.moment_id,
																    gm.moment_type,
																    gm.moment_profile,
																    gm.moment_name,
																
																    ms.snapshot_date,
																    ms.memory_count,
																    ms.milestone_count,
																    ms.what_changed_json,
																    ms.budget_reflection_json,
																    ms.identity_label,
																
																    ai.insight_title AS memory_insight_title,
																    ai.insight_body AS memory_insight_body,
																    ai.confidence_level AS memory_insight_confidence
																
																FROM group_moments gm
																LEFT JOIN LATERAL (
																    SELECT *
																    FROM group_memory_snapshots ms1
																    WHERE ms1.moment_id = gm.moment_id
																    ORDER BY ms1.snapshot_date DESC, ms1.created_at DESC
																    LIMIT 1
																) ms ON TRUE
																LEFT JOIN LATERAL (
																    SELECT *
																    FROM group_ai_insights ai1
																    WHERE ai1.moment_id = gm.moment_id
																      AND ai1.insight_layer = 'MEMORY'
																      AND ai1.is_active = TRUE
																    ORDER BY ai1.display_order NULLS LAST, ai1.created_at DESC
																    LIMIT 1
																) ai ON TRUE;
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_group_life_intelligence AS
																SELECT
																    l.life_space_id,
																    l.life_snapshot_id,
																    ai.insight_id,
																    ai.insight_title,
																    ai.insight_body,
																    ai.confidence_level,
																    ai.supporting_metrics_json,
																    ai.display_order,
																    ai.created_at
																FROM vw_group_life_latest l
																JOIN group_ai_insights ai
																    ON ai.related_life_space_id = l.life_space_id
																WHERE ai.insight_layer = 'LIFE'
																  AND ai.is_active = TRUE;
-- >>>STMT<<<
-- DEFECT: two vw_business_pulse definitions with incompatible column shapes
-- (pulse_status vs health_score/health_status/health_reason). The later,
-- health-column version is the intended one and matches the ALTERed table.
-- FIX: drop the stale view and create the intended definition.
DROP VIEW IF EXISTS vw_business_pulse
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_business_pulse AS
SELECT
    bm.moment_id,
    bm.moment_name,
    bm.moment_type,
    bm.status,
    bps.snapshot_date,
    bps.activities_count,
    bps.completed_activities,
    bps.in_progress_activities,
    bps.planned_activities,
    bps.pending_approvals,
    bps.open_risks,
    bps.critical_risks,
    bps.monthly_spend,
    bps.top_spend_category,
    bps.health_score,
    bps.health_status,
    bps.health_reason,
    bps.generated_at
FROM business_moments bm
JOIN business_pulse_snapshots bps
    ON bm.moment_id = bps.moment_id
WHERE bm.status = 'active'
-- >>>STMT<<<
-- DEFECT: referenced snap.budget_used_total / snap.budget_remaining_total which
-- do not exist on business_operations_snapshots (columns are budget_used /
-- budget_remaining).
-- FIX: read the real columns and keep the original output column names via alias.
CREATE OR REPLACE VIEW vw_business_operations_pulse AS
SELECT
    bm.moment_id,
    bm.moment_name,
    bos.operations_type,
    bos.operating_currency,
    snap.operations_health_status,
    snap.active_issue_count,
    snap.open_approval_count,
    snap.budget_alert_count,
    snap.improvement_count,
    snap.budget_used AS budget_used_total,
    snap.budget_remaining AS budget_remaining_total,
    snap.vendor_activity_count,
    snap.generated_at
FROM business_moments bm
JOIN business_operations_setup bos
    ON bos.moment_id = bm.moment_id
JOIN business_operations_snapshots snap
    ON snap.moment_id = bm.moment_id
WHERE snap.snapshot_date = CURRENT_DATE
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_business_operations_dashboard AS
																SELECT
																
																    p.moment_id,
																
																    p.moment_name,
																
																    p.operations_type,
																
																    p.operations_health_status,
																
																    p.active_issue_count,
																
																    p.open_approval_count,
																
																    p.budget_alert_count,
																
																    p.improvement_count,
																
																    p.budget_used_total,
																
																    p.budget_remaining_total,
																
																    p.vendor_activity_count,
																
																    m.latest_spend_title,
																
																    m.latest_issue_title,
																
																    m.latest_approval_status,
																
																    m.latest_improvement_title,
																
																    m.last_operations_activity_at
																
																FROM vw_business_operations_pulse p
																
																LEFT JOIN vw_business_operations_moments m
																    ON m.moment_id = p.moment_id;
-- >>>STMT<<<
-- DEFECT: referenced lf.live_feed_id; the business_live_feed PK is feed_id.
-- FIX: select feed_id and alias it to the original output name.
CREATE OR REPLACE VIEW vw_business_operations_live AS
SELECT
    lf.feed_id AS live_feed_id,
    lf.moment_id,
    lf.source_table,
    lf.source_record_id,
    lf.event_type,
    lf.actor_name,
    lf.headline,
    lf.detail_message,
    lf.visibility,
    lf.event_timestamp
FROM business_live_feed lf
WHERE lf.source_table IN (
    'operations_spend_entries',
    'operations_vendor_updates',
    'operations_approval_requests',
    'operations_issues',
    'operations_improvements'
)
-- >>>STMT<<<
-- DEFECT: the spend branch referenced budget_category_name which does not exist
-- on operations_spend_entries.
-- FIX: use spend_category (consistent with the other UNION branches' category).
CREATE OR REPLACE VIEW vw_business_operations_transaction_detail AS
SELECT
    moment_id,
    spend_entry_id AS record_id,
    'Spend Entry' AS transaction_type,
    spend_name AS title,
    spend_category AS category,
    amount_in_operating_currency AS amount,
    approval_status AS status,
    created_at
FROM operations_spend_entries
WHERE archived_at IS NULL
UNION ALL
SELECT
    moment_id, vendor_update_id, 'Vendor Update', vendor_name, vendor_category,
    NULL, vendor_status, created_at
FROM operations_vendor_updates
WHERE archived_at IS NULL
UNION ALL
SELECT
    moment_id, operations_approval_id, 'Approval Request', request_title, request_type,
    amount, approval_status, created_at
FROM operations_approval_requests
WHERE archived_at IS NULL
UNION ALL
SELECT
    moment_id, operations_issue_id, 'Issue / Risk', issue_title, issue_category,
    NULL, issue_status, created_at
FROM operations_issues
WHERE archived_at IS NULL
UNION ALL
SELECT
    moment_id, improvement_id, 'Operational Improvement', improvement_title, improvement_type,
    NULL, improvement_status, created_at
FROM operations_improvements
WHERE archived_at IS NULL
-- >>>STMT<<<
-- DEFECT: referenced created_at; business_orchestration_jobs uses queued_at.
-- FIX: aggregate over queued_at.
CREATE OR REPLACE VIEW vw_business_orchestration_health AS
SELECT
    job_type,
    job_status,
    COUNT(*) AS total_jobs,
    MAX(queued_at) AS latest_job,
    MAX(completed_at) AS latest_completion
FROM business_orchestration_jobs
GROUP BY job_type, job_status
-- >>>STMT<<<
-- DEFECT: same created_at issue as vw_business_orchestration_health.
CREATE OR REPLACE VIEW vw_business_orchestration_health_v2 AS
SELECT
    job_type,
    job_status,
    COUNT(*) total_jobs,
    MAX(queued_at) latest_job,
    MAX(completed_at) latest_completion
FROM business_orchestration_jobs
GROUP BY job_type, job_status
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_business_memory_v2 AS
SELECT

    bms.workspace_id,

    bms.memory_score,
    bms.memory_status,

    bms.learning_count,
    bms.playbook_count,
    bms.risk_count,
    bms.success_count,
    bms.wisdom_count,

    bms.strongest_learning_id,
    bms.strongest_wisdom_id,

    bms.memory_score_delta,

    bms.generated_at

FROM business_memory_snapshots bms;
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_business_memory360_export AS
SELECT

    workspace_id,

    memory_score,

    learning_count,

    playbook_count,

    risk_count,

    success_count,

    wisdom_count,

    generated_at

FROM business_memory_snapshots;
-- >>>STMT<<<
-- DEFECT: unqualified workspace_id was ambiguous (present on both joined tables).
-- FIX: qualify every referenced column.
CREATE OR REPLACE VIEW vw_business_experience_health AS
SELECT
    bls.workspace_id,
    (
        COALESCE(bls.life_score,0) * 0.40 +
        COALESCE(bms.memory_score,0) * 0.30 +
        COALESCE(bls.active_moment_count,0) * 3
    ) AS experience_health_score
FROM business_life_snapshots bls
LEFT JOIN business_memory_snapshots bms
    ON bls.workspace_id = bms.workspace_id
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_circle_home_state AS
SELECT
    u.user_id,
    COUNT(cp.circle_participant_id) AS participant_count,
    CASE
        WHEN COUNT(cp.circle_participant_id) = 0 THEN 'EMPTY'
        ELSE 'FULL'
    END AS circle_state
FROM users u
LEFT JOIN circle_participants cp
    ON cp.user_id = u.user_id
GROUP BY u.user_id;
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_circle_home AS
SELECT
    cp.user_id,
    COUNT(cp.circle_participant_id) AS total_participants,
    COUNT(cp.circle_participant_id) FILTER (WHERE cp.is_active = TRUE) AS active_participants,
    COUNT(cp.circle_participant_id) FILTER (WHERE cp.last_seen_date >= CURRENT_DATE - INTERVAL '30 days') AS recent_participants
FROM circle_participants cp
GROUP BY cp.user_id;
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_circle_participants_filtered AS
SELECT
    cp.user_id,
    cp.circle_participant_id,
    cp.participant_user_id,
    cp.participant_name,
    cp.participant_phone,
    cp.participant_email,
    cp.first_seen_date,
    cp.last_seen_date,
    cp.is_active,

    COALESCE(cps.shared_moment_count, 0) AS shared_moment_count,
    COALESCE(cps.active_moment_count, 0) AS active_moment_count,
    COALESCE(cps.recent_activity_count, 0) AS recent_activity_count,
    COALESCE(cps.participation_score, 0) AS participation_score,
    COALESCE(cps.rank_order, 9999) AS rank_order,

    EXISTS (
        SELECT 1
        FROM circle_participant_sources s
        WHERE s.circle_participant_id = cp.circle_participant_id
          AND s.source_type = 'GROUP'
    ) AS is_group_participant,

    EXISTS (
        SELECT 1
        FROM circle_participant_sources s
        WHERE s.circle_participant_id = cp.circle_participant_id
          AND s.source_type = 'BUSINESS'
    ) AS is_business_participant

FROM circle_participants cp
LEFT JOIN circle_participant_stats cps
    ON cps.circle_participant_id = cp.circle_participant_id;
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_circle_recent_activity AS
SELECT
    cps.user_id,
    cps.source_type,
    cps.source_moment_id,
    cps.source_moment_name,
    cps.source_moment_type,
    COUNT(DISTINCT cps.circle_participant_id) AS participant_count,
    MAX(cps.participation_date) AS last_activity_date
FROM circle_participant_sources cps
GROUP BY
    cps.user_id,
    cps.source_type,
    cps.source_moment_id,
    cps.source_moment_name,
    cps.source_moment_type;
