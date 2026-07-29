import { requestWithRetry } from "@/lib/api/client";

export type GroupLifeSatelliteScore = {
  moment_type_code: string;
  label: string;
  score: number | null;
  color_token: string;
};

export type GroupLifeHealthHero = {
  life_score: number;
  status_label: string;
  delta_month: number | null;
  insight_quote: string;
  satellite_scores: GroupLifeSatelliteScore[];
};

export type GroupLifeBalanceDimension = {
  dimension_code: string;
  label: string;
  score: number;
  badge_label: string;
  badge_color_token: string;
};

export type GroupLifeBalanceModel = {
  subtitle: string;
  dimensions: GroupLifeBalanceDimension[];
};

export type GroupLifeDriver = {
  source_type_code: string;
  title: string;
  relation: string;
  icon: string;
  accent_token: string;
  impact_percent: number;
  body: string;
  action: string;
  priority: string;
};

export type GroupLifeDriftAlert = {
  title: string;
  body: string;
  impact_label: string;
  impact_body: string;
};

export type GroupLifeLeverage = {
  title: string;
  impact_lines: string[];
  impact_score: number;
  confidence_label: string;
};

export type GroupLifeEvolutionPoint = {
  label: string;
  value: number;
};

export type GroupLifeEvolutionSeries = {
  dimension_code: string;
  label: string;
  delta_percent: number;
  color_token: string;
  points: GroupLifeEvolutionPoint[];
};

export type GroupLifeMonthlyChange = {
  change_code: string;
  label: string;
  delta_percent: number;
  color_token: string;
};

export type GroupLifeJourneyItem = {
  event_key: string;
  title: string;
  subtitle?: string | null;
  icon: string;
  accent_token: string;
  is_current?: boolean;
};

export type GroupLifeIntelligence = {
  insight_text: string;
  confidence_label: string;
  dimension_pills: string[];
};

export type GroupLifeQuickAction = {
  action_code: string;
  label: string;
  moment_type_code: string;
  color_token: string;
};

export type GroupLifeMetrics = {
  life_health: GroupLifeHealthHero;
  balance_model: GroupLifeBalanceModel;
  drivers: GroupLifeDriver[];
  drift_alert: GroupLifeDriftAlert | null;
  leverage: GroupLifeLeverage | null;
  evolution: GroupLifeEvolutionSeries[];
  monthly_changes: GroupLifeMonthlyChange[];
  journey: GroupLifeJourneyItem[];
  intelligence: GroupLifeIntelligence;
  quick_actions: GroupLifeQuickAction[];
};

export type GroupLifeResponse = {
  active_moment_count: number;
  is_empty: boolean;
  date_range_label: string | null;
  metrics: GroupLifeMetrics | null;
};

export async function getGroupLife(): Promise<GroupLifeResponse> {
  return requestWithRetry<GroupLifeResponse>("/api/v1/group/life");
}
