import type {
  PersonalEmotionalSecurityMemory,
  PersonalEmotionalSecurityMomentDetail,
  PersonalEmotionalSecurityPulse,
  PersonalEmotionalSecuritySetupPreview,
  PersonalFutureBuildingMemory,
  PersonalFutureBuildingMomentDetail,
  PersonalFutureBuildingPulse,
  PersonalFutureBuildingSetupPreview,
  PersonalLifestyleMemory,
  PersonalLifestyleMomentDetail,
  PersonalLifestylePulse,
  PersonalLifestyleSetupPreview,
} from "@/lib/api/personalDomainTypes";

export type PersonalSetupAnswers = Record<string, string | string[]>;

export interface PersonalMomentResponse {
  moment_id: string;
  moment_type_id: string;
  moment_type_code: string | null;
  moment_name: string;
  moment_description: string | null;
  status: string;
  current_runtime_state: string | null;
  activated_at: string | null;
  projection_status?: "READY" | "REFRESHING";
}

export type PersonalMomentManageStatus =
  | "DRAFT"
  | "ACTIVE"
  | "PAUSED"
  | "COMPLETED"
  | "ARCHIVED";

export interface PersonalMomentUpdateRequest {
  moment_name?: string;
  moment_description?: string | null;
  status?: "ACTIVE" | "PAUSED" | "ARCHIVED";
}

export interface PersonalCreateOptionCard {
  moment_type_id: string;
  moment_type_code: string;
  moment_type_name: string;
  create_tagline: string | null;
  create_badge_label: string | null;
  is_create_featured: boolean;
  theme_color: string | null;
  icon_name: string | null;
  display_order: number;
  linked_moment_id: string | null;
  linked_moment_status: string | null;
  has_draft: boolean;
  action_label: string;
  background_image_url: string | null;
}

export interface PersonalCreateOptionsResponse {
  hero_badge_label: string;
  hero_subtitle: string;
  featured_hero_image_url: string;
  cta_label: string;
  section_title: string;
  footer_badge: string;
  footer_quote: string;
  cards: PersonalCreateOptionCard[];
}

export interface PersonalMomentCreateRequest {
  moment_type_code: string;
  moment_name?: string | null;
}

export interface PersonalSetupOption {
  value: string;
  label: string;
  description?: string | null;
  bar_level?: number | null;
  accent?: string | null;
}

export type PersonalSetupFieldType =
  | "single_select"
  | "multi_select"
  | "text"
  | "number"
  | "date"
  | "money"
  | "location"
  | (string & {});

export interface PersonalSetupField {
  field_key: string;
  label: string;
  helper_text?: string | null;
  field_type: PersonalSetupFieldType;
  options?: PersonalSetupOption[] | null;
  required?: boolean;
}

export interface PersonalSetupMission {
  badge_label: string;
  title: string;
  body: string;
}

export interface PersonalSetupMeter {
  label: string;
  pct: number;
}

export interface PersonalSetupPreview {
  narrative: string;
  rhythm: PersonalSetupMeter;
  pressure: PersonalSetupMeter;
  recovery: PersonalSetupMeter;
  runtime_priorities: string[];
  identity_chips: string[];
  future_building?: PersonalFutureBuildingSetupPreview | null;
  lifestyle?: PersonalLifestyleSetupPreview | null;
  emotional_security?: PersonalEmotionalSecuritySetupPreview | null;
}

export interface PersonalSetupResponse {
  moment_id: string;
  moment_type_code: string;
  moment_name: string;
  status: string;
  title: string;
  subtitle: string;
  background_image_url: string | null;
  fields: PersonalSetupField[];
  mission: PersonalSetupMission | null;
  saved_answers: PersonalSetupAnswers | null;
  cta_label: string | null;
  footer_note: string | null;
}

export interface PersonalSetupSubmitRequest {
  answers: PersonalSetupAnswers;
}

export interface PulseDashboardRecentItem {
  id: string;
  activity_type: string;
  title: string;
  subtitle: string;
  amount_label?: string | null;
  occurred_at: string;
  relative_time: string;
  icon?: string | null;
  color?: string | null;
  impact_label?: string | null;
  impact_direction?: string | null;
  edit_event_type?: string;
  can_edit?: boolean;
  can_delete?: boolean;
  editable?: boolean;
  category_code?: string | null;
  subcategory_code?: string | null;
  category_label?: string | null;
  subcategory_label?: string | null;
  mood_label?: string | null;
  mood?: {
    code?: string | null;
    label?: string | null;
    intensity?: string | null;
    source?: string | null;
  } | null;
  domain?: string | null;
  domain_label?: string | null;
  type_label?: string | null;
  domain_type_subtitle?: string | null;
  primary_metric?: {
    kind?: string | null;
    display?: string | null;
    amount_minor?: number | null;
    currency_code?: string | null;
  } | null;
  chips?: Array<{ code?: string | null; label?: string | null }> | null;
}

export type TemplateActivityListResponse = {
  moment_id: string;
  moment_type_code: string;
  items: import("@/lib/personal/template/activity/types").TemplateActivityItem[];
  next_cursor?: string | null;
};

export interface PersonalLifeOpsActivitySummary {
  total_logs: number;
  this_month: number;
  total_amount_minor: number;
}

export interface PersonalLifeOpsActivityItem {
  id: string;
  event_type: string;
  title?: string | null;
  category_label: string;
  detail_line: string;
  relative_time: string;
  captured_at: string;
  edit_event_type: string;
  can_edit: boolean;
  can_delete: boolean;
  amount_label?: string | null;
  account_label?: string | null;
  icon?: string | null;
  color?: string | null;
  impact_label?: string | null;
  impact_direction?: string | null;
  category_code?: string | null;
  subcategory_code?: string | null;
  subcategory_label?: string | null;
  mood_label?: string | null;
}

export interface PersonalLifeOpsActivityResponse {
  moment_id: string;
  summary: PersonalLifeOpsActivitySummary;
  items: PersonalLifeOpsActivityItem[];
}

export interface PersonalQuickAddDetail {
  quick_add_event_id: string;
  moment_id: string;
  event_type: string;
  event_title: string;
  event_summary?: string | null;
  captured_at: string;
  recovery?: Record<string, unknown> | null;
  reflection?: Record<string, unknown> | null;
  rhythm?: Record<string, unknown> | null;
  expense?: Record<string, unknown> | null;
  commitment?: Record<string, unknown> | null;
}

export interface PulseDashboardCard {
  moment_id?: string | null;
  moment_name?: string | null;
  moment_type_code: string;
  kpis: Array<{ kpi_id: string; label: string; value: string }>;
  recent_items: PulseDashboardRecentItem[];
  empty_recent_message?: string | null;
}

export interface PersonalLifeOpsPulseMetrics {
  data_sufficient?: boolean;
  ops_index: number | null;
  ops_index_delta_month: number | null;
  status_band: string;
  axis_scores: { pressure: number; recovery: number; discipline: number; attention: number };
  capacity: {
    budget_minor: number;
    used_minor: number;
    remaining_minor: number | null;
    utilization_percent: number | null;
    has_budget?: boolean;
  };
  signals: Array<{ signal_id: string; trend: string }>;
  financial_segments: Array<{
    category_id: string;
    category_name?: string | null;
    amount_minor: number;
    share_percent: number;
    icon?: string | null;
    color?: string | null;
  }>;
  trends_30d: {
    recovery: Array<{ date: string; value: number }>;
    pressure: Array<{ date: string; value: number }>;
  };
  score_drivers: Array<{ driver_id: string; impact: number }>;
  gauges: Array<{ gauge_id: string; percent: number }>;
  opportunity: { priority_id: string; stress_impact: number; capacity_boost: number };
  intelligence: { pattern_id: string; confidence_percent: number };
}

export interface PersonalLifestylePulseMetrics {
  vitality_index: number;
  vitality_delta_month: number | null;
  status_band: string;
  axis_scores: { joy: number; fulfillment: number; vitality: number; exploration: number };
  capacity: {
    lifestyle_spend_minor: number;
    experience_count: number;
    discovery_count: number;
    creative_session_count: number;
  };
  signals: Array<{ signal_id: string; trend: string }>;
  financial_segments: Array<{ category_id: string; category_name?: string | null; amount_minor: number; share_percent: number }>;
  trends_30d: {
    joy: Array<{ date: string; value: number }>;
    vitality: Array<{ date: string; value: number }>;
  };
  score_drivers: Array<{ driver_id: string; impact: number; icon?: string | null }>;
  gauges: Array<{ gauge_id: string; percent: number; label?: string | null }>;
  opportunity: { priority_id: string; title: string; body: string; cta_label: string };
  intelligence: { pattern_id: string; confidence_percent: number; quote: string };
}

export interface PersonalLifeOperationsPulse {
  rhythm_label?: string;
  hero_subtitle?: string;
  dashboard_card?: PulseDashboardCard | null;
  metrics?: PersonalLifeOpsPulseMetrics | null;
}

export interface PersonalPulseResponse {
  overall_rhythm_state: string;
  active_moment_count: number;
  is_empty: boolean;
  hero_title?: string | null;
  hero_subtitle?: string | null;
  journey_title?: string | null;
  journey_subtitle?: string | null;
  cta_label?: string | null;
  life_operations?: PersonalLifeOperationsPulse | null;
  future_building?: PersonalFutureBuildingPulse | null;
  lifestyle?: PersonalLifestylePulse | null;
  emotional_security?: PersonalEmotionalSecurityPulse | null;
}

export interface PersonalLiveRecentActivityItem {
  id: string;
  event_type: string;
  category_label: string;
  detail_line: string;
  relative_time: string;
  captured_at: string;
  edit_event_type: string;
  can_edit?: boolean;
  can_delete?: boolean;
  editable?: boolean;
  title?: string | null;
  subtitle?: string | null;
  amount_label?: string | null;
  activity_type?: string | null;
  icon?: string | null;
  color?: string | null;
  impact_label?: string | null;
  impact_direction?: string | null;
  category_code?: string | null;
  subcategory_code?: string | null;
  subcategory_label?: string | null;
  mood_label?: string | null;
  mood?: {
    code?: string | null;
    label?: string | null;
    intensity?: string | null;
    source?: string | null;
  } | null;
  domain_label?: string | null;
  type_label?: string | null;
  domain_type_subtitle?: string | null;
  primary_metric?: {
    kind?: string | null;
    display?: string | null;
    amount_minor?: number | null;
    currency_code?: string | null;
  } | null;
  chips?: Array<{ code?: string | null; label?: string | null }> | null;
}

export interface PersonalLifeOpsJourneyPhase {
  phase_id: string;
  label: string;
  is_active: boolean;
}

export interface PersonalLifeOpsJourneyHero {
  journey_score: number;
  status_band: string;
  phases: PersonalLifeOpsJourneyPhase[];
  insight_body: string;
  days_active: number;
  recovery_events: number;
  adjustments_made: number;
  pressure_reduced_percent: number;
}

export interface PersonalLifeOpsMoneyJourneyPoint {
  date: string;
  value_minor: number;
}

export interface PersonalLifeOpsMoneyJourneySeries {
  category_id: string;
  category_name: string;
  points: PersonalLifeOpsMoneyJourneyPoint[];
}

export interface PersonalLifeOpsMoneyJourneyMonthStat {
  label: string;
  amount_minor: number;
}

export interface PersonalLifeOpsMoneyJourney {
  title: string;
  period_label: string;
  series: PersonalLifeOpsMoneyJourneySeries[];
  total_spend_minor: number;
  highest_month: PersonalLifeOpsMoneyJourneyMonthStat;
  lowest_month: PersonalLifeOpsMoneyJourneyMonthStat;
}

export interface PersonalLifeOpsBestMomentCard {
  card_id: string;
  title: string;
  period_label: string;
  impact_lines: string[];
  icon: string;
}

export interface PersonalLifeOpsTurningPoint {
  turning_point_id: string;
  title: string;
  subtitle: string;
  icon: string;
}

export interface PersonalLifeOpsMomentsMetrics {
  journey_hero: PersonalLifeOpsJourneyHero;
  journey_timeline: PersonalLiveRecentActivityItem[];
  money_journey: PersonalLifeOpsMoneyJourney;
  best_moments: PersonalLifeOpsBestMomentCard[];
  turning_points: PersonalLifeOpsTurningPoint[];
}

/** Unified projection slice — same shape as widget metrics */
export type MomentProjection = PersonalLifeOpsMomentsMetrics;
export type MemoryProjection = PersonalLifeOpsMemoryMetrics;
export type LifeProjection = PersonalLifeMetrics;

export interface PersonalLifestyleJourneyHero {
  journey_score: number;
  status_band: string;
  phases: PersonalLifeOpsJourneyPhase[];
  insight_body: string;
  experience_count: number;
  discovery_count: number;
  creative_session_count: number;
  lifestyle_spend_minor: number;
}

export interface PersonalLifestyleBestMomentCard {
  card_id: string;
  title: string;
  period_label: string;
  impact_lines: string[];
  icon: string;
  image_url?: string | null;
  axis_tag?: string | null;
  spend_amount_minor?: number | null;
}

export interface PersonalLifestyleTimelineItem {
  id: string;
  event_type: string;
  title: string;
  group_label: string;
  impact_line?: string | null;
  impact_tone?: "positive" | "vitality" | "fulfillment" | "neutral" | null;
  thumbnail_url?: string | null;
  captured_at: string;
}

export interface PersonalLifestyleMoneyJourneyPoint {
  date: string;
  value_minor: number;
}

export interface PersonalLifestyleMoneyJourneySeries {
  category_id: string;
  category_name: string;
  points: PersonalLifestyleMoneyJourneyPoint[];
}

export interface PersonalLifestyleMoneyJourney {
  title: string;
  period_label: string;
  series: PersonalLifestyleMoneyJourneySeries[];
  total_spend_minor: number;
  highest_area_label: string;
  highest_area_amount_minor: number;
  lowest_return_label: string;
  lowest_return_amount_minor: number;
}

export interface PersonalLifestyleTurningPoint {
  turning_point_id: string;
  title: string;
  subtitle: string;
  icon: string;
  occurred_label?: string | null;
}

export interface PersonalLifestyleMomentsMetrics {
  journey_hero: PersonalLifestyleJourneyHero;
  journey_timeline: PersonalLifestyleTimelineItem[];
  money_journey: PersonalLifestyleMoneyJourney;
  best_moments: PersonalLifestyleBestMomentCard[];
  turning_points: PersonalLifestyleTurningPoint[];
}

export interface PersonalLifeOperationsMomentDetail {
  moment_id: string;
  screen_title: string;
  metrics?: PersonalLifeOpsMomentsMetrics | null;
}

export interface PersonalMomentHomeCard {
  moment_type_id?: string;
  moment_type_code: string;
  moment_type_name: string;
  display_order: number;
  is_active: boolean;
  linked_moment_id?: string | null;
  linked_moment_status?: string | null;
  moment_name?: string | null;
}

export interface PersonalMomentsHomeResponse {
  active_moment_count: number;
  is_empty: boolean;
  subtitle: string;
  cards: PersonalMomentHomeCard[];
  life_operations_detail?: PersonalLifeOperationsMomentDetail | null;
  future_building_detail?: PersonalFutureBuildingMomentDetail | null;
  lifestyle_detail?: PersonalLifestyleMomentDetail | null;
  emotional_security_detail?: PersonalEmotionalSecurityMomentDetail | null;
}

export interface PersonalLifeOpsIdentitySnapshot {
  title: string;
  trend_label: string;
  confidence_percent: number;
  body: string;
  image_url?: string | null;
}

export interface PersonalLifeOpsCorePatternNode {
  node_id: string;
  icon: string;
  label: string;
  subtitle: string;
}

export interface PersonalLifeOpsCorePattern {
  pattern_confidence_percent: number;
  nodes: PersonalLifeOpsCorePatternNode[];
}

export interface PersonalLifeOpsDriver {
  rank: number;
  label: string;
  impact_percent: number;
  impact_description?: string | null;
}

export interface PersonalLifeOpsReturnBehaviorBar {
  behavior_code: string;
  label: string;
  height_fraction: number;
}

export interface PersonalLifeOpsReturnBehaviors {
  title: string;
  roi_label: string;
  bars: PersonalLifeOpsReturnBehaviorBar[];
}

export interface PersonalLifeOpsEmotionalDnaSegment {
  segment_id: string;
  label: string;
  percent: number;
  color_token: string;
}

export interface PersonalLifeOpsEmotionalDna {
  dominant_label: string;
  segments: PersonalLifeOpsEmotionalDnaSegment[];
  insight_body: string;
}

export interface PersonalLifeOpsBehavioralPattern {
  pattern_id: string;
  icon: string;
  title: string;
  subtitle: string;
  confidence_percent: number;
}

export interface PersonalLifeOpsEvolutionPhase {
  phase_id: string;
  label: string;
  is_active: boolean;
}

export interface PersonalLifeOpsAiInterpretation {
  quote: string;
}

export interface PersonalLifeOpsGrowthEdge {
  title: string;
  body: string;
  cta_label: string;
}

export interface PersonalLifeOpsMemoryMetrics {
  identity_snapshot: PersonalLifeOpsIdentitySnapshot;
  core_pattern: PersonalLifeOpsCorePattern;
  best_drivers: PersonalLifeOpsDriver[];
  lowest_drivers: PersonalLifeOpsDriver[];
  highest_return_behaviors: PersonalLifeOpsReturnBehaviors;
  emotional_dna: PersonalLifeOpsEmotionalDna;
  behavioral_patterns: PersonalLifeOpsBehavioralPattern[];
  evolution_timeline: PersonalLifeOpsEvolutionPhase[];
  ai_interpretation: PersonalLifeOpsAiInterpretation;
  next_growth_edge: PersonalLifeOpsGrowthEdge;
}

export interface PersonalLifestyleRoiAnalysis {
  title: string;
  roi_label: string;
  bars: Array<{ behavior_code: string; label: string; height_fraction: number }>;
}

export interface PersonalLifestyleMemoryMetrics {
  identity_snapshot: PersonalLifeOpsIdentitySnapshot;
  core_pattern: PersonalLifeOpsCorePattern;
  best_drivers: PersonalLifeOpsDriver[];
  lowest_drivers: PersonalLifeOpsDriver[];
  roi_analysis: PersonalLifestyleRoiAnalysis;
  emotional_dna: PersonalLifeOpsEmotionalDna;
  behavioral_patterns: PersonalLifeOpsBehavioralPattern[];
  evolution_timeline: PersonalLifeOpsEvolutionPhase[];
  ai_interpretation: PersonalLifeOpsAiInterpretation;
  next_growth_edge: PersonalLifeOpsGrowthEdge;
}

export interface PersonalLifeOperationsMemory {
  synthesis_title: string;
  metrics?: PersonalLifeOpsMemoryMetrics | null;
}

export interface PersonalMemoryResponse {
  is_empty: boolean;
  life_operations?: PersonalLifeOperationsMemory | null;
  future_building?: PersonalFutureBuildingMemory | null;
  lifestyle?: PersonalLifestyleMemory | null;
  emotional_security?: PersonalEmotionalSecurityMemory | null;
}

export interface PersonalLifeSatelliteScore {
  moment_type_code: string;
  label: string;
  score: number | null;
  color_token: string;
}

export interface PersonalLifeHealthHero {
  life_score: number;
  status_label: string;
  delta_month: number | null;
  insight_quote: string;
  satellite_scores: PersonalLifeSatelliteScore[];
}

export interface PersonalLifeTrendPoint {
  week_label: string;
  connection: number;
  joy: number;
  stress: number;
  fulfillment: number;
}

export interface PersonalLifeEmotionBreakdown {
  emotion_code: string;
  label: string;
  percent: number;
  color_token: string;
}

export interface PersonalLifeBalanceDimension {
  dimension_code: string;
  label: string;
  score: number;
  badge_label: string;
  badge_color_token: string;
  driver_text: string;
}

export interface PersonalLifeConnection {
  from_type_code: string;
  from_label: string;
  to_type_code: string;
  to_label: string;
  summary: string;
  sentiment: string;
}

export interface PersonalLifeHappinessBar {
  label: string;
  height_fraction: number;
}

export interface PersonalLifeMetrics {
  life_health: PersonalLifeHealthHero;
  emotional_trend: { window_label: string; series: PersonalLifeTrendPoint[]; is_sparse?: boolean };
  dominant_emotion: {
    dominant_code: string;
    dominant_label: string;
    dominant_percent: number;
    breakdown: PersonalLifeEmotionBreakdown[];
    footer_text: string;
    is_sparse?: boolean;
  };
  balance_model: {
    subtitle: string;
    dimensions: PersonalLifeBalanceDimension[];
  };
  connections: PersonalLifeConnection[];
  drift_alert: { title: string; body: string; cta_label: string } | null;
  leverage: {
    title: string;
    body: string;
    cta_label: string;
    action_code: string;
    expected_impact: { dimension_code: string; label: string; delta: number }[];
  } | null;
  happiness: {
    top_drivers: string[];
    highest_return: PersonalLifeHappinessBar[];
    lowest_return: PersonalLifeHappinessBar[];
    footer_text: string;
  };
  intelligence: {
    preamble: string;
    insight_text: string;
    cta_label: string;
    cta_action_code?: string;
  };
  monthly_changes: {
    change_code: string;
    label: string;
    sublabel: string;
    delta_percent: number;
    direction: "UP" | "DOWN";
  }[];
  journey: { period_label: string; summary: string }[];
  quick_actions: {
    action_code: string;
    label: string;
    event_type: string | null;
    color_token: string;
  }[];
  footer_quote: string;
}

export interface PersonalLifeResponse {
  projection_version?: number;
  generated_at?: string;
  active_moment_count: number;
  is_empty: boolean;
  date_range_label: string | null;
  life_projection?: LifeProjection | null;
  metrics: PersonalLifeMetrics | null;
}

// --------------------------------------------------------------------------- #
// Template tab projections (Reference Vertical)
// --------------------------------------------------------------------------- #
export interface TemplateProgressBlock {
  key: string;
  label: string;
  value: string;
  tone: string;
}

export interface TemplateMomentsResponse {
  projection_version?: number;
  generated_at?: string;
  moment_type_code: string;
  status: "ACTIVE" | "SETUP" | "EMPTY";
  moment: PersonalMomentResponse | null;
  moment_projection?: MomentProjection | null;
  setup_summary: {
    pressure_sources: string[];
    recovery_supports: string[];
    runtime_priorities: string[];
    identity_chips: string[];
  };
  recent_events: Record<string, unknown>[];
  accounts_summary: {
    total_accounts: number;
    active_accounts: number;
    accounts: Record<string, unknown>[];
  };
  timeline_count: number;
  last_activity_at: string | null;
  progress: {
    label: string;
    subtitle: string;
    blocks: TemplateProgressBlock[];
  };
}

export interface TemplateLifeDimension {
  score: number;
  label: string;
  detail: string;
}

export interface TemplateLifeResponse {
  projection_version?: number;
  generated_at?: string;
  moment_type_code: string;
  status: string;
  headline: string;
  subtitle: string;
  operating_summary: {
    ops_index: number;
    momentum: { direction: string; label: string };
    today_vs_week: { spend_delta_percent: number; recovery_sessions: number };
  };
  dimensions: {
    financial_health: TemplateLifeDimension;
    recovery: TemplateLifeDimension;
    attention: TemplateLifeDimension;
    rhythm: TemplateLifeDimension;
    workload: TemplateLifeDimension;
    momentum: TemplateLifeDimension;
  };
  pressure_sources: string[];
  recovery_supports: string[];
  today: Record<string, unknown>;
  week: Record<string, unknown>;
  signals: Record<string, unknown>[];
  recent_activity: Record<string, unknown>[];
}

export interface TemplateMemoryItem {
  id: string;
  title: string;
  subtitle?: string | null;
  memory_type: string;
  occurred_at: string;
  source_event_ids: string[];
  tags: string[];
  importance: string;
}

export interface TemplateMemoryPattern {
  id: string;
  title: string;
  subtitle: string;
  occurrence_count: number;
  tags: string[];
}

export interface TemplateMemoryInsight {
  id: string;
  title: string;
  subtitle: string;
  confidence: number;
  insight_type: string;
  tags: string[];
}

export interface TemplateMemoryTimelinePeriod {
  period_label: string;
  period_start: string | null;
  memories: TemplateMemoryItem[];
}

export interface TemplateMemoryResponse {
  projection_version?: number;
  generated_at?: string;
  moment_type_code: string;
  status: string;
  memory_projection?: MemoryProjection | null;
  /** @deprecated legacy timeline memory — use memory_projection */
  memories?: TemplateMemoryItem[];
  patterns?: TemplateMemoryPattern[];
  insights?: TemplateMemoryInsight[];
  timeline?: TemplateMemoryTimelinePeriod[];
}
