import { requestWithRetry } from "@/lib/api/client";

/* ------------------------------------------------------------------ */
/*  Types                                                             */
/* ------------------------------------------------------------------ */

export type BusinessActionCapabilities = {
  drafts?: boolean;
  favorites?: boolean;
  search?: boolean;
  review?: boolean;
  attachments?: boolean;
  participants?: boolean;
  offline?: boolean;
};

export type BusinessRendererField = {
  key: string;
  label: string;
  field_type: string;
  required?: boolean;
  options?: Array<{ value: string; label: string }>;
  placeholder?: string;
  default_value?: string | boolean;
  default?: string | boolean;
  step_id?: string;
  step_title?: string;
  visible_when?: { field: string; equals: string };
  label_when?: Array<{ field: string; equals: string; label: string }>;
  multiple?: boolean;
  searchable?: boolean;
  allow_custom?: boolean;
};

export type BusinessCatalogAction = {
  action_id: string;
  action_type: string;
  label: string;
  icon: string;
  renderer_id: string;
  category_id: string;
  cta_label: string;
  supports: BusinessActionCapabilities;
  subtitle?: string;
  estimated_time_sec?: number;
  tags?: string[];
  synonyms?: string[];
  priority?: number;
  /** Embedded renderer schema — prefer over GET .../renderer */
  fields?: BusinessRendererField[];
  required_fields?: string[];
};

export type BusinessCatalogCategory = {
  id: string;
  label: string;
  actions: BusinessCatalogAction[];
};

export type BusinessCatalogMember = {
  member_id?: string;
  id?: string;
  name?: string;
  display_name?: string;
  role?: string;
  user_id?: string | null;
  avatar_url?: string;
};

export type BusinessActionCatalogResponse = {
  moment_id: string;
  moment_type: string;
  template_id: string;
  /** Bump invalidates client schema caches */
  schema_version?: number;
  categories: BusinessCatalogCategory[];
  actions: BusinessCatalogAction[];
  members: BusinessCatalogMember[];
};

export type BusinessRendererMeta = {
  renderer_id: string;
  title?: string;
  label?: string;
  fields: BusinessRendererField[];
  required_fields?: string[];
  review_enabled?: boolean;
  cta_label?: string;
  supports?: BusinessActionCapabilities;
  steps?: Array<{ id: string; title: string; field_keys: string[] }>;
};

export type BusinessActivityPayload = {
  action_type: string;
  title: string;
  subtitle?: string;
  payload: Record<string, unknown>;
  client_request_id?: string;
  source: "action_center";
};

export type BusinessActivityResponse = {
  event_id?: string;
  action_type?: string;
  title?: string;
  created_at?: string;
  activity?: Record<string, unknown>;
  projection_hint?: Record<string, unknown>;
  [key: string]: unknown;
};

/* ------------------------------------------------------------------ */
/*  Repository functions                                              */
/* ------------------------------------------------------------------ */

export async function fetchCatalog(
  momentId: string,
): Promise<BusinessActionCatalogResponse> {
  return requestWithRetry<BusinessActionCatalogResponse>(
    `/api/v1/business/active/${momentId}/action-catalog`,
    { method: "GET" },
  );
}

export async function fetchRendererMeta(
  momentId: string,
  actionKey: string,
): Promise<BusinessRendererMeta> {
  return requestWithRetry<BusinessRendererMeta>(
    `/api/v1/business/active/${momentId}/actions/${actionKey}/renderer`,
    { method: "GET" },
  );
}

export async function createAction(
  momentId: string,
  body: BusinessActivityPayload,
): Promise<BusinessActivityResponse> {
  return requestWithRetry<BusinessActivityResponse>(
    `/api/v1/business/active/${momentId}/activity`,
    { method: "POST", body: JSON.stringify(body) },
  );
}

export async function patchAction(
  momentId: string,
  eventId: string,
  body: Partial<BusinessActivityPayload>,
): Promise<BusinessActivityResponse> {
  return requestWithRetry<BusinessActivityResponse>(
    `/api/v1/business/active/${momentId}/activity/${eventId}`,
    { method: "PATCH", body: JSON.stringify(body) },
  );
}

export async function deleteAction(
  momentId: string,
  eventId: string,
): Promise<void> {
  return requestWithRetry<void>(
    `/api/v1/business/active/${momentId}/activity/${eventId}`,
    { method: "DELETE" },
  );
}
