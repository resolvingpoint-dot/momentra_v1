/** Circle domain — live API driven by sp_refresh_circle / circle_* tables. */

import { requestWithRetry } from "@/lib/api/client";
import { API_ENDPOINTS } from "@/lib/api/endpoints";

export type CircleHomeResponse = {
  context: string;
  state: string;
  counts?: {
    participants?: number;
    active_participants?: number;
    suggestions?: number;
  };
  empty_state_override?: Record<string, unknown> | null;
};

export type CircleParticipant = {
  circle_participant_id: string;
  user_id: string;
  participant_name: string;
  participant_user_id?: string | null;
  participant_phone?: string | null;
  participant_email?: string | null;
  first_seen_date?: string | null;
  last_seen_date?: string | null;
  is_active?: boolean | null;
};

export type CircleParticipantStats = {
  circle_participant_id: string;
  shared_moment_count?: number | null;
  active_moment_count?: number | null;
  recent_activity_count?: number | null;
  participation_score?: number | string | null;
  rank_order?: number | null;
  last_activity_date?: string | null;
};

export type CircleParticipantEntry = {
  participant: CircleParticipant;
  stats?: CircleParticipantStats | null;
  is_group_participant?: boolean;
  is_business_participant?: boolean;
};

export type CircleRecentActivity = {
  source_type: string;
  source_moment_id: string;
  source_moment_name?: string | null;
  source_moment_type?: string | null;
  participant_count?: number;
  last_activity_date?: string | null;
};

export type CircleSuggestion = {
  suggestion_id: string;
  suggestion_type: string;
  participant_ids_json?: unknown;
  suggestion_title: string;
  suggestion_description: string;
  confidence_score?: number | string | null;
  cta_label?: string | null;
  target_create_flow?: string | null;
  is_active?: boolean | null;
};

export type CircleReadResponse = {
  participants: CircleParticipantEntry[];
  suggestions: CircleSuggestion[];
  recent_activity?: CircleRecentActivity[];
};

export type CircleRefreshResponse = {
  refreshed: boolean;
  participant_count: number;
  suggestion_count: number;
};

export type CircleSummaryResponse = {
  participant_count: number;
  active_participant_count: number;
  suggestion_count: number;
};

export function isCircleEmptyState(state: string | null | undefined): boolean {
  const s = (state ?? "").toUpperCase();
  return s === "EMPTY" || s === "" || s === "NONE";
}

export async function getHome(): Promise<CircleHomeResponse> {
  return requestWithRetry<CircleHomeResponse>(API_ENDPOINTS.circle.home, {
    method: "GET",
  });
}

export async function refresh(): Promise<CircleRefreshResponse> {
  return requestWithRetry<CircleRefreshResponse>(API_ENDPOINTS.circle.refresh, {
    method: "POST",
  });
}

export async function read(): Promise<CircleReadResponse> {
  return requestWithRetry<CircleReadResponse>(API_ENDPOINTS.circle.read, {
    method: "GET",
  });
}

export async function summary(): Promise<CircleSummaryResponse> {
  return requestWithRetry<CircleSummaryResponse>(API_ENDPOINTS.circle.summary, {
    method: "GET",
  });
}

export const CircleRepository = {
  getHome,
  refresh,
  read,
  summary,
  isCircleEmptyState,
};
