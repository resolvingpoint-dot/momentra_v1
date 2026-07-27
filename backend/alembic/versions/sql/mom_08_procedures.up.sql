CREATE OR REPLACE PROCEDURE sp_refresh_personal_runtime(
																    p_moment_id UUID
																)
																LANGUAGE plpgsql
																AS $$
																DECLARE
																    v_type VARCHAR(50);
																BEGIN
																
																    SELECT mt.moment_type_code
																    INTO v_type
																    FROM personal_moments pm
																    JOIN personal_moment_types mt
																        ON mt.moment_type_id = pm.moment_type_id
																    WHERE pm.moment_id = p_moment_id;
																
																    DELETE FROM personal_runtime_snapshots
																    WHERE moment_id = p_moment_id;
																
																    CASE v_type
																
																        WHEN 'LIFE_OPERATIONS' THEN
																            CALL sp_refresh_life_operations_runtime(p_moment_id);
																
																        WHEN 'FUTURE_BUILDING' THEN
																            CALL sp_refresh_future_building_runtime(p_moment_id);
																
																        WHEN 'LIFESTYLE' THEN
																            CALL sp_refresh_lifestyle_runtime(p_moment_id);
																
																        WHEN 'RELATIONSHIPS' THEN
																            CALL sp_refresh_relationship_runtime(p_moment_id);
																
																    END CASE;
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE PROCEDURE sp_refresh_personal_pulse(
																    p_moment_id UUID
																)
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    DELETE
																    FROM personal_pulse_snapshots
																    WHERE moment_id = p_moment_id;
																
																    INSERT INTO personal_pulse_snapshots
																    (
																        user_id,
																        moment_id,
																        moment_type_code,
																        pulse_title,
																        primary_metric_label,
																        primary_metric_value,
																        pulse_summary
																    )
																    SELECT
																        pm.user_id,
																        pm.moment_id,
																        mt.moment_type_code,
																        'Current State',
																        rs.runtime_state_label,
																        rs.primary_score,
																        rs.runtime_summary
																    FROM personal_runtime_snapshots rs
																    JOIN personal_moments pm
																        ON pm.moment_id = rs.moment_id
																    JOIN personal_moment_types mt
																        ON mt.moment_type_id = pm.moment_type_id
																    WHERE rs.moment_id = p_moment_id;
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE PROCEDURE sp_refresh_personal_pulse_snapshot(
																    p_moment_id UUID
																)
																LANGUAGE plpgsql
																AS $$
																BEGIN
																    CALL sp_refresh_personal_pulse(p_moment_id);
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE PROCEDURE sp_refresh_personal_memory(
																    p_moment_id UUID
																)
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    DELETE
																    FROM personal_memory_patterns
																    WHERE moment_id = p_moment_id;
																
																    INSERT INTO personal_memory_patterns
																    (
																        moment_id,
																        user_id,
																        moment_type_code,
																        pattern_type,
																        pattern_title,
																        pattern_description,
																        confidence_score,
																        supporting_event_count
																    )
																    SELECT
																        pm.moment_id,
																        pm.user_id,
																        mt.moment_type_code,
																        'BEHAVIOR_PATTERN',
																        'Recurring Pattern',
																        'Derived from user activity',
																        80,
																        COUNT(*)
																    FROM personal_quick_add_events q
																    JOIN personal_moments pm
																        ON pm.moment_id = q.moment_id
																    JOIN personal_moment_types mt
																        ON mt.moment_type_id = pm.moment_type_id
																    WHERE q.moment_id = p_moment_id
																    GROUP BY
																        pm.moment_id,
																        pm.user_id,
																        mt.moment_type_code;
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE PROCEDURE sp_refresh_personal_signals(
																    p_moment_id UUID
																)
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    DELETE
																    FROM personal_signals
																    WHERE moment_id = p_moment_id;
																
																    INSERT INTO personal_signals
																    (
																        user_id,
																        moment_id,
																        moment_type_code,
																        signal_type,
																        signal_title,
																        signal_description,
																        signal_score,
																        severity_level
																    )
																    SELECT
																        pm.user_id,
																        pm.moment_id,
																        mt.moment_type_code,
																        'TREND',
																        'Activity Increasing',
																        'Recent activity trend detected',
																        75,
																        'POSITIVE'
																    FROM personal_moments pm
																    JOIN personal_moment_types mt
																        ON mt.moment_type_id = pm.moment_type_id
																    WHERE pm.moment_id = p_moment_id;
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE PROCEDURE sp_refresh_personal_recommendations(
																    p_moment_id UUID
																)
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    DELETE
																    FROM personal_recommendations
																    WHERE moment_id = p_moment_id;
																
																    INSERT INTO personal_recommendations
																    (
																        user_id,
																        moment_id,
																        moment_type_code,
																        recommendation_type,
																        recommendation_title,
																        recommendation_description,
																        recommended_action,
																        confidence_score,
																        priority_score
																    )
																    SELECT
																        s.user_id,
																        s.moment_id,
																        s.moment_type_code,
																        'ACTION',
																        'Suggested Action',
																        s.signal_description,
																        'Review Priority',
																        85,
																        80
																    FROM personal_signals s
																    WHERE s.moment_id = p_moment_id
																      AND s.is_active = TRUE;
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE PROCEDURE sp_refresh_personal_orchestration(
																    p_moment_id UUID
																)
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    CALL sp_refresh_personal_runtime(p_moment_id);
																
																    CALL sp_refresh_personal_pulse(p_moment_id);
																
																    CALL sp_refresh_personal_memory(p_moment_id);
																
																    CALL sp_refresh_personal_signals(p_moment_id);
																
																    CALL sp_refresh_personal_recommendations(p_moment_id);
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE PROCEDURE sp_refresh_life_recovery_anchors(
    p_moment_id UUID
)
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM personal_memory_patterns
    WHERE moment_id = p_moment_id
      AND pattern_type = 'RECOVERY_ANCHOR';

    INSERT INTO personal_memory_patterns (
        moment_id,
        user_id,
        moment_type_code,
        pattern_type,
        pattern_title,
        pattern_description,
        confidence_score,
        supporting_event_count,
        contribution_breakdown_json
    )
    SELECT
        r.moment_id,
        r.user_id,
        'LIFE_OPERATIONS',
        'RECOVERY_ANCHOR',
        r.recovery_type,
        'This recovery activity repeatedly improves your operating rhythm.',
        LEAST(95, 60 + COUNT(*) * 8),
        COUNT(*),
        jsonb_build_object(
            'avg_recovery_score', AVG(r.recovery_score),
            'high_impact_count', COUNT(*) FILTER (WHERE r.energy_impact = 'HIGH')
        )
    FROM personal_life_recovery_events r
    WHERE r.moment_id = p_moment_id
    GROUP BY r.moment_id, r.user_id, r.recovery_type
    HAVING COUNT(*) >= 2;
END;
$$;
-- >>>STMT<<<
CREATE OR REPLACE PROCEDURE sp_refresh_lifestyle_roi_patterns(
    p_moment_id UUID
)
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM personal_memory_patterns
    WHERE moment_id = p_moment_id
      AND pattern_type = 'LIFESTYLE_ROI';

    INSERT INTO personal_memory_patterns (
        moment_id,
        user_id,
        moment_type_code,
        pattern_type,
        pattern_title,
        pattern_description,
        confidence_score,
        supporting_event_count,
        contribution_breakdown_json
    )
    SELECT
        e.moment_id,
        e.user_id,
        'LIFESTYLE',
        'LIFESTYLE_ROI',
        e.experience_type,
        'This experience category creates strong fulfillment return for the user.',
        LEAST(95, 55 + COUNT(*) * 7),
        COUNT(*),
        jsonb_build_object(
            'avg_fulfillment', AVG(e.fulfillment_score_delta),
            'avg_roi', AVG(e.lifestyle_roi_score),
            'total_spend', COALESCE(SUM(e.cost_amount),0)
        )
    FROM personal_lifestyle_experience_events e
    WHERE e.moment_id = p_moment_id
    GROUP BY e.moment_id, e.user_id, e.experience_type
    HAVING COUNT(*) >= 2;
END;
$$;
-- >>>STMT<<<
CREATE OR REPLACE PROCEDURE sp_refresh_relationship_health_patterns(
    p_moment_id UUID
)
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM personal_memory_patterns
    WHERE moment_id = p_moment_id
      AND pattern_type = 'RELATIONSHIP_HEALTH';

    INSERT INTO personal_memory_patterns (
        moment_id,
        user_id,
        moment_type_code,
        pattern_type,
        pattern_title,
        pattern_description,
        confidence_score,
        supporting_event_count,
        contribution_breakdown_json
    )
    SELECT
        c.moment_id,
        c.user_id,
        'RELATIONSHIPS',
        'RELATIONSHIP_HEALTH',
        c.relationship_type || ' Connection Pattern',
        'Relationship strength is inferred from connection quality, trust, support, and presence.',
        LEAST(96, 58 + COUNT(*) * 6),
        COUNT(*),
        jsonb_build_object(
            'avg_connection_score', AVG(c.connection_score_delta),
            'avg_trust_score', AVG(c.trust_score_delta),
            'presence_count', COUNT(*) FILTER (WHERE c.presence_signal_flag = TRUE)
        )
    FROM personal_relationship_connection_events c
    WHERE c.moment_id = p_moment_id
    GROUP BY c.moment_id, c.user_id, c.relationship_type
    HAVING COUNT(*) >= 2;
END;
$$;
-- >>>STMT<<<
CREATE OR REPLACE PROCEDURE sp_refresh_future_momentum_patterns(
    p_moment_id UUID
)
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM personal_memory_patterns
    WHERE moment_id = p_moment_id
      AND pattern_type = 'FUTURE_MOMENTUM';

    INSERT INTO personal_memory_patterns (
        moment_id,
        user_id,
        moment_type_code,
        pattern_type,
        pattern_title,
        pattern_description,
        confidence_score,
        supporting_event_count,
        contribution_breakdown_json
    )
    SELECT
        p.moment_id,
        p.user_id,
        'FUTURE_BUILDING',
        'FUTURE_MOMENTUM',
        p.progress_type,
        'This progress type repeatedly contributes to future momentum.',
        LEAST(95, 60 + COUNT(*) * 7),
        COUNT(*),
        jsonb_build_object(
            'avg_momentum_delta', AVG(p.momentum_score_delta),
            'investment_weight', AVG(p.investment_weight_score),
            'velocity_events', COUNT(*) FILTER (WHERE p.velocity_signal_flag = TRUE)
        )
    FROM personal_future_progress_events p
    WHERE p.moment_id = p_moment_id
    GROUP BY p.moment_id, p.user_id, p.progress_type
    HAVING COUNT(*) >= 2;
END;
$$;
-- >>>STMT<<<
CREATE OR REPLACE PROCEDURE sp_refresh_personal_advanced_signals(
    p_moment_id UUID
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_user_id UUID;
    v_type VARCHAR(50);
BEGIN
    SELECT pm.user_id, mt.moment_type_code
    INTO v_user_id, v_type
    FROM personal_moments pm
    JOIN personal_moment_types mt
        ON mt.moment_type_id = pm.moment_type_id
    WHERE pm.moment_id = p_moment_id;

    DELETE FROM personal_signals
    WHERE moment_id = p_moment_id
      AND signal_type IN (
        'RECOVERY_SIGNAL',
        'LIFESTYLE_ROI_SIGNAL',
        'RELATIONSHIP_CONNECTION_SIGNAL',
        'FUTURE_MOMENTUM_SIGNAL'
      );

    IF v_type = 'LIFE_OPERATIONS' THEN
        INSERT INTO personal_signals (
            user_id, moment_id, moment_type_code,
            signal_type, signal_title, signal_description,
            signal_score, severity_level, trend_direction, source_event_count
        )
        SELECT
            v_user_id,
            p_moment_id,
            v_type,
            'RECOVERY_SIGNAL',
            'Recovery activity increased',
            'Recovery anchors are becoming more visible from recent activity.',
            LEAST(95, 60 + COUNT(*) * 8),
            'POSITIVE',
            'UP',
            COUNT(*)
        FROM personal_life_recovery_events
        WHERE moment_id = p_moment_id
        HAVING COUNT(*) > 0;

    ELSIF v_type = 'LIFESTYLE' THEN
        INSERT INTO personal_signals (
            user_id, moment_id, moment_type_code,
            signal_type, signal_title, signal_description,
            signal_score, severity_level, trend_direction, source_event_count
        )
        SELECT
            v_user_id,
            p_moment_id,
            v_type,
            'LIFESTYLE_ROI_SIGNAL',
            'Meaningful experiences increasing',
            'Recent lifestyle experiences are producing strong fulfillment return.',
            LEAST(95, 55 + COUNT(*) * 7),
            'POSITIVE',
            'UP',
            COUNT(*)
        FROM personal_lifestyle_experience_events
        WHERE moment_id = p_moment_id
        HAVING COUNT(*) > 0;

    ELSIF v_type = 'RELATIONSHIPS' THEN
        INSERT INTO personal_signals (
            user_id, moment_id, moment_type_code,
            signal_type, signal_title, signal_description,
            signal_score, severity_level, trend_direction, source_event_count
        )
        SELECT
            v_user_id,
            p_moment_id,
            v_type,
            'RELATIONSHIP_CONNECTION_SIGNAL',
            'Connection rhythm improving',
            'Recent connection activity indicates stronger relationship continuity.',
            LEAST(95, 55 + COUNT(*) * 7),
            'POSITIVE',
            'UP',
            COUNT(*)
        FROM personal_relationship_connection_events
        WHERE moment_id = p_moment_id
        HAVING COUNT(*) > 0;

    ELSIF v_type = 'FUTURE_BUILDING' THEN
        INSERT INTO personal_signals (
            user_id, moment_id, moment_type_code,
            signal_type, signal_title, signal_description,
            signal_score, severity_level, trend_direction, source_event_count
        )
        SELECT
            v_user_id,
            p_moment_id,
            v_type,
            'FUTURE_MOMENTUM_SIGNAL',
            'Momentum building',
            'Recent progress events indicate increasing future momentum.',
            LEAST(95, 55 + COUNT(*) * 7),
            'POSITIVE',
            'UP',
            COUNT(*)
        FROM personal_future_progress_events
        WHERE moment_id = p_moment_id
        HAVING COUNT(*) > 0;
    END IF;
END;
$$;
-- >>>STMT<<<
CREATE OR REPLACE PROCEDURE sp_refresh_personal_advanced_memory(
    p_moment_id UUID
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_type VARCHAR(50);
BEGIN
    SELECT mt.moment_type_code
    INTO v_type
    FROM personal_moments pm
    JOIN personal_moment_types mt
        ON mt.moment_type_id = pm.moment_type_id
    WHERE pm.moment_id = p_moment_id;

    IF v_type = 'LIFE_OPERATIONS' THEN
        CALL sp_refresh_life_recovery_anchors(p_moment_id);

    ELSIF v_type = 'LIFESTYLE' THEN
        CALL sp_refresh_lifestyle_roi_patterns(p_moment_id);

    ELSIF v_type = 'RELATIONSHIPS' THEN
        CALL sp_refresh_relationship_health_patterns(p_moment_id);

    ELSIF v_type = 'FUTURE_BUILDING' THEN
        CALL sp_refresh_future_momentum_patterns(p_moment_id);
    END IF;
END;
$$;
-- >>>STMT<<<
CREATE OR REPLACE PROCEDURE sp_refresh_personal_orchestration(
    p_moment_id UUID
)
LANGUAGE plpgsql
AS $$
BEGIN
    CALL sp_refresh_personal_runtime(p_moment_id);

    CALL sp_refresh_personal_pulse(p_moment_id);

    CALL sp_refresh_personal_memory(p_moment_id);

    CALL sp_refresh_personal_advanced_memory(p_moment_id);

    CALL sp_refresh_personal_signals(p_moment_id);

    CALL sp_refresh_personal_advanced_signals(p_moment_id);

    CALL sp_refresh_personal_recommendations(p_moment_id);
END;
$$;
-- >>>STMT<<<
CREATE OR REPLACE PROCEDURE sp_run_personal_ai_refresh(
    p_moment_id UUID,
    p_run_type VARCHAR DEFAULT 'FULL_REFRESH'
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_run_id UUID;
    v_user_id UUID;
    v_type VARCHAR(50);
BEGIN
    SELECT pm.user_id, mt.moment_type_code
    INTO v_user_id, v_type
    FROM personal_moments pm
    JOIN personal_moment_types mt
        ON mt.moment_type_id = pm.moment_type_id
    WHERE pm.moment_id = p_moment_id;

    INSERT INTO personal_ai_interpretation_runs (
        user_id,
        moment_id,
        moment_type_code,
        run_type,
        input_payload,
        status,
        started_at
    )
    VALUES (
        v_user_id,
        p_moment_id,
        v_type,
        p_run_type,
        jsonb_build_object('moment_id', p_moment_id),
        'RUNNING',
        CURRENT_TIMESTAMP
    )
    RETURNING run_id INTO v_run_id;

    CALL sp_refresh_personal_orchestration(p_moment_id);

    UPDATE personal_ai_interpretation_runs
    SET
        status = 'COMPLETED',
        completed_at = CURRENT_TIMESTAMP,
        output_payload = jsonb_build_object(
            'status', 'completed',
            'moment_id', p_moment_id,
            'moment_type_code', v_type
        )
    WHERE run_id = v_run_id;

EXCEPTION WHEN OTHERS THEN
    UPDATE personal_ai_interpretation_runs
    SET
        status = 'FAILED',
        error_message = SQLERRM,
        completed_at = CURRENT_TIMESTAMP
    WHERE run_id = v_run_id;

    RAISE;
END;
$$;
-- >>>STMT<<<
CREATE OR REPLACE PROCEDURE sp_refresh_life_operations_runtime(
    p_moment_id UUID
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_user_id UUID;

    v_attention_score DECIMAL(5,2) := 70;
    v_recovery_score DECIMAL(5,2) := 70;
    v_mood_score DECIMAL(5,2) := 70;
    v_money_score DECIMAL(5,2) := 70;
    v_adjust_score DECIMAL(5,2) := 70;

    v_pressure_score DECIMAL(5,2);
    v_stability_score DECIMAL(5,2);
    v_cognitive_load_score DECIMAL(5,2);
    v_operational_balance_score DECIMAL(5,2);

    v_state_label VARCHAR(120);
    v_risk_label VARCHAR(150);
    v_summary TEXT;
BEGIN
    SELECT user_id
    INTO v_user_id
    FROM personal_moments
    WHERE moment_id = p_moment_id;

    -- Attention / focus load
    SELECT
        COALESCE(
            100 - AVG(
                CASE
                    WHEN intensity_level = 'HEAVY' THEN 75
                    WHEN intensity_level = 'MODERATE' THEN 45
                    WHEN intensity_level = 'LIGHT' THEN 20
                    ELSE 40
                END
            ),
            70
        )
    INTO v_attention_score
    FROM personal_life_attention_events
    WHERE moment_id = p_moment_id;

    -- Recovery strength
    SELECT
        COALESCE(
            AVG(
                CASE
                    WHEN energy_impact = 'HIGH' THEN 90
                    WHEN energy_impact = 'MODERATE' THEN 65
                    WHEN energy_impact = 'LOW' THEN 35
                    ELSE 50
                END
            ),
            70
        )
    INTO v_recovery_score
    FROM personal_life_recovery_events
    WHERE moment_id = p_moment_id;

    -- Mood stability
    SELECT
        COALESCE(AVG(mood_score), 70)
    INTO v_mood_score
    FROM personal_life_mood_events
    WHERE moment_id = p_moment_id;

    -- Money pressure
    SELECT
        COALESCE(
            100 - AVG(financial_pressure_score),
            70
        )
    INTO v_money_score
    FROM personal_money_events
    WHERE moment_id = p_moment_id
      AND moment_type_code = 'LIFE_OPERATIONS'
      AND is_voided = FALSE;

    -- Runtime adjustment health
    SELECT
        COALESCE(AVG(runtime_shift_score), 70)
    INTO v_adjust_score
    FROM personal_life_adjust_events
    WHERE moment_id = p_moment_id;

    -- Exact UI formulas
    v_pressure_score :=
        ROUND(
            (100 - v_attention_score) * 0.40
          + (100 - v_recovery_score) * 0.25
          + (100 - v_mood_score) * 0.20
          + (100 - v_money_score) * 0.15,
        2);

    v_stability_score :=
        ROUND(
            v_attention_score * 0.25
          + v_recovery_score * 0.25
          + v_mood_score * 0.20
          + v_money_score * 0.20
          + v_adjust_score * 0.10,
        2);

    v_cognitive_load_score :=
        ROUND(
            (100 - v_attention_score) * 0.50
          + v_pressure_score * 0.30
          + (100 - v_recovery_score) * 0.20,
        2);

    v_operational_balance_score :=
        ROUND(
            v_stability_score * 0.45
          + v_recovery_score * 0.25
          + v_money_score * 0.20
          + v_mood_score * 0.10,
        2);

    v_state_label :=
        CASE
            WHEN v_stability_score >= 85 THEN 'Stable Flow'
            WHEN v_stability_score >= 70 THEN 'Mostly Stable'
            WHEN v_stability_score >= 55 THEN 'Pressure Building'
            WHEN v_stability_score >= 40 THEN 'Needs Recovery'
            ELSE 'High Pressure'
        END;

    v_risk_label :=
        CASE
            WHEN v_pressure_score >= 70 THEN 'Pressure load is high'
            WHEN v_cognitive_load_score >= 65 THEN 'Cognitive load is rising'
            WHEN v_recovery_score < 50 THEN 'Recovery support is weak'
            WHEN v_money_score < 50 THEN 'Money pressure is affecting rhythm'
            ELSE 'No major risk detected'
        END;

    v_summary :=
        'Life Operations score is based on attention load, recovery strength, mood stability, money pressure, and runtime adjustment signals.';

    INSERT INTO personal_runtime_snapshots (
        moment_id,
        user_id,
        moment_type_code,
        runtime_state_label,
        runtime_summary,
        primary_score,
        secondary_score,
        risk_or_gap_label,
        trend_direction
    )
    VALUES (
        p_moment_id,
        v_user_id,
        'LIFE_OPERATIONS',
        v_state_label,
        v_summary,
        v_stability_score,
        v_operational_balance_score,
        v_risk_label,
        CASE
            WHEN v_stability_score >= 70 THEN 'UP'
            WHEN v_stability_score < 55 THEN 'DOWN'
            ELSE 'STABLE'
        END
    );

    INSERT INTO personal_metric_snapshots (
        user_id,
        moment_id,
        moment_type_code,
        metric_code,
        metric_label,
        metric_value,
        trend_direction
    )
    VALUES
    (v_user_id, p_moment_id, 'LIFE_OPERATIONS', 'STABILITY_SCORE', 'Stability Score', v_stability_score, 'STABLE'),
    (v_user_id, p_moment_id, 'LIFE_OPERATIONS', 'PRESSURE_SCORE', 'Pressure Score', v_pressure_score, 'STABLE'),
    (v_user_id, p_moment_id, 'LIFE_OPERATIONS', 'RECOVERY_SCORE', 'Recovery Score', v_recovery_score, 'STABLE'),
    (v_user_id, p_moment_id, 'LIFE_OPERATIONS', 'COGNITIVE_LOAD_SCORE', 'Cognitive Load', v_cognitive_load_score, 'STABLE'),
    (v_user_id, p_moment_id, 'LIFE_OPERATIONS', 'OPERATIONAL_BALANCE_SCORE', 'Operational Balance', v_operational_balance_score, 'STABLE');

END;
$$;
-- >>>STMT<<<
CREATE OR REPLACE PROCEDURE sp_refresh_future_building_runtime(
    p_moment_id UUID
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_user_id UUID;

    v_progress_score DECIMAL(5,2) := 70;
    v_milestone_score DECIMAL(5,2) := 70;
    v_opportunity_score DECIMAL(5,2) := 70;
    v_learning_score DECIMAL(5,2) := 70;
    v_pivot_score DECIMAL(5,2) := 70;
    v_money_investment_score DECIMAL(5,2) := 70;

    v_momentum_health DECIMAL(5,2);
    v_future_confidence_score DECIMAL(5,2);
    v_investment_effectiveness DECIMAL(5,2);
    v_breakthrough_potential_score DECIMAL(5,2);

    v_state_label VARCHAR(120);
    v_risk_label VARCHAR(150);
    v_summary TEXT;
BEGIN
    SELECT user_id
    INTO v_user_id
    FROM personal_moments
    WHERE moment_id = p_moment_id;

    -- Progress score
    SELECT
        COALESCE(
            AVG(
                CASE
                    WHEN progress_level = 'Breakthrough' THEN 95
                    WHEN progress_level = 'Major Progress' THEN 85
                    WHEN progress_level = 'Moderate Progress' THEN 70
                    WHEN progress_level = 'Small Step' THEN 55
                    ELSE 60
                END
            ),
            70
        )
    INTO v_progress_score
    FROM personal_future_progress_events
    WHERE moment_id = p_moment_id;

    -- Milestone score
    SELECT
        COALESCE(
            AVG(
                CASE
                    WHEN impact_level = 'Transformational' THEN 95
                    WHEN impact_level = 'Major' THEN 85
                    WHEN impact_level = 'Meaningful' THEN 70
                    WHEN impact_level = 'Minor' THEN 50
                    ELSE 60
                END
            ),
            70
        )
    INTO v_milestone_score
    FROM personal_future_milestone_events
    WHERE moment_id = p_moment_id;

    -- Opportunity score
    SELECT
        COALESCE(
            AVG(
                CASE
                    WHEN potential_level = 'Game-Changing' THEN 95
                    WHEN potential_level = 'High' THEN 85
                    WHEN potential_level = 'Moderate' THEN 65
                    WHEN potential_level = 'Low' THEN 45
                    ELSE 60
                END
            ),
            70
        )
    INTO v_opportunity_score
    FROM personal_future_opportunity_events
    WHERE moment_id = p_moment_id;

    -- Learning score
    SELECT
        COALESCE(
            AVG(
                CASE
                    WHEN relevance_level = 'Transformational' THEN 95
                    WHEN relevance_level = 'High Leverage' THEN 85
                    WHEN relevance_level = 'Important' THEN 70
                    WHEN relevance_level = 'Useful' THEN 55
                    ELSE 60
                END
            ),
            70
        )
    INTO v_learning_score
    FROM personal_future_learning_events
    WHERE moment_id = p_moment_id;

    -- Pivot/adaptability score
    SELECT
        COALESCE(
            AVG(
                CASE
                    WHEN confidence_level = 'High' THEN 85
                    WHEN confidence_level = 'Medium' THEN 65
                    WHEN confidence_level = 'Low' THEN 45
                    ELSE 60
                END
            ),
            70
        )
    INTO v_pivot_score
    FROM personal_future_pivot_events
    WHERE moment_id = p_moment_id;

    -- Money/investment effectiveness signal
    SELECT
        COALESCE(AVG(investment_score), 70)
    INTO v_money_investment_score
    FROM personal_money_events
    WHERE moment_id = p_moment_id
      AND moment_type_code = 'FUTURE_BUILDING'
      AND is_voided = FALSE;

    -- Exact UI formulas
    v_momentum_health :=
        ROUND(
            v_progress_score * 0.35
          + v_milestone_score * 0.20
          + v_learning_score * 0.15
          + v_opportunity_score * 0.20
          + v_pivot_score * 0.10,
        2);

    v_future_confidence_score :=
        ROUND(
            v_progress_score * 0.30
          + v_milestone_score * 0.25
          + v_opportunity_score * 0.20
          + v_learning_score * 0.15
          + v_pivot_score * 0.10,
        2);

    v_investment_effectiveness :=
        ROUND(
            v_money_investment_score * 0.40
          + v_learning_score * 0.25
          + v_progress_score * 0.25
          + v_opportunity_score * 0.10,
        2);

    v_breakthrough_potential_score :=
        ROUND(
            v_opportunity_score * 0.35
          + v_progress_score * 0.25
          + v_milestone_score * 0.20
          + v_learning_score * 0.10
          + v_pivot_score * 0.10,
        2);

    v_state_label :=
        CASE
            WHEN v_momentum_health >= 85 THEN 'Momentum Building Fast'
            WHEN v_momentum_health >= 70 THEN 'Momentum Building'
            WHEN v_momentum_health >= 55 THEN 'Direction Forming'
            WHEN v_momentum_health >= 40 THEN 'Progress Needs Focus'
            ELSE 'Future Momentum Blocked'
        END;

    v_risk_label :=
        CASE
            WHEN v_progress_score < 50 THEN 'Progress activity is weak'
            WHEN v_opportunity_score < 50 THEN 'Opportunity pipeline is low'
            WHEN v_learning_score < 50 THEN 'Capability growth needs attention'
            WHEN v_investment_effectiveness < 50 THEN 'Investment return is unclear'
            ELSE 'No major future-building risk detected'
        END;

    v_summary :=
        'Future Building score is based on progress, milestones, opportunity, learning, adaptability, and money invested toward future growth.';

    INSERT INTO personal_runtime_snapshots (
        moment_id,
        user_id,
        moment_type_code,
        runtime_state_label,
        runtime_summary,
        primary_score,
        secondary_score,
        risk_or_gap_label,
        trend_direction
    )
    VALUES (
        p_moment_id,
        v_user_id,
        'FUTURE_BUILDING',
        v_state_label,
        v_summary,
        v_momentum_health,
        v_breakthrough_potential_score,
        v_risk_label,
        CASE
            WHEN v_momentum_health >= 70 THEN 'UP'
            WHEN v_momentum_health < 55 THEN 'DOWN'
            ELSE 'STABLE'
        END
    );

    INSERT INTO personal_metric_snapshots (
        user_id,
        moment_id,
        moment_type_code,
        metric_code,
        metric_label,
        metric_value,
        trend_direction
    )
    VALUES
    (v_user_id, p_moment_id, 'FUTURE_BUILDING', 'MOMENTUM_HEALTH', 'Momentum Health', v_momentum_health, 'STABLE'),
    (v_user_id, p_moment_id, 'FUTURE_BUILDING', 'FUTURE_CONFIDENCE_SCORE', 'Future Confidence', v_future_confidence_score, 'STABLE'),
    (v_user_id, p_moment_id, 'FUTURE_BUILDING', 'OPPORTUNITY_SCORE', 'Opportunity Score', v_opportunity_score, 'STABLE'),
    (v_user_id, p_moment_id, 'FUTURE_BUILDING', 'INVESTMENT_EFFECTIVENESS', 'Investment Effectiveness', v_investment_effectiveness, 'STABLE'),
    (v_user_id, p_moment_id, 'FUTURE_BUILDING', 'BREAKTHROUGH_POTENTIAL', 'Breakthrough Potential', v_breakthrough_potential_score, 'STABLE');

END;
$$;
-- >>>STMT<<<
CREATE OR REPLACE PROCEDURE sp_refresh_lifestyle_runtime(
    p_moment_id UUID
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_user_id UUID;

    v_experience_score DECIMAL(5,2) := 70;
    v_wellbeing_score DECIMAL(5,2) := 70;
    v_discovery_score DECIMAL(5,2) := 70;
    v_expression_score DECIMAL(5,2) := 70;
    v_adjust_score DECIMAL(5,2) := 70;
    v_money_roi_score DECIMAL(5,2) := 70;

    v_lifestyle_vitality DECIMAL(5,2);
    v_fulfillment_score DECIMAL(5,2);
    v_lifestyle_roi DECIMAL(5,2);
    v_creativity_balance DECIMAL(5,2);
    v_best_day_driver_score DECIMAL(5,2);

    v_state_label VARCHAR(120);
    v_risk_label VARCHAR(150);
    v_summary TEXT;
BEGIN
    SELECT user_id
    INTO v_user_id
    FROM personal_moments
    WHERE moment_id = p_moment_id;

    -- Experience quality
    SELECT COALESCE(
        AVG(
            CASE
                WHEN experience_quality = 'Exceptional' THEN 95
                WHEN experience_quality = 'Memorable' THEN 85
                WHEN experience_quality = 'Enjoyable' THEN 70
                WHEN experience_quality = 'Ordinary' THEN 50
                ELSE 60
            END
        ), 70
    )
    INTO v_experience_score
    FROM personal_lifestyle_experience_events
    WHERE moment_id = p_moment_id;

    -- Wellbeing state
    SELECT COALESCE(
        AVG(
            CASE
                WHEN wellbeing_state = 'Excellent' THEN 95
                WHEN wellbeing_state = 'Good' THEN 80
                WHEN wellbeing_state = 'Moderate' THEN 60
                WHEN wellbeing_state = 'Low' THEN 40
                ELSE 60
            END
        ), 70
    )
    INTO v_wellbeing_score
    FROM personal_lifestyle_wellbeing_events
    WHERE moment_id = p_moment_id;

    -- Discovery / exploration
    SELECT COALESCE(
        AVG(
            CASE
                WHEN impact_level = 'Life-Changing' THEN 95
                WHEN impact_level = 'Inspiring' THEN 85
                WHEN impact_level = 'Useful' THEN 70
                WHEN impact_level = 'Interesting' THEN 55
                ELSE 60
            END
        ), 70
    )
    INTO v_discovery_score
    FROM personal_lifestyle_discovery_events
    WHERE moment_id = p_moment_id;

    -- Expression / creativity
    SELECT COALESCE(
        AVG(
            CASE
                WHEN satisfaction_level = 'Exceptional' THEN 95
                WHEN satisfaction_level = 'High' THEN 80
                WHEN satisfaction_level = 'Moderate' THEN 60
                WHEN satisfaction_level = 'Low' THEN 40
                ELSE 60
            END
        ), 70
    )
    INTO v_expression_score
    FROM personal_lifestyle_expression_events
    WHERE moment_id = p_moment_id;

    -- Lifestyle adjustment readiness
    SELECT COALESCE(AVG(change_readiness_score), 70)
    INTO v_adjust_score
    FROM personal_lifestyle_adjust_events
    WHERE moment_id = p_moment_id;

    -- Money ROI from lifestyle spends
    SELECT COALESCE(AVG(roi_signal_score), 70)
    INTO v_money_roi_score
    FROM personal_money_events
    WHERE moment_id = p_moment_id
      AND moment_type_code = 'LIFESTYLE'
      AND is_voided = FALSE;

    -- Exact UI formulas
    v_fulfillment_score :=
        ROUND(
            v_experience_score * 0.35
          + v_wellbeing_score * 0.25
          + v_discovery_score * 0.15
          + v_expression_score * 0.15
          + v_adjust_score * 0.10,
        2);

    v_lifestyle_roi :=
        ROUND(
            v_money_roi_score * 0.40
          + v_experience_score * 0.25
          + v_wellbeing_score * 0.15
          + v_discovery_score * 0.10
          + v_expression_score * 0.10,
        2);

    v_creativity_balance :=
        ROUND(
            v_expression_score * 0.45
          + v_discovery_score * 0.25
          + v_experience_score * 0.15
          + v_wellbeing_score * 0.15,
        2);

    v_best_day_driver_score :=
        ROUND(
            v_experience_score * 0.35
          + v_wellbeing_score * 0.25
          + v_discovery_score * 0.20
          + v_expression_score * 0.10
          + v_lifestyle_roi * 0.10,
        2);

    v_lifestyle_vitality :=
        ROUND(
            v_fulfillment_score * 0.35
          + v_wellbeing_score * 0.25
          + v_lifestyle_roi * 0.20
          + v_creativity_balance * 0.10
          + v_best_day_driver_score * 0.10,
        2);

    v_state_label :=
        CASE
            WHEN v_lifestyle_vitality >= 85 THEN 'Lifestyle Flourishing'
            WHEN v_lifestyle_vitality >= 70 THEN 'Lifestyle Enriched'
            WHEN v_lifestyle_vitality >= 55 THEN 'Lifestyle Rebalancing'
            WHEN v_lifestyle_vitality >= 40 THEN 'Fulfillment Needs Attention'
            ELSE 'Lifestyle Energy Low'
        END;

    v_risk_label :=
        CASE
            WHEN v_wellbeing_score < 50 THEN 'Wellbeing is under-supported'
            WHEN v_experience_score < 50 THEN 'Experiences are not creating enough fulfillment'
            WHEN v_lifestyle_roi < 50 THEN 'Lifestyle spend value is unclear'
            WHEN v_expression_score < 50 THEN 'Creative expression is low'
            ELSE 'No major lifestyle risk detected'
        END;

    v_summary :=
        'Lifestyle score is based on experiences, wellbeing, discovery, expression, lifestyle ROI, and adjustment readiness.';

    INSERT INTO personal_runtime_snapshots (
        moment_id,
        user_id,
        moment_type_code,
        runtime_state_label,
        runtime_summary,
        primary_score,
        secondary_score,
        risk_or_gap_label,
        trend_direction
    )
    VALUES (
        p_moment_id,
        v_user_id,
        'LIFESTYLE',
        v_state_label,
        v_summary,
        v_lifestyle_vitality,
        v_fulfillment_score,
        v_risk_label,
        CASE
            WHEN v_lifestyle_vitality >= 70 THEN 'UP'
            WHEN v_lifestyle_vitality < 55 THEN 'DOWN'
            ELSE 'STABLE'
        END
    );

    INSERT INTO personal_metric_snapshots (
        user_id,
        moment_id,
        moment_type_code,
        metric_code,
        metric_label,
        metric_value,
        trend_direction
    )
    VALUES
    (v_user_id, p_moment_id, 'LIFESTYLE', 'LIFESTYLE_VITALITY', 'Lifestyle Vitality', v_lifestyle_vitality, 'STABLE'),
    (v_user_id, p_moment_id, 'LIFESTYLE', 'FULFILLMENT_SCORE', 'Fulfillment Score', v_fulfillment_score, 'STABLE'),
    (v_user_id, p_moment_id, 'LIFESTYLE', 'LIFESTYLE_ROI', 'Lifestyle ROI', v_lifestyle_roi, 'STABLE'),
    (v_user_id, p_moment_id, 'LIFESTYLE', 'CREATIVITY_BALANCE', 'Creativity Balance', v_creativity_balance, 'STABLE'),
    (v_user_id, p_moment_id, 'LIFESTYLE', 'BEST_DAY_DRIVER_SCORE', 'Best-Day Driver Score', v_best_day_driver_score, 'STABLE');

END;
$$;
-- >>>STMT<<<
CREATE OR REPLACE PROCEDURE sp_refresh_relationship_runtime(
																    p_moment_id UUID
																)
																LANGUAGE plpgsql
																AS $$
																DECLARE
																    v_user_id UUID;
																
																    v_connection_score DECIMAL(5,2) := 70;
																    v_support_score DECIMAL(5,2) := 70;
																    v_experience_score DECIMAL(5,2) := 70;
																    v_investment_score DECIMAL(5,2) := 70;
																    v_adjust_score DECIMAL(5,2) := 70;
																    v_money_roi_score DECIMAL(5,2) := 70;
																
																    v_connection_health DECIMAL(5,2);
																    v_trust_score DECIMAL(5,2);
																    v_support_balance DECIMAL(5,2);
																    v_relationship_roi DECIMAL(5,2);
																    v_quality_time_score DECIMAL(5,2);
																
																    v_state_label VARCHAR(120);
																    v_risk_label VARCHAR(150);
																    v_summary TEXT;
																BEGIN
																    SELECT user_id
																    INTO v_user_id
																    FROM personal_moments
																    WHERE moment_id = p_moment_id;
																
																    SELECT COALESCE(
																        AVG(
																            CASE
																                WHEN connection_quality = 'Memorable' THEN 95
																                WHEN connection_quality = 'Deep' THEN 85
																                WHEN connection_quality = 'Meaningful' THEN 75
																                WHEN connection_quality = 'Routine' THEN 55
																                ELSE 60
																            END
																        ), 70
																    )
																    INTO v_connection_score
																    FROM personal_relationship_connection_events
																    WHERE moment_id = p_moment_id;
																
																    SELECT COALESCE(
																        AVG(
																            CASE
																                WHEN impact_level = 'Transformational' THEN 95
																                WHEN impact_level = 'Important' THEN 85
																                WHEN impact_level = 'Meaningful' THEN 70
																                WHEN impact_level = 'Small' THEN 50
																                ELSE 60
																            END
																        ), 70
																    )
																    INTO v_support_score
																    FROM personal_relationship_support_events
																    WHERE moment_id = p_moment_id;
																
																    SELECT COALESCE(
																        AVG(
																            CASE
																                WHEN value_received = 'Life Enriching' THEN 95
																                WHEN value_received = 'Relationship Building' THEN 85
																                WHEN value_received = 'Excellent Value' THEN 80
																                WHEN value_received = 'Worth It' THEN 70
																                WHEN value_received = 'Okay' THEN 50
																                ELSE 60
																            END
																        ), 70
																    )
																    INTO v_experience_score
																    FROM personal_relationship_experience_events
																    WHERE moment_id = p_moment_id;
																
																    SELECT COALESCE(
																        AVG(
																            CASE
																                WHEN perceived_value = 'Exceptional' THEN 95
																                WHEN perceived_value = 'High' THEN 80
																                WHEN perceived_value = 'Moderate' THEN 65
																                WHEN perceived_value = 'Low' THEN 45
																                ELSE 60
																            END
																        ), 70
																    )
																    INTO v_investment_score
																    FROM personal_relationship_investment_events
																    WHERE moment_id = p_moment_id;
																
																    SELECT COALESCE(AVG(relationship_readiness_score), 70)
																    INTO v_adjust_score
																    FROM personal_relationship_adjust_events
																    WHERE moment_id = p_moment_id;
																
																    SELECT COALESCE(AVG(roi_signal_score), 70)
																    INTO v_money_roi_score
																    FROM personal_money_events
																    WHERE moment_id = p_moment_id
																      AND moment_type_code = 'RELATIONSHIPS'
																      AND is_voided = FALSE;
																
																    v_connection_health :=
																        ROUND(
																            v_connection_score * 0.35
																          + v_support_score * 0.20
																          + v_experience_score * 0.20
																          + v_investment_score * 0.15
																          + v_adjust_score * 0.10,
																        2);
																
																    v_trust_score :=
																        ROUND(
																            v_connection_score * 0.40
																          + v_support_score * 0.30
																          + v_experience_score * 0.15
																          + v_adjust_score * 0.15,
																        2);
																
																    v_support_balance :=
																        ROUND(
																            v_support_score * 0.45
																          + v_connection_score * 0.25
																          + v_investment_score * 0.15
																          + v_adjust_score * 0.15,
																        2);
																
																    v_relationship_roi :=
																        ROUND(
																            v_money_roi_score * 0.35
																          + v_experience_score * 0.25
																          + v_investment_score * 0.20
																          + v_connection_score * 0.20,
																        2);
																
																    v_quality_time_score :=
																        ROUND(
																            v_connection_score * 0.40
																          + v_experience_score * 0.30
																          + v_support_score * 0.15
																          + v_adjust_score * 0.15,
																        2);
																
																    v_state_label :=
																        CASE
																            WHEN v_connection_health >= 85 THEN 'Connection Flourishing'
																            WHEN v_connection_health >= 70 THEN 'Connection Growing'
																            WHEN v_connection_health >= 55 THEN 'Connection Needs Presence'
																            WHEN v_connection_health >= 40 THEN 'Relationship Needs Attention'
																            ELSE 'Connection At Risk'
																        END;
																
																    v_risk_label :=
																        CASE
																            WHEN v_connection_score < 50 THEN 'Connection quality is low'
																            WHEN v_support_balance < 50 THEN 'Support balance needs attention'
																            WHEN v_trust_score < 50 THEN 'Trust signal is weak'
																            WHEN v_relationship_roi < 50 THEN 'Relationship investment value is unclear'
																            ELSE 'No major relationship risk detected'
																        END;
																
																    v_summary :=
																        'Relationship score is based on connection quality, support, shared experiences, relationship investment, trust, and quality time.';
																
																    INSERT INTO personal_runtime_snapshots (
																        moment_id,
																        user_id,
																        moment_type_code,
																        runtime_state_label,
																        runtime_summary,
																        primary_score,
																        secondary_score,
																        risk_or_gap_label,
																        trend_direction
																    )
																    VALUES (
																        p_moment_id,
																        v_user_id,
																        'RELATIONSHIPS',
																        v_state_label,
																        v_summary,
																        v_connection_health,
																        v_trust_score,
																        v_risk_label,
																        CASE
																            WHEN v_connection_health >= 70 THEN 'UP'
																            WHEN v_connection_health < 55 THEN 'DOWN'
																            ELSE 'STABLE'
																        END
																    );
																
																    INSERT INTO personal_metric_snapshots (
																        user_id,
																        moment_id,
																        moment_type_code,
																        metric_code,
																        metric_label,
																        metric_value,
																        trend_direction
																    )
																    VALUES
																    (v_user_id, p_moment_id, 'RELATIONSHIPS', 'CONNECTION_HEALTH', 'Connection Health', v_connection_health, 'STABLE'),
																    (v_user_id, p_moment_id, 'RELATIONSHIPS', 'TRUST_SCORE', 'Trust Score', v_trust_score, 'STABLE'),
																    (v_user_id, p_moment_id, 'RELATIONSHIPS', 'SUPPORT_BALANCE', 'Support Balance', v_support_balance, 'STABLE'),
																    (v_user_id, p_moment_id, 'RELATIONSHIPS', 'RELATIONSHIP_ROI', 'Relationship ROI', v_relationship_roi, 'STABLE'),
																    (v_user_id, p_moment_id, 'RELATIONSHIPS', 'QUALITY_TIME_SCORE', 'Quality-Time Score', v_quality_time_score, 'STABLE');
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE PROCEDURE sp_refresh_personal_moment_highlights(
																    p_user_id UUID
																)
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    DELETE FROM personal_moment_highlights
																    WHERE user_id = p_user_id;
																
																    INSERT INTO personal_moment_highlights
																    (
																        user_id,
																        moment_id,
																        moment_type_code,
																        highlight_title,
																        highlight_type,
																        impact_label,
																        impact_score,
																        amount,
																        occurred_at
																    )
																    SELECT
																        e.user_id,
																        e.moment_id,
																        e.moment_type_code,
																
																        e.event_title,
																
																        'BEST_MOMENT',
																
																        CASE
																            WHEN e.mood_delta >= 20 THEN 'Major Positive Shift'
																            WHEN e.mood_delta >= 10 THEN 'Positive Shift'
																            ELSE 'Meaningful Event'
																        END,
																
																        scored.impact_score,
																
																        e.amount,
																
																        e.event_date
																
																    FROM personal_events e
																    CROSS JOIN LATERAL (
																        SELECT fn_personal_highlight_impact_score(
																            COALESCE(e.mood_delta,50),
																            COALESCE(e.outcome_score,50),
																            COALESCE(e.financial_weight_score,50),
																            fn_personal_recency_score(e.event_date)
																        ) AS impact_score
																    ) scored
																
																    WHERE e.user_id = p_user_id
																
																    ORDER BY scored.impact_score DESC
																
																    LIMIT 50;
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE PROCEDURE sp_refresh_personal_moment_turning_points(
																    p_user_id UUID
																)
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    DELETE FROM personal_moment_turning_points
																    WHERE user_id = p_user_id;
																
																    INSERT INTO personal_moment_turning_points
																    (
																        user_id,
																        moment_id,
																        moment_type_code,
																        turning_point_title,
																        turning_point_type,
																        turning_point_description,
																        impact_score,
																        occurred_at
																    )
																    SELECT
																        e.user_id,
																
																        e.moment_id,
																
																        e.moment_type_code,
																
																        e.event_title,
																
																        'BEHAVIOR_SHIFT',
																
																        'Detected significant behavioral change',
																
																        fn_personal_turning_point_impact_score(
																            COALESCE(e.behavior_shift_score,50),
																            COALESCE(e.duration_score,50),
																            COALESCE(e.outcome_score,50),
																            COALESCE(e.mood_delta,50)
																        ),
																
																        e.event_date
																
																    FROM personal_events e
																
																    WHERE e.user_id = p_user_id
																      AND COALESCE(e.behavior_shift_score,0) >= 70;
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE PROCEDURE sp_refresh_personal_memory_identity(
																    p_moment_id UUID
																)
																LANGUAGE plpgsql
																AS $$
																DECLARE
																    v_user_id UUID;
																    v_type VARCHAR(50);
																    v_score DECIMAL(5,2);
																    v_identity_title VARCHAR(100);
																    v_summary TEXT;
																BEGIN
																    SELECT pm.user_id, mt.moment_type_code
																    INTO v_user_id, v_type
																    FROM personal_moments pm
																    JOIN personal_moment_types mt
																        ON mt.moment_type_id = pm.moment_type_id
																    WHERE pm.moment_id = p_moment_id;
																
																    SELECT COALESCE(AVG(primary_score), 70)
																    INTO v_score
																    FROM personal_runtime_snapshots
																    WHERE moment_id = p_moment_id;
																
																    v_identity_title :=
																        CASE v_type
																            WHEN 'LIFE_OPERATIONS' THEN 'Structured Stabilizer'
																            WHEN 'FUTURE_BUILDING' THEN 'Consistent Builder'
																            WHEN 'LIFESTYLE' THEN 'Experience Seeker'
																            WHEN 'RELATIONSHIPS' THEN 'Connection Builder'
																            ELSE 'Personal Builder'
																        END;
																
																    v_summary :=
																        CASE v_type
																            WHEN 'LIFE_OPERATIONS' THEN 'You create stability through recovery, planning, and rhythm.'
																            WHEN 'FUTURE_BUILDING' THEN 'You grow through consistent learning, execution, and progress.'
																            WHEN 'LIFESTYLE' THEN 'You create fulfillment through experiences, discovery, and creativity.'
																            WHEN 'RELATIONSHIPS' THEN 'You strengthen life through connection, support, and shared moments.'
																            ELSE 'Your identity is forming through repeated moment patterns.'
																        END;
																
																    UPDATE personal_memory_identity_snapshots
																    SET is_current = FALSE
																    WHERE moment_id = p_moment_id;
																
																    INSERT INTO personal_memory_identity_snapshots (
																        user_id,
																        moment_id,
																        moment_type_code,
																        identity_title,
																        confidence_pct,
																        confidence_trend_pct,
																        identity_summary,
																        identity_visual_type,
																        snapshot_month,
																        is_current
																    )
																    VALUES (
																        v_user_id,
																        p_moment_id,
																        v_type,
																        v_identity_title,
																        fn_personal_identity_confidence_score(v_score, 80, 80),
																        NULL,
																        v_summary,
																        v_type,
																        DATE_TRUNC('month', CURRENT_DATE)::DATE,
																        TRUE
																    );
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE PROCEDURE sp_refresh_personal_memory_drivers(
																    p_moment_id UUID
																)
																LANGUAGE plpgsql
																AS $$
																DECLARE
																    v_user_id UUID;
																    v_type VARCHAR(50);
																BEGIN
																    SELECT pm.user_id, mt.moment_type_code
																    INTO v_user_id, v_type
																    FROM personal_moments pm
																    JOIN personal_moment_types mt
																        ON mt.moment_type_id = pm.moment_type_id
																    WHERE pm.moment_id = p_moment_id;
																
																    UPDATE personal_memory_driver_rankings
																    SET is_current = FALSE
																    WHERE moment_id = p_moment_id;
																
																    INSERT INTO personal_memory_driver_rankings (
																        user_id,
																        moment_id,
																        moment_type_code,
																        driver_category,
																        driver_rank,
																        driver_name,
																        impact_pct,
																        impact_description,
																        return_multiplier,
																        snapshot_month,
																        is_current
																    )
																    SELECT
																        v_user_id,
																        p_moment_id,
																        v_type,
																        'POSITIVE',
																        ROW_NUMBER() OVER (ORDER BY AVG(metric_value) DESC),
																        metric_label,
																        ROUND(AVG(metric_value), 2),
																        metric_label || ' is a positive driver in this moment.',
																        NULL,
																        DATE_TRUNC('month', CURRENT_DATE)::DATE,
																        TRUE
																    FROM personal_metric_snapshots
																    WHERE moment_id = p_moment_id
																    GROUP BY metric_label
																    ORDER BY AVG(metric_value) DESC
																    LIMIT 3;
																
																    INSERT INTO personal_memory_driver_rankings (
																        user_id,
																        moment_id,
																        moment_type_code,
																        driver_category,
																        driver_rank,
																        driver_name,
																        impact_pct,
																        impact_description,
																        return_multiplier,
																        snapshot_month,
																        is_current
																    )
																    SELECT
																        v_user_id,
																        p_moment_id,
																        v_type,
																        'HIGHEST_RETURN',
																        ROW_NUMBER() OVER (ORDER BY AVG(metric_value) DESC),
																        metric_label,
																        ROUND(AVG(metric_value), 2),
																        metric_label || ' creates high return for this personal moment.',
																        fn_personal_growth_edge_multiplier(AVG(metric_value), 10),
																        DATE_TRUNC('month', CURRENT_DATE)::DATE,
																        TRUE
																    FROM personal_metric_snapshots
																    WHERE moment_id = p_moment_id
																    GROUP BY metric_label
																    ORDER BY AVG(metric_value) DESC
																    LIMIT 3;
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE PROCEDURE sp_refresh_personal_emotional_dna(
																    p_moment_id UUID
																)
																LANGUAGE plpgsql
																AS $$
																DECLARE
																    v_user_id UUID;
																    v_type VARCHAR(50);
																BEGIN
																    SELECT pm.user_id, mt.moment_type_code
																    INTO v_user_id, v_type
																    FROM personal_moments pm
																    JOIN personal_moment_types mt
																        ON mt.moment_type_id = pm.moment_type_id
																    WHERE pm.moment_id = p_moment_id;
																
																    UPDATE personal_memory_emotional_dna
																    SET is_current = FALSE
																    WHERE moment_id = p_moment_id;
																
																    INSERT INTO personal_memory_emotional_dna (
																        user_id,
																        moment_id,
																        moment_type_code,
																        emotion_name,
																        emotion_pct,
																        emotion_rank,
																        dna_summary,
																        snapshot_month,
																        is_current
																    )
																    SELECT
																        v_user_id,
																        p_moment_id,
																        v_type,
																        emotion_name,
																        emotion_pct,
																        emotion_rank,
																        emotion_name || ' is part of the dominant emotional pattern.',
																        DATE_TRUNC('month', CURRENT_DATE)::DATE,
																        TRUE
																    FROM (
																        SELECT *
																        FROM (
																            VALUES
																                (CASE WHEN v_type = 'LIFE_OPERATIONS' THEN 'Calm'
																                      WHEN v_type = 'FUTURE_BUILDING' THEN 'Confidence'
																                      WHEN v_type = 'LIFESTYLE' THEN 'Joy'
																                      ELSE 'Trust' END, 40::DECIMAL, 1),
																
																                (CASE WHEN v_type = 'LIFE_OPERATIONS' THEN 'Relief'
																                      WHEN v_type = 'FUTURE_BUILDING' THEN 'Hope'
																                      WHEN v_type = 'LIFESTYLE' THEN 'Fulfillment'
																                      ELSE 'Belonging' END, 35::DECIMAL, 2),
																
																                (CASE WHEN v_type = 'LIFE_OPERATIONS' THEN 'Stress'
																                      WHEN v_type = 'FUTURE_BUILDING' THEN 'Achievement'
																                      WHEN v_type = 'LIFESTYLE' THEN 'Excitement'
																                      ELSE 'Connection' END, 25::DECIMAL, 3)
																        ) AS e(emotion_name, emotion_pct, emotion_rank)
																    ) x;
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE PROCEDURE sp_refresh_personal_evolution(
																    p_moment_id UUID
																)
																LANGUAGE plpgsql
																AS $$
																DECLARE
																    v_user_id UUID;
																    v_type VARCHAR(50);
																    v_score DECIMAL(5,2);
																    v_previous VARCHAR(100);
																    v_current VARCHAR(100);
																    v_emerging VARCHAR(100);
																BEGIN
																    SELECT pm.user_id, mt.moment_type_code
																    INTO v_user_id, v_type
																    FROM personal_moments pm
																    JOIN personal_moment_types mt
																        ON mt.moment_type_id = pm.moment_type_id
																    WHERE pm.moment_id = p_moment_id;
																
																    SELECT COALESCE(AVG(primary_score), 70)
																    INTO v_score
																    FROM personal_runtime_snapshots
																    WHERE moment_id = p_moment_id;
																
																    IF v_type = 'LIFE_OPERATIONS' THEN
																        v_previous := 'Reactive';
																        v_current := CASE WHEN v_score >= 70 THEN 'Stable' ELSE 'Recovering' END;
																        v_emerging := 'Structured';
																
																    ELSIF v_type = 'FUTURE_BUILDING' THEN
																        v_previous := 'Exploring';
																        v_current := CASE WHEN v_score >= 70 THEN 'Building' ELSE 'Searching' END;
																        v_emerging := 'Accelerating';
																
																    ELSIF v_type = 'LIFESTYLE' THEN
																        v_previous := 'Passive';
																        v_current := CASE WHEN v_score >= 70 THEN 'Intentional' ELSE 'Rebalancing' END;
																        v_emerging := 'Flourishing';
																
																    ELSE
																        v_previous := 'Disconnected';
																        v_current := CASE WHEN v_score >= 70 THEN 'Connected' ELSE 'Rebuilding' END;
																        v_emerging := 'Growing';
																    END IF;
																
																    UPDATE personal_memory_evolution_snapshots
																    SET is_current = FALSE
																    WHERE moment_id = p_moment_id;
																
																    INSERT INTO personal_memory_evolution_snapshots (
																        user_id,
																        moment_id,
																        moment_type_code,
																        previous_stage,
																        current_stage,
																        emerging_stage,
																        evolution_confidence_pct,
																        transition_date,
																        snapshot_month,
																        is_current
																    )
																    VALUES (
																        v_user_id,
																        p_moment_id,
																        v_type,
																        v_previous,
																        v_current,
																        v_emerging,
																        fn_personal_clamp_score(v_score),
																        CURRENT_DATE,
																        DATE_TRUNC('month', CURRENT_DATE)::DATE,
																        TRUE
																    );
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE PROCEDURE sp_refresh_personal_final_memory(
																    p_moment_id UUID
																)
																LANGUAGE plpgsql
																AS $$
																BEGIN
																    CALL sp_refresh_personal_memory(p_moment_id);
																    CALL sp_refresh_personal_advanced_memory(p_moment_id);
																    CALL sp_refresh_personal_memory_identity(p_moment_id);
																    CALL sp_refresh_personal_memory_drivers(p_moment_id);
																    CALL sp_refresh_personal_emotional_dna(p_moment_id);
																    CALL sp_refresh_personal_evolution(p_moment_id);
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE PROCEDURE sp_refresh_personal_life_health(
																    p_user_id UUID
																)
																LANGUAGE plpgsql
																AS $$
																DECLARE
																    v_stability DECIMAL(5,2);
																    v_growth DECIMAL(5,2);
																    v_fulfillment DECIMAL(5,2);
																    v_relationship DECIMAL(5,2);
																
																    v_life_health DECIMAL(5,2);
																BEGIN
																
																    SELECT COALESCE(AVG(primary_score),70)
																    INTO v_stability
																    FROM personal_runtime_snapshots prs
																    JOIN personal_moments pm
																      ON pm.moment_id = prs.moment_id
																    JOIN personal_moment_types mt
																      ON mt.moment_type_id = pm.moment_type_id
																    WHERE pm.user_id = p_user_id
																      AND mt.moment_type_code = 'LIFE_OPERATIONS';
																
																    SELECT COALESCE(AVG(primary_score),70)
																    INTO v_growth
																    FROM personal_runtime_snapshots prs
																    JOIN personal_moments pm
																      ON pm.moment_id = prs.moment_id
																    JOIN personal_moment_types mt
																      ON mt.moment_type_id = pm.moment_type_id
																    WHERE pm.user_id = p_user_id
																      AND mt.moment_type_code = 'FUTURE_BUILDING';
																
																    SELECT COALESCE(AVG(primary_score),70)
																    INTO v_fulfillment
																    FROM personal_runtime_snapshots prs
																    JOIN personal_moments pm
																      ON pm.moment_id = prs.moment_id
																    JOIN personal_moment_types mt
																      ON mt.moment_type_id = pm.moment_type_id
																    WHERE pm.user_id = p_user_id
																      AND mt.moment_type_code = 'LIFESTYLE';
																
																    SELECT COALESCE(AVG(primary_score),70)
																    INTO v_relationship
																    FROM personal_runtime_snapshots prs
																    JOIN personal_moments pm
																      ON pm.moment_id = prs.moment_id
																    JOIN personal_moment_types mt
																      ON mt.moment_type_id = pm.moment_type_id
																    WHERE pm.user_id = p_user_id
																      AND mt.moment_type_code = 'RELATIONSHIPS';
																
																    v_life_health :=
																        fn_personal_life_health_score(
																            v_stability,
																            v_growth,
																            v_fulfillment,
																            v_relationship
																        );
																
																    UPDATE personal_life_health_snapshots
																       SET is_current = FALSE
																     WHERE user_id = p_user_id;
																
																    INSERT INTO personal_life_health_snapshots
																    (
																        user_id,
																        life_health_score,
																        health_status_label,
																        snapshot_month,
																        is_current
																    )
																    VALUES
																    (
																        p_user_id,
																        v_life_health,
																        fn_personal_score_status_label(v_life_health),
																        DATE_TRUNC('month',CURRENT_DATE)::DATE,
																        TRUE
																    );
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE PROCEDURE sp_refresh_personal_life_dimensions(
																    p_user_id UUID
																)
																LANGUAGE plpgsql
																AS $$
																DECLARE
																    v_stress DECIMAL(5,2);
																    v_capacity DECIMAL(5,2);
																    v_growth DECIMAL(5,2);
																    v_fulfillment DECIMAL(5,2);
																BEGIN
																
																    DELETE FROM personal_life_dimension_scores
																    WHERE user_id = p_user_id
																      AND snapshot_month =
																          DATE_TRUNC('month',CURRENT_DATE)::DATE;
																
																    v_stress :=
																        fn_personal_stress_score(
																            60,
																            55,
																            40
																        );
																
																    v_capacity :=
																        fn_personal_capacity_score(
																            75,
																            70,
																            72
																        );
																
																    v_growth := 78;
																    v_fulfillment := 74;
																
																    INSERT INTO personal_life_dimension_scores
																    (
																        user_id,
																        dimension_code,
																        dimension_label,
																        dimension_score,
																        status_label,
																        snapshot_month,
																        is_current
																    )
																    VALUES
																    (
																        p_user_id,
																        'STRESS',
																        'Stress',
																        v_stress,
																        fn_personal_score_status_label(100-v_stress),
																        DATE_TRUNC('month',CURRENT_DATE)::DATE,
																        TRUE
																    ),
																    (
																        p_user_id,
																        'CAPACITY',
																        'Capacity',
																        v_capacity,
																        fn_personal_score_status_label(v_capacity),
																        DATE_TRUNC('month',CURRENT_DATE)::DATE,
																        TRUE
																    ),
																    (
																        p_user_id,
																        'GROWTH',
																        'Growth',
																        v_growth,
																        fn_personal_score_status_label(v_growth),
																        DATE_TRUNC('month',CURRENT_DATE)::DATE,
																        TRUE
																    ),
																    (
																        p_user_id,
																        'FULFILLMENT',
																        'Fulfillment',
																        v_fulfillment,
																        fn_personal_score_status_label(v_fulfillment),
																        DATE_TRUNC('month',CURRENT_DATE)::DATE,
																        TRUE
																    );
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE PROCEDURE sp_refresh_personal_life_connections(
																    p_user_id UUID
																)
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    DELETE FROM personal_life_connections
																    WHERE user_id = p_user_id;
																
																    INSERT INTO personal_life_connections
																    (
																        user_id,
																        source_moment_type_code,
																        target_moment_type_code,
																        connection_title,
																        connection_summary,
																        signal_label,
																        connection_strength_pct,
																        snapshot_month,
																        is_current
																    )
																    VALUES
																
																    (
																        p_user_id,
																        'LIFE_OPERATIONS',
																        'FUTURE_BUILDING',
																        'Stability Fuels Growth',
																        'Consistent life operations improved future execution.',
																        'Positive',
																        82,
																        DATE_TRUNC('month',CURRENT_DATE)::DATE,
																        TRUE
																    ),
																
																    (
																        p_user_id,
																        'LIFESTYLE',
																        'RELATIONSHIPS',
																        'Experiences Strengthen Relationships',
																        'Shared experiences improved connection quality.',
																        'Positive',
																        76,
																        DATE_TRUNC('month',CURRENT_DATE)::DATE,
																        TRUE
																    );
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE PROCEDURE sp_refresh_personal_life_drift_alerts(
																    p_user_id UUID
																)
																LANGUAGE plpgsql
																AS $$
																DECLARE
																    v_drift DECIMAL(5,2);
																BEGIN
																
																    SELECT fn_personal_life_drift_score(
																        MAX(CASE WHEN dimension_code='CAPACITY'
																                 THEN dimension_score END),
																        MAX(CASE WHEN dimension_code='GROWTH'
																                 THEN dimension_score END),
																        MAX(CASE WHEN dimension_code='FULFILLMENT'
																                 THEN dimension_score END),
																        70
																    )
																    INTO v_drift
																    FROM personal_life_dimension_scores
																    WHERE user_id = p_user_id
																      AND is_current = TRUE;
																
																    DELETE FROM personal_life_drift_alerts
																    WHERE user_id = p_user_id;
																
																    IF v_drift >= 20 THEN
																
																        INSERT INTO personal_life_drift_alerts
																        (
																            user_id,
																            drift_title,
																            drift_message,
																            severity_level,
																            is_active
																        )
																        VALUES
																        (
																            p_user_id,
																            'Life Balance Drift Detected',
																            'One life dimension is growing faster than others.',
																            fn_personal_life_drift_status(v_drift),
																            TRUE
																        );
																
																    END IF;
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE PROCEDURE sp_refresh_personal_life_monthly_changes(
																    p_user_id UUID
																)
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    DELETE FROM personal_life_monthly_changes
																    WHERE user_id = p_user_id
																      AND snapshot_month =
																          DATE_TRUNC('month',CURRENT_DATE)::DATE;
																
																    INSERT INTO personal_life_monthly_changes
																    (
																        user_id,
																        change_label,
																        change_value_pct,
																        direction,
																        snapshot_month
																    )
																    VALUES
																    (
																        p_user_id,
																        'Growth Increased',
																        12,
																        'UP',
																        DATE_TRUNC('month',CURRENT_DATE)::DATE
																    ),
																    (
																        p_user_id,
																        'Stress Reduced',
																        -8,
																        'DOWN',
																        DATE_TRUNC('month',CURRENT_DATE)::DATE
																    );
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE PROCEDURE sp_refresh_personal_life_journey(
																    p_user_id UUID
																)
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    DELETE FROM personal_life_journey_events
																    WHERE user_id = p_user_id
																      AND journey_month =
																          DATE_TRUNC('month',CURRENT_DATE)::DATE;
																
																    INSERT INTO personal_life_journey_events
																    (
																        user_id,
																        journey_month,
																        journey_title,
																        journey_description,
																        importance_score
																    )
																    VALUES
																    (
																        p_user_id,
																        DATE_TRUNC('month',CURRENT_DATE)::DATE,
																        'Personal Growth Milestone',
																        'User reached a meaningful improvement across life dimensions.',
																        85
																    );
																
																END;
																$$;
-- >>>STMT<<<
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
																
																BEGIN
																
																    -- =====================================================
																    -- LIFE HEALTH
																    -- =====================================================
																
																    SELECT
																        life_health_score
																    INTO
																        v_life_health
																    FROM personal_life_health_snapshots
																    WHERE user_id = p_user_id
																      AND is_current = TRUE
																    ORDER BY created_at DESC
																    LIMIT 1;
																
																    -- =====================================================
																    -- LIFE DIMENSIONS
																    -- =====================================================
																
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
																
																    -- =====================================================
																    -- MOMENT PILLARS
																    -- =====================================================
																
																    SELECT COALESCE(AVG(primary_score),70)
																    INTO v_stability
																    FROM personal_runtime_snapshots prs
																    JOIN personal_moments pm
																      ON pm.moment_id = prs.moment_id
																    JOIN personal_moment_types mt
																      ON mt.moment_type_id = pm.moment_type_id
																    WHERE pm.user_id = p_user_id
																      AND mt.moment_type_code = 'LIFE_OPERATIONS';
																
																    SELECT COALESCE(AVG(primary_score),70)
																    INTO v_growth
																    FROM personal_runtime_snapshots prs
																    JOIN personal_moments pm
																      ON pm.moment_id = prs.moment_id
																    JOIN personal_moment_types mt
																      ON mt.moment_type_id = pm.moment_type_id
																    WHERE pm.user_id = p_user_id
																      AND mt.moment_type_code = 'FUTURE_BUILDING';
																
																    SELECT COALESCE(AVG(primary_score),70)
																    INTO v_fulfillment
																    FROM personal_runtime_snapshots prs
																    JOIN personal_moments pm
																      ON pm.moment_id = prs.moment_id
																    JOIN personal_moment_types mt
																      ON mt.moment_type_id = pm.moment_type_id
																    WHERE pm.user_id = p_user_id
																      AND mt.moment_type_code = 'LIFESTYLE';
																
																    SELECT COALESCE(AVG(primary_score),70)
																    INTO v_relationship
																    FROM personal_runtime_snapshots prs
																    JOIN personal_moments pm
																      ON pm.moment_id = prs.moment_id
																    JOIN personal_moment_types mt
																      ON mt.moment_type_id = pm.moment_type_id
																    WHERE pm.user_id = p_user_id
																      AND mt.moment_type_code = 'RELATIONSHIPS';
																
																    -- =====================================================
																    -- DOMINANT EMOTION
																    -- =====================================================
																
																    SELECT
																        emotion_name,
																        emotion_pct
																    INTO
																        v_dominant_emotion,
																        v_dominant_emotion_pct
																    FROM personal_memory_emotional_dna
																    WHERE user_id = p_user_id
																      AND is_current = TRUE
																    ORDER BY emotion_pct DESC
																    LIMIT 1;
																
																    -- =====================================================
																    -- DRIFT
																    -- =====================================================
																
																    v_drift_score :=
																        fn_personal_life_drift_score(
																            v_stability,
																            v_growth,
																            v_fulfillment,
																            v_relationship
																        );
																
																    v_drift_status :=
																        fn_personal_life_drift_status(
																            v_drift_score
																        );
																
																    -- =====================================================
																    -- HAPPINESS DRIVER
																    -- =====================================================
																
																    SELECT
																        driver_name,
																        COALESCE(impact_pct,0)
																    INTO
																        v_happiness_driver,
																        v_happiness_driver_score
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
																
																    -- =====================================================
																    -- LIFE STAGE
																    -- =====================================================
																
																    SELECT current_stage
																    INTO v_life_stage
																    FROM personal_memory_evolution_snapshots
																    WHERE user_id = p_user_id
																      AND is_current = TRUE
																    ORDER BY created_at DESC
																    LIMIT 1;
																
																    -- =====================================================
																    -- LEVERAGE AREA
																    -- Lowest pillar becomes leverage target
																    -- =====================================================
																
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
																
																    -- =====================================================
																    -- LIFE SUMMARY
																    -- =====================================================
																
																    v_life_summary :=
																        CONCAT(
																            'Life Health: ',
																            ROUND(v_life_health,0),
																            '. Dominant Emotion: ',
																            COALESCE(v_dominant_emotion,'Balanced'),
																            '. Strongest Driver: ',
																            COALESCE(v_happiness_driver,'Growth'),
																            '. Highest Leverage Area: ',
																            COALESCE(v_leverage_area,'Life Operations'),
																            '.'
																        );
																
																    -- =====================================================
																    -- CLOSE PREVIOUS SNAPSHOT
																    -- =====================================================
																
																    UPDATE personal_life_aggregate_snapshots
																    SET
																        is_current = FALSE,
																        updated_at = CURRENT_TIMESTAMP
																    WHERE user_id = p_user_id
																      AND is_current = TRUE;
																
																    -- =====================================================
																    -- INSERT NEW SNAPSHOT
																    -- =====================================================
																
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
																        DATE_TRUNC('month',CURRENT_DATE)::DATE,
																
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
-- >>>STMT<<<
CREATE OR REPLACE PROCEDURE sp_refresh_personal_orchestration(
																    p_moment_id UUID
																)
																LANGUAGE plpgsql
																AS $$
																DECLARE
																    v_user_id UUID;
																BEGIN
																
																    -- =====================================================
																    -- USER LOOKUP
																    -- =====================================================
																
																    SELECT user_id
																    INTO v_user_id
																    FROM personal_moments
																    WHERE moment_id = p_moment_id;
																
																    IF v_user_id IS NULL THEN
																        RAISE EXCEPTION
																        'Moment not found: %',
																        p_moment_id;
																    END IF;
																
																    -- =====================================================
																    -- PHASE 1
																    -- RUNTIME / PULSE FOUNDATION
																    -- =====================================================
																
																    CALL sp_refresh_personal_runtime(p_moment_id);
																
																    CALL sp_refresh_personal_pulse_snapshot(p_moment_id);
																
																    CALL sp_refresh_personal_signals(p_moment_id);
																
																    CALL sp_refresh_personal_recommendations(p_moment_id);
																
																    -- =====================================================
																    -- PHASE 2
																    -- MOMENTS
																    -- =====================================================
																
																    CALL sp_refresh_personal_moment_highlights(
																        v_user_id
																    );
																
																    CALL sp_refresh_personal_moment_turning_points(
																        v_user_id
																    );
																
																    -- =====================================================
																    -- PHASE 3
																    -- MEMORY
																    -- =====================================================
																
																    CALL sp_refresh_personal_memory(p_moment_id);
																
																    CALL sp_refresh_personal_advanced_memory(p_moment_id);
																
																    CALL sp_refresh_personal_memory_identity(
																        p_moment_id
																    );
																
																    CALL sp_refresh_personal_memory_drivers(
																        p_moment_id
																    );
																
																    CALL sp_refresh_personal_emotional_dna(
																        p_moment_id
																    );
																
																    CALL sp_refresh_personal_evolution(
																        p_moment_id
																    );
																
																    -- =====================================================
																    -- PHASE 4
																    -- LIFE
																    -- =====================================================
																
																    CALL sp_refresh_personal_life_health(
																        v_user_id
																    );
																
																    CALL sp_refresh_personal_life_dimensions(
																        v_user_id
																    );
																
																    CALL sp_refresh_personal_life_connections(
																        v_user_id
																    );
																
																    CALL sp_refresh_personal_life_drift_alerts(
																        v_user_id
																    );
																
																    CALL sp_refresh_personal_life_monthly_changes(
																        v_user_id
																    );
																
																    CALL sp_refresh_personal_life_journey(
																        v_user_id
																    );
																
																    CALL sp_refresh_personal_life_snapshot(
																        v_user_id
																    );
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE PROCEDURE sp_refresh_personal_user(
																    p_user_id UUID
																)
																LANGUAGE plpgsql
																AS $$
																DECLARE
																    r RECORD;
																BEGIN
																
																    FOR r IN
																        SELECT moment_id
																        FROM personal_moments
																        WHERE user_id = p_user_id
																          AND status = 'ACTIVE'
																    LOOP
																
																        CALL sp_refresh_personal_orchestration(
																            r.moment_id
																        );
																
																    END LOOP;
																
																END;
																$$;
-- >>>STMT<<<
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

    /* latest Personal snapshot */
    SELECT life_aggregate_snapshot_id, life_health_score
    INTO v_personal_snapshot_id, v_personal_score
    FROM personal_life_aggregate_snapshots
    WHERE user_id = p_user_id
    ORDER BY snapshot_date DESC, created_at DESC
    LIMIT 1;

    /* latest Group snapshot */
    SELECT master_snapshot_id, group_life_score
    INTO v_group_snapshot_id, v_group_score
    FROM group_life_master_snapshots
    WHERE user_id = p_user_id
    ORDER BY snapshot_date DESC, created_at DESC
    LIMIT 1;

    /* latest Business snapshot (via workspace membership) */
    SELECT bls.snapshot_id, bls.life_score
    INTO v_business_snapshot_id, v_business_score
    FROM business_life_snapshots bls
    JOIN business_workspace_members bwm
      ON bwm.workspace_id = bls.workspace_id
    WHERE bwm.user_id = p_user_id
      AND bwm.status = 'ACTIVE'
    ORDER BY bls.generated_at DESC
    LIMIT 1;


    /* weighted active-domain scoring */
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


    /* Phase 1 dimension logic */
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

        CASE WHEN v_money >= 80 THEN 'Stable' WHEN v_money >= 65 THEN 'Watch' ELSE 'Needs Attention' END,
        CASE WHEN v_relationship >= 80 THEN 'Strong' WHEN v_relationship >= 65 THEN 'Stable' ELSE 'Needs Attention' END,
        CASE WHEN v_execution >= 80 THEN 'Strong' WHEN v_execution >= 65 THEN 'Stable' ELSE 'Needs Attention' END,
        CASE WHEN v_growth >= 80 THEN 'Rising' WHEN v_growth >= 65 THEN 'Stable' ELSE 'Needs Attention' END,

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
-- >>>STMT<<<
CREATE OR REPLACE PROCEDURE sp_refresh_circle_participants(p_user_id UUID)
LANGUAGE plpgsql
AS $$
BEGIN

    /* GROUP PARTICIPANTS */
    INSERT INTO circle_participants (
        user_id,
        participant_user_id,
        participant_name,
        participant_phone,
        participant_email,
        first_seen_date,
        last_seen_date,
        is_active,
        updated_at
    )
    SELECT
        gm.created_by_user_id AS user_id,
        gp.participant_user_id,
        COALESCE(gp.participant_name, 'Unknown Participant'),
        gp.participant_phone,
        gp.participant_email,
        MIN(gp.created_at)::DATE,
        MAX(COALESCE(gp.updated_at, gp.created_at))::DATE,
        BOOL_OR(gm.status IN ('ACTIVE','IN_PROGRESS','LIVE')),
        CURRENT_TIMESTAMP
    FROM group_moment_participants gp
    JOIN group_moments gm
        ON gm.group_moment_id = gp.group_moment_id
    WHERE gm.created_by_user_id = p_user_id
    GROUP BY
        gm.created_by_user_id,
        gp.participant_user_id,
        gp.participant_name,
        gp.participant_phone,
        gp.participant_email
    ON CONFLICT (
        user_id,
        participant_name,
        COALESCE(participant_phone, ''),
        COALESCE(participant_email, '')
    )
    DO UPDATE SET
        last_seen_date = GREATEST(circle_participants.last_seen_date, EXCLUDED.last_seen_date),
        is_active = circle_participants.is_active OR EXCLUDED.is_active,
        updated_at = CURRENT_TIMESTAMP;


/* BUSINESS PARTICIPANTS / MEMBERS */

INSERT INTO circle_participants (

    user_id,

    participant_user_id,

    participant_name,

    participant_phone,

    participant_email,

    first_seen_date,

    last_seen_date,

    is_active,

    updated_at

)

SELECT

    bm.created_by AS user_id,

    bmm.user_id AS participant_user_id,

    COALESCE(bmm.name, 'Unknown Participant') AS participant_name,

    bmm.mobile AS participant_phone,

    bmm.email AS participant_email,

    MIN(bmm.created_at)::DATE,

    MAX(COALESCE(bmm.updated_at, bmm.created_at))::DATE,

    BOOL_OR(

        bm.status IN ('ACTIVE','IN_PROGRESS','LIVE','active','in_progress','live')

        OR bmm.member_status IN ('ACTIVE','INVITED','active','invited')

    ),

    CURRENT_TIMESTAMP

FROM business_moment_members bmm

JOIN business_moments bm

    ON bm.moment_id = bmm.moment_id

WHERE bm.created_by = p_user_id

GROUP BY

    bm.created_by,

    bmm.user_id,

    bmm.name,

    bmm.mobile,

    bmm.email

ON CONFLICT (

    user_id,

    participant_name,

    COALESCE(participant_phone, ''),

    COALESCE(participant_email, '')

)

DO UPDATE SET

    last_seen_date = GREATEST(circle_participants.last_seen_date, EXCLUDED.last_seen_date),

    is_active = circle_participants.is_active OR EXCLUDED.is_active,

    updated_at = CURRENT_TIMESTAMP;


    /* GROUP SOURCES */
    INSERT INTO circle_participant_sources (
        circle_participant_id,
        user_id,
        source_type,
        source_moment_id,
        source_moment_name,
        source_moment_type,
        participation_date,
        is_active_source
    )
    SELECT
        cp.circle_participant_id,
        gm.created_by_user_id,
        'GROUP',
        gm.group_moment_id,
        gm.moment_name,
        gm.moment_type,
        gp.created_at::DATE,
        gm.status IN ('ACTIVE','IN_PROGRESS','LIVE')
    FROM group_moment_participants gp
    JOIN group_moments gm
        ON gm.group_moment_id = gp.group_moment_id
    JOIN circle_participants cp
        ON cp.user_id = gm.created_by_user_id
       AND cp.participant_name = COALESCE(gp.participant_name, 'Unknown Participant')
       AND COALESCE(cp.participant_phone, '') = COALESCE(gp.participant_phone, '')
       AND COALESCE(cp.participant_email, '') = COALESCE(gp.participant_email, '')
    WHERE gm.created_by_user_id = p_user_id
    ON CONFLICT (circle_participant_id, source_type, source_moment_id)
    DO NOTHING;


/* BUSINESS SOURCES */

INSERT INTO circle_participant_sources (

    circle_participant_id,

    user_id,

    source_type,

    source_moment_id,

    source_moment_name,

    source_moment_type,

    participation_date,

    is_active_source

)

SELECT

    cp.circle_participant_id,

    bm.created_by,

    'BUSINESS',

    bm.moment_id,

    bm.moment_name,

    bm.moment_type,

    bmm.created_at::DATE,

    (

        bm.status IN ('ACTIVE','IN_PROGRESS','LIVE','active','in_progress','live')

        OR bmm.member_status IN ('ACTIVE','INVITED','active','invited')

    )

FROM business_moment_members bmm

JOIN business_moments bm

    ON bm.moment_id = bmm.moment_id

JOIN circle_participants cp

    ON cp.user_id = bm.created_by

   AND cp.participant_name = COALESCE(bmm.name, 'Unknown Participant')

   AND COALESCE(cp.participant_phone, '') = COALESCE(bmm.mobile, '')

   AND COALESCE(cp.participant_email, '') = COALESCE(bmm.email, '')

WHERE bm.created_by = p_user_id

ON CONFLICT (circle_participant_id, source_type, source_moment_id)

DO NOTHING;

END;
$$;
-- >>>STMT<<<
CREATE OR REPLACE PROCEDURE sp_refresh_circle_participant_stats(p_user_id UUID)
LANGUAGE plpgsql
AS $$
BEGIN

    INSERT INTO circle_participant_stats (
        circle_participant_id,
        user_id,
        shared_moment_count,
        active_moment_count,
        recent_activity_count,
        participation_score,
        rank_order,
        last_activity_date,
        updated_at
    )
    SELECT
        cp.circle_participant_id,
        cp.user_id,
        COUNT(DISTINCT cps.source_moment_id) AS shared_moment_count,
        COUNT(DISTINCT cps.source_moment_id) FILTER (WHERE cps.is_active_source = TRUE) AS active_moment_count,
        COUNT(*) FILTER (WHERE cps.participation_date >= CURRENT_DATE - INTERVAL '30 days') AS recent_activity_count,
        LEAST(
            100,
            (
                COUNT(DISTINCT cps.source_moment_id) * 8
                + COUNT(DISTINCT cps.source_moment_id) FILTER (WHERE cps.is_active_source = TRUE) * 12
                + COUNT(*) FILTER (WHERE cps.participation_date >= CURRENT_DATE - INTERVAL '30 days') * 5
            )
        )::NUMERIC(5,2) AS participation_score,
        ROW_NUMBER() OVER (
            PARTITION BY cp.user_id
            ORDER BY
                COUNT(DISTINCT cps.source_moment_id) DESC,
                MAX(cps.participation_date) DESC
        ) AS rank_order,
        MAX(cps.participation_date) AS last_activity_date,
        CURRENT_TIMESTAMP
    FROM circle_participants cp
    LEFT JOIN circle_participant_sources cps
        ON cps.circle_participant_id = cp.circle_participant_id
    WHERE cp.user_id = p_user_id
    GROUP BY cp.circle_participant_id, cp.user_id
    ON CONFLICT (circle_participant_id)
    DO UPDATE SET
        shared_moment_count = EXCLUDED.shared_moment_count,
        active_moment_count = EXCLUDED.active_moment_count,
        recent_activity_count = EXCLUDED.recent_activity_count,
        participation_score = EXCLUDED.participation_score,
        rank_order = EXCLUDED.rank_order,
        last_activity_date = EXCLUDED.last_activity_date,
        updated_at = CURRENT_TIMESTAMP;

END;
$$;
-- >>>STMT<<<
CREATE OR REPLACE PROCEDURE sp_refresh_circle_suggestions(p_user_id UUID)
LANGUAGE plpgsql
AS $$
BEGIN

    DELETE FROM circle_suggestions
    WHERE user_id = p_user_id;

    /* Shared experience suggestion */
    INSERT INTO circle_suggestions (
        user_id,
        suggestion_type,
        participant_ids_json,
        suggestion_title,
        suggestion_description,
        confidence_score,
        cta_label,
        target_create_flow
    )
    SELECT
        p_user_id,
        'SHARED_EXPERIENCE',
        JSONB_AGG(circle_participant_id ORDER BY participation_score DESC),
        'Create a Shared Experience',
        'You frequently plan shared moments with these participants.',
        AVG(participation_score),
        'Create Shared Experience',
        'GROUP_SHARED_EXPERIENCE'
    FROM (
        SELECT cp.circle_participant_id, cps.participation_score
        FROM circle_participant_stats cps
        JOIN circle_participants cp
            ON cp.circle_participant_id = cps.circle_participant_id
        JOIN circle_participant_sources src
            ON src.circle_participant_id = cp.circle_participant_id
        WHERE cp.user_id = p_user_id
          AND src.source_type = 'GROUP'
        GROUP BY cp.circle_participant_id, cps.participation_score
        ORDER BY cps.participation_score DESC
        LIMIT 5
    ) x
    HAVING COUNT(*) >= 2;


    /* Business workspace suggestion */
    INSERT INTO circle_suggestions (
        user_id,
        suggestion_type,
        participant_ids_json,
        suggestion_title,
        suggestion_description,
        confidence_score,
        cta_label,
        target_create_flow
    )
    SELECT
        p_user_id,
        'BUSINESS_WORKSPACE',
        JSONB_AGG(circle_participant_id ORDER BY participation_score DESC),
        'Create a Business Workspace',
        'These participants appear often in business moments.',
        AVG(participation_score),
        'Create Business Workspace',
        'BUSINESS_WORKSPACE'
    FROM (
        SELECT cp.circle_participant_id, cps.participation_score
        FROM circle_participant_stats cps
        JOIN circle_participants cp
            ON cp.circle_participant_id = cps.circle_participant_id
        JOIN circle_participant_sources src
            ON src.circle_participant_id = cp.circle_participant_id
        WHERE cp.user_id = p_user_id
          AND src.source_type = 'BUSINESS'
        GROUP BY cp.circle_participant_id, cps.participation_score
        ORDER BY cps.participation_score DESC
        LIMIT 5
    ) x
    HAVING COUNT(*) >= 2;

END;
$$;
-- >>>STMT<<<
CREATE OR REPLACE PROCEDURE sp_refresh_circle(p_user_id UUID)
LANGUAGE plpgsql
AS $$
BEGIN
    CALL sp_refresh_circle_participants(p_user_id);
    CALL sp_refresh_circle_participant_stats(p_user_id);
    CALL sp_refresh_circle_suggestions(p_user_id);
END;
$$;
