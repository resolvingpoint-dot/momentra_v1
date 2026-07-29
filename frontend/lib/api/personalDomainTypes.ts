import type {
  PersonalLiveRecentActivityItem,
  PersonalLifestyleMemoryMetrics,
  PersonalLifestyleMomentsMetrics,
  PersonalLifestylePulseMetrics,
  PulseDashboardCard,
} from "@/lib/api/personal";

export interface PersonalDomainRuntimeTile {
  label: string;
  value: string;
}

export interface PersonalDomainBreakthrough {
  label: string;
  body: string;
}

export interface PersonalDomainIdentifiedPattern {
  name: string;
  confidence_percent: number;
}

export interface PersonalDomainConfidencePoint {
  month: string;
  value: number;
}

export interface PersonalDomainGraphSeries {
  series_code: string;
  label: string;
  points: number[];
}

export interface PersonalLifeOpsTimelineFilterChip {
  id: string;
  label: string;
}

export interface PersonalDomainActivityTimeline {
  section_title: string;
  filter_chips: PersonalLifeOpsTimelineFilterChip[];
  items: PersonalLiveRecentActivityItem[];
  search_placeholder: string;
  empty_message?: string | null;
}

export interface PersonalDomainBottomActions {
  edit_label: string;
  export_label: string;
  archive_label: string;
}

// --- Setup preview blocks ---

export interface PersonalDomainSetupPreviewIdentity {
  badge_label: string;
  title: string;
  body: string;
  icon_name: string;
}

export interface PersonalDomainSetupPreviewRow {
  label: string;
  value: string;
  accent?: string | null;
}

export interface PersonalFutureBuildingSetupPreviewHorizon {
  trajectory: string;
  momentum_percent: number;
  opportunity: string;
  breakthrough: string;
  obstacle_title: string;
  obstacle_body: string;
}

export interface PersonalFutureBuildingSetupPreview {
  assigned_identity: PersonalDomainSetupPreviewIdentity;
  runtime_projection: PersonalDomainSetupPreviewRow[];
  future_horizon: PersonalFutureBuildingSetupPreviewHorizon;
}

export interface PersonalLifestyleSetupPreviewHorizon {
  trajectory: string;
  vitality_percent: number;
  opportunity: string;
  fulfillment: string;
  gap_title: string;
  gap_body: string;
}

export interface PersonalLifestyleSetupPreview {
  assigned_identity: PersonalDomainSetupPreviewIdentity;
  lifestyle_snapshot: PersonalDomainSetupPreviewRow[];
  lifestyle_horizon: PersonalLifestyleSetupPreviewHorizon;
}

export interface PersonalEmotionalSecuritySetupPreviewHorizon {
  trajectory: string;
  bond_percent: number;
  opportunity: string;
  potential: string;
  gap_title: string;
  gap_body: string;
}

export interface PersonalEmotionalSecuritySetupPreview {
  assigned_identity: PersonalDomainSetupPreviewIdentity;
  relationship_snapshot: PersonalDomainSetupPreviewRow[];
  relationship_horizon: PersonalEmotionalSecuritySetupPreviewHorizon;
}

// --- Future Building ---

export interface PersonalFutureBuildingInvestmentEffectiveness {
  capital_inr: string;
  time_hours: string;
  return_label: string;
}

export interface PersonalFutureBuildingOpportunitySignalsDetail {
  captured_count: number;
  high_potential_count: number;
}

export interface PersonalFutureBuildingPulse {
  hero_title: string;
  hero_subtitle: string;
  confidence_label: string;
  confidence_trend: string;
  momentum_rate_percent: number;
  momentum_rate_suffix: string;
  opportunity_signals_title: string;
  pattern_insight_title: string;
  pattern_insight_body: string;
  identity_label: string;
  direction_label: string;
  confidence_section_label: string;
  momentum_rate_section_label: string;
  breakthrough?: PersonalDomainBreakthrough | null;
  investment_effectiveness?: PersonalFutureBuildingInvestmentEffectiveness | null;
  opportunity_signals?: PersonalFutureBuildingOpportunitySignalsDetail | null;
  horizon_trajectory?: string | null;
  horizon_opportunity?: string | null;
  dashboard_card?: PulseDashboardCard | null;
  metrics?: PersonalFutureBuildingPulseMetrics | null;
}

export interface PersonalFutureBuildingAxisScores {
  learning: number;
  execution: number;
  milestones: number;
  opportunities: number;
  confidence: number;
}

export interface PersonalFutureBuildingPulseMetrics {
  momentum_index: number;
  momentum_index_delta_month: number | null;
  status_band: string;
  status_label: string;
  axis_scores: PersonalFutureBuildingAxisScores;
  capacity_stats: {
    investments_minor: number;
    milestones: number;
    learning_events: number;
    opportunities: number;
  };
  signals: Array<{ signal_id: string; label: string; trend: string }>;
  financial_segments: Array<{
    category_id: string;
    category_name?: string | null;
    amount_minor: number;
    share_percent: number;
  }>;
  trends_30d: {
    learning: Array<{ date: string; value: number }>;
    execution: Array<{ date: string; value: number }>;
    progress: Array<{ date: string; value: number }>;
  };
  score_drivers: Array<{ driver_id: string; label: string; impact: number; fill_percent: number }>;
  gauges: Array<{ gauge_id: string; label: string; percent: number }>;
  opportunity: {
    priority_id: string;
    title: string;
    body: string;
    cta_label: string;
    growth_impact: number;
    confidence_impact: number;
  };
  intelligence: { insight_text: string; confidence_percent: number };
  recent_activity: Array<{
    id: string;
    event_type: string;
    category_label: string;
    detail_line: string;
    relative_time: string;
    captured_at: string;
    edit_event_type: string;
  }>;
}

export interface PersonalFutureBuildingJourneyHero {
  journey_score: number;
  status_band: string;
  status_label: string;
  phases: Array<{ phase_id: string; label: string; is_active: boolean }>;
  insight_body: string;
  milestones: number;
  learning_events: number;
  invested_minor: number;
  opportunities: number;
}

export interface PersonalFutureBuildingMoneyJourney {
  title: string;
  period_label: string;
  series: Array<{
    category_id: string;
    category_name: string;
    points: Array<{ date: string; value_minor: number }>;
  }>;
  total_invested_minor: number;
  highest_month: { label: string; amount_minor: number };
  highest_area: { label: string; amount_minor: number };
}

export interface PersonalFutureBuildingMomentsMetrics {
  journey_hero: PersonalFutureBuildingJourneyHero;
  journey_timeline: Array<{
    id: string;
    event_type: string;
    category_label: string;
    detail_line: string;
    relative_time: string;
    captured_at: string;
    edit_event_type: string;
  }>;
  money_journey: PersonalFutureBuildingMoneyJourney;
  best_moments: Array<{
    card_id: string;
    title: string;
    period_label: string;
    impact_lines: string[];
    icon: string;
  }>;
  turning_points: Array<{
    turning_point_id: string;
    title: string;
    subtitle: string;
    icon: string;
    period_label?: string | null;
  }>;
}

export type PersonalFutureBuildingMemoryMetrics = import("@/lib/api/personal").PersonalLifeOpsMemoryMetrics;

export interface PersonalFutureBuildingFutureProfileHero {
  identity_label: string;
  momentum_percent: number;
  direction_label: string;
  confidence_label: string;
  current_state_label: string;
}

export interface PersonalFutureBuildingInvestmentSummary {
  capital_inr: string;
  time_hours: string;
  effort_events: number;
}

export interface PersonalFutureBuildingReturnsSummary {
  income_growth_inr: string;
  milestones: number;
  opportunities: number;
  learning_events: number;
}

export interface PersonalFutureBuildingMomentDetail {
  moment_id: string;
  screen_title: string;
  avatar_image_url?: string | null;
  section_label: string;
  rhythm_label: string;
  active_session_label: string;
  runtime_profile: PersonalDomainRuntimeTile;
  runtime_direction: PersonalDomainRuntimeTile;
  runtime_confidence: PersonalDomainRuntimeTile;
  runtime_state: PersonalDomainRuntimeTile;
  activity_timeline: { timeline: PersonalDomainActivityTimeline };
  bottom_actions: PersonalDomainBottomActions;
  future_profile?: PersonalFutureBuildingFutureProfileHero | null;
  investment_summary?: PersonalFutureBuildingInvestmentSummary | null;
  returns_summary?: PersonalFutureBuildingReturnsSummary | null;
  future_insight?: string | null;
  metrics?: PersonalFutureBuildingMomentsMetrics | null;
}

export interface PersonalFutureBuildingMemory {
  section_label: string;
  status_label: string;
  synthesis_title: string;
  synthesis_body: string;
  system_state: string;
  days_analyzed: number;
  confidence_percent: number;
  confidence_title: string;
  confidence_body: string;
  identity_label: string;
  direction_label: string;
  neural_growth_title: string;
  neural_growth_subtitle: string;
  breakthrough_title: string;
  breakthrough_body: string;
  breakthrough_active: boolean;
  focus_title: string;
  focus_percent: number;
  focus_body: string;
  identified_patterns: PersonalDomainIdentifiedPattern[];
  confidence_evolution: PersonalDomainConfidencePoint[];
  intelligence_graph: PersonalDomainGraphSeries[];
  focus_optimization_percent?: number | null;
  metrics?: PersonalFutureBuildingMemoryMetrics | null;
}

// --- Lifestyle ---

export interface PersonalLifestyleSpendEffectiveness {
  spend_inr: string;
  experience_count: string;
  return_label: string;
}

export interface PersonalLifestyleExperienceSignalsDetail {
  captured_count: number;
  high_fulfillment_count: number;
}

export interface PersonalLifestylePulse {
  hero_title: string;
  hero_subtitle: string;
  vitality_label: string;
  vitality_trend: string;
  fulfillment_rate_percent: number;
  fulfillment_rate_suffix: string;
  experience_signals_title: string;
  pattern_insight_title: string;
  pattern_insight_body: string;
  identity_label: string;
  style_label: string;
  vitality_section_label: string;
  fulfillment_rate_section_label: string;
  breakthrough?: PersonalDomainBreakthrough | null;
  spend_effectiveness?: PersonalLifestyleSpendEffectiveness | null;
  experience_signals?: PersonalLifestyleExperienceSignalsDetail | null;
  horizon_trajectory?: string | null;
  horizon_opportunity?: string | null;
  dashboard_card?: PulseDashboardCard | null;
  metrics?: PersonalLifestylePulseMetrics | null;
}

export interface PersonalLifestyleFulfillmentProfileHero {
  identity_label: string;
  vitality_percent: number;
  style_label: string;
  energy_label: string;
  want_more_label: string;
}

export interface PersonalLifestyleSpendSummary {
  spend_inr: string;
  experience_count: number;
  return_label: string;
}

export interface PersonalLifestyleReturnsSummary {
  fulfillment_score_inr: string;
  experiences: number;
  wellbeing_entries: number;
  discoveries: number;
  creative_sessions: number;
}

export interface PersonalLifestyleMomentDetail {
  moment_id: string;
  screen_title: string;
  avatar_image_url?: string | null;
  section_label: string;
  rhythm_label: string;
  active_session_label: string;
  runtime_profile: PersonalDomainRuntimeTile;
  runtime_style: PersonalDomainRuntimeTile;
  runtime_energy: PersonalDomainRuntimeTile;
  runtime_want_more: PersonalDomainRuntimeTile;
  activity_timeline: { timeline: PersonalDomainActivityTimeline };
  bottom_actions: PersonalDomainBottomActions;
  fulfillment_profile?: PersonalLifestyleFulfillmentProfileHero | null;
  spend_summary?: PersonalLifestyleSpendSummary | null;
  returns_summary?: PersonalLifestyleReturnsSummary | null;
  lifestyle_insight?: string | null;
  metrics?: PersonalLifestyleMomentsMetrics | null;
}

export interface PersonalLifestyleMemory {
  section_label: string;
  status_label: string;
  synthesis_title: string;
  synthesis_body: string;
  system_state: string;
  days_analyzed: number;
  confidence_percent: number;
  confidence_title: string;
  confidence_body: string;
  identity_label: string;
  style_label: string;
  neural_growth_title: string;
  neural_growth_subtitle: string;
  breakthrough_title: string;
  breakthrough_body: string;
  breakthrough_active: boolean;
  focus_title: string;
  focus_percent: number;
  focus_body: string;
  identified_patterns: PersonalDomainIdentifiedPattern[];
  confidence_evolution: PersonalDomainConfidencePoint[];
  intelligence_graph: PersonalDomainGraphSeries[];
  focus_optimization_percent?: number | null;
  metrics?: PersonalLifestyleMemoryMetrics | null;
}

// --- Emotional Security (Relationships) ---

export interface PersonalEmotionalSecurityRadarAxis {
  axis_id: string;
  label: string;
  score: number;
}

export interface PersonalEmotionalSecurityPulseMetrics {
  bond_index: number;
  bond_index_delta_month: number | null;
  status_band: string;
  network_stability_label: string;
  radar_axes: PersonalEmotionalSecurityRadarAxis[];
  hero_stats: {
    connections: number;
    support: number;
    experiences: number;
    spend_minor: number;
  };
  signal_chips: Array<{ signal_id: string; label: string; trend: string }>;
  connection_count: number;
  spend_minor: number;
  recent_activity: PersonalLiveRecentActivityItem[];
  financial_segments: Array<{
    category_id: string;
    category_name?: string | null;
    amount_minor: number;
    share_percent: number;
  }>;
  trends_30d: {
    trust: Array<{ date: string; value: number }>;
    connection: Array<{ date: string; value: number }>;
  };
  gauges: Array<{ gauge_id: string; percent: number }>;
  opportunity: {
    title: string;
    body: string;
    cta_label: string;
    impact_chips: string[];
  };
  intelligence: { body: string; confidence_percent: number };
  analysis_signals: Array<{ signal_id: string; label: string; icon: string }>;
  quick_capture_actions: Array<{ action_code: string; label: string; is_primary: boolean }>;
}

export interface PersonalEmotionalSecurityJourneyHero {
  journey_score: number;
  status_band: string;
  phases: Array<{ phase_id: string; label: string; is_active: boolean }>;
  insight_body: string;
  connections: number;
  support: number;
  experiences: number;
  spend_minor: number;
}

export type PersonalEmotionalSecurityMemoryMetrics =
  import("@/lib/api/personal").PersonalLifestyleMemoryMetrics & {
    highest_return_behaviors?: import("@/lib/api/personal").PersonalLifeOpsReturnBehaviors | null;
  };

export interface PersonalEmotionalSecurityJourneyTimelineItem {
  id: string;
  event_type: string;
  category_label: string;
  detail_line: string;
  relative_time: string;
  captured_at: string;
  edit_event_type: string;
  can_edit: boolean;
  can_delete: boolean;
  image_url?: string | null;
}

export interface PersonalEmotionalSecurityBestMomentCard {
  card_id: string;
  title: string;
  period_label: string;
  tag_label: string;
  star_rating: number;
  image_url?: string | null;
  impact_lines: string[];
  icon: string;
}

export interface PersonalEmotionalSecurityTurningPoint {
  turning_point_id: string;
  title: string;
  subtitle: string;
  icon: string;
  date_label?: string | null;
  accent_color?: string | null;
}

export interface PersonalEmotionalSecurityMomentsMetrics {
  journey_hero: PersonalEmotionalSecurityJourneyHero;
  journey_timeline: PersonalEmotionalSecurityJourneyTimelineItem[];
  money_journey: import("@/lib/api/personal").PersonalLifeOpsMoneyJourney;
  best_moments: PersonalEmotionalSecurityBestMomentCard[];
  turning_points: PersonalEmotionalSecurityTurningPoint[];
}

export interface PersonalEmotionalSecuritySpendEffectiveness {
  spend_inr: string;
  connection_count: string;
  return_label: string;
}

export interface PersonalEmotionalSecurityConnectionSignalsDetail {
  captured_count: number;
  high_bond_count: number;
}

export interface PersonalEmotionalSecurityPulse {
  hero_title: string;
  hero_subtitle: string;
  vitality_label: string;
  vitality_trend: string;
  bond_rate_percent: number;
  bond_rate_suffix: string;
  connection_signals_title: string;
  pattern_insight_title: string;
  pattern_insight_body: string;
  identity_label: string;
  focus_label: string;
  vitality_section_label: string;
  bond_rate_section_label: string;
  breakthrough?: PersonalDomainBreakthrough | null;
  spend_effectiveness?: PersonalEmotionalSecuritySpendEffectiveness | null;
  connection_signals?: PersonalEmotionalSecurityConnectionSignalsDetail | null;
  horizon_trajectory?: string | null;
  horizon_opportunity?: string | null;
  dashboard_card?: PulseDashboardCard | null;
  metrics?: PersonalEmotionalSecurityPulseMetrics | null;
}

export interface PersonalEmotionalSecurityBondProfileHero {
  identity_label: string;
  bond_percent: number;
  focus_label: string;
  energy_label: string;
  want_more_label: string;
}

export interface PersonalEmotionalSecuritySpendSummary {
  spend_inr: string;
  connection_count: number;
  return_label: string;
}

export interface PersonalEmotionalSecurityReturnsSummary {
  bond_score_inr: string;
  connections: number;
  support_entries: number;
  shared_experiences: number;
  investments: number;
}

export interface PersonalEmotionalSecurityMomentDetail {
  moment_id: string;
  screen_title: string;
  avatar_image_url?: string | null;
  section_label: string;
  rhythm_label: string;
  active_session_label: string;
  runtime_profile: PersonalDomainRuntimeTile;
  runtime_focus: PersonalDomainRuntimeTile;
  runtime_energy: PersonalDomainRuntimeTile;
  runtime_want_more: PersonalDomainRuntimeTile;
  activity_timeline: { timeline: PersonalDomainActivityTimeline };
  bottom_actions: PersonalDomainBottomActions;
  bond_profile?: PersonalEmotionalSecurityBondProfileHero | null;
  spend_summary?: PersonalEmotionalSecuritySpendSummary | null;
  returns_summary?: PersonalEmotionalSecurityReturnsSummary | null;
  relationship_insight?: string | null;
  metrics?: PersonalEmotionalSecurityMomentsMetrics | null;
}

export interface PersonalEmotionalSecurityMemory {
  section_label: string;
  status_label: string;
  synthesis_title: string;
  synthesis_body: string;
  system_state: string;
  days_analyzed: number;
  confidence_percent: number;
  confidence_title: string;
  confidence_body: string;
  identity_label: string;
  focus_label: string;
  neural_growth_title: string;
  neural_growth_subtitle: string;
  breakthrough_title: string;
  breakthrough_body: string;
  breakthrough_active: boolean;
  focus_title: string;
  focus_percent: number;
  focus_body: string;
  identified_patterns: PersonalDomainIdentifiedPattern[];
  confidence_evolution: PersonalDomainConfidencePoint[];
  intelligence_graph: PersonalDomainGraphSeries[];
  focus_optimization_percent?: number | null;
  metrics?: PersonalEmotionalSecurityMemoryMetrics | null;
}
