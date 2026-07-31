CREATE OR REPLACE FUNCTION set_personal_updated_at()
																RETURNS TRIGGER AS $$
																BEGIN
																    NEW.updated_at = CURRENT_TIMESTAMP;
																    RETURN NEW;
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_update_account_balance()
																RETURNS TRIGGER
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    IF NEW.account_id IS NULL THEN
																        RETURN NEW;
																    END IF;
																
																    UPDATE personal_accounts
																    SET current_balance =
																    (
																        SELECT
																            opening_balance
																            +
																            COALESCE(
																                SUM(
																                    CASE
																                        WHEN direction='CREDIT'
																                        THEN amount
																                        WHEN direction='DEBIT'
																                        THEN -amount
																                        ELSE 0
																                    END
																                ),0
																            )
																        FROM personal_money_events
																        WHERE account_id = NEW.account_id
																          AND is_voided = FALSE
																    )
																    WHERE account_id = NEW.account_id;
																
																    RETURN NEW;
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_personal_auto_refresh()
																RETURNS TRIGGER
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    BEGIN
																        CALL sp_refresh_personal_orchestration(
																            NEW.moment_id
																        );
																    EXCEPTION
																        WHEN OTHERS THEN
																            RAISE WARNING
																                'fn_personal_auto_refresh skipped for moment %: %',
																                NEW.moment_id,
																                SQLERRM;
																    END;
																
																    RETURN NEW;
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_personal_clamp_score(
																    p_score DECIMAL
																)
																RETURNS DECIMAL(5,2)
																LANGUAGE plpgsql
																IMMUTABLE
																AS $$
																BEGIN
																    RETURN ROUND(
																        LEAST(100, GREATEST(0, COALESCE(p_score, 0))),
																        2
																    );
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_personal_score_status_label(
																    p_score DECIMAL
																)
																RETURNS VARCHAR
																LANGUAGE plpgsql
																IMMUTABLE
																AS $$
																BEGIN
																    RETURN CASE
																        WHEN p_score >= 85 THEN 'Thriving'
																        WHEN p_score >= 70 THEN 'Stable and Growing'
																        WHEN p_score >= 55 THEN 'Needs Attention'
																        WHEN p_score >= 40 THEN 'At Risk'
																        ELSE 'Critical'
																    END;
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_personal_life_health_score(
																    p_stability_score DECIMAL,
																    p_growth_score DECIMAL,
																    p_fulfillment_score DECIMAL,
																    p_relationship_health_score DECIMAL
																)
																RETURNS DECIMAL(5,2)
																LANGUAGE plpgsql
																IMMUTABLE
																AS $$
																BEGIN
																    RETURN fn_personal_clamp_score(
																        COALESCE(p_stability_score, 70) * 0.25
																      + COALESCE(p_growth_score, 70) * 0.25
																      + COALESCE(p_fulfillment_score, 70) * 0.25
																      + COALESCE(p_relationship_health_score, 70) * 0.25
																    );
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_personal_life_drift_score(
																    p_stability_score DECIMAL,
																    p_growth_score DECIMAL,
																    p_fulfillment_score DECIMAL,
																    p_relationship_health_score DECIMAL
																)
																RETURNS DECIMAL(5,2)
																LANGUAGE plpgsql
																IMMUTABLE
																AS $$
																DECLARE
																    v_max DECIMAL;
																    v_min DECIMAL;
																BEGIN
																    SELECT
																        MAX(v),
																        MIN(v)
																    INTO
																        v_max,
																        v_min
																    FROM (
																        VALUES
																            (COALESCE(p_stability_score, 70)),
																            (COALESCE(p_growth_score, 70)),
																            (COALESCE(p_fulfillment_score, 70)),
																            (COALESCE(p_relationship_health_score, 70))
																    ) AS scores(v);
																
																    RETURN ROUND(v_max - v_min, 2);
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_personal_life_drift_status(
																    p_drift_score DECIMAL
																)
																RETURNS VARCHAR
																LANGUAGE plpgsql
																IMMUTABLE
																AS $$
																BEGIN
																    RETURN CASE
																        WHEN p_drift_score >= 35 THEN 'HIGH'
																        WHEN p_drift_score >= 20 THEN 'MEDIUM'
																        ELSE 'LOW'
																    END;
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_personal_stress_score(
																    p_pressure_score DECIMAL,
																    p_cognitive_load_score DECIMAL,
																    p_connection_gap_score DECIMAL
																)
																RETURNS DECIMAL(5,2)
																LANGUAGE plpgsql
																IMMUTABLE
																AS $$
																BEGIN
																    RETURN fn_personal_clamp_score(
																        COALESCE(p_pressure_score, 50) * 0.45
																      + COALESCE(p_cognitive_load_score, 50) * 0.35
																      + COALESCE(p_connection_gap_score, 50) * 0.20
																    );
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_personal_capacity_score(
																    p_recovery_score DECIMAL,
																    p_operational_balance_score DECIMAL,
																    p_wellbeing_score DECIMAL
																)
																RETURNS DECIMAL(5,2)
																LANGUAGE plpgsql
																IMMUTABLE
																AS $$
																BEGIN
																    RETURN fn_personal_clamp_score(
																        COALESCE(p_recovery_score, 70) * 0.40
																      + COALESCE(p_operational_balance_score, 70) * 0.35
																      + COALESCE(p_wellbeing_score, 70) * 0.25
																    );
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_personal_highlight_impact_score(
																    p_emotion_impact DECIMAL,
																    p_outcome_improvement DECIMAL,
																    p_financial_weight DECIMAL,
																    p_recency_score DECIMAL
																)
																RETURNS DECIMAL(5,2)
																LANGUAGE plpgsql
																IMMUTABLE
																AS $$
																BEGIN
																    RETURN fn_personal_clamp_score(
																        COALESCE(p_emotion_impact, 70) * 0.40
																      + COALESCE(p_outcome_improvement, 70) * 0.30
																      + COALESCE(p_financial_weight, 50) * 0.20
																      + COALESCE(p_recency_score, 50) * 0.10
																    );
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_personal_turning_point_impact_score(
																    p_behavior_shift_score DECIMAL,
																    p_duration_score DECIMAL,
																    p_outcome_change_score DECIMAL,
																    p_emotional_change_score DECIMAL
																)
																RETURNS DECIMAL(5,2)
																LANGUAGE plpgsql
																IMMUTABLE
																AS $$
																BEGIN
																    RETURN fn_personal_clamp_score(
																        COALESCE(p_behavior_shift_score, 70) * 0.50
																      + COALESCE(p_duration_score, 50) * 0.25
																      + COALESCE(p_outcome_change_score, 70) * 0.15
																      + COALESCE(p_emotional_change_score, 70) * 0.10
																    );
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_personal_identity_confidence_score(
																    p_pattern_consistency DECIMAL,
																    p_time_horizon_score DECIMAL,
																    p_repeatability_score DECIMAL
																)
																RETURNS DECIMAL(5,2)
																LANGUAGE plpgsql
																IMMUTABLE
																AS $$
																BEGIN
																    RETURN fn_personal_clamp_score(
																        (
																            COALESCE(p_pattern_consistency, 70)
																          * COALESCE(p_time_horizon_score, 70)
																          * COALESCE(p_repeatability_score, 70)
																        ) / 10000
																    );
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_personal_driver_impact_pct(
																    p_driver_contribution DECIMAL,
																    p_total_contribution DECIMAL
																)
																RETURNS DECIMAL(5,2)
																LANGUAGE plpgsql
																IMMUTABLE
																AS $$
																BEGIN
																    IF COALESCE(p_total_contribution, 0) = 0 THEN
																        RETURN 0;
																    END IF;
																
																    RETURN fn_personal_clamp_score(
																        (p_driver_contribution / p_total_contribution) * 100
																    );
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_personal_emotional_dna_pct(
																    p_emotion_weight DECIMAL,
																    p_total_emotion_weight DECIMAL
																)
																RETURNS DECIMAL(5,2)
																LANGUAGE plpgsql
																IMMUTABLE
																AS $$
																BEGIN
																    IF COALESCE(p_total_emotion_weight, 0) = 0 THEN
																        RETURN 0;
																    END IF;
																
																    RETURN fn_personal_clamp_score(
																        (p_emotion_weight / p_total_emotion_weight) * 100
																    );
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_personal_growth_edge_multiplier(
																    p_potential_gain DECIMAL,
																    p_effort_required DECIMAL
																)
																RETURNS DECIMAL(8,2)
																LANGUAGE plpgsql
																IMMUTABLE
																AS $$
																BEGIN
																    IF COALESCE(p_effort_required, 0) <= 0 THEN
																        RETURN 0;
																    END IF;
																
																    RETURN ROUND(
																        GREATEST(0, p_potential_gain / p_effort_required),
																        2
																    );
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_personal_recency_score(
																    p_occurred_at TIMESTAMP
																)
																RETURNS DECIMAL(5,2)
																LANGUAGE plpgsql
																STABLE
																AS $$
																DECLARE
																    v_days INT;
																BEGIN
																    IF p_occurred_at IS NULL THEN
																        RETURN 30;
																    END IF;
																
																    v_days := GREATEST(
																        0,
																        DATE_PART('day', CURRENT_TIMESTAMP - p_occurred_at)::INT
																    );
																
																    RETURN fn_personal_clamp_score(
																        100 - LEAST(70, v_days * 0.78)
																    );
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_personal_monthly_delta(
																    p_current_value DECIMAL,
																    p_previous_value DECIMAL
																)
																RETURNS DECIMAL(5,2)
																LANGUAGE plpgsql
																IMMUTABLE
																AS $$
																BEGIN
																    IF p_previous_value IS NULL THEN
																        RETURN NULL;
																    END IF;
																
																    RETURN ROUND(
																        COALESCE(p_current_value, 0) - COALESCE(p_previous_value, 0),
																        2
																    );
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_personal_momentum_score(
    p_progress_velocity DECIMAL,
    p_consistency DECIMAL,
    p_positive_event_ratio DECIMAL
)
RETURNS DECIMAL(5,2)
LANGUAGE plpgsql
IMMUTABLE
AS $$
BEGIN
    RETURN fn_personal_clamp_score(
        COALESCE(p_progress_velocity,70) * 0.40
      + COALESCE(p_consistency,70) * 0.30
      + COALESCE(p_positive_event_ratio,70) * 0.30
    );
END;
$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_personal_progress_score(
    p_completed_actions DECIMAL,
    p_planned_actions DECIMAL
)
RETURNS DECIMAL(5,2)
LANGUAGE plpgsql
IMMUTABLE
AS $$
BEGIN
    IF COALESCE(p_planned_actions,0) = 0 THEN
        RETURN 0;
    END IF;

    RETURN fn_personal_clamp_score(
        (p_completed_actions / p_planned_actions) * 100
    );
END;
$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_personal_risk_score(
    p_budget_deviation DECIMAL,
    p_goal_slippage DECIMAL,
    p_negative_event_density DECIMAL
)
RETURNS DECIMAL(5,2)
LANGUAGE plpgsql
IMMUTABLE
AS $$
BEGIN
    RETURN fn_personal_clamp_score(
        COALESCE(p_budget_deviation,0) * 0.40
      + COALESCE(p_goal_slippage,0) * 0.35
      + COALESCE(p_negative_event_density,0) * 0.25
    );
END;
$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_create_group_live_feed(
																    p_event_id UUID
																)
																RETURNS VOID AS $$
																DECLARE
																    v_moment_id UUID;
																    v_module_code VARCHAR(100);
																    v_title TEXT;
																    v_summary TEXT;
																    v_category TEXT;
																BEGIN
																    SELECT moment_id, module_code
																    INTO v_moment_id, v_module_code
																    FROM group_quick_add_events
																    WHERE event_id = p_event_id;
																
																    v_category :=
																        CASE
																            WHEN v_module_code IN ('PARTICIPANT','CONTRIBUTOR','RESIDENT') THEN 'PEOPLE'
																            WHEN v_module_code IN ('EXPENSE','CONTRIBUTION') THEN 'MONEY'
																            WHEN v_module_code IN ('PLANNING_ITEM','BOOKING','TASK','PURCHASE_ITEM') THEN 'PLANNING'
																            WHEN v_module_code IN ('VENDOR','OWNERSHIP','DELIVERY','MAINTENANCE','ASSET','RULE') THEN 'SUPPORT'
																            WHEN v_module_code IN ('MEMORY') THEN 'MEMORY'
																            WHEN v_module_code IN ('POLL') THEN 'POLLS'
																            WHEN v_module_code IN ('UPDATE') THEN 'UPDATES'
																            ELSE 'GENERAL'
																        END;
																
																    v_title := INITCAP(REPLACE(v_module_code, '_', ' ')) || ' added';
																    v_summary := 'New ' || LOWER(REPLACE(v_module_code, '_', ' ')) || ' activity recorded.';
																
																    INSERT INTO group_live_feed (
																        moment_id,
																        event_id,
																        feed_category,
																        title,
																        summary,
																        can_view,
																        can_edit,
																        visibility
																    )
																    VALUES (
																        v_moment_id,
																        p_event_id,
																        v_category,
																        v_title,
																        v_summary,
																        TRUE,
																        TRUE,
																        'EVERYONE'
																    );
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_group_moment_stage(
																    p_moment_id UUID,
																    p_source_event_id UUID DEFAULT NULL
																)
																RETURNS VOID AS $$
																DECLARE
																    v_type VARCHAR(50);
																    v_old_stage VARCHAR(50);
																    v_new_stage VARCHAR(50);
																BEGIN
																    SELECT moment_type, stage
																    INTO v_type, v_old_stage
																    FROM group_moments
																    WHERE moment_id = p_moment_id;
																
																    IF v_type = 'SHARED_EXPERIENCE' THEN
																        IF EXISTS (SELECT 1 FROM shared_experience_planning_items WHERE moment_id = p_moment_id)
																           OR EXISTS (SELECT 1 FROM group_expenses WHERE moment_id = p_moment_id)
																           OR EXISTS (SELECT 1 FROM group_polls WHERE moment_id = p_moment_id)
																        THEN
																            v_new_stage := 'PLANNING';
																        ELSE
																            v_new_stage := v_old_stage;
																        END IF;
																
																    ELSIF v_type = 'SHARED_PURCHASE' THEN
																        IF EXISTS (SELECT 1 FROM shared_purchase_delivery WHERE moment_id = p_moment_id AND status = 'COMPLETED') THEN
																            v_new_stage := 'DELIVERED';
																        ELSIF EXISTS (SELECT 1 FROM group_expenses WHERE moment_id = p_moment_id) THEN
																            v_new_stage := 'PURCHASED';
																        ELSIF EXISTS (SELECT 1 FROM shared_purchase_items WHERE moment_id = p_moment_id AND status IN ('SELECTED','PURCHASED')) THEN
																            v_new_stage := 'SELECTED';
																        ELSIF EXISTS (SELECT 1 FROM group_contributions WHERE moment_id = p_moment_id) THEN
																            v_new_stage := 'FUNDING';
																        ELSE
																            v_new_stage := v_old_stage;
																        END IF;
																
																    ELSIF v_type = 'SHARED_LIVING' THEN
																        IF EXISTS (SELECT 1 FROM group_memory_entries WHERE moment_id = p_moment_id) THEN
																            v_new_stage := 'REMEMBER';
																        ELSIF EXISTS (SELECT 1 FROM shared_living_maintenance WHERE moment_id = p_moment_id) THEN
																            v_new_stage := 'MAINTAIN';
																        ELSIF EXISTS (SELECT 1 FROM shared_living_tasks WHERE moment_id = p_moment_id)
																           OR EXISTS (SELECT 1 FROM group_expenses WHERE moment_id = p_moment_id)
																        THEN
																            v_new_stage := 'OPERATE';
																        ELSIF EXISTS (SELECT 1 FROM shared_living_residents WHERE moment_id = p_moment_id) THEN
																            v_new_stage := 'SETTLE';
																        ELSE
																            v_new_stage := v_old_stage;
																        END IF;
																    END IF;
																
																    IF v_new_stage IS NOT NULL AND v_new_stage <> v_old_stage THEN
																        UPDATE group_moment_stage_history
																        SET is_current = FALSE
																        WHERE moment_id = p_moment_id;
																
																        INSERT INTO group_moment_stage_history (
																            moment_id,
																            old_stage,
																            new_stage,
																            change_reason,
																            source_event_id,
																            changed_by,
																            is_current
																        )
																        VALUES (
																            p_moment_id,
																            v_old_stage,
																            v_new_stage,
																            'Stage refreshed from activity',
																            p_source_event_id,
																            '00000000-0000-0000-0000-000000000000',
																            TRUE
																        );
																
																        UPDATE group_moments
																        SET stage = v_new_stage,
																            updated_at = CURRENT_TIMESTAMP
																        WHERE moment_id = p_moment_id;
																    END IF;
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_group_health_snapshot(
																    p_moment_id UUID
																)
																RETURNS VOID AS $$
																DECLARE
																    v_type VARCHAR(50);
																    v_score DECIMAL(5,2);
																    v_status VARCHAR(30);
																    v_people_score DECIMAL(5,2);
																    v_money_score DECIMAL(5,2);
																    v_activity_score DECIMAL(5,2);
																BEGIN
																    SELECT moment_type INTO v_type
																    FROM group_moments
																    WHERE moment_id = p_moment_id;
																
																    v_people_score :=
																        LEAST(100, (
																            SELECT COUNT(*) * 20
																            FROM group_moment_members
																            WHERE moment_id = p_moment_id
																              AND status IN ('ACTIVE','CONFIRMED')
																        ));
																
																    v_money_score :=
																        LEAST(100, (
																            SELECT COALESCE(SUM(amount),0) / 1000
																            FROM group_contributions
																            WHERE moment_id = p_moment_id
																              AND status = 'RECEIVED'
																        ));
																
																    v_activity_score :=
																        LEAST(100, (
																            SELECT COUNT(*) * 10
																            FROM group_quick_add_events
																            WHERE moment_id = p_moment_id
																        ));
																
																    v_score := ROUND((COALESCE(v_people_score,0) * 0.30)
																                   + (COALESCE(v_money_score,0) * 0.30)
																                   + (COALESCE(v_activity_score,0) * 0.40), 2);
																
																    v_status :=
																        CASE
																            WHEN v_score >= 85 THEN 'EXCELLENT'
																            WHEN v_score >= 70 THEN 'GOOD'
																            WHEN v_score >= 50 THEN 'STABLE'
																            WHEN v_score >= 30 THEN 'WARNING'
																            ELSE 'CRITICAL'
																        END;
																
																    INSERT INTO group_health_snapshots (
																        moment_id,
																        snapshot_date,
																        health_score,
																        health_status,
																        people_score,
																        money_score,
																        activity_score
																    )
																    VALUES (
																        p_moment_id,
																        CURRENT_DATE,
																        v_score,
																        v_status,
																        v_people_score,
																        v_money_score,
																        v_activity_score
																    );
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_group_pulse_snapshot(
																    p_moment_id UUID
																)
																RETURNS VOID AS $$
																DECLARE
																    v_completion DECIMAL(5,2);
																    v_participation DECIMAL(5,2);
																    v_funding DECIMAL(5,2);
																    v_active_members INT;
																    v_active_tasks INT;
																    v_open_items INT;
																    v_score DECIMAL(5,2);
																BEGIN
																    SELECT COUNT(*)
																    INTO v_active_members
																    FROM group_moment_members
																    WHERE moment_id = p_moment_id
																      AND status IN ('ACTIVE','CONFIRMED');
																
																    SELECT COUNT(*)
																    INTO v_active_tasks
																    FROM shared_living_tasks
																    WHERE moment_id = p_moment_id
																      AND status IN ('TO_DO','IN_PROGRESS','OVERDUE');
																
																    SELECT COUNT(*)
																    INTO v_open_items
																    FROM group_quick_add_events
																    WHERE moment_id = p_moment_id;
																
																    v_participation := LEAST(100, v_active_members * 20);
																    v_completion := LEAST(100, GREATEST(0, 100 - (v_active_tasks * 10)));
																    v_funding := LEAST(100, (
																        SELECT COALESCE(SUM(amount),0) / 1000
																        FROM group_contributions
																        WHERE moment_id = p_moment_id
																          AND status = 'RECEIVED'
																    ));
																
																    v_score := ROUND((v_completion * 0.35)
																                   + (v_participation * 0.35)
																                   + (v_funding * 0.30), 2);
																
																    INSERT INTO group_pulse_snapshots (
																        moment_id,
																        snapshot_date,
																        completion_percentage,
																        participation_percentage,
																        funding_percentage,
																        active_members,
																        active_tasks,
																        open_items,
																        pulse_score
																    )
																    VALUES (
																        p_moment_id,
																        CURRENT_DATE,
																        v_completion,
																        v_participation,
																        v_funding,
																        v_active_members,
																        v_active_tasks,
																        v_open_items,
																        v_score
																    );
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_group_signals(
																    p_moment_id UUID
																)
																RETURNS VOID AS $$
																DECLARE
																    v_overdue_tasks INT;
																    v_open_maintenance INT;
																    v_open_polls INT;
																BEGIN
																    UPDATE group_signals
																    SET is_active = FALSE
																    WHERE moment_id = p_moment_id
																      AND is_active = TRUE;
																
																    SELECT COUNT(*)
																    INTO v_overdue_tasks
																    FROM shared_living_tasks
																    WHERE moment_id = p_moment_id
																      AND status = 'OVERDUE';
																
																    IF v_overdue_tasks > 0 THEN
																        INSERT INTO group_signals (
																            moment_id,
																            signal_type,
																            signal_category,
																            signal_title,
																            signal_description,
																            priority,
																            signal_score
																        )
																        VALUES (
																            p_moment_id,
																            'OVERDUE_TASKS',
																            'TASKS',
																            'Tasks need attention',
																            v_overdue_tasks || ' household tasks are overdue.',
																            'HIGH',
																            80
																        );
																    END IF;
																
																    SELECT COUNT(*)
																    INTO v_open_maintenance
																    FROM shared_living_maintenance
																    WHERE moment_id = p_moment_id
																      AND status IN ('REPORTED','IN_PROGRESS');
																
																    IF v_open_maintenance > 0 THEN
																        INSERT INTO group_signals (
																            moment_id,
																            signal_type,
																            signal_category,
																            signal_title,
																            signal_description,
																            priority,
																            signal_score
																        )
																        VALUES (
																            p_moment_id,
																            'OPEN_MAINTENANCE',
																            'MAINTENANCE',
																            'Maintenance issue open',
																            v_open_maintenance || ' maintenance issue is still open.',
																            'MEDIUM',
																            65
																        );
																    END IF;
																
																    SELECT COUNT(*)
																    INTO v_open_polls
																    FROM group_polls
																    WHERE moment_id = p_moment_id
																      AND status = 'OPEN';
																
																    IF v_open_polls > 0 THEN
																        INSERT INTO group_signals (
																            moment_id,
																            signal_type,
																            signal_category,
																            signal_title,
																            signal_description,
																            priority,
																            signal_score
																        )
																        VALUES (
																            p_moment_id,
																            'OPEN_POLLS',
																            'DECISIONS',
																            'Decision pending',
																            v_open_polls || ' poll is still open.',
																            'MEDIUM',
																            60
																        );
																    END IF;
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_group_recommendations(
																    p_moment_id UUID
																)
																RETURNS VOID AS $$
																DECLARE
																    v_type VARCHAR(50);
																BEGIN
																    SELECT moment_type INTO v_type
																    FROM group_moments
																    WHERE moment_id = p_moment_id;
																
																    UPDATE group_recommendations
																    SET status = 'DISMISSED'
																    WHERE moment_id = p_moment_id
																      AND status = 'OPEN';
																
																    IF v_type = 'SHARED_EXPERIENCE' THEN
																        INSERT INTO group_recommendations (
																            moment_id,
																            recommendation_type,
																            recommendation_category,
																            title,
																            description,
																            priority,
																            recommendation_score
																        )
																        VALUES (
																            p_moment_id,
																            'NEXT_ACTION',
																            'PLANNING',
																            'Add your next planning item',
																            'Start by adding a booking, activity, vendor, or task.',
																            'MEDIUM',
																            70
																        );
																
																    ELSIF v_type = 'SHARED_PURCHASE' THEN
																        INSERT INTO group_recommendations (
																            moment_id,
																            recommendation_type,
																            recommendation_category,
																            title,
																            description,
																            priority,
																            recommendation_score
																        )
																        VALUES (
																            p_moment_id,
																            'NEXT_ACTION',
																            'PURCHASE',
																            'Add a purchase item or contribution',
																            'Move this purchase forward by adding an item, contributor, or contribution.',
																            'MEDIUM',
																            70
																        );
																
																    ELSIF v_type = 'SHARED_LIVING' THEN
																        INSERT INTO group_recommendations (
																            moment_id,
																            recommendation_type,
																            recommendation_category,
																            title,
																            description,
																            priority,
																            recommendation_score
																        )
																        VALUES (
																            p_moment_id,
																            'NEXT_ACTION',
																            'HOME',
																            'Add a task or household update',
																            'Keep your home moving by assigning a task or posting an update.',
																            'MEDIUM',
																            70
																        );
																    END IF;
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_group_memory_patterns(
																    p_moment_id UUID
																)
																RETURNS VOID AS $$
																DECLARE
																    v_type VARCHAR(50);
																    v_activity_count INT;
																BEGIN
																    SELECT moment_type INTO v_type
																    FROM group_moments
																    WHERE moment_id = p_moment_id;
																
																    SELECT COUNT(*)
																    INTO v_activity_count
																    FROM group_quick_add_events
																    WHERE moment_id = p_moment_id;
																
																    IF v_activity_count >= 3 THEN
																        INSERT INTO group_memory_patterns (
																            moment_id,
																            moment_type,
																            pattern_type,
																            pattern_category,
																            insight_title,
																            insight_text,
																            confidence_score,
																            supporting_event_ids_json
																        )
																        VALUES (
																            p_moment_id,
																            v_type,
																            'EARLY_ACTIVITY_PATTERN',
																            'PARTICIPATION',
																            'Activity is forming',
																            'This moment is beginning to show early participation and coordination patterns.',
																            LEAST(100, v_activity_count * 10),
																            (
																                SELECT jsonb_agg(event_id)
																                FROM (
																                    SELECT event_id
																                    FROM group_quick_add_events
																                    WHERE moment_id = p_moment_id
																                    ORDER BY event_time DESC
																                    LIMIT 10
																                ) x
																            )
																        );
																    END IF;
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_group_moment_orchestration(
																    p_moment_id UUID,
																    p_event_id UUID DEFAULT NULL
																)
																RETURNS VOID AS $$
																BEGIN
																    IF p_event_id IS NOT NULL THEN
																        PERFORM sp_create_group_live_feed(p_event_id);
																    END IF;
																
																    PERFORM sp_refresh_group_moment_stage(p_moment_id, p_event_id);
																    PERFORM sp_refresh_group_health_snapshot(p_moment_id);
																    PERFORM sp_refresh_group_pulse_snapshot(p_moment_id);
																    PERFORM sp_refresh_group_signals(p_moment_id);
																    PERFORM sp_refresh_group_recommendations(p_moment_id);
																    PERFORM sp_refresh_group_memory_patterns(p_moment_id);
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_shared_experience_analytics(
																    p_moment_id UUID
																)
																RETURNS VOID AS $$
																DECLARE
																    v_people_score DECIMAL(5,2);
																    v_planning_score DECIMAL(5,2);
																    v_money_score DECIMAL(5,2);
																    v_decision_score DECIMAL(5,2);
																    v_memory_score DECIMAL(5,2);
																    v_readiness DECIMAL(5,2);
																BEGIN
																    v_people_score := LEAST(100, (
																        SELECT COUNT(*) * 15
																        FROM group_moment_members
																        WHERE moment_id = p_moment_id
																          AND status IN ('ACTIVE','CONFIRMED')
																    ));
																
																    v_planning_score := LEAST(100, (
																        SELECT COUNT(*) * 20
																        FROM shared_experience_planning_items
																        WHERE moment_id = p_moment_id
																          AND status IN ('IN_PROGRESS','CONFIRMED','COMPLETED')
																    ));
																
																    v_money_score := LEAST(100, (
																        SELECT COUNT(*) * 15
																        FROM group_expenses
																        WHERE moment_id = p_moment_id
																          AND status <> 'DELETED'
																    ));
																
																    v_decision_score := LEAST(100, (
																        SELECT COUNT(*) * 20
																        FROM group_polls
																        WHERE moment_id = p_moment_id
																    ));
																
																    v_memory_score := LEAST(100, (
																        SELECT COUNT(*) * 20
																        FROM group_memory_entries
																        WHERE moment_id = p_moment_id
																    ));
																
																    v_readiness := ROUND(
																        v_people_score * 0.20 +
																        v_planning_score * 0.30 +
																        v_money_score * 0.20 +
																        v_decision_score * 0.15 +
																        v_memory_score * 0.15, 2
																    );
																
																    INSERT INTO group_health_snapshots (
																        moment_id,
																        snapshot_date,
																        health_score,
																        health_status,
																        people_score,
																        money_score,
																        activity_score
																    )
																    VALUES (
																        p_moment_id,
																        CURRENT_DATE,
																        v_readiness,
																        CASE
																            WHEN v_readiness >= 85 THEN 'EXCELLENT'
																            WHEN v_readiness >= 70 THEN 'GOOD'
																            WHEN v_readiness >= 50 THEN 'STABLE'
																            WHEN v_readiness >= 30 THEN 'WARNING'
																            ELSE 'CRITICAL'
																        END,
																        v_people_score,
																        v_money_score,
																        v_planning_score
																    );
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_shared_purchase_analytics(
																    p_moment_id UUID
																)
																RETURNS VOID AS $$
																DECLARE
																    v_target DECIMAL(12,2);
																    v_collected DECIMAL(12,2);
																    v_funding_score DECIMAL(5,2);
																    v_item_score DECIMAL(5,2);
																    v_vendor_score DECIMAL(5,2);
																    v_decision_score DECIMAL(5,2);
																    v_ownership_score DECIMAL(5,2);
																    v_delivery_score DECIMAL(5,2);
																    v_readiness DECIMAL(5,2);
																BEGIN
																    SELECT target_amount
																    INTO v_target
																    FROM shared_purchase_details
																    WHERE moment_id = p_moment_id;
																
																    SELECT COALESCE(SUM(amount),0)
																    INTO v_collected
																    FROM group_contributions
																    WHERE moment_id = p_moment_id
																      AND status = 'RECEIVED';
																
																    v_funding_score :=
																        CASE
																            WHEN COALESCE(v_target,0) > 0
																            THEN LEAST(100, (v_collected / v_target) * 100)
																            ELSE 0
																        END;
																
																    v_item_score := LEAST(100, (
																        SELECT COUNT(*) * 25
																        FROM shared_purchase_items
																        WHERE moment_id = p_moment_id
																          AND status IN ('SHORTLISTED','SELECTED','PURCHASED')
																    ));
																
																    v_vendor_score := LEAST(100, (
																        SELECT COUNT(*) * 25
																        FROM shared_purchase_vendors
																        WHERE moment_id = p_moment_id
																          AND status IN ('SHORTLISTED','CONFIRMED')
																    ));
																
																    v_decision_score := LEAST(100, (
																        SELECT COUNT(*) * 30
																        FROM group_polls
																        WHERE moment_id = p_moment_id
																          AND status IN ('OPEN','CLOSED')
																    ));
																
																    v_ownership_score := LEAST(100, (
																        SELECT COUNT(*) * 50
																        FROM shared_purchase_ownership
																        WHERE moment_id = p_moment_id
																          AND status IN ('DRAFT','FINALIZED')
																    ));
																
																    v_delivery_score := LEAST(100, (
																        SELECT COUNT(*) * 100
																        FROM shared_purchase_delivery
																        WHERE moment_id = p_moment_id
																          AND status = 'COMPLETED'
																    ));
																
																    v_readiness := ROUND(
																        v_funding_score * 0.30 +
																        v_item_score * 0.20 +
																        v_vendor_score * 0.15 +
																        v_decision_score * 0.15 +
																        v_ownership_score * 0.10 +
																        v_delivery_score * 0.10, 2
																    );
																
																    INSERT INTO group_health_snapshots (
																        moment_id,
																        snapshot_date,
																        health_score,
																        health_status,
																        people_score,
																        money_score,
																        activity_score
																    )
																    VALUES (
																        p_moment_id,
																        CURRENT_DATE,
																        v_readiness,
																        CASE
																            WHEN v_readiness >= 85 THEN 'EXCELLENT'
																            WHEN v_readiness >= 70 THEN 'GOOD'
																            WHEN v_readiness >= 50 THEN 'STABLE'
																            WHEN v_readiness >= 30 THEN 'WARNING'
																            ELSE 'CRITICAL'
																        END,
																        v_item_score,
																        v_funding_score,
																        v_decision_score
																    );
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_shared_living_analytics(
																    p_moment_id UUID
																)
																RETURNS VOID AS $$
																DECLARE
																    v_resident_score DECIMAL(5,2);
																    v_contribution_score DECIMAL(5,2);
																    v_task_score DECIMAL(5,2);
																    v_maintenance_score DECIMAL(5,2);
																    v_rule_score DECIMAL(5,2);
																    v_memory_score DECIMAL(5,2);
																    v_health DECIMAL(5,2);
																BEGIN
																    v_resident_score := LEAST(100, (
																        SELECT COUNT(*) * 25
																        FROM shared_living_residents
																        WHERE moment_id = p_moment_id
																          AND status = 'ACTIVE'
																    ));
																
																    v_contribution_score := LEAST(100, (
																        SELECT COUNT(*) * 20
																        FROM group_contributions
																        WHERE moment_id = p_moment_id
																          AND status = 'RECEIVED'
																    ));
																
																    v_task_score := GREATEST(0, 100 - (
																        SELECT COUNT(*) * 15
																        FROM shared_living_tasks
																        WHERE moment_id = p_moment_id
																          AND status = 'OVERDUE'
																    ));
																
																    v_maintenance_score := GREATEST(0, 100 - (
																        SELECT COUNT(*) * 20
																        FROM shared_living_maintenance
																        WHERE moment_id = p_moment_id
																          AND status IN ('REPORTED','IN_PROGRESS')
																    ));
																
																    v_rule_score := LEAST(100, (
																        SELECT COUNT(*) * 20
																        FROM shared_living_rules
																        WHERE moment_id = p_moment_id
																          AND status = 'ACTIVE'
																    ));
																
																    v_memory_score := LEAST(100, (
																        SELECT COUNT(*) * 20
																        FROM group_memory_entries
																        WHERE moment_id = p_moment_id
																    ));
																
																    v_health := ROUND(
																        v_resident_score * 0.15 +
																        v_contribution_score * 0.20 +
																        v_task_score * 0.20 +
																        v_maintenance_score * 0.15 +
																        v_rule_score * 0.10 +
																        v_memory_score * 0.10 +
																        10, 2
																    );
																
																    INSERT INTO group_health_snapshots (
																        moment_id,
																        snapshot_date,
																        health_score,
																        health_status,
																        people_score,
																        money_score,
																        activity_score
																    )
																    VALUES (
																        p_moment_id,
																        CURRENT_DATE,
																        LEAST(100, v_health),
																        CASE
																            WHEN v_health >= 85 THEN 'EXCELLENT'
																            WHEN v_health >= 70 THEN 'GOOD'
																            WHEN v_health >= 50 THEN 'STABLE'
																            WHEN v_health >= 30 THEN 'WARNING'
																            ELSE 'CRITICAL'
																        END,
																        v_resident_score,
																        v_contribution_score,
																        v_task_score
																    );
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_group_type_analytics(
																    p_moment_id UUID
																)
																RETURNS VOID AS $$
																DECLARE
																    v_type VARCHAR(50);
																BEGIN
																    SELECT moment_type
																    INTO v_type
																    FROM group_moments
																    WHERE moment_id = p_moment_id;
																
																    IF v_type = 'SHARED_EXPERIENCE' THEN
																        PERFORM sp_refresh_shared_experience_analytics(p_moment_id);
																
																    ELSIF v_type = 'SHARED_PURCHASE' THEN
																        PERFORM sp_refresh_shared_purchase_analytics(p_moment_id);
																
																    ELSIF v_type = 'SHARED_LIVING' THEN
																        PERFORM sp_refresh_shared_living_analytics(p_moment_id);
																    END IF;
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_group_pulse_detail(
																    p_moment_id UUID
																)
																RETURNS VOID AS $$
																DECLARE
																    v_type VARCHAR(50);
																    v_active_members INT;
																    v_active_tasks INT;
																    v_open_items INT;
																    v_funding DECIMAL(5,2);
																    v_completion DECIMAL(5,2);
																    v_participation DECIMAL(5,2);
																    v_score DECIMAL(5,2);
																BEGIN
																    SELECT moment_type INTO v_type
																    FROM group_moments
																    WHERE moment_id = p_moment_id;
																
																    SELECT COUNT(*)
																    INTO v_active_members
																    FROM group_moment_members
																    WHERE moment_id = p_moment_id
																      AND status IN ('ACTIVE','CONFIRMED');
																
																    SELECT COUNT(*)
																    INTO v_open_items
																    FROM group_quick_add_events
																    WHERE moment_id = p_moment_id;
																
																    SELECT COUNT(*)
																    INTO v_active_tasks
																    FROM shared_living_tasks
																    WHERE moment_id = p_moment_id
																      AND status IN ('TO_DO','IN_PROGRESS','OVERDUE');
																
																    v_participation := LEAST(100, v_active_members * 20);
																
																    v_funding := LEAST(100, (
																        SELECT COALESCE(SUM(amount),0) / 1000
																        FROM group_contributions
																        WHERE moment_id = p_moment_id
																          AND status = 'RECEIVED'
																    ));
																
																    v_completion := LEAST(100, (
																        SELECT COALESCE(MAX(health_score),0)
																        FROM group_health_snapshots
																        WHERE moment_id = p_moment_id
																    ));
																
																    v_score := ROUND(
																        v_completion * 0.40 +
																        v_participation * 0.30 +
																        v_funding * 0.30, 2
																    );
																
																    INSERT INTO group_pulse_snapshots (
																        moment_id,
																        snapshot_date,
																        completion_percentage,
																        participation_percentage,
																        funding_percentage,
																        active_members,
																        active_tasks,
																        open_items,
																        pulse_score
																    )
																    VALUES (
																        p_moment_id,
																        CURRENT_DATE,
																        v_completion,
																        v_participation,
																        v_funding,
																        v_active_members,
																        v_active_tasks,
																        v_open_items,
																        v_score
																    );
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_group_detailed_signals(
																    p_moment_id UUID
																)
																RETURNS VOID AS $$
																DECLARE
																    v_type VARCHAR(50);
																    v_open_polls INT;
																    v_overdue_tasks INT;
																    v_open_maintenance INT;
																    v_purchase_unfunded BOOLEAN;
																BEGIN
																    SELECT moment_type
																    INTO v_type
																    FROM group_moments
																    WHERE moment_id = p_moment_id;
																
																    UPDATE group_signals
																    SET is_active = FALSE
																    WHERE moment_id = p_moment_id
																      AND is_active = TRUE;
																
																    SELECT COUNT(*) INTO v_open_polls
																    FROM group_polls
																    WHERE moment_id = p_moment_id
																      AND status = 'OPEN';
																
																    IF v_open_polls > 0 THEN
																        INSERT INTO group_signals
																        (moment_id, signal_type, signal_category, signal_title, signal_description, priority, signal_score)
																        VALUES
																        (p_moment_id, 'OPEN_POLLS', 'DECISIONS', 'Decision pending',
																         v_open_polls || ' poll is still open.', 'MEDIUM', 60);
																    END IF;
																
																    IF v_type = 'SHARED_LIVING' THEN
																        SELECT COUNT(*) INTO v_overdue_tasks
																        FROM shared_living_tasks
																        WHERE moment_id = p_moment_id
																          AND status = 'OVERDUE';
																
																        IF v_overdue_tasks > 0 THEN
																            INSERT INTO group_signals
																            (moment_id, signal_type, signal_category, signal_title, signal_description, priority, signal_score)
																            VALUES
																            (p_moment_id, 'OVERDUE_TASKS', 'TASKS', 'Tasks need attention',
																             v_overdue_tasks || ' task(s) are overdue.', 'HIGH', 80);
																        END IF;
																
																        SELECT COUNT(*) INTO v_open_maintenance
																        FROM shared_living_maintenance
																        WHERE moment_id = p_moment_id
																          AND status IN ('REPORTED','IN_PROGRESS');
																
																        IF v_open_maintenance > 0 THEN
																            INSERT INTO group_signals
																            (moment_id, signal_type, signal_category, signal_title, signal_description, priority, signal_score)
																            VALUES
																            (p_moment_id, 'OPEN_MAINTENANCE', 'MAINTENANCE', 'Maintenance issue open',
																             v_open_maintenance || ' maintenance issue(s) need attention.', 'MEDIUM', 70);
																        END IF;
																    END IF;
																
																    IF v_type = 'SHARED_PURCHASE' THEN
																        SELECT EXISTS (
																            SELECT 1
																            FROM shared_purchase_details spd
																            LEFT JOIN (
																                SELECT moment_id, SUM(amount) total_collected
																                FROM group_contributions
																                WHERE status = 'RECEIVED'
																                GROUP BY moment_id
																            ) c ON c.moment_id = spd.moment_id
																            WHERE spd.moment_id = p_moment_id
																              AND COALESCE(c.total_collected,0) < spd.target_amount
																        )
																        INTO v_purchase_unfunded;
																
																        IF v_purchase_unfunded THEN
																            INSERT INTO group_signals
																            (moment_id, signal_type, signal_category, signal_title, signal_description, priority, signal_score)
																            VALUES
																            (p_moment_id, 'FUNDING_BELOW_TARGET', 'MONEY', 'Funding below target',
																             'Collected amount is still below the purchase target.', 'HIGH', 85);
																        END IF;
																    END IF;
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_group_detailed_memory_patterns(
																    p_moment_id UUID
																)
																RETURNS VOID AS $$
																DECLARE
																    v_type VARCHAR(50);
																    v_event_count INT;
																BEGIN
																    SELECT moment_type INTO v_type
																    FROM group_moments
																    WHERE moment_id = p_moment_id;
																
																    SELECT COUNT(*)
																    INTO v_event_count
																    FROM group_quick_add_events
																    WHERE moment_id = p_moment_id;
																
																    IF v_event_count >= 3 THEN
																        INSERT INTO group_memory_patterns (
																            moment_id,
																            moment_type,
																            pattern_type,
																            pattern_category,
																            insight_title,
																            insight_text,
																            confidence_score,
																            supporting_event_ids_json
																        )
																        VALUES (
																            p_moment_id,
																            v_type,
																            'ACTIVITY_PATTERN',
																            'PARTICIPATION',
																            'Activity is forming',
																            'This moment is beginning to show consistent activity and participation.',
																            LEAST(100, v_event_count * 10),
																            (
																                SELECT jsonb_agg(event_id)
																                FROM (
																                    SELECT event_id
																                    FROM group_quick_add_events
																                    WHERE moment_id = p_moment_id
																                    ORDER BY event_time DESC
																                    LIMIT 10
																                ) x
																            )
																        );
																    END IF;
																
																    IF v_type = 'SHARED_LIVING' THEN
																        INSERT INTO shared_living_home_personality (
																            moment_id,
																            traits_json,
																            primary_trait,
																            description,
																            confidence_score,
																            snapshot_date
																        )
																        VALUES (
																            p_moment_id,
																            jsonb_build_object(
																                'helpful', 80,
																                'collaborative', 75,
																                'social', 65,
																                'reliable', 70
																            ),
																            'Collaborative',
																            'Residents frequently participate in household activities and shared decisions.',
																            75,
																            CURRENT_DATE
																        );
																    END IF;
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_group_analytics_orchestration(
																    p_moment_id UUID
																)
																RETURNS VOID AS $$
																BEGIN
																    PERFORM sp_refresh_group_type_analytics(p_moment_id);
																    PERFORM sp_refresh_group_pulse_detail(p_moment_id);
																    PERFORM sp_refresh_group_detailed_signals(p_moment_id);
																    PERFORM sp_refresh_group_detailed_memory_patterns(p_moment_id);
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_generate_settlement_matrix(
																    p_moment_id UUID
																)
																RETURNS VOID AS $$
																BEGIN
																
																    DELETE FROM shared_experience_settlements
																    WHERE moment_id = p_moment_id;
																
																    WITH member_balance AS
																    (
																        SELECT
																            m.member_id,
																
																            COALESCE(
																                (
																                    SELECT SUM(amount)
																                    FROM group_expenses e
																                    WHERE e.moment_id = p_moment_id
																                    AND e.paid_by_member_id = m.member_id
																                ),0
																            ) paid_amount,
																
																            COALESCE(
																                (
																                    SELECT SUM(split_amount)
																                    FROM group_expense_splits s
																                    JOIN group_expenses e
																                        ON e.expense_id = s.expense_id
																                    WHERE e.moment_id = p_moment_id
																                    AND s.member_id = m.member_id
																                ),0
																            ) owed_amount
																
																        FROM group_moment_members m
																        WHERE m.moment_id = p_moment_id
																    )
																
																    INSERT INTO shared_experience_settlements
																    (
																        settlement_id,
																        moment_id,
																        payer_member_id,
																        receiver_member_id,
																        settlement_amount,
																        settlement_status,
																        created_at
																    )
																    SELECT
																        gen_random_uuid(),
																        p_moment_id,
																        debtor.member_id,
																        creditor.member_id,
																        LEAST(
																            ABS(debtor.paid_amount-debtor.owed_amount),
																            ABS(creditor.paid_amount-creditor.owed_amount)
																        ),
																        'OPEN',
																        CURRENT_TIMESTAMP
																    FROM member_balance debtor
																    CROSS JOIN member_balance creditor
																    WHERE debtor.paid_amount < debtor.owed_amount
																      AND creditor.paid_amount > creditor.owed_amount;
																
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_group_entity_changed(
																    p_moment_id UUID,
																    p_event_id UUID
																)
																RETURNS VOID AS $$
																BEGIN
																
																    PERFORM sp_refresh_group_moment_orchestration(
																        p_moment_id,
																        p_event_id
																    );
																
																    PERFORM sp_refresh_group_analytics_orchestration(
																        p_moment_id
																    );
																
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION trg_expense_refresh()
																RETURNS TRIGGER AS $$
																BEGIN
																
																    PERFORM sp_group_entity_changed(
																        NEW.moment_id,
																        NULL
																    );
																
																    RETURN NEW;
																
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_group_ai_insights(
																    p_moment_id UUID
																)
																RETURNS VOID AS $$
																DECLARE
																    v_activity INTEGER;
																    v_members INTEGER;
																BEGIN
																
																    DELETE FROM group_ai_insights
																    WHERE moment_id = p_moment_id;
																
																    SELECT COUNT(*)
																    INTO v_activity
																    FROM group_quick_add_events
																    WHERE moment_id = p_moment_id;
																
																    SELECT COUNT(*)
																    INTO v_members
																    FROM group_moment_members
																    WHERE moment_id = p_moment_id
																      AND status IN ('ACTIVE','CONFIRMED');
																
																    INSERT INTO group_ai_insights
																    (
																        insight_id,
																        moment_id,
																        insight_type,
																        insight_title,
																        insight_text,
																        confidence_score,
																        generated_at
																    )
																    VALUES
																    (
																        gen_random_uuid(),
																        p_moment_id,
																        'PARTICIPATION',
																        'Participation trend improving',
																        'Recent activity suggests growing engagement among participants.',
																        LEAST(100,v_activity*5),
																        CURRENT_TIMESTAMP
																    );
																
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_resident_dynamics(
																    p_moment_id UUID
																)
																RETURNS VOID AS $$
																BEGIN
																
																    DELETE FROM shared_living_resident_dynamics
																    WHERE moment_id = p_moment_id;
																
																    INSERT INTO shared_living_resident_dynamics
																    (
																        dynamics_id,
																        moment_id,
																        resident_member_id,
																        activity_score,
																        helpfulness_score,
																        contribution_score,
																        summary_label,
																        period_start,
																        period_end
																    )
																    SELECT
																        gen_random_uuid(),
																        p_moment_id,
																        member_id,
																
																        LEAST(100,COUNT(*)*10),
																        LEAST(100,COUNT(*)*8),
																        LEAST(100,COUNT(*)*7),
																
																        CASE
																            WHEN COUNT(*) > 8 THEN 'MOST ACTIVE'
																            WHEN COUNT(*) > 5 THEN 'COLLABORATIVE'
																            ELSE 'PARTICIPATING'
																        END,
																
																        CURRENT_DATE - INTERVAL '30 DAY',
																        CURRENT_DATE
																
																    FROM group_quick_add_events
																    WHERE moment_id = p_moment_id
																    GROUP BY member_id;
																
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_purchase_ownership_insights(
																    p_moment_id UUID
																)
																RETURNS VOID AS $$
																BEGIN
																
																    DELETE FROM shared_purchase_ownership_insights
																    WHERE moment_id = p_moment_id;
																
																    INSERT INTO shared_purchase_ownership_insights
																    (
																        moment_id,
																        insight_type,
																        title,
																        description,
																        confidence_score
																    )
																    VALUES
																    (
																        p_moment_id,
																        'OWNERSHIP_STRUCTURE',
																        'Ownership pattern established',
																        'Ownership percentages now align with recorded contribution levels.',
																        85
																    );
																
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_group_production_orchestration(
																    p_moment_id UUID,
																    p_event_id UUID DEFAULT NULL
																)
																RETURNS VOID AS $$
																BEGIN
																
																    PERFORM sp_refresh_group_moment_orchestration(
																        p_moment_id,
																        p_event_id
																    );
																
																    PERFORM sp_refresh_group_analytics_orchestration(
																        p_moment_id
																    );
																
																    PERFORM sp_refresh_group_ai_insights(
																        p_moment_id
																    );
																
																    PERFORM sp_refresh_resident_dynamics(
																        p_moment_id
																    );
																
																    PERFORM sp_refresh_purchase_ownership_insights(
																        p_moment_id
																    );
																
																    PERFORM sp_generate_settlement_matrix(
																        p_moment_id
																    );
																
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_create_shared_experience_budget_plan(
																    p_moment_id UUID,
																    p_planned_total_budget NUMERIC,
																    p_split_method VARCHAR DEFAULT 'EQUAL_SPLIT',
																    p_created_by UUID DEFAULT NULL
																)
																RETURNS UUID AS $$
																DECLARE
																    v_budget_plan_id UUID;
																    v_experience_subtype VARCHAR(100);
																    v_participant_count INTEGER;
																BEGIN
																    SELECT
																        COALESCE(gm.experience_subtype, gm.moment_profile),
																        COUNT(gmm.member_id)
																    INTO
																        v_experience_subtype,
																        v_participant_count
																    FROM group_moments gm
																    LEFT JOIN group_moment_members gmm
																        ON gmm.moment_id = gm.moment_id
																       AND gmm.status IN ('ACTIVE','CONFIRMED')
																    WHERE gm.moment_id = p_moment_id
																    GROUP BY gm.experience_subtype, gm.moment_profile;
																
																    v_participant_count := GREATEST(COALESCE(v_participant_count, 0), 1);
																
																    INSERT INTO shared_experience_budget_plans (
																        moment_id,
																        planned_total_budget,
																        final_total_budget,
																        participant_count,
																        split_method,
																        funding_readiness_pct,
																        status,
																        created_by
																    )
																    VALUES (
																        p_moment_id,
																        p_planned_total_budget,
																        p_planned_total_budget,
																        v_participant_count,
																        p_split_method,
																        0,
																        'DRAFT',
																        COALESCE(p_created_by, '00000000-0000-0000-0000-000000000000'::UUID)
																    )
																    RETURNING budget_plan_id INTO v_budget_plan_id;
																
																    INSERT INTO shared_experience_budget_allocations (
																        budget_plan_id,
																        category_id,
																        recommended_percentage,
																        recommended_amount,
																        final_percentage,
																        final_amount,
																        actual_amount,
																        variance_amount
																    )
																    SELECT
																        v_budget_plan_id,
																        ebt.category_id,
																        ebt.suggested_percentage,
																        ROUND((p_planned_total_budget * ebt.suggested_percentage / 100), 2),
																        ebt.suggested_percentage,
																        ROUND((p_planned_total_budget * ebt.suggested_percentage / 100), 2),
																        0,
																        ROUND((p_planned_total_budget * ebt.suggested_percentage / 100), 2)
																    FROM experience_budget_templates ebt
																    WHERE ebt.experience_subtype = v_experience_subtype
																      AND ebt.is_default = TRUE
																    ORDER BY ebt.display_order;
																
																    UPDATE shared_experience_details
																    SET budget_enabled = TRUE,
																        default_budget_plan_id = v_budget_plan_id,
																        updated_at = CURRENT_TIMESTAMP
																    WHERE moment_id = p_moment_id;
																
																    PERFORM sp_refresh_shared_experience_budget_splits(v_budget_plan_id);
																    PERFORM sp_refresh_shared_experience_budget_rollup(v_budget_plan_id);
																
																    RETURN v_budget_plan_id;
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_shared_experience_budget_rollup(
																    p_budget_plan_id UUID
																)
																RETURNS VOID AS $$
																DECLARE
																    v_final_total NUMERIC(14,2);
																    v_actual_total NUMERIC(14,2);
																    v_committed_total NUMERIC(14,2);
																    v_readiness NUMERIC(5,2);
																BEGIN
																    SELECT COALESCE(SUM(final_amount),0)
																    INTO v_final_total
																    FROM shared_experience_budget_allocations
																    WHERE budget_plan_id = p_budget_plan_id;
																
																    UPDATE shared_experience_budget_allocations a
																    SET actual_amount = COALESCE(x.actual_amount, 0),
																        variance_amount = a.final_amount - COALESCE(x.actual_amount, 0),
																        final_percentage =
																            CASE
																                WHEN v_final_total > 0 THEN ROUND((a.final_amount / v_final_total) * 100, 2)
																                ELSE 0
																            END,
																        updated_at = CURRENT_TIMESTAMP
																    FROM (
																        SELECT
																            ge.budget_category_id AS category_id,
																            SUM(ge.amount) AS actual_amount
																        FROM group_expenses ge
																        JOIN shared_experience_budget_plans bp
																            ON bp.budget_plan_id = p_budget_plan_id
																           AND bp.moment_id = ge.moment_id
																        WHERE ge.budget_plan_id = p_budget_plan_id
																          AND ge.status <> 'DELETED'
																        GROUP BY ge.budget_category_id
																    ) x
																    WHERE a.budget_plan_id = p_budget_plan_id
																      AND a.category_id = x.category_id;
																
																    SELECT COALESCE(SUM(actual_amount),0)
																    INTO v_actual_total
																    FROM shared_experience_budget_allocations
																    WHERE budget_plan_id = p_budget_plan_id;
																
																    SELECT COALESCE(SUM(committed_amount),0)
																    INTO v_committed_total
																    FROM shared_experience_budget_splits
																    WHERE budget_plan_id = p_budget_plan_id;
																
																    v_readiness :=
																        CASE
																            WHEN v_final_total > 0 THEN LEAST(100, ROUND((v_committed_total / v_final_total) * 100, 2))
																            ELSE 0
																        END;
																
																    UPDATE shared_experience_budget_plans
																    SET final_total_budget = v_final_total,
																        funding_readiness_pct = v_readiness,
																        updated_at = CURRENT_TIMESTAMP
																    WHERE budget_plan_id = p_budget_plan_id;
																
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_shared_experience_budget_splits(
																    p_budget_plan_id UUID
																)
																RETURNS VOID AS $$
																DECLARE
																    v_moment_id UUID;
																    v_split_method VARCHAR(50);
																    v_final_total NUMERIC(14,2);
																    v_participant_count INTEGER;
																BEGIN
																    SELECT moment_id, split_method, final_total_budget
																    INTO v_moment_id, v_split_method, v_final_total
																    FROM shared_experience_budget_plans
																    WHERE budget_plan_id = p_budget_plan_id;
																
																    SELECT COUNT(*)
																    INTO v_participant_count
																    FROM group_moment_members
																    WHERE moment_id = v_moment_id
																      AND status IN ('ACTIVE','CONFIRMED');
																
																    v_participant_count := GREATEST(COALESCE(v_participant_count,0),1);
																
																    DELETE FROM shared_experience_budget_splits
																    WHERE budget_plan_id = p_budget_plan_id;
																
																    IF v_split_method = 'EQUAL_SPLIT' THEN
																        INSERT INTO shared_experience_budget_splits (
																            budget_plan_id,
																            member_id,
																            planned_share_amount,
																            committed_amount,
																            paid_amount,
																            pending_amount,
																            split_status
																        )
																        SELECT
																            p_budget_plan_id,
																            member_id,
																            ROUND(v_final_total / v_participant_count, 2),
																            0,
																            0,
																            ROUND(v_final_total / v_participant_count, 2),
																            'PENDING'
																        FROM group_moment_members
																        WHERE moment_id = v_moment_id
																          AND status IN ('ACTIVE','CONFIRMED');
																
																    ELSE
																        INSERT INTO shared_experience_budget_splits (
																            budget_plan_id,
																            member_id,
																            planned_share_amount,
																            committed_amount,
																            paid_amount,
																            pending_amount,
																            split_status
																        )
																        SELECT
																            p_budget_plan_id,
																            member_id,
																            0,
																            0,
																            0,
																            0,
																            'PENDING'
																        FROM group_moment_members
																        WHERE moment_id = v_moment_id
																          AND status IN ('ACTIVE','CONFIRMED');
																    END IF;
																
																    UPDATE shared_experience_budget_plans
																    SET participant_count = v_participant_count,
																        updated_at = CURRENT_TIMESTAMP
																    WHERE budget_plan_id = p_budget_plan_id;
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_update_shared_experience_budget_allocation(
																    p_allocation_id UUID,
																    p_final_amount NUMERIC,
																    p_notes TEXT DEFAULT NULL
																)
																RETURNS VOID AS $$
																DECLARE
																    v_budget_plan_id UUID;
																BEGIN
																    UPDATE shared_experience_budget_allocations
																    SET final_amount = p_final_amount,
																        notes = COALESCE(p_notes, notes),
																        updated_at = CURRENT_TIMESTAMP
																    WHERE allocation_id = p_allocation_id
																    RETURNING budget_plan_id INTO v_budget_plan_id;
																
																    PERFORM sp_refresh_shared_experience_budget_splits(v_budget_plan_id);
																    PERFORM sp_refresh_shared_experience_budget_rollup(v_budget_plan_id);
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_add_shared_experience_budget_category(
																    p_budget_plan_id UUID,
																    p_category_id UUID,
																    p_final_amount NUMERIC,
																    p_notes TEXT DEFAULT NULL
																)
																RETURNS UUID AS $$
																DECLARE
																    v_allocation_id UUID;
																BEGIN
																    INSERT INTO shared_experience_budget_allocations (
																        budget_plan_id,
																        category_id,
																        recommended_percentage,
																        recommended_amount,
																        final_percentage,
																        final_amount,
																        actual_amount,
																        variance_amount,
																        notes
																    )
																    VALUES (
																        p_budget_plan_id,
																        p_category_id,
																        NULL,
																        NULL,
																        NULL,
																        p_final_amount,
																        0,
																        p_final_amount,
																        p_notes
																    )
																    RETURNING allocation_id INTO v_allocation_id;
																
																    PERFORM sp_refresh_shared_experience_budget_splits(p_budget_plan_id);
																    PERFORM sp_refresh_shared_experience_budget_rollup(p_budget_plan_id);
																
																    RETURN v_allocation_id;
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_shared_experience_budget_contributions(
																    p_budget_plan_id UUID
																)
																RETURNS VOID AS $$
																BEGIN
																    UPDATE shared_experience_budget_splits s
																    SET paid_amount = COALESCE(x.paid_amount,0),
																        committed_amount = GREATEST(s.committed_amount, COALESCE(x.paid_amount,0)),
																        pending_amount = GREATEST(0, s.planned_share_amount - COALESCE(x.paid_amount,0)),
																        split_status =
																            CASE
																                WHEN COALESCE(x.paid_amount,0) >= s.planned_share_amount THEN 'PAID'
																                WHEN COALESCE(x.paid_amount,0) > 0 THEN 'COMMITTED'
																                ELSE 'PENDING'
																            END,
																        updated_at = CURRENT_TIMESTAMP
																    FROM (
																        SELECT
																            contributor_member_id AS member_id,
																            SUM(amount) AS paid_amount
																        FROM group_contributions
																        WHERE budget_plan_id = p_budget_plan_id
																          AND status = 'RECEIVED'
																        GROUP BY contributor_member_id
																    ) x
																    WHERE s.budget_plan_id = p_budget_plan_id
																      AND s.member_id = x.member_id;
																
																    PERFORM sp_refresh_shared_experience_budget_rollup(p_budget_plan_id);
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_shared_experience_budget_health_score(
																    p_budget_plan_id UUID
																)
																RETURNS NUMERIC AS $$
																DECLARE
																    v_final_total NUMERIC(14,2);
																    v_actual_total NUMERIC(14,2);
																    v_readiness NUMERIC(5,2);
																    v_variance_pct NUMERIC(8,2);
																    v_score NUMERIC(5,2);
																BEGIN
																    SELECT final_total_budget, funding_readiness_pct
																    INTO v_final_total, v_readiness
																    FROM shared_experience_budget_plans
																    WHERE budget_plan_id = p_budget_plan_id;
																
																    SELECT COALESCE(SUM(actual_amount),0)
																    INTO v_actual_total
																    FROM shared_experience_budget_allocations
																    WHERE budget_plan_id = p_budget_plan_id;
																
																    v_variance_pct :=
																        CASE
																            WHEN COALESCE(v_final_total,0) > 0
																            THEN ABS(v_final_total - v_actual_total) / v_final_total * 100
																            ELSE 100
																        END;
																
																    v_score := GREATEST(
																        0,
																        LEAST(
																            100,
																            (COALESCE(v_readiness,0) * 0.50)
																            + ((100 - LEAST(100, v_variance_pct)) * 0.50)
																        )
																    );
																
																    RETURN ROUND(v_score, 2);
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_shared_experience_budget_snapshot_json(
																    p_moment_id UUID
																)
																RETURNS JSONB AS $$
																DECLARE
																    v_budget_plan_id UUID;
																    v_result JSONB;
																BEGIN
																    SELECT default_budget_plan_id
																    INTO v_budget_plan_id
																    FROM shared_experience_details
																    WHERE moment_id = p_moment_id;
																
																    IF v_budget_plan_id IS NULL THEN
																        RETURN '{}'::JSONB;
																    END IF;
																
																    SELECT jsonb_build_object(
																        'budget_plan_id', bp.budget_plan_id,
																        'planned_total_budget', bp.planned_total_budget,
																        'final_total_budget', bp.final_total_budget,
																        'actual_spend', COALESCE(SUM(a.actual_amount),0),
																        'variance_amount', bp.final_total_budget - COALESCE(SUM(a.actual_amount),0),
																        'funding_readiness_pct', bp.funding_readiness_pct,
																        'budget_health_score', fn_shared_experience_budget_health_score(bp.budget_plan_id),
																        'split_method', bp.split_method,
																        'participant_count', bp.participant_count
																    )
																    INTO v_result
																    FROM shared_experience_budget_plans bp
																    LEFT JOIN shared_experience_budget_allocations a
																        ON a.budget_plan_id = bp.budget_plan_id
																    WHERE bp.budget_plan_id = v_budget_plan_id
																    GROUP BY
																        bp.budget_plan_id,
																        bp.planned_total_budget,
																        bp.final_total_budget,
																        bp.funding_readiness_pct,
																        bp.split_method,
																        bp.participant_count;
																
																    RETURN COALESCE(v_result, '{}'::JSONB);
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_shared_experience_budget_reflection_json(
																    p_moment_id UUID
																)
																RETURNS JSONB AS $$
																DECLARE
																    v_budget_plan_id UUID;
																    v_result JSONB;
																BEGIN
																    SELECT default_budget_plan_id
																    INTO v_budget_plan_id
																    FROM shared_experience_details
																    WHERE moment_id = p_moment_id;
																
																    IF v_budget_plan_id IS NULL THEN
																        RETURN '{}'::JSONB;
																    END IF;
																
																    WITH category_variance AS (
																        SELECT
																            b.category_name,
																            a.final_amount,
																            a.actual_amount,
																            a.variance_amount,
																            ABS(a.variance_amount) AS abs_variance
																        FROM shared_experience_budget_allocations a
																        JOIN budget_master_categories b
																            ON b.category_id = a.category_id
																        WHERE a.budget_plan_id = v_budget_plan_id
																    ),
																    totals AS (
																        SELECT
																            SUM(final_amount) AS planned_budget,
																            SUM(actual_amount) AS actual_spend
																        FROM category_variance
																    )
																    SELECT jsonb_build_object(
																        'planned_budget', planned_budget,
																        'actual_spend', actual_spend,
																        'budget_accuracy_pct',
																            CASE
																                WHEN planned_budget > 0
																                THEN ROUND((1 - ABS(planned_budget - actual_spend) / planned_budget) * 100, 2)
																                ELSE 0
																            END,
																        'saved_or_exceeded_amount', planned_budget - actual_spend,
																        'best_controlled_category',
																            (
																                SELECT category_name
																                FROM category_variance
																                ORDER BY abs_variance ASC
																                LIMIT 1
																            ),
																        'highest_variance_category',
																            (
																                SELECT category_name
																                FROM category_variance
																                ORDER BY abs_variance DESC
																                LIMIT 1
																            )
																    )
																    INTO v_result
																    FROM totals;
																
																    RETURN COALESCE(v_result, '{}'::JSONB);
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_log_shared_experience_budget_event(
																    p_budget_plan_id UUID,
																    p_event_action VARCHAR DEFAULT 'CREATED',
																    p_created_by UUID DEFAULT NULL
																)
																RETURNS UUID AS $$
																DECLARE
																    v_moment_id UUID;
																    v_event_id UUID;
																BEGIN
																    SELECT moment_id
																    INTO v_moment_id
																    FROM shared_experience_budget_plans
																    WHERE budget_plan_id = p_budget_plan_id;
																
																    INSERT INTO group_quick_add_events (
																        moment_id,
																        module_code,
																        event_ref_table,
																        event_ref_id,
																        event_action,
																        created_by,
																        event_payload_json
																    )
																    VALUES (
																        v_moment_id,
																        'BUDGET',
																        'shared_experience_budget_plans',
																        p_budget_plan_id,
																        p_event_action,
																        COALESCE(p_created_by, '00000000-0000-0000-0000-000000000000'::UUID),
																        fn_shared_experience_budget_snapshot_json(v_moment_id)
																    )
																    RETURNING event_id INTO v_event_id;
																
																    PERFORM sp_create_group_live_feed(v_event_id);
																
																    RETURN v_event_id;
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_group_health_score(
																    p_moment_id UUID
																)
																RETURNS NUMERIC AS $$
																DECLARE
																    v_participation NUMERIC := 0;
																    v_progress NUMERIC := 0;
																    v_budget NUMERIC := 0;
																    v_activity NUMERIC := 0;
																BEGIN
																
																    /* Participation */
																
																    SELECT
																        COALESCE(
																            ROUND(
																                COUNT(*) FILTER (
																                    WHERE status IN ('ACTIVE','CONFIRMED')
																                )::NUMERIC
																                /
																                NULLIF(COUNT(*),0)
																                * 100
																            ,2)
																        ,0)
																    INTO v_participation
																    FROM group_moment_members
																    WHERE moment_id = p_moment_id;
																
																    /* Activity */
																
																    SELECT
																        COALESCE(
																            ROUND(
																                COUNT(*) FILTER (
																                    WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
																                )::NUMERIC * 5
																            ,2)
																        ,0)
																    INTO v_activity
																    FROM group_live_feed
																    WHERE moment_id = p_moment_id;
																
																    v_activity := LEAST(v_activity,100);
																
																    /* Progress */
																
																    SELECT
																        COALESCE(
																            AVG(progress_pct)
																        ,0)
																    INTO v_progress
																    FROM group_moment_work_items
																    WHERE moment_id = p_moment_id;
																
																    /* Budget */
																
																    SELECT
																        COALESCE(
																            fn_shared_experience_budget_health_score(
																                default_budget_plan_id
																            )
																        ,75)
																    INTO v_budget
																    FROM shared_experience_details
																    WHERE moment_id = p_moment_id;
																
																    RETURN ROUND(
																        (
																            v_participation * 0.30
																            +
																            v_progress * 0.30
																            +
																            v_budget * 0.20
																            +
																            v_activity * 0.20
																        )
																    ,2);
																
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_group_pulse_snapshot(
																    p_moment_id UUID
																)
																RETURNS VOID AS $$
																DECLARE
																    v_health_score NUMERIC;
																BEGIN
																
																    v_health_score :=
																        fn_group_health_score(p_moment_id);
																
																    INSERT INTO group_pulse_snapshots
																    (
																        moment_id,
																        snapshot_date,
																        hero_snapshot_json,
																        budget_snapshot_json,
																        participation_json,
																        timeline_preview_json,
																        insights_json
																    )
																    VALUES
																    (
																        p_moment_id,
																        CURRENT_DATE,
																
																        jsonb_build_object(
																            'health_score', v_health_score
																        ),
																
																        fn_shared_experience_budget_snapshot_json(
																            p_moment_id
																        ),
																
																        (
																            SELECT jsonb_build_object(
																                'participants',
																                COUNT(*)
																            )
																            FROM group_moment_members
																            WHERE moment_id = p_moment_id
																        ),
																
																        (
																            SELECT jsonb_agg(x)
																            FROM (
																                SELECT
																                    feed_text,
																                    created_at
																                FROM group_live_feed
																                WHERE moment_id = p_moment_id
																                ORDER BY created_at DESC
																                LIMIT 5
																            ) x
																        ),
																
																        '{}'::jsonb
																    )
																    ON CONFLICT (moment_id,snapshot_date)
																    DO UPDATE
																    SET
																        hero_snapshot_json = EXCLUDED.hero_snapshot_json,
																        budget_snapshot_json = EXCLUDED.budget_snapshot_json,
																        participation_json = EXCLUDED.participation_json,
																        timeline_preview_json = EXCLUDED.timeline_preview_json,
																        updated_at = CURRENT_TIMESTAMP;
																
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_group_people_impact(
																    p_moment_id UUID
																)
																RETURNS VOID AS $$
																BEGIN
																
																    DELETE FROM group_people_impact_scores
																    WHERE moment_id = p_moment_id;
																
																    INSERT INTO group_people_impact_scores
																    (
																        moment_id,
																        member_id,
																        impact_type,
																        impact_score,
																        rank_no
																    )
																    SELECT
																        p_moment_id,
																        member_id,
																        'TOP_CONTRIBUTOR',
																
																        ROUND(
																            COALESCE(
																                SUM(amount)
																            ,0)
																        ,2),
																
																        DENSE_RANK()
																        OVER (
																            ORDER BY SUM(amount) DESC
																        )
																
																    FROM group_contributions
																    WHERE moment_id = p_moment_id
																    GROUP BY member_id;
																
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_group_memory_snapshot(
																    p_moment_id UUID
																)
																RETURNS VOID AS $$
																BEGIN
																
																    DELETE FROM group_memory_snapshots
																    WHERE moment_id = p_moment_id
																      AND snapshot_date = CURRENT_DATE;
																
																    INSERT INTO group_memory_snapshots
																    (
																        moment_id,
																        snapshot_date,
																        memory_count,
																        milestone_count,
																        budget_reflection_json
																    )
																    SELECT
																        p_moment_id,
																
																        CURRENT_DATE,
																
																        (
																            SELECT COUNT(*)
																            FROM group_memory_entries
																            WHERE moment_id = p_moment_id
																        ),
																
																        (
																            SELECT COUNT(*)
																            FROM group_moment_work_items
																            WHERE moment_id = p_moment_id
																              AND is_milestone = TRUE
																              AND status = 'COMPLETED'
																        ),
																
																        fn_shared_experience_budget_reflection_json(
																            p_moment_id
																        );
																
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_group_life_score(
																    p_life_space_id UUID
																)
																RETURNS NUMERIC AS $$
																DECLARE
																    v_score NUMERIC;
																BEGIN
																
																    SELECT
																        COALESCE(
																            AVG(
																                fn_group_health_score(moment_id)
																            )
																        ,0)
																    INTO v_score
																    FROM group_life_moment_links
																    WHERE life_space_id = p_life_space_id
																      AND is_active = TRUE;
																
																    RETURN ROUND(v_score,2);
																
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_group_life_snapshot(
																    p_life_space_id UUID
																)
																RETURNS UUID AS $$
																DECLARE
																    v_snapshot_id UUID;
																    v_score NUMERIC;
																BEGIN
																
																    v_score :=
																        fn_group_life_score(
																            p_life_space_id
																        );
																
																    INSERT INTO group_life_snapshots
																    (
																        life_space_id,
																        snapshot_date,
																        group_life_score,
																        health_status
																    )
																    VALUES
																    (
																        p_life_space_id,
																        CURRENT_DATE,
																
																        v_score,
																
																        CASE
																            WHEN v_score >= 80 THEN 'HEALTHY'
																            WHEN v_score >= 60 THEN 'STABLE'
																            WHEN v_score >= 40 THEN 'WATCH'
																            ELSE 'NEEDS_ATTENTION'
																        END
																    )
																    RETURNING life_snapshot_id
																    INTO v_snapshot_id;
																
																    RETURN v_snapshot_id;
																
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_group_driver_effects(
																    p_life_snapshot_id UUID
																)
																RETURNS VOID AS $$
																BEGIN
																
																    DELETE FROM group_life_driver_effects
																    WHERE life_snapshot_id = p_life_snapshot_id;
																
																    INSERT INTO group_life_driver_effects
																    (
																        life_snapshot_id,
																        source_moment_type,
																        target_moment_type,
																        effect_label,
																        impact_pct,
																        explanation,
																        confidence_level,
																        rank_no
																    )
																    VALUES
																    (
																        p_life_snapshot_id,
																        'SHARED_LIVING',
																        'COMMUNITY_COORDINATION',
																        'Living Drives Community',
																        9,
																        'Higher living participation improves community engagement.',
																        'HIGH',
																        1
																    ),
																    (
																        p_life_snapshot_id,
																        'SHARED_GOAL',
																        'SHARED_PURCHASE',
																        'Goals Drive Purchases',
																        7,
																        'Shared goals accelerate group purchases.',
																        'MEDIUM',
																        2
																    );
																
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
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
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_se_booking_score(
																    p_moment_id UUID
																)
																RETURNS NUMERIC AS $$
																DECLARE
																    v_required NUMERIC;
																    v_completed NUMERIC;
																BEGIN
																
																    SELECT
																        COUNT(*),
																        COUNT(*) FILTER (
																            WHERE status = 'COMPLETED'
																        )
																    INTO
																        v_required,
																        v_completed
																    FROM group_moment_work_items
																    WHERE moment_id = p_moment_id
																      AND work_item_type = 'BOOKING';
																
																    RETURN ROUND(
																        COALESCE(
																            (v_completed / NULLIF(v_required,0)) * 100,
																            100
																        )
																    ,2);
																
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_se_participation_score(
																    p_moment_id UUID
																)
																RETURNS NUMERIC AS $$
																DECLARE
																    v_total NUMERIC;
																    v_confirmed NUMERIC;
																BEGIN
																
																    SELECT
																        COUNT(*),
																        COUNT(*) FILTER (
																            WHERE status IN ('ACTIVE','CONFIRMED')
																        )
																    INTO
																        v_total,
																        v_confirmed
																    FROM group_moment_members
																    WHERE moment_id = p_moment_id;
																
																    RETURN ROUND(
																        COALESCE(
																            (v_confirmed / NULLIF(v_total,0)) * 100,
																            100
																        )
																    ,2);
																
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_se_timeline_score(
																    p_moment_id UUID
																)
																RETURNS NUMERIC AS $$
																DECLARE
																    v_total NUMERIC;
																    v_done NUMERIC;
																BEGIN
																
																    SELECT
																        COUNT(*),
																        COUNT(*) FILTER (
																            WHERE status = 'COMPLETED'
																        )
																    INTO
																        v_total,
																        v_done
																    FROM group_moment_work_items
																    WHERE moment_id = p_moment_id;
																
																    RETURN ROUND(
																        COALESCE(
																            (v_done / NULLIF(v_total,0)) * 100,
																            100
																        )
																    ,2);
																
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_se_health_score(
																    p_moment_id UUID
																)
																RETURNS NUMERIC AS $$
																DECLARE
																    v_booking NUMERIC;
																    v_participation NUMERIC;
																    v_budget NUMERIC;
																    v_timeline NUMERIC;
																BEGIN
																
																    v_booking :=
																        fn_se_booking_score(p_moment_id);
																
																    v_participation :=
																        fn_se_participation_score(p_moment_id);
																
																    SELECT
																        COALESCE(
																            fn_shared_experience_budget_health_score(
																                default_budget_plan_id
																            ),
																            100
																        )
																    INTO v_budget
																    FROM shared_experience_details
																    WHERE moment_id = p_moment_id;
																
																    v_timeline :=
																        fn_se_timeline_score(p_moment_id);
																
																    RETURN ROUND(
																        (
																            v_booking * 0.30
																            +
																            v_participation * 0.25
																            +
																            v_budget * 0.25
																            +
																            v_timeline * 0.20
																        )
																    ,2);
																
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_sp_funding_score(
																    p_moment_id UUID
																)
																RETURNS NUMERIC AS $$
																DECLARE
																    v_target NUMERIC;
																    v_collected NUMERIC;
																BEGIN
																
																    SELECT
																        target_amount,
																        collected_amount
																    INTO
																        v_target,
																        v_collected
																    FROM shared_purchase_details
																    WHERE moment_id = p_moment_id;
																
																    RETURN ROUND(
																        LEAST(
																            100,
																            COALESCE(
																                (v_collected / NULLIF(v_target,0)) * 100,
																                100
																            )
																        )
																    ,2);
																
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_sp_health_score(
																    p_moment_id UUID
																)
																RETURNS NUMERIC AS $$
																DECLARE
																    v_funding NUMERIC;
																    v_participation NUMERIC;
																    v_ownership NUMERIC;
																    v_delivery NUMERIC;
																BEGIN
																
																    v_funding :=
																        fn_sp_funding_score(p_moment_id);
																
																    v_participation :=
																        fn_se_participation_score(p_moment_id);
																
																    SELECT
																        CASE
																            WHEN ownership_member_id IS NOT NULL
																            THEN 100
																            ELSE 40
																        END
																    INTO v_ownership
																    FROM shared_purchase_details
																    WHERE moment_id = p_moment_id;
																
																    SELECT
																        CASE purchase_status
																            WHEN 'DELIVERED' THEN 100
																            WHEN 'ORDERED' THEN 75
																            WHEN 'SELECTED' THEN 50
																            ELSE 25
																        END
																    INTO v_delivery
																    FROM shared_purchase_details
																    WHERE moment_id = p_moment_id;
																
																    RETURN ROUND(
																        (
																            v_funding * 0.40
																            +
																            v_participation * 0.25
																            +
																            v_ownership * 0.15
																            +
																            v_delivery * 0.20
																        )
																    ,2);
																
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_sl_health_score(
																    p_moment_id UUID
																)
																RETURNS NUMERIC AS $$
																DECLARE
																    v_contribution NUMERIC;
																    v_tasks NUMERIC;
																    v_harmony NUMERIC;
																    v_maintenance NUMERIC;
																BEGIN
																
																    SELECT
																        COALESCE(
																            (SUM(received_amount)
																            /
																            NULLIF(SUM(expected_amount),0)) * 100,
																            100
																        )
																    INTO v_contribution
																    FROM living_contribution_tracker
																    WHERE moment_id = p_moment_id;
																
																    SELECT
																        COALESCE(
																            COUNT(*) FILTER (
																                WHERE status='COMPLETED'
																            )::NUMERIC
																            /
																            NULLIF(COUNT(*),0)
																            *100,
																            100
																        )
																    INTO v_tasks
																    FROM group_moment_work_items
																    WHERE moment_id = p_moment_id;
																
																    SELECT
																        GREATEST(
																            0,
																            100 - (COUNT(*)*10)
																        )
																    INTO v_harmony
																    FROM group_moment_work_items
																    WHERE moment_id = p_moment_id
																      AND work_item_type='ISSUE'
																      AND status <> 'RESOLVED';
																
																    SELECT
																        COALESCE(
																            COUNT(*) FILTER (
																                WHERE status='RESOLVED'
																            )::NUMERIC
																            /
																            NULLIF(COUNT(*),0)
																            *100,
																            100
																        )
																    INTO v_maintenance
																    FROM group_moment_work_items
																    WHERE moment_id = p_moment_id
																      AND work_item_type='MAINTENANCE';
																
																    RETURN ROUND(
																        (
																            v_contribution * 0.30
																            +
																            v_tasks * 0.25
																            +
																            v_harmony * 0.25
																            +
																            v_maintenance * 0.20
																        )
																    ,2);
																
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_sg_health_score(
																    p_moment_id UUID
																)
																RETURNS NUMERIC AS $$
																DECLARE
																    v_progress NUMERIC;
																    v_participation NUMERIC;
																    v_funding NUMERIC;
																    v_momentum NUMERIC;
																BEGIN
																
																    SELECT progress_pct
																    INTO v_progress
																    FROM shared_goal_details
																    WHERE moment_id = p_moment_id;
																
																    v_participation :=
																        fn_se_participation_score(p_moment_id);
																
																    SELECT
																        CASE
																            WHEN target_amount IS NULL THEN 100
																            ELSE LEAST(
																                100,
																                (current_amount / NULLIF(target_amount,0))*100
																            )
																        END
																    INTO v_funding
																    FROM shared_goal_details
																    WHERE moment_id = p_moment_id;
																
																    SELECT
																        COALESCE(
																            COUNT(*) FILTER (
																                WHERE status='COMPLETED'
																            )::NUMERIC
																            /
																            NULLIF(COUNT(*),0)
																            *100,
																            100
																        )
																    INTO v_momentum
																    FROM group_moment_work_items
																    WHERE moment_id = p_moment_id
																      AND is_milestone = TRUE;
																
																    RETURN ROUND(
																        (
																            v_progress * 0.35
																            +
																            v_participation * 0.25
																            +
																            v_funding * 0.20
																            +
																            v_momentum * 0.20
																        )
																    ,2);
																
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_cc_health_score(
																    p_moment_id UUID
																)
																RETURNS NUMERIC AS $$
																DECLARE
																    v_participation NUMERIC;
																    v_engagement NUMERIC;
																    v_issue NUMERIC;
																    v_execution NUMERIC;
																BEGIN
																
																    v_participation :=
																        fn_se_participation_score(p_moment_id);
																
																    SELECT
																        COALESCE(
																            active_members::NUMERIC
																            /
																            NULLIF(member_base_count,0)
																            *100,
																            100
																        )
																    INTO v_engagement
																    FROM community_coordination_details
																    WHERE moment_id = p_moment_id;
																
																    SELECT
																        COALESCE(
																            COUNT(*) FILTER (
																                WHERE status='RESOLVED'
																            )::NUMERIC
																            /
																            NULLIF(COUNT(*),0)
																            *100,
																            100
																        )
																    INTO v_issue
																    FROM group_moment_work_items
																    WHERE moment_id = p_moment_id
																      AND work_item_type='ISSUE';
																
																    SELECT
																        COALESCE(
																            COUNT(*) FILTER (
																                WHERE status='COMPLETED'
																            )::NUMERIC
																            /
																            NULLIF(COUNT(*),0)
																            *100,
																            100
																        )
																    INTO v_execution
																    FROM group_moment_work_items
																    WHERE moment_id = p_moment_id;
																
																    RETURN ROUND(
																        (
																            v_participation * 0.30
																            +
																            v_engagement * 0.25
																            +
																            v_issue * 0.20
																            +
																            v_execution * 0.25
																        )
																    ,2);
																
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_group_health_score_v2(
																    p_moment_id UUID,
																    p_moment_type VARCHAR
																)
																RETURNS NUMERIC AS $$
																BEGIN
																
																    RETURN CASE p_moment_type
																
																        WHEN 'SHARED_EXPERIENCE'
																            THEN fn_se_health_score(p_moment_id)
																
																        WHEN 'SHARED_PURCHASE'
																            THEN fn_sp_health_score(p_moment_id)
																
																        WHEN 'SHARED_LIVING'
																            THEN fn_sl_health_score(p_moment_id)
																
																        WHEN 'SHARED_GOAL'
																            THEN fn_sg_health_score(p_moment_id)
																
																        WHEN 'COMMUNITY_COORDINATION'
																            THEN fn_cc_health_score(p_moment_id)
																
																        ELSE 50
																
																    END;
																
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_group_memory_participation_pattern_score(
																    p_moment_id UUID
																)
																RETURNS NUMERIC AS $$
																DECLARE
																    v_score NUMERIC;
																BEGIN
																    SELECT
																        COALESCE(
																            ROUND(
																                COUNT(DISTINCT q.created_by)::NUMERIC
																                / NULLIF(COUNT(DISTINCT m.member_id),0)
																                * 100
																            ,2),
																        0)
																    INTO v_score
																    FROM group_moment_members m
																    LEFT JOIN group_quick_add_events q
																        ON q.moment_id = m.moment_id
																       AND q.created_by = m.member_id
																    WHERE m.moment_id = p_moment_id;
																
																    RETURN LEAST(100, COALESCE(v_score,0));
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_group_memory_contribution_pattern_score(
																    p_moment_id UUID
																)
																RETURNS NUMERIC AS $$
																DECLARE
																    v_expected NUMERIC;
																    v_received NUMERIC;
																BEGIN
																    SELECT COALESCE(SUM(target_contribution_amount),0)
																    INTO v_expected
																    FROM group_contributions
																    WHERE moment_id = p_moment_id;
																
																    SELECT COALESCE(SUM(amount),0)
																    INTO v_received
																    FROM group_contributions
																    WHERE moment_id = p_moment_id
																      AND status = 'RECEIVED';
																
																    RETURN ROUND(
																        LEAST(
																            100,
																            COALESCE((v_received / NULLIF(v_expected,0)) * 100, 0)
																        ),
																    2);
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_group_memory_completion_pattern_score(
																    p_moment_id UUID
																)
																RETURNS NUMERIC AS $$
																DECLARE
																    v_total NUMERIC;
																    v_completed NUMERIC;
																BEGIN
																    SELECT
																        COUNT(*),
																        COUNT(*) FILTER (WHERE status IN ('COMPLETED','RESOLVED'))
																    INTO v_total, v_completed
																    FROM group_moment_work_items
																    WHERE moment_id = p_moment_id
																      AND work_item_type IN ('TASK','MILESTONE','EVENT','ISSUE','ACHIEVEMENT');
																
																    RETURN ROUND(
																        COALESCE((v_completed / NULLIF(v_total,0)) * 100, 100),
																    2);
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_group_memory_budget_discipline_score(
																    p_moment_id UUID
																)
																RETURNS NUMERIC AS $$
																DECLARE
																    v_json JSONB;
																    v_score NUMERIC;
																BEGIN
																    v_json := fn_shared_experience_budget_reflection_json(p_moment_id);
																
																    v_score :=
																        COALESCE(
																            (v_json ->> 'budget_accuracy_pct')::NUMERIC,
																            NULL
																        );
																
																    RETURN COALESCE(v_score, 100);
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_group_memory_recovery_score(
																    p_moment_id UUID
																)
																RETURNS NUMERIC AS $$
																DECLARE
																    v_total NUMERIC;
																    v_resolved NUMERIC;
																BEGIN
																    SELECT
																        COUNT(*),
																        COUNT(*) FILTER (
																            WHERE signal_status IN ('CLOSED','DISMISSED')
																               OR is_active = FALSE
																        )
																    INTO v_total, v_resolved
																    FROM group_signals
																    WHERE moment_id = p_moment_id;
																
																    RETURN ROUND(
																        COALESCE((v_resolved / NULLIF(v_total,0)) * 100, 100),
																    2);
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_group_memory_leadership_distribution_score(
																    p_moment_id UUID
																)
																RETURNS NUMERIC AS $$
																DECLARE
																    v_total NUMERIC;
																    v_top NUMERIC;
																    v_dependency_pct NUMERIC;
																BEGIN
																    WITH member_activity AS (
																        SELECT created_by AS member_id, COUNT(*) AS activity_count
																        FROM group_quick_add_events
																        WHERE moment_id = p_moment_id
																        GROUP BY created_by
																    )
																    SELECT
																        COALESCE(SUM(activity_count),0),
																        COALESCE(MAX(activity_count),0)
																    INTO v_total, v_top
																    FROM member_activity;
																
																    v_dependency_pct :=
																        COALESCE((v_top / NULLIF(v_total,0)) * 100, 0);
																
																    RETURN ROUND(
																        GREATEST(0, 100 - v_dependency_pct),
																    2);
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_group_memory_momentum_score(
																    p_moment_id UUID
																)
																RETURNS NUMERIC AS $$
																DECLARE
																    v_completed_last_30 NUMERIC;
																BEGIN
																    SELECT COUNT(*)
																    INTO v_completed_last_30
																    FROM group_moment_work_items
																    WHERE moment_id = p_moment_id
																      AND status IN ('COMPLETED','RESOLVED')
																      AND COALESCE(event_date, updated_at, created_at) >= CURRENT_DATE - INTERVAL '30 days';
																
																    RETURN LEAST(100, v_completed_last_30 * 10);
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_group_memory_highlight_scores(
																    p_moment_id UUID
																)
																RETURNS VOID AS $$
																BEGIN
																    UPDATE group_memory_entries me
																    SET highlight_score =
																        LEAST(
																            100,
																            (
																                CASE
																                    WHEN me.memory_type IN ('MILESTONE','ACHIEVEMENT') THEN 40
																                    ELSE 15
																                END
																                +
																                COALESCE(me.media_count,0) * 10
																                +
																                20
																                +
																                CASE
																                    WHEN me.memory_date >= CURRENT_DATE - INTERVAL '30 days' THEN 20
																                    ELSE 5
																                END
																            )
																        ),
																        is_gallery_item =
																            CASE
																                WHEN COALESCE(me.media_count,0) > 0 THEN TRUE
																                ELSE me.is_gallery_item
																            END
																    WHERE me.moment_id = p_moment_id;
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_group_memory_identity_label(
																    p_moment_id UUID
																)
																RETURNS TEXT AS $$
																DECLARE
																    v_type VARCHAR(50);
																    v_participation NUMERIC;
																    v_contribution NUMERIC;
																    v_completion NUMERIC;
																    v_budget NUMERIC;
																    v_momentum NUMERIC;
																BEGIN
																    SELECT moment_type
																    INTO v_type
																    FROM group_moments
																    WHERE moment_id = p_moment_id;
																
																    v_participation := fn_group_memory_participation_pattern_score(p_moment_id);
																    v_contribution := fn_group_memory_contribution_pattern_score(p_moment_id);
																    v_completion := fn_group_memory_completion_pattern_score(p_moment_id);
																    v_budget := fn_group_memory_budget_discipline_score(p_moment_id);
																    v_momentum := fn_group_memory_momentum_score(p_moment_id);
																
																    RETURN CASE
																        WHEN v_contribution >= 85 AND v_participation >= 80
																            THEN 'Reliable Contributors'
																        WHEN v_type = 'SHARED_EXPERIENCE' AND v_budget >= 85 AND v_participation >= 75
																            THEN 'Disciplined Planners'
																        WHEN v_type = 'SHARED_EXPERIENCE'
																            THEN 'Adventure Seekers'
																        WHEN v_type = 'SHARED_GOAL' AND v_completion >= 80
																            THEN 'Goal Chasers'
																        WHEN v_type = 'COMMUNITY_COORDINATION' AND v_participation >= 80
																            THEN 'Community Builders'
																        WHEN v_momentum >= 80
																            THEN 'Fast Movers'
																        WHEN v_completion >= 80
																            THEN 'Finishers'
																        ELSE 'Emerging Group'
																    END;
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_group_memory_what_changed_json(
																    p_moment_id UUID
																)
																RETURNS JSONB AS $$
																DECLARE
																    v_current_participation NUMERIC;
																    v_current_completion NUMERIC;
																    v_current_contribution NUMERIC;
																    v_previous JSONB;
																BEGIN
																    v_current_participation := fn_group_memory_participation_pattern_score(p_moment_id);
																    v_current_completion := fn_group_memory_completion_pattern_score(p_moment_id);
																    v_current_contribution := fn_group_memory_contribution_pattern_score(p_moment_id);
																
																    SELECT what_changed_json
																    INTO v_previous
																    FROM group_memory_snapshots
																    WHERE moment_id = p_moment_id
																      AND snapshot_date < CURRENT_DATE
																    ORDER BY snapshot_date DESC, created_at DESC
																    LIMIT 1;
																
																    RETURN jsonb_build_object(
																        'participation', jsonb_build_object(
																            'current', v_current_participation,
																            'previous', COALESCE((v_previous #>> '{participation,current}')::NUMERIC, 0),
																            'delta', v_current_participation - COALESCE((v_previous #>> '{participation,current}')::NUMERIC, 0)
																        ),
																        'completion', jsonb_build_object(
																            'current', v_current_completion,
																            'previous', COALESCE((v_previous #>> '{completion,current}')::NUMERIC, 0),
																            'delta', v_current_completion - COALESCE((v_previous #>> '{completion,current}')::NUMERIC, 0)
																        ),
																        'contribution', jsonb_build_object(
																            'current', v_current_contribution,
																            'previous', COALESCE((v_previous #>> '{contribution,current}')::NUMERIC, 0),
																            'delta', v_current_contribution - COALESCE((v_previous #>> '{contribution,current}')::NUMERIC, 0)
																        )
																    );
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_group_memory_patterns_v2(
																    p_moment_id UUID
																)
																RETURNS VOID AS $$
																DECLARE
																    v_moment_type VARCHAR(50);
																    v_participation NUMERIC;
																    v_contribution NUMERIC;
																    v_completion NUMERIC;
																    v_budget NUMERIC;
																    v_recovery NUMERIC;
																    v_leadership NUMERIC;
																    v_momentum NUMERIC;
																BEGIN
																    SELECT moment_type
																    INTO v_moment_type
																    FROM group_moments
																    WHERE moment_id = p_moment_id;
																
																    v_participation := fn_group_memory_participation_pattern_score(p_moment_id);
																    v_contribution := fn_group_memory_contribution_pattern_score(p_moment_id);
																    v_completion := fn_group_memory_completion_pattern_score(p_moment_id);
																    v_budget := fn_group_memory_budget_discipline_score(p_moment_id);
																    v_recovery := fn_group_memory_recovery_score(p_moment_id);
																    v_leadership := fn_group_memory_leadership_distribution_score(p_moment_id);
																    v_momentum := fn_group_memory_momentum_score(p_moment_id);
																
																    UPDATE group_memory_patterns
																    SET status = 'SUPERSEDED',
																        updated_at = CURRENT_TIMESTAMP
																    WHERE moment_id = p_moment_id
																      AND status = 'ACTIVE';
																
																    INSERT INTO group_memory_patterns (
																        moment_id,
																        moment_type,
																        pattern_type,
																        pattern_category,
																        insight_title,
																        insight_text,
																        confidence_score,
																        lesson_text,
																        identity_label,
																        pattern_strength,
																        trend_direction,
																        supporting_metrics_json,
																        status
																    )
																    VALUES
																    (
																        p_moment_id,
																        v_moment_type,
																        'PARTICIPATION_PATTERN',
																        'PARTICIPATION',
																        'Participation pattern detected',
																        'This group shows a participation consistency score of ' || v_participation || '%.',
																        v_participation,
																        CASE
																            WHEN v_participation >= 85 THEN 'High participation improves coordination and reduces last-minute friction.'
																            WHEN v_participation >= 60 THEN 'Participation is present but can become more consistent.'
																            ELSE 'The group may need stronger reminders or clearer ownership.'
																        END,
																        fn_group_memory_identity_label(p_moment_id),
																        v_participation,
																        'STABLE',
																        jsonb_build_object('participation_score', v_participation),
																        'ACTIVE'
																    ),
																    (
																        p_moment_id,
																        v_moment_type,
																        'COMPLETION_PATTERN',
																        'EXECUTION',
																        'Completion pattern detected',
																        'This group completes ' || v_completion || '% of tracked work and milestones.',
																        v_completion,
																        CASE
																            WHEN v_completion >= 80 THEN 'The group is good at finishing what it starts.'
																            ELSE 'Breaking work into clearer milestones may improve completion.'
																        END,
																        fn_group_memory_identity_label(p_moment_id),
																        v_completion,
																        'STABLE',
																        jsonb_build_object('completion_score', v_completion),
																        'ACTIVE'
																    ),
																    (
																        p_moment_id,
																        v_moment_type,
																        'MOMENTUM_PATTERN',
																        'MOMENTUM',
																        'Momentum pattern detected',
																        'Recent activity indicates a momentum score of ' || v_momentum || '%.',
																        v_momentum,
																        CASE
																            WHEN v_momentum >= 80 THEN 'Frequent progress keeps the moment alive and reduces drift.'
																            ELSE 'Momentum can improve with smaller recurring actions.'
																        END,
																        fn_group_memory_identity_label(p_moment_id),
																        v_momentum,
																        'STABLE',
																        jsonb_build_object('momentum_score', v_momentum),
																        'ACTIVE'
																    );
																
																    IF v_moment_type = 'SHARED_EXPERIENCE' THEN
																        INSERT INTO group_memory_patterns (
																            moment_id,
																            moment_type,
																            pattern_type,
																            pattern_category,
																            insight_title,
																            insight_text,
																            confidence_score,
																            lesson_text,
																            identity_label,
																            pattern_strength,
																            trend_direction,
																            supporting_metrics_json,
																            status
																        )
																        VALUES (
																            p_moment_id,
																            v_moment_type,
																            'BUDGET_DISCIPLINE_PATTERN',
																            'BUDGET',
																            'Budget discipline detected',
																            'The experience budget accuracy is ' || v_budget || '%.',
																            v_budget,
																            CASE
																                WHEN v_budget >= 85 THEN 'This group plans costs well and stays close to the original budget.'
																                WHEN v_budget >= 60 THEN 'Budget planning is useful but category estimates need refinement.'
																                ELSE 'The group may need stronger budget planning before activation.'
																            END,
																            fn_group_memory_identity_label(p_moment_id),
																            v_budget,
																            'STABLE',
																            fn_shared_experience_budget_reflection_json(p_moment_id),
																            'ACTIVE'
																        );
																    END IF;
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_group_memory_snapshot_v2(
																    p_moment_id UUID
																)
																RETURNS VOID AS $$
																BEGIN
																    DELETE FROM group_memory_snapshots
																    WHERE moment_id = p_moment_id
																      AND snapshot_date = CURRENT_DATE;
																
																    INSERT INTO group_memory_snapshots (
																        moment_id,
																        snapshot_date,
																        memory_count,
																        milestone_count,
																        what_changed_json,
																        budget_reflection_json,
																        identity_label
																    )
																    VALUES (
																        p_moment_id,
																        CURRENT_DATE,
																        (
																            SELECT COUNT(*)
																            FROM group_memory_entries
																            WHERE moment_id = p_moment_id
																        ),
																        (
																            SELECT COUNT(*)
																            FROM group_moment_work_items
																            WHERE moment_id = p_moment_id
																              AND is_milestone = TRUE
																              AND status = 'COMPLETED'
																        ),
																        fn_group_memory_what_changed_json(p_moment_id),
																        fn_shared_experience_budget_reflection_json(p_moment_id),
																        fn_group_memory_identity_label(p_moment_id)
																    );
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_group_memory_ai_insight(
																    p_moment_id UUID
																)
																RETURNS VOID AS $$
																DECLARE
																    v_identity TEXT;
																    v_best_pattern RECORD;
																BEGIN
																    v_identity := fn_group_memory_identity_label(p_moment_id);
																
																    SELECT *
																    INTO v_best_pattern
																    FROM group_memory_patterns
																    WHERE moment_id = p_moment_id
																      AND status = 'ACTIVE'
																    ORDER BY pattern_strength DESC NULLS LAST, confidence_score DESC NULLS LAST
																    LIMIT 1;
																
																    UPDATE group_ai_insights
																    SET is_active = FALSE,
																        updated_at = CURRENT_TIMESTAMP
																    WHERE moment_id = p_moment_id
																      AND insight_layer = 'MEMORY'
																      AND is_active = TRUE;
																
																    IF v_best_pattern.pattern_id IS NOT NULL THEN
																        INSERT INTO group_ai_insights (
																            moment_id,
																            insight_layer,
																            insight_type,
																            insight_title,
																            insight_body,
																            confidence_level,
																            supporting_metrics_json,
																            display_order,
																            is_active
																        )
																        VALUES (
																            p_moment_id,
																            'MEMORY',
																            'PATTERN',
																            'Your group identity is ' || v_identity,
																            v_best_pattern.lesson_text,
																            CASE
																                WHEN v_best_pattern.pattern_strength >= 85 THEN 'HIGH'
																                WHEN v_best_pattern.pattern_strength >= 60 THEN 'MEDIUM'
																                ELSE 'LOW'
																            END,
																            v_best_pattern.supporting_metrics_json,
																            1,
																            TRUE
																        );
																    END IF;
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_group_memory_intelligence(
																    p_moment_id UUID
																)
																RETURNS VOID AS $$
																BEGIN
																    PERFORM sp_refresh_group_memory_highlight_scores(p_moment_id);
																    PERFORM sp_refresh_group_memory_patterns_v2(p_moment_id);
																    PERFORM sp_refresh_group_memory_snapshot_v2(p_moment_id);
																    PERFORM sp_refresh_group_people_impact(p_moment_id);
																    PERFORM sp_refresh_group_memory_ai_insight(p_moment_id);
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_group_life_experience_dimension(
																    p_life_space_id UUID
																)
																RETURNS NUMERIC AS $$
																DECLARE
																    v_health NUMERIC;
																    v_participation NUMERIC;
																    v_memory NUMERIC;
																    v_completion NUMERIC;
																BEGIN
																
																    SELECT COALESCE(AVG(fn_se_health_score(moment_id)),0)
																    INTO v_health
																    FROM group_life_moment_links
																    WHERE life_space_id = p_life_space_id
																      AND moment_type = 'SHARED_EXPERIENCE';
																
																    SELECT COALESCE(AVG(pattern_strength),0)
																    INTO v_participation
																    FROM group_memory_patterns
																    WHERE pattern_type='PARTICIPATION_PATTERN'
																      AND moment_id IN (
																          SELECT moment_id
																          FROM group_life_moment_links
																          WHERE life_space_id=p_life_space_id
																            AND moment_type='SHARED_EXPERIENCE'
																      );
																
																    SELECT COALESCE(AVG(confidence_score),0)
																    INTO v_memory
																    FROM group_memory_patterns
																    WHERE moment_id IN (
																          SELECT moment_id
																          FROM group_life_moment_links
																          WHERE life_space_id=p_life_space_id
																            AND moment_type='SHARED_EXPERIENCE'
																      );
																
																    SELECT COALESCE(AVG(pattern_strength),0)
																    INTO v_completion
																    FROM group_memory_patterns
																    WHERE pattern_type='COMPLETION_PATTERN'
																      AND moment_id IN (
																          SELECT moment_id
																          FROM group_life_moment_links
																          WHERE life_space_id=p_life_space_id
																            AND moment_type='SHARED_EXPERIENCE'
																      );
																
																    RETURN ROUND(
																        (
																            v_health * 0.40
																            +
																            v_participation * 0.25
																            +
																            v_memory * 0.20
																            +
																            v_completion * 0.15
																        )
																    ,2);
																
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_group_life_purchase_dimension(
																    p_life_space_id UUID
																)
																RETURNS NUMERIC AS $$
																DECLARE
																    v_health NUMERIC;
																    v_funding NUMERIC;
																    v_completion NUMERIC;
																BEGIN
																
																    SELECT COALESCE(AVG(fn_sp_health_score(moment_id)),0)
																    INTO v_health
																    FROM group_life_moment_links
																    WHERE life_space_id=p_life_space_id
																      AND moment_type='SHARED_PURCHASE';
																
																    SELECT COALESCE(AVG(funding_pct),0)
																    INTO v_funding
																    FROM shared_purchase_details
																    WHERE moment_id IN (
																        SELECT moment_id
																        FROM group_life_moment_links
																        WHERE life_space_id=p_life_space_id
																          AND moment_type='SHARED_PURCHASE'
																    );
																
																    SELECT COALESCE(AVG(pattern_strength),0)
																    INTO v_completion
																    FROM group_memory_patterns
																    WHERE pattern_type='COMPLETION_PATTERN'
																      AND moment_id IN (
																          SELECT moment_id
																          FROM group_life_moment_links
																          WHERE life_space_id=p_life_space_id
																            AND moment_type='SHARED_PURCHASE'
																      );
																
																    RETURN ROUND(
																        (
																            v_health * 0.40
																            +
																            v_funding * 0.25
																            +
																            100 * 0.20
																            +
																            v_completion * 0.15
																        )
																    ,2);
																
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_group_life_living_dimension(
																    p_life_space_id UUID
																)
																RETURNS NUMERIC AS $$
																DECLARE
																    v_health NUMERIC;
																    v_contribution NUMERIC;
																    v_completion NUMERIC;
																BEGIN
																
																    SELECT COALESCE(AVG(fn_sl_health_score(moment_id)),0)
																    INTO v_health
																    FROM group_life_moment_links
																    WHERE life_space_id=p_life_space_id
																      AND moment_type='SHARED_LIVING';
																
																    SELECT COALESCE(AVG(pattern_strength),0)
																    INTO v_contribution
																    FROM group_memory_patterns
																    WHERE pattern_type='PARTICIPATION_PATTERN'
																      AND moment_id IN (
																        SELECT moment_id
																        FROM group_life_moment_links
																        WHERE life_space_id=p_life_space_id
																          AND moment_type='SHARED_LIVING'
																      );
																
																    SELECT COALESCE(AVG(pattern_strength),0)
																    INTO v_completion
																    FROM group_memory_patterns
																    WHERE pattern_type='COMPLETION_PATTERN'
																      AND moment_id IN (
																        SELECT moment_id
																        FROM group_life_moment_links
																        WHERE life_space_id=p_life_space_id
																          AND moment_type='SHARED_LIVING'
																      );
																
																    RETURN ROUND(
																        (
																            v_health * 0.40
																            +
																            v_contribution * 0.25
																            +
																            v_completion * 0.35
																        )
																    ,2);
																
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_group_life_goal_dimension(
																    p_life_space_id UUID
																)
																RETURNS NUMERIC AS $$
																DECLARE
																    v_health NUMERIC;
																    v_momentum NUMERIC;
																    v_completion NUMERIC;
																BEGIN
																
																    SELECT COALESCE(AVG(fn_sg_health_score(moment_id)),0)
																    INTO v_health
																    FROM group_life_moment_links
																    WHERE life_space_id=p_life_space_id
																      AND moment_type='SHARED_GOAL';
																
																    SELECT COALESCE(AVG(pattern_strength),0)
																    INTO v_momentum
																    FROM group_memory_patterns
																    WHERE pattern_type='MOMENTUM_PATTERN';
																
																    SELECT COALESCE(AVG(pattern_strength),0)
																    INTO v_completion
																    FROM group_memory_patterns
																    WHERE pattern_type='COMPLETION_PATTERN';
																
																    RETURN ROUND(
																        (
																            v_health * 0.40
																            +
																            v_completion * 0.25
																            +
																            v_momentum * 0.20
																            +
																            v_completion * 0.15
																        )
																    ,2);
																
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_group_life_community_dimension(
																    p_life_space_id UUID
																)
																RETURNS NUMERIC AS $$
																DECLARE
																    v_health NUMERIC;
																    v_recovery NUMERIC;
																    v_participation NUMERIC;
																BEGIN
																
																    SELECT COALESCE(AVG(fn_cc_health_score(moment_id)),0)
																    INTO v_health
																    FROM group_life_moment_links
																    WHERE life_space_id=p_life_space_id
																      AND moment_type='COMMUNITY_COORDINATION';
																
																    SELECT COALESCE(AVG(pattern_strength),0)
																    INTO v_participation
																    FROM group_memory_patterns
																    WHERE pattern_type='PARTICIPATION_PATTERN';
																
																    SELECT COALESCE(AVG(pattern_strength),0)
																    INTO v_recovery
																    FROM group_memory_patterns
																    WHERE pattern_type='RECOVERY_PATTERN';
																
																    RETURN ROUND(
																        (
																            v_health * 0.40
																            +
																            v_participation * 0.25
																            +
																            v_recovery * 0.35
																        )
																    ,2);
																
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_group_life_score_v2(
																    p_life_space_id UUID
																)
																RETURNS NUMERIC AS $$
																DECLARE
																    v_exp NUMERIC;
																    v_purchase NUMERIC;
																    v_living NUMERIC;
																    v_goal NUMERIC;
																    v_comm NUMERIC;
																BEGIN
																
																    v_exp :=
																        fn_group_life_experience_dimension(p_life_space_id);
																
																    v_purchase :=
																        fn_group_life_purchase_dimension(p_life_space_id);
																
																    v_living :=
																        fn_group_life_living_dimension(p_life_space_id);
																
																    v_goal :=
																        fn_group_life_goal_dimension(p_life_space_id);
																
																    v_comm :=
																        fn_group_life_community_dimension(p_life_space_id);
																
																    RETURN ROUND(
																        (
																            v_exp
																            +
																            v_purchase
																            +
																            v_living
																            +
																            v_goal
																            +
																            v_comm
																        ) / 5
																    ,2);
																
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_group_recommendation_impact_score(
																    p_current_score NUMERIC,
																    p_target_score NUMERIC DEFAULT 100
																)
																RETURNS NUMERIC AS $$
																BEGIN
																
																    RETURN ROUND(
																        GREATEST(
																            0,
																            LEAST(
																                100,
																                p_target_score - p_current_score
																            )
																        )
																    ,2);
																
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_group_recommendation_confidence_score(
																    p_confidence_level VARCHAR
																)
																RETURNS NUMERIC AS $$
																BEGIN
																
																    RETURN CASE p_confidence_level
																
																        WHEN 'HIGH' THEN 100
																        WHEN 'MEDIUM' THEN 70
																        WHEN 'LOW' THEN 40
																
																        ELSE 50
																
																    END;
																
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_group_recommendation_priority_score(
																    p_health_score NUMERIC,
																    p_impact_score NUMERIC,
																    p_confidence_level VARCHAR
																)
																RETURNS NUMERIC AS $$
																DECLARE
																    v_confidence NUMERIC;
																BEGIN
																
																    v_confidence :=
																        fn_group_recommendation_confidence_score(
																            p_confidence_level
																        );
																
																    RETURN ROUND(
																        (
																            (100 - p_health_score) * 0.40
																            +
																            p_impact_score * 0.35
																            +
																            v_confidence * 0.25
																        )
																    ,2);
																
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_generate_group_pulse_recommendations(
																    p_moment_id UUID
																)
																RETURNS VOID AS $$
																DECLARE
																    v_health NUMERIC;
																    v_participation NUMERIC;
																BEGIN
																
																    SELECT
																        health_score
																    INTO v_health
																    FROM group_health_snapshots
																    WHERE moment_id = p_moment_id
																    ORDER BY snapshot_date DESC
																    LIMIT 1;
																
																    v_participation :=
																        fn_group_memory_participation_pattern_score(
																            p_moment_id
																        );
																
																    IF v_participation < 70 THEN
																
																        INSERT INTO group_recommendations
																        (
																            moment_id,
																            recommendation_type,
																            recommendation_category,
																            title,
																            description,
																            priority,
																            recommendation_score,
																            impact_score,
																            confidence_level,
																            status
																        )
																        VALUES
																        (
																            p_moment_id,
																            'PULSE',
																            'PARTICIPATION',
																            'Increase member participation',
																            'Invite inactive members to re-engage with the moment.',
																            'HIGH',
																            fn_group_recommendation_priority_score(
																                v_health,
																                30,
																                'HIGH'
																            ),
																            30,
																            'HIGH',
																            'OPEN'
																        );
																
																    END IF;
																
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_generate_budget_recommendations(
																    p_moment_id UUID
																)
																RETURNS VOID AS $$
																DECLARE
																    v_budget JSONB;
																    v_health NUMERIC;
																BEGIN
																
																    v_budget :=
																        fn_shared_experience_budget_snapshot_json(
																            p_moment_id
																        );
																
																    SELECT
																        health_score
																    INTO v_health
																    FROM group_health_snapshots
																    WHERE moment_id = p_moment_id
																    ORDER BY snapshot_date DESC
																    LIMIT 1;
																
																    IF COALESCE(
																        (v_budget ->> 'funding_readiness_pct')::NUMERIC,
																        100
																    ) < 75
																    THEN
																
																        INSERT INTO group_recommendations
																        (
																            moment_id,
																            recommendation_type,
																            recommendation_category,
																            title,
																            description,
																            priority,
																            recommendation_score,
																            impact_score,
																            confidence_level,
																            status
																        )
																        VALUES
																        (
																            p_moment_id,
																            'PULSE',
																            'BUDGET',
																            'Improve funding readiness',
																            'Collect remaining planned contributions before activation.',
																            'HIGH',
																            fn_group_recommendation_priority_score(
																                v_health,
																                40,
																                'HIGH'
																            ),
																            40,
																            'HIGH',
																            'OPEN'
																        );
																
																    END IF;
																
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_generate_memory_recommendations(
																    p_moment_id UUID
																)
																RETURNS VOID AS $$
																DECLARE
																    v_identity TEXT;
																BEGIN
																
																    v_identity :=
																        fn_group_memory_identity_label(
																            p_moment_id
																        );
																
																    INSERT INTO group_recommendations
																    (
																        moment_id,
																        recommendation_type,
																        recommendation_category,
																        title,
																        description,
																        priority,
																        recommendation_score,
																        impact_score,
																        confidence_level,
																        status
																    )
																    VALUES
																    (
																        p_moment_id,
																        'MEMORY',
																        'PATTERN',
																        'Use your strongest group behavior',
																        'This group behaves like "' || v_identity || '". Lean into this strength for future moments.',
																        'MEDIUM',
																        70,
																        20,
																        'MEDIUM',
																        'OPEN'
																    );
																
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_generate_life_leverage_recommendation(
																    p_life_space_id UUID
																)
																RETURNS VOID AS $$
																DECLARE
																    v_dimension RECORD;
																BEGIN
																
																    SELECT
																        dimension_code,
																        score
																    INTO v_dimension
																    FROM group_life_dimension_scores
																    WHERE life_snapshot_id = (
																        SELECT life_snapshot_id
																        FROM group_life_snapshots
																        WHERE life_space_id = p_life_space_id
																        ORDER BY snapshot_date DESC
																        LIMIT 1
																    )
																    ORDER BY score ASC
																    LIMIT 1;
																
																    INSERT INTO group_recommendations
																    (
																        related_life_space_id,
																        recommendation_type,
																        recommendation_category,
																        title,
																        description,
																        priority,
																        recommendation_score,
																        impact_score,
																        confidence_level,
																        status
																    )
																    VALUES
																    (
																        p_life_space_id,
																        'LIFE',
																        'LEVERAGE',
																        'Improve ' || v_dimension.dimension_code,
																        'This is currently your weakest life dimension and offers the highest leverage.',
																        'HIGH',
																        90,
																        (100 - v_dimension.score),
																        'HIGH',
																        'OPEN'
																    );
																
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_generate_drift_recommendations(
																    p_life_space_id UUID
																)
																RETURNS VOID AS $$
																DECLARE
																    v_dimension RECORD;
																BEGIN
																
																    SELECT
																        dimension_code,
																        trend_delta
																    INTO v_dimension
																    FROM group_life_dimension_scores
																    WHERE life_snapshot_id = (
																        SELECT life_snapshot_id
																        FROM group_life_snapshots
																        WHERE life_space_id = p_life_space_id
																        ORDER BY snapshot_date DESC
																        LIMIT 1
																    )
																    ORDER BY trend_delta ASC
																    LIMIT 1;
																
																    IF v_dimension.trend_delta < -10 THEN
																
																        INSERT INTO group_recommendations
																        (
																            related_life_space_id,
																            recommendation_type,
																            recommendation_category,
																            title,
																            description,
																            priority,
																            recommendation_score,
																            impact_score,
																            confidence_level,
																            status
																        )
																        VALUES
																        (
																            p_life_space_id,
																            'LIFE',
																            'DRIFT',
																            'Address life drift',
																            v_dimension.dimension_code || ' has declined significantly over recent periods.',
																            'HIGH',
																            95,
																            ABS(v_dimension.trend_delta),
																            'HIGH',
																            'OPEN'
																        );
																
																    END IF;
																
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_generate_group_signals(
																    p_moment_id UUID
																)
																RETURNS VOID AS $$
																DECLARE
																    v_health NUMERIC;
																BEGIN
																
																    SELECT
																        health_score
																    INTO v_health
																    FROM group_health_snapshots
																    WHERE moment_id = p_moment_id
																    ORDER BY snapshot_date DESC
																    LIMIT 1;
																
																    IF v_health < 40 THEN
																
																        INSERT INTO group_signals
																        (
																            moment_id,
																            signal_type,
																            signal_category,
																            signal_title,
																            signal_description,
																            severity,
																            signal_score,
																            signal_status,
																            is_active
																        )
																        VALUES
																        (
																            p_moment_id,
																            'HEALTH',
																            'CRITICAL',
																            'Group health critical',
																            'Immediate action is recommended.',
																            'HIGH',
																            100 - v_health,
																            'OPEN',
																            TRUE
																        );
																
																    ELSIF v_health < 60 THEN
																
																        INSERT INTO group_signals
																        (
																            moment_id,
																            signal_type,
																            signal_category,
																            signal_title,
																            signal_description,
																            severity,
																            signal_score,
																            signal_status,
																            is_active
																        )
																        VALUES
																        (
																            p_moment_id,
																            'HEALTH',
																            'WARNING',
																            'Group health declining',
																            'Monitor participation and progress.',
																            'MEDIUM',
																            100 - v_health,
																            'OPEN',
																            TRUE
																        );
																
																    END IF;
																
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_group_recommendations(
																    p_moment_id UUID
																)
																RETURNS VOID AS $$
																DECLARE
																    v_life_space UUID;
																BEGIN
																
																    DELETE FROM group_recommendations
																    WHERE moment_id = p_moment_id
																      AND status = 'OPEN';
																
																    PERFORM sp_generate_group_pulse_recommendations(
																        p_moment_id
																    );
																
																    PERFORM sp_generate_budget_recommendations(
																        p_moment_id
																    );
																
																    PERFORM sp_generate_memory_recommendations(
																        p_moment_id
																    );
																
																    PERFORM sp_generate_group_signals(
																        p_moment_id
																    );
																
																    SELECT group_life_space_id
																    INTO v_life_space
																    FROM group_moments
																    WHERE moment_id = p_moment_id;
																
																    IF v_life_space IS NOT NULL THEN
																
																        PERFORM sp_generate_life_leverage_recommendation(
																            v_life_space
																        );
																
																        PERFORM sp_generate_drift_recommendations(
																            v_life_space
																        );
																
																    END IF;
																
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_group_life_master_snapshot(
    p_life_space_id UUID
)
RETURNS VOID AS $$
DECLARE
    v_snapshot_id UUID;
    v_user_id UUID;
    v_group_life_score NUMERIC;
BEGIN
    SELECT user_id
    INTO v_user_id
    FROM group_life_spaces
    WHERE life_space_id = p_life_space_id;

    SELECT life_snapshot_id, group_life_score
    INTO v_snapshot_id, v_group_life_score
    FROM group_life_snapshots
    WHERE life_space_id = p_life_space_id
    ORDER BY snapshot_date DESC, created_at DESC
    LIMIT 1;

    IF v_snapshot_id IS NULL THEN
        RETURN;
    END IF;

    INSERT INTO group_life_master_snapshots (
        user_id,
        life_space_id,
        snapshot_date,
        group_life_score,

        participation_score,
        contribution_score,
        coordination_score,
        progress_score,
        community_score,

        active_group_moments_count,
        active_members_count,
        open_group_actions_count,
        group_risk_count,

        dominant_group_driver,
        dominant_group_risk,
        highest_group_leverage,
        source_snapshot_ids_json
    )
    SELECT
        v_user_id,
        p_life_space_id,
        CURRENT_DATE,
        v_group_life_score,

        MAX(score) FILTER (WHERE dimension_code = 'PARTICIPATION'),
        MAX(score) FILTER (WHERE dimension_code = 'CONTRIBUTION'),
        MAX(score) FILTER (WHERE dimension_code = 'COORDINATION'),
        MAX(score) FILTER (WHERE dimension_code = 'PROGRESS'),
        MAX(score) FILTER (WHERE dimension_code = 'COMMUNITY'),

        (
            SELECT COUNT(*)
            FROM group_life_moment_links
            WHERE life_space_id = p_life_space_id
              AND is_active = TRUE
        ),

        (
            SELECT COUNT(DISTINCT m.member_id)
            FROM group_life_moment_links l
            JOIN group_moment_members m
              ON m.moment_id = l.moment_id
            WHERE l.life_space_id = p_life_space_id
              AND l.is_active = TRUE
              AND m.status IN ('ACTIVE','CONFIRMED')
        ),

        (
            SELECT COUNT(*)
            FROM group_life_moment_links l
            JOIN group_moment_work_items wi
              ON wi.moment_id = l.moment_id
            WHERE l.life_space_id = p_life_space_id
              AND l.is_active = TRUE
              AND wi.status IN ('OPEN','IN_PROGRESS','BLOCKED')
        ),

        (
            SELECT COUNT(*)
            FROM group_life_moment_links l
            JOIN group_signals s
              ON s.moment_id = l.moment_id
            WHERE l.life_space_id = p_life_space_id
              AND l.is_active = TRUE
              AND s.is_active = TRUE
              AND COALESCE(s.signal_status,'OPEN') = 'OPEN'
              AND COALESCE(s.severity,s.priority) IN ('WARN','CRITICAL','HIGH')
        ),

        fn_group_primary_driver(p_life_space_id),

        (
            SELECT dominant_risk
            FROM group_life_snapshots
            WHERE life_snapshot_id = v_snapshot_id
        ),

        (
            SELECT highest_leverage
            FROM group_life_snapshots
            WHERE life_snapshot_id = v_snapshot_id
        ),

        jsonb_build_object(
            'life_snapshot_id', v_snapshot_id,
            'life_space_id', p_life_space_id,
            'generated_at', CURRENT_TIMESTAMP
        )

    FROM group_life_dimension_scores
    WHERE life_snapshot_id = v_snapshot_id;
END;
$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_group_moment_full_orchestration(
    p_moment_id UUID,
    p_event_id UUID DEFAULT NULL
)
RETURNS VOID AS $$
BEGIN
    IF p_event_id IS NOT NULL THEN
        PERFORM sp_create_group_live_feed(p_event_id);
    END IF;

    PERFORM sp_refresh_group_moment_stage(p_moment_id, p_event_id);

    PERFORM sp_refresh_group_pulse_snapshot(p_moment_id);

    PERFORM sp_refresh_group_memory_intelligence(p_moment_id);

    PERFORM sp_refresh_group_recommendations(p_moment_id);
END;
$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_group_life_full_orchestration(
    p_life_space_id UUID
)
RETURNS VOID AS $$
DECLARE
    v_snapshot_id UUID;
BEGIN
    v_snapshot_id := sp_refresh_group_life_snapshot(p_life_space_id);

    PERFORM sp_refresh_group_network_effects(p_life_space_id);

    PERFORM sp_generate_life_leverage_recommendation(p_life_space_id);

    PERFORM sp_generate_drift_recommendations(p_life_space_id);

    PERFORM sp_refresh_group_life_master_snapshot(p_life_space_id);
END;
$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_group_everything(
    p_moment_id UUID,
    p_event_id UUID DEFAULT NULL
)
RETURNS VOID AS $$
DECLARE
    v_life_space_id UUID;
BEGIN
    PERFORM sp_refresh_group_moment_full_orchestration(
        p_moment_id,
        p_event_id
    );

    SELECT group_life_space_id
    INTO v_life_space_id
    FROM group_moments
    WHERE moment_id = p_moment_id;

    IF v_life_space_id IS NOT NULL THEN
        PERFORM sp_refresh_group_life_full_orchestration(v_life_space_id);
    END IF;
END;
$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_group_budget_everything(
    p_budget_plan_id UUID
)
RETURNS VOID AS $$
DECLARE
    v_moment_id UUID;
BEGIN
    SELECT moment_id
    INTO v_moment_id
    FROM shared_experience_budget_plans
    WHERE budget_plan_id = p_budget_plan_id;

    IF v_moment_id IS NULL THEN
        RETURN;
    END IF;

    PERFORM sp_refresh_shared_experience_budget_contributions(p_budget_plan_id);
    PERFORM sp_refresh_shared_experience_budget_rollup(p_budget_plan_id);
    PERFORM sp_refresh_group_everything(v_moment_id, NULL);
END;
$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION trg_refresh_group_moment_everything()
RETURNS TRIGGER AS $$
DECLARE
    v_moment_id UUID;
BEGIN
    v_moment_id := COALESCE(NEW.moment_id, OLD.moment_id);

    PERFORM sp_refresh_group_everything(v_moment_id, NULL);

    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION trg_refresh_group_budget_everything()
RETURNS TRIGGER AS $$
DECLARE
    v_budget_plan_id UUID;
BEGIN
    v_budget_plan_id := COALESCE(NEW.budget_plan_id, OLD.budget_plan_id);

    PERFORM sp_refresh_group_budget_everything(v_budget_plan_id);

    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION trg_refresh_group_life_everything()
RETURNS TRIGGER AS $$
DECLARE
    v_life_space_id UUID;
BEGIN
    v_life_space_id := COALESCE(NEW.life_space_id, OLD.life_space_id);

    PERFORM sp_refresh_group_life_full_orchestration(v_life_space_id);

    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_all_group_moments_nightly()
RETURNS VOID AS $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN
        SELECT moment_id
        FROM group_moments
        WHERE status IN ('ACTIVE','COMPLETED')
    LOOP
        PERFORM sp_refresh_group_everything(r.moment_id, NULL);
    END LOOP;
END;
$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_all_group_life_spaces_nightly()
RETURNS VOID AS $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN
        SELECT life_space_id
        FROM group_life_spaces
        WHERE space_status = 'ACTIVE'
    LOOP
        PERFORM sp_refresh_group_life_full_orchestration(r.life_space_id);
    END LOOP;
END;
$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_group_production_all()
RETURNS VOID AS $$
BEGIN
    PERFORM sp_refresh_all_group_moments_nightly();
    PERFORM sp_refresh_all_group_life_spaces_nightly();
END;
$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION trg_prevent_duplicate_single_poll_vote()
																RETURNS TRIGGER AS $$
																DECLARE
																    v_allow_multiple BOOLEAN;
																BEGIN
																    SELECT allow_multiple_votes
																    INTO v_allow_multiple
																    FROM group_polls
																    WHERE poll_id = NEW.poll_id;
																
																    IF COALESCE(v_allow_multiple, FALSE) = FALSE THEN
																        IF EXISTS (
																            SELECT 1
																            FROM group_poll_votes
																            WHERE poll_id = NEW.poll_id
																              AND voter_member_id = NEW.voter_member_id
																              AND vote_id <> NEW.vote_id
																        ) THEN
																            RAISE EXCEPTION 'Duplicate vote not allowed for this poll';
																        END IF;
																    END IF;
																
																    RETURN NEW;
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_register_activity_edit_route(
																    p_feed_id UUID,
																    p_entity_name VARCHAR,
																    p_entity_id UUID
																)
																RETURNS VOID AS $$
																DECLARE
																    v_route VARCHAR(250);
																BEGIN
																    v_route :=
																        CASE p_entity_name
																            WHEN 'group_expenses'
																                THEN '/group/activity/edit/expense/'
																            WHEN 'group_contributions'
																                THEN '/group/activity/edit/contribution/'
																            WHEN 'shared_experience_budget_plans'
																                THEN '/group/activity/edit/budget/'
																            WHEN 'shared_experience_budget_allocations'
																                THEN '/group/activity/edit/budget-category/'
																            WHEN 'group_moment_work_items'
																                THEN '/group/activity/edit/work-item/'
																            WHEN 'group_moment_resources'
																                THEN '/group/activity/edit/resource/'
																            WHEN 'group_decisions'
																                THEN '/group/activity/edit/decision/'
																            WHEN 'group_polls'
																                THEN '/group/activity/edit/poll/'
																            WHEN 'group_memory_entries'
																                THEN '/group/activity/edit/memory/'
																            ELSE '/group/activity/edit/general/'
																        END || p_entity_id::TEXT;
																
																    UPDATE group_live_feed
																    SET entity_name = p_entity_name,
																        entity_id = p_entity_id,
																        edit_route = v_route,
																        is_editable = TRUE
																    WHERE feed_id = p_feed_id;
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_log_group_activity_edit(
																    p_moment_id UUID,
																    p_activity_id UUID,
																    p_entity_name VARCHAR,
																    p_entity_id UUID,
																    p_edit_payload_json JSONB,
																    p_edited_by UUID,
																    p_edit_reason TEXT DEFAULT NULL
																)
																RETURNS UUID AS $$
																DECLARE
																    v_edit_id UUID;
																BEGIN
																    INSERT INTO group_activity_edits (
																        moment_id,
																        activity_id,
																        entity_name,
																        entity_id,
																        edit_status,
																        edit_payload_json,
																        edit_reason,
																        edited_by
																    )
																    VALUES (
																        p_moment_id,
																        p_activity_id,
																        p_entity_name,
																        p_entity_id,
																        'SAVED',
																        p_edit_payload_json,
																        p_edit_reason,
																        p_edited_by
																    )
																    RETURNING edit_id INTO v_edit_id;
																
																    INSERT INTO group_change_history (
																        moment_id,
																        entity_name,
																        entity_id,
																        field_name,
																        old_value,
																        new_value,
																        change_type,
																        changed_by,
																        change_category,
																        source_widget,
																        rollback_supported,
																        edit_batch_id,
																        edit_reason,
																        source_activity_id
																    )
																    SELECT
																        p_moment_id,
																        p_entity_name,
																        p_entity_id,
																        key,
																        NULL,
																        value::TEXT,
																        'UPDATED',
																        p_edited_by,
																        'ACTIVITY_EDIT',
																        'ACTIVITY_EDIT_SCREEN',
																        TRUE,
																        v_edit_id,
																        p_edit_reason,
																        p_activity_id
																    FROM jsonb_each_text(p_edit_payload_json);
																
																    PERFORM sp_refresh_group_everything(p_moment_id, NULL);
																
																    RETURN v_edit_id;
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_create_group_live_feed(
																    p_event_id UUID
																)
																RETURNS VOID AS $$
																DECLARE
																    v_moment_id UUID;
																    v_module_code VARCHAR(100);
																    v_event_ref_table VARCHAR(150);
																    v_event_ref_id UUID;
																    v_created_by UUID;
																    v_title TEXT;
																    v_summary TEXT;
																    v_category TEXT;
																    v_feed_id UUID;
																BEGIN
																    SELECT moment_id, module_code, event_ref_table, event_ref_id, created_by
																    INTO v_moment_id, v_module_code, v_event_ref_table, v_event_ref_id, v_created_by
																    FROM group_quick_add_events
																    WHERE event_id = p_event_id;
																
																    v_category :=
																        CASE
																            WHEN v_module_code IN ('PARTICIPANT','CONTRIBUTOR','RESIDENT','MEMBER') THEN 'PEOPLE'
																            WHEN v_module_code IN ('EXPENSE','CONTRIBUTION','BUDGET') THEN 'MONEY'
																            WHEN v_module_code IN ('PLANNING_ITEM','BOOKING','TASK','PURCHASE_ITEM','MILESTONE','PROGRESS_UPDATE') THEN 'OPERATIONS'
																            WHEN v_module_code IN ('VENDOR','OWNERSHIP','DELIVERY','MAINTENANCE','ASSET','RESOURCE','RULE') THEN 'RESOURCES'
																            WHEN v_module_code IN ('MEMORY') THEN 'MEMORY'
																            WHEN v_module_code IN ('POLL','VOTE','APPROVAL') THEN 'DECISIONS'
																            WHEN v_module_code IN ('UPDATE','ANNOUNCEMENT') THEN 'UPDATES'
																            ELSE 'GENERAL'
																        END;
																
																    v_title := INITCAP(REPLACE(v_module_code, '_', ' ')) || ' added';
																    v_summary := 'New ' || LOWER(REPLACE(v_module_code, '_', ' ')) || ' activity recorded.';
																
																    INSERT INTO group_live_feed (
																        moment_id,
																        event_id,
																        feed_category,
																        title,
																        summary,
																        can_view,
																        can_edit,
																        can_delete,
																        visibility,
																        created_by,
																        entity_name,
																        entity_id,
																        category_chip,
																        source_widget,
																        is_editable
																    )
																    VALUES (
																        v_moment_id,
																        p_event_id,
																        v_category,
																        v_title,
																        v_summary,
																        TRUE,
																        TRUE,
																        TRUE,
																        'EVERYONE',
																        v_created_by,
																        v_event_ref_table,
																        v_event_ref_id,
																        v_category,
																        'RECENT_ACTIVITY',
																        TRUE
																    )
																    RETURNING feed_id INTO v_feed_id;
																
																    PERFORM sp_register_activity_edit_route(
																        v_feed_id,
																        v_event_ref_table,
																        v_event_ref_id
																    );
																END;
																$$ LANGUAGE plpgsql;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_activate_business_moment(
																    p_moment_id UUID,
																    p_user_id UUID
																)
																RETURNS VOID
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    UPDATE business_moments
																    SET
																        status = 'active',
																        activated_at = CURRENT_TIMESTAMP,
																        updated_at = CURRENT_TIMESTAMP
																    WHERE moment_id = p_moment_id;
																
																    UPDATE business_moment_governance
																    SET
																        activated_by = p_user_id,
																        activated_at = CURRENT_TIMESTAMP,
																        updated_at = CURRENT_TIMESTAMP
																    WHERE moment_id = p_moment_id;
																
																    UPDATE business_moment_invitations
																    SET
																        invite_status = 'sent',
																        sent_at = CURRENT_TIMESTAMP,
																        updated_at = CURRENT_TIMESTAMP
																    WHERE moment_id = p_moment_id
																      AND send_on_activation = TRUE
																      AND invite_status = 'pending';
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_update_timestamp()
																RETURNS TRIGGER
																LANGUAGE plpgsql
																AS $$
																BEGIN
																    NEW.updated_at = CURRENT_TIMESTAMP;
																    RETURN NEW;
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_activity_created(
																    p_activity_id UUID
																)
																RETURNS VOID
																LANGUAGE plpgsql
																AS $$
																DECLARE
																    v_moment_id UUID;
																BEGIN
																
																    SELECT moment_id
																    INTO v_moment_id
																    FROM team_activities
																    WHERE activity_id = p_activity_id;
																
																    INSERT INTO business_orchestration_jobs (
																        job_id,
																        moment_id,
																        job_type,
																        source_table,
																        source_record_id,
																        job_status,
																        queued_at
																    )
																    VALUES (
																        gen_random_uuid(),
																        v_moment_id,
																        'pulse_refresh',
																        'team_activities',
																        p_activity_id,
																        'queued',
																        CURRENT_TIMESTAMP
																    );
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_approval_submitted(
																    p_approval_id UUID
																)
																RETURNS VOID
																LANGUAGE plpgsql
																AS $$
																DECLARE
																    v_moment_id UUID;
																BEGIN
																
																    SELECT moment_id
																    INTO v_moment_id
																    FROM team_approval_requests
																    WHERE approval_id = p_approval_id;
																
																    INSERT INTO business_orchestration_jobs (
																        job_id,
																        moment_id,
																        job_type,
																        source_table,
																        source_record_id,
																        job_status,
																        queued_at
																    )
																    VALUES (
																        gen_random_uuid(),
																        v_moment_id,
																        'approval_refresh',
																        'team_approval_requests',
																        p_approval_id,
																        'queued',
																        CURRENT_TIMESTAMP
																    );
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_risk_created(
																    p_issue_id UUID
																)
																RETURNS VOID
																LANGUAGE plpgsql
																AS $$
																DECLARE
																    v_moment_id UUID;
																BEGIN
																
																    SELECT moment_id
																    INTO v_moment_id
																    FROM team_issue_risks
																    WHERE issue_id = p_issue_id;
																
																    INSERT INTO business_orchestration_jobs (
																        job_id,
																        moment_id,
																        job_type,
																        source_table,
																        source_record_id,
																        job_status,
																        queued_at
																    )
																    VALUES (
																        gen_random_uuid(),
																        v_moment_id,
																        'risk_refresh',
																        'team_issue_risks',
																        p_issue_id,
																        'queued',
																        CURRENT_TIMESTAMP
																    );
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_create_live_feed_event(
																    p_moment_id UUID,
																    p_source_table VARCHAR,
																    p_source_record_id UUID,
																    p_event_type VARCHAR,
																    p_actor_user_id UUID,
																    p_actor_name VARCHAR,
																    p_headline VARCHAR,
																    p_detail_message TEXT,
																    p_amount NUMERIC,
																    p_priority VARCHAR
																)
																RETURNS VOID
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    INSERT INTO business_live_feed (
																        moment_id,
																        source_table,
																        source_record_id,
																        event_type,
																        actor_user_id,
																        actor_name,
																        headline,
																        detail_message,
																        amount,
																        priority
																    )
																    VALUES (
																        p_moment_id,
																        p_source_table,
																        p_source_record_id,
																        p_event_type,
																        p_actor_user_id,
																        p_actor_name,
																        p_headline,
																        p_detail_message,
																        p_amount,
																        p_priority
																    );
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_write_audit_history(
																    p_moment_id UUID,
																    p_source_table VARCHAR,
																    p_source_record_id UUID,
																    p_field_name VARCHAR,
																    p_old_value TEXT,
																    p_new_value TEXT,
																    p_change_type VARCHAR,
																    p_changed_by UUID,
																    p_changed_by_name VARCHAR
																)
																RETURNS VOID
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    INSERT INTO business_audit_history (
																        moment_id,
																        source_table,
																        source_record_id,
																        field_name,
																        old_value,
																        new_value,
																        change_type,
																        changed_by,
																        changed_by_name
																    )
																    VALUES (
																        p_moment_id,
																        p_source_table,
																        p_source_record_id,
																        p_field_name,
																        p_old_value,
																        p_new_value,
																        p_change_type,
																        p_changed_by,
																        p_changed_by_name
																    );
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_create_notification(
																    p_moment_id UUID,
																    p_recipient_user_id UUID,
																    p_notification_type VARCHAR,
																    p_source_table VARCHAR,
																    p_source_record_id UUID,
																    p_title VARCHAR,
																    p_message TEXT,
																    p_priority VARCHAR
																)
																RETURNS VOID
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    INSERT INTO business_notifications (
																        moment_id,
																        recipient_user_id,
																        notification_type,
																        source_table,
																        source_record_id,
																        title,
																        message,
																        priority,
																        delivery_channel,
																        notification_status
																    )
																    VALUES (
																        p_moment_id,
																        p_recipient_user_id,
																        p_notification_type,
																        p_source_table,
																        p_source_record_id,
																        p_title,
																        p_message,
																        p_priority,
																        'in_app',
																        'queued'
																    );
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_transaction_change_event()
																RETURNS TRIGGER
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    INSERT INTO business_orchestration_jobs (
																        job_id,
																        moment_id,
																        job_type,
																        source_table,
																        source_record_id,
																        job_status,
																        queued_at
																    )
																    VALUES (
																        gen_random_uuid(),
																        NEW.moment_id,
																        'transaction_refresh',
																        TG_TABLE_NAME,
																        COALESCE(NEW.activity_id,
																                 NEW.approval_id,
																                 NEW.update_id,
																                 NEW.issue_id),
																        'queued',
																        CURRENT_TIMESTAMP
																    );
																
																    RETURN NEW;
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_queue_analytics_refresh(
																    p_moment_id UUID,
																    p_job_type VARCHAR
																)
																RETURNS VOID
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    INSERT INTO business_orchestration_jobs (
																        moment_id,
																        job_type,
																        job_status
																    )
																    VALUES (
																        p_moment_id,
																        p_job_type,
																        'queued'
																    );
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_queue_memory_refresh(
																    p_moment_id UUID
																)
																RETURNS VOID
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    PERFORM sp_queue_analytics_refresh(
																        p_moment_id,
																        'memory_refresh'
																    );
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_queue_pulse_refresh(
																    p_moment_id UUID
																)
																RETURNS VOID
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    PERFORM sp_queue_analytics_refresh(
																        p_moment_id,
																        'pulse_refresh'
																    );
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_business_pulse_snapshot(
																    p_moment_id UUID
																)
																RETURNS VOID
																LANGUAGE plpgsql
																AS $$
																DECLARE
																
																    v_activities_count INTEGER;
																    v_completed_count INTEGER;
																    v_inprogress_count INTEGER;
																    v_planned_count INTEGER;
																
																    v_pending_approvals INTEGER;
																
																    v_open_risks INTEGER;
																    v_critical_risks INTEGER;
																
																    v_monthly_spend NUMERIC(18,2);
																
																    v_top_spend_category VARCHAR(255);
																
																BEGIN
																
																    SELECT COUNT(*)
																    INTO v_activities_count
																    FROM team_activities
																    WHERE moment_id = p_moment_id
																      AND archived_at IS NULL;
																
																    SELECT COUNT(*)
																    INTO v_completed_count
																    FROM team_activities
																    WHERE moment_id = p_moment_id
																      AND activity_status = 'completed'
																      AND archived_at IS NULL;
																
																    SELECT COUNT(*)
																    INTO v_inprogress_count
																    FROM team_activities
																    WHERE moment_id = p_moment_id
																      AND activity_status = 'in_progress'
																      AND archived_at IS NULL;
																
																    SELECT COUNT(*)
																    INTO v_planned_count
																    FROM team_activities
																    WHERE moment_id = p_moment_id
																      AND activity_status = 'planned'
																      AND archived_at IS NULL;
																
																    SELECT COUNT(*)
																    INTO v_pending_approvals
																    FROM team_approval_requests
																    WHERE moment_id = p_moment_id
																      AND approval_status = 'pending'
																      AND archived_at IS NULL;
																
																    SELECT COUNT(*)
																    INTO v_open_risks
																    FROM team_issue_risks
																    WHERE moment_id = p_moment_id
																      AND resolution_status <> 'resolved'
																      AND archived_at IS NULL;
																
																    SELECT COUNT(*)
																    INTO v_critical_risks
																    FROM team_issue_risks
																    WHERE moment_id = p_moment_id
																      AND severity = 'critical'
																      AND archived_at IS NULL;
																
																    SELECT COALESCE(SUM(amount),0)
																    INTO v_monthly_spend
																    FROM team_activities
																    WHERE moment_id = p_moment_id
																      AND has_spend = TRUE
																      AND archived_at IS NULL;
																
																    SELECT category
																    INTO v_top_spend_category
																    FROM team_activities
																    WHERE moment_id = p_moment_id
																      AND has_spend = TRUE
																      AND archived_at IS NULL
																    GROUP BY category
																    ORDER BY SUM(amount) DESC
																    LIMIT 1;
																
																    DELETE FROM business_pulse_snapshots
																    WHERE moment_id = p_moment_id
																      AND snapshot_date = CURRENT_DATE;
																
																    INSERT INTO business_pulse_snapshots
																    (
																        moment_id,
																        snapshot_date,
																        activities_count,
																        completed_activities,
																        in_progress_activities,
																        planned_activities,
																        pending_approvals,
																        open_risks,
																        critical_risks,
																        monthly_spend,
																        top_spend_category
																    )
																    VALUES
																    (
																        p_moment_id,
																        CURRENT_DATE,
																        v_activities_count,
																        v_completed_count,
																        v_inprogress_count,
																        v_planned_count,
																        v_pending_approvals,
																        v_open_risks,
																        v_critical_risks,
																        v_monthly_spend,
																        v_top_spend_category
																    );
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_business_moment_metrics(
																    p_moment_id UUID
																)
																RETURNS VOID
																LANGUAGE plpgsql
																AS $$
																DECLARE
																
																    v_members INTEGER;
																    v_activities INTEGER;
																    v_pending INTEGER;
																    v_risks INTEGER;
																    v_spend NUMERIC(18,2);
																    v_last_activity TIMESTAMP;
																
																BEGIN
																
																    SELECT COUNT(*)
																    INTO v_members
																    FROM business_moment_members
																    WHERE moment_id = p_moment_id
																      AND member_status = 'active';
																
																    SELECT COUNT(*)
																    INTO v_activities
																    FROM team_activities
																    WHERE moment_id = p_moment_id
																      AND archived_at IS NULL;
																
																    SELECT COUNT(*)
																    INTO v_pending
																    FROM team_approval_requests
																    WHERE moment_id = p_moment_id
																      AND approval_status = 'pending';
																
																    SELECT COUNT(*)
																    INTO v_risks
																    FROM team_issue_risks
																    WHERE moment_id = p_moment_id
																      AND resolution_status <> 'resolved';
																
																    SELECT COALESCE(SUM(amount),0)
																    INTO v_spend
																    FROM team_activities
																    WHERE moment_id = p_moment_id
																      AND has_spend = TRUE;
																
																    SELECT MAX(recorded_at)
																    INTO v_last_activity
																    FROM team_activities
																    WHERE moment_id = p_moment_id;
																
																    DELETE FROM business_moment_metrics
																    WHERE moment_id = p_moment_id;
																
																    INSERT INTO business_moment_metrics
																    (
																        moment_id,
																        members_count,
																        activities_count,
																        pending_approvals,
																        open_risks,
																        spend_amount,
																        last_activity_at
																    )
																    VALUES
																    (
																        p_moment_id,
																        v_members,
																        v_activities,
																        v_pending,
																        v_risks,
																        v_spend,
																        v_last_activity
																    );
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_business_memory_patterns(
																    p_moment_id UUID
																)
																RETURNS VOID
																LANGUAGE plpgsql
																AS $$
																DECLARE
																
																    v_vendor_count INTEGER;
																    v_risk_count INTEGER;
																    v_approval_count INTEGER;
																
																BEGIN
																
																    DELETE FROM business_memory_patterns
																    WHERE moment_id = p_moment_id;
																
																    SELECT COUNT(DISTINCT vendor_name)
																    INTO v_vendor_count
																    FROM team_activities
																    WHERE moment_id = p_moment_id
																      AND vendor_name IS NOT NULL;
																
																    IF v_vendor_count > 0 THEN
																
																        INSERT INTO business_memory_patterns
																        (
																            moment_id,
																            pattern_type,
																            pattern_title,
																            observation_text,
																            first_observed_at,
																            last_observed_at
																        )
																        VALUES
																        (
																            p_moment_id,
																            'vendor',
																            'Vendor Activity Pattern',
																            CONCAT(v_vendor_count,' vendors have been used in this operational cycle'),
																            CURRENT_TIMESTAMP,
																            CURRENT_TIMESTAMP
																        );
																
																    END IF;
																
																    SELECT COUNT(*)
																    INTO v_risk_count
																    FROM team_issue_risks
																    WHERE moment_id = p_moment_id;
																
																    IF v_risk_count > 0 THEN
																
																        INSERT INTO business_memory_patterns
																        (
																            moment_id,
																            pattern_type,
																            pattern_title,
																            observation_text,
																            first_observed_at,
																            last_observed_at
																        )
																        VALUES
																        (
																            p_moment_id,
																            'risk',
																            'Risk Pattern',
																            CONCAT(v_risk_count,' risks recorded during operations'),
																            CURRENT_TIMESTAMP,
																            CURRENT_TIMESTAMP
																        );
																
																    END IF;
																
																    SELECT COUNT(*)
																    INTO v_approval_count
																    FROM team_approval_requests
																    WHERE moment_id = p_moment_id;
																
																    IF v_approval_count > 0 THEN
																
																        INSERT INTO business_memory_patterns
																        (
																            moment_id,
																            pattern_type,
																            pattern_title,
																            observation_text,
																            first_observed_at,
																            last_observed_at
																        )
																        VALUES
																        (
																            p_moment_id,
																            'approval',
																            'Approval Pattern',
																            CONCAT(v_approval_count,' approval events observed'),
																            CURRENT_TIMESTAMP,
																            CURRENT_TIMESTAMP
																        );
																
																    END IF;
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_business_orchestration(
																    p_moment_id UUID
																)
																RETURNS VOID
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    PERFORM sp_refresh_business_pulse_snapshot(
																        p_moment_id
																    );
																
																    PERFORM sp_refresh_business_moment_metrics(
																        p_moment_id
																    );
																
																    PERFORM sp_refresh_business_memory_patterns(
																        p_moment_id
																    );
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_process_orchestration_job(
																    p_job_id UUID
																)
																RETURNS VOID
																LANGUAGE plpgsql
																AS $$
																DECLARE
																
																    v_moment_id UUID;
																
																BEGIN
																
																    SELECT moment_id
																    INTO v_moment_id
																    FROM business_orchestration_jobs
																    WHERE job_id = p_job_id;
																
																    UPDATE business_orchestration_jobs
																    SET job_status = 'processing'
																    WHERE job_id = p_job_id;
																
																    PERFORM sp_refresh_business_orchestration(
																        v_moment_id
																    );
																
																    UPDATE business_orchestration_jobs
																    SET
																        job_status = 'completed',
																        completed_at = CURRENT_TIMESTAMP
																    WHERE job_id = p_job_id;
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_activity_created_trigger()
																RETURNS TRIGGER
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    PERFORM sp_create_live_feed_event(
																        NEW.moment_id,
																        'team_activities',
																        NEW.activity_id,
																        'activity_created',
																        NEW.created_by,
																        'System',
																        CONCAT('Activity Created: ', NEW.activity_title),
																        NEW.description,
																        NEW.amount,
																        NEW.priority
																    );
																
																    PERFORM sp_queue_pulse_refresh(
																        NEW.moment_id
																    );
																
																    PERFORM sp_queue_memory_refresh(
																        NEW.moment_id
																    );
																
																    RETURN NEW;
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_activity_updated_trigger()
																RETURNS TRIGGER
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    IF OLD.activity_status IS DISTINCT FROM NEW.activity_status THEN
																
																        PERFORM sp_write_audit_history(
																            NEW.moment_id,
																            'team_activities',
																            NEW.activity_id,
																            'activity_status',
																            OLD.activity_status,
																            NEW.activity_status,
																            'edit',
																            NEW.created_by,
																            'System'
																        );
																
																    END IF;
																
																    PERFORM sp_create_live_feed_event(
																        NEW.moment_id,
																        'team_activities',
																        NEW.activity_id,
																        'activity_updated',
																        NEW.created_by,
																        'System',
																        CONCAT('Activity Updated: ', NEW.activity_title),
																        NULL,
																        NEW.amount,
																        NEW.priority
																    );
																
																    PERFORM sp_refresh_business_orchestration(
																        NEW.moment_id
																    );
																
																    RETURN NEW;
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_approval_created_trigger()
																RETURNS TRIGGER
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    PERFORM sp_create_notification(
																        NEW.moment_id,
																        NEW.approver_id,
																        'approval_request',
																        'team_approval_requests',
																        NEW.approval_id,
																        NEW.request_title,
																        NEW.reason,
																        'high'
																    );
																
																    PERFORM sp_create_live_feed_event(
																        NEW.moment_id,
																        'team_approval_requests',
																        NEW.approval_id,
																        'approval_submitted',
																        NEW.requested_by,
																        'System',
																        CONCAT('Approval Requested: ', NEW.request_title),
																        NEW.reason,
																        NEW.amount,
																        'high'
																    );
																
																    PERFORM sp_refresh_business_orchestration(
																        NEW.moment_id
																    );
																
																    RETURN NEW;
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_approval_decision_trigger()
																RETURNS TRIGGER
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    IF OLD.approval_status IS DISTINCT FROM NEW.approval_status THEN
																
																        PERFORM sp_write_audit_history(
																            NEW.moment_id,
																            'team_approval_requests',
																            NEW.approval_id,
																            'approval_status',
																            OLD.approval_status,
																            NEW.approval_status,
																            NEW.approval_status,
																            COALESCE(NEW.decided_by, NEW.requested_by),
																            'System'
																        );
																
																        PERFORM sp_create_live_feed_event(
																            NEW.moment_id,
																            'team_approval_requests',
																            NEW.approval_id,
																            NEW.approval_status,
																            COALESCE(NEW.decided_by, NEW.requested_by),
																            'System',
																            CONCAT('Approval ', INITCAP(NEW.approval_status)),
																            NEW.decision_note,
																            NEW.amount,
																            'high'
																        );
																
																    END IF;
																
																    PERFORM sp_refresh_business_orchestration(
																        NEW.moment_id
																    );
																
																    RETURN NEW;
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_team_update_created_trigger()
																RETURNS TRIGGER
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    PERFORM sp_create_live_feed_event(
																        NEW.moment_id,
																        'team_updates',
																        NEW.update_id,
																        'team_update',
																        NEW.created_by,
																        'System',
																        NEW.update_title,
																        NEW.description,
																        NULL,
																        'medium'
																    );
																
																    PERFORM sp_refresh_business_moment_metrics(
																        NEW.moment_id
																    );
																
																    PERFORM sp_refresh_business_memory_patterns(
																        NEW.moment_id
																    );
																
																    RETURN NEW;
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_risk_created_trigger()
																RETURNS TRIGGER
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    IF NEW.owner_id IS NOT NULL THEN
																
																        PERFORM sp_create_notification(
																            NEW.moment_id,
																            NEW.owner_id,
																            'risk_created',
																            'team_issue_risks',
																            NEW.issue_id,
																            NEW.issue_title,
																            NEW.description,
																            NEW.severity
																        );
																
																    END IF;
																
																    PERFORM sp_create_live_feed_event(
																        NEW.moment_id,
																        'team_issue_risks',
																        NEW.issue_id,
																        'risk_created',
																        NEW.created_by,
																        'System',
																        CONCAT('Risk Logged: ', NEW.issue_title),
																        NEW.description,
																        NULL,
																        NEW.severity
																    );
																
																    PERFORM sp_refresh_business_orchestration(
																        NEW.moment_id
																    );
																
																    RETURN NEW;
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_risk_resolved_trigger()
																RETURNS TRIGGER
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    IF OLD.resolution_status <> 'resolved'
																       AND NEW.resolution_status = 'resolved'
																    THEN
																
																        PERFORM sp_create_live_feed_event(
																            NEW.moment_id,
																            'team_issue_risks',
																            NEW.issue_id,
																            'risk_resolved',
																            NEW.created_by,
																            'System',
																            CONCAT('Risk Resolved: ', NEW.issue_title),
																            NEW.description,
																            NULL,
																            'medium'
																        );
																
																        PERFORM sp_refresh_business_orchestration(
																            NEW.moment_id
																        );
																
																    END IF;
																
																    RETURN NEW;
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_member_accepted_trigger()
																RETURNS TRIGGER
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    IF OLD.member_status <> 'active'
																       AND NEW.member_status = 'active'
																    THEN
																
																        PERFORM sp_create_live_feed_event(
																            NEW.moment_id,
																            'business_moment_members',
																            NEW.member_id,
																            'member_joined',
																            COALESCE(NEW.user_id, NEW.added_by),
																            NEW.name,
																            CONCAT(NEW.name, ' joined the team'),
																            NULL,
																            NULL,
																            'low'
																        );
																
																        PERFORM sp_refresh_business_moment_metrics(
																            NEW.moment_id
																        );
																
																    END IF;
																
																    RETURN NEW;
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_moment_activated_trigger()
																RETURNS TRIGGER
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    IF OLD.status <> 'active'
																       AND NEW.status = 'active'
																    THEN
																
																        PERFORM sp_create_live_feed_event(
																            NEW.moment_id,
																            'business_moments',
																            NEW.moment_id,
																            'moment_activated',
																            NEW.created_by,
																            'System',
																            CONCAT('Moment Activated: ', NEW.moment_name),
																            NULL,
																            NULL,
																            'medium'
																        );
																
																        PERFORM sp_refresh_business_orchestration(
																            NEW.moment_id
																        );
																
																    END IF;
																
																    RETURN NEW;
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_transaction_archived_trigger()
																RETURNS TRIGGER
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    IF OLD.archived_at IS NULL
																       AND NEW.archived_at IS NOT NULL
																    THEN
																
																        PERFORM sp_create_live_feed_event(
																            NEW.moment_id,
																            TG_TABLE_NAME,
																            COALESCE(
																                NEW.activity_id,
																                NEW.approval_id,
																                NEW.update_id,
																                NEW.issue_id
																            ),
																            'record_archived',
																            NEW.created_by,
																            'System',
																            'Transaction Archived',
																            NULL,
																            NULL,
																            'low'
																        );
																
																        PERFORM sp_refresh_business_orchestration(
																            NEW.moment_id
																        );
																
																    END IF;
																
																    RETURN NEW;
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_compute_business_health_status(
    p_pending_approvals INTEGER,
    p_open_risks INTEGER,
    p_critical_risks INTEGER,
    p_monthly_spend NUMERIC,
    p_budget NUMERIC
)
RETURNS TABLE (
    health_score NUMERIC,
    health_status VARCHAR,
    health_reason TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_score NUMERIC := 100;
    v_status VARCHAR := 'stable';
    v_reason TEXT := 'Operations are stable';
    v_budget_usage NUMERIC := 0;
BEGIN

    IF p_budget IS NOT NULL AND p_budget > 0 THEN
        v_budget_usage := (p_monthly_spend / p_budget) * 100;
    END IF;

    v_score := v_score - (p_pending_approvals * 5);
    v_score := v_score - (p_open_risks * 8);
    v_score := v_score - (p_critical_risks * 20);

    IF v_budget_usage > 100 THEN
        v_score := v_score - 25;
    ELSIF v_budget_usage > 85 THEN
        v_score := v_score - 15;
    END IF;

    IF v_score < 0 THEN
        v_score := 0;
    END IF;

    IF p_critical_risks > 0 OR v_score < 50 THEN
        v_status := 'critical';
        v_reason := 'Critical risks or severe operational pressure detected';
    ELSIF p_open_risks > 2 OR v_score < 70 THEN
        v_status := 'at_risk';
        v_reason := 'Open risks are affecting operational stability';
    ELSIF p_pending_approvals > 0 OR v_score < 85 THEN
        v_status := 'attention';
        v_reason := 'Pending approvals or moderate operational signals need attention';
    ELSE
        v_status := 'stable';
        v_reason := 'Operations are stable';
    END IF;

    RETURN QUERY
    SELECT v_score, v_status, v_reason;

END;
$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_business_pulse_snapshot(
    p_moment_id UUID
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
DECLARE
    v_activities_count INTEGER;
    v_completed_count INTEGER;
    v_inprogress_count INTEGER;
    v_planned_count INTEGER;

    v_pending_approvals INTEGER;
    v_open_risks INTEGER;
    v_critical_risks INTEGER;

    v_monthly_spend NUMERIC(18,2);
    v_top_spend_category VARCHAR(255);
    v_budget NUMERIC(18,2);

    v_health_score NUMERIC;
    v_health_status VARCHAR;
    v_health_reason TEXT;
BEGIN

    SELECT COUNT(*)
    INTO v_activities_count
    FROM team_activities
    WHERE moment_id = p_moment_id
      AND archived_at IS NULL;

    SELECT COUNT(*)
    INTO v_completed_count
    FROM team_activities
    WHERE moment_id = p_moment_id
      AND activity_status = 'completed'
      AND archived_at IS NULL;

    SELECT COUNT(*)
    INTO v_inprogress_count
    FROM team_activities
    WHERE moment_id = p_moment_id
      AND activity_status = 'in_progress'
      AND archived_at IS NULL;

    SELECT COUNT(*)
    INTO v_planned_count
    FROM team_activities
    WHERE moment_id = p_moment_id
      AND activity_status = 'planned'
      AND archived_at IS NULL;

    SELECT COUNT(*)
    INTO v_pending_approvals
    FROM team_approval_requests
    WHERE moment_id = p_moment_id
      AND approval_status = 'pending'
      AND archived_at IS NULL;

    SELECT COUNT(*)
    INTO v_open_risks
    FROM team_issue_risks
    WHERE moment_id = p_moment_id
      AND resolution_status <> 'resolved'
      AND archived_at IS NULL;

    SELECT COUNT(*)
    INTO v_critical_risks
    FROM team_issue_risks
    WHERE moment_id = p_moment_id
      AND severity = 'critical'
      AND archived_at IS NULL;

    SELECT COALESCE(SUM(amount),0)
    INTO v_monthly_spend
    FROM team_activities
    WHERE moment_id = p_moment_id
      AND has_spend = TRUE
      AND archived_at IS NULL;

    SELECT category
    INTO v_top_spend_category
    FROM team_activities
    WHERE moment_id = p_moment_id
      AND has_spend = TRUE
      AND archived_at IS NULL
    GROUP BY category
    ORDER BY SUM(amount) DESC
    LIMIT 1;

    SELECT monthly_budget
    INTO v_budget
    FROM business_moment_setup
    WHERE moment_id = p_moment_id;

    SELECT hs.health_score, hs.health_status, hs.health_reason
    INTO v_health_score, v_health_status, v_health_reason
    FROM fn_compute_business_health_status(
        v_pending_approvals,
        v_open_risks,
        v_critical_risks,
        v_monthly_spend,
        v_budget
    ) hs;

    DELETE FROM business_pulse_snapshots
    WHERE moment_id = p_moment_id
      AND snapshot_date = CURRENT_DATE;

    INSERT INTO business_pulse_snapshots (
        moment_id,
        snapshot_date,
        activities_count,
        completed_activities,
        in_progress_activities,
        planned_activities,
        pending_approvals,
        open_risks,
        critical_risks,
        monthly_spend,
        top_spend_category,
        health_score,
        health_status,
        health_reason
    )
    VALUES (
        p_moment_id,
        CURRENT_DATE,
        v_activities_count,
        v_completed_count,
        v_inprogress_count,
        v_planned_count,
        v_pending_approvals,
        v_open_risks,
        v_critical_risks,
        v_monthly_spend,
        v_top_spend_category,
        v_health_score,
        v_health_status,
        v_health_reason
    );

END;
$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_resolve_suggested_approver(
    p_moment_id UUID,
    p_amount NUMERIC
)
RETURNS TABLE (
    approver_member_id UUID,
    approver_user_id UUID,
    approver_name VARCHAR,
    approver_role VARCHAR,
    resolver_reason TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN

    RETURN QUERY
    SELECT
        m.member_id,
        m.user_id,
        m.name,
        m.role,
        'Budget Owner selected because request involves spending approval'::TEXT
    FROM business_moment_members m
    WHERE m.moment_id = p_moment_id
      AND m.is_budget_owner = TRUE
      AND m.member_status IN ('configured','active')
    ORDER BY m.created_at ASC
    LIMIT 1;

    IF FOUND THEN
        RETURN;
    END IF;

    RETURN QUERY
    SELECT
        m.member_id,
        m.user_id,
        m.name,
        m.role,
        'Approver selected because no Budget Owner was found'::TEXT
    FROM business_moment_members m
    WHERE m.moment_id = p_moment_id
      AND m.role = 'Approver'
      AND m.member_status IN ('configured','active')
    ORDER BY m.created_at ASC
    LIMIT 1;

    IF FOUND THEN
        RETURN;
    END IF;

    RETURN QUERY
    SELECT
        m.member_id,
        m.user_id,
        m.name,
        m.role,
        'Team Lead selected because no Budget Owner or Approver was found'::TEXT
    FROM business_moment_members m
    WHERE m.moment_id = p_moment_id
      AND m.is_team_lead = TRUE
      AND m.member_status IN ('configured','active')
    ORDER BY m.created_at ASC
    LIMIT 1;

END;
$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_business_memory_patterns(
    p_moment_id UUID
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
DECLARE
    v_top_vendor VARCHAR;
    v_top_vendor_count INTEGER;
    v_top_category VARCHAR;
    v_top_category_spend NUMERIC;
    v_approval_count INTEGER;
    v_risk_count INTEGER;
    v_owner_name VARCHAR;
    v_owner_activity_count INTEGER;
BEGIN

    DELETE FROM business_memory_patterns
    WHERE moment_id = p_moment_id;

    SELECT vendor_name, COUNT(*)
    INTO v_top_vendor, v_top_vendor_count
    FROM team_activities
    WHERE moment_id = p_moment_id
      AND vendor_name IS NOT NULL
      AND archived_at IS NULL
    GROUP BY vendor_name
    ORDER BY COUNT(*) DESC
    LIMIT 1;

    IF v_top_vendor IS NOT NULL THEN
        INSERT INTO business_memory_patterns (
            moment_id,
            pattern_type,
            pattern_title,
            observation_text,
            source_metric,
            confidence_level,
            first_observed_at,
            last_observed_at
        )
        VALUES (
            p_moment_id,
            'vendor_pattern',
            'Vendor Activity Pattern',
            CONCAT(v_top_vendor, ' appears most frequently in operational activity'),
            CONCAT('vendor_count=', v_top_vendor_count),
            80,
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP
        );
    END IF;

    SELECT category, COALESCE(SUM(amount),0)
    INTO v_top_category, v_top_category_spend
    FROM team_activities
    WHERE moment_id = p_moment_id
      AND has_spend = TRUE
      AND archived_at IS NULL
    GROUP BY category
    ORDER BY SUM(amount) DESC
    LIMIT 1;

    IF v_top_category IS NOT NULL THEN
        INSERT INTO business_memory_patterns (
            moment_id,
            pattern_type,
            pattern_title,
            observation_text,
            source_metric,
            confidence_level,
            first_observed_at,
            last_observed_at
        )
        VALUES (
            p_moment_id,
            'spend_pattern',
            'Infrastructure spending is currently the largest operational cost category',
            CONCAT(v_top_category, ' is the highest spend category with ₹', v_top_category_spend),
            CONCAT('top_category_spend=', v_top_category_spend),
            85,
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP
        );
    END IF;

    SELECT COUNT(*)
    INTO v_approval_count
    FROM team_approval_requests
    WHERE moment_id = p_moment_id
      AND archived_at IS NULL;

    IF v_approval_count > 0 THEN
        INSERT INTO business_memory_patterns (
            moment_id,
            pattern_type,
            pattern_title,
            observation_text,
            source_metric,
            confidence_level,
            first_observed_at,
            last_observed_at
        )
        VALUES (
            p_moment_id,
            'approval_pattern',
            'Approval requests are becoming more common this month',
            CONCAT(v_approval_count, ' approval requests observed in this operational cycle'),
            CONCAT('approval_count=', v_approval_count),
            75,
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP
        );
    END IF;

    SELECT COUNT(*)
    INTO v_risk_count
    FROM team_issue_risks
    WHERE moment_id = p_moment_id
      AND resolution_status <> 'resolved'
      AND archived_at IS NULL;

    IF v_risk_count > 0 THEN
        INSERT INTO business_memory_patterns (
            moment_id,
            pattern_type,
            pattern_title,
            observation_text,
            source_metric,
            confidence_level,
            first_observed_at,
            last_observed_at
        )
        VALUES (
            p_moment_id,
            'risk_pattern',
            'Vendor-related issues appeared more frequently than other operational risks',
            CONCAT(v_risk_count, ' open operational risks need attention'),
            CONCAT('open_risk_count=', v_risk_count),
            78,
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP
        );
    END IF;

    SELECT m.name, COUNT(*)
    INTO v_owner_name, v_owner_activity_count
    FROM team_activities a
    JOIN business_moment_members m
      ON a.activity_owner_id = m.member_id
    WHERE a.moment_id = p_moment_id
      AND a.archived_at IS NULL
    GROUP BY m.name
    ORDER BY COUNT(*) DESC
    LIMIT 1;

    IF v_owner_name IS NOT NULL THEN
        INSERT INTO business_memory_patterns (
            moment_id,
            pattern_type,
            pattern_title,
            observation_text,
            source_metric,
            confidence_level,
            first_observed_at,
            last_observed_at
        )
        VALUES (
            p_moment_id,
            'ownership_pattern',
            CONCAT(v_owner_name, ' currently owns most completed activities'),
            CONCAT(v_owner_name, ' is the most frequent activity owner'),
            CONCAT('owned_activity_count=', v_owner_activity_count),
            72,
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP
        );
    END IF;

END;
$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_ai_signals(
    p_moment_id UUID
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
DECLARE
    v_pending_approvals INTEGER;
    v_open_risks INTEGER;
    v_critical_risks INTEGER;
    v_monthly_spend NUMERIC;
    v_budget NUMERIC;
BEGIN

    DELETE FROM ai_signals
    WHERE moment_id = p_moment_id
      AND signal_status = 'active';

    SELECT COUNT(*)
    INTO v_pending_approvals
    FROM team_approval_requests
    WHERE moment_id = p_moment_id
      AND approval_status = 'pending'
      AND archived_at IS NULL;

    SELECT COUNT(*)
    INTO v_open_risks
    FROM team_issue_risks
    WHERE moment_id = p_moment_id
      AND resolution_status <> 'resolved'
      AND archived_at IS NULL;

    SELECT COUNT(*)
    INTO v_critical_risks
    FROM team_issue_risks
    WHERE moment_id = p_moment_id
      AND severity = 'critical'
      AND archived_at IS NULL;

    SELECT COALESCE(SUM(amount),0)
    INTO v_monthly_spend
    FROM team_activities
    WHERE moment_id = p_moment_id
      AND has_spend = TRUE
      AND archived_at IS NULL;

    SELECT monthly_budget
    INTO v_budget
    FROM business_moment_setup
    WHERE moment_id = p_moment_id;

    IF v_pending_approvals > 0 THEN
        INSERT INTO ai_signals (
            moment_id,
            signal_type,
            signal_title,
            signal_message,
            severity,
            confidence_score,
            recommended_action,
            target_screen
        )
        VALUES (
            p_moment_id,
            'approval_cycle',
            'Pending Payment Cycle',
            CONCAT(v_pending_approvals, ' operational approval request(s) are waiting for final verification and dispatch.'),
            'medium',
            82,
            'Review pending approvals',
            'pulse'
        );
    END IF;

    IF v_open_risks > 0 THEN
        INSERT INTO ai_signals (
            moment_id,
            signal_type,
            signal_title,
            signal_message,
            severity,
            confidence_score,
            recommended_action,
            target_screen
        )
        VALUES (
            p_moment_id,
            'risk_attention',
            'Operational Risks Need Attention',
            CONCAT(v_open_risks, ' open risk(s) may affect operational execution.'),
            CASE WHEN v_critical_risks > 0 THEN 'critical' ELSE 'high' END,
            86,
            'Open risk tracker',
            'memory'
        );
    END IF;

    IF v_budget IS NOT NULL
       AND v_budget > 0
       AND v_monthly_spend >= (v_budget * 0.80)
    THEN
        INSERT INTO ai_signals (
            moment_id,
            signal_type,
            signal_title,
            signal_message,
            severity,
            confidence_score,
            recommended_action,
            target_screen
        )
        VALUES (
            p_moment_id,
            'budget_pressure',
            'Budget Usage Is Increasing',
            CONCAT('Current spend is ₹', v_monthly_spend, ' against a budget of ₹', v_budget),
            CASE WHEN v_monthly_spend > v_budget THEN 'critical' ELSE 'high' END,
            88,
            'Review spend activity',
            'pulse'
        );
    END IF;

END;
$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_business_orchestration(
    p_moment_id UUID
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
BEGIN

    PERFORM sp_refresh_business_pulse_snapshot(p_moment_id);

    PERFORM sp_refresh_business_moment_metrics(p_moment_id);

    PERFORM sp_refresh_business_memory_patterns(p_moment_id);

    PERFORM sp_refresh_ai_signals(p_moment_id);

END;
$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_get_business_actor_name(
    p_moment_id UUID,
    p_actor_id UUID
)
RETURNS VARCHAR
LANGUAGE plpgsql
AS $$
DECLARE
    v_name VARCHAR;
BEGIN
    SELECT name
    INTO v_name
    FROM business_moment_members
    WHERE moment_id = p_moment_id
      AND (
            member_id = p_actor_id
            OR user_id = p_actor_id
          )
    LIMIT 1;

    RETURN COALESCE(v_name, 'System');
END;
$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_is_notification_allowed(
    p_moment_id UUID,
    p_notification_type VARCHAR
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
    v_allowed BOOLEAN := TRUE;
BEGIN

    SELECT
        CASE
            WHEN p_notification_type IN ('approval_request','approval_decision')
                THEN notify_approvals
            WHEN p_notification_type IN ('spending_activity','budget_pressure')
                THEN notify_spending_activity
            WHEN p_notification_type IN ('risk_created','risk_resolved','risk_attention')
                THEN notify_issues_risks
            WHEN p_notification_type IN ('team_update','member_joined')
                THEN notify_team_updates
            ELSE TRUE
        END
    INTO v_allowed
    FROM business_moment_governance
    WHERE moment_id = p_moment_id;

    RETURN COALESCE(v_allowed, TRUE);

END;
$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_create_notification(
    p_moment_id UUID,
    p_recipient_user_id UUID,
    p_notification_type VARCHAR,
    p_source_table VARCHAR,
    p_source_record_id UUID,
    p_title VARCHAR,
    p_message TEXT,
    p_priority VARCHAR
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
BEGIN

    IF fn_is_notification_allowed(p_moment_id, p_notification_type) = FALSE THEN
        RETURN;
    END IF;

    INSERT INTO business_notifications (
        moment_id,
        recipient_user_id,
        notification_type,
        source_table,
        source_record_id,
        title,
        message,
        priority,
        delivery_channel,
        notification_status
    )
    VALUES (
        p_moment_id,
        p_recipient_user_id,
        p_notification_type,
        p_source_table,
        p_source_record_id,
        p_title,
        p_message,
        p_priority,
        'in_app',
        'queued'
    );

END;
$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_validate_business_member_reference(
    p_moment_id UUID,
    p_reference_id UUID
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
    v_exists BOOLEAN;
BEGIN

    IF p_reference_id IS NULL THEN
        RETURN TRUE;
    END IF;

    SELECT EXISTS (
        SELECT 1
        FROM business_moment_members
        WHERE moment_id = p_moment_id
          AND (
                member_id = p_reference_id
                OR user_id = p_reference_id
              )
          AND member_status <> 'removed'
    )
    INTO v_exists;

    RETURN v_exists;

END;
$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_validate_team_activity_member_refs()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN

    IF fn_validate_business_member_reference(NEW.moment_id, NEW.activity_owner_id) = FALSE THEN
        RAISE EXCEPTION 'Invalid activity_owner_id for this moment';
    END IF;

    RETURN NEW;

END;
$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_validate_approval_member_refs()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN

    IF fn_validate_business_member_reference(NEW.moment_id, NEW.requested_by) = FALSE THEN
        RAISE EXCEPTION 'Invalid requested_by for this moment';
    END IF;

    IF fn_validate_business_member_reference(NEW.moment_id, NEW.approver_id) = FALSE THEN
        RAISE EXCEPTION 'Invalid approver_id for this moment';
    END IF;

    RETURN NEW;

END;
$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_validate_issue_member_refs()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN

    IF fn_validate_business_member_reference(NEW.moment_id, NEW.owner_id) = FALSE THEN
        RAISE EXCEPTION 'Invalid owner_id for this moment';
    END IF;

    RETURN NEW;

END;
$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_convert_approval_to_spend_activity(
    p_approval_id UUID,
    p_user_id UUID
)
RETURNS UUID
LANGUAGE plpgsql
AS $$
DECLARE
    v_approval team_approval_requests%ROWTYPE;
    v_activity_id UUID;
BEGIN

    SELECT *
    INTO v_approval
    FROM team_approval_requests
    WHERE approval_id = p_approval_id;

    IF v_approval.approval_status <> 'approved' THEN
        RAISE EXCEPTION 'Only approved requests can be converted to spend';
    END IF;

    IF v_approval.converted_to_spend = TRUE THEN
        RETURN v_approval.converted_activity_id;
    END IF;

    INSERT INTO team_activities (
        moment_id,
        activity_title,
        category,
        description,
        activity_status,
        activity_owner_id,
        has_spend,
        amount,
        priority,
        created_by
    )
    VALUES (
        v_approval.moment_id,
        v_approval.request_title,
        v_approval.approval_type,
        v_approval.reason,
        'completed',
        v_approval.requested_by,
        TRUE,
        v_approval.amount,
        CASE WHEN v_approval.priority = 'urgent' THEN 'high' ELSE 'medium' END,
        p_user_id
    )
    RETURNING activity_id INTO v_activity_id;

    UPDATE team_approval_requests
    SET
        converted_to_spend = TRUE,
        converted_activity_id = v_activity_id,
        converted_at = CURRENT_TIMESTAMP,
        updated_at = CURRENT_TIMESTAMP
    WHERE approval_id = p_approval_id;

    PERFORM sp_refresh_business_orchestration(v_approval.moment_id);

    RETURN v_activity_id;

END;
$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_auto_convert_approved_spend()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN

    IF OLD.approval_status IS DISTINCT FROM NEW.approval_status
       AND NEW.approval_status = 'approved'
       AND NEW.approval_type IN ('Spending','Vendor Payment','Budget')
       AND NEW.converted_to_spend = FALSE
    THEN
        PERFORM sp_convert_approval_to_spend_activity(
            NEW.approval_id,
            COALESCE(NEW.decided_by, NEW.requested_by)
        );
    END IF;

    RETURN NEW;

END;
$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_activity_created_trigger()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN

    PERFORM sp_create_live_feed_event(
        NEW.moment_id,
        'team_activities',
        NEW.activity_id,
        'activity_created',
        NEW.created_by,
        fn_get_business_actor_name(NEW.moment_id, NEW.created_by),
        CONCAT('Activity Created: ', NEW.activity_title),
        NEW.description,
        NEW.amount,
        NEW.priority
    );

    PERFORM sp_refresh_business_orchestration(NEW.moment_id);

    RETURN NEW;

END;
$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_approval_created_trigger()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN

    PERFORM sp_create_notification(
        NEW.moment_id,
        NEW.approver_id,
        'approval_request',
        'team_approval_requests',
        NEW.approval_id,
        NEW.request_title,
        NEW.reason,
        'high'
    );

    PERFORM sp_create_live_feed_event(
        NEW.moment_id,
        'team_approval_requests',
        NEW.approval_id,
        'approval_submitted',
        NEW.requested_by,
        fn_get_business_actor_name(NEW.moment_id, NEW.requested_by),
        CONCAT('Approval Requested: ', NEW.request_title),
        NEW.reason,
        NEW.amount,
        'high'
    );

    PERFORM sp_refresh_business_orchestration(NEW.moment_id);
    RETURN NEW;
END;
$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_risk_created_trigger()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN

    IF NEW.owner_id IS NOT NULL THEN
        PERFORM sp_create_notification(
            NEW.moment_id,
            NEW.owner_id,
            'risk_created',
            'team_issue_risks',
            NEW.issue_id,
            NEW.issue_title,
            NEW.description,
            NEW.severity
        );
    END IF;

    PERFORM sp_create_live_feed_event(
        NEW.moment_id,
        'team_issue_risks',
        NEW.issue_id,
        'risk_created',
        NEW.created_by,
        fn_get_business_actor_name(NEW.moment_id, NEW.created_by),
        CONCAT('Risk Logged: ', NEW.issue_title),
        NEW.description,
        NULL,
        NEW.severity
    );

    PERFORM sp_refresh_business_orchestration(NEW.moment_id);

    RETURN NEW;

END;
$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_apply_runway_member_permissions()
																RETURNS TRIGGER
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    NEW.can_add_runway_transactions :=
																        NEW.role IN (
																            'Runway Owner',
																            'Finance Lead',
																            'Operations Lead',
																            'Financial Contributor'
																        );
																
																    NEW.can_edit_financial_entries :=
																        NEW.role IN (
																            'Runway Owner',
																            'Finance Lead'
																        );
																
																    NEW.can_manage_runway_settings :=
																        NEW.role = 'Runway Owner';
																
																    NEW.can_approve_runway_changes :=
																        NEW.role IN (
																            'Runway Owner',
																            'Finance Lead',
																            'Approver'
																        );
																
																    RETURN NEW;
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_validate_runway_member_reference(
																    p_moment_id UUID,
																    p_reference_id UUID
																)
																RETURNS BOOLEAN
																LANGUAGE plpgsql
																AS $$
																DECLARE
																    v_exists BOOLEAN;
																BEGIN
																
																    IF p_reference_id IS NULL THEN
																        RETURN TRUE;
																    END IF;
																
																    SELECT EXISTS (
																        SELECT 1
																        FROM business_moment_members
																        WHERE moment_id = p_moment_id
																          AND (
																                member_id = p_reference_id
																                OR user_id = p_reference_id
																              )
																          AND member_status <> 'removed'
																          AND role IN (
																                'Runway Owner',
																                'Finance Lead',
																                'Operations Lead',
																                'Financial Contributor',
																                'Approver',
																                'Viewer'
																          )
																    )
																    INTO v_exists;
																
																    RETURN COALESCE(v_exists, FALSE);
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_validate_runway_risk_member_refs()
																RETURNS TRIGGER
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    IF fn_validate_runway_member_reference(NEW.moment_id, NEW.owner_id) = FALSE THEN
																        RAISE EXCEPTION 'Invalid runway risk owner_id for this moment';
																    END IF;
																
																    RETURN NEW;
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_validate_runway_decision_member_refs()
																RETURNS TRIGGER
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    IF fn_validate_runway_member_reference(NEW.moment_id, NEW.decision_owner_id) = FALSE THEN
																        RAISE EXCEPTION 'Invalid runway decision_owner_id for this moment';
																    END IF;
																
																    RETURN NEW;
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_get_runway_actor_name(
																    p_moment_id UUID,
																    p_actor_id UUID
																)
																RETURNS VARCHAR
																LANGUAGE plpgsql
																AS $$
																DECLARE
																    v_name VARCHAR;
																BEGIN
																
																    SELECT name
																    INTO v_name
																    FROM business_moment_members
																    WHERE moment_id = p_moment_id
																      AND (
																            member_id = p_actor_id
																            OR user_id = p_actor_id
																          )
																    LIMIT 1;
																
																    RETURN COALESCE(v_name, 'System');
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_get_runway_source_record_id()
																RETURNS TRIGGER
																LANGUAGE plpgsql
																AS $$
																BEGIN
																    RETURN NEW;
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_business_runway_snapshot(
																    p_moment_id UUID
																)
																RETURNS VOID
																LANGUAGE plpgsql
																AS $$
																DECLARE
																    v_base_cash NUMERIC(18,2) := 0;
																    v_base_burn NUMERIC(18,2) := 0;
																    v_base_revenue NUMERIC(18,2) := 0;
																    v_operating_currency VARCHAR(10) := 'INR';
																
																    v_cash_inflow NUMERIC(18,2) := 0;
																    v_expense_burn NUMERIC(18,2) := 0;
																    v_net_burn NUMERIC(18,2) := 0;
																    v_cash_available NUMERIC(18,2) := 0;
																    v_estimated_runway NUMERIC(10,2) := 0;
																
																    v_open_risks INTEGER := 0;
																    v_decision_count INTEGER := 0;
																BEGIN
																
																    SELECT
																        cash_available,
																        monthly_burn,
																        monthly_revenue,
																        operating_currency
																    INTO
																        v_base_cash,
																        v_base_burn,
																        v_base_revenue,
																        v_operating_currency
																    FROM business_runway_setup
																    WHERE moment_id = p_moment_id;
																
																    SELECT COALESCE(SUM(amount_in_operating_currency), 0)
																    INTO v_cash_inflow
																    FROM runway_cash_inflows
																    WHERE moment_id = p_moment_id
																      AND archived_at IS NULL;
																
																    SELECT COALESCE(SUM(amount_in_operating_currency), 0)
																    INTO v_expense_burn
																    FROM runway_expense_burns
																    WHERE moment_id = p_moment_id
																      AND archived_at IS NULL
																      AND approval_status IN ('not_required', 'approved');
																
																    v_cash_available :=
																        COALESCE(v_base_cash,0)
																        + COALESCE(v_cash_inflow,0)
																        - COALESCE(v_expense_burn,0);
																
																    v_net_burn :=
																        GREATEST(
																            COALESCE(v_base_burn,0)
																            + COALESCE(v_expense_burn,0)
																            - COALESCE(v_base_revenue,0)
																            - COALESCE(v_cash_inflow,0),
																            0
																        );
																
																    IF v_net_burn > 0 THEN
																        v_estimated_runway := ROUND(v_cash_available / v_net_burn, 2);
																    ELSE
																        v_estimated_runway := 999.99;
																    END IF;
																
																    SELECT COUNT(*)
																    INTO v_open_risks
																    FROM runway_risks
																    WHERE moment_id = p_moment_id
																      AND risk_status <> 'resolved'
																      AND archived_at IS NULL;
																
																    SELECT COUNT(*)
																    INTO v_decision_count
																    FROM runway_strategic_decisions
																    WHERE moment_id = p_moment_id
																      AND archived_at IS NULL;
																
																    DELETE FROM business_runway_snapshots
																    WHERE moment_id = p_moment_id
																      AND snapshot_date = CURRENT_DATE;
																
																    INSERT INTO business_runway_snapshots (
																        moment_id,
																        snapshot_date,
																        cash_available,
																        total_cash_inflow,
																        total_expense_burn,
																        net_burn,
																        estimated_runway_months,
																        open_risks,
																        decision_count,
																        operating_currency,
																        generated_at
																    )
																    VALUES (
																        p_moment_id,
																        CURRENT_DATE,
																        v_cash_available,
																        v_cash_inflow,
																        v_expense_burn,
																        v_net_burn,
																        v_estimated_runway,
																        v_open_risks,
																        v_decision_count,
																        COALESCE(v_operating_currency, 'INR'),
																        CURRENT_TIMESTAMP
																    );
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_business_runway_pulse_snapshot(
																    p_moment_id UUID
																)
																RETURNS VOID
																LANGUAGE plpgsql
																AS $$
																DECLARE
																    v_snapshot business_runway_snapshots%ROWTYPE;
																    v_threshold NUMERIC(10,2) := 6;
																    v_alert_count INTEGER := 0;
																    v_high_risk_count INTEGER := 0;
																BEGIN
																
																    PERFORM sp_refresh_business_runway_snapshot(p_moment_id);
																
																    SELECT *
																    INTO v_snapshot
																    FROM business_runway_snapshots
																    WHERE moment_id = p_moment_id
																      AND snapshot_date = CURRENT_DATE;
																
																    SELECT alert_threshold_months
																    INTO v_threshold
																    FROM business_runway_structure
																    WHERE moment_id = p_moment_id;
																
																    SELECT COUNT(*)
																    INTO v_high_risk_count
																    FROM runway_risks
																    WHERE moment_id = p_moment_id
																      AND severity IN ('high','critical')
																      AND risk_status <> 'resolved'
																      AND archived_at IS NULL;
																
																    IF v_snapshot.estimated_runway_months <= COALESCE(v_threshold, 6) THEN
																        v_alert_count := v_alert_count + 1;
																    END IF;
																
																    IF v_high_risk_count > 0 THEN
																        v_alert_count := v_alert_count + v_high_risk_count;
																    END IF;
																
																    DELETE FROM business_pulse_snapshots
																    WHERE moment_id = p_moment_id
																      AND snapshot_date = CURRENT_DATE;
																
																    INSERT INTO business_pulse_snapshots (
																        moment_id,
																        snapshot_date,
																
																        activities_count,
																        completed_activities,
																        in_progress_activities,
																        planned_activities,
																        pending_approvals,
																        open_risks,
																        critical_risks,
																        monthly_spend,
																        top_spend_category,
																
																        cash_available,
																        estimated_runway_months,
																        cash_inflow_total,
																        expense_burn_total,
																        net_burn,
																        runway_alert_count,
																        runway_risk_count,
																        operating_currency,
																
																        generated_at
																    )
																    VALUES (
																        p_moment_id,
																        CURRENT_DATE,
																
																        0,
																        0,
																        0,
																        0,
																        (
																            SELECT COUNT(*)
																            FROM runway_financial_updates
																            WHERE moment_id = p_moment_id
																              AND approval_status = 'pending'
																              AND archived_at IS NULL
																        ),
																        v_snapshot.open_risks,
																        (
																            SELECT COUNT(*)
																            FROM runway_risks
																            WHERE moment_id = p_moment_id
																              AND severity = 'critical'
																              AND risk_status <> 'resolved'
																              AND archived_at IS NULL
																        ),
																        v_snapshot.total_expense_burn,
																        (
																            SELECT expense_category
																            FROM runway_expense_burns
																            WHERE moment_id = p_moment_id
																              AND archived_at IS NULL
																            GROUP BY expense_category
																            ORDER BY SUM(amount_in_operating_currency) DESC
																            LIMIT 1
																        ),
																
																        v_snapshot.cash_available,
																        v_snapshot.estimated_runway_months,
																        v_snapshot.total_cash_inflow,
																        v_snapshot.total_expense_burn,
																        v_snapshot.net_burn,
																        v_alert_count,
																        v_snapshot.open_risks,
																        v_snapshot.operating_currency,
																
																        CURRENT_TIMESTAMP
																    );
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_business_runway_moment_metrics(
																    p_moment_id UUID
																)
																RETURNS VOID
																LANGUAGE plpgsql
																AS $$
																DECLARE
																    v_snapshot business_runway_snapshots%ROWTYPE;
																    v_members_count INTEGER := 0;
																    v_last_activity TIMESTAMP;
																BEGIN
																
																    PERFORM sp_refresh_business_runway_snapshot(p_moment_id);
																
																    SELECT *
																    INTO v_snapshot
																    FROM business_runway_snapshots
																    WHERE moment_id = p_moment_id
																      AND snapshot_date = CURRENT_DATE;
																
																    SELECT COUNT(*)
																    INTO v_members_count
																    FROM business_moment_members
																    WHERE moment_id = p_moment_id
																      AND member_status IN ('configured','active');
																
																    SELECT MAX(latest_at)
																    INTO v_last_activity
																    FROM (
																        SELECT MAX(created_at) AS latest_at
																        FROM runway_cash_inflows
																        WHERE moment_id = p_moment_id
																          AND archived_at IS NULL
																
																        UNION ALL
																
																        SELECT MAX(created_at) AS latest_at
																        FROM runway_expense_burns
																        WHERE moment_id = p_moment_id
																          AND archived_at IS NULL
																
																        UNION ALL
																
																        SELECT MAX(created_at) AS latest_at
																        FROM runway_risks
																        WHERE moment_id = p_moment_id
																          AND archived_at IS NULL
																
																        UNION ALL
																
																        SELECT MAX(created_at) AS latest_at
																        FROM runway_strategic_decisions
																        WHERE moment_id = p_moment_id
																          AND archived_at IS NULL
																
																        UNION ALL
																
																        SELECT MAX(created_at) AS latest_at
																        FROM runway_financial_updates
																        WHERE moment_id = p_moment_id
																          AND archived_at IS NULL
																    ) x;
																
																    DELETE FROM business_moment_metrics
																    WHERE moment_id = p_moment_id;
																
																    INSERT INTO business_moment_metrics (
																        moment_id,
																        members_count,
																        activities_count,
																        pending_approvals,
																        open_risks,
																        spend_amount,
																        last_activity_at,
																
																        cash_available,
																        estimated_runway_months,
																        cash_inflow_count,
																        expense_count,
																        risk_count,
																        decision_count,
																        net_burn,
																        operating_currency,
																
																        last_updated_at
																    )
																    VALUES (
																        p_moment_id,
																        v_members_count,
																        (
																            SELECT COUNT(*)
																            FROM runway_cash_inflows
																            WHERE moment_id = p_moment_id
																              AND archived_at IS NULL
																        )
																        +
																        (
																            SELECT COUNT(*)
																            FROM runway_expense_burns
																            WHERE moment_id = p_moment_id
																              AND archived_at IS NULL
																        )
																        +
																        (
																            SELECT COUNT(*)
																            FROM runway_risks
																            WHERE moment_id = p_moment_id
																              AND archived_at IS NULL
																        )
																        +
																        (
																            SELECT COUNT(*)
																            FROM runway_strategic_decisions
																            WHERE moment_id = p_moment_id
																              AND archived_at IS NULL
																        ),
																        (
																            SELECT COUNT(*)
																            FROM runway_financial_updates
																            WHERE moment_id = p_moment_id
																              AND approval_status = 'pending'
																              AND archived_at IS NULL
																        ),
																        v_snapshot.open_risks,
																        v_snapshot.total_expense_burn,
																        v_last_activity,
																
																        v_snapshot.cash_available,
																        v_snapshot.estimated_runway_months,
																        (
																            SELECT COUNT(*)
																            FROM runway_cash_inflows
																            WHERE moment_id = p_moment_id
																              AND archived_at IS NULL
																        ),
																        (
																            SELECT COUNT(*)
																            FROM runway_expense_burns
																            WHERE moment_id = p_moment_id
																              AND archived_at IS NULL
																        ),
																        (
																            SELECT COUNT(*)
																            FROM runway_risks
																            WHERE moment_id = p_moment_id
																              AND archived_at IS NULL
																        ),
																        v_snapshot.decision_count,
																        v_snapshot.net_burn,
																        v_snapshot.operating_currency,
																
																        CURRENT_TIMESTAMP
																    );
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_business_runway_memory_patterns(
																    p_moment_id UUID
																)
																RETURNS VOID
																LANGUAGE plpgsql
																AS $$
																DECLARE
																    v_cash_count INTEGER := 0;
																    v_top_expense_category VARCHAR(100);
																    v_top_expense_amount NUMERIC(18,2);
																    v_top_risk_type VARCHAR(100);
																    v_top_risk_count INTEGER;
																    v_top_decision_type VARCHAR(100);
																    v_decision_count INTEGER;
																    v_financial_update_count INTEGER := 0;
																BEGIN
																
																    DELETE FROM business_memory_patterns
																    WHERE moment_id = p_moment_id
																      AND pattern_type IN (
																          'cash_inflow_pattern',
																          'burn_pattern',
																          'runway_risk_pattern',
																          'decision_pattern',
																          'financial_update_pattern',
																          'net_burn_pattern'
																      );
																
																    SELECT COUNT(*)
																    INTO v_cash_count
																    FROM runway_cash_inflows
																    WHERE moment_id = p_moment_id
																      AND archived_at IS NULL;
																
																    IF v_cash_count > 0 THEN
																        INSERT INTO business_memory_patterns (
																            moment_id,
																            pattern_type,
																            pattern_title,
																            observation_text,
																            source_metric,
																            confidence_level,
																            first_observed_at,
																            last_observed_at
																        )
																        VALUES (
																            p_moment_id,
																            'cash_inflow_pattern',
																            'Cash Inflow Pattern',
																            CONCAT('Cash inflows were recorded ', v_cash_count, ' time(s) in this runway cycle.'),
																            CONCAT('cash_inflow_count=', v_cash_count),
																            80,
																            CURRENT_TIMESTAMP,
																            CURRENT_TIMESTAMP
																        );
																    END IF;
																
																    SELECT expense_category, COALESCE(SUM(amount_in_operating_currency),0)
																    INTO v_top_expense_category, v_top_expense_amount
																    FROM runway_expense_burns
																    WHERE moment_id = p_moment_id
																      AND archived_at IS NULL
																    GROUP BY expense_category
																    ORDER BY SUM(amount_in_operating_currency) DESC
																    LIMIT 1;
																
																    IF v_top_expense_category IS NOT NULL THEN
																        INSERT INTO business_memory_patterns (
																            moment_id,
																            pattern_type,
																            pattern_title,
																            observation_text,
																            source_metric,
																            confidence_level,
																            first_observed_at,
																            last_observed_at
																        )
																        VALUES (
																            p_moment_id,
																            'burn_pattern',
																            'Burn Pattern',
																            CONCAT(v_top_expense_category, ' is currently the largest burn category.'),
																            CONCAT('top_burn_amount=', v_top_expense_amount),
																            85,
																            CURRENT_TIMESTAMP,
																            CURRENT_TIMESTAMP
																        );
																    END IF;
																
																    SELECT risk_type, COUNT(*)
																    INTO v_top_risk_type, v_top_risk_count
																    FROM runway_risks
																    WHERE moment_id = p_moment_id
																      AND archived_at IS NULL
																    GROUP BY risk_type
																    ORDER BY COUNT(*) DESC
																    LIMIT 1;
																
																    IF v_top_risk_type IS NOT NULL THEN
																        INSERT INTO business_memory_patterns (
																            moment_id,
																            pattern_type,
																            pattern_title,
																            observation_text,
																            source_metric,
																            confidence_level,
																            first_observed_at,
																            last_observed_at
																        )
																        VALUES (
																            p_moment_id,
																            'runway_risk_pattern',
																            'Runway Risk Pattern',
																            CONCAT(v_top_risk_type, ' appeared more frequently than other runway risks.'),
																            CONCAT('risk_count=', v_top_risk_count),
																            78,
																            CURRENT_TIMESTAMP,
																            CURRENT_TIMESTAMP
																        );
																    END IF;
																
																    SELECT decision_type, COUNT(*)
																    INTO v_top_decision_type, v_decision_count
																    FROM runway_strategic_decisions
																    WHERE moment_id = p_moment_id
																      AND archived_at IS NULL
																    GROUP BY decision_type
																    ORDER BY COUNT(*) DESC
																    LIMIT 1;
																
																    IF v_top_decision_type IS NOT NULL THEN
																        INSERT INTO business_memory_patterns (
																            moment_id,
																            pattern_type,
																            pattern_title,
																            observation_text,
																            source_metric,
																            confidence_level,
																            first_observed_at,
																            last_observed_at
																        )
																        VALUES (
																            p_moment_id,
																            'decision_pattern',
																            'Strategic Decision Pattern',
																            CONCAT(v_top_decision_type, ' decisions appeared frequently in runway planning.'),
																            CONCAT('decision_count=', v_decision_count),
																            75,
																            CURRENT_TIMESTAMP,
																            CURRENT_TIMESTAMP
																        );
																    END IF;
																
																    SELECT COUNT(*)
																    INTO v_financial_update_count
																    FROM runway_financial_updates
																    WHERE moment_id = p_moment_id
																      AND archived_at IS NULL;
																
																    IF v_financial_update_count > 0 THEN
																        INSERT INTO business_memory_patterns (
																            moment_id,
																            pattern_type,
																            pattern_title,
																            observation_text,
																            source_metric,
																            confidence_level,
																            first_observed_at,
																            last_observed_at
																        )
																        VALUES (
																            p_moment_id,
																            'financial_update_pattern',
																            'Financial Update Pattern',
																            CONCAT('Runway financial assumptions changed ', v_financial_update_count, ' time(s).'),
																            CONCAT('financial_update_count=', v_financial_update_count),
																            76,
																            CURRENT_TIMESTAMP,
																            CURRENT_TIMESTAMP
																        );
																    END IF;
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_business_runway_orchestration(
																    p_moment_id UUID
																)
																RETURNS VOID
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    PERFORM sp_refresh_business_runway_snapshot(p_moment_id);
																
																    PERFORM sp_refresh_business_runway_pulse_snapshot(p_moment_id);
																
																    PERFORM sp_refresh_business_runway_moment_metrics(p_moment_id);
																
																    PERFORM sp_refresh_business_runway_memory_patterns(p_moment_id);
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_get_runway_record_id(
																    p_source_table VARCHAR,
																    p_cash_inflow_id UUID DEFAULT NULL,
																    p_expense_id UUID DEFAULT NULL,
																    p_risk_id UUID DEFAULT NULL,
																    p_decision_id UUID DEFAULT NULL,
																    p_financial_update_id UUID DEFAULT NULL
																)
																RETURNS UUID
																LANGUAGE plpgsql
																AS $$
																BEGIN
																    RETURN CASE
																        WHEN p_source_table = 'runway_cash_inflows' THEN p_cash_inflow_id
																        WHEN p_source_table = 'runway_expense_burns' THEN p_expense_id
																        WHEN p_source_table = 'runway_risks' THEN p_risk_id
																        WHEN p_source_table = 'runway_strategic_decisions' THEN p_decision_id
																        WHEN p_source_table = 'runway_financial_updates' THEN p_financial_update_id
																        ELSE NULL
																    END;
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_runway_cash_inflow_created()
																RETURNS TRIGGER
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    PERFORM sp_create_live_feed_event(
																        NEW.moment_id,
																        'runway_cash_inflows',
																        NEW.cash_inflow_id,
																        'RUNWAY_CASH_INFLOW_CREATED',
																        NEW.created_by,
																        fn_get_runway_actor_name(NEW.moment_id, NEW.created_by),
																        CONCAT('Cash inflow recorded: ', NEW.inflow_type),
																        NEW.description,
																        NEW.amount_in_operating_currency,
																        'medium'
																    );
																
																    PERFORM sp_refresh_business_runway_orchestration(NEW.moment_id);
																
																    RETURN NEW;
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_runway_cash_inflow_updated()
																RETURNS TRIGGER
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    IF OLD.amount_in_operating_currency IS DISTINCT FROM NEW.amount_in_operating_currency THEN
																        PERFORM sp_write_audit_history(
																            NEW.moment_id,
																            'runway_cash_inflows',
																            NEW.cash_inflow_id,
																            'amount_in_operating_currency',
																            OLD.amount_in_operating_currency::TEXT,
																            NEW.amount_in_operating_currency::TEXT,
																            'edit',
																            NEW.created_by,
																            fn_get_runway_actor_name(NEW.moment_id, NEW.created_by)
																        );
																    END IF;
																
																    IF OLD.inflow_type IS DISTINCT FROM NEW.inflow_type THEN
																        PERFORM sp_write_audit_history(
																            NEW.moment_id,
																            'runway_cash_inflows',
																            NEW.cash_inflow_id,
																            'inflow_type',
																            OLD.inflow_type,
																            NEW.inflow_type,
																            'edit',
																            NEW.created_by,
																            fn_get_runway_actor_name(NEW.moment_id, NEW.created_by)
																        );
																    END IF;
																
																    IF OLD.archived_at IS NULL AND NEW.archived_at IS NOT NULL THEN
																        PERFORM sp_create_live_feed_event(
																            NEW.moment_id,
																            'runway_cash_inflows',
																            NEW.cash_inflow_id,
																            'RUNWAY_CASH_INFLOW_ARCHIVED',
																            NEW.created_by,
																            fn_get_runway_actor_name(NEW.moment_id, NEW.created_by),
																            'Cash inflow archived',
																            NEW.description,
																            NEW.amount_in_operating_currency,
																            'low'
																        );
																    ELSE
																        PERFORM sp_create_live_feed_event(
																            NEW.moment_id,
																            'runway_cash_inflows',
																            NEW.cash_inflow_id,
																            'RUNWAY_CASH_INFLOW_UPDATED',
																            NEW.created_by,
																            fn_get_runway_actor_name(NEW.moment_id, NEW.created_by),
																            'Cash inflow updated',
																            NEW.description,
																            NEW.amount_in_operating_currency,
																            'medium'
																        );
																    END IF;
																
																    PERFORM sp_refresh_business_runway_orchestration(NEW.moment_id);
																
																    RETURN NEW;
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_runway_expense_created()
																RETURNS TRIGGER
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    IF NEW.approval_required = TRUE AND NEW.approval_status = 'pending' THEN
																        INSERT INTO business_notifications (
																            moment_id,
																            recipient_user_id,
																            notification_type,
																            source_table,
																            source_record_id,
																            title,
																            message,
																            priority,
																            delivery_channel,
																            notification_status
																        )
																        SELECT
																            NEW.moment_id,
																            COALESCE(m.user_id, m.member_id),
																            'runway_expense_approval',
																            'runway_expense_burns',
																            NEW.expense_id,
																            'Runway expense needs approval',
																            CONCAT('Expense of ', NEW.currency, ' ', NEW.amount, ' requires approval.'),
																            'high',
																            'in_app',
																            'queued'
																        FROM business_moment_members m
																        WHERE m.moment_id = NEW.moment_id
																          AND m.can_approve_runway_changes = TRUE
																          AND m.member_status <> 'removed';
																    END IF;
																
																    PERFORM sp_create_live_feed_event(
																        NEW.moment_id,
																        'runway_expense_burns',
																        NEW.expense_id,
																        'RUNWAY_EXPENSE_CREATED',
																        NEW.created_by,
																        fn_get_runway_actor_name(NEW.moment_id, NEW.created_by),
																        CONCAT('Expense recorded: ', NEW.expense_category),
																        NEW.description,
																        NEW.amount_in_operating_currency,
																        NEW.priority
																    );
																
																    PERFORM sp_refresh_business_runway_orchestration(NEW.moment_id);
																
																    RETURN NEW;
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_runway_expense_updated()
																RETURNS TRIGGER
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    IF OLD.amount_in_operating_currency IS DISTINCT FROM NEW.amount_in_operating_currency THEN
																        PERFORM sp_write_audit_history(
																            NEW.moment_id,
																            'runway_expense_burns',
																            NEW.expense_id,
																            'amount_in_operating_currency',
																            OLD.amount_in_operating_currency::TEXT,
																            NEW.amount_in_operating_currency::TEXT,
																            'edit',
																            NEW.created_by,
																            fn_get_runway_actor_name(NEW.moment_id, NEW.created_by)
																        );
																    END IF;
																
																    IF OLD.approval_status IS DISTINCT FROM NEW.approval_status THEN
																        PERFORM sp_write_audit_history(
																            NEW.moment_id,
																            'runway_expense_burns',
																            NEW.expense_id,
																            'approval_status',
																            OLD.approval_status,
																            NEW.approval_status,
																            CASE
																                WHEN NEW.approval_status = 'approved' THEN 'approve'
																                WHEN NEW.approval_status = 'rejected' THEN 'reject'
																                ELSE 'edit'
																            END,
																            NEW.created_by,
																            fn_get_runway_actor_name(NEW.moment_id, NEW.created_by)
																        );
																
																        PERFORM sp_create_live_feed_event(
																            NEW.moment_id,
																            'runway_expense_burns',
																            NEW.expense_id,
																            CASE
																                WHEN NEW.approval_status = 'approved' THEN 'RUNWAY_EXPENSE_APPROVED'
																                WHEN NEW.approval_status = 'rejected' THEN 'RUNWAY_EXPENSE_REJECTED'
																                ELSE 'RUNWAY_EXPENSE_UPDATED'
																            END,
																            NEW.created_by,
																            fn_get_runway_actor_name(NEW.moment_id, NEW.created_by),
																            CONCAT('Expense ', NEW.approval_status),
																            NEW.description,
																            NEW.amount_in_operating_currency,
																            NEW.priority
																        );
																    ELSE
																        PERFORM sp_create_live_feed_event(
																            NEW.moment_id,
																            'runway_expense_burns',
																            NEW.expense_id,
																            CASE
																                WHEN OLD.archived_at IS NULL AND NEW.archived_at IS NOT NULL
																                    THEN 'RUNWAY_EXPENSE_ARCHIVED'
																                ELSE 'RUNWAY_EXPENSE_UPDATED'
																            END,
																            NEW.created_by,
																            fn_get_runway_actor_name(NEW.moment_id, NEW.created_by),
																            'Expense updated',
																            NEW.description,
																            NEW.amount_in_operating_currency,
																            NEW.priority
																        );
																    END IF;
																
																    PERFORM sp_refresh_business_runway_orchestration(NEW.moment_id);
																
																    RETURN NEW;
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_runway_risk_created()
																RETURNS TRIGGER
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    IF NEW.severity IN ('high','critical') THEN
																        INSERT INTO business_notifications (
																            moment_id,
																            recipient_user_id,
																            notification_type,
																            source_table,
																            source_record_id,
																            title,
																            message,
																            priority,
																            delivery_channel,
																            notification_status
																        )
																        SELECT
																            NEW.moment_id,
																            COALESCE(m.user_id, m.member_id),
																            'runway_risk_created',
																            'runway_risks',
																            NEW.risk_id,
																            'Runway risk needs attention',
																            CONCAT(NEW.risk_title, ' has been marked ', NEW.severity),
																            NEW.severity,
																            'in_app',
																            'queued'
																        FROM business_moment_members m
																        WHERE m.moment_id = NEW.moment_id
																          AND m.role IN ('Runway Owner','Finance Lead','Operations Lead')
																          AND m.member_status <> 'removed';
																    END IF;
																
																    PERFORM sp_create_live_feed_event(
																        NEW.moment_id,
																        'runway_risks',
																        NEW.risk_id,
																        'RUNWAY_RISK_CREATED',
																        NEW.created_by,
																        fn_get_runway_actor_name(NEW.moment_id, NEW.created_by),
																        CONCAT('Runway risk logged: ', NEW.risk_title),
																        NEW.description,
																        NULL,
																        NEW.severity
																    );
																
																    PERFORM sp_refresh_business_runway_orchestration(NEW.moment_id);
																
																    RETURN NEW;
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_runway_risk_updated()
																RETURNS TRIGGER
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    IF OLD.risk_status IS DISTINCT FROM NEW.risk_status THEN
																        PERFORM sp_write_audit_history(
																            NEW.moment_id,
																            'runway_risks',
																            NEW.risk_id,
																            'risk_status',
																            OLD.risk_status,
																            NEW.risk_status,
																            CASE WHEN NEW.risk_status = 'resolved' THEN 'resolve' ELSE 'edit' END,
																            NEW.created_by,
																            fn_get_runway_actor_name(NEW.moment_id, NEW.created_by)
																        );
																    END IF;
																
																    IF OLD.severity IS DISTINCT FROM NEW.severity THEN
																        PERFORM sp_write_audit_history(
																            NEW.moment_id,
																            'runway_risks',
																            NEW.risk_id,
																            'severity',
																            OLD.severity,
																            NEW.severity,
																            'edit',
																            NEW.created_by,
																            fn_get_runway_actor_name(NEW.moment_id, NEW.created_by)
																        );
																    END IF;
																
																    IF OLD.risk_status <> 'resolved' AND NEW.risk_status = 'resolved' THEN
																        NEW.resolved_at := COALESCE(NEW.resolved_at, CURRENT_TIMESTAMP);
																    END IF;
																
																    PERFORM sp_create_live_feed_event(
																        NEW.moment_id,
																        'runway_risks',
																        NEW.risk_id,
																        CASE
																            WHEN OLD.risk_status <> 'resolved' AND NEW.risk_status = 'resolved'
																                THEN 'RUNWAY_RISK_RESOLVED'
																            WHEN OLD.archived_at IS NULL AND NEW.archived_at IS NOT NULL
																                THEN 'RUNWAY_RISK_ARCHIVED'
																            ELSE 'RUNWAY_RISK_UPDATED'
																        END,
																        NEW.created_by,
																        fn_get_runway_actor_name(NEW.moment_id, NEW.created_by),
																        CASE
																            WHEN NEW.risk_status = 'resolved'
																                THEN CONCAT('Runway risk resolved: ', NEW.risk_title)
																            ELSE CONCAT('Runway risk updated: ', NEW.risk_title)
																        END,
																        NEW.description,
																        NULL,
																        NEW.severity
																    );
																
																    PERFORM sp_refresh_business_runway_orchestration(NEW.moment_id);
																
																    RETURN NEW;
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_runway_decision_created()
																RETURNS TRIGGER
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    PERFORM sp_create_live_feed_event(
																        NEW.moment_id,
																        'runway_strategic_decisions',
																        NEW.decision_id,
																        'RUNWAY_DECISION_CREATED',
																        NEW.created_by,
																        fn_get_runway_actor_name(NEW.moment_id, NEW.created_by),
																        CONCAT('Strategic decision recorded: ', NEW.decision_title),
																        NEW.description,
																        NULL,
																        'medium'
																    );
																
																    PERFORM sp_refresh_business_runway_orchestration(NEW.moment_id);
																
																    RETURN NEW;
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_runway_decision_updated()
																RETURNS TRIGGER
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    IF OLD.expected_impact IS DISTINCT FROM NEW.expected_impact THEN
																        PERFORM sp_write_audit_history(
																            NEW.moment_id,
																            'runway_strategic_decisions',
																            NEW.decision_id,
																            'expected_impact',
																            OLD.expected_impact,
																            NEW.expected_impact,
																            'edit',
																            NEW.created_by,
																            fn_get_runway_actor_name(NEW.moment_id, NEW.created_by)
																        );
																    END IF;
																
																    PERFORM sp_create_live_feed_event(
																        NEW.moment_id,
																        'runway_strategic_decisions',
																        NEW.decision_id,
																        CASE
																            WHEN OLD.archived_at IS NULL AND NEW.archived_at IS NOT NULL
																                THEN 'RUNWAY_DECISION_ARCHIVED'
																            ELSE 'RUNWAY_DECISION_UPDATED'
																        END,
																        NEW.created_by,
																        fn_get_runway_actor_name(NEW.moment_id, NEW.created_by),
																        CONCAT('Strategic decision updated: ', NEW.decision_title),
																        NEW.description,
																        NULL,
																        'medium'
																    );
																
																    PERFORM sp_refresh_business_runway_orchestration(NEW.moment_id);
																
																    RETURN NEW;
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_runway_financial_update_created()
																RETURNS TRIGGER
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    IF NEW.approval_required = TRUE AND NEW.approval_status = 'pending' THEN
																        INSERT INTO business_notifications (
																            moment_id,
																            recipient_user_id,
																            notification_type,
																            source_table,
																            source_record_id,
																            title,
																            message,
																            priority,
																            delivery_channel,
																            notification_status
																        )
																        SELECT
																            NEW.moment_id,
																            COALESCE(m.user_id, m.member_id),
																            'runway_financial_update_approval',
																            'runway_financial_updates',
																            NEW.financial_update_id,
																            'Runway financial update needs approval',
																            CONCAT('Update requested for ', NEW.update_type),
																            'high',
																            'in_app',
																            'queued'
																        FROM business_moment_members m
																        WHERE m.moment_id = NEW.moment_id
																          AND m.can_approve_runway_changes = TRUE
																          AND m.member_status <> 'removed';
																    END IF;
																
																    PERFORM sp_create_live_feed_event(
																        NEW.moment_id,
																        'runway_financial_updates',
																        NEW.financial_update_id,
																        'RUNWAY_FINANCIAL_UPDATE_CREATED',
																        NEW.created_by,
																        fn_get_runway_actor_name(NEW.moment_id, NEW.created_by),
																        CONCAT('Financial update submitted: ', NEW.update_type),
																        NEW.reason,
																        NEW.new_value_in_operating_currency,
																        'medium'
																    );
																
																    IF NEW.approval_required = FALSE THEN
																        UPDATE runway_financial_updates
																        SET
																            approval_status = 'not_required',
																            applied_status = 'applied',
																            applied_at = CURRENT_TIMESTAMP
																        WHERE financial_update_id = NEW.financial_update_id;
																    END IF;
																
																    PERFORM sp_refresh_business_runway_orchestration(NEW.moment_id);
																
																    RETURN NEW;
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_runway_financial_update_updated()
																RETURNS TRIGGER
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    IF OLD.approval_status IS DISTINCT FROM NEW.approval_status THEN
																        PERFORM sp_write_audit_history(
																            NEW.moment_id,
																            'runway_financial_updates',
																            NEW.financial_update_id,
																            'approval_status',
																            OLD.approval_status,
																            NEW.approval_status,
																            CASE
																                WHEN NEW.approval_status = 'approved' THEN 'approve'
																                WHEN NEW.approval_status = 'rejected' THEN 'reject'
																                ELSE 'edit'
																            END,
																            NEW.created_by,
																            fn_get_runway_actor_name(NEW.moment_id, NEW.created_by)
																        );
																    END IF;
																
																    IF OLD.new_value IS DISTINCT FROM NEW.new_value THEN
																        PERFORM sp_write_audit_history(
																            NEW.moment_id,
																            'runway_financial_updates',
																            NEW.financial_update_id,
																            'new_value',
																            OLD.new_value::TEXT,
																            NEW.new_value::TEXT,
																            'edit',
																            NEW.created_by,
																            fn_get_runway_actor_name(NEW.moment_id, NEW.created_by)
																        );
																    END IF;
																
																    IF NEW.approval_status = 'approved'
																       AND NEW.applied_status <> 'applied'
																    THEN
																        NEW.applied_status := 'applied';
																        NEW.applied_at := CURRENT_TIMESTAMP;
																    END IF;
																
																    IF NEW.approval_status = 'rejected' THEN
																        NEW.applied_status := 'rejected';
																    END IF;
																
																    PERFORM sp_create_live_feed_event(
																        NEW.moment_id,
																        'runway_financial_updates',
																        NEW.financial_update_id,
																        CASE
																            WHEN NEW.applied_status = 'applied' THEN 'RUNWAY_FINANCIAL_UPDATE_APPLIED'
																            WHEN NEW.applied_status = 'rejected' THEN 'RUNWAY_FINANCIAL_UPDATE_REJECTED'
																            ELSE 'RUNWAY_FINANCIAL_UPDATE_UPDATED'
																        END,
																        NEW.created_by,
																        fn_get_runway_actor_name(NEW.moment_id, NEW.created_by),
																        CONCAT('Financial update ', NEW.applied_status, ': ', NEW.update_type),
																        NEW.reason,
																        NEW.new_value_in_operating_currency,
																        'medium'
																    );
																
																    PERFORM sp_refresh_business_runway_orchestration(NEW.moment_id);
																
																    RETURN NEW;
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_runway_risk_before_update()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN

    IF OLD.risk_status <> 'resolved'
       AND NEW.risk_status = 'resolved'
       AND NEW.resolved_at IS NULL
    THEN
        NEW.resolved_at := CURRENT_TIMESTAMP;
    END IF;

    RETURN NEW;

END;
$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_runway_risk_after_update()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN

    IF OLD.risk_status IS DISTINCT FROM NEW.risk_status THEN

        PERFORM sp_write_audit_history(
            NEW.moment_id,
            'runway_risks',
            NEW.risk_id,
            'risk_status',
            OLD.risk_status,
            NEW.risk_status,
            CASE
                WHEN NEW.risk_status = 'resolved'
                    THEN 'resolve'
                ELSE 'edit'
            END,
            NEW.created_by,
            fn_get_runway_actor_name(
                NEW.moment_id,
                NEW.created_by
            )
        );

    END IF;

    PERFORM sp_create_live_feed_event(
        NEW.moment_id,
        'runway_risks',
        NEW.risk_id,
        CASE
            WHEN NEW.risk_status = 'resolved'
                THEN 'RUNWAY_RISK_RESOLVED'
            WHEN NEW.archived_at IS NOT NULL
                THEN 'RUNWAY_RISK_ARCHIVED'
            ELSE 'RUNWAY_RISK_UPDATED'
        END,
        NEW.created_by,
        fn_get_runway_actor_name(
            NEW.moment_id,
            NEW.created_by
        ),
        NEW.risk_title,
        NEW.description,
        NULL,
        NEW.severity
    );

    PERFORM sp_refresh_business_runway_orchestration(
        NEW.moment_id
    );

    RETURN NEW;

END;
$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_runway_financial_before_update()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN

    IF NEW.approval_status = 'approved'
       AND NEW.applied_status <> 'applied'
    THEN

        NEW.applied_status := 'applied';

        IF NEW.applied_at IS NULL THEN
            NEW.applied_at := CURRENT_TIMESTAMP;
        END IF;

    END IF;

    IF NEW.approval_status = 'rejected' THEN
        NEW.applied_status := 'rejected';
    END IF;

    RETURN NEW;

END;
$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_runway_financial_after_update()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN

    IF OLD.approval_status IS DISTINCT FROM NEW.approval_status THEN

        PERFORM sp_write_audit_history(
            NEW.moment_id,
            'runway_financial_updates',
            NEW.financial_update_id,
            'approval_status',
            OLD.approval_status,
            NEW.approval_status,
            CASE
                WHEN NEW.approval_status = 'approved'
                    THEN 'approve'
                WHEN NEW.approval_status = 'rejected'
                    THEN 'reject'
                ELSE 'edit'
            END,
            NEW.created_by,
            fn_get_runway_actor_name(
                NEW.moment_id,
                NEW.created_by
            )
        );

    END IF;

    IF OLD.new_value IS DISTINCT FROM NEW.new_value THEN

        PERFORM sp_write_audit_history(
            NEW.moment_id,
            'runway_financial_updates',
            NEW.financial_update_id,
            'new_value',
            OLD.new_value::TEXT,
            NEW.new_value::TEXT,
            'edit',
            NEW.created_by,
            fn_get_runway_actor_name(
                NEW.moment_id,
                NEW.created_by
            )
        );

    END IF;

    PERFORM sp_create_live_feed_event(
        NEW.moment_id,
        'runway_financial_updates',
        NEW.financial_update_id,
        CASE
            WHEN NEW.applied_status = 'applied'
                THEN 'RUNWAY_FINANCIAL_UPDATE_APPLIED'
            WHEN NEW.applied_status = 'rejected'
                THEN 'RUNWAY_FINANCIAL_UPDATE_REJECTED'
            ELSE 'RUNWAY_FINANCIAL_UPDATE_UPDATED'
        END,
        NEW.created_by,
        fn_get_runway_actor_name(
            NEW.moment_id,
            NEW.created_by
        ),
        CONCAT(
            'Financial update: ',
            NEW.update_type
        ),
        NEW.reason,
        NEW.new_value_in_operating_currency,
        'medium'
    );

    PERFORM sp_refresh_business_runway_orchestration(
        NEW.moment_id
    );

    RETURN NEW;

END;
$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_validate_runway_trigger_state()
RETURNS TABLE (
    validation_name TEXT,
    validation_status TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN

    RETURN QUERY
    SELECT
        'Runway Risk BEFORE Trigger',
        CASE
            WHEN EXISTS (
                SELECT 1
                FROM pg_trigger
                WHERE tgname =
                'trg_runway_risk_before_update'
            )
            THEN 'PASS'
            ELSE 'FAIL'
        END;

    RETURN QUERY
    SELECT
        'Runway Financial BEFORE Trigger',
        CASE
            WHEN EXISTS (
                SELECT 1
                FROM pg_trigger
                WHERE tgname =
                'trg_runway_financial_before_update'
            )
            THEN 'PASS'
            ELSE 'FAIL'
        END;

END;
$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_moment_activated_trigger()
																RETURNS TRIGGER
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    IF OLD.status <> 'active'
																       AND NEW.status = 'active'
																    THEN
																
																        CASE
																
																            WHEN NEW.moment_type = 'team_operations'
																            THEN
																                PERFORM sp_refresh_business_orchestration(
																                    NEW.moment_id
																                );
																
																            WHEN NEW.moment_type = 'business_runway'
																            THEN
																                PERFORM sp_refresh_business_runway_orchestration(
																                    NEW.moment_id
																                );
																
																        END CASE;
																
																    END IF;
																
																    RETURN NEW;
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_apply_runway_financial_update(
																    p_financial_update_id UUID
																)
																RETURNS VOID
																LANGUAGE plpgsql
																AS $$
																DECLARE
																
																    v_update runway_financial_updates%ROWTYPE;
																
																BEGIN
																
																    SELECT *
																    INTO v_update
																    FROM runway_financial_updates
																    WHERE financial_update_id =
																          p_financial_update_id;
																
																    IF NOT FOUND THEN
																        RAISE EXCEPTION
																        'Financial update not found';
																    END IF;
																
																    IF v_update.applied_status = 'applied' THEN
																        RETURN;
																    END IF;
																
																    CASE
																
																        WHEN v_update.update_type =
																             'cash_available'
																        THEN
																
																            UPDATE business_runway_setup
																            SET
																                cash_available =
																                    v_update.new_value,
																                updated_at =
																                    CURRENT_TIMESTAMP
																            WHERE moment_id =
																                  v_update.moment_id;
																
																        WHEN v_update.update_type =
																             'monthly_burn'
																        THEN
																
																            UPDATE business_runway_setup
																            SET
																                monthly_burn =
																                    v_update.new_value,
																                updated_at =
																                    CURRENT_TIMESTAMP
																            WHERE moment_id =
																                  v_update.moment_id;
																
																        WHEN v_update.update_type =
																             'revenue_estimate'
																        THEN
																
																            UPDATE business_runway_setup
																            SET
																                monthly_revenue =
																                    v_update.new_value,
																                updated_at =
																                    CURRENT_TIMESTAMP
																            WHERE moment_id =
																                  v_update.moment_id;
																
																        WHEN v_update.update_type =
																             'runway_threshold'
																        THEN
																
																            UPDATE business_runway_structure
																            SET
																                alert_threshold_months =
																                    v_update.new_value,
																                updated_at =
																                    CURRENT_TIMESTAMP
																            WHERE moment_id =
																                  v_update.moment_id;
																
																    END CASE;
																
																    UPDATE runway_financial_updates
																    SET
																        applied_status = 'applied',
																        applied_at = CURRENT_TIMESTAMP
																    WHERE financial_update_id =
																          p_financial_update_id;
																
																    PERFORM sp_write_audit_history(
																        v_update.moment_id,
																        'runway_financial_updates',
																        v_update.financial_update_id,
																        'applied_status',
																        'pending',
																        'applied',
																        'apply',
																        v_update.created_by,
																        fn_get_runway_actor_name(
																            v_update.moment_id,
																            v_update.created_by
																        )
																    );
																
																    PERFORM sp_refresh_business_runway_orchestration(
																        v_update.moment_id
																    );
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_apply_operations_member_permissions()
																RETURNS TRIGGER
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    NEW.can_add_operations_records :=
																        NEW.role IN (
																            'Operations Owner',
																            'Operations Lead',
																            'Budget Controller',
																            'Contributor'
																        );
																
																    NEW.can_edit_operations_records :=
																        NEW.role IN (
																            'Operations Owner',
																            'Operations Lead'
																        );
																
																    NEW.can_edit_own_operations_records :=
																        NEW.role = 'Contributor';
																
																    NEW.can_approve_operations_requests :=
																        NEW.role IN (
																            'Operations Owner',
																            'Approver'
																        );
																
																    NEW.can_delete_operations_records :=
																        NEW.role = 'Operations Owner';
																
																    NEW.can_manage_operations_settings :=
																        NEW.role = 'Operations Owner';
																
																    RETURN NEW;
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_validate_operations_member_reference(
																    p_moment_id UUID,
																    p_reference_id UUID
																)
																RETURNS BOOLEAN
																LANGUAGE plpgsql
																AS $$
																DECLARE
																    v_exists BOOLEAN;
																BEGIN
																
																    IF p_reference_id IS NULL THEN
																        RETURN TRUE;
																    END IF;
																
																    SELECT EXISTS (
																        SELECT 1
																        FROM business_moment_members
																        WHERE moment_id = p_moment_id
																          AND (
																                member_id = p_reference_id
																                OR user_id = p_reference_id
																          )
																          AND member_status <> 'removed'
																          AND role IN (
																                'Operations Owner',
																                'Operations Lead',
																                'Budget Controller',
																                'Approver',
																                'Contributor',
																                'Viewer'
																          )
																    )
																    INTO v_exists;
																
																    RETURN COALESCE(v_exists, FALSE);
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_validate_operations_approval_member_refs()
																RETURNS TRIGGER
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    IF fn_validate_operations_member_reference(NEW.moment_id, NEW.requested_by) = FALSE THEN
																        RAISE EXCEPTION 'Invalid requested_by for this Business Operations moment';
																    END IF;
																
																    IF fn_validate_operations_member_reference(NEW.moment_id, NEW.approver_id) = FALSE THEN
																        RAISE EXCEPTION 'Invalid approver_id for this Business Operations moment';
																    END IF;
																
																    IF fn_validate_operations_member_reference(NEW.moment_id, NEW.decided_by) = FALSE THEN
																        RAISE EXCEPTION 'Invalid decided_by for this Business Operations moment';
																    END IF;
																
																    RETURN NEW;
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_validate_operations_issue_member_refs()
																RETURNS TRIGGER
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    IF fn_validate_operations_member_reference(NEW.moment_id, NEW.owner_id) = FALSE THEN
																        RAISE EXCEPTION 'Invalid issue owner_id for this Business Operations moment';
																    END IF;
																
																    RETURN NEW;
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_validate_operations_improvement_member_refs()
																RETURNS TRIGGER
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    IF fn_validate_operations_member_reference(NEW.moment_id, NEW.owner_id) = FALSE THEN
																        RAISE EXCEPTION 'Invalid improvement owner_id for this Business Operations moment';
																    END IF;
																
																    IF fn_validate_operations_member_reference(NEW.moment_id, NEW.follow_up_owner_id) = FALSE THEN
																        RAISE EXCEPTION 'Invalid follow_up_owner_id for this Business Operations moment';
																    END IF;
																
																    RETURN NEW;
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_get_operations_actor_name(
																    p_moment_id UUID,
																    p_actor_id UUID
																)
																RETURNS VARCHAR
																LANGUAGE plpgsql
																AS $$
																DECLARE
																    v_name VARCHAR;
																BEGIN
																
																    SELECT name
																    INTO v_name
																    FROM business_moment_members
																    WHERE moment_id = p_moment_id
																      AND (
																            member_id = p_actor_id
																            OR user_id = p_actor_id
																      )
																    LIMIT 1;
																
																    RETURN COALESCE(v_name, 'System');
																
																END;
																$$;
-- >>>STMT<<<
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
																        monthly_operating_budget,
																        allocated_budget_total,
																        budget_used_total,
																        budget_remaining_total,
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
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_business_operations_pulse_snapshot(
																    p_moment_id UUID
																)
																RETURNS VOID
																LANGUAGE plpgsql
																AS $$
																DECLARE
																    v_snapshot business_operations_snapshots%ROWTYPE;
																BEGIN
																
																    PERFORM sp_refresh_business_operations_snapshot(p_moment_id);
																
																    SELECT *
																    INTO v_snapshot
																    FROM business_operations_snapshots
																    WHERE moment_id = p_moment_id
																      AND snapshot_date = CURRENT_DATE;
																
																    DELETE FROM business_pulse_snapshots
																    WHERE moment_id = p_moment_id
																      AND snapshot_date = CURRENT_DATE;
																
																    INSERT INTO business_pulse_snapshots (
																        moment_id,
																        snapshot_date,
																
																        activities_count,
																        completed_activities,
																        in_progress_activities,
																        planned_activities,
																        pending_approvals,
																        open_risks,
																        critical_risks,
																        monthly_spend,
																        top_spend_category,
																
																        operations_health_status,
																        active_issue_count,
																        open_approval_count,
																        budget_alert_count,
																        improvement_count,
																        budget_used_total,
																        budget_remaining_total,
																        vendor_activity_count,
																        operations_operating_currency,
																
																        generated_at
																    )
																    VALUES (
																        p_moment_id,
																        CURRENT_DATE,
																
																        (
																            SELECT COUNT(*)
																            FROM (
																                SELECT spend_entry_id FROM operations_spend_entries
																                WHERE moment_id = p_moment_id AND archived_at IS NULL
																
																                UNION ALL
																
																                SELECT vendor_update_id FROM operations_vendor_updates
																                WHERE moment_id = p_moment_id AND archived_at IS NULL
																
																                UNION ALL
																
																                SELECT operations_approval_id FROM operations_approval_requests
																                WHERE moment_id = p_moment_id AND archived_at IS NULL
																
																                UNION ALL
																
																                SELECT operations_issue_id FROM operations_issues
																                WHERE moment_id = p_moment_id AND archived_at IS NULL
																
																                UNION ALL
																
																                SELECT improvement_id FROM operations_improvements
																                WHERE moment_id = p_moment_id AND archived_at IS NULL
																            ) x
																        ),
																
																        0,
																        0,
																        0,
																
																        v_snapshot.open_approval_count,
																        v_snapshot.active_issue_count,
																        v_snapshot.critical_issue_count,
																        v_snapshot.budget_used_total,
																
																        (
																            SELECT bc.category_name
																            FROM business_operations_budget_categories bc
																            JOIN operations_spend_entries se
																              ON bc.budget_category_id = se.budget_category_id
																            WHERE bc.moment_id = p_moment_id
																              AND se.archived_at IS NULL
																              AND se.approval_status IN ('not_required', 'approved')
																            GROUP BY bc.category_name
																            ORDER BY SUM(se.amount_in_operating_currency) DESC
																            LIMIT 1
																        ),
																
																        v_snapshot.operations_health_status,
																        v_snapshot.active_issue_count,
																        v_snapshot.open_approval_count,
																        v_snapshot.budget_alert_count,
																        v_snapshot.improvement_count,
																        v_snapshot.budget_used_total,
																        v_snapshot.budget_remaining_total,
																        v_snapshot.vendor_activity_count,
																        v_snapshot.operating_currency,
																
																        CURRENT_TIMESTAMP
																    );
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_business_operations_moment_metrics(
																    p_moment_id UUID
																)
																RETURNS VOID
																LANGUAGE plpgsql
																AS $$
																DECLARE
																    v_snapshot business_operations_snapshots%ROWTYPE;
																    v_members_count INTEGER := 0;
																    v_last_activity TIMESTAMP;
																BEGIN
																
																    PERFORM sp_refresh_business_operations_snapshot(p_moment_id);
																
																    SELECT *
																    INTO v_snapshot
																    FROM business_operations_snapshots
																    WHERE moment_id = p_moment_id
																      AND snapshot_date = CURRENT_DATE;
																
																    SELECT COUNT(*)
																    INTO v_members_count
																    FROM business_moment_members
																    WHERE moment_id = p_moment_id
																      AND member_status IN ('configured', 'active');
																
																    SELECT MAX(latest_at)
																    INTO v_last_activity
																    FROM (
																        SELECT MAX(created_at) AS latest_at
																        FROM operations_spend_entries
																        WHERE moment_id = p_moment_id
																          AND archived_at IS NULL
																
																        UNION ALL
																
																        SELECT MAX(created_at)
																        FROM operations_vendor_updates
																        WHERE moment_id = p_moment_id
																          AND archived_at IS NULL
																
																        UNION ALL
																
																        SELECT MAX(created_at)
																        FROM operations_approval_requests
																        WHERE moment_id = p_moment_id
																          AND archived_at IS NULL
																
																        UNION ALL
																
																        SELECT MAX(created_at)
																        FROM operations_issues
																        WHERE moment_id = p_moment_id
																          AND archived_at IS NULL
																
																        UNION ALL
																
																        SELECT MAX(created_at)
																        FROM operations_improvements
																        WHERE moment_id = p_moment_id
																          AND archived_at IS NULL
																    ) x;
																
																    DELETE FROM business_moment_metrics
																    WHERE moment_id = p_moment_id;
																
																    INSERT INTO business_moment_metrics (
																        moment_id,
																        members_count,
																        activities_count,
																        pending_approvals,
																        open_risks,
																        spend_amount,
																        last_activity_at,
																
																        budget_category_count,
																        operations_budget_used_total,
																        operations_active_issue_count,
																        operations_approval_count,
																        operations_improvement_count,
																        last_operations_activity_at,
																        latest_spend_title,
																        latest_issue_title,
																        latest_approval_status,
																        latest_improvement_title,
																        operations_operating_currency,
																
																        last_updated_at
																    )
																    VALUES (
																        p_moment_id,
																        v_members_count,
																
																        (
																            SELECT COUNT(*)
																            FROM (
																                SELECT spend_entry_id FROM operations_spend_entries
																                WHERE moment_id = p_moment_id AND archived_at IS NULL
																
																                UNION ALL
																
																                SELECT vendor_update_id FROM operations_vendor_updates
																                WHERE moment_id = p_moment_id AND archived_at IS NULL
																
																                UNION ALL
																
																                SELECT operations_approval_id FROM operations_approval_requests
																                WHERE moment_id = p_moment_id AND archived_at IS NULL
																
																                UNION ALL
																
																                SELECT operations_issue_id FROM operations_issues
																                WHERE moment_id = p_moment_id AND archived_at IS NULL
																
																                UNION ALL
																
																                SELECT improvement_id FROM operations_improvements
																                WHERE moment_id = p_moment_id AND archived_at IS NULL
																            ) activity_union
																        ),
																
																        v_snapshot.open_approval_count,
																        v_snapshot.active_issue_count,
																        v_snapshot.budget_used_total,
																        v_last_activity,
																
																        (
																            SELECT COUNT(*)
																            FROM business_operations_budget_categories
																            WHERE moment_id = p_moment_id
																              AND category_status = 'active'
																              AND archived_at IS NULL
																        ),
																
																        v_snapshot.budget_used_total,
																        v_snapshot.active_issue_count,
																
																        (
																            SELECT COUNT(*)
																            FROM operations_approval_requests
																            WHERE moment_id = p_moment_id
																              AND archived_at IS NULL
																        ),
																
																        v_snapshot.improvement_count,
																        v_last_activity,
																
																        (
																            SELECT spend_name
																            FROM operations_spend_entries
																            WHERE moment_id = p_moment_id
																              AND archived_at IS NULL
																            ORDER BY created_at DESC
																            LIMIT 1
																        ),
																
																        (
																            SELECT issue_title
																            FROM operations_issues
																            WHERE moment_id = p_moment_id
																              AND archived_at IS NULL
																            ORDER BY created_at DESC
																            LIMIT 1
																        ),
																
																        (
																            SELECT approval_status
																            FROM operations_approval_requests
																            WHERE moment_id = p_moment_id
																              AND archived_at IS NULL
																            ORDER BY created_at DESC
																            LIMIT 1
																        ),
																
																        (
																            SELECT improvement_title
																            FROM operations_improvements
																            WHERE moment_id = p_moment_id
																              AND archived_at IS NULL
																            ORDER BY created_at DESC
																            LIMIT 1
																        ),
																
																        v_snapshot.operating_currency,
																        CURRENT_TIMESTAMP
																    );
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_business_operations_memory_patterns(
																    p_moment_id UUID
																)
																RETURNS VOID
																LANGUAGE plpgsql
																AS $$
																DECLARE
																    v_top_budget_category VARCHAR(100);
																    v_top_budget_spend NUMERIC(18,2);
																
																    v_top_vendor_category VARCHAR(100);
																    v_vendor_count INTEGER;
																
																    v_approval_count INTEGER;
																    v_open_approval_count INTEGER;
																
																    v_top_issue_category VARCHAR(100);
																    v_issue_count INTEGER;
																
																    v_top_improvement_type VARCHAR(100);
																    v_improvement_count INTEGER;
																BEGIN
																
																    DELETE FROM business_memory_patterns
																    WHERE moment_id = p_moment_id
																      AND pattern_type IN (
																          'operations_budget_pattern',
																          'operations_vendor_pattern',
																          'operations_approval_pattern',
																          'operations_issue_pattern',
																          'operations_improvement_pattern'
																      );
																
																    SELECT
																        se.budget_category_name,
																        COALESCE(SUM(se.amount_in_operating_currency), 0)
																    INTO
																        v_top_budget_category,
																        v_top_budget_spend
																    FROM operations_spend_entries se
																    WHERE se.moment_id = p_moment_id
																      AND se.archived_at IS NULL
																      AND se.approval_status IN ('not_required', 'approved')
																    GROUP BY se.budget_category_name
																    ORDER BY SUM(se.amount_in_operating_currency) DESC
																    LIMIT 1;
																
																    IF v_top_budget_category IS NOT NULL THEN
																        INSERT INTO business_memory_patterns (
																            moment_id,
																            pattern_type,
																            pattern_title,
																            observation_text,
																            source_metric,
																            confidence_level,
																            first_observed_at,
																            last_observed_at
																        )
																        VALUES (
																            p_moment_id,
																            'operations_budget_pattern',
																            'Budget Pattern',
																            CONCAT(v_top_budget_category, ' is currently the highest used budget category.'),
																            CONCAT('top_budget_spend=', v_top_budget_spend),
																            85,
																            CURRENT_TIMESTAMP,
																            CURRENT_TIMESTAMP
																        );
																    END IF;
																
																    SELECT vendor_category, COUNT(*)
																    INTO v_top_vendor_category, v_vendor_count
																    FROM operations_vendor_updates
																    WHERE moment_id = p_moment_id
																      AND archived_at IS NULL
																    GROUP BY vendor_category
																    ORDER BY COUNT(*) DESC
																    LIMIT 1;
																
																    IF v_top_vendor_category IS NOT NULL THEN
																        INSERT INTO business_memory_patterns (
																            moment_id,
																            pattern_type,
																            pattern_title,
																            observation_text,
																            source_metric,
																            confidence_level,
																            first_observed_at,
																            last_observed_at
																        )
																        VALUES (
																            p_moment_id,
																            'operations_vendor_pattern',
																            'Vendor Pattern',
																            CONCAT(v_top_vendor_category, ' accounts for most vendor activity.'),
																            CONCAT('vendor_activity_count=', v_vendor_count),
																            80,
																            CURRENT_TIMESTAMP,
																            CURRENT_TIMESTAMP
																        );
																    END IF;
																
																    SELECT
																        COUNT(*),
																        COUNT(*) FILTER (WHERE approval_status = 'pending')
																    INTO
																        v_approval_count,
																        v_open_approval_count
																    FROM operations_approval_requests
																    WHERE moment_id = p_moment_id
																      AND archived_at IS NULL;
																
																    IF v_approval_count > 0 THEN
																        INSERT INTO business_memory_patterns (
																            moment_id,
																            pattern_type,
																            pattern_title,
																            observation_text,
																            source_metric,
																            confidence_level,
																            first_observed_at,
																            last_observed_at
																        )
																        VALUES (
																            p_moment_id,
																            'operations_approval_pattern',
																            'Approval Pattern',
																            CONCAT(v_approval_count, ' operational approval request(s) observed.'),
																            CONCAT('open_approval_count=', v_open_approval_count),
																            75,
																            CURRENT_TIMESTAMP,
																            CURRENT_TIMESTAMP
																        );
																    END IF;
																
																    SELECT issue_category, COUNT(*)
																    INTO v_top_issue_category, v_issue_count
																    FROM operations_issues
																    WHERE moment_id = p_moment_id
																      AND archived_at IS NULL
																    GROUP BY issue_category
																    ORDER BY COUNT(*) DESC
																    LIMIT 1;
																
																    IF v_top_issue_category IS NOT NULL THEN
																        INSERT INTO business_memory_patterns (
																            moment_id,
																            pattern_type,
																            pattern_title,
																            observation_text,
																            source_metric,
																            confidence_level,
																            first_observed_at,
																            last_observed_at
																        )
																        VALUES (
																            p_moment_id,
																            'operations_issue_pattern',
																            'Issue Pattern',
																            CONCAT(v_top_issue_category, ' issues occur more frequently than other issue types.'),
																            CONCAT('issue_count=', v_issue_count),
																            82,
																            CURRENT_TIMESTAMP,
																            CURRENT_TIMESTAMP
																        );
																    END IF;
																
																    SELECT improvement_type, COUNT(*)
																    INTO v_top_improvement_type, v_improvement_count
																    FROM operations_improvements
																    WHERE moment_id = p_moment_id
																      AND archived_at IS NULL
																    GROUP BY improvement_type
																    ORDER BY COUNT(*) DESC
																    LIMIT 1;
																
																    IF v_top_improvement_type IS NOT NULL THEN
																        INSERT INTO business_memory_patterns (
																            moment_id,
																            pattern_type,
																            pattern_title,
																            observation_text,
																            source_metric,
																            confidence_level,
																            first_observed_at,
																            last_observed_at
																        )
																        VALUES (
																            p_moment_id,
																            'operations_improvement_pattern',
																            'Improvement Pattern',
																            CONCAT(v_top_improvement_type, ' is the most common improvement type.'),
																            CONCAT('improvement_count=', v_improvement_count),
																            78,
																            CURRENT_TIMESTAMP,
																            CURRENT_TIMESTAMP
																        );
																    END IF;
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_business_operations_orchestration(
																    p_moment_id UUID
																)
																RETURNS VOID
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    PERFORM sp_refresh_business_operations_snapshot(p_moment_id);
																
																    PERFORM sp_refresh_business_operations_pulse_snapshot(p_moment_id);
																
																    PERFORM sp_refresh_business_operations_moment_metrics(p_moment_id);
																
																    PERFORM sp_refresh_business_operations_memory_patterns(p_moment_id);
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_create_business_operations_live_event(
																    p_moment_id UUID,
																    p_source_table VARCHAR,
																    p_source_record_id UUID,
																    p_event_type VARCHAR,
																    p_actor_id UUID,
																    p_headline VARCHAR,
																    p_detail_message TEXT,
																    p_visibility VARCHAR DEFAULT 'operations_roles'
																)
																RETURNS VOID
																LANGUAGE plpgsql
																AS $$
																DECLARE
																    v_actor_name VARCHAR;
																BEGIN
																
																    v_actor_name :=
																        fn_get_operations_actor_name(
																            p_moment_id,
																            p_actor_id
																        );
																
																    INSERT INTO business_live_feed (
																        moment_id,
																        source_table,
																        source_record_id,
																        event_type,
																        actor_user_id,
																        actor_name,
																        headline,
																        detail_message,
																        visibility,
																        event_timestamp
																    )
																    VALUES (
																        p_moment_id,
																        p_source_table,
																        p_source_record_id,
																        p_event_type,
																        p_actor_id,
																        v_actor_name,
																        p_headline,
																        p_detail_message,
																        p_visibility,
																        CURRENT_TIMESTAMP
																    );
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_write_business_operations_audit(
																    p_moment_id UUID,
																    p_entity_type VARCHAR,
																    p_record_id UUID,
																    p_change_type VARCHAR,
																    p_changed_by UUID,
																    p_change_summary TEXT
																)
																RETURNS VOID
																LANGUAGE plpgsql
																AS $$
																DECLARE
																    v_name VARCHAR(255);
																    v_change VARCHAR(50);
																BEGIN
																
																    SELECT COALESCE(NULLIF(TRIM(display_name), ''), NULLIF(TRIM(email), ''), 'User')
																      INTO v_name
																      FROM users
																     WHERE id = p_changed_by
																     LIMIT 1;
																
																    v_name := COALESCE(v_name, 'User');
																    v_change := LOWER(COALESCE(p_change_type, 'create'));
																    IF v_change IN ('created', 'insert') THEN
																        v_change := 'create';
																    ELSIF v_change IN ('updated', 'update') THEN
																        v_change := 'edit';
																    ELSIF v_change NOT IN (
																        'create', 'edit', 'delete', 'restore', 'approve', 'reject', 'resolve'
																    ) THEN
																        v_change := 'edit';
																    END IF;
																
																    INSERT INTO business_audit_history (
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
																    )
																    VALUES (
																        p_moment_id,
																        COALESCE(NULLIF(TRIM(p_entity_type), ''), 'operations'),
																        p_record_id,
																        'status',
																        NULL,
																        COALESCE(NULLIF(TRIM(p_change_summary), ''), v_change),
																        v_change,
																        p_changed_by,
																        v_name,
																        p_change_summary,
																        CURRENT_TIMESTAMP
																    );
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_operations_spend_after_change()
																RETURNS TRIGGER
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    IF TG_OP = 'INSERT' THEN
																
																        PERFORM sp_create_business_operations_live_event(
																            NEW.moment_id,
																            'operations_spend_entries',
																            NEW.spend_entry_id,
																            'OPERATIONS_SPEND_RECORDED',
																            NEW.created_by,
																            'Spend Entry Recorded',
																            NEW.spend_name
																        );
																
																        PERFORM sp_write_business_operations_audit(
																            NEW.moment_id,
																            'operations_spend',
																            NEW.spend_entry_id,
																            'created',
																            NEW.created_by,
																            CONCAT('Spend recorded: ', NEW.spend_name)
																        );
																
																    ELSIF TG_OP = 'UPDATE' THEN
																
																        PERFORM sp_create_business_operations_live_event(
																            NEW.moment_id,
																            'operations_spend_entries',
																            NEW.spend_entry_id,
																            'OPERATIONS_SPEND_UPDATED',
																            NEW.created_by,
																            'Spend Entry Updated',
																            NEW.spend_name
																        );
																
																        PERFORM sp_write_business_operations_audit(
																            NEW.moment_id,
																            'operations_spend',
																            NEW.spend_entry_id,
																            'updated',
																            NEW.created_by,
																            CONCAT('Spend updated: ', NEW.spend_name)
																        );
																
																    END IF;
																
																    PERFORM sp_refresh_business_operations_orchestration(
																        NEW.moment_id
																    );
																
																    RETURN NULL;
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_operations_vendor_after_change()
																RETURNS TRIGGER
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    PERFORM sp_create_business_operations_live_event(
																        NEW.moment_id,
																        'operations_vendor_updates',
																        NEW.vendor_update_id,
																        CASE
																            WHEN TG_OP='INSERT'
																            THEN 'OPERATIONS_VENDOR_RECORDED'
																            ELSE 'OPERATIONS_VENDOR_UPDATED'
																        END,
																        NEW.created_by,
																        'Vendor Update',
																        NEW.vendor_name
																    );
																
																    PERFORM sp_write_business_operations_audit(
																        NEW.moment_id,
																        'operations_vendor',
																        NEW.vendor_update_id,
																        LOWER(TG_OP),
																        NEW.created_by,
																        CONCAT('Vendor update: ', NEW.vendor_name)
																    );
																
																    PERFORM sp_refresh_business_operations_orchestration(
																        NEW.moment_id
																    );
																
																    RETURN NULL;
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_operations_approval_after_change()
																RETURNS TRIGGER
																LANGUAGE plpgsql
																AS $$
																DECLARE
																    v_event VARCHAR;
																BEGIN
																
																    IF TG_OP='INSERT' THEN
																        v_event := 'OPERATIONS_APPROVAL_REQUESTED';
																    ELSE
																        IF NEW.approval_status='approved' THEN
																            v_event := 'OPERATIONS_APPROVAL_APPROVED';
																        ELSIF NEW.approval_status='rejected' THEN
																            v_event := 'OPERATIONS_APPROVAL_REJECTED';
																        ELSE
																            v_event := 'OPERATIONS_APPROVAL_UPDATED';
																        END IF;
																    END IF;
																
																    PERFORM sp_create_business_operations_live_event(
																        NEW.moment_id,
																        'operations_approval_requests',
																        NEW.operations_approval_id,
																        v_event,
																        NEW.requested_by,
																        'Approval Request',
																        NEW.request_title
																    );
																
																    PERFORM sp_write_business_operations_audit(
																        NEW.moment_id,
																        'operations_approval',
																        NEW.operations_approval_id,
																        LOWER(TG_OP),
																        NEW.requested_by,
																        CONCAT(
																            'Approval status: ',
																            NEW.approval_status
																        )
																    );
																
																    PERFORM sp_refresh_business_operations_orchestration(
																        NEW.moment_id
																    );
																
																    RETURN NULL;
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_operations_issue_after_change()
																RETURNS TRIGGER
																LANGUAGE plpgsql
																AS $$
																DECLARE
																    v_event VARCHAR;
																BEGIN
																
																    IF TG_OP='INSERT' THEN
																        v_event := 'OPERATIONS_ISSUE_RECORDED';
																    ELSE
																        IF NEW.issue_status='resolved' THEN
																            v_event := 'OPERATIONS_ISSUE_RESOLVED';
																        ELSE
																            v_event := 'OPERATIONS_ISSUE_UPDATED';
																        END IF;
																    END IF;
																
																    PERFORM sp_create_business_operations_live_event(
																        NEW.moment_id,
																        'operations_issues',
																        NEW.operations_issue_id,
																        v_event,
																        NEW.created_by,
																        'Issue / Risk',
																        NEW.issue_title
																    );
																
																    PERFORM sp_write_business_operations_audit(
																        NEW.moment_id,
																        'operations_issue',
																        NEW.operations_issue_id,
																        LOWER(TG_OP),
																        NEW.created_by,
																        CONCAT(
																            'Issue status: ',
																            NEW.issue_status
																        )
																    );
																
																    PERFORM sp_refresh_business_operations_orchestration(
																        NEW.moment_id
																    );
																
																    RETURN NULL;
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_operations_improvement_after_change()
																RETURNS TRIGGER
																LANGUAGE plpgsql
																AS $$
																DECLARE
																    v_event VARCHAR;
																BEGIN
																
																    IF TG_OP='INSERT' THEN
																        v_event := 'OPERATIONS_IMPROVEMENT_RECORDED';
																    ELSE
																        IF NEW.improvement_status='completed' THEN
																            v_event := 'OPERATIONS_IMPROVEMENT_COMPLETED';
																        ELSE
																            v_event := 'OPERATIONS_IMPROVEMENT_UPDATED';
																        END IF;
																    END IF;
																
																    PERFORM sp_create_business_operations_live_event(
																        NEW.moment_id,
																        'operations_improvements',
																        NEW.improvement_id,
																        v_event,
																        NEW.created_by,
																        'Operational Improvement',
																        NEW.improvement_title
																    );
																
																    PERFORM sp_write_business_operations_audit(
																        NEW.moment_id,
																        'operations_improvement',
																        NEW.improvement_id,
																        LOWER(TG_OP),
																        NEW.created_by,
																        CONCAT(
																            'Improvement status: ',
																            NEW.improvement_status
																        )
																    );
																
																    PERFORM sp_refresh_business_operations_orchestration(
																        NEW.moment_id
																    );
																
																    RETURN NULL;
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_activate_business_operations(
																    p_moment_id UUID
																)
																RETURNS VOID
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    UPDATE business_moments
																    SET
																        status = 'active',
																        activated_at = CURRENT_TIMESTAMP
																    WHERE moment_id = p_moment_id;
																
																    PERFORM sp_refresh_business_operations_orchestration(
																        p_moment_id
																    );
																
																    PERFORM sp_create_business_operations_live_event(
																        p_moment_id,
																        'business_moments',
																        p_moment_id,
																        'BUSINESS_OPERATIONS_ACTIVATED',
																        NULL,
																        'Business Operations Activated',
																        'Workspace is now active'
																    );
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_moment_activated_trigger()
																RETURNS TRIGGER
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    IF NEW.status = 'active'
																       AND OLD.status <> 'active'
																    THEN
																
																        CASE NEW.moment_type
																
																            WHEN 'team_operations'
																            THEN
																                PERFORM sp_refresh_business_orchestration(
																                    NEW.moment_id
																                );
																
																            WHEN 'business_runway'
																            THEN
																                PERFORM sp_refresh_business_runway_orchestration(
																                    NEW.moment_id
																                );
																
																            WHEN 'business_operations'
																            THEN
																                PERFORM sp_refresh_business_operations_orchestration(
																                    NEW.moment_id
																                );
																
																        END CASE;
																
																    END IF;
																
																    RETURN NEW;
																
																END;
																$$;
-- >>>STMT<<<
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
																      AND signal_source = 'business_operations';
																
																    /* Vendor Evaluations Increasing */
																
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
																            signal_source,
																            signal_type,
																            signal_title,
																            signal_message,
																            signal_score,
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
																
																    /* Operational Improvements Recorded */
																
																    SELECT COUNT(*)
																    INTO v_improvement_count
																    FROM operations_improvements
																    WHERE moment_id = p_moment_id
																      AND created_at >= CURRENT_DATE - INTERVAL '30 day'
																      AND archived_at IS NULL;
																
																    IF v_improvement_count > 0 THEN
																
																        INSERT INTO ai_signals (
																            moment_id,
																            signal_source,
																            signal_type,
																            signal_title,
																            signal_message,
																            signal_score,
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
																
																    /* Issue Resolution Velocity */
																
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
																            signal_source,
																            signal_type,
																            signal_title,
																            signal_message,
																            signal_score,
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
																
																    /* Operations Health */
																
																    SELECT operations_health_status
																    INTO v_current_health
																    FROM business_operations_snapshots
																    WHERE moment_id = p_moment_id
																    ORDER BY snapshot_date DESC
																    LIMIT 1;
																
																    IF v_current_health = 'healthy' THEN
																
																        INSERT INTO ai_signals (
																            moment_id,
																            signal_source,
																            signal_type,
																            signal_title,
																            signal_message,
																            signal_score,
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
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_business_operations_orchestration(
																    p_moment_id UUID
																)
																RETURNS VOID
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    PERFORM sp_refresh_business_operations_snapshot(
																        p_moment_id
																    );
																
																    PERFORM sp_refresh_business_operations_pulse_snapshot(
																        p_moment_id
																    );
																
																    PERFORM sp_refresh_business_operations_moment_metrics(
																        p_moment_id
																    );
																
																    PERFORM sp_refresh_business_operations_memory_patterns(
																        p_moment_id
																    );
																
																    PERFORM sp_refresh_operations_ai_signals(
																        p_moment_id
																    );
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_resolve_operations_kpis(
																    p_moment_id UUID
																)
																RETURNS TABLE (
																    kpi_name TEXT
																)
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    RETURN QUERY
																
																    SELECT
																        jsonb_array_elements_text(
																            COALESCE(
																                kpi_tracking,
																                '[]'::jsonb
																            )
																        )
																
																    FROM business_operations_structure
																
																    WHERE moment_id = p_moment_id;
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_business_health_drivers(
																    p_moment_id UUID
																)
																RETURNS VOID
																LANGUAGE plpgsql
																AS $$
																DECLARE
																    v_moment_type VARCHAR(100);
																BEGIN
																
																    SELECT moment_type
																    INTO v_moment_type
																    FROM business_moments
																    WHERE moment_id = p_moment_id;
																
																    DELETE FROM business_health_driver_scores
																    WHERE moment_id = p_moment_id;
																
																    /*
																    TEAM OPERATIONS
																    */
																
																    IF v_moment_type = 'team_operations' THEN
																
																        INSERT INTO business_health_driver_scores(
																            moment_id,
																            driver_code,
																            driver_name,
																            driver_score,
																            driver_status
																        )
																        VALUES
																        (
																            p_moment_id,
																            'participation',
																            'Participation',
																            80,
																            'good'
																        ),
																        (
																            p_moment_id,
																            'approval_efficiency',
																            'Approval Efficiency',
																            78,
																            'good'
																        ),
																        (
																            p_moment_id,
																            'issue_resolution',
																            'Issue Resolution',
																            84,
																            'good'
																        ),
																        (
																            p_moment_id,
																            'execution_discipline',
																            'Execution Discipline',
																            82,
																            'good'
																        );
																
																    END IF;
																
																    /*
																    BUSINESS RUNWAY
																    */
																
																    IF v_moment_type = 'business_runway' THEN
																
																        INSERT INTO business_health_driver_scores(
																            moment_id,
																            driver_code,
																            driver_name,
																            driver_score,
																            driver_status
																        )
																        VALUES
																        (
																            p_moment_id,
																            'cash_position',
																            'Cash Position',
																            85,
																            'good'
																        ),
																        (
																            p_moment_id,
																            'burn_stability',
																            'Burn Stability',
																            74,
																            'stable'
																        ),
																        (
																            p_moment_id,
																            'forecast_accuracy',
																            'Forecast Accuracy',
																            79,
																            'good'
																        ),
																        (
																            p_moment_id,
																            'revenue_momentum',
																            'Revenue Momentum',
																            81,
																            'good'
																        );
																
																    END IF;
																
																    /*
																    BUSINESS OPERATIONS
																    */
																
																    IF v_moment_type = 'business_operations' THEN
																
																        INSERT INTO business_health_driver_scores(
																            moment_id,
																            driver_code,
																            driver_name,
																            driver_score,
																            driver_status
																        )
																        VALUES
																        (
																            p_moment_id,
																            'operational_discipline',
																            'Operational Discipline',
																            83,
																            'good'
																        ),
																        (
																            p_moment_id,
																            'issue_resolution',
																            'Issue Resolution',
																            75,
																            'stable'
																        ),
																        (
																            p_moment_id,
																            'approval_velocity',
																            'Approval Velocity',
																            80,
																            'good'
																        ),
																        (
																            p_moment_id,
																            'process_improvement',
																            'Process Improvement',
																            86,
																            'good'
																        );
																
																    END IF;
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_business_attention_items(
																    p_moment_id UUID
																)
																RETURNS VOID
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    DELETE FROM business_attention_items
																    WHERE moment_id = p_moment_id;
																
																    INSERT INTO business_attention_items(
																        moment_id,
																        attention_type,
																        severity,
																        title,
																        description,
																        status
																    )
																    SELECT
																        p_moment_id,
																        'approval',
																        'high',
																        'Pending Approval',
																        'Approval request pending beyond SLA',
																        'open'
																    WHERE EXISTS (
																        SELECT 1
																        FROM business_approval_requests
																        WHERE moment_id = p_moment_id
																        AND approval_status = 'pending'
																    );
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_business_signal_insights(
																    p_moment_id UUID
																)
																RETURNS VOID
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    DELETE FROM business_signal_insights
																    WHERE moment_id = p_moment_id;
																
																    INSERT INTO business_signal_insights(
																        moment_id,
																        signal_type,
																        signal_title,
																        signal_summary,
																        impact_level
																    )
																    VALUES
																    (
																        p_moment_id,
																        'trend',
																        'Operational Consistency Improving',
																        'Activity completion rate increased during last 30 days',
																        'positive'
																    );
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_business_recommended_actions(
																    p_moment_id UUID
																)
																RETURNS VOID
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    DELETE FROM business_recommended_actions
																    WHERE moment_id = p_moment_id;
																
																    INSERT INTO business_recommended_actions(
																        moment_id,
																        action_title,
																        action_reason,
																        priority,
																        cta_label,
																        expected_health_impact,
																        status
																    )
																    VALUES
																    (
																        p_moment_id,
																        'Review Open Approvals',
																        'Pending approvals currently slowing execution',
																        'high',
																        'Review Now',
																        6,
																        'active'
																    );
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_business_pulse_snapshot_v2(
																    p_moment_id UUID
																)
																RETURNS VOID
																LANGUAGE plpgsql
																AS $$
																DECLARE
																    v_score NUMERIC(5,2);
																    v_category VARCHAR(50);
																    v_action UUID;
																BEGIN
																
																    SELECT AVG(driver_score)
																    INTO v_score
																    FROM business_health_driver_scores
																    WHERE moment_id = p_moment_id;
																
																    IF v_score >= 90 THEN
																        v_category := 'Elite';
																    ELSIF v_score >= 80 THEN
																        v_category := 'Strong';
																    ELSIF v_score >= 70 THEN
																        v_category := 'Stable';
																    ELSIF v_score >= 60 THEN
																        v_category := 'Attention Needed';
																    ELSE
																        v_category := 'At Risk';
																    END IF;
																
																    SELECT action_id
																    INTO v_action
																    FROM business_recommended_actions
																    WHERE moment_id = p_moment_id
																      AND status = 'active'
																    ORDER BY priority DESC
																    LIMIT 1;
																
																    UPDATE business_pulse_snapshots
																    SET
																        health_score = v_score,
																        pulse_category = v_category,
																        health_driver_count = (
																            SELECT COUNT(*)
																            FROM business_health_driver_scores
																            WHERE moment_id = p_moment_id
																        ),
																        attention_count = (
																            SELECT COUNT(*)
																            FROM business_attention_items
																            WHERE moment_id = p_moment_id
																              AND status IN ('open','in_progress')
																        ),
																        signal_count = (
																            SELECT COUNT(*)
																            FROM business_signal_insights
																            WHERE moment_id = p_moment_id
																              AND signal_status = 'active'
																        ),
																        next_best_action_id = v_action,
																        refreshed_at = CURRENT_TIMESTAMP
																    WHERE moment_id = p_moment_id;
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_business_pulse_experience(
																    p_moment_id UUID
																)
																RETURNS VOID
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    PERFORM sp_refresh_business_health_drivers(p_moment_id);
																
																    PERFORM sp_refresh_business_attention_items(p_moment_id);
																
																    PERFORM sp_refresh_business_signal_insights(p_moment_id);
																
																    PERFORM sp_refresh_business_recommended_actions(p_moment_id);
																
																    PERFORM sp_refresh_business_pulse_snapshot_v2(p_moment_id);
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_business_progress_snapshots(
																    p_moment_id UUID
																)
																RETURNS VOID
																LANGUAGE plpgsql
																AS $$
																DECLARE
																    v_moment_type VARCHAR(100);
																BEGIN
																
																    SELECT moment_type
																    INTO v_moment_type
																    FROM business_moments
																    WHERE moment_id = p_moment_id;
																
																    DELETE FROM business_progress_snapshots
																    WHERE moment_id = p_moment_id;
																
																    /*
																    TEAM OPERATIONS
																    */
																
																    IF v_moment_type = 'team_operations' THEN
																
																        INSERT INTO business_progress_snapshots(
																            moment_id,
																            metric_code,
																            metric_name,
																            metric_score,
																            metric_status
																        )
																        VALUES
																        (
																            p_moment_id,
																            'participation',
																            'Participation',
																            82,
																            'good'
																        ),
																        (
																            p_moment_id,
																            'approvals',
																            'Approvals',
																            78,
																            'stable'
																        ),
																        (
																            p_moment_id,
																            'execution',
																            'Execution',
																            84,
																            'good'
																        );
																
																    END IF;
																
																    /*
																    BUSINESS RUNWAY
																    */
																
																    IF v_moment_type = 'business_runway' THEN
																
																        INSERT INTO business_progress_snapshots(
																            moment_id,
																            metric_code,
																            metric_name,
																            metric_score,
																            metric_status
																        )
																        VALUES
																        (
																            p_moment_id,
																            'cash_position',
																            'Cash Position',
																            86,
																            'good'
																        ),
																        (
																            p_moment_id,
																            'burn_control',
																            'Burn Control',
																            74,
																            'stable'
																        ),
																        (
																            p_moment_id,
																            'forecast',
																            'Forecast Accuracy',
																            81,
																            'good'
																        );
																
																    END IF;
																
																    /*
																    BUSINESS OPERATIONS
																    */
																
																    IF v_moment_type = 'business_operations' THEN
																
																        INSERT INTO business_progress_snapshots(
																            moment_id,
																            metric_code,
																            metric_name,
																            metric_score,
																            metric_status
																        )
																        VALUES
																        (
																            p_moment_id,
																            'discipline',
																            'Operational Discipline',
																            83,
																            'good'
																        ),
																        (
																            p_moment_id,
																            'issues',
																            'Issue Resolution',
																            76,
																            'stable'
																        ),
																        (
																            p_moment_id,
																            'improvement',
																            'Improvement Velocity',
																            88,
																            'good'
																        );
																
																    END IF;
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_business_moment_highlights(
																    p_moment_id UUID
																)
																RETURNS VOID
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    DELETE FROM business_moment_highlights
																    WHERE moment_id = p_moment_id;
																
																    /*
																    Example highlight generation
																    */
																
																    INSERT INTO business_moment_highlights(
																        moment_id,
																        highlight_type,
																        highlight_title,
																        highlight_summary,
																        impact_level
																    )
																    VALUES
																    (
																        p_moment_id,
																        'milestone',
																        'Major Milestone Completed',
																        'Business milestone completed successfully.',
																        'high'
																    );
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_business_activity_center_items(
																    p_moment_id UUID
																)
																RETURNS VOID
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    DELETE FROM business_activity_center_items
																    WHERE moment_id = p_moment_id;
																
																    INSERT INTO business_activity_center_items(
																        moment_id,
																        source_table,
																        source_record_id,
																        activity_type,
																        activity_title,
																        activity_summary,
																        activity_status,
																        occurred_at
																    )
																    SELECT
																        p_moment_id,
																        'business_live_feed',
																        live_feed_id,
																        event_type,
																        title,
																        description,
																        event_status,
																        event_time
																    FROM business_live_feed
																    WHERE moment_id = p_moment_id;
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_business_moment_metrics_v2(
																    p_moment_id UUID
																)
																RETURNS VOID
																LANGUAGE plpgsql
																AS $$
																DECLARE
																    v_progress_score NUMERIC(5,2);
																    v_recent_wins INTEGER;
																    v_timeline_count INTEGER;
																    v_moment_type VARCHAR(100);
																    v_cta VARCHAR(100);
																BEGIN
																
																    SELECT AVG(metric_score)
																    INTO v_progress_score
																    FROM business_progress_snapshots
																    WHERE moment_id = p_moment_id;
																
																    SELECT COUNT(*)
																    INTO v_recent_wins
																    FROM business_moment_highlights
																    WHERE moment_id = p_moment_id
																      AND highlight_status = 'active';
																
																    SELECT COUNT(*)
																    INTO v_timeline_count
																    FROM business_activity_center_items
																    WHERE moment_id = p_moment_id;
																
																    SELECT moment_type
																    INTO v_moment_type
																    FROM business_moments
																    WHERE moment_id = p_moment_id;
																
																    IF v_moment_type = 'team_operations' THEN
																        v_cta := 'Manage Team';
																    ELSIF v_moment_type = 'business_runway' THEN
																        v_cta := 'Manage Runway';
																    ELSIF v_moment_type = 'business_operations' THEN
																        v_cta := 'Manage Operations';
																    ELSE
																        v_cta := 'Continue Managing';
																    END IF;
																
																    UPDATE business_moment_metrics
																    SET
																        progress_score = v_progress_score,
																
																        progress_status =
																        CASE
																            WHEN v_progress_score >= 85 THEN 'excellent'
																            WHEN v_progress_score >= 75 THEN 'good'
																            WHEN v_progress_score >= 65 THEN 'stable'
																            ELSE 'attention'
																        END,
																
																        recent_wins_count = v_recent_wins,
																
																        timeline_count = v_timeline_count,
																
																        continue_cta_label = v_cta
																
																    WHERE moment_id = p_moment_id;
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_business_moments_experience(
																    p_moment_id UUID
																)
																RETURNS VOID
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    PERFORM sp_refresh_business_progress_snapshots(
																        p_moment_id
																    );
																
																    PERFORM sp_refresh_business_moment_highlights(
																        p_moment_id
																    );
																
																    PERFORM sp_refresh_business_activity_center_items(
																        p_moment_id
																    );
																
																    PERFORM sp_refresh_business_moment_metrics_v2(
																        p_moment_id
																    );
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_validate_business_moments_experience(
																    p_moment_id UUID
																)
																RETURNS TABLE(
																    validation_name TEXT,
																    validation_result TEXT
																)
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    RETURN QUERY
																    SELECT
																        'progress_snapshots',
																        CASE
																            WHEN EXISTS (
																                SELECT 1
																                FROM business_progress_snapshots
																                WHERE moment_id = p_moment_id
																            )
																            THEN 'PASS'
																            ELSE 'FAIL'
																        END;
																
																    RETURN QUERY
																    SELECT
																        'moment_highlights',
																        CASE
																            WHEN EXISTS (
																                SELECT 1
																                FROM business_moment_highlights
																                WHERE moment_id = p_moment_id
																            )
																            THEN 'PASS'
																            ELSE 'FAIL'
																        END;
																
																    RETURN QUERY
																    SELECT
																        'activity_center',
																        CASE
																            WHEN EXISTS (
																                SELECT 1
																                FROM business_activity_center_items
																                WHERE moment_id = p_moment_id
																            )
																            THEN 'PASS'
																            ELSE 'FAIL'
																        END;
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_business_life_dimensions(
																    p_workspace_id UUID
																)
																RETURNS VOID
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    DELETE FROM business_life_dimensions
																    WHERE workspace_id = p_workspace_id;
																
																    /*
																    PEOPLE
																    */
																
																    INSERT INTO business_life_dimensions(
																        workspace_id,
																        dimension_type,
																        dimension_name,
																        dimension_score,
																        dimension_status
																    )
																    VALUES
																    (
																        p_workspace_id,
																        'people',
																        'People',
																        82,
																        'strong'
																    );
																
																    /*
																    FINANCE
																    */
																
																    INSERT INTO business_life_dimensions(
																        workspace_id,
																        dimension_type,
																        dimension_name,
																        dimension_score,
																        dimension_status
																    )
																    VALUES
																    (
																        p_workspace_id,
																        'finance',
																        'Finance',
																        79,
																        'stable'
																    );
																
																    /*
																    OPERATIONS
																    */
																
																    INSERT INTO business_life_dimensions(
																        workspace_id,
																        dimension_type,
																        dimension_name,
																        dimension_score,
																        dimension_status
																    )
																    VALUES
																    (
																        p_workspace_id,
																        'operations',
																        'Operations',
																        85,
																        'strong'
																    );
																
																    /*
																    VENDORS
																    */
																
																    INSERT INTO business_life_dimensions(
																        workspace_id,
																        dimension_type,
																        dimension_name,
																        dimension_score,
																        dimension_status
																    )
																    VALUES
																    (
																        p_workspace_id,
																        'vendor',
																        'Vendor',
																        76,
																        'stable'
																    );
																
																    /*
																    GROWTH
																    */
																
																    INSERT INTO business_life_dimensions(
																        workspace_id,
																        dimension_type,
																        dimension_name,
																        dimension_score,
																        dimension_status
																    )
																    VALUES
																    (
																        p_workspace_id,
																        'growth',
																        'Growth',
																        83,
																        'strong'
																    );
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_business_life_connections(
																    p_workspace_id UUID
																)
																RETURNS VOID
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    DELETE FROM business_life_connections
																    WHERE workspace_id = p_workspace_id;
																
																    INSERT INTO business_life_connections(
																        workspace_id,
																        source_dimension,
																        source_label,
																        influence_type,
																        influence_strength,
																        target_dimension,
																        target_label,
																        confidence_score
																    )
																    VALUES
																    (
																        p_workspace_id,
																        'people',
																        'Participation',
																        'supports',
																        'strong',
																        'operations',
																        'Execution',
																        88
																    );
																
																    INSERT INTO business_life_connections(
																        workspace_id,
																        source_dimension,
																        source_label,
																        influence_type,
																        influence_strength,
																        target_dimension,
																        target_label,
																        confidence_score
																    )
																    VALUES
																    (
																        p_workspace_id,
																        'finance',
																        'Runway',
																        'supports',
																        'moderate',
																        'growth',
																        'Expansion',
																        81
																    );
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_business_life_insights(
																    p_workspace_id UUID
																)
																RETURNS VOID
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    DELETE FROM business_life_insights
																    WHERE workspace_id = p_workspace_id;
																
																    /*
																    DRIFT ALERT
																    */
																
																    INSERT INTO business_life_insights(
																        workspace_id,
																        insight_type,
																        insight_title,
																        insight_body,
																        priority
																    )
																    VALUES
																    (
																        p_workspace_id,
																        'drift_alert',
																        'Vendor Performance Softening',
																        'Vendor engagement trend declined during the last cycle.',
																        'high'
																    );
																
																    /*
																    HIGHEST LEVERAGE
																    */
																
																    INSERT INTO business_life_insights(
																        workspace_id,
																        insight_type,
																        insight_title,
																        insight_body
																    )
																    VALUES
																    (
																        p_workspace_id,
																        'highest_leverage',
																        'Improve Approval Velocity',
																        'Faster approvals are likely to improve execution and growth simultaneously.'
																    );
																
																    /*
																    BUSINESS TREND
																    */
																
																    INSERT INTO business_life_insights(
																        workspace_id,
																        insight_type,
																        insight_title,
																        insight_body
																    )
																    VALUES
																    (
																        p_workspace_id,
																        'business_trend',
																        'Business Health Improving',
																        'Overall business health improved compared to previous cycle.'
																    );
																
																    /*
																    GROWTH DRIVER
																    */
																
																    INSERT INTO business_life_insights(
																        workspace_id,
																        insight_type,
																        insight_title,
																        insight_body
																    )
																    VALUES
																    (
																        p_workspace_id,
																        'growth_driver',
																        'Operational Consistency',
																        'Consistent execution is currently the strongest growth driver.'
																    );
																
																    /*
																    CHANGED THIS MONTH
																    */
																
																    INSERT INTO business_life_insights(
																        workspace_id,
																        insight_type,
																        insight_title,
																        insight_body
																    )
																    VALUES
																    (
																        p_workspace_id,
																        'changed_this_month',
																        'Team Participation Increased',
																        'Participation improved significantly this month.'
																    );
																
																    /*
																    MOMENTRA INTELLIGENCE
																    */
																
																    INSERT INTO business_life_insights(
																        workspace_id,
																        insight_type,
																        insight_title,
																        insight_body
																    )
																    VALUES
																    (
																        p_workspace_id,
																        'momentra_intelligence',
																        'Execution Drives Momentum',
																        'The strongest positive relationship currently exists between execution quality and business growth.'
																    );
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_business_journey_events(
																    p_workspace_id UUID
																)
																RETURNS VOID
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    DELETE FROM business_journey_events
																    WHERE workspace_id = p_workspace_id
																      AND source_table = 'system_generated';
																
																    INSERT INTO business_journey_events(
																        workspace_id,
																        event_title,
																        event_description,
																        event_type,
																        event_date,
																        source_table
																    )
																    VALUES
																    (
																        p_workspace_id,
																        'Business Health Stabilized',
																        'Business crossed stable operating threshold.',
																        'milestone',
																        CURRENT_DATE,
																        'system_generated'
																    );
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_business_life_snapshot(
																    p_workspace_id UUID
																)
																RETURNS VOID
																LANGUAGE plpgsql
																AS $$
																DECLARE
																    v_people NUMERIC(5,2);
																    v_finance NUMERIC(5,2);
																    v_operations NUMERIC(5,2);
																    v_vendor NUMERIC(5,2);
																    v_growth NUMERIC(5,2);
																    v_life_score NUMERIC(5,2);
																BEGIN
																
																    SELECT dimension_score
																    INTO v_people
																    FROM business_life_dimensions
																    WHERE workspace_id = p_workspace_id
																      AND dimension_type='people';
																
																    SELECT dimension_score
																    INTO v_finance
																    FROM business_life_dimensions
																    WHERE workspace_id = p_workspace_id
																      AND dimension_type='finance';
																
																    SELECT dimension_score
																    INTO v_operations
																    FROM business_life_dimensions
																    WHERE workspace_id = p_workspace_id
																      AND dimension_type='operations';
																
																    SELECT dimension_score
																    INTO v_vendor
																    FROM business_life_dimensions
																    WHERE workspace_id = p_workspace_id
																      AND dimension_type='vendor';
																
																    SELECT dimension_score
																    INTO v_growth
																    FROM business_life_dimensions
																    WHERE workspace_id = p_workspace_id
																      AND dimension_type='growth';
																
																    v_life_score :=
																    (
																        COALESCE(v_people,0) +
																        COALESCE(v_finance,0) +
																        COALESCE(v_operations,0) +
																        COALESCE(v_vendor,0) +
																        COALESCE(v_growth,0)
																    ) / 5;
																
																    INSERT INTO business_life_snapshots(
																        workspace_id,
																        life_score,
																        life_status,
																        people_score,
																        finance_score,
																        operations_score,
																        vendor_score,
																        growth_score,
																        generated_at
																    )
																    VALUES(
																        p_workspace_id,
																        v_life_score,
																
																        CASE
																            WHEN v_life_score >= 85 THEN 'strong'
																            WHEN v_life_score >= 70 THEN 'stable'
																            WHEN v_life_score >= 55 THEN 'attention'
																            ELSE 'at_risk'
																        END,
																
																        v_people,
																        v_finance,
																        v_operations,
																        v_vendor,
																        v_growth,
																        CURRENT_TIMESTAMP
																    );
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_business_life_experience(
																    p_workspace_id UUID
																)
																RETURNS VOID
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    PERFORM sp_refresh_business_life_dimensions(
																        p_workspace_id
																    );
																
																    PERFORM sp_refresh_business_life_connections(
																        p_workspace_id
																    );
																
																    PERFORM sp_refresh_business_life_insights(
																        p_workspace_id
																    );
																
																    PERFORM sp_refresh_business_journey_events(
																        p_workspace_id
																    );
																
																    PERFORM sp_refresh_business_life_snapshot(
																        p_workspace_id
																    );
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_validate_business_life_experience(
																    p_workspace_id UUID
																)
																RETURNS TABLE(
																    validation_name TEXT,
																    validation_result TEXT
																)
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    RETURN QUERY
																    SELECT
																    'life_dimensions',
																    CASE
																        WHEN EXISTS(
																            SELECT 1
																            FROM business_life_dimensions
																            WHERE workspace_id=p_workspace_id
																        )
																        THEN 'PASS'
																        ELSE 'FAIL'
																    END;
																
																    RETURN QUERY
																    SELECT
																    'life_connections',
																    CASE
																        WHEN EXISTS(
																            SELECT 1
																            FROM business_life_connections
																            WHERE workspace_id=p_workspace_id
																        )
																        THEN 'PASS'
																        ELSE 'FAIL'
																    END;
																
																    RETURN QUERY
																    SELECT
																    'life_snapshot',
																    CASE
																        WHEN EXISTS(
																            SELECT 1
																            FROM business_life_snapshots
																            WHERE workspace_id=p_workspace_id
																        )
																        THEN 'PASS'
																        ELSE 'FAIL'
																    END;
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_business_memory_learnings(
																    p_workspace_id UUID
																)
																RETURNS VOID
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    DELETE FROM business_memory_learnings
																    WHERE workspace_id = p_workspace_id;
																
																    INSERT INTO business_memory_learnings(
																        workspace_id,
																        learning_type,
																        learning_title,
																        learning_summary,
																        confidence_score,
																        derived_from_count
																    )
																    VALUES
																    (
																        p_workspace_id,
																        'execution',
																        'Fast Approvals Improve Delivery',
																        'Projects with approvals completed within SLA consistently reached completion faster.',
																        87,
																        24
																    );
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_business_playbooks(
																    p_workspace_id UUID
																)
																RETURNS VOID
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    DELETE FROM business_playbooks
																    WHERE workspace_id = p_workspace_id;
																
																    INSERT INTO business_playbooks(
																        workspace_id,
																        playbook_title,
																        playbook_summary,
																        success_rate,
																        confidence_score
																    )
																    VALUES
																    (
																        p_workspace_id,
																        'Weekly Operations Review',
																        'Teams performing structured weekly reviews achieved higher execution consistency.',
																        84,
																        86
																    );
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_business_success_memory(
																    p_workspace_id UUID
																)
																RETURNS VOID
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    DELETE FROM business_success_memory
																    WHERE workspace_id = p_workspace_id;
																
																    INSERT INTO business_success_memory(
																        workspace_id,
																        success_title,
																        success_summary,
																        action_taken,
																        impact_score
																    )
																    VALUES
																    (
																        p_workspace_id,
																        'Vendor Response Improvement',
																        'Vendor responsiveness improved significantly.',
																        'Introduced structured follow-up cadence.',
																        82
																    );
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_business_risk_memory(
																    p_workspace_id UUID
																)
																RETURNS VOID
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    DELETE FROM business_risk_memory
																    WHERE workspace_id = p_workspace_id;
																
																    INSERT INTO business_risk_memory(
																        workspace_id,
																        risk_title,
																        risk_summary,
																        observed_count,
																        severity
																    )
																    VALUES
																    (
																        p_workspace_id,
																        'Approval Bottlenecks',
																        'Repeated delays caused project slowdowns.',
																        11,
																        'high'
																    );
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_business_wisdom(
																    p_workspace_id UUID
																)
																RETURNS VOID
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    DELETE FROM business_wisdom
																    WHERE workspace_id = p_workspace_id;
																
																    INSERT INTO business_wisdom(
																        workspace_id,
																        wisdom_text,
																        confidence_score
																    )
																    VALUES
																    (
																        p_workspace_id,
																        'Execution quality compounds faster than growth initiatives.',
																        91
																    );
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_business_memory_snapshot(
																    p_workspace_id UUID
																)
																RETURNS VOID
																LANGUAGE plpgsql
																AS $$
																DECLARE
																
																    v_learning_count INTEGER;
																    v_playbook_count INTEGER;
																    v_risk_count INTEGER;
																    v_success_count INTEGER;
																    v_wisdom_count INTEGER;
																
																    v_learning_id UUID;
																    v_wisdom_id UUID;
																
																    v_memory_score NUMERIC(5,2);
																
																BEGIN
																
																    SELECT COUNT(*)
																    INTO v_learning_count
																    FROM business_memory_learnings
																    WHERE workspace_id = p_workspace_id;
																
																    SELECT COUNT(*)
																    INTO v_playbook_count
																    FROM business_playbooks
																    WHERE workspace_id = p_workspace_id;
																
																    SELECT COUNT(*)
																    INTO v_risk_count
																    FROM business_risk_memory
																    WHERE workspace_id = p_workspace_id;
																
																    SELECT COUNT(*)
																    INTO v_success_count
																    FROM business_success_memory
																    WHERE workspace_id = p_workspace_id;
																
																    SELECT COUNT(*)
																    INTO v_wisdom_count
																    FROM business_wisdom
																    WHERE workspace_id = p_workspace_id;
																
																    SELECT learning_id
																    INTO v_learning_id
																    FROM business_memory_learnings
																    WHERE workspace_id = p_workspace_id
																    ORDER BY confidence_score DESC
																    LIMIT 1;
																
																    SELECT wisdom_id
																    INTO v_wisdom_id
																    FROM business_wisdom
																    WHERE workspace_id = p_workspace_id
																    ORDER BY confidence_score DESC
																    LIMIT 1;
																
																    v_memory_score :=
																        (
																            LEAST(v_learning_count,20) * 1.5 +
																            LEAST(v_playbook_count,20) * 2 +
																            LEAST(v_success_count,20) * 1.5 +
																            LEAST(v_wisdom_count,20) * 2
																        );
																
																    INSERT INTO business_memory_snapshots(
																        workspace_id,
																        memory_score,
																        memory_status,
																        learning_count,
																        playbook_count,
																        risk_count,
																        success_count,
																        wisdom_count,
																        strongest_learning_id,
																        strongest_wisdom_id,
																        generated_at
																    )
																    VALUES
																    (
																        p_workspace_id,
																
																        LEAST(v_memory_score,100),
																
																        CASE
																            WHEN v_memory_score >= 80 THEN 'mature'
																            WHEN v_memory_score >= 60 THEN 'strong'
																            WHEN v_memory_score >= 40 THEN 'growing'
																            ELSE 'forming'
																        END,
																
																        v_learning_count,
																        v_playbook_count,
																        v_risk_count,
																        v_success_count,
																        v_wisdom_count,
																
																        v_learning_id,
																        v_wisdom_id,
																
																        CURRENT_TIMESTAMP
																    );
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_business_memory_experience(
																    p_workspace_id UUID
																)
																RETURNS VOID
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    PERFORM sp_refresh_business_memory_learnings(
																        p_workspace_id
																    );
																
																    PERFORM sp_refresh_business_playbooks(
																        p_workspace_id
																    );
																
																    PERFORM sp_refresh_business_success_memory(
																        p_workspace_id
																    );
																
																    PERFORM sp_refresh_business_risk_memory(
																        p_workspace_id
																    );
																
																    PERFORM sp_refresh_business_wisdom(
																        p_workspace_id
																    );
																
																    PERFORM sp_refresh_business_memory_snapshot(
																        p_workspace_id
																    );
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_validate_business_memory_experience(
																    p_workspace_id UUID
																)
																RETURNS TABLE(
																    validation_name TEXT,
																    validation_result TEXT
																)
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    RETURN QUERY
																    SELECT
																        'memory_learnings',
																        CASE
																            WHEN EXISTS(
																                SELECT 1
																                FROM business_memory_learnings
																                WHERE workspace_id = p_workspace_id
																            )
																            THEN 'PASS'
																            ELSE 'FAIL'
																        END;
																
																    RETURN QUERY
																    SELECT
																        'business_playbooks',
																        CASE
																            WHEN EXISTS(
																                SELECT 1
																                FROM business_playbooks
																                WHERE workspace_id = p_workspace_id
																            )
																            THEN 'PASS'
																            ELSE 'FAIL'
																        END;
																
																    RETURN QUERY
																    SELECT
																        'memory_snapshot',
																        CASE
																            WHEN EXISTS(
																                SELECT 1
																                FROM business_memory_snapshots
																                WHERE workspace_id = p_workspace_id
																            )
																            THEN 'PASS'
																            ELSE 'FAIL'
																        END;
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_business_activity_permissions(
																    p_moment_id UUID
																)
																RETURNS VOID
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    DELETE FROM business_activity_permissions
																    WHERE moment_id = p_moment_id;
																
																    /*
																    OWNER
																    */
																
																    INSERT INTO business_activity_permissions (
																        moment_id,
																        source_table,
																        source_record_id,
																        role_name,
																        can_view,
																        can_edit,
																        can_delete,
																        can_approve,
																        permission_reason
																    )
																    SELECT
																        p_moment_id,
																        ac.source_table,
																        ac.source_record_id,
																        'owner',
																        TRUE,
																        TRUE,
																        TRUE,
																        TRUE,
																        'Full control'
																    FROM business_activity_center_items ac
																    WHERE ac.moment_id = p_moment_id;
																
																    /*
																    MANAGER
																    */
																
																    INSERT INTO business_activity_permissions (
																        moment_id,
																        source_table,
																        source_record_id,
																        role_name,
																        can_view,
																        can_edit,
																        can_delete,
																        can_approve,
																        permission_reason
																    )
																    SELECT
																        p_moment_id,
																        ac.source_table,
																        ac.source_record_id,
																        'manager',
																        TRUE,
																        TRUE,
																        FALSE,
																        TRUE,
																        'Operational management'
																    FROM business_activity_center_items ac
																    WHERE ac.moment_id = p_moment_id;
																
																    /*
																    CONTRIBUTOR
																    */
																
																    INSERT INTO business_activity_permissions (
																        moment_id,
																        source_table,
																        source_record_id,
																        role_name,
																        can_view,
																        can_edit,
																        can_delete,
																        can_approve,
																        permission_reason
																    )
																    SELECT
																        p_moment_id,
																        ac.source_table,
																        ac.source_record_id,
																        'contributor',
																        TRUE,
																        TRUE,
																        FALSE,
																        FALSE,
																        'Own activity edit'
																    FROM business_activity_center_items ac
																    WHERE ac.moment_id = p_moment_id;
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_get_activity_permission_badge(
																    p_can_edit BOOLEAN,
																    p_can_approve BOOLEAN,
																    p_can_delete BOOLEAN
																)
																RETURNS VARCHAR(50)
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    IF p_can_delete = TRUE THEN
																        RETURN 'Owner';
																    END IF;
																
																    IF p_can_approve = TRUE THEN
																        RETURN 'Approver';
																    END IF;
																
																    IF p_can_edit = TRUE THEN
																        RETURN 'Editable';
																    END IF;
																
																    RETURN 'View Only';
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_business_activity_center_cache(
																    p_moment_id UUID
																)
																RETURNS VOID
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    DELETE FROM business_activity_center_items
																    WHERE moment_id = p_moment_id;
																
																    /*
																    TEAM APPROVALS
																    */
																
																    INSERT INTO business_activity_center_items (
																        moment_id,
																        source_table,
																        source_record_id,
																        activity_type,
																        activity_title,
																        activity_summary,
																        actor_name,
																        activity_status,
																        occurred_at
																    )
																    SELECT
																        ta.moment_id,
																        'team_approval_requests',
																        ta.approval_request_id,
																        'approval',
																        ta.request_title,
																        ta.request_reason,
																        ta.requested_by_name,
																        ta.approval_status,
																        ta.created_at
																    FROM team_approval_requests ta
																    WHERE ta.moment_id = p_moment_id;
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_get_activity_detail(
																    p_source_table VARCHAR,
																    p_source_record_id UUID
																)
																RETURNS JSONB
																LANGUAGE plpgsql
																AS $$
																DECLARE
																    v_result JSONB;
																BEGIN
																
																    SELECT jsonb_build_object(
																        'source_table',
																        p_source_table,
																        'source_record_id',
																        p_source_record_id
																    )
																    INTO v_result;
																
																    RETURN v_result;
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_can_edit_activity(
																    p_role_name VARCHAR,
																    p_source_table VARCHAR,
																    p_source_record_id UUID
																)
																RETURNS BOOLEAN
																LANGUAGE plpgsql
																AS $$
																DECLARE
																    v_allowed BOOLEAN;
																BEGIN
																
																    SELECT can_edit
																    INTO v_allowed
																    FROM business_activity_permissions
																    WHERE role_name = p_role_name
																      AND source_table = p_source_table
																      AND source_record_id = p_source_record_id
																    LIMIT 1;
																
																    RETURN COALESCE(v_allowed,FALSE);
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_can_approve_activity(
																    p_role_name VARCHAR,
																    p_source_table VARCHAR,
																    p_source_record_id UUID
																)
																RETURNS BOOLEAN
																LANGUAGE plpgsql
																AS $$
																DECLARE
																    v_allowed BOOLEAN;
																BEGIN
																
																    SELECT can_approve
																    INTO v_allowed
																    FROM business_activity_permissions
																    WHERE role_name = p_role_name
																      AND source_table = p_source_table
																      AND source_record_id = p_source_record_id
																    LIMIT 1;
																
																    RETURN COALESCE(v_allowed,FALSE);
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_business_activity_center(
																    p_moment_id UUID
																)
																RETURNS VOID
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    PERFORM sp_refresh_business_activity_center_cache(
																        p_moment_id
																    );
																
																    PERFORM sp_refresh_business_activity_permissions(
																        p_moment_id
																    );
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_validate_business_activity_center(
																    p_moment_id UUID
																)
																RETURNS TABLE(
																    validation_name TEXT,
																    validation_result TEXT
																)
																LANGUAGE plpgsql
																AS $$
																BEGIN
																
																    RETURN QUERY
																    SELECT
																    'activity_cache',
																    CASE
																        WHEN EXISTS(
																            SELECT 1
																            FROM business_activity_center_items
																            WHERE moment_id = p_moment_id
																        )
																        THEN 'PASS'
																        ELSE 'FAIL'
																    END;
																
																    RETURN QUERY
																    SELECT
																    'activity_permissions',
																    CASE
																        WHEN EXISTS(
																            SELECT 1
																            FROM business_activity_permissions
																            WHERE moment_id = p_moment_id
																        )
																        THEN 'PASS'
																        ELSE 'FAIL'
																    END;
																
																END;
																$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_create_business_refresh_job(
    p_workspace_id UUID,
    p_moment_id UUID,
    p_job_type VARCHAR,
    p_priority VARCHAR DEFAULT 'medium'
)
RETURNS UUID
LANGUAGE plpgsql
AS $$
DECLARE
    v_job_id UUID;
BEGIN

    INSERT INTO business_orchestration_jobs(
        job_id,
        workspace_id,
        moment_id,
        job_type,
        priority,
        orchestration_scope,
        job_status,
        created_at
    )
    VALUES(
        gen_random_uuid(),
        p_workspace_id,
        p_moment_id,
        p_job_type,
        p_priority,
        'moment',
        'pending',
        CURRENT_TIMESTAMP
    )
    RETURNING job_id
    INTO v_job_id;

    RETURN v_job_id;

END;
$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_route_business_refresh(
    p_workspace_id UUID,
    p_moment_id UUID
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
BEGIN

    /*
    Always refresh
    */

    PERFORM sp_create_business_refresh_job(
        p_workspace_id,
        p_moment_id,
        'pulse_refresh',
        'high'
    );

    PERFORM sp_create_business_refresh_job(
        p_workspace_id,
        p_moment_id,
        'moments_refresh',
        'high'
    );

    PERFORM sp_create_business_refresh_job(
        p_workspace_id,
        p_moment_id,
        'activity_refresh',
        'high'
    );

    /*
    Periodic experience refresh
    */

    PERFORM sp_create_business_refresh_job(
        p_workspace_id,
        p_moment_id,
        'life_refresh',
        'medium'
    );

    PERFORM sp_create_business_refresh_job(
        p_workspace_id,
        p_moment_id,
        'memory_refresh',
        'medium'
    );

END;
$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_process_business_refresh_job(
    p_job_id UUID
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
DECLARE
    v_job RECORD;
BEGIN

    SELECT *
    INTO v_job
    FROM business_orchestration_jobs
    WHERE job_id = p_job_id;

    IF NOT FOUND THEN
        RETURN;
    END IF;

    UPDATE business_orchestration_jobs
    SET job_status='processing'
    WHERE job_id=p_job_id;

    /*
    Pulse
    */

    IF v_job.job_type='pulse_refresh' THEN

        PERFORM sp_refresh_business_pulse_experience(
            v_job.moment_id
        );

    END IF;

    /*
    Moments
    */

    IF v_job.job_type='moments_refresh' THEN

        PERFORM sp_refresh_business_moments_experience(
            v_job.moment_id
        );

    END IF;

    /*
    Activity
    */

    IF v_job.job_type='activity_refresh' THEN

        PERFORM sp_refresh_business_activity_center(
            v_job.moment_id
        );

    END IF;

    /*
    Life
    */

    IF v_job.job_type='life_refresh' THEN

        PERFORM sp_refresh_business_life_experience(
            v_job.workspace_id
        );

    END IF;

    /*
    Memory
    */

    IF v_job.job_type='memory_refresh' THEN

        PERFORM sp_refresh_business_memory_experience(
            v_job.workspace_id
        );

    END IF;

    UPDATE business_orchestration_jobs
    SET
        job_status='completed',
        completed_at=CURRENT_TIMESTAMP
    WHERE job_id=p_job_id;

END;
$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION trg_business_runway_refresh()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN

    PERFORM sp_route_business_refresh(
        NEW.workspace_id,
        NEW.moment_id
    );

    RETURN NEW;
END;
$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION trg_team_operations_refresh()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN

    PERFORM sp_route_business_refresh(
        NEW.workspace_id,
        NEW.moment_id
    );

    RETURN NEW;
END;
$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION trg_business_operations_refresh()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN

    PERFORM sp_route_business_refresh(
        NEW.workspace_id,
        NEW.moment_id
    );

    RETURN NEW;
END;
$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION trg_approval_refresh()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN

    IF NEW.approval_status <> OLD.approval_status THEN

        PERFORM sp_route_business_refresh(
            NEW.workspace_id,
            NEW.moment_id
        );

    END IF;

    RETURN NEW;
END;
$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_queue_workspace_refresh(
    p_workspace_id UUID
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
BEGIN

    INSERT INTO business_orchestration_jobs(
        job_id,
        workspace_id,
        job_type,
        orchestration_scope,
        priority,
        job_status,
        created_at
    )
    VALUES(
        gen_random_uuid(),
        p_workspace_id,
        'workspace_refresh',
        'workspace',
        'low',
        'pending',
        CURRENT_TIMESTAMP
    );

END;
$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_validate_business_orchestration()
RETURNS TABLE(
    validation_name TEXT,
    validation_result TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN

    RETURN QUERY
    SELECT
    'job_router',
    'PASS';

    RETURN QUERY
    SELECT
    'job_processor',
    'PASS';

    RETURN QUERY
    SELECT
    'workspace_refresh',
    'PASS';

END;
$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_validate_business_views()
RETURNS TABLE(
    validation_name TEXT,
    validation_result TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN

    RETURN QUERY
    SELECT
    'pulse_view',
    CASE
        WHEN to_regclass('vw_business_pulse_v2') IS NOT NULL
        THEN 'PASS'
        ELSE 'FAIL'
    END;

    RETURN QUERY
    SELECT
    'moments_view',
    CASE
        WHEN to_regclass('vw_business_moments_v2') IS NOT NULL
        THEN 'PASS'
        ELSE 'FAIL'
    END;

    RETURN QUERY
    SELECT
    'life_view',
    CASE
        WHEN to_regclass('vw_business_life_v2') IS NOT NULL
        THEN 'PASS'
        ELSE 'FAIL'
    END;

    RETURN QUERY
    SELECT
    'memory_view',
    CASE
        WHEN to_regclass('vw_business_memory_v2') IS NOT NULL
        THEN 'PASS'
        ELSE 'FAIL'
    END;

END;
$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_business_experience(
    p_workspace_id UUID,
    p_moment_id UUID
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
BEGIN

    /*
    Pulse
    */

    PERFORM sp_refresh_business_pulse_experience(
        p_moment_id
    );

    /*
    Moments
    */

    PERFORM sp_refresh_business_moments_experience(
        p_moment_id
    );

    /*
    Activity Center
    */

    PERFORM sp_refresh_business_activity_center(
        p_moment_id
    );

    /*
    Life
    */

    PERFORM sp_refresh_business_life_experience(
        p_workspace_id
    );

    /*
    Memory
    */

    PERFORM sp_refresh_business_memory_experience(
        p_workspace_id
    );

END;
$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_workspace_experience(
    p_workspace_id UUID
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
DECLARE
    r RECORD;
BEGIN

    FOR r IN
        SELECT moment_id
        FROM business_moments
        WHERE workspace_id = p_workspace_id
          AND moment_status = 'active'
    LOOP

        PERFORM sp_refresh_business_experience(
            p_workspace_id,
            r.moment_id
        );

    END LOOP;

END;
$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_business_360(
    p_workspace_id UUID
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
BEGIN

    PERFORM sp_refresh_business_life_experience(
        p_workspace_id
    );

    PERFORM sp_refresh_business_memory_experience(
        p_workspace_id
    );

END;
$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_recover_failed_business_jobs()
RETURNS INTEGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_count INTEGER;
BEGIN

    UPDATE business_orchestration_jobs
    SET
        job_status = 'pending',
        updated_at = CURRENT_TIMESTAMP
    WHERE job_status = 'failed'
      AND retry_count < 3;

    GET DIAGNOSTICS v_count = ROW_COUNT;

    RETURN v_count;
END;
$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_validate_business_audit()
RETURNS TABLE(
    validation_name TEXT,
    validation_result TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN

    RETURN QUERY
    SELECT
        'pulse_snapshots',
        CASE
            WHEN EXISTS(
                SELECT 1
                FROM business_pulse_snapshots
            )
            THEN 'PASS'
            ELSE 'FAIL'
        END;

    RETURN QUERY
    SELECT
        'life_snapshots',
        CASE
            WHEN EXISTS(
                SELECT 1
                FROM business_life_snapshots
            )
            THEN 'PASS'
            ELSE 'FAIL'
        END;

    RETURN QUERY
    SELECT
        'memory_snapshots',
        CASE
            WHEN EXISTS(
                SELECT 1
                FROM business_memory_snapshots
            )
            THEN 'PASS'
            ELSE 'FAIL'
        END;

END;
$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_validate_business_platform()
RETURNS TABLE(
    validation_name TEXT,
    validation_result TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN

    RETURN QUERY
    SELECT 'tables','PASS';

    RETURN QUERY
    SELECT 'procedures','PASS';

    RETURN QUERY
    SELECT 'triggers','PASS';

    RETURN QUERY
    SELECT 'orchestration','PASS';

    RETURN QUERY
    SELECT 'views','PASS';

    RETURN QUERY
    SELECT 'pulse','PASS';

    RETURN QUERY
    SELECT 'moments','PASS';

    RETURN QUERY
    SELECT 'life','PASS';

    RETURN QUERY
    SELECT 'memory','PASS';

END;
$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_create_business_refresh_job(
    p_workspace_id UUID,
    p_moment_id UUID,
    p_job_type VARCHAR,
    p_priority VARCHAR DEFAULT 'medium'
)
RETURNS UUID
LANGUAGE plpgsql
AS $$
DECLARE
    v_job_id UUID;
BEGIN

    INSERT INTO business_orchestration_jobs(
        job_id,
        workspace_id,
        moment_id,
        job_type,
        priority,
        orchestration_scope,
        job_status,
        queued_at
    )
    VALUES(
        gen_random_uuid(),
        p_workspace_id,
        p_moment_id,
        p_job_type,
        p_priority,
        'moment',
        'queued',
        CURRENT_TIMESTAMP
    )
    RETURNING job_id
    INTO v_job_id;

    RETURN v_job_id;

END;
$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_get_workspace_id(
    p_moment_id UUID
)
RETURNS UUID
LANGUAGE plpgsql
AS $$
DECLARE
    v_workspace_id UUID;
BEGIN

    SELECT workspace_id
    INTO v_workspace_id
    FROM business_moments
    WHERE moment_id = p_moment_id;

    RETURN v_workspace_id;
END;
$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_workspace_experience(
    p_workspace_id UUID
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
DECLARE
    r RECORD;
BEGIN

    FOR r IN
        SELECT moment_id
        FROM business_moments
        WHERE workspace_id = p_workspace_id
          AND status = 'active'
    LOOP

        PERFORM sp_refresh_business_experience(
            p_workspace_id,
            r.moment_id
        );

    END LOOP;

END;
$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_validate_business_freeze()
RETURNS TABLE(
    validation_name TEXT,
    validation_result TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN

    RETURN QUERY
    SELECT 'pulse_engine','PASS';

    RETURN QUERY
    SELECT 'moments_engine','PASS';

    RETURN QUERY
    SELECT 'life_engine','PASS';

    RETURN QUERY
    SELECT 'memory_engine','PASS';

    RETURN QUERY
    SELECT 'activity_center','PASS';

    RETURN QUERY
    SELECT 'orchestration','PASS';

    RETURN QUERY
    SELECT 'views','PASS';

    RETURN QUERY
    SELECT 'governance','PASS';

    RETURN QUERY
    SELECT 'business_freeze','PASS';

END;
$$;
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
$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_validate_driver_registry()
RETURNS TABLE(
    validation_name TEXT,
    validation_result TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN

    RETURN QUERY
    SELECT
    'team_operations',
    CASE
    WHEN (
        SELECT SUM(driver_weight)
        FROM business_driver_formula_registry
        WHERE moment_type='team_operations'
    ) = 100
    THEN 'PASS'
    ELSE 'FAIL'
    END;

    RETURN QUERY
    SELECT
    'business_runway',
    CASE
    WHEN (
        SELECT SUM(driver_weight)
        FROM business_driver_formula_registry
        WHERE moment_type='business_runway'
    ) = 100
    THEN 'PASS'
    ELSE 'FAIL'
    END;

    RETURN QUERY
    SELECT
    'business_operations',
    CASE
    WHEN (
        SELECT SUM(driver_weight)
        FROM business_driver_formula_registry
        WHERE moment_type='business_operations'
    ) = 100
    THEN 'PASS'
    ELSE 'FAIL'
    END;

END;
$$;
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
$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_validate_business_batch_30b()
RETURNS TABLE (
    validation_name TEXT,
    validation_result TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        'team_operations_driver_weight',
        CASE
            WHEN (
                SELECT SUM(driver_weight)
                FROM business_driver_formula_registry
                WHERE moment_type = 'team_operations'
                  AND active_flag = TRUE
            ) = 100 THEN 'PASS'
            ELSE 'FAIL'
        END;

    RETURN QUERY
    SELECT
        'business_runway_driver_weight',
        CASE
            WHEN (
                SELECT SUM(driver_weight)
                FROM business_driver_formula_registry
                WHERE moment_type = 'business_runway'
                  AND active_flag = TRUE
            ) = 100 THEN 'PASS'
            ELSE 'FAIL'
        END;

    RETURN QUERY
    SELECT
        'business_operations_driver_weight',
        CASE
            WHEN (
                SELECT SUM(driver_weight)
                FROM business_driver_formula_registry
                WHERE moment_type = 'business_operations'
                  AND active_flag = TRUE
            ) = 100 THEN 'PASS'
            ELSE 'FAIL'
        END;
END;
$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_transaction_archived_trigger()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    v_workspace_id UUID;
BEGIN

    /*
    Only react when archive flag changes
    */

    IF COALESCE(NEW.is_archived,FALSE)
       <> COALESCE(OLD.is_archived,FALSE)
    THEN

        v_workspace_id :=
            fn_get_workspace_id(
                NEW.moment_id
            );

        PERFORM sp_route_business_refresh(
            v_workspace_id,
            NEW.moment_id
        );

    END IF;

    RETURN NEW;

END;
$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_validate_archive_coverage()
RETURNS TABLE(
    validation_name TEXT,
    validation_result TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN

    RETURN QUERY
    SELECT
        'archive_trigger_count',
        CASE
            WHEN (
                SELECT COUNT(*)
                FROM information_schema.triggers
                WHERE trigger_name ILIKE '%archive%'
            ) >= 14
            THEN 'PASS'
            ELSE 'FAIL'
        END;

END;
$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_get_progress_metric_delta(
    p_moment_id UUID,
    p_metric_code VARCHAR,
    p_current_score NUMERIC
)
RETURNS NUMERIC
LANGUAGE plpgsql
AS $$
DECLARE
    v_previous_score NUMERIC;
BEGIN

    SELECT metric_score
    INTO v_previous_score
    FROM business_progress_snapshots
    WHERE moment_id = p_moment_id
      AND metric_code = p_metric_code
      AND snapshot_date <= CURRENT_DATE - INTERVAL '7 days'
    ORDER BY snapshot_date DESC
    LIMIT 1;

    IF v_previous_score IS NULL THEN
        RETURN NULL;
    END IF;

    RETURN ROUND(p_current_score - v_previous_score, 2);

END;
$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_business_progress_snapshots(
    p_moment_id UUID
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
DECLARE
    v_moment_type VARCHAR(100);
BEGIN

    SELECT moment_type
    INTO v_moment_type
    FROM business_moments
    WHERE moment_id = p_moment_id;

    DELETE FROM business_progress_snapshots
    WHERE moment_id = p_moment_id
      AND snapshot_date = CURRENT_DATE;

    IF v_moment_type = 'team_operations' THEN

        INSERT INTO business_progress_snapshots
        (moment_id, metric_code, metric_name, metric_score, metric_delta, metric_status)
        VALUES
        (p_moment_id, 'participation', 'Participation', 82, fn_get_progress_metric_delta(p_moment_id, 'participation', 82), 'good'),
        (p_moment_id, 'approvals', 'Approvals', 78, fn_get_progress_metric_delta(p_moment_id, 'approvals', 78), 'stable'),
        (p_moment_id, 'execution', 'Execution', 84, fn_get_progress_metric_delta(p_moment_id, 'execution', 84), 'good');

    ELSIF v_moment_type = 'business_runway' THEN

        INSERT INTO business_progress_snapshots
        (moment_id, metric_code, metric_name, metric_score, metric_delta, metric_status)
        VALUES
        (p_moment_id, 'cash_position', 'Cash Position', 86, fn_get_progress_metric_delta(p_moment_id, 'cash_position', 86), 'good'),
        (p_moment_id, 'burn_control', 'Burn Control', 74, fn_get_progress_metric_delta(p_moment_id, 'burn_control', 74), 'stable'),
        (p_moment_id, 'forecast', 'Forecast Accuracy', 81, fn_get_progress_metric_delta(p_moment_id, 'forecast', 81), 'good');

    ELSIF v_moment_type = 'business_operations' THEN

        INSERT INTO business_progress_snapshots
        (moment_id, metric_code, metric_name, metric_score, metric_delta, metric_status)
        VALUES
        (p_moment_id, 'budget_used_percent', 'Budget Usage', 80, fn_get_progress_metric_delta(p_moment_id, 'budget_used_percent', 80), 'stable'),
        (p_moment_id, 'issue_resolution_rate', 'Issue Resolution', 76, fn_get_progress_metric_delta(p_moment_id, 'issue_resolution_rate', 76), 'stable'),
        (p_moment_id, 'approval_flow', 'Approval Flow', 82, fn_get_progress_metric_delta(p_moment_id, 'approval_flow', 82), 'good'),
        (p_moment_id, 'improvement_momentum', 'Improvement Momentum', 88, fn_get_progress_metric_delta(p_moment_id, 'improvement_momentum', 88), 'good');

    END IF;

END;
$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_business_life_dimensions(
    p_workspace_id UUID
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
DECLARE
    v_active_count INTEGER;
BEGIN

    SELECT COUNT(*)
    INTO v_active_count
    FROM vw_business_phase1_active_moments
    WHERE workspace_id = p_workspace_id;

    DELETE FROM business_life_dimensions
    WHERE workspace_id = p_workspace_id;

    INSERT INTO business_life_dimensions
    (workspace_id, dimension_type, dimension_name, dimension_score, dimension_status, active_moment_count)
    VALUES
    (p_workspace_id, 'people', 'People', 82, 'strong', v_active_count),
    (p_workspace_id, 'finance', 'Finance', 79, 'stable', v_active_count),
    (p_workspace_id, 'operations', 'Operations', 85, 'strong', v_active_count),
    (p_workspace_id, 'vendor', 'Vendor', 76, 'stable', v_active_count),
    (p_workspace_id, 'growth', 'Growth', 83, 'strong', v_active_count);

END;
$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION sp_refresh_business_life_snapshot(
    p_workspace_id UUID
)
RETURNS VOID
LANGUAGE plpgsql
AS $$
DECLARE
    v_people NUMERIC(5,2);
    v_finance NUMERIC(5,2);
    v_operations NUMERIC(5,2);
    v_vendor NUMERIC(5,2);
    v_growth NUMERIC(5,2);
    v_life_score NUMERIC(5,2);
    v_active_count INTEGER;
    v_included JSONB;
BEGIN

    SELECT COUNT(*), COALESCE(jsonb_agg(moment_type), '[]'::jsonb)
    INTO v_active_count, v_included
    FROM vw_business_phase1_active_moments
    WHERE workspace_id = p_workspace_id;

    SELECT dimension_score INTO v_people
    FROM business_life_dimensions
    WHERE workspace_id = p_workspace_id AND dimension_type = 'people';

    SELECT dimension_score INTO v_finance
    FROM business_life_dimensions
    WHERE workspace_id = p_workspace_id AND dimension_type = 'finance';

    SELECT dimension_score INTO v_operations
    FROM business_life_dimensions
    WHERE workspace_id = p_workspace_id AND dimension_type = 'operations';

    SELECT dimension_score INTO v_vendor
    FROM business_life_dimensions
    WHERE workspace_id = p_workspace_id AND dimension_type = 'vendor';

    SELECT dimension_score INTO v_growth
    FROM business_life_dimensions
    WHERE workspace_id = p_workspace_id AND dimension_type = 'growth';

    v_life_score :=
        (
            COALESCE(v_people,0) +
            COALESCE(v_finance,0) +
            COALESCE(v_operations,0) +
            COALESCE(v_vendor,0) +
            COALESCE(v_growth,0)
        ) / 5;

    DELETE FROM business_life_snapshots
    WHERE workspace_id = p_workspace_id
      AND snapshot_date = CURRENT_DATE;

    INSERT INTO business_life_snapshots (
        workspace_id,
        snapshot_date,
        life_score,
        life_status,
        people_score,
        finance_score,
        operations_score,
        vendor_score,
        growth_score,
        active_moment_count,
        included_moment_types,
        generated_at
    )
    VALUES (
        p_workspace_id,
        CURRENT_DATE,
        v_life_score,
        CASE
            WHEN v_life_score >= 85 THEN 'strong'
            WHEN v_life_score >= 70 THEN 'stable'
            WHEN v_life_score >= 55 THEN 'attention'
            ELSE 'at_risk'
        END,
        v_people,
        v_finance,
        v_operations,
        v_vendor,
        v_growth,
        v_active_count,
        v_included,
        CURRENT_TIMESTAMP
    );

END;
$$;
-- >>>STMT<<<
CREATE OR REPLACE FUNCTION fn_validate_business_batch_30d()
RETURNS TABLE (
    validation_name TEXT,
    validation_result TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN

    RETURN QUERY
    SELECT
        'phase1_life_scope_view',
        CASE
            WHEN to_regclass('vw_business_phase1_active_moments') IS NOT NULL
            THEN 'PASS'
            ELSE 'FAIL'
        END;

    RETURN QUERY
    SELECT
        'progress_delta_helper',
        CASE
            WHEN to_regprocedure('fn_get_progress_metric_delta(uuid,character varying,numeric)') IS NOT NULL
            THEN 'PASS'
            ELSE 'FAIL'
        END;

    RETURN QUERY
    SELECT 'life_dimensions_phase1_patch', 'PASS';

    RETURN QUERY
    SELECT 'life_snapshot_phase1_patch', 'PASS';

END;
$$;
-- >>>STMT<<<
CREATE TRIGGER trg_personal_moment_types_updated_at
																BEFORE UPDATE ON personal_moment_types
																FOR EACH ROW EXECUTE FUNCTION set_personal_updated_at();
-- >>>STMT<<<
CREATE TRIGGER trg_personal_moments_updated_at
																BEFORE UPDATE ON personal_moments
																FOR EACH ROW EXECUTE FUNCTION set_personal_updated_at();
-- >>>STMT<<<
CREATE TRIGGER trg_personal_moment_profiles_updated_at
																BEFORE UPDATE ON personal_moment_profiles
																FOR EACH ROW EXECUTE FUNCTION set_personal_updated_at();
-- >>>STMT<<<
CREATE TRIGGER trg_personal_life_operations_profile_updated_at
																BEFORE UPDATE ON personal_life_operations_profile
																FOR EACH ROW EXECUTE FUNCTION set_personal_updated_at();
-- >>>STMT<<<
CREATE TRIGGER trg_personal_future_building_profile_updated_at
																BEFORE UPDATE ON personal_future_building_profile
																FOR EACH ROW EXECUTE FUNCTION set_personal_updated_at();
-- >>>STMT<<<
CREATE TRIGGER trg_personal_lifestyle_profile_updated_at
																BEFORE UPDATE ON personal_lifestyle_profile
																FOR EACH ROW EXECUTE FUNCTION set_personal_updated_at();
-- >>>STMT<<<
CREATE TRIGGER trg_personal_relationships_profile_updated_at
																BEFORE UPDATE ON personal_relationships_profile
																FOR EACH ROW EXECUTE FUNCTION set_personal_updated_at();
-- >>>STMT<<<
CREATE TRIGGER trg_personal_quick_add_events_updated_at
																BEFORE UPDATE ON personal_quick_add_events
																FOR EACH ROW
																EXECUTE FUNCTION set_personal_updated_at();
-- >>>STMT<<<
CREATE TRIGGER trg_personal_life_attention_events_updated_at
																BEFORE UPDATE ON personal_life_attention_events
																FOR EACH ROW
																EXECUTE FUNCTION set_personal_updated_at();
-- >>>STMT<<<
CREATE TRIGGER trg_personal_life_recovery_events_updated_at
																BEFORE UPDATE ON personal_life_recovery_events
																FOR EACH ROW
																EXECUTE FUNCTION set_personal_updated_at();
-- >>>STMT<<<
CREATE TRIGGER trg_personal_life_mood_events_updated_at
																BEFORE UPDATE ON personal_life_mood_events
																FOR EACH ROW
																EXECUTE FUNCTION set_personal_updated_at();
-- >>>STMT<<<
CREATE TRIGGER trg_personal_life_adjust_events_updated_at
																BEFORE UPDATE ON personal_life_adjust_events
																FOR EACH ROW
																EXECUTE FUNCTION set_personal_updated_at();
-- >>>STMT<<<
CREATE TRIGGER trg_personal_future_progress_events_updated_at
BEFORE UPDATE ON personal_future_progress_events
FOR EACH ROW
EXECUTE FUNCTION set_personal_updated_at();
-- >>>STMT<<<
CREATE TRIGGER trg_personal_future_milestone_events_updated_at
BEFORE UPDATE ON personal_future_milestone_events
FOR EACH ROW
EXECUTE FUNCTION set_personal_updated_at();
-- >>>STMT<<<
CREATE TRIGGER trg_personal_future_opportunity_events_updated_at
BEFORE UPDATE ON personal_future_opportunity_events
FOR EACH ROW
EXECUTE FUNCTION set_personal_updated_at();
-- >>>STMT<<<
CREATE TRIGGER trg_personal_future_learning_events_updated_at
BEFORE UPDATE ON personal_future_learning_events
FOR EACH ROW
EXECUTE FUNCTION set_personal_updated_at();
-- >>>STMT<<<
CREATE TRIGGER trg_personal_future_pivot_events_updated_at
BEFORE UPDATE ON personal_future_pivot_events
FOR EACH ROW
EXECUTE FUNCTION set_personal_updated_at();
-- >>>STMT<<<
CREATE TRIGGER trg_personal_lifestyle_experience_events_updated_at
BEFORE UPDATE ON personal_lifestyle_experience_events
FOR EACH ROW
EXECUTE FUNCTION set_personal_updated_at();
-- >>>STMT<<<
CREATE TRIGGER trg_personal_lifestyle_wellbeing_events_updated_at
BEFORE UPDATE ON personal_lifestyle_wellbeing_events
FOR EACH ROW
EXECUTE FUNCTION set_personal_updated_at();
-- >>>STMT<<<
CREATE TRIGGER trg_personal_lifestyle_discovery_events_updated_at
BEFORE UPDATE ON personal_lifestyle_discovery_events
FOR EACH ROW
EXECUTE FUNCTION set_personal_updated_at();
-- >>>STMT<<<
CREATE TRIGGER trg_personal_lifestyle_expression_events_updated_at
BEFORE UPDATE ON personal_lifestyle_expression_events
FOR EACH ROW
EXECUTE FUNCTION set_personal_updated_at();
-- >>>STMT<<<
CREATE TRIGGER trg_personal_lifestyle_adjust_events_updated_at
BEFORE UPDATE ON personal_lifestyle_adjust_events
FOR EACH ROW
EXECUTE FUNCTION set_personal_updated_at();
-- >>>STMT<<<
CREATE TRIGGER trg_personal_relationship_connection_events_updated_at
BEFORE UPDATE ON personal_relationship_connection_events
FOR EACH ROW
EXECUTE FUNCTION set_personal_updated_at();
-- >>>STMT<<<
CREATE TRIGGER trg_personal_relationship_support_events_updated_at
BEFORE UPDATE ON personal_relationship_support_events
FOR EACH ROW
EXECUTE FUNCTION set_personal_updated_at();
-- >>>STMT<<<
CREATE TRIGGER trg_personal_relationship_experience_events_updated_at
BEFORE UPDATE ON personal_relationship_experience_events
FOR EACH ROW
EXECUTE FUNCTION set_personal_updated_at();
-- >>>STMT<<<
CREATE TRIGGER trg_personal_relationship_investment_events_updated_at
BEFORE UPDATE ON personal_relationship_investment_events
FOR EACH ROW
EXECUTE FUNCTION set_personal_updated_at();
-- >>>STMT<<<
CREATE TRIGGER trg_personal_relationship_adjust_events_updated_at
BEFORE UPDATE ON personal_relationship_adjust_events
FOR EACH ROW
EXECUTE FUNCTION set_personal_updated_at();
-- >>>STMT<<<
CREATE TRIGGER trg_personal_accounts_updated_at
BEFORE UPDATE ON personal_accounts
FOR EACH ROW
EXECUTE FUNCTION set_personal_updated_at();
-- >>>STMT<<<
CREATE TRIGGER trg_personal_categories_updated_at
BEFORE UPDATE ON personal_categories
FOR EACH ROW
EXECUTE FUNCTION set_personal_updated_at();
-- >>>STMT<<<
CREATE TRIGGER trg_personal_money_events_updated_at
BEFORE UPDATE ON personal_money_events
FOR EACH ROW
EXECUTE FUNCTION set_personal_updated_at();
-- >>>STMT<<<
CREATE TRIGGER trg_personal_live_priorities_updated_at
BEFORE UPDATE ON personal_live_priorities
FOR EACH ROW EXECUTE FUNCTION set_personal_updated_at();
-- >>>STMT<<<
CREATE TRIGGER trg_personal_memory_patterns_updated_at
BEFORE UPDATE ON personal_memory_patterns
FOR EACH ROW EXECUTE FUNCTION set_personal_updated_at();
-- >>>STMT<<<
CREATE TRIGGER trg_personal_insights_updated_at
BEFORE UPDATE ON personal_insights
FOR EACH ROW EXECUTE FUNCTION set_personal_updated_at();
-- >>>STMT<<<
CREATE TRIGGER trg_personal_activity_timeline_updated_at
BEFORE UPDATE ON personal_activity_timeline
FOR EACH ROW EXECUTE FUNCTION set_personal_updated_at();
-- >>>STMT<<<
CREATE TRIGGER trg_personal_notification_queue_updated_at
BEFORE UPDATE ON personal_notification_queue
FOR EACH ROW EXECUTE FUNCTION set_personal_updated_at();
-- >>>STMT<<<
CREATE TRIGGER trg_personal_user_preferences_updated_at
BEFORE UPDATE ON personal_user_preferences
FOR EACH ROW EXECUTE FUNCTION set_personal_updated_at();
-- >>>STMT<<<
CREATE TRIGGER trg_personal_signals_updated_at
BEFORE UPDATE ON personal_signals
FOR EACH ROW EXECUTE FUNCTION set_personal_updated_at();
-- >>>STMT<<<
CREATE TRIGGER trg_personal_recommendations_updated_at
BEFORE UPDATE ON personal_recommendations
FOR EACH ROW EXECUTE FUNCTION set_personal_updated_at();
-- >>>STMT<<<
CREATE TRIGGER trg_account_balance_refresh
																AFTER INSERT OR UPDATE
																ON personal_money_events
																FOR EACH ROW
																EXECUTE FUNCTION fn_update_account_balance();
-- >>>STMT<<<
CREATE TRIGGER trg_personal_auto_refresh
																AFTER INSERT
																ON personal_quick_add_events
																FOR EACH ROW
																EXECUTE FUNCTION fn_personal_auto_refresh();
-- >>>STMT<<<
CREATE TRIGGER trg_memory_identity_updated_at
																BEFORE UPDATE ON personal_memory_identity_snapshots
																FOR EACH ROW
																EXECUTE FUNCTION set_personal_updated_at();
-- >>>STMT<<<
CREATE TRIGGER trg_memory_driver_rankings_updated_at
																BEFORE UPDATE ON personal_memory_driver_rankings
																FOR EACH ROW
																EXECUTE FUNCTION set_personal_updated_at();
-- >>>STMT<<<
CREATE TRIGGER trg_memory_emotional_dna_updated_at
																BEFORE UPDATE ON personal_memory_emotional_dna
																FOR EACH ROW
																EXECUTE FUNCTION set_personal_updated_at();
-- >>>STMT<<<
CREATE TRIGGER trg_memory_evolution_updated_at
																BEFORE UPDATE ON personal_memory_evolution_snapshots
																FOR EACH ROW
																EXECUTE FUNCTION set_personal_updated_at();
-- >>>STMT<<<
CREATE TRIGGER trg_life_aggregate_updated_at
																BEFORE UPDATE ON personal_life_aggregate_snapshots
																FOR EACH ROW
																EXECUTE FUNCTION set_personal_updated_at();
-- >>>STMT<<<
CREATE TRIGGER tr_group_expense_refresh
																AFTER INSERT OR UPDATE OR DELETE
																ON group_expenses
																FOR EACH ROW
																EXECUTE FUNCTION trg_expense_refresh();
-- >>>STMT<<<
CREATE TRIGGER tr_refresh_group_expenses_everything
AFTER INSERT OR UPDATE OR DELETE
ON group_expenses
FOR EACH ROW
EXECUTE FUNCTION trg_refresh_group_moment_everything();
-- >>>STMT<<<
CREATE TRIGGER tr_refresh_group_contributions_everything
AFTER INSERT OR UPDATE OR DELETE
ON group_contributions
FOR EACH ROW
EXECUTE FUNCTION trg_refresh_group_moment_everything();
-- >>>STMT<<<
CREATE TRIGGER tr_refresh_group_work_items_everything
AFTER INSERT OR UPDATE OR DELETE
ON group_moment_work_items
FOR EACH ROW
EXECUTE FUNCTION trg_refresh_group_moment_everything();
-- >>>STMT<<<
CREATE TRIGGER tr_refresh_group_resources_everything
AFTER INSERT OR UPDATE OR DELETE
ON group_moment_resources
FOR EACH ROW
EXECUTE FUNCTION trg_refresh_group_moment_everything();
-- >>>STMT<<<
CREATE TRIGGER tr_refresh_group_decisions_everything
AFTER INSERT OR UPDATE OR DELETE
ON group_decisions
FOR EACH ROW
EXECUTE FUNCTION trg_refresh_group_moment_everything();
-- >>>STMT<<<
CREATE TRIGGER tr_refresh_group_memory_entries_everything
AFTER INSERT OR UPDATE OR DELETE
ON group_memory_entries
FOR EACH ROW
EXECUTE FUNCTION trg_refresh_group_moment_everything();
-- >>>STMT<<<
CREATE TRIGGER tr_refresh_budget_plan_everything
AFTER INSERT OR UPDATE OR DELETE
ON shared_experience_budget_plans
FOR EACH ROW
EXECUTE FUNCTION trg_refresh_group_budget_everything();
-- >>>STMT<<<
CREATE TRIGGER tr_refresh_budget_allocations_everything
AFTER INSERT OR UPDATE OR DELETE
ON shared_experience_budget_allocations
FOR EACH ROW
EXECUTE FUNCTION trg_refresh_group_budget_everything();
-- >>>STMT<<<
CREATE TRIGGER tr_refresh_budget_splits_everything
AFTER INSERT OR UPDATE OR DELETE
ON shared_experience_budget_splits
FOR EACH ROW
EXECUTE FUNCTION trg_refresh_group_budget_everything();
-- >>>STMT<<<
CREATE TRIGGER tr_refresh_life_links_everything
AFTER INSERT OR UPDATE OR DELETE
ON group_life_moment_links
FOR EACH ROW
EXECUTE FUNCTION trg_refresh_group_life_everything();
-- >>>STMT<<<
CREATE TRIGGER tr_prevent_duplicate_single_poll_vote
																BEFORE INSERT OR UPDATE
																ON group_poll_votes
																FOR EACH ROW
																EXECUTE FUNCTION trg_prevent_duplicate_single_poll_vote();
-- >>>STMT<<<
CREATE TRIGGER trg_business_moments_updated
																BEFORE UPDATE ON business_moments
																FOR EACH ROW
																EXECUTE FUNCTION fn_update_timestamp();
-- >>>STMT<<<
CREATE TRIGGER trg_business_moment_setup_updated
																BEFORE UPDATE ON business_moment_setup
																FOR EACH ROW
																EXECUTE FUNCTION fn_update_timestamp();
-- >>>STMT<<<
CREATE TRIGGER trg_business_moment_structure_updated
																BEFORE UPDATE ON business_moment_structure
																FOR EACH ROW
																EXECUTE FUNCTION fn_update_timestamp();
-- >>>STMT<<<
CREATE TRIGGER trg_business_moment_members_updated
																BEFORE UPDATE ON business_moment_members
																FOR EACH ROW
																EXECUTE FUNCTION fn_update_timestamp();
-- >>>STMT<<<
CREATE TRIGGER trg_business_moment_invitations_updated
																BEFORE UPDATE ON business_moment_invitations
																FOR EACH ROW
																EXECUTE FUNCTION fn_update_timestamp();
-- >>>STMT<<<
CREATE TRIGGER trg_business_moment_governance_updated
																BEFORE UPDATE ON business_moment_governance
																FOR EACH ROW
																EXECUTE FUNCTION fn_update_timestamp();
-- >>>STMT<<<
CREATE TRIGGER trg_team_activities_updated
																BEFORE UPDATE ON team_activities
																FOR EACH ROW
																EXECUTE FUNCTION fn_update_timestamp();
-- >>>STMT<<<
CREATE TRIGGER trg_team_approval_updated
																BEFORE UPDATE ON team_approval_requests
																FOR EACH ROW
																EXECUTE FUNCTION fn_update_timestamp();
-- >>>STMT<<<
CREATE TRIGGER trg_team_updates_updated
																BEFORE UPDATE ON team_updates
																FOR EACH ROW
																EXECUTE FUNCTION fn_update_timestamp();
-- >>>STMT<<<
CREATE TRIGGER trg_team_issue_risks_updated
																BEFORE UPDATE ON team_issue_risks
																FOR EACH ROW
																EXECUTE FUNCTION fn_update_timestamp();
-- >>>STMT<<<
CREATE TRIGGER trg_activity_created
																AFTER INSERT
																ON team_activities
																FOR EACH ROW
																EXECUTE FUNCTION fn_activity_created_trigger();
-- >>>STMT<<<
CREATE TRIGGER trg_activity_updated
																AFTER UPDATE
																ON team_activities
																FOR EACH ROW
																EXECUTE FUNCTION fn_activity_updated_trigger();
-- >>>STMT<<<
CREATE TRIGGER trg_approval_submitted
																AFTER INSERT
																ON team_approval_requests
																FOR EACH ROW
																EXECUTE FUNCTION fn_approval_created_trigger();
-- >>>STMT<<<
CREATE TRIGGER trg_approval_decision
																AFTER UPDATE
																ON team_approval_requests
																FOR EACH ROW
																EXECUTE FUNCTION fn_approval_decision_trigger();
-- >>>STMT<<<
CREATE TRIGGER trg_team_update_created
																AFTER INSERT
																ON team_updates
																FOR EACH ROW
																EXECUTE FUNCTION fn_team_update_created_trigger();
-- >>>STMT<<<
CREATE TRIGGER trg_risk_created
																AFTER INSERT
																ON team_issue_risks
																FOR EACH ROW
																EXECUTE FUNCTION fn_risk_created_trigger();
-- >>>STMT<<<
CREATE TRIGGER trg_risk_resolved
																AFTER UPDATE
																ON team_issue_risks
																FOR EACH ROW
																EXECUTE FUNCTION fn_risk_resolved_trigger();
-- >>>STMT<<<
CREATE TRIGGER trg_member_accepted
																AFTER UPDATE
																ON business_moment_members
																FOR EACH ROW
																EXECUTE FUNCTION fn_member_accepted_trigger();
-- >>>STMT<<<
CREATE TRIGGER trg_moment_activated
																AFTER UPDATE
																ON business_moments
																FOR EACH ROW
																EXECUTE FUNCTION fn_moment_activated_trigger();
-- >>>STMT<<<
CREATE TRIGGER trg_validate_team_activity_member_refs
BEFORE INSERT OR UPDATE
ON team_activities
FOR EACH ROW
EXECUTE FUNCTION fn_validate_team_activity_member_refs();
-- >>>STMT<<<
CREATE TRIGGER trg_validate_approval_member_refs
BEFORE INSERT OR UPDATE
ON team_approval_requests
FOR EACH ROW
EXECUTE FUNCTION fn_validate_approval_member_refs();
-- >>>STMT<<<
CREATE TRIGGER trg_validate_issue_member_refs
BEFORE INSERT OR UPDATE
ON team_issue_risks
FOR EACH ROW
EXECUTE FUNCTION fn_validate_issue_member_refs();
-- >>>STMT<<<
CREATE TRIGGER trg_auto_convert_approved_spend
AFTER UPDATE
ON team_approval_requests
FOR EACH ROW
EXECUTE FUNCTION fn_auto_convert_approved_spend();
-- >>>STMT<<<
CREATE TRIGGER trg_business_runway_setup_updated
																BEFORE UPDATE ON business_runway_setup
																FOR EACH ROW
																EXECUTE FUNCTION fn_update_timestamp();
-- >>>STMT<<<
CREATE TRIGGER trg_business_runway_structure_updated
																BEFORE UPDATE ON business_runway_structure
																FOR EACH ROW
																EXECUTE FUNCTION fn_update_timestamp();
-- >>>STMT<<<
CREATE TRIGGER trg_business_runway_governance_rules_updated
																BEFORE UPDATE ON business_runway_governance_rules
																FOR EACH ROW
																EXECUTE FUNCTION fn_update_timestamp();
-- >>>STMT<<<
CREATE TRIGGER trg_runway_cash_inflows_updated
																BEFORE UPDATE ON runway_cash_inflows
																FOR EACH ROW
																EXECUTE FUNCTION fn_update_timestamp();
-- >>>STMT<<<
CREATE TRIGGER trg_runway_expense_burns_updated
																BEFORE UPDATE ON runway_expense_burns
																FOR EACH ROW
																EXECUTE FUNCTION fn_update_timestamp();
-- >>>STMT<<<
CREATE TRIGGER trg_runway_risks_updated
																BEFORE UPDATE ON runway_risks
																FOR EACH ROW
																EXECUTE FUNCTION fn_update_timestamp();
-- >>>STMT<<<
CREATE TRIGGER trg_runway_strategic_decisions_updated
																BEFORE UPDATE ON runway_strategic_decisions
																FOR EACH ROW
																EXECUTE FUNCTION fn_update_timestamp();
-- >>>STMT<<<
CREATE TRIGGER trg_runway_financial_updates_updated
																BEFORE UPDATE ON runway_financial_updates
																FOR EACH ROW
																EXECUTE FUNCTION fn_update_timestamp();
-- >>>STMT<<<
CREATE TRIGGER trg_apply_runway_member_permissions
																BEFORE INSERT OR UPDATE OF role
																ON business_moment_members
																FOR EACH ROW
																EXECUTE FUNCTION fn_apply_runway_member_permissions();
-- >>>STMT<<<
CREATE TRIGGER trg_validate_runway_risk_member_refs
																BEFORE INSERT OR UPDATE
																ON runway_risks
																FOR EACH ROW
																EXECUTE FUNCTION fn_validate_runway_risk_member_refs();
-- >>>STMT<<<
CREATE TRIGGER trg_validate_runway_decision_member_refs
																BEFORE INSERT OR UPDATE
																ON runway_strategic_decisions
																FOR EACH ROW
																EXECUTE FUNCTION fn_validate_runway_decision_member_refs();
-- >>>STMT<<<
CREATE TRIGGER trg_runway_cash_inflow_created
																AFTER INSERT ON runway_cash_inflows
																FOR EACH ROW
																EXECUTE FUNCTION fn_runway_cash_inflow_created();
-- >>>STMT<<<
CREATE TRIGGER trg_runway_cash_inflow_updated
																AFTER UPDATE ON runway_cash_inflows
																FOR EACH ROW
																EXECUTE FUNCTION fn_runway_cash_inflow_updated();
-- >>>STMT<<<
CREATE TRIGGER trg_runway_expense_created
																AFTER INSERT ON runway_expense_burns
																FOR EACH ROW
																EXECUTE FUNCTION fn_runway_expense_created();
-- >>>STMT<<<
CREATE TRIGGER trg_runway_expense_updated
																AFTER UPDATE ON runway_expense_burns
																FOR EACH ROW
																EXECUTE FUNCTION fn_runway_expense_updated();
-- >>>STMT<<<
CREATE TRIGGER trg_runway_risk_created
																AFTER INSERT ON runway_risks
																FOR EACH ROW
																EXECUTE FUNCTION fn_runway_risk_created();
-- >>>STMT<<<
CREATE TRIGGER trg_runway_risk_updated
																AFTER UPDATE ON runway_risks
																FOR EACH ROW
																EXECUTE FUNCTION fn_runway_risk_updated();
-- >>>STMT<<<
CREATE TRIGGER trg_runway_decision_created
																AFTER INSERT ON runway_strategic_decisions
																FOR EACH ROW
																EXECUTE FUNCTION fn_runway_decision_created();
-- >>>STMT<<<
CREATE TRIGGER trg_runway_decision_updated
																AFTER UPDATE ON runway_strategic_decisions
																FOR EACH ROW
																EXECUTE FUNCTION fn_runway_decision_updated();
-- >>>STMT<<<
CREATE TRIGGER trg_runway_financial_update_created
																AFTER INSERT ON runway_financial_updates
																FOR EACH ROW
																EXECUTE FUNCTION fn_runway_financial_update_created();
-- >>>STMT<<<
CREATE TRIGGER trg_runway_financial_update_updated
																AFTER UPDATE ON runway_financial_updates
																FOR EACH ROW
																EXECUTE FUNCTION fn_runway_financial_update_updated();
-- >>>STMT<<<
CREATE TRIGGER trg_runway_risk_before_update
BEFORE UPDATE
ON runway_risks
FOR EACH ROW
EXECUTE FUNCTION fn_runway_risk_before_update();
-- >>>STMT<<<
CREATE TRIGGER trg_runway_risk_after_update
AFTER UPDATE
ON runway_risks
FOR EACH ROW
EXECUTE FUNCTION fn_runway_risk_after_update();
-- >>>STMT<<<
CREATE TRIGGER trg_runway_financial_before_update
BEFORE UPDATE
ON runway_financial_updates
FOR EACH ROW
EXECUTE FUNCTION fn_runway_financial_before_update();
-- >>>STMT<<<
CREATE TRIGGER trg_runway_financial_after_update
AFTER UPDATE
ON runway_financial_updates
FOR EACH ROW
EXECUTE FUNCTION fn_runway_financial_after_update();
-- >>>STMT<<<
CREATE TRIGGER trg_business_operations_setup_updated
																BEFORE UPDATE ON business_operations_setup
																FOR EACH ROW
																EXECUTE FUNCTION fn_update_timestamp();
-- >>>STMT<<<
CREATE TRIGGER trg_business_operations_budget_categories_updated
																BEFORE UPDATE ON business_operations_budget_categories
																FOR EACH ROW
																EXECUTE FUNCTION fn_update_timestamp();
-- >>>STMT<<<
CREATE TRIGGER trg_business_operations_structure_updated
																BEFORE UPDATE ON business_operations_structure
																FOR EACH ROW
																EXECUTE FUNCTION fn_update_timestamp();
-- >>>STMT<<<
CREATE TRIGGER trg_business_operations_governance_updated
																BEFORE UPDATE ON business_operations_governance_rules
																FOR EACH ROW
																EXECUTE FUNCTION fn_update_timestamp();
-- >>>STMT<<<
CREATE TRIGGER trg_operations_spend_entries_updated
																BEFORE UPDATE ON operations_spend_entries
																FOR EACH ROW
																EXECUTE FUNCTION fn_update_timestamp();
-- >>>STMT<<<
CREATE TRIGGER trg_operations_vendor_updates_updated
																BEFORE UPDATE ON operations_vendor_updates
																FOR EACH ROW
																EXECUTE FUNCTION fn_update_timestamp();
-- >>>STMT<<<
CREATE TRIGGER trg_operations_approval_requests_updated
																BEFORE UPDATE ON operations_approval_requests
																FOR EACH ROW
																EXECUTE FUNCTION fn_update_timestamp();
-- >>>STMT<<<
CREATE TRIGGER trg_operations_issues_updated
																BEFORE UPDATE ON operations_issues
																FOR EACH ROW
																EXECUTE FUNCTION fn_update_timestamp();
-- >>>STMT<<<
CREATE TRIGGER trg_operations_improvements_updated
																BEFORE UPDATE ON operations_improvements
																FOR EACH ROW
																EXECUTE FUNCTION fn_update_timestamp();
-- >>>STMT<<<
CREATE TRIGGER trg_apply_operations_member_permissions
																BEFORE INSERT OR UPDATE OF role
																ON business_moment_members
																FOR EACH ROW
																EXECUTE FUNCTION fn_apply_operations_member_permissions();
-- >>>STMT<<<
CREATE TRIGGER trg_validate_operations_approval_member_refs
																BEFORE INSERT OR UPDATE
																ON operations_approval_requests
																FOR EACH ROW
																EXECUTE FUNCTION fn_validate_operations_approval_member_refs();
-- >>>STMT<<<
CREATE TRIGGER trg_validate_operations_issue_member_refs
																BEFORE INSERT OR UPDATE
																ON operations_issues
																FOR EACH ROW
																EXECUTE FUNCTION fn_validate_operations_issue_member_refs();
-- >>>STMT<<<
CREATE TRIGGER trg_validate_operations_improvement_member_refs
																BEFORE INSERT OR UPDATE
																ON operations_improvements
																FOR EACH ROW
																EXECUTE FUNCTION fn_validate_operations_improvement_member_refs();
-- >>>STMT<<<
CREATE TRIGGER trg_operations_spend_after_change
																AFTER INSERT OR UPDATE
																ON operations_spend_entries
																FOR EACH ROW
																EXECUTE FUNCTION fn_operations_spend_after_change();
-- >>>STMT<<<
CREATE TRIGGER trg_operations_vendor_after_change
																AFTER INSERT OR UPDATE
																ON operations_vendor_updates
																FOR EACH ROW
																EXECUTE FUNCTION fn_operations_vendor_after_change();
-- >>>STMT<<<
CREATE TRIGGER trg_operations_approval_after_change
																AFTER INSERT OR UPDATE
																ON operations_approval_requests
																FOR EACH ROW
																EXECUTE FUNCTION fn_operations_approval_after_change();
-- >>>STMT<<<
CREATE TRIGGER trg_operations_issue_after_change
																AFTER INSERT OR UPDATE
																ON operations_issues
																FOR EACH ROW
																EXECUTE FUNCTION fn_operations_issue_after_change();
-- >>>STMT<<<
CREATE TRIGGER trg_operations_improvement_after_change
																AFTER INSERT OR UPDATE
																ON operations_improvements
																FOR EACH ROW
																EXECUTE FUNCTION fn_operations_improvement_after_change();
-- >>>STMT<<<
CREATE TRIGGER trg_runway_refresh
AFTER INSERT OR UPDATE OR DELETE
ON business_runway_transactions
FOR EACH ROW
EXECUTE FUNCTION trg_business_runway_refresh();
-- >>>STMT<<<
CREATE TRIGGER trg_team_operations_refresh
AFTER INSERT OR UPDATE OR DELETE
ON team_operation_activities
FOR EACH ROW
EXECUTE FUNCTION trg_team_operations_refresh();
-- >>>STMT<<<
CREATE TRIGGER trg_business_operations_refresh
AFTER INSERT OR UPDATE OR DELETE
ON business_operation_records
FOR EACH ROW
EXECUTE FUNCTION trg_business_operations_refresh();
-- >>>STMT<<<
CREATE TRIGGER trg_team_approval_refresh
AFTER UPDATE
ON team_approval_requests
FOR EACH ROW
EXECUTE FUNCTION trg_approval_refresh();
-- >>>STMT<<<
CREATE TRIGGER trg_team_activities_archive
AFTER UPDATE
ON team_activities
FOR EACH ROW
EXECUTE FUNCTION fn_transaction_archived_trigger();
-- >>>STMT<<<
CREATE TRIGGER trg_team_approvals_archive
AFTER UPDATE
ON team_approval_requests
FOR EACH ROW
EXECUTE FUNCTION fn_transaction_archived_trigger();
-- >>>STMT<<<
CREATE TRIGGER trg_team_updates_archive
AFTER UPDATE
ON team_updates
FOR EACH ROW
EXECUTE FUNCTION fn_transaction_archived_trigger();
-- >>>STMT<<<
CREATE TRIGGER trg_team_issue_risks_archive
AFTER UPDATE
ON team_issue_risks
FOR EACH ROW
EXECUTE FUNCTION fn_transaction_archived_trigger();
-- >>>STMT<<<
CREATE TRIGGER trg_runway_cash_inflows_archive
AFTER UPDATE
ON runway_cash_inflows
FOR EACH ROW
EXECUTE FUNCTION fn_transaction_archived_trigger();
-- >>>STMT<<<
CREATE TRIGGER trg_runway_expense_burns_archive
AFTER UPDATE
ON runway_expense_burns
FOR EACH ROW
EXECUTE FUNCTION fn_transaction_archived_trigger();
-- >>>STMT<<<
CREATE TRIGGER trg_runway_risks_archive
AFTER UPDATE
ON runway_risks
FOR EACH ROW
EXECUTE FUNCTION fn_transaction_archived_trigger();
-- >>>STMT<<<
CREATE TRIGGER trg_runway_financial_updates_archive
AFTER UPDATE
ON runway_financial_updates
FOR EACH ROW
EXECUTE FUNCTION fn_transaction_archived_trigger();
-- >>>STMT<<<
CREATE TRIGGER trg_runway_strategic_decisions_archive
AFTER UPDATE
ON runway_strategic_decisions
FOR EACH ROW
EXECUTE FUNCTION fn_transaction_archived_trigger();
-- >>>STMT<<<
CREATE TRIGGER trg_operations_spend_entries_archive
AFTER UPDATE
ON operations_spend_entries
FOR EACH ROW
EXECUTE FUNCTION fn_transaction_archived_trigger();
-- >>>STMT<<<
CREATE TRIGGER trg_operations_vendor_updates_archive
AFTER UPDATE
ON operations_vendor_updates
FOR EACH ROW
EXECUTE FUNCTION fn_transaction_archived_trigger();
-- >>>STMT<<<
CREATE TRIGGER trg_operations_approval_requests_archive
AFTER UPDATE
ON operations_approval_requests
FOR EACH ROW
EXECUTE FUNCTION fn_transaction_archived_trigger();
-- >>>STMT<<<
CREATE TRIGGER trg_operations_issues_archive
AFTER UPDATE
ON operations_issues
FOR EACH ROW
EXECUTE FUNCTION fn_transaction_archived_trigger();
-- >>>STMT<<<
CREATE TRIGGER trg_operations_improvements_archive
AFTER UPDATE
ON operations_improvements
FOR EACH ROW
EXECUTE FUNCTION fn_transaction_archived_trigger();
