CREATE OR REPLACE VIEW vw_personal_moment_dashboard AS
SELECT
    pm.moment_id,
    pm.user_id,
    mt.moment_type_code,
    mt.moment_type_name,
    pm.moment_name,
    pm.status,
    pm.current_identity_label,
    pm.current_state_label,
    rs.runtime_state_label,
    rs.primary_score AS runtime_score,
    ps.pulse_title,
    ps.primary_metric_label,
    ps.primary_metric_value,
    lp.priority_title,
    lp.recommended_action_label,
    COUNT(DISTINCT mp.memory_pattern_id) AS active_memory_patterns,
    COUNT(DISTINCT s.signal_id) AS active_signals,
    COUNT(DISTINCT r.recommendation_id) AS active_recommendations,
    pm.last_activity_at,
    pm.created_at,
    pm.updated_at
FROM personal_moments pm
JOIN personal_moment_types mt
    ON mt.moment_type_id = pm.moment_type_id
LEFT JOIN personal_runtime_snapshots rs
    ON rs.moment_id = pm.moment_id
LEFT JOIN personal_pulse_snapshots ps
    ON ps.moment_id = pm.moment_id
LEFT JOIN personal_live_priorities lp
    ON lp.moment_id = pm.moment_id
   AND lp.is_current = TRUE
LEFT JOIN personal_memory_patterns mp
    ON mp.moment_id = pm.moment_id
   AND mp.is_active = TRUE
LEFT JOIN personal_signals s
    ON s.moment_id = pm.moment_id
   AND s.is_active = TRUE
LEFT JOIN personal_recommendations r
    ON r.moment_id = pm.moment_id
   AND r.status = 'ACTIVE'
GROUP BY
    pm.moment_id,
    pm.user_id,
    mt.moment_type_code,
    mt.moment_type_name,
    pm.moment_name,
    pm.status,
    pm.current_identity_label,
    pm.current_state_label,
    rs.runtime_state_label,
    rs.primary_score,
    ps.pulse_title,
    ps.primary_metric_label,
    ps.primary_metric_value,
    lp.priority_title,
    lp.recommended_action_label,
    pm.last_activity_at,
    pm.created_at,
    pm.updated_at;
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_personal_moment_journey AS
																SELECT
																    t.user_id,
																    t.moment_id,
																    t.moment_type_code,
																    t.event_occurred_at AS event_date,
																    t.display_title AS event_title,
																    t.display_amount AS amount,
																    NULL::DECIMAL(5,2) AS mood_delta,
																    NULL::DECIMAL(5,2) AS outcome_score
																FROM personal_activity_timeline t
																JOIN personal_moments m
																  ON m.moment_id = t.moment_id
																WHERE t.is_voided = FALSE;
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_personal_events AS
SELECT
    t.user_id,
    t.moment_id,
    t.moment_type_code,
    t.event_type,
    t.display_title AS event_title,
    t.display_amount AS amount,
    t.event_occurred_at AS event_date,
    NULL::DECIMAL(5,2) AS mood_delta,
    NULL::DECIMAL(5,2) AS outcome_score,
    NULL::DECIMAL(5,2) AS financial_weight_score,
    NULL::DECIMAL(5,2) AS behavior_shift_score,
    NULL::DECIMAL(5,2) AS duration_score
FROM personal_activity_timeline t
WHERE t.is_voided = FALSE;
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_group_quick_add_options AS
																SELECT
																    q.config_id,
																    q.moment_type,
																    q.moment_profile,
																    q.module_code,
																    q.module_label,
																    q.display_order,
																    q.is_enabled,
																    q.is_visible
																FROM group_quick_add_config q
																WHERE q.is_enabled = TRUE
																  AND q.is_visible = TRUE;
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_group_field_values AS
																SELECT
																    config_value_id,
																    moment_type,
																    moment_profile,
																    module_code,
																    field_name,
																    value_code,
																    value_label,
																    display_order,
																    is_top_category,
																    is_active
																FROM group_field_value_config
																WHERE is_active = TRUE;
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_group_live AS
																SELECT
																    lf.feed_id,
																    lf.moment_id,
																    gm.moment_type,
																    gm.moment_profile,
																    gm.moment_name,
																    gm.stage,
																    gm.status,
																    lf.event_id,
																    qe.module_code,
																    qe.event_ref_table,
																    qe.event_ref_id,
																    lf.feed_category,
																    lf.title,
																    lf.summary,
																    lf.can_view,
																    lf.can_edit,
																    lf.visibility,
																    lf.created_at
																FROM group_live_feed lf
																JOIN group_moments gm
																    ON gm.moment_id = lf.moment_id
																JOIN group_quick_add_events qe
																    ON qe.event_id = lf.event_id
																WHERE lf.is_hidden = FALSE;
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_group_pulse AS
																SELECT
																    gm.moment_id,
																    gm.moment_type,
																    gm.moment_profile,
																    gm.moment_name,
																    gm.stage,
																    gm.status,
																
																    hs.health_score,
																    hs.health_status,
																    hs.people_score,
																    hs.money_score,
																    hs.activity_score,
																
																    ps.completion_percentage,
																    ps.participation_percentage,
																    ps.funding_percentage,
																    ps.active_members,
																    ps.active_tasks,
																    ps.open_items,
																    ps.pulse_score,
																
																    ps.snapshot_date
																FROM group_moments gm
																LEFT JOIN LATERAL (
																    SELECT *
																    FROM group_health_snapshots hs1
																    WHERE hs1.moment_id = gm.moment_id
																    ORDER BY hs1.snapshot_date DESC, hs1.created_at DESC
																    LIMIT 1
																) hs ON TRUE
																LEFT JOIN LATERAL (
																    SELECT *
																    FROM group_pulse_snapshots ps1
																    WHERE ps1.moment_id = gm.moment_id
																    ORDER BY ps1.snapshot_date DESC, ps1.created_at DESC
																    LIMIT 1
																) ps ON TRUE;
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_group_moments AS
																SELECT
																    gm.moment_id,
																    gm.moment_type,
																    gm.moment_profile,
																    gm.moment_name,
																    gm.stage,
																    gm.status,
																    gm.currency_code,
																    gm.created_by,
																    gm.created_at,
																    gm.activated_at,
																
																    COUNT(DISTINCT gmm.member_id) FILTER (
																        WHERE gmm.status IN ('ACTIVE','CONFIRMED')
																    ) AS active_member_count,
																
																    COUNT(DISTINCT qe.event_id) AS total_activity_count,
																
																    COUNT(DISTINCT gp.poll_id) FILTER (
																        WHERE gp.status = 'OPEN'
																    ) AS open_poll_count,
																
																    COUNT(DISTINCT gme.memory_id) AS memory_count
																FROM group_moments gm
																LEFT JOIN group_moment_members gmm
																    ON gmm.moment_id = gm.moment_id
																LEFT JOIN group_quick_add_events qe
																    ON qe.moment_id = gm.moment_id
																LEFT JOIN group_polls gp
																    ON gp.moment_id = gm.moment_id
																LEFT JOIN group_memory_entries gme
																    ON gme.moment_id = gm.moment_id
																GROUP BY
																    gm.moment_id,
																    gm.moment_type,
																    gm.moment_profile,
																    gm.moment_name,
																    gm.stage,
																    gm.status,
																    gm.currency_code,
																    gm.created_by,
																    gm.created_at,
																    gm.activated_at;
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_group_memory AS
																SELECT
																    gm.moment_id,
																    gm.moment_type,
																    gm.moment_profile,
																    gm.moment_name,
																
																    me.memory_id,
																    me.memory_type,
																    me.category,
																    me.title,
																    me.description,
																    me.memory_date,
																    me.created_at,
																
																    mp.pattern_id,
																    mp.pattern_type,
																    mp.pattern_category,
																    mp.insight_title,
																    mp.insight_text,
																    mp.confidence_score
																FROM group_moments gm
																LEFT JOIN group_memory_entries me
																    ON me.moment_id = gm.moment_id
																LEFT JOIN group_memory_patterns mp
																    ON mp.moment_id = gm.moment_id
																   AND mp.status = 'ACTIVE';
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_shared_experience_state AS
																SELECT
																    gm.moment_id,
																    gm.moment_name,
																    gm.stage,
																    sed.experience_profile,
																    sed.location,
																    sed.start_date,
																    sed.end_date,
																    sed.expected_participants,
																
																    COUNT(DISTINCT gmm.member_id) FILTER (
																        WHERE gmm.status IN ('ACTIVE','CONFIRMED')
																    ) AS joined_participants,
																
																    COUNT(DISTINCT sepi.item_id) AS planning_items,
																    COUNT(DISTINCT ge.expense_id) AS expense_count,
																    COALESCE(SUM(ge.amount),0) AS total_expenses,
																    COUNT(DISTINCT gp.poll_id) FILTER (WHERE gp.status = 'OPEN') AS open_polls,
																    COUNT(DISTINCT gme.memory_id) AS memories
																FROM group_moments gm
																JOIN shared_experience_details sed
																    ON sed.moment_id = gm.moment_id
																LEFT JOIN group_moment_members gmm
																    ON gmm.moment_id = gm.moment_id
																LEFT JOIN shared_experience_planning_items sepi
																    ON sepi.moment_id = gm.moment_id
																LEFT JOIN group_expenses ge
																    ON ge.moment_id = gm.moment_id
																LEFT JOIN group_polls gp
																    ON gp.moment_id = gm.moment_id
																LEFT JOIN group_memory_entries gme
																    ON gme.moment_id = gm.moment_id
																GROUP BY
																    gm.moment_id,
																    gm.moment_name,
																    gm.stage,
																    sed.experience_profile,
																    sed.location,
																    sed.start_date,
																    sed.end_date,
																    sed.expected_participants;
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_shared_purchase_state AS
																SELECT
																    gm.moment_id,
																    gm.moment_name,
																    gm.stage,
																    spd.purchase_type,
																    spd.target_amount,
																    spd.target_date,
																    spd.funding_style,
																
																    COUNT(DISTINCT spc.contributor_id) AS contributors,
																    COALESCE(SUM(gc.amount) FILTER (WHERE gc.status = 'RECEIVED'),0) AS collected_amount,
																    COUNT(DISTINCT spi.item_id) AS purchase_items,
																    COUNT(DISTINCT spv.vendor_id) AS vendors,
																    COUNT(DISTINCT spo.ownership_id) AS ownership_records,
																    COUNT(DISTINCT spdel.delivery_id) AS delivery_records,
																    COUNT(DISTINCT gp.poll_id) FILTER (WHERE gp.status = 'OPEN') AS open_polls
																FROM group_moments gm
																JOIN shared_purchase_details spd
																    ON spd.moment_id = gm.moment_id
																LEFT JOIN shared_purchase_contributors spc
																    ON spc.moment_id = gm.moment_id
																LEFT JOIN group_contributions gc
																    ON gc.moment_id = gm.moment_id
																LEFT JOIN shared_purchase_items spi
																    ON spi.moment_id = gm.moment_id
																LEFT JOIN shared_purchase_vendors spv
																    ON spv.moment_id = gm.moment_id
																LEFT JOIN shared_purchase_ownership spo
																    ON spo.moment_id = gm.moment_id
																LEFT JOIN shared_purchase_delivery spdel
																    ON spdel.moment_id = gm.moment_id
																LEFT JOIN group_polls gp
																    ON gp.moment_id = gm.moment_id
																GROUP BY
																    gm.moment_id,
																    gm.moment_name,
																    gm.stage,
																    spd.purchase_type,
																    spd.target_amount,
																    spd.target_date,
																    spd.funding_style;
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_shared_living_state AS
																SELECT
																    gm.moment_id,
																    gm.moment_name,
																    gm.stage,
																    sld.living_type,
																    sld.living_name,
																    sld.move_in_date,
																    sld.monthly_budget,
																    sld.management_style,
																
																    COUNT(DISTINCT slr.resident_id) FILTER (
																        WHERE slr.status = 'ACTIVE'
																    ) AS active_residents,
																
																    COALESCE(SUM(ge.amount),0) AS monthly_expenses,
																
																    COALESCE(SUM(gc.amount) FILTER (
																        WHERE gc.status = 'RECEIVED'
																    ),0) AS contributions_received,
																
																    COUNT(DISTINCT slt.task_id) FILTER (
																        WHERE slt.status IN ('TO_DO','IN_PROGRESS','OVERDUE')
																    ) AS open_tasks,
																
																    COUNT(DISTINCT sla.asset_id) AS assets,
																    COUNT(DISTINCT slrule.rule_id) FILTER (
																        WHERE slrule.status = 'ACTIVE'
																    ) AS active_rules,
																
																    COUNT(DISTINCT slm.maintenance_id) FILTER (
																        WHERE slm.status IN ('REPORTED','IN_PROGRESS')
																    ) AS open_maintenance,
																
																    COUNT(DISTINCT gme.memory_id) AS memories
																FROM group_moments gm
																JOIN shared_living_details sld
																    ON sld.moment_id = gm.moment_id
																LEFT JOIN shared_living_residents slr
																    ON slr.moment_id = gm.moment_id
																LEFT JOIN group_expenses ge
																    ON ge.moment_id = gm.moment_id
																LEFT JOIN group_contributions gc
																    ON gc.moment_id = gm.moment_id
																LEFT JOIN shared_living_tasks slt
																    ON slt.moment_id = gm.moment_id
																LEFT JOIN shared_living_assets sla
																    ON sla.moment_id = gm.moment_id
																LEFT JOIN shared_living_rules slrule
																    ON slrule.moment_id = gm.moment_id
																LEFT JOIN shared_living_maintenance slm
																    ON slm.moment_id = gm.moment_id
																LEFT JOIN group_memory_entries gme
																    ON gme.moment_id = gm.moment_id
																GROUP BY
																    gm.moment_id,
																    gm.moment_name,
																    gm.stage,
																    sld.living_type,
																    sld.living_name,
																    sld.move_in_date,
																    sld.monthly_budget,
																    sld.management_style;
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_shared_experience_budget AS
																SELECT
																    bp.budget_plan_id,
																    bp.moment_id,
																    gm.moment_name,
																    gm.experience_subtype,
																    gm.planning_mode,
																    bp.planned_total_budget,
																    bp.final_total_budget,
																    bp.participant_count,
																    bp.split_method,
																    bp.funding_readiness_pct,
																    bp.status AS budget_status,
																    fn_shared_experience_budget_health_score(bp.budget_plan_id) AS budget_health_score,
																    fn_shared_experience_budget_snapshot_json(bp.moment_id) AS budget_snapshot_json,
																    fn_shared_experience_budget_reflection_json(bp.moment_id) AS budget_reflection_json,
																    bp.created_at,
																    bp.updated_at
																FROM shared_experience_budget_plans bp
																JOIN group_moments gm
																    ON gm.moment_id = bp.moment_id;
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_shared_experience_budget_allocations AS
																SELECT
																    a.allocation_id,
																    a.budget_plan_id,
																    bp.moment_id,
																    c.category_code,
																    c.category_name,
																    c.icon_name,
																    a.recommended_percentage,
																    a.recommended_amount,
																    a.final_percentage,
																    a.final_amount,
																    a.actual_amount,
																    a.variance_amount,
																    a.notes
																FROM shared_experience_budget_allocations a
																JOIN shared_experience_budget_plans bp
																    ON bp.budget_plan_id = a.budget_plan_id
																JOIN budget_master_categories c
																    ON c.category_id = a.category_id;
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_shared_experience_budget_splits AS
																SELECT
																    s.split_id,
																    s.budget_plan_id,
																    bp.moment_id,
																    s.member_id,
																    m.display_name,
																    s.planned_share_amount,
																    s.committed_amount,
																    s.paid_amount,
																    s.pending_amount,
																    s.split_status
																FROM shared_experience_budget_splits s
																JOIN shared_experience_budget_plans bp
																    ON bp.budget_plan_id = s.budget_plan_id
																JOIN group_moment_members m
																    ON m.member_id = s.member_id;
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_group_pulse_widgets AS
																SELECT
																    gm.moment_id,
																    gm.moment_type,
																    gm.moment_profile,
																    gm.moment_name,
																    gm.stage,
																    gm.status,
																    gm.experience_subtype,
																    gm.planning_mode,
																    gm.activation_status,
																
																    ps.snapshot_date,
																    ps.hero_snapshot_json,
																    ps.health_driver_json,
																    ps.progress_context_json,
																    ps.budget_snapshot_json,
																    ps.participation_json,
																    ps.timeline_preview_json,
																    ps.insights_json,
																    ps.pulse_score,
																
																    hs.health_score,
																    hs.health_status,
																    hs.health_delta,
																    hs.health_delta_period,
																    hs.health_driver_breakdown_json,
																    hs.budget_health_score,
																    hs.dimension_breakdown_json
																
																FROM group_moments gm
																LEFT JOIN LATERAL (
																    SELECT *
																    FROM group_pulse_snapshots ps1
																    WHERE ps1.moment_id = gm.moment_id
																    ORDER BY ps1.snapshot_date DESC, ps1.created_at DESC
																    LIMIT 1
																) ps ON TRUE
																LEFT JOIN LATERAL (
																    SELECT *
																    FROM group_health_snapshots hs1
																    WHERE hs1.moment_id = gm.moment_id
																    ORDER BY hs1.snapshot_date DESC, hs1.created_at DESC
																    LIMIT 1
																) hs ON TRUE;
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_group_pulse_signals AS
																SELECT
																    s.signal_id,
																    s.moment_id,
																    s.signal_type,
																    s.signal_category,
																    s.signal_title,
																    s.signal_description,
																    COALESCE(s.severity, s.priority) AS severity,
																    s.signal_status,
																    s.signal_score,
																    s.display_order,
																    s.source_widget,
																    s.related_budget_plan_id,
																    s.generated_at,
																    s.expires_at
																FROM group_signals s
																WHERE s.is_active = TRUE
																  AND COALESCE(s.signal_status, 'OPEN') = 'OPEN';
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_group_next_best_actions AS
																SELECT
																    r.recommendation_id,
																    r.moment_id,
																    r.related_life_space_id,
																    r.recommendation_type,
																    r.recommendation_category,
																    r.title,
																    r.description,
																    r.priority,
																    r.recommendation_score,
																    r.expected_impact_json,
																    r.impact_score,
																    r.confidence_level,
																    r.action_deeplink,
																    r.status,
																    r.generated_at
																FROM group_recommendations r
																WHERE r.status = 'OPEN';
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_group_moment_dashboard AS
																SELECT
																    gm.moment_id,
																    gm.moment_type,
																    gm.moment_profile,
																    gm.moment_name,
																    gm.stage,
																    gm.status,
																    gm.activation_status,
																    gm.currency_code,
																
																    COUNT(DISTINCT mem.member_id) FILTER (
																        WHERE mem.status IN ('ACTIVE','CONFIRMED')
																    ) AS active_member_count,
																
																    COUNT(DISTINCT wi.work_item_id) FILTER (
																        WHERE wi.status IN ('OPEN','IN_PROGRESS','BLOCKED')
																    ) AS open_work_items,
																
																    COUNT(DISTINCT wi.work_item_id) FILTER (
																        WHERE wi.work_item_type IN ('MILESTONE','ACHIEVEMENT')
																          AND wi.status = 'COMPLETED'
																    ) AS completed_milestones,
																
																    COUNT(DISTINCT res.resource_id) FILTER (
																        WHERE res.status = 'ACTIVE'
																    ) AS active_resources,
																
																    COUNT(DISTINCT d.decision_id) FILTER (
																        WHERE d.status IN ('OPEN','DRAFT')
																    ) AS open_decisions,
																
																    COUNT(DISTINCT lf.feed_id) AS activity_count
																
																FROM group_moments gm
																LEFT JOIN group_moment_members mem
																    ON mem.moment_id = gm.moment_id
																LEFT JOIN group_moment_work_items wi
																    ON wi.moment_id = gm.moment_id
																LEFT JOIN group_moment_resources res
																    ON res.moment_id = gm.moment_id
																LEFT JOIN group_decisions d
																    ON d.moment_id = gm.moment_id
																LEFT JOIN group_live_feed lf
																    ON lf.moment_id = gm.moment_id
																GROUP BY
																    gm.moment_id,
																    gm.moment_type,
																    gm.moment_profile,
																    gm.moment_name,
																    gm.stage,
																    gm.status,
																    gm.activation_status,
																    gm.currency_code;
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
CREATE OR REPLACE VIEW vw_group_people_impact AS
																SELECT
																    p.impact_id,
																    p.moment_id,
																    p.member_id,
																    m.display_name,
																    p.impact_type,
																    p.impact_score,
																    p.rank_no,
																    p.badge_label,
																    p.supporting_metrics_json
																FROM group_people_impact_scores p
																JOIN group_moment_members m
																    ON m.member_id = p.member_id;
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_group_memory_gallery AS
																SELECT
																    me.memory_id,
																    me.moment_id,
																    me.memory_type,
																    me.memory_category,
																    me.category,
																    me.title,
																    me.description,
																    me.media_count,
																    me.highlight_score,
																    me.is_gallery_item,
																    me.memory_date,
																    ga.attachment_id,
																    ga.thumbnail_url,
																    ga.file_url,
																    ga.file_type
																FROM group_memory_entries me
																LEFT JOIN group_attachments ga
																    ON ga.entity_id = me.memory_id
																   AND ga.entity_name = 'group_memory_entries'
																WHERE me.is_gallery_item = TRUE
																   OR ga.is_gallery_item = TRUE;
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_group_life_latest AS
																SELECT
																    gls.life_space_id,
																    gls.user_id,
																    gls.space_name,
																    gls.space_status,
																
																    snap.life_snapshot_id,
																    snap.snapshot_date,
																    snap.group_life_score,
																    snap.health_status,
																    snap.dominant_driver,
																    snap.dominant_risk,
																    snap.highest_leverage,
																    snap.trend_delta
																
																FROM group_life_spaces gls
																LEFT JOIN LATERAL (
																    SELECT *
																    FROM group_life_snapshots s
																    WHERE s.life_space_id = gls.life_space_id
																    ORDER BY s.snapshot_date DESC, s.created_at DESC
																    LIMIT 1
																) snap ON TRUE;
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_group_life_dimensions AS
																SELECT
																    l.life_space_id,
																    l.life_snapshot_id,
																    d.dimension_score_id,
																    d.dimension_code,
																    d.dimension_name,
																    d.score,
																    d.status,
																    d.trend_delta,
																    d.explanation
																FROM vw_group_life_latest l
																JOIN group_life_dimension_scores d
																    ON d.life_snapshot_id = l.life_snapshot_id;
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_group_life_driver_effects AS
																SELECT
																    l.life_space_id,
																    l.life_snapshot_id,
																    e.driver_effect_id,
																    e.source_moment_type,
																    e.target_moment_type,
																    e.effect_label,
																    e.impact_pct,
																    e.explanation,
																    e.recommended_action,
																    e.confidence_level,
																    e.rank_no,
																    e.supporting_metrics_json
																FROM vw_group_life_latest l
																JOIN group_life_driver_effects e
																    ON e.life_snapshot_id = l.life_snapshot_id
																ORDER BY e.rank_no;
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
CREATE OR REPLACE VIEW vw_group_life_master_latest AS
																SELECT
																    x.*
																FROM (
																    SELECT
																        ms.*,
																        ROW_NUMBER() OVER (
																            PARTITION BY ms.user_id, ms.life_space_id
																            ORDER BY ms.snapshot_date DESC, ms.created_at DESC
																        ) AS rn
																    FROM group_life_master_snapshots ms
																) x
																WHERE x.rn = 1;
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_budget_quick_add_options AS
																SELECT
																    q.config_id,
																    q.moment_type,
																    q.moment_profile,
																    q.module_code,
																    q.module_label,
																    q.display_order,
																    q.quick_add_category,
																    q.is_enabled,
																    q.is_visible
																FROM group_quick_add_config q
																WHERE q.module_code = 'BUDGET'
																  AND q.is_enabled = TRUE
																  AND q.is_visible = TRUE;
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_group_activity_timeline AS
																
																SELECT
																    lf.feed_id AS activity_id,
																    lf.moment_id,
																    gm.moment_type,
																    gm.moment_profile,
																    gm.moment_name,
																
																    lf.feed_category AS activity_category,
																    COALESCE(lf.category_chip, lf.feed_category) AS category_chip,
																
																    lf.title,
																    lf.summary,
																
																    lf.entity_name,
																    lf.entity_id,
																
																    lf.created_by,
																    mem.display_name AS created_by_name,
																
																    lf.created_at AS activity_time,
																
																    lf.can_view,
																    lf.can_edit,
																    lf.can_delete,
																    lf.is_editable,
																    lf.edit_route,
																
																    lf.timeline_display_json,
																
																    LOWER(
																        COALESCE(lf.title,'') || ' ' ||
																        COALESCE(lf.summary,'') || ' ' ||
																        COALESCE(lf.feed_category,'') || ' ' ||
																        COALESCE(mem.display_name,'')
																    ) AS search_text
																
																FROM group_live_feed lf
																JOIN group_moments gm
																    ON gm.moment_id = lf.moment_id
																LEFT JOIN group_moment_members mem
																    ON mem.member_id = lf.created_by
																WHERE lf.is_hidden = FALSE;
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
																
																    CASE
																        WHEN bps.critical_risks > 0 THEN 'critical'
																        WHEN bps.pending_approvals > 5 THEN 'attention'
																        ELSE 'healthy'
																    END AS pulse_status,
																
																    bps.generated_at
																
																FROM business_moments bm
																
																JOIN business_pulse_snapshots bps
																    ON bm.moment_id = bps.moment_id
																
																WHERE bm.status = 'active';
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_business_moments AS
																
																SELECT
																
																    bm.moment_id,
																
																    bm.moment_name,
																
																    bm.moment_type,
																
																    bm.status,
																
																    bmm.members_count,
																
																    bmm.activities_count,
																
																    bmm.pending_approvals,
																
																    bmm.open_risks,
																
																    bmm.spend_amount,
																
																    bmm.last_activity_at,
																
																    bmm.last_updated_at,
																
																    CASE
																        WHEN bmm.open_risks > 5 THEN 'needs_attention'
																        WHEN bmm.pending_approvals > 3 THEN 'pending_actions'
																        ELSE 'on_track'
																    END AS moment_health
																
																FROM business_moments bm
																
																LEFT JOIN business_moment_metrics bmm
																    ON bm.moment_id = bmm.moment_id
																
																WHERE bm.status = 'active';
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_business_live AS
																
																SELECT
																
																    feed_id,
																
																    moment_id,
																
																    source_table,
																
																    source_record_id,
																
																    event_type,
																
																    actor_user_id,
																
																    actor_name,
																
																    headline,
																
																    detail_message,
																
																    amount,
																
																    priority,
																
																    event_timestamp,
																
																    visibility
																
																FROM business_live_feed
																
																WHERE is_deleted = FALSE
																
																ORDER BY event_timestamp DESC;
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_business_live_transaction_details AS
																
																SELECT
																
																    p.moment_id,
																
																    p.source_table,
																
																    p.source_record_id,
																
																    p.role_name,
																
																    p.can_view,
																
																    p.can_edit,
																
																    p.can_delete,
																
																    p.permission_reason,
																
																    p.granted_at
																
																FROM business_transaction_permissions p
																
																WHERE p.active_flag = TRUE;
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_business_live_audit_history AS
																
																SELECT
																
																    audit_id,
																
																    moment_id,
																
																    source_table,
																
																    source_record_id,
																
																    field_name,
																
																    old_value,
																
																    new_value,
																
																    change_type,
																
																    changed_by,
																
																    changed_by_name,
																
																    change_reason,
																
																    changed_at
																
																FROM business_audit_history
																
																ORDER BY changed_at DESC;
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_business_memory AS
																
																SELECT
																
																    pattern_id,
																
																    moment_id,
																
																    pattern_type,
																
																    pattern_title,
																
																    observation_text,
																
																    source_metric,
																
																    confidence_level,
																
																    first_observed_at,
																
																    last_observed_at,
																
																    pattern_status
																
																FROM business_memory_patterns
																
																WHERE pattern_status = 'active'
																
																ORDER BY last_observed_at DESC;
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_business_notifications AS
																
																SELECT
																
																    notification_id,
																
																    moment_id,
																
																    recipient_user_id,
																
																    notification_type,
																
																    title,
																
																    message,
																
																    priority,
																
																    notification_status,
																
																    created_at,
																
																    read_at
																
																FROM business_notifications
																
																WHERE notification_status <> 'archived'
																
																ORDER BY created_at DESC;
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_business_team_dashboard AS
																
																SELECT
																
																    bm.workspace_id,
																
																    COUNT(DISTINCT bm.moment_id) AS active_moments,
																
																    SUM(bmm.members_count) AS total_members,
																
																    SUM(bmm.activities_count) AS total_activities,
																
																    SUM(bmm.pending_approvals) AS pending_approvals,
																
																    SUM(bmm.open_risks) AS open_risks,
																
																    SUM(bmm.spend_amount) AS total_spend,
																
																    MAX(bmm.last_activity_at) AS last_activity
																
																FROM business_moments bm
																
																LEFT JOIN business_moment_metrics bmm
																    ON bm.moment_id = bmm.moment_id
																
																WHERE bm.status = 'active'
																
																GROUP BY bm.workspace_id;
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
WHERE bm.status = 'active';
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_business_ai_signals AS
SELECT
    signal_id,
    moment_id,
    signal_scope,
    signal_type,
    signal_title,
    signal_message,
    source_table,
    source_record_id,
    severity,
    confidence_score,
    recommended_action,
    target_screen,
    generated_at,
    expires_at
FROM ai_signals
WHERE signal_status = 'active'
  AND (
        expires_at IS NULL
        OR expires_at > CURRENT_TIMESTAMP
      )
ORDER BY
    CASE severity
        WHEN 'critical' THEN 1
        WHEN 'high' THEN 2
        WHEN 'medium' THEN 3
        WHEN 'low' THEN 4
        ELSE 5
    END,
    generated_at DESC;
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_business_live_transaction_rich_details AS

SELECT
    lf.feed_id,
    lf.moment_id,
    lf.source_table,
    lf.source_record_id,
    lf.event_type,
    lf.actor_user_id,
    lf.actor_name,
    lf.headline,
    lf.detail_message,
    lf.amount,
    lf.priority,
    lf.event_timestamp,
    lf.visibility,

    a.activity_title,
    a.category AS activity_category,
    a.activity_status,
    a.activity_owner_id,
    fn_get_business_actor_name(a.moment_id, a.activity_owner_id) AS activity_owner_name,
    a.has_spend,
    a.vendor_name,

    ar.request_title,
    ar.approval_type,
    ar.approval_status,
    ar.requested_by,
    fn_get_business_actor_name(ar.moment_id, ar.requested_by) AS requested_by_name,
    ar.approver_id,
    fn_get_business_actor_name(ar.moment_id, ar.approver_id) AS approver_name,
    ar.needed_by,
    ar.decision_note,
    ar.converted_to_spend,
    ar.converted_activity_id,

    tu.update_type,
    tu.update_title,
    tu.people_involved,
    tu.visibility AS update_visibility,

    ir.issue_title,
    ir.issue_type,
    ir.severity,
    ir.current_impact,
    ir.owner_id AS issue_owner_id,
    fn_get_business_actor_name(ir.moment_id, ir.owner_id) AS issue_owner_name,
    ir.target_resolution_date,
    ir.resolution_status,

    (
        SELECT jsonb_agg(
            jsonb_build_object(
                'field_name', ah.field_name,
                'old_value', ah.old_value,
                'new_value', ah.new_value,
                'change_type', ah.change_type,
                'changed_by', ah.changed_by,
                'changed_by_name', ah.changed_by_name,
                'changed_at', ah.changed_at
            )
            ORDER BY ah.changed_at DESC
        )
        FROM business_audit_history ah
        WHERE ah.moment_id = lf.moment_id
          AND ah.source_table = lf.source_table
          AND ah.source_record_id = lf.source_record_id
    ) AS change_history,

    (
        SELECT jsonb_agg(
            jsonb_build_object(
                'role_name', tp.role_name,
                'can_view', tp.can_view,
                'can_edit', tp.can_edit,
                'can_delete', tp.can_delete,
                'permission_reason', tp.permission_reason
            )
        )
        FROM business_transaction_permissions tp
        WHERE tp.moment_id = lf.moment_id
          AND tp.source_table = lf.source_table
          AND tp.source_record_id = lf.source_record_id
          AND tp.active_flag = TRUE
    ) AS permissions

FROM business_live_feed lf

LEFT JOIN team_activities a
  ON lf.source_table = 'team_activities'
 AND lf.source_record_id = a.activity_id

LEFT JOIN team_approval_requests ar
  ON lf.source_table = 'team_approval_requests'
 AND lf.source_record_id = ar.approval_id

LEFT JOIN team_updates tu
  ON lf.source_table = 'team_updates'
 AND lf.source_record_id = tu.update_id

LEFT JOIN team_issue_risks ir
  ON lf.source_table = 'team_issue_risks'
 AND lf.source_record_id = ir.issue_id

WHERE lf.is_deleted = FALSE;
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_business_runway_pulse AS
																
																SELECT
																    bm.moment_id,
																    bm.workspace_id,
																    bm.moment_name,
																    bm.moment_type,
																    bm.status,
																
																    bps.snapshot_date,
																
																    bps.cash_available,
																    bps.estimated_runway_months,
																    bps.cash_inflow_total,
																    bps.expense_burn_total,
																    bps.net_burn,
																    bps.runway_alert_count,
																    bps.runway_risk_count,
																    bps.operating_currency,
																
																    bps.pending_approvals,
																    bps.critical_risks,
																    bps.generated_at,
																
																    CASE
																        WHEN bps.critical_risks > 0 THEN 'critical'
																        WHEN bps.runway_alert_count > 0 THEN 'attention'
																        WHEN bps.net_burn > 0 THEN 'stable'
																        ELSE 'positive'
																    END AS runway_health_status,
																
																    CASE
																        WHEN bps.critical_risks > 0
																            THEN 'Critical runway risks need attention'
																        WHEN bps.runway_alert_count > 0
																            THEN 'Runway alerts are active'
																        WHEN bps.net_burn > 0
																            THEN 'Runway is being monitored'
																        ELSE 'Cash inflow is covering current burn'
																    END AS runway_health_reason
																
																FROM business_moments bm
																
																JOIN business_pulse_snapshots bps
																    ON bm.moment_id = bps.moment_id
																
																WHERE bm.status = 'active'
																  AND bm.moment_type = 'business_runway';
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_business_runway_pulse_signals AS
																
																SELECT
																    bm.moment_id,
																    'runway_threshold' AS signal_type,
																    'Runway Threshold Alert' AS signal_title,
																    CONCAT(
																        'Estimated runway is ',
																        bps.estimated_runway_months,
																        ' months'
																    ) AS signal_message,
																    'high' AS severity,
																    bps.generated_at AS signal_time
																FROM business_moments bm
																JOIN business_pulse_snapshots bps
																    ON bm.moment_id = bps.moment_id
																JOIN business_runway_structure brs
																    ON bm.moment_id = brs.moment_id
																WHERE bm.status = 'active'
																  AND bm.moment_type = 'business_runway'
																  AND bps.estimated_runway_months <= brs.alert_threshold_months
																
																UNION ALL
																
																SELECT
																    rr.moment_id,
																    'runway_risk' AS signal_type,
																    'High Runway Risk' AS signal_title,
																    rr.risk_title AS signal_message,
																    rr.severity,
																    rr.created_at AS signal_time
																FROM runway_risks rr
																WHERE rr.archived_at IS NULL
																  AND rr.risk_status <> 'resolved'
																  AND rr.severity IN ('high', 'critical')
																
																UNION ALL
																
																SELECT
																    reb.moment_id,
																    'expense_activity' AS signal_type,
																    'Expense Activity Recorded' AS signal_title,
																    CONCAT(
																        reb.expense_category,
																        ' expense recorded'
																    ) AS signal_message,
																    reb.priority AS severity,
																    reb.created_at AS signal_time
																FROM runway_expense_burns reb
																WHERE reb.archived_at IS NULL
																
																UNION ALL
																
																SELECT
																    rci.moment_id,
																    'cash_inflow' AS signal_type,
																    'Cash Inflow Recorded' AS signal_title,
																    CONCAT(
																        rci.inflow_type,
																        ' recorded'
																    ) AS signal_message,
																    'medium' AS severity,
																    rci.created_at AS signal_time
																FROM runway_cash_inflows rci
																WHERE rci.archived_at IS NULL;
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_business_runway_moments AS
																
																SELECT
																    bm.moment_id,
																    bm.workspace_id,
																    bm.moment_name,
																    bm.moment_type,
																    bm.status,
																
																    bmm.members_count,
																    bmm.cash_available,
																    bmm.estimated_runway_months,
																    bmm.cash_inflow_count,
																    bmm.expense_count,
																    bmm.risk_count,
																    bmm.decision_count,
																    bmm.net_burn,
																    bmm.operating_currency,
																    bmm.last_activity_at,
																    bmm.last_updated_at,
																
																    CASE
																        WHEN bmm.risk_count > 0 THEN 'needs_attention'
																        WHEN bmm.net_burn > 0 THEN 'active'
																        ELSE 'stable'
																    END AS moment_state
																
																FROM business_moments bm
																
																LEFT JOIN business_moment_metrics bmm
																    ON bm.moment_id = bmm.moment_id
																
																WHERE bm.status = 'active'
																  AND bm.moment_type = 'business_runway';
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_business_runway_moment_timeline AS
																
																SELECT
																    lf.feed_id,
																    lf.moment_id,
																    lf.event_type,
																    lf.headline,
																    lf.detail_message,
																    lf.amount,
																    lf.priority,
																    lf.actor_name,
																    lf.event_timestamp
																FROM business_live_feed lf
																JOIN business_moments bm
																    ON lf.moment_id = bm.moment_id
																WHERE bm.moment_type = 'business_runway'
																  AND bm.status = 'active'
																  AND lf.is_deleted = FALSE
																ORDER BY lf.event_timestamp DESC;
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_business_runway_live AS
																
																SELECT
																    lf.feed_id,
																    lf.moment_id,
																    lf.source_table,
																    lf.source_record_id,
																    lf.event_type,
																    lf.actor_user_id,
																    lf.actor_name,
																    lf.headline,
																    lf.detail_message,
																    lf.amount,
																    lf.priority,
																    lf.event_timestamp,
																    lf.visibility
																
																FROM business_live_feed lf
																
																JOIN business_moments bm
																    ON lf.moment_id = bm.moment_id
																
																WHERE bm.status = 'active'
																  AND bm.moment_type = 'business_runway'
																  AND lf.is_deleted = FALSE
																
																ORDER BY lf.event_timestamp DESC;
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_business_runway_live_rich_details AS
																
																SELECT
																    lf.feed_id,
																    lf.moment_id,
																    lf.source_table,
																    lf.source_record_id,
																    lf.event_type,
																    lf.actor_user_id,
																    lf.actor_name,
																    lf.headline,
																    lf.detail_message,
																    lf.amount,
																    lf.priority,
																    lf.event_timestamp,
																    lf.visibility,
																
																    rci.inflow_type,
																    rci.amount AS cash_inflow_amount,
																    rci.currency AS cash_inflow_currency,
																    rci.amount_in_operating_currency AS cash_inflow_amount_operating,
																    rci.inflow_date,
																    rci.reference AS cash_inflow_reference,
																
																    reb.expense_category,
																    reb.amount AS expense_amount,
																    reb.currency AS expense_currency,
																    reb.amount_in_operating_currency AS expense_amount_operating,
																    reb.vendor_name,
																    reb.expense_date,
																    reb.approval_required AS expense_approval_required,
																    reb.approval_status AS expense_approval_status,
																
																    rr.risk_title,
																    rr.risk_type,
																    rr.severity AS risk_severity,
																    rr.expected_impact,
																    rr.owner_id AS risk_owner_id,
																    fn_get_runway_actor_name(rr.moment_id, rr.owner_id) AS risk_owner_name,
																    rr.target_resolution_date,
																    rr.risk_status,
																
																    rsd.decision_type,
																    rsd.decision_title,
																    rsd.decision_owner_id,
																    fn_get_runway_actor_name(rsd.moment_id, rsd.decision_owner_id) AS decision_owner_name,
																    rsd.expected_impact AS decision_expected_impact,
																    rsd.decision_status,
																
																    rfu.update_type,
																    rfu.current_value,
																    rfu.new_value,
																    rfu.currency AS financial_update_currency,
																    rfu.new_value_in_operating_currency,
																    rfu.reason AS financial_update_reason,
																    rfu.approval_required AS financial_update_approval_required,
																    rfu.approval_status AS financial_update_approval_status,
																    rfu.applied_status,
																    rfu.applied_at,
																
																    (
																        SELECT jsonb_agg(
																            jsonb_build_object(
																                'field_name', ah.field_name,
																                'old_value', ah.old_value,
																                'new_value', ah.new_value,
																                'change_type', ah.change_type,
																                'changed_by', ah.changed_by,
																                'changed_by_name', ah.changed_by_name,
																                'changed_at', ah.changed_at
																            )
																            ORDER BY ah.changed_at DESC
																        )
																        FROM business_audit_history ah
																        WHERE ah.moment_id = lf.moment_id
																          AND ah.source_table = lf.source_table
																          AND ah.source_record_id = lf.source_record_id
																    ) AS change_history,
																
																    (
																        SELECT jsonb_agg(
																            jsonb_build_object(
																                'role_name', tp.role_name,
																                'can_view', tp.can_view,
																                'can_edit', tp.can_edit,
																                'can_delete', tp.can_delete,
																                'permission_reason', tp.permission_reason
																            )
																        )
																        FROM business_transaction_permissions tp
																        WHERE tp.moment_id = lf.moment_id
																          AND tp.source_table = lf.source_table
																          AND tp.source_record_id = lf.source_record_id
																          AND tp.active_flag = TRUE
																    ) AS permissions
																
																FROM business_live_feed lf
																
																JOIN business_moments bm
																    ON lf.moment_id = bm.moment_id
																
																LEFT JOIN runway_cash_inflows rci
																    ON lf.source_table = 'runway_cash_inflows'
																   AND lf.source_record_id = rci.cash_inflow_id
																
																LEFT JOIN runway_expense_burns reb
																    ON lf.source_table = 'runway_expense_burns'
																   AND lf.source_record_id = reb.expense_id
																
																LEFT JOIN runway_risks rr
																    ON lf.source_table = 'runway_risks'
																   AND lf.source_record_id = rr.risk_id
																
																LEFT JOIN runway_strategic_decisions rsd
																    ON lf.source_table = 'runway_strategic_decisions'
																   AND lf.source_record_id = rsd.decision_id
																
																LEFT JOIN runway_financial_updates rfu
																    ON lf.source_table = 'runway_financial_updates'
																   AND lf.source_record_id = rfu.financial_update_id
																
																WHERE bm.status = 'active'
																  AND bm.moment_type = 'business_runway'
																  AND lf.is_deleted = FALSE;
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_business_runway_memory AS
																
																SELECT
																    bmp.pattern_id,
																    bmp.moment_id,
																    bmp.pattern_type,
																    bmp.pattern_title,
																    bmp.observation_text,
																    bmp.source_metric,
																    bmp.confidence_level,
																    bmp.first_observed_at,
																    bmp.last_observed_at,
																    bmp.pattern_status
																
																FROM business_memory_patterns bmp
																
																JOIN business_moments bm
																    ON bmp.moment_id = bm.moment_id
																
																WHERE bm.status = 'active'
																  AND bm.moment_type = 'business_runway'
																  AND bmp.pattern_status = 'active'
																  AND bmp.pattern_type IN (
																        'cash_inflow_pattern',
																        'burn_pattern',
																        'runway_risk_pattern',
																        'decision_pattern',
																        'financial_update_pattern',
																        'net_burn_pattern'
																  )
																
																ORDER BY bmp.last_observed_at DESC;
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_business_runway_notifications AS
																
																SELECT
																    bn.notification_id,
																    bn.moment_id,
																    bn.recipient_user_id,
																    bn.notification_type,
																    bn.source_table,
																    bn.source_record_id,
																    bn.title,
																    bn.message,
																    bn.priority,
																    bn.notification_status,
																    bn.created_at,
																    bn.read_at
																
																FROM business_notifications bn
																
																JOIN business_moments bm
																    ON bn.moment_id = bm.moment_id
																
																WHERE bm.status = 'active'
																  AND bm.moment_type = 'business_runway'
																  AND bn.notification_status <> 'archived'
																
																ORDER BY bn.created_at DESC;
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_business_runway_revenue_signals AS
																
																SELECT
																    moment_id,
																
																    'revenue_improved' AS signal_type,
																
																    'Revenue Improved'
																        AS signal_title,
																
																    CONCAT(
																        'Revenue collection improved this cycle'
																    ) AS signal_message,
																
																    'positive' AS severity,
																
																    MAX(created_at)
																        AS signal_time
																
																FROM runway_cash_inflows
																
																WHERE inflow_type =
																      'revenue_collected'
																
																GROUP BY moment_id
																
																HAVING COUNT(*) >= 2;
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_business_runway_funding_signals AS
																
																SELECT
																    moment_id,
																
																    'funding_activity'
																        AS signal_type,
																
																    'Funding Activity Increased'
																        AS signal_title,
																
																    CONCAT(
																        COUNT(*),
																        ' funding events recorded'
																    ) AS signal_message,
																
																    'medium' AS severity,
																
																    MAX(created_at)
																        AS signal_time
																
																FROM runway_cash_inflows
																
																WHERE inflow_type IN (
																    'investor_funding',
																    'owner_contribution',
																    'bank_loan',
																    'government_grant'
																)
																
																GROUP BY moment_id
																
																HAVING COUNT(*) > 0;
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_business_runway_burn_signals AS
																
																SELECT
																    moment_id,
																
																    'burn_increase'
																        AS signal_type,
																
																    'Burn Increased This Month'
																        AS signal_title,
																
																    'Expense activity increased'
																        AS signal_message,
																
																    'attention' AS severity,
																
																    MAX(created_at)
																        AS signal_time
																
																FROM runway_expense_burns
																
																GROUP BY moment_id
																
																HAVING
																    SUM(amount_in_operating_currency)
																    >
																    0;
-- >>>STMT<<<
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
																
																    snap.budget_used_total,
																
																    snap.budget_remaining_total,
																
																    snap.vendor_activity_count,
																
																    snap.generated_at
																
																FROM business_moments bm
																
																JOIN business_operations_setup bos
																    ON bos.moment_id = bm.moment_id
																
																JOIN business_operations_snapshots snap
																    ON snap.moment_id = bm.moment_id
																
																WHERE snap.snapshot_date = CURRENT_DATE;
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_business_operations_budget_activity AS
																SELECT
																
																    bc.moment_id,
																
																    bc.budget_category_id,
																
																    bc.category_name,
																
																    bc.currency,
																
																    bc.allocated_budget,
																
																    COALESCE(
																        SUM(se.amount_in_operating_currency),
																        0
																    ) AS budget_used,
																
																    GREATEST(
																        bc.allocated_budget -
																        COALESCE(
																            SUM(se.amount_in_operating_currency),
																            0
																        ),
																        0
																    ) AS budget_remaining,
																
																    ROUND(
																        (
																            COALESCE(
																                SUM(se.amount_in_operating_currency),
																                0
																            )
																            /
																            NULLIF(
																                bc.allocated_budget,
																                0
																            )
																        ) * 100,
																        2
																    ) AS utilization_percent
																
																FROM business_operations_budget_categories bc
																
																LEFT JOIN operations_spend_entries se
																    ON se.budget_category_id = bc.budget_category_id
																   AND se.archived_at IS NULL
																   AND se.approval_status IN (
																        'approved',
																        'not_required'
																   )
																
																WHERE bc.category_status = 'active'
																  AND bc.archived_at IS NULL
																
																GROUP BY
																    bc.moment_id,
																    bc.budget_category_id,
																    bc.category_name,
																    bc.currency,
																    bc.allocated_budget;
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_business_operations_signals AS
																SELECT
																
																    moment_id,
																
																    'Budget Alert' AS signal_type,
																
																    CONCAT(
																        category_name,
																        ' utilization exceeded threshold'
																    ) AS signal_text,
																
																    utilization_percent,
																
																    CURRENT_TIMESTAMP AS generated_at
																
																FROM vw_business_operations_budget_activity
																
																WHERE utilization_percent >= 85
																
																UNION ALL
																
																SELECT
																
																    moment_id,
																
																    'Approval Attention',
																
																    CONCAT(
																        COUNT(*),
																        ' approvals pending'
																    ),
																
																    COUNT(*)::NUMERIC,
																
																    CURRENT_TIMESTAMP
																
																FROM operations_approval_requests
																
																WHERE approval_status = 'pending'
																  AND archived_at IS NULL
																
																GROUP BY moment_id
																
																UNION ALL
																
																SELECT
																
																    moment_id,
																
																    'Critical Issue',
																
																    CONCAT(
																        COUNT(*),
																        ' critical issue(s) active'
																    ),
																
																    COUNT(*)::NUMERIC,
																
																    CURRENT_TIMESTAMP
																
																FROM operations_issues
																
																WHERE severity = 'critical'
																  AND issue_status <> 'resolved'
																  AND archived_at IS NULL
																
																GROUP BY moment_id;
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_business_operations_moments AS
																SELECT
																
																    bm.moment_id,
																
																    bm.moment_name,
																
																    bos.operations_type,
																
																    bos.operating_currency,
																
																    metrics.budget_category_count,
																
																    metrics.operations_budget_used_total,
																
																    metrics.operations_active_issue_count,
																
																    metrics.operations_approval_count,
																
																    metrics.operations_improvement_count,
																
																    metrics.latest_spend_title,
																
																    metrics.latest_issue_title,
																
																    metrics.latest_approval_status,
																
																    metrics.latest_improvement_title,
																
																    metrics.last_operations_activity_at
																
																FROM business_moments bm
																
																JOIN business_operations_setup bos
																    ON bos.moment_id = bm.moment_id
																
																JOIN business_moment_metrics metrics
																    ON metrics.moment_id = bm.moment_id;
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_business_operations_live AS
																SELECT
																
																    lf.live_feed_id,
																
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
																);
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_business_operations_transaction_detail AS
																
																SELECT
																
																    moment_id,
																
																    spend_entry_id AS record_id,
																
																    'Spend Entry' AS transaction_type,
																
																    spend_name AS title,
																
																    budget_category_name AS category,
																
																    amount_in_operating_currency AS amount,
																
																    approval_status AS status,
																
																    created_at
																
																FROM operations_spend_entries
																
																WHERE archived_at IS NULL
																
																UNION ALL
																
																SELECT
																
																    moment_id,
																
																    vendor_update_id,
																
																    'Vendor Update',
																
																    vendor_name,
																
																    vendor_category,
																
																    NULL,
																
																    vendor_status,
																
																    created_at
																
																FROM operations_vendor_updates
																
																WHERE archived_at IS NULL
																
																UNION ALL
																
																SELECT
																
																    moment_id,
																
																    operations_approval_id,
																
																    'Approval Request',
																
																    request_title,
																
																    request_type,
																
																    amount,
																
																    approval_status,
																
																    created_at
																
																FROM operations_approval_requests
																
																WHERE archived_at IS NULL
																
																UNION ALL
																
																SELECT
																
																    moment_id,
																
																    operations_issue_id,
																
																    'Issue / Risk',
																
																    issue_title,
																
																    issue_category,
																
																    NULL,
																
																    issue_status,
																
																    created_at
																
																FROM operations_issues
																
																WHERE archived_at IS NULL
																
																UNION ALL
																
																SELECT
																
																    moment_id,
																
																    improvement_id,
																
																    'Operational Improvement',
																
																    improvement_title,
																
																    improvement_type,
																
																    NULL,
																
																    improvement_status,
																
																    created_at
																
																FROM operations_improvements
																
																WHERE archived_at IS NULL;
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_business_operations_memory AS
																SELECT
																
																    moment_id,
																
																    pattern_type,
																
																    pattern_title,
																
																    observation_text,
																
																    source_metric,
																
																    confidence_level,
																
																    first_observed_at,
																
																    last_observed_at
																
																FROM business_memory_patterns
																
																WHERE pattern_type IN (
																    'operations_budget_pattern',
																    'operations_vendor_pattern',
																    'operations_approval_pattern',
																    'operations_issue_pattern',
																    'operations_improvement_pattern'
																);
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_business_operations_memory_summary AS
																SELECT
																
																    bm.moment_id,
																
																    (
																        SELECT category_name
																        FROM vw_business_operations_budget_activity b
																        WHERE b.moment_id = bm.moment_id
																        ORDER BY budget_used DESC
																        LIMIT 1
																    ) AS most_active_budget_category,
																
																    (
																        SELECT issue_category
																        FROM operations_issues i
																        WHERE i.moment_id = bm.moment_id
																          AND i.archived_at IS NULL
																        GROUP BY issue_category
																        ORDER BY COUNT(*) DESC
																        LIMIT 1
																    ) AS most_frequent_issue,
																
																    (
																        SELECT improvement_type
																        FROM operations_improvements imp
																        WHERE imp.moment_id = bm.moment_id
																          AND imp.archived_at IS NULL
																        GROUP BY improvement_type
																        ORDER BY COUNT(*) DESC
																        LIMIT 1
																    ) AS most_recorded_improvement
																
																FROM business_moments bm
																
																WHERE bm.moment_type = 'business_operations';
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_business_operations_permission_matrix AS
																SELECT
																
																    moment_id,
																
																    role_name,
																
																    can_view,
																
																    can_edit,
																
																    can_approve,
																
																    can_delete
																
																FROM business_transaction_permissions
																
																WHERE role_name IN (
																    'Operations Owner',
																    'Operations Lead',
																    'Budget Controller',
																    'Approver',
																    'Contributor',
																    'Viewer'
																);
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
CREATE OR REPLACE VIEW vw_business_operations_signals AS
																
																/* Budget Alert */
																
																SELECT
																    moment_id,
																    'Budget Alert' AS signal_type,
																    CONCAT(
																        category_name,
																        ' utilization exceeded threshold'
																    ) AS signal_text,
																    utilization_percent,
																    CURRENT_TIMESTAMP AS generated_at
																FROM vw_business_operations_budget_activity
																WHERE utilization_percent >= 85
																
																UNION ALL
																
																/* Approval Attention */
																
																SELECT
																    moment_id,
																    'Approval Requests Rising',
																    CONCAT(
																        COUNT(*),
																        ' approvals pending'
																    ),
																    COUNT(*)::NUMERIC,
																    CURRENT_TIMESTAMP
																FROM operations_approval_requests
																WHERE approval_status='pending'
																  AND archived_at IS NULL
																GROUP BY moment_id
																
																UNION ALL
																
																/* Vendor Evaluations Increasing */
																
																SELECT
																    moment_id,
																    'Vendor Evaluations Increasing',
																    CONCAT(
																        COUNT(*),
																        ' evaluations recorded'
																    ),
																    COUNT(*)::NUMERIC,
																    CURRENT_TIMESTAMP
																FROM operations_vendor_updates
																WHERE vendor_event_type='vendor_evaluation'
																  AND archived_at IS NULL
																  AND created_at >= CURRENT_DATE - INTERVAL '30 day'
																GROUP BY moment_id
																
																UNION ALL
																
																/* Operational Improvements */
																
																SELECT
																    moment_id,
																    'Operational Improvements Recorded',
																    CONCAT(
																        COUNT(*),
																        ' improvements logged'
																    ),
																    COUNT(*)::NUMERIC,
																    CURRENT_TIMESTAMP
																FROM operations_improvements
																WHERE archived_at IS NULL
																  AND created_at >= CURRENT_DATE - INTERVAL '30 day'
																GROUP BY moment_id
																
																UNION ALL
																
																/* Critical Issues */
																
																SELECT
																    moment_id,
																    'Critical Issue',
																    CONCAT(
																        COUNT(*),
																        ' critical issues active'
																    ),
																    COUNT(*)::NUMERIC,
																    CURRENT_TIMESTAMP
																FROM operations_issues
																WHERE severity='critical'
																  AND issue_status<>'resolved'
																  AND archived_at IS NULL
																GROUP BY moment_id;
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_business_operations_improvement_momentum AS
																SELECT
																
																    moment_id,
																
																    improvement_type,
																
																    COUNT(*) AS improvement_count
																
																FROM operations_improvements
																
																WHERE archived_at IS NULL
																
																GROUP BY
																    moment_id,
																    improvement_type;
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_business_orchestration_health AS
SELECT
    job_type,
    job_status,
    COUNT(*) AS total_jobs,
    MAX(created_at) AS latest_job,
    MAX(completed_at) AS latest_completion
FROM business_orchestration_jobs
GROUP BY
    job_type,
    job_status;
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_business_pulse_v2 AS
SELECT

    bp.moment_id,

    bm.workspace_id,

    bm.moment_name,
    bm.moment_type,

    bp.health_score,
    bp.pulse_category,
    bp.pulse_description,

    bp.health_driver_count,
    bp.attention_count,
    bp.signal_count,

    bra.action_id,
    bra.action_title,
    bra.cta_label,
    bra.priority,

    bp.refreshed_at

FROM business_pulse_snapshots bp

JOIN business_moments bm
ON bm.moment_id = bp.moment_id

LEFT JOIN business_recommended_actions bra
ON bra.action_id = bp.next_best_action_id;
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_business_moments_v2 AS
SELECT

    bm.moment_id,

    bm.workspace_id,

    bm.moment_name,
    bm.moment_type,

    bpm.health_score,

    bmm.progress_score,
    bmm.progress_status,

    bmm.recent_wins_count,

    bmm.timeline_count,

    bmm.continue_cta_label,

    bmm.updated_at

FROM business_moment_metrics bmm

JOIN business_moments bm
ON bm.moment_id = bmm.moment_id

LEFT JOIN business_pulse_snapshots bpm
ON bpm.moment_id = bm.moment_id;
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_business_life_v2 AS
SELECT

    bls.workspace_id,

    bls.life_score,
    bls.life_status,

    bls.people_score,
    bls.finance_score,
    bls.operations_score,
    bls.vendor_score,
    bls.growth_score,

    bls.strongest_dimension,
    bls.weakest_dimension,
    bls.leverage_dimension,

    bls.drift_detected,

    bls.life_score_delta,

    bls.generated_at

FROM business_life_snapshots bls;
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
CREATE OR REPLACE VIEW vw_business_activity_center_v2 AS
SELECT

    ac.activity_center_item_id,

    ac.moment_id,

    bm.workspace_id,

    bm.moment_name,
    bm.moment_type,

    ac.activity_type,
    ac.activity_title,
    ac.activity_summary,

    ac.amount,
    ac.currency,

    ac.actor_user_id,
    ac.actor_name,

    ac.activity_status,

    ac.permission_badge,

    ac.occurred_at

FROM business_activity_center_items ac

JOIN business_moments bm
ON bm.moment_id = ac.moment_id;
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_business_life_dimensions_v2 AS
SELECT

    workspace_id,

    dimension_type,

    dimension_name,

    dimension_score,

    dimension_status,

    trend_direction,

    trend_delta,

    active_moment_count,

    generated_at

FROM business_life_dimensions;
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_business_life_connections_v2 AS
SELECT

    workspace_id,

    source_dimension,
    source_label,

    influence_type,
    influence_strength,

    target_dimension,
    target_label,

    confidence_score,

    generated_at

FROM business_life_connections;
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_business_life_insights_v2 AS
SELECT

    workspace_id,

    insight_type,

    insight_title,

    insight_body,

    insight_score,

    priority,

    generated_at

FROM business_life_insights

WHERE insight_status='active';
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_business_memory_learnings_v2 AS
SELECT

    learning_id,

    workspace_id,

    learning_type,

    learning_title,

    learning_summary,

    confidence_score,

    derived_from_count,

    created_at

FROM business_memory_learnings

WHERE learning_status='active';
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_business_playbooks_v2 AS
SELECT

    playbook_id,

    workspace_id,

    playbook_title,

    playbook_summary,

    success_rate,

    confidence_score,

    created_at

FROM business_playbooks

WHERE playbook_status='active';
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_business_journey_v2 AS
SELECT

    workspace_id,

    moment_id,

    event_title,

    event_description,

    event_type,

    event_date,

    created_at

FROM business_journey_events

ORDER BY event_date DESC;
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_business_orchestration_health_v2 AS
SELECT

    job_type,

    job_status,

    COUNT(*) total_jobs,

    MAX(created_at) latest_job,

    MAX(completed_at) latest_completion

FROM business_orchestration_jobs

GROUP BY
    job_type,
    job_status;
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_business_stale_snapshots AS
SELECT
    workspace_id,
    MAX(generated_at) AS last_refresh,
    CURRENT_TIMESTAMP - MAX(generated_at) AS refresh_age
FROM business_life_snapshots
GROUP BY workspace_id
HAVING CURRENT_TIMESTAMP - MAX(generated_at)
       > INTERVAL '24 HOURS';
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_business_experience_health AS
SELECT

    workspace_id,

    (
        COALESCE(life_score,0) * 0.40 +
        COALESCE(memory_score,0) * 0.30 +
        COALESCE(active_moment_count,0) * 3
    ) AS experience_health_score

FROM business_life_snapshots bls

LEFT JOIN business_memory_snapshots bms
ON bls.workspace_id = bms.workspace_id;
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_business_life360_export AS
SELECT

    workspace_id,

    life_score,

    people_score,

    finance_score,

    operations_score,

    vendor_score,

    growth_score,

    active_moment_count,

    generated_at

FROM business_life_snapshots;
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
CREATE OR REPLACE VIEW vw_business_pulse_v2 AS
SELECT

    bp.moment_id,
    bm.workspace_id,
    bm.moment_name,
    bm.moment_type,

    bp.health_score,
    bp.pulse_category,
    bp.pulse_description,

    bp.health_driver_count,
    bp.attention_count,
    bp.signal_count,

    bra.action_id,
    bra.action_title,
    bra.cta_label,
    bra.priority,

    bp.generated_at

FROM business_pulse_snapshots bp
JOIN business_moments bm
ON bm.moment_id = bp.moment_id

LEFT JOIN business_recommended_actions bra
ON bra.action_id = bp.next_best_action_id;
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_business_moments_v2 AS
SELECT

    bm.moment_id,
    bm.workspace_id,
    bm.moment_name,
    bm.moment_type,

    bpm.health_score,

    bmm.progress_score,
    bmm.progress_status,

    bmm.recent_wins_count,
    bmm.timeline_count,

    bmm.continue_cta_label,

    bmm.last_updated_at

FROM business_moment_metrics bmm
JOIN business_moments bm
ON bm.moment_id = bmm.moment_id

LEFT JOIN business_pulse_snapshots bpm
ON bpm.moment_id = bm.moment_id;
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_business_driver_formulas AS
SELECT

    moment_type,

    driver_code,

    driver_name,

    driver_weight,

    source_table,

    source_column,

    formula_description

FROM business_driver_formula_registry

WHERE active_flag = TRUE;
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_business_driver_formulas AS
SELECT
    moment_type,
    driver_code,
    driver_name,
    driver_weight,
    source_table,
    source_column,
    formula_description
FROM business_driver_formula_registry
WHERE active_flag = TRUE;
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_archive_trigger_coverage AS
SELECT
    event_object_table,
    trigger_name
FROM information_schema.triggers
WHERE trigger_name ILIKE '%archive%';
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_business_phase1_active_moments AS
SELECT
    moment_id,
    workspace_id,
    moment_type,
    moment_name,
    status
FROM business_moments
WHERE status = 'active'
  AND moment_type IN (
      'team_operations',
      'business_runway',
      'business_operations'
  );
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_life360_home_state AS
SELECT
    u.user_id,
    CASE
        WHEN l.life360_snapshot_id IS NULL OR l.signal_confidence_score < 25
            THEN 'EMPTY'
        ELSE 'FULL'
    END AS life360_state
FROM users u
LEFT JOIN LATERAL (
    SELECT *
    FROM life360_snapshots l
    WHERE l.user_id = u.user_id
    ORDER BY l.snapshot_date DESC
    LIMIT 1
) l ON TRUE;
-- >>>STMT<<<
CREATE OR REPLACE VIEW vw_life360_home AS
SELECT *
FROM life360_snapshots l
WHERE l.snapshot_date = (
    SELECT MAX(l2.snapshot_date)
    FROM life360_snapshots l2
    WHERE l2.user_id = l.user_id
);
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
