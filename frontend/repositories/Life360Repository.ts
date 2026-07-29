/** Life360 domain — live API only (no mock fixtures). */

import { requestWithRetry } from "@/lib/api/client";
import { API_ENDPOINTS } from "@/lib/api/endpoints";

export type Life360HomeResponse = {
  module: string;
  state: string;
  counts?: {
    personal_signals?: number;
    group_signals?: number;
    business_signals?: number;
  };
  empty_state_override?: Record<string, unknown> | null;
};

export type Life360Snapshot = {
  life360_snapshot_id: string;
  user_id: string;
  snapshot_date: string;
  snapshot_month: string;
  life_alignment_score: number | string;
  source_personal_snapshot_id?: string | null;
  source_group_snapshot_id?: string | null;
  source_business_snapshot_id?: string | null;
  personal_score?: number | string | null;
  group_score?: number | string | null;
  business_score?: number | string | null;
  life_phase?: string | null;
  money_score?: number | string | null;
  relationship_score?: number | string | null;
  execution_score?: number | string | null;
  growth_score?: number | string | null;
  personal_energy_pct?: number | string | null;
  group_energy_pct?: number | string | null;
  business_energy_pct?: number | string | null;
  momentum_score?: number | string | null;
  momentum_status?: string | null;
  strongest_driver?: string | null;
  biggest_tension?: string | null;
  money_status?: string | null;
  relationship_status?: string | null;
  execution_status?: string | null;
  growth_status?: string | null;
  reflection_summary?: string | null;
  active_dimensions_count?: number | null;
  signal_confidence_score?: number | string | null;
  created_at?: string | null;
  updated_at?: string | null;
};

export type Life360DimensionStat = {
  dimension: string;
  score?: number | string | null;
  status?: string | null;
};

export type Life360AnalyticsResponse = {
  snapshot_date?: string | null;
  life_alignment_score?: number | string | null;
  signal_confidence_score?: number | string | null;
  momentum_score?: number | string | null;
  momentum_status?: string | null;
  strongest_driver?: string | null;
  biggest_tension?: string | null;
  dimensions?: Life360DimensionStat[];
  energy?: {
    personal_pct?: number | string | null;
    group_pct?: number | string | null;
    business_pct?: number | string | null;
  };
  domain_scores?: Record<string, number | string | null>;
  trend?: Array<{
    snapshot_date: string;
    life_alignment_score: number | string;
  }>;
};

export type Life360RefreshResponse = {
  refreshed: boolean;
  snapshot: Life360Snapshot | null;
};

export type Life360SummaryResponse = {
  snapshot_date?: string | null;
  life_alignment_score?: number | string | null;
  life_phase?: string | null;
  momentum_score?: number | string | null;
  momentum_status?: string | null;
  strongest_driver?: string | null;
  biggest_tension?: string | null;
  reflection_summary?: string | null;
  active_dimensions_count?: number | null;
};

export function toNumber(value: number | string | null | undefined): number | null {
  if (value == null || value === "") return null;
  const n = typeof value === "number" ? value : Number(value);
  return Number.isFinite(n) ? n : null;
}

export function formatScore(value: number | string | null | undefined): string {
  const n = toNumber(value);
  if (n == null) return "—";
  return Number.isInteger(n) ? String(n) : n.toFixed(0);
}

export function formatSignedScore(value: number | string | null | undefined): string {
  const n = toNumber(value);
  if (n == null) return "—";
  const rounded = Number.isInteger(n) ? n : Math.round(n);
  return rounded > 0 ? `+${rounded}` : String(rounded);
}

export function isLife360EmptyState(state: string | null | undefined): boolean {
  const s = (state ?? "").toUpperCase();
  return s === "EMPTY" || s === "" || s === "NONE";
}

export async function getHome(): Promise<Life360HomeResponse> {
  return requestWithRetry<Life360HomeResponse>(API_ENDPOINTS.life360.home, {
    method: "GET",
  });
}

export async function refresh(force = false): Promise<Life360RefreshResponse> {
  const qs = force ? "?force=true" : "";
  return requestWithRetry<Life360RefreshResponse>(
    `${API_ENDPOINTS.life360.refresh}${qs}`,
    { method: "POST" },
  );
}

export async function read(): Promise<Life360Snapshot> {
  return requestWithRetry<Life360Snapshot>(API_ENDPOINTS.life360.read, {
    method: "GET",
  });
}

export async function analytics(trendLimit = 12): Promise<Life360AnalyticsResponse> {
  return requestWithRetry<Life360AnalyticsResponse>(
    `${API_ENDPOINTS.life360.analytics}?trend_limit=${trendLimit}`,
    { method: "GET" },
  );
}

export async function summary(): Promise<Life360SummaryResponse> {
  return requestWithRetry<Life360SummaryResponse>(API_ENDPOINTS.life360.summary, {
    method: "GET",
  });
}

export const Life360Repository = {
  getHome,
  refresh,
  read,
  analytics,
  summary,
  toNumber,
  formatScore,
  formatSignedScore,
  isLife360EmptyState,
};
