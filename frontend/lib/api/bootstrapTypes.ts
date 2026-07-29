import type { UserResponse } from "@/lib/api/types";

/** Backend context keys from /app/bootstrap and /app/preferences */
export type BackendContextKey = "MY_MONEY" | "GROUP" | "BUSINESS" | "CIRCLE";

export type ContextState = "EMPTY" | "ACTIVE" | "DRAFT" | string;

export interface BootstrapContextEntry {
  key: BackendContextKey;
  label: string;
  state: ContextState;
}

export interface BootstrapModuleEntry {
  state: ContextState;
}

export interface BootstrapPreferences {
  id: string;
  user_id: string;
  selected_context: BackendContextKey;
  default_currency_code: string;
  locale: string;
  country_code: string;
  timezone: string;
  created_at: string;
  updated_at: string;
}

export interface BootstrapSummaryCounts {
  my_money_moments: number;
  group_moments: number;
  business_moments: number;
  circle_participants: number;
  memories: number;
}

export interface BootstrapResponse {
  user: UserResponse;
  preferences: BootstrapPreferences;
  contexts: BootstrapContextEntry[];
  modules: Record<string, BootstrapModuleEntry>;
  summary_counts: BootstrapSummaryCounts;
  reference_data_version: number;
  template_version?: number;
  ui_schema_version?: number;
  quick_add_version?: number;
  setup_version?: number;
  metadata_version?: number;
  server_time: string;
}

export type BootstrapVersionFields = Pick<
  BootstrapResponse,
  | "reference_data_version"
  | "template_version"
  | "ui_schema_version"
  | "quick_add_version"
  | "setup_version"
  | "metadata_version"
>;

export interface PreferenceUpdateRequest {
  selected_context?: BackendContextKey;
  default_currency_code?: string;
  locale?: string;
  country_code?: string;
  timezone?: string;
}

export type PreferenceUpdateResponse = BootstrapPreferences;
