DROP TRIGGER IF EXISTS trg_personal_moment_types_updated_at ON personal_moment_types CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_personal_moments_updated_at ON personal_moments CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_personal_moment_profiles_updated_at ON personal_moment_profiles CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_personal_life_operations_profile_updated_at ON personal_life_operations_profile CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_personal_future_building_profile_updated_at ON personal_future_building_profile CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_personal_lifestyle_profile_updated_at ON personal_lifestyle_profile CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_personal_relationships_profile_updated_at ON personal_relationships_profile CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_personal_quick_add_events_updated_at ON personal_quick_add_events CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_personal_life_attention_events_updated_at ON personal_life_attention_events CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_personal_life_recovery_events_updated_at ON personal_life_recovery_events CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_personal_life_mood_events_updated_at ON personal_life_mood_events CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_personal_life_adjust_events_updated_at ON personal_life_adjust_events CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_personal_future_progress_events_updated_at ON personal_future_progress_events CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_personal_future_milestone_events_updated_at ON personal_future_milestone_events CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_personal_future_opportunity_events_updated_at ON personal_future_opportunity_events CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_personal_future_learning_events_updated_at ON personal_future_learning_events CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_personal_future_pivot_events_updated_at ON personal_future_pivot_events CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_personal_lifestyle_experience_events_updated_at ON personal_lifestyle_experience_events CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_personal_lifestyle_wellbeing_events_updated_at ON personal_lifestyle_wellbeing_events CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_personal_lifestyle_discovery_events_updated_at ON personal_lifestyle_discovery_events CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_personal_lifestyle_expression_events_updated_at ON personal_lifestyle_expression_events CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_personal_lifestyle_adjust_events_updated_at ON personal_lifestyle_adjust_events CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_personal_relationship_connection_events_updated_at ON personal_relationship_connection_events CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_personal_relationship_support_events_updated_at ON personal_relationship_support_events CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_personal_relationship_experience_events_updated_at ON personal_relationship_experience_events CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_personal_relationship_investment_events_updated_at ON personal_relationship_investment_events CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_personal_relationship_adjust_events_updated_at ON personal_relationship_adjust_events CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_personal_accounts_updated_at ON personal_accounts CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_personal_categories_updated_at ON personal_categories CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_personal_money_events_updated_at ON personal_money_events CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_personal_live_priorities_updated_at ON personal_live_priorities CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_personal_memory_patterns_updated_at ON personal_memory_patterns CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_personal_insights_updated_at ON personal_insights CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_personal_activity_timeline_updated_at ON personal_activity_timeline CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_personal_notification_queue_updated_at ON personal_notification_queue CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_personal_user_preferences_updated_at ON personal_user_preferences CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_personal_signals_updated_at ON personal_signals CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_personal_recommendations_updated_at ON personal_recommendations CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_account_balance_refresh ON personal_money_events CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_personal_auto_refresh ON personal_quick_add_events CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_memory_identity_updated_at ON personal_memory_identity_snapshots CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_memory_driver_rankings_updated_at ON personal_memory_driver_rankings CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_memory_emotional_dna_updated_at ON personal_memory_emotional_dna CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_memory_evolution_updated_at ON personal_memory_evolution_snapshots CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_life_aggregate_updated_at ON personal_life_aggregate_snapshots CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS tr_group_expense_refresh ON group_expenses CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS tr_refresh_group_expenses_everything ON group_expenses CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS tr_refresh_group_contributions_everything ON group_contributions CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS tr_refresh_group_work_items_everything ON group_moment_work_items CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS tr_refresh_group_resources_everything ON group_moment_resources CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS tr_refresh_group_decisions_everything ON group_decisions CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS tr_refresh_group_memory_entries_everything ON group_memory_entries CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS tr_refresh_budget_plan_everything ON shared_experience_budget_plans CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS tr_refresh_budget_allocations_everything ON shared_experience_budget_allocations CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS tr_refresh_budget_splits_everything ON shared_experience_budget_splits CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS tr_refresh_life_links_everything ON group_life_moment_links CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS tr_prevent_duplicate_single_poll_vote ON group_poll_votes CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_business_moments_updated ON business_moments CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_business_moment_setup_updated ON business_moment_setup CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_business_moment_structure_updated ON business_moment_structure CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_business_moment_members_updated ON business_moment_members CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_business_moment_invitations_updated ON business_moment_invitations CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_business_moment_governance_updated ON business_moment_governance CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_team_activities_updated ON team_activities CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_team_approval_updated ON team_approval_requests CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_team_updates_updated ON team_updates CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_team_issue_risks_updated ON team_issue_risks CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_activity_created ON team_activities CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_activity_updated ON team_activities CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_approval_submitted ON team_approval_requests CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_approval_decision ON team_approval_requests CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_team_update_created ON team_updates CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_risk_created ON team_issue_risks CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_risk_resolved ON team_issue_risks CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_member_accepted ON business_moment_members CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_moment_activated ON business_moments CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_validate_team_activity_member_refs ON team_activities CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_validate_approval_member_refs ON team_approval_requests CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_validate_issue_member_refs ON team_issue_risks CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_auto_convert_approved_spend ON team_approval_requests CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_business_runway_setup_updated ON business_runway_setup CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_business_runway_structure_updated ON business_runway_structure CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_business_runway_governance_rules_updated ON business_runway_governance_rules CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_runway_cash_inflows_updated ON runway_cash_inflows CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_runway_expense_burns_updated ON runway_expense_burns CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_runway_risks_updated ON runway_risks CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_runway_strategic_decisions_updated ON runway_strategic_decisions CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_runway_financial_updates_updated ON runway_financial_updates CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_apply_runway_member_permissions ON business_moment_members CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_validate_runway_risk_member_refs ON runway_risks CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_validate_runway_decision_member_refs ON runway_strategic_decisions CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_runway_cash_inflow_created ON runway_cash_inflows CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_runway_cash_inflow_updated ON runway_cash_inflows CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_runway_expense_created ON runway_expense_burns CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_runway_expense_updated ON runway_expense_burns CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_runway_risk_created ON runway_risks CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_runway_risk_updated ON runway_risks CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_runway_decision_created ON runway_strategic_decisions CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_runway_decision_updated ON runway_strategic_decisions CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_runway_financial_update_created ON runway_financial_updates CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_runway_financial_update_updated ON runway_financial_updates CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_runway_risk_before_update ON runway_risks CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_runway_risk_after_update ON runway_risks CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_runway_financial_before_update ON runway_financial_updates CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_runway_financial_after_update ON runway_financial_updates CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_business_operations_setup_updated ON business_operations_setup CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_business_operations_budget_categories_updated ON business_operations_budget_categories CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_business_operations_structure_updated ON business_operations_structure CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_business_operations_governance_updated ON business_operations_governance_rules CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_operations_spend_entries_updated ON operations_spend_entries CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_operations_vendor_updates_updated ON operations_vendor_updates CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_operations_approval_requests_updated ON operations_approval_requests CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_operations_issues_updated ON operations_issues CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_operations_improvements_updated ON operations_improvements CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_apply_operations_member_permissions ON business_moment_members CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_validate_operations_approval_member_refs ON operations_approval_requests CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_validate_operations_issue_member_refs ON operations_issues CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_validate_operations_improvement_member_refs ON operations_improvements CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_operations_spend_after_change ON operations_spend_entries CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_operations_vendor_after_change ON operations_vendor_updates CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_operations_approval_after_change ON operations_approval_requests CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_operations_issue_after_change ON operations_issues CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_operations_improvement_after_change ON operations_improvements CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_runway_refresh ON business_runway_transactions CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_team_operations_refresh ON team_operation_activities CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_business_operations_refresh ON business_operation_records CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_team_approval_refresh ON team_approval_requests CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_team_activities_archive ON team_activities CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_team_approvals_archive ON team_approval_requests CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_team_updates_archive ON team_updates CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_team_issue_risks_archive ON team_issue_risks CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_runway_cash_inflows_archive ON runway_cash_inflows CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_runway_expense_burns_archive ON runway_expense_burns CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_runway_risks_archive ON runway_risks CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_runway_financial_updates_archive ON runway_financial_updates CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_runway_strategic_decisions_archive ON runway_strategic_decisions CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_operations_spend_entries_archive ON operations_spend_entries CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_operations_vendor_updates_archive ON operations_vendor_updates CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_operations_approval_requests_archive ON operations_approval_requests CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_operations_issues_archive ON operations_issues CASCADE
-- >>>STMT<<<
DROP TRIGGER IF EXISTS trg_operations_improvements_archive ON operations_improvements CASCADE
-- >>>STMT<<<
DO $$ DECLARE r record; BEGIN FOR r IN SELECT oid::regprocedure AS sig FROM pg_proc WHERE proname = ANY(ARRAY['set_personal_updated_at', 'fn_update_account_balance', 'fn_personal_auto_refresh', 'fn_personal_clamp_score', 'fn_personal_score_status_label', 'fn_personal_life_health_score', 'fn_personal_life_drift_score', 'fn_personal_life_drift_status', 'fn_personal_stress_score', 'fn_personal_capacity_score', 'fn_personal_highlight_impact_score', 'fn_personal_turning_point_impact_score', 'fn_personal_identity_confidence_score', 'fn_personal_driver_impact_pct', 'fn_personal_emotional_dna_pct', 'fn_personal_growth_edge_multiplier', 'fn_personal_recency_score', 'fn_personal_monthly_delta', 'fn_personal_momentum_score', 'fn_personal_progress_score', 'fn_personal_risk_score', 'sp_create_group_live_feed', 'sp_refresh_group_moment_stage', 'sp_refresh_group_health_snapshot', 'sp_refresh_group_pulse_snapshot', 'sp_refresh_group_signals', 'sp_refresh_group_recommendations', 'sp_refresh_group_memory_patterns', 'sp_refresh_group_moment_orchestration', 'sp_refresh_shared_experience_analytics', 'sp_refresh_shared_purchase_analytics', 'sp_refresh_shared_living_analytics', 'sp_refresh_group_type_analytics', 'sp_refresh_group_pulse_detail', 'sp_refresh_group_detailed_signals', 'sp_refresh_group_detailed_memory_patterns', 'sp_refresh_group_analytics_orchestration', 'sp_generate_settlement_matrix', 'sp_group_entity_changed', 'trg_expense_refresh', 'sp_refresh_group_ai_insights', 'sp_refresh_resident_dynamics', 'sp_refresh_purchase_ownership_insights', 'sp_refresh_group_production_orchestration', 'sp_create_shared_experience_budget_plan', 'sp_refresh_shared_experience_budget_rollup', 'sp_refresh_shared_experience_budget_splits', 'sp_update_shared_experience_budget_allocation', 'sp_add_shared_experience_budget_category', 'sp_refresh_shared_experience_budget_contributions', 'fn_shared_experience_budget_health_score', 'fn_shared_experience_budget_snapshot_json', 'fn_shared_experience_budget_reflection_json', 'sp_log_shared_experience_budget_event', 'fn_group_health_score', 'sp_refresh_group_people_impact', 'sp_refresh_group_memory_snapshot', 'fn_group_life_score', 'sp_refresh_group_life_snapshot', 'sp_refresh_group_driver_effects', 'sp_refresh_group_analytics', 'fn_se_booking_score', 'fn_se_participation_score', 'fn_se_timeline_score', 'fn_se_health_score', 'fn_sp_funding_score', 'fn_sp_health_score', 'fn_sl_health_score', 'fn_sg_health_score', 'fn_cc_health_score', 'fn_group_health_score_v2', 'fn_group_memory_participation_pattern_score', 'fn_group_memory_contribution_pattern_score', 'fn_group_memory_completion_pattern_score', 'fn_group_memory_budget_discipline_score', 'fn_group_memory_recovery_score', 'fn_group_memory_leadership_distribution_score', 'fn_group_memory_momentum_score', 'sp_refresh_group_memory_highlight_scores', 'fn_group_memory_identity_label', 'fn_group_memory_what_changed_json', 'sp_refresh_group_memory_patterns_v2', 'sp_refresh_group_memory_snapshot_v2', 'sp_refresh_group_memory_ai_insight', 'sp_refresh_group_memory_intelligence', 'fn_group_life_experience_dimension', 'fn_group_life_purchase_dimension', 'fn_group_life_living_dimension', 'fn_group_life_goal_dimension', 'fn_group_life_community_dimension', 'fn_group_life_score_v2', 'fn_group_recommendation_impact_score', 'fn_group_recommendation_confidence_score', 'fn_group_recommendation_priority_score', 'sp_generate_group_pulse_recommendations', 'sp_generate_budget_recommendations', 'sp_generate_memory_recommendations', 'sp_generate_life_leverage_recommendation', 'sp_generate_drift_recommendations', 'sp_generate_group_signals', 'sp_refresh_group_life_master_snapshot', 'sp_refresh_group_moment_full_orchestration', 'sp_refresh_group_life_full_orchestration', 'sp_refresh_group_everything', 'sp_refresh_group_budget_everything', 'trg_refresh_group_moment_everything', 'trg_refresh_group_budget_everything', 'trg_refresh_group_life_everything', 'sp_refresh_all_group_moments_nightly', 'sp_refresh_all_group_life_spaces_nightly', 'sp_refresh_group_production_all', 'trg_prevent_duplicate_single_poll_vote', 'sp_register_activity_edit_route', 'sp_log_group_activity_edit', 'sp_activate_business_moment', 'fn_update_timestamp', 'sp_activity_created', 'sp_approval_submitted', 'sp_risk_created', 'sp_create_live_feed_event', 'sp_write_audit_history', 'sp_create_notification', 'fn_transaction_change_event', 'sp_queue_analytics_refresh', 'sp_queue_memory_refresh', 'sp_queue_pulse_refresh', 'sp_refresh_business_pulse_snapshot', 'sp_refresh_business_moment_metrics', 'sp_refresh_business_memory_patterns', 'sp_refresh_business_orchestration', 'sp_process_orchestration_job', 'fn_activity_created_trigger', 'fn_activity_updated_trigger', 'fn_approval_created_trigger', 'fn_approval_decision_trigger', 'fn_team_update_created_trigger', 'fn_risk_created_trigger', 'fn_risk_resolved_trigger', 'fn_member_accepted_trigger', 'fn_moment_activated_trigger', 'fn_transaction_archived_trigger', 'fn_compute_business_health_status', 'fn_resolve_suggested_approver', 'sp_refresh_ai_signals', 'fn_get_business_actor_name', 'fn_is_notification_allowed', 'fn_validate_business_member_reference', 'fn_validate_team_activity_member_refs', 'fn_validate_approval_member_refs', 'fn_validate_issue_member_refs', 'sp_convert_approval_to_spend_activity', 'fn_auto_convert_approved_spend', 'fn_apply_runway_member_permissions', 'fn_validate_runway_member_reference', 'fn_validate_runway_risk_member_refs', 'fn_validate_runway_decision_member_refs', 'fn_get_runway_actor_name', 'fn_get_runway_source_record_id', 'sp_refresh_business_runway_snapshot', 'sp_refresh_business_runway_pulse_snapshot', 'sp_refresh_business_runway_moment_metrics', 'sp_refresh_business_runway_memory_patterns', 'sp_refresh_business_runway_orchestration', 'fn_get_runway_record_id', 'fn_runway_cash_inflow_created', 'fn_runway_cash_inflow_updated', 'fn_runway_expense_created', 'fn_runway_expense_updated', 'fn_runway_risk_created', 'fn_runway_risk_updated', 'fn_runway_decision_created', 'fn_runway_decision_updated', 'fn_runway_financial_update_created', 'fn_runway_financial_update_updated', 'fn_runway_risk_before_update', 'fn_runway_risk_after_update', 'fn_runway_financial_before_update', 'fn_runway_financial_after_update', 'fn_validate_runway_trigger_state', 'sp_apply_runway_financial_update', 'fn_apply_operations_member_permissions', 'fn_validate_operations_member_reference', 'fn_validate_operations_approval_member_refs', 'fn_validate_operations_issue_member_refs', 'fn_validate_operations_improvement_member_refs', 'fn_get_operations_actor_name', 'sp_refresh_business_operations_snapshot', 'sp_refresh_business_operations_pulse_snapshot', 'sp_refresh_business_operations_moment_metrics', 'sp_refresh_business_operations_memory_patterns', 'sp_refresh_business_operations_orchestration', 'sp_create_business_operations_live_event', 'sp_write_business_operations_audit', 'fn_operations_spend_after_change', 'fn_operations_vendor_after_change', 'fn_operations_approval_after_change', 'fn_operations_issue_after_change', 'fn_operations_improvement_after_change', 'sp_activate_business_operations', 'sp_refresh_operations_ai_signals', 'fn_resolve_operations_kpis', 'sp_refresh_business_health_drivers', 'sp_refresh_business_attention_items', 'sp_refresh_business_signal_insights', 'sp_refresh_business_recommended_actions', 'sp_refresh_business_pulse_snapshot_v2', 'sp_refresh_business_pulse_experience', 'sp_refresh_business_progress_snapshots', 'sp_refresh_business_moment_highlights', 'sp_refresh_business_activity_center_items', 'sp_refresh_business_moment_metrics_v2', 'sp_refresh_business_moments_experience', 'fn_validate_business_moments_experience', 'sp_refresh_business_life_dimensions', 'sp_refresh_business_life_connections', 'sp_refresh_business_life_insights', 'sp_refresh_business_journey_events', 'sp_refresh_business_life_snapshot', 'sp_refresh_business_life_experience', 'fn_validate_business_life_experience', 'sp_refresh_business_memory_learnings', 'sp_refresh_business_playbooks', 'sp_refresh_business_success_memory', 'sp_refresh_business_risk_memory', 'sp_refresh_business_wisdom', 'sp_refresh_business_memory_snapshot', 'sp_refresh_business_memory_experience', 'fn_validate_business_memory_experience', 'sp_refresh_business_activity_permissions', 'fn_get_activity_permission_badge', 'sp_refresh_business_activity_center_cache', 'fn_get_activity_detail', 'fn_can_edit_activity', 'fn_can_approve_activity', 'sp_refresh_business_activity_center', 'fn_validate_business_activity_center', 'sp_create_business_refresh_job', 'sp_route_business_refresh', 'sp_process_business_refresh_job', 'trg_business_runway_refresh', 'trg_team_operations_refresh', 'trg_business_operations_refresh', 'trg_approval_refresh', 'sp_queue_workspace_refresh', 'fn_validate_business_orchestration', 'fn_validate_business_views', 'sp_refresh_business_experience', 'sp_refresh_workspace_experience', 'sp_refresh_business_360', 'sp_recover_failed_business_jobs', 'fn_validate_business_audit', 'fn_validate_business_platform', 'fn_get_workspace_id', 'fn_validate_business_freeze', 'fn_validate_driver_weights', 'fn_validate_driver_registry', 'fn_validate_business_batch_30b', 'fn_validate_archive_coverage', 'fn_get_progress_metric_delta', 'fn_validate_business_batch_30d']) AND prokind = 'f' LOOP EXECUTE 'DROP FUNCTION IF EXISTS ' || r.sig || ' CASCADE'; END LOOP; END $$
