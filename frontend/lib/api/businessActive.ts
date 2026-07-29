/** Team Operations active projection contracts (Run 8). */

export type SectionState = "empty" | "partial" | "complete";

export type TeamOpsEventItem = {
  event_id: string;
  action_type: string;
  title: string;
  subtitle?: string | null;
  occurred_at?: string;
  source_moment_id?: string | null;
};

export type TeamOpsHealth = {
  label: string;
  band: "empty" | "healthy" | "needs_attention" | "at_risk" | string;
  rule?: string;
  inputs?: Record<string, number | null>;
  score?: number;
  max_score?: number;
  open_issues_per_member_pct?: number;
  pending_approvals_per_member_pct?: number;
};

export type TeamOpsHealthDriver = {
  driver_code: string;
  driver_name: string;
  score: number;
  status: string;
  delta?: number;
  trend?: string;
  weight?: number;
};

export type TeamOpsProgressMetric = {
  metric_code: string;
  metric_name: string;
  score: number;
  delta?: number;
  status?: string;
  trend?: string;
};

export type TeamOpsSection<T extends Record<string, unknown> = Record<string, unknown>> = T & {
  state: SectionState | string;
};

export type TeamOpsPulseResponse = {
  moment_id: string;
  moment_type: string;
  moment_name?: string | null;
  team_name?: string | null;
  status: string;
  is_active: boolean;
  member_count?: number;
  activity_count?: number;
  operating_currency?: string;
  stats?: Record<string, number>;
  hero: TeamOpsSection<{
    title: string;
    subtitle?: string;
    status?: string;
    is_active?: boolean;
    overall_team_health?: TeamOpsHealth;
  }>;
  health_drivers: TeamOpsSection<{ items: TeamOpsHealthDriver[] }>;
  kpis: TeamOpsSection<{
    members: number;
    open_issues: number;
    pending_approvals: number;
    recognitions: number;
    meetings: number;
    escalations: number;
    participation: number;
    overall_team_health?: TeamOpsHealth;
  }>;
  approvals: TeamOpsSection<{ pending_count: number; items: TeamOpsEventItem[] }>;
  participation: TeamOpsSection<{ count: number; items: TeamOpsEventItem[] }>;
  issues: TeamOpsSection<{
    open_count: number;
    escalation_count: number;
    items: TeamOpsEventItem[];
  }>;
  recognition: TeamOpsSection<{ count: number; items: TeamOpsEventItem[] }>;
  recent_activity: TeamOpsSection<{ items: TeamOpsEventItem[] }>;
  attention: TeamOpsSection<{
    items: Array<{
      kind: string;
      label: string;
      count: number;
      severity?: string;
      description?: string;
    }>;
  }>;
  signals: TeamOpsSection<{
    items: Array<{
      signal_id?: string;
      signal_type?: string;
      title?: string;
      label?: string;
      summary?: string;
      change_percent?: number;
      priority?: string;
      severity?: string;
    }>;
  }>;
  next_action: TeamOpsSection<{
    item: {
      action_id: string;
      label: string;
      reason: string;
      cta_label?: string;
      target_screen?: string;
      priority?: string;
    } | null;
  }>;
};

export type TeamOpsMomentsResponse = {
  moment_id: string;
  moment_type: string;
  moment_name?: string | null;
  team_name?: string | null;
  status: string;
  operations_hub?: Record<string, number>;
  journey_hero: TeamOpsSection<{
    title: string;
    subtitle?: string;
    member_count?: number;
    activity_count?: number;
    is_active?: boolean;
  }>;
  progress_snapshot: TeamOpsSection<{ items: TeamOpsProgressMetric[] }>;
  highlights: TeamOpsSection<{ items: TeamOpsEventItem[] }>;
  milestones: TeamOpsSection<{ items: TeamOpsEventItem[] }>;
  meetings: TeamOpsSection<{ count?: number; items: TeamOpsEventItem[] }>;
  approvals: TeamOpsSection<{ pending_count?: number; items: TeamOpsEventItem[] }>;
  recognition: TeamOpsSection<{ count?: number; items: TeamOpsEventItem[] }>;
  issues: TeamOpsSection<{ open_count?: number; items: TeamOpsEventItem[] }>;
  team_changes: TeamOpsSection<{ items: TeamOpsEventItem[] }>;
  timeline: TeamOpsSection<{ items: TeamOpsEventItem[] }>;
  recent_activity: TeamOpsSection<{ items: TeamOpsEventItem[] }>;
};

export type BusinessLifeSlice = {
  key: string;
  label: string;
  state: string;
  count: number;
  band?: string;
  items?: TeamOpsEventItem[];
  inputs?: Record<string, number | null>;
  source_moment_id?: string;
  source_moment_name?: string;
};

export type BusinessLifeSignal = {
  signal_type?: string;
  dimension?: string;
  severity?: string;
  count?: number;
  label: string;
};

export type BusinessLifeDimension = {
  key: string;
  label: string;
  band: string;
  state: string;
  count: number;
  source_slice?: string;
  source_moment_id?: string | null;
  source_moment_name?: string | null;
};

export type BusinessLifeJourneyItem = {
  kind?: string;
  title: string;
  occurred_at?: string | null;
  event_id?: string | null;
  source_moment_id?: string | null;
};

export type BusinessLifeHealth = {
  band: string;
  label: string;
  active_dimension_count?: number;
  description?: string;
};

export type BusinessLifeResponse = {
  active_moment_count: number;
  moments: Array<{
    moment_id: string;
    moment_type: string;
    moment_name: string;
    status: string;
  }>;
  health?: BusinessLifeHealth;
  signals?: BusinessLifeSignal[];
  dimensions?: BusinessLifeDimension[];
  journey?: BusinessLifeJourneyItem[];
  slices: Record<string, BusinessLifeSlice>;
};

export type BusinessMemoryEvent = {
  event_id: string;
  action_type: string;
  title: string;
  occurred_at?: string;
  source_moment_id?: string;
  source_moment_name?: string;
  source_moment_type?: string;
};

export type BusinessMemorySummary = {
  active_moment_count: number;
  event_count: number;
  months_active: number;
  description?: string;
};

export type BusinessMemorySourceFilter = {
  key: string;
  label: string;
  moment_types: string[];
};

export type BusinessMemoryMemoryItem = {
  kind?: string;
  title: string;
  detail?: string;
  observed_count?: number;
  impact?: string;
};

export type BusinessMemoryJourneyItem = {
  kind?: string;
  title: string;
  occurred_at?: string | null;
  event_id?: string | null;
  source_moment_id?: string | null;
};

export type BusinessMemoryResponse = {
  active_moment_count: number;
  moments?: Array<{ moment_id: string; moment_type: string; moment_name: string; status: string }>;
  summary?: BusinessMemorySummary;
  source_filters?: BusinessMemorySourceFilter[];
  patterns?: Array<{ pattern_type?: string; dimension?: string; label?: string; count?: number } | string>;
  success_memory?: BusinessMemoryMemoryItem[];
  risk_memory?: BusinessMemoryMemoryItem[];
  playbooks?: unknown[];
  journey?: BusinessMemoryJourneyItem[];
  events: BusinessMemoryEvent[];
  buckets: Record<string, { state: string; items: BusinessMemoryEvent[] }>;
};

export type BusinessActivityListItem = {
  event_id: string;
  action_type: string;
  title: string;
  subtitle?: string | null;
  created_at?: string;
  occurred_at?: string;
  created_by?: string | null;
  source?: string | null;
  is_voided?: boolean;
  payload?: Record<string, unknown>;
  /** Server-owned — clients must not infer from registries. */
  is_editable: boolean;
  is_deletable: boolean;
  supported_actions: string[];
  /** Set by parser when API emitted is_editable / is_deletable. */
  _flags_from_api?: boolean;
  [key: string]: unknown;
};

export type BusinessActivityListResponse = {
  items: BusinessActivityListItem[];
  total: number;
  page: number;
  page_size: number;
};

export const TEAM_OPS_PULSE_SECTION_KEYS = [
  "hero",
  "health_drivers",
  "kpis",
  "approvals",
  "participation",
  "issues",
  "recognition",
  "recent_activity",
  "attention",
  "signals",
  "next_action",
] as const;

export const TEAM_OPS_MOMENTS_SECTION_KEYS = [
  "journey_hero",
  "progress_snapshot",
  "highlights",
  "milestones",
  "meetings",
  "approvals",
  "recognition",
  "issues",
  "team_changes",
  "timeline",
  "recent_activity",
] as const;

export const TEAM_OPS_LIFE_SLICE_KEYS = [
  "team_health",
  "governance",
  "collaboration",
  "execution",
  "participation",
  "recognition",
  "issues",
] as const;

export type RunwayHealth = {
  label: string;
  band: "empty" | "healthy" | "needs_attention" | "at_risk" | "critical" | string;
  rule?: string;
  inputs?: Record<string, number | null>;
};

export type RunwayPulseResponse = {
  moment_id: string;
  moment_type: string;
  moment_name?: string | null;
  runway_name?: string | null;
  status: string;
  is_active: boolean;
  operating_currency?: string;
  stats?: Record<string, number | null>;
  hero: TeamOpsSection<{
    title: string;
    subtitle?: string;
    runway_health?: RunwayHealth;
  }>;
  runway_health: TeamOpsSection<{ health: RunwayHealth }>;
  cash_position: TeamOpsSection<{ cash_available_minor: number; operating_currency?: string }>;
  monthly_burn: TeamOpsSection<{ monthly_burn_minor: number; activity_burn_minor?: number }>;
  revenue_trend: TeamOpsSection<{ monthly_revenue_minor: number; revenue_status?: string | null }>;
  collection_rate: TeamOpsSection<{ collection_rate_percent: number | null }>;
  runway_months: TeamOpsSection<{
    runway_months: number | null;
    runway_goal_months?: number | null;
    alert_threshold_months?: number | null;
  }>;
  cash_movement: TeamOpsSection<{
    total_inflow_minor: number;
    total_burn_minor: number;
    net_burn_minor: number;
  }>;
  kpis: TeamOpsSection<Record<string, number | null>>;
  forecast: TeamOpsSection<{
    runway_goal_months?: number | null;
    projected_runway_months?: number | null;
    alert_threshold_months?: number | null;
  }>;
  attention_items: TeamOpsSection<{
    items: Array<{
      kind: string;
      label: string;
      count: number;
      severity?: string;
      description?: string;
    }>;
  }>;
  trends: TeamOpsSection<{
    items: Array<{ trend_code: string; label: string; count: number; window_days?: number }>;
  }>;
  signals: TeamOpsSection<{
    items: Array<{
      signal_type?: string;
      label?: string;
      title?: string;
      summary?: string;
      change_percent?: number;
      severity?: string;
    }>;
  }>;
  recent_activity: TeamOpsSection<{ items: TeamOpsEventItem[] }>;
  next_best_action: TeamOpsSection<{
    item: {
      action_id: string;
      label: string;
      reason: string;
      cta_label?: string;
      target_screen?: string;
      priority?: string;
    } | null;
  }>;
};

export type RunwayMomentsResponse = {
  moment_id: string;
  moment_type: string;
  moment_name?: string | null;
  runway_name?: string | null;
  status: string;
  runway_hub?: {
    cash_available_minor?: number | null;
    monthly_burn_minor?: number | null;
    runway_months?: number | null;
    risk_count?: number | null;
    decision_count?: number | null;
    operating_currency?: string | null;
  };
  journey_hero: TeamOpsSection<{
    title: string;
    subtitle?: string;
    activity_count?: number;
    is_active?: boolean;
    runway_months?: number | null;
  }>;
  cash_available: TeamOpsSection<{ cash_available_minor: number; operating_currency?: string }>;
  runway_months: TeamOpsSection<{ runway_months: number | null; runway_goal_months?: number | null }>;
  timeline: TeamOpsSection<{ items: TeamOpsEventItem[] }>;
  revenue_updates: TeamOpsSection<{ items: TeamOpsEventItem[] }>;
  forecast_changes: TeamOpsSection<{ items: TeamOpsEventItem[] }>;
  expense_events: TeamOpsSection<{ items: TeamOpsEventItem[] }>;
  inflow_events: TeamOpsSection<{ items: TeamOpsEventItem[] }>;
  funding_events: TeamOpsSection<{ items: TeamOpsEventItem[] }>;
  invoices: TeamOpsSection<{ items: TeamOpsEventItem[]; empty_reason?: string }>;
  payroll: TeamOpsSection<{ items: TeamOpsEventItem[]; empty_reason?: string }>;
  milestones: TeamOpsSection<{ items: TeamOpsEventItem[] }>;
  recent_activity: TeamOpsSection<{ items: TeamOpsEventItem[] }>;
};

export const RUNWAY_PULSE_SECTION_KEYS = [
  "hero",
  "runway_health",
  "cash_position",
  "monthly_burn",
  "revenue_trend",
  "collection_rate",
  "runway_months",
  "cash_movement",
  "kpis",
  "forecast",
  "attention_items",
  "trends",
  "signals",
  "recent_activity",
  "next_best_action",
] as const;

export const RUNWAY_MOMENTS_SECTION_KEYS = [
  "journey_hero",
  "runway_hub",
  "cash_available",
  "runway_months",
  "timeline",
  "revenue_updates",
  "forecast_changes",
  "expense_events",
  "inflow_events",
  "funding_events",
  "invoices",
  "payroll",
  "milestones",
  "recent_activity",
] as const;

export const RUNWAY_LIFE_SLICE_KEYS = [
  "financial_health",
  "stability",
  "cash_flow",
  "growth",
  "discipline",
  "risk",
  "forecast_accuracy",
] as const;

/** Business Operations health — rule bands only (no composite score). */
export type OpsHealthBand = "EMPTY" | "HEALTHY" | "NEEDS_ATTENTION" | "AT_RISK" | string;

export type OpsHealth = {
  label: string;
  band: OpsHealthBand;
  rule?: string;
  drivers?: Record<string, number | null>;
};

export type OpsPulseResponse = {
  moment_id: string;
  moment_type: string;
  moment_name?: string | null;
  operations_name?: string | null;
  status: string;
  is_active: boolean;
  operating_currency?: string;
  stats?: Record<string, number | null>;
  hero: TeamOpsSection<{
    moment_name?: string;
    operations_name?: string;
    operations_scope?: string | null;
    operating_model?: string | null;
    owner?: string | null;
    last_updated?: string | null;
    title?: string;
    subtitle?: string;
  }>;
  operations_health: TeamOpsSection<{
    label: string;
    band: OpsHealthBand;
    rule?: string;
    drivers?: Record<string, number | null>;
  }>;
  kpis: TeamOpsSection<{
    monthly_budget_minor?: number | null;
    spent_minor?: number | null;
    remaining_minor?: number | null;
    budget_usage_percent?: number | null;
    pending_approval_count?: number | null;
    open_issue_count?: number | null;
    active_vendor_count?: number | null;
    completed_improvement_count?: number | null;
  }>;
  budget_usage: TeamOpsSection<{
    total_budget_minor: number;
    total_spend_minor: number;
    remaining_minor: number;
    allocations?: unknown[];
    over_budget_allocations?: unknown[];
    unallocated_minor?: number;
    operating_currency?: string;
  }>;
  approvals: TeamOpsSection<{
    pending: number;
    overdue: number;
    approved_recently: number;
    rejected_recently: number;
    amount_awaiting_minor?: number | null;
  }>;
  issues: TeamOpsSection<{
    open: number;
    critical: number;
    overdue: number;
    unassigned: number;
    resolved_recently: number;
  }>;
  vendors: TeamOpsSection<{
    active: number;
    status_changes: number;
    critical_dependencies: number;
    unresolved_events: number;
  }>;
  improvements: TeamOpsSection<{
    planned: number;
    in_progress: number;
    completed: number;
    overdue: number;
  }>;
  monitoring: TeamOpsSection<{
    level?: string | null;
    active_alerts?: unknown[];
    recipients?: unknown[];
  }>;
  attention_items: TeamOpsSection<{
    items: Array<{
      kind: string;
      label: string;
      count?: number;
      severity?: string;
      description?: string;
    }>;
  }>;
  signals: TeamOpsSection<{
    items: Array<{
      signal_type?: string;
      label?: string;
      title?: string;
      summary?: string;
      change_percent?: number;
      severity?: string;
    }>;
  }>;
  recent_activity: TeamOpsSection<{ items: TeamOpsEventItem[] }>;
  next_best_action: TeamOpsSection<{
    item: {
      action_id: string;
      renderer_id?: string;
      title?: string;
      label?: string;
      subtitle?: string;
      reason?: string;
      cta_label?: string;
      metadata?: Record<string, unknown>;
    } | null;
  }>;
};

export type OpsMilestoneItem = {
  kind?: string;
  title: string;
  occurred_at?: string | null;
  event_id?: string;
};

export type OpsMomentsResponse = {
  moment_id: string;
  moment_type: string;
  moment_name?: string | null;
  operations_name?: string | null;
  status: string;
  journey_hero: TeamOpsSection<{
    title: string;
    start_date?: string | null;
    current_phase?: string | null;
    progress_percent?: number | null;
    subtitle?: string;
  }>;
  summary_stats: TeamOpsSection<{
    budget_used_percent?: number;
    approvals?: number;
    open_issues?: number;
    vendors?: number;
    improvements?: number;
  }>;
  spend_timeline: TeamOpsSection<{ items: TeamOpsEventItem[] }>;
  approval_timeline: TeamOpsSection<{ items: TeamOpsEventItem[] }>;
  issue_timeline: TeamOpsSection<{ items: TeamOpsEventItem[] }>;
  vendor_timeline: TeamOpsSection<{ items: TeamOpsEventItem[] }>;
  improvement_timeline: TeamOpsSection<{ items: TeamOpsEventItem[] }>;
  milestones: TeamOpsSection<{ items: OpsMilestoneItem[] }>;
  key_decisions: TeamOpsSection<{ items: TeamOpsEventItem[] }>;
  timeline: TeamOpsSection<{ items: TeamOpsEventItem[] }>;
  recent_activity: TeamOpsSection<{ items: TeamOpsEventItem[] }>;
};

export const OPS_PULSE_SECTION_KEYS = [
  "hero",
  "operations_health",
  "kpis",
  "budget_usage",
  "approvals",
  "issues",
  "vendors",
  "improvements",
  "monitoring",
  "attention_items",
  "signals",
  "recent_activity",
  "next_best_action",
] as const;

export const OPS_MOMENTS_SECTION_KEYS = [
  "journey_hero",
  "summary_stats",
  "spend_timeline",
  "approval_timeline",
  "issue_timeline",
  "vendor_timeline",
  "improvement_timeline",
  "milestones",
  "key_decisions",
  "timeline",
  "recent_activity",
] as const;

export const OPS_LIFE_SLICE_KEYS = [
  "operational_health",
  "budget_discipline",
  "approval_efficiency",
  "vendor_health",
  "issue_load",
  "improvement_momentum",
  "governance",
  "execution",
] as const;
