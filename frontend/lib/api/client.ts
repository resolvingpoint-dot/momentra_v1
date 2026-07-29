import {
  clearLegacyRefreshToken,
  clearTokens,
  getAccessToken,
  getLegacyRefreshToken,
  saveAccessToken,
} from "@/lib/auth/tokens";
import { API_ENDPOINTS } from "@/lib/api/endpoints";
import type {
  BootstrapResponse,
  PreferenceUpdateRequest,
  PreferenceUpdateResponse,
} from "@/lib/api/bootstrapTypes";
import type {
  FirebaseExchangeRequest,
  FirebaseExchangeResponse,
  RefreshTokenRequest,
  TokenResponse,
  UserResponse,
  AvatarUploadUrlRequest,
  AvatarUploadUrlResponse,
  AvatarConfirmRequest,
  UserProfileUpdateRequest,
} from "@/lib/api/types";
import type {
  PersonalCreateOptionsResponse,
  PersonalMomentCreateRequest,
  PersonalMomentResponse,
  PersonalMomentUpdateRequest,
  PersonalLifeResponse,
  PersonalMemoryResponse,
  PersonalMomentsHomeResponse,
  PersonalPulseResponse,
  PersonalSetupAnswers,
  PersonalSetupPreview,
  PersonalSetupResponse,
  PersonalSetupSubmitRequest,
  TemplateLifeResponse,
  TemplateMemoryResponse,
  TemplateMomentsResponse,
} from "@/lib/api/personal";
import {
  endSpan,
  recordResponseHeaders,
  startSpan,
} from "@/lib/telemetry/performanceTelemetry";
import { createClientRequestId } from "@/lib/quick_add/draftStore";

const baseUrl = (
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "https://api.mallaapp.org"
).replace(/\/$/, "");

/** Match Android/iOS (~30s). Web was 15s and timed out on Business Pulse over ngrok while mobile succeeded. */
const REQUEST_TIMEOUT_MS = 30_000;

const WEB_CLIENT_HEADER = "X-Momentra-Client";
const WEB_CLIENT_VALUE = "web";

function applyWebAuthHeaders(headers: Headers): void {
  headers.set(WEB_CLIENT_HEADER, WEB_CLIENT_VALUE);
}

export enum ApiErrorCode {
  APP_ERROR = "app_error",
  VALIDATION_ERROR = "validation_error",
  NOT_FOUND = "not_found",
  PERMISSION_DENIED = "permission_denied",
  CONFLICT = "conflict",
  INVALID_STATE_TRANSITION = "invalid_state_transition",
  INVALID_CURRENCY = "invalid_currency",
  ACCOUNT_ARCHIVED = "account_archived",
  DRAFT_CONFLICT = "draft_conflict",
  REFERENCE_DATA_STALE = "reference_data_stale",
  SNAPSHOT_REBUILDING = "snapshot_rebuilding",
}

export function getUserMessage(code: string | undefined, fallback?: string): string {
  switch (code) {
    case ApiErrorCode.VALIDATION_ERROR:
      return fallback ?? "Please check your input and try again.";
    case ApiErrorCode.NOT_FOUND:
      return "We couldn't find that item. It may have been removed.";
    case ApiErrorCode.PERMISSION_DENIED:
      return "You don't have permission to do that.";
    case ApiErrorCode.CONFLICT:
      return fallback ?? "This conflicts with existing data.";
    case ApiErrorCode.INVALID_STATE_TRANSITION:
      return "That action isn't allowed in the current state.";
    case ApiErrorCode.INVALID_CURRENCY:
      return "That currency isn't supported. Choose another.";
    case ApiErrorCode.ACCOUNT_ARCHIVED:
      return "That account is archived. Choose an active account.";
    case ApiErrorCode.DRAFT_CONFLICT:
      return "Your draft was updated elsewhere. Refresh and try again.";
    case ApiErrorCode.REFERENCE_DATA_STALE:
      return "App data is updating. Please wait a moment and retry.";
    case ApiErrorCode.SNAPSHOT_REBUILDING:
      return "Your dashboard is refreshing. Try again in a few seconds.";
    default:
      return fallback ?? "Something went wrong. Please try again.";
  }
}

type ParsedApiError = {
  message: string;
  code?: string;
  details?: unknown;
};

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public code?: string,
    public details?: unknown,
  ) {
    super(message);
    this.name = "ApiError";
  }

  get userMessage(): string {
    return getUserMessage(this.code, this.message);
  }
}

async function parseError(res: Response): Promise<ParsedApiError> {
  try {
    const body = (await res.json()) as {
      error?: { code?: string; message?: string; details?: unknown };
      detail?: string | { msg?: string }[];
    };
    if (body.error?.message) {
      return {
        message: body.error.message,
        code: body.error.code,
        details: body.error.details,
      };
    }
    if (typeof body.detail === "string") {
      return { message: body.detail };
    }
    if (Array.isArray(body.detail) && body.detail[0]?.msg) {
      return { message: body.detail[0].msg };
    }
  } catch {
    // ignore
  }
  return { message: `Request failed (${res.status})` };
}

async function fetchWithTimeout(
  url: string,
  init: RequestInit,
  signal?: AbortSignal,
): Promise<Response> {
  const controller = new AbortController();
  let timedOut = false;
  const timeoutId = setTimeout(() => {
    timedOut = true;
    controller.abort();
  }, REQUEST_TIMEOUT_MS);
  const onExternalAbort = () => controller.abort();
  signal?.addEventListener("abort", onExternalAbort);
  try {
    return await fetch(url, {
      ...init,
      signal: controller.signal,
    });
  } catch (err) {
    if (err instanceof Error && err.name === "AbortError") {
      if (signal?.aborted && !timedOut) {
        throw err; // Caller cancelled — not a timeout.
      }
      throw new ApiError("Request timed out", 408);
    }
    const base = baseUrl.replace(/\/$/, "");
    const hint = base.includes("ngrok")
      ? "Check that the backend and ngrok tunnel are running on your dev machine."
      : "Check that the backend is running (uvicorn on port 8000).";
    throw new ApiError(
      `Cannot reach the Momentra API at ${base}. ${hint}`,
      0,
      ApiErrorCode.APP_ERROR,
    );
  } finally {
    clearTimeout(timeoutId);
    signal?.removeEventListener("abort", onExternalAbort);
  }
}

function joinApiUrl(base: string, path: string): string {
  const normalizedPath = path.replace(/^\/+/, "");
  return `${base}/${normalizedPath}`;
}

/** Absolute http(s) unchanged; relative stubs (e.g. /local-uploads/...) → API origin. */
export function resolveMediaUrl(url: string | null | undefined): string | null {
  if (!url) return null;
  const trimmed = url.trim();
  if (!trimmed) return null;
  if (trimmed.startsWith("http://") || trimmed.startsWith("https://")) {
    return trimmed;
  }
  return joinApiUrl(baseUrl, trimmed);
}

async function request<T>(
  path: string,
  options: RequestInit & {
    authenticated?: boolean;
    signal?: AbortSignal;
    telemetrySpanId?: string;
    /** Include cookies (refresh HttpOnly) and web CSRF header. */
    withCredentials?: boolean;
  } = {},
): Promise<T> {
  const {
    authenticated = false,
    signal,
    telemetrySpanId,
    withCredentials = false,
    ...init
  } = options;
  const headers = new Headers(init.headers);
  headers.set("Content-Type", "application/json");
  if (baseUrl.includes("ngrok")) {
    headers.set("ngrok-skip-browser-warning", "true");
  }
  if (withCredentials) {
    applyWebAuthHeaders(headers);
  }

  if (authenticated) {
    const token = getAccessToken();
    if (!token) throw new ApiError("Not signed in", 401);
    headers.set("Authorization", `Bearer ${token}`);
  }

  const res = await fetchWithTimeout(
    joinApiUrl(baseUrl, path),
    {
      ...init,
      headers,
      credentials: withCredentials ? "include" : init.credentials,
    },
    signal,
  );
  recordResponseHeaders(res, telemetrySpanId);

  if (!res.ok) {
    const parsed = await parseError(res);
    throw new ApiError(
      getUserMessage(parsed.code, parsed.message),
      res.status,
      parsed.code,
      parsed.details,
    );
  }

  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

async function requestWithRetry<T>(
  path: string,
  init: RequestInit & {
    signal?: AbortSignal;
    telemetrySpanId?: string;
    withCredentials?: boolean;
  } = {},
): Promise<T> {
  try {
    return await request<T>(path, { ...init, authenticated: true });
  } catch (err) {
    if (err instanceof ApiError && err.status === 401) {
      try {
        await refreshAccessToken();
      } catch (refreshErr) {
        clearTokens();
        throw refreshErr;
      }
      try {
        return await request<T>(path, { ...init, authenticated: true });
      } catch (retryErr) {
        if (retryErr instanceof ApiError && retryErr.status === 401) {
          clearTokens();
        }
        throw retryErr;
      }
    }
    throw err;
  }
}

export async function exchangeFirebaseToken(
  idToken: string,
): Promise<FirebaseExchangeResponse> {
  const body: FirebaseExchangeRequest = {
    id_token: idToken,
    device_info: typeof navigator !== "undefined" ? navigator.userAgent : null,
  };
  const response = await request<FirebaseExchangeResponse>(
    API_ENDPOINTS.auth.firebaseExchange,
    {
      method: "POST",
      body: JSON.stringify(body),
      withCredentials: true,
    },
  );
  // Access token stays in memory; refresh is Set-Cookie HttpOnly on the API host.
  saveAccessToken(response.tokens.access_token, response.tokens.expires_in);
  clearLegacyRefreshToken();
  return response;
}

export async function refreshAccessToken(): Promise<TokenResponse> {
  const legacyRefresh = getLegacyRefreshToken();
  const body: RefreshTokenRequest | Record<string, never> = legacyRefresh
    ? { refresh_token: legacyRefresh }
    : {};

  const response = await request<TokenResponse>(API_ENDPOINTS.auth.refresh, {
    method: "POST",
    body: JSON.stringify(body),
    withCredentials: true,
  });
  saveAccessToken(response.access_token, response.expires_in);
  clearLegacyRefreshToken();
  return response;
}

export async function fetchMe(): Promise<UserResponse> {
  return requestWithRetry<UserResponse>(API_ENDPOINTS.me, { method: "GET" });
}

export async function getAppBootstrap(): Promise<BootstrapResponse> {
  return requestWithRetry<BootstrapResponse>(API_ENDPOINTS.app.bootstrap, {
    method: "GET",
  });
}

export async function patchAppPreferences(
  body: PreferenceUpdateRequest,
): Promise<PreferenceUpdateResponse> {
  return requestWithRetry<PreferenceUpdateResponse>(
    API_ENDPOINTS.app.preferences,
    { method: "PATCH", body: JSON.stringify(body) },
  );
}

export async function logout(): Promise<void> {
  try {
    const legacyRefresh = getLegacyRefreshToken();
    await request<{ message?: string }>(API_ENDPOINTS.auth.logout, {
      method: "POST",
      body: JSON.stringify(
        legacyRefresh ? { refresh_token: legacyRefresh } : {},
      ),
      withCredentials: true,
    });
  } finally {
    clearTokens();
  }
}

/** Sign out every device (revokes all refresh sessions). */
export async function logoutAll(): Promise<void> {
  try {
    await requestWithRetry<{ revoked: number }>(API_ENDPOINTS.auth.logoutAll, {
      method: "POST",
      withCredentials: true,
    });
  } finally {
    clearTokens();
  }
}

export async function requestAvatarUploadUrl(
  contentType: string,
  byteSize: number,
): Promise<AvatarUploadUrlResponse> {
  const body: AvatarUploadUrlRequest = {
    content_type: contentType,
    byte_size: byteSize,
  };
  return requestWithRetry<AvatarUploadUrlResponse>(
    "api/v1/me/avatar/upload-url",
    { method: "POST", body: JSON.stringify(body) },
  );
}

export async function putToSignedUrl(
  uploadUrl: string,
  data: Blob,
  contentType: string,
): Promise<void> {
  // Relative stub URLs (/local-uploads/...) must hit the API origin, not Next.js.
  const resolved = resolveMediaUrl(uploadUrl) ?? uploadUrl;

  const headers: Record<string, string> = {
    "Content-Type": contentType,
    "x-upsert": "true",
  };
  if (resolved.includes("ngrok")) {
    headers["ngrok-skip-browser-warning"] = "true";
  }

  const res = await fetchWithTimeout(resolved, {
    method: "PUT",
    headers,
    body: data,
  });
  if (!res.ok) {
    const detail = (await res.text().catch(() => "")).trim().slice(0, 180);
    const suffix = detail ? `: ${detail}` : "";
    throw new ApiError(`Upload failed (${res.status})${suffix}`, res.status);
  }
}

export async function confirmAvatarUpload(
  storagePath: string,
): Promise<UserResponse> {
  const body: AvatarConfirmRequest = { storage_path: storagePath };
  return requestWithRetry<UserResponse>("api/v1/me/avatar", {
    method: "PATCH",
    body: JSON.stringify(body),
  });
}

export async function updateProfile(displayName: string): Promise<UserResponse> {
  const body: UserProfileUpdateRequest = { display_name: displayName };
  return requestWithRetry<UserResponse>("api/v1/me", {
    method: "PATCH",
    body: JSON.stringify(body),
  });
}

export async function getPersonalCreateOptions(): Promise<PersonalCreateOptionsResponse> {
  return requestWithRetry<PersonalCreateOptionsResponse>(
    "api/v1/personal/create/options",
    { method: "GET" },
  );
}

export async function createPersonalMoment(
  body: PersonalMomentCreateRequest,
): Promise<PersonalMomentResponse> {
  return requestWithRetry<PersonalMomentResponse>("api/v1/personal/moments", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function patchPersonalMoment(
  momentId: string,
  body: PersonalMomentUpdateRequest,
): Promise<PersonalMomentResponse> {
  return requestWithRetry<PersonalMomentResponse>(
    `api/v1/personal/moments/${momentId}`,
    { method: "PATCH", body: JSON.stringify(body) },
  );
}

export type GroupMomentUpdateRequest = {
  moment_name?: string;
  status?: "ACTIVE" | "PAUSED" | "ARCHIVED";
};

export async function patchGroupMoment(
  momentId: string,
  body: GroupMomentUpdateRequest,
): Promise<Record<string, unknown>> {
  return requestWithRetry<Record<string, unknown>>(
    `api/v1/group/moments/${momentId}`,
    { method: "PATCH", body: JSON.stringify(body) },
  );
}

export async function completeGroupMoment(momentId: string): Promise<Record<string, unknown>> {
  return requestWithRetry<Record<string, unknown>>(
    `api/v1/group/moments/${momentId}/complete`,
    { method: "POST" },
  );
}

export async function archiveGroupMoment(momentId: string): Promise<Record<string, unknown>> {
  return requestWithRetry<Record<string, unknown>>(
    `api/v1/group/moments/${momentId}/archive`,
    { method: "POST" },
  );
}

export type BusinessMomentUpdateRequest = {
  moment_name?: string;
  status?: "ACTIVE" | "PAUSED" | "ARCHIVED";
};

export async function patchBusinessMoment(
  momentId: string,
  body: BusinessMomentUpdateRequest,
): Promise<Record<string, unknown>> {
  return requestWithRetry<Record<string, unknown>>(
    `api/v1/business/moments/${momentId}`,
    { method: "PATCH", body: JSON.stringify(body) },
  );
}

export async function completeBusinessMoment(momentId: string): Promise<Record<string, unknown>> {
  return requestWithRetry<Record<string, unknown>>(
    `api/v1/business/moments/${momentId}/complete`,
    { method: "POST" },
  );
}

export async function archiveBusinessMoment(momentId: string): Promise<Record<string, unknown>> {
  return requestWithRetry<Record<string, unknown>>(
    `api/v1/business/moments/${momentId}/archive`,
    { method: "POST" },
  );
}

export async function getBusinessSessionBootstrap(opts?: {
  workspaceId?: string | null;
}): Promise<import("@/lib/api/business").BusinessSessionBootstrapResponse> {
  const qs =
    opts?.workspaceId != null && opts.workspaceId !== ""
      ? `?workspace_id=${encodeURIComponent(opts.workspaceId)}`
      : "";
  return requestWithRetry(`api/v1/business/session/bootstrap${qs}`, { method: "GET" });
}

export async function getBusinessSession(opts?: {
  workspaceId?: string | null;
}): Promise<{
  selected_workspace?: import("@/lib/api/business").BusinessWorkspaceSummary | null;
  workspaces?: import("@/lib/api/business").BusinessWorkspaceSummary[];
  module_tiles?: import("@/lib/api/business").BusinessModuleTile[];
}> {
  const qs =
    opts?.workspaceId != null && opts.workspaceId !== ""
      ? `?workspace_id=${encodeURIComponent(opts.workspaceId)}`
      : "";
  return requestWithRetry(`api/v1/business/session${qs}`, { method: "GET" });
}

export async function getBusinessWorkspaceOverview(
  workspaceId: string,
): Promise<{
  workspace_id: string;
  dashboard?: import("@/lib/api/business").BusinessDashboardSummary;
  recent_moments?: import("@/lib/api/business").BusinessMomentResponse[];
}> {
  return requestWithRetry(
    `api/v1/business/workspaces/${encodeURIComponent(workspaceId)}/overview`,
    { method: "GET" },
  );
}

export async function getBusinessWorkspaceMoments(
  workspaceId: string,
): Promise<{
  workspace_id: string;
  moments_home?: import("@/lib/api/business").BusinessMomentsHomeResponse;
  moments?: import("@/lib/api/business").BusinessMomentResponse[];
  pulse?: unknown;
}> {
  return requestWithRetry(
    `api/v1/business/workspaces/${encodeURIComponent(workspaceId)}/moments`,
    { method: "GET" },
  );
}

export async function createBusinessWorkspace(body: {
  name: string;
  currency_code?: string;
  timezone?: string;
  industry?: string | null;
  logo_url?: string | null;
}): Promise<import("@/lib/api/business").BusinessWorkspaceSummary> {
  return requestWithRetry("api/v1/business/workspaces", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function updateBusinessWorkspace(
  workspaceId: string,
  body: {
    name?: string | null;
    logo_url?: string | null;
    industry?: string | null;
    currency_code?: string | null;
    timezone?: string | null;
    status?: string | null;
  },
): Promise<import("@/lib/api/business").BusinessWorkspaceSummary> {
  return requestWithRetry(`api/v1/business/workspaces/${workspaceId}`, {
    method: "PATCH",
    body: JSON.stringify(body),
  });
}

export async function selectBusinessWorkspace(
  workspaceId: string,
): Promise<import("@/lib/api/business").BusinessWorkspaceSummary> {
  return requestWithRetry("api/v1/business/workspaces/select", {
    method: "POST",
    body: JSON.stringify({ workspace_id: workspaceId }),
  });
}

export async function listBusinessWorkspaceMembers(
  workspaceId: string,
): Promise<{ members: Array<{ member_id: string; user_id: string; role: string; status: string }> }> {
  return requestWithRetry(`api/v1/business/workspaces/${workspaceId}/members`, {
    method: "GET",
  });
}

export async function inviteBusinessWorkspaceMember(
  workspaceId: string,
  body: { email: string; role?: string },
): Promise<Record<string, unknown>> {
  return requestWithRetry(`api/v1/business/workspaces/${workspaceId}/invites`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function acceptBusinessWorkspaceInvite(
  token: string,
): Promise<import("@/lib/api/business").BusinessWorkspaceSummary> {
  return requestWithRetry("api/v1/business/workspaces/invites/accept", {
    method: "POST",
    body: JSON.stringify({ token }),
  });
}

export async function getBusinessCreateOptions(): Promise<import("@/lib/api/business").BusinessCreateOptionsResponse> {
  return requestWithRetry("api/v1/business/create/options", { method: "GET" });
}

export async function createBusinessMoment(body: {
  moment_type_code: string;
  moment_name?: string | null;
  title?: string | null;
  template_id?: string | null;
  template_version?: string | number | null;
  workspace_id?: string | null;
}): Promise<import("@/lib/api/business").BusinessMomentCreateResponse> {
  return requestWithRetry("api/v1/business/moments", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function getBusinessSetupState(
  momentId: string,
): Promise<import("@/lib/api/business").BusinessSetupState> {
  return requestWithRetry(`api/v1/business/moments/${momentId}/setup`, { method: "GET" });
}

export async function saveBusinessSetupDraft(
  momentId: string,
  body: {
    answers: Record<string, unknown>;
    progress?: { current_step: number; completed_steps: number[] };
    template_id?: string;
    template_version?: string;
    setup_version?: string;
  },
): Promise<import("@/lib/api/business").BusinessSetupState> {
  return requestWithRetry(`api/v1/business/moments/${momentId}/setup/draft`, {
    method: "PUT",
    body: JSON.stringify(body),
  });
}

export async function previewBusinessSetup(
  momentId: string,
  body?: { answers?: Record<string, unknown> },
): Promise<import("@/lib/api/business").BusinessSetupPreview> {
  return requestWithRetry(`api/v1/business/moments/${momentId}/setup/preview`, {
    method: "POST",
    body: JSON.stringify(body ?? {}),
  });
}

export async function activateBusinessSetup(
  momentId: string,
): Promise<import("@/lib/api/business").BusinessActivateResponse> {
  return requestWithRetry(`api/v1/business/moments/${momentId}/setup/activate`, {
    method: "POST",
  });
}

export async function createBusinessSetupInviteDraft(
  momentId: string,
  body: { local_id: string; channel?: string },
): Promise<import("@/lib/api/business").BusinessSetupInviteDraft> {
  return requestWithRetry(`api/v1/business/moments/${momentId}/setup/invites/draft`, {
    method: "POST",
    body: JSON.stringify({
      local_id: body.local_id,
      channel: body.channel ?? "EMAIL",
    }),
  });
}

export async function getPersonalMomentSetup(
  momentId: string,
): Promise<PersonalSetupResponse> {
  return requestWithRetry<PersonalSetupResponse>(
    `api/v1/personal/moments/${momentId}/setup`,
    { method: "GET" },
  );
}

export async function savePersonalSetupDraft(
  momentId: string,
  answers: PersonalSetupAnswers,
): Promise<PersonalSetupResponse> {
  const body: PersonalSetupSubmitRequest = { answers };
  return requestWithRetry<PersonalSetupResponse>(
    `api/v1/personal/moments/${momentId}/setup/draft`,
    { method: "PUT", body: JSON.stringify(body) },
  );
}

export async function previewPersonalSetup(
  momentId: string,
  answers: PersonalSetupAnswers,
): Promise<PersonalSetupPreview> {
  const body: PersonalSetupSubmitRequest = { answers };
  return requestWithRetry<PersonalSetupPreview>(
    `api/v1/personal/moments/${momentId}/setup/preview`,
    { method: "POST", body: JSON.stringify(body) },
  );
}

export async function submitPersonalSetup(
  momentId: string,
  answers: PersonalSetupAnswers,
): Promise<PersonalMomentResponse> {
  const body: PersonalSetupSubmitRequest = { answers };
  return requestWithRetry<PersonalMomentResponse>(
    `api/v1/personal/moments/${momentId}/setup`,
    { method: "POST", body: JSON.stringify(body) },
  );
}

export async function getPersonalPulse(
  options?: { momentTypeCode?: string; forceRefresh?: boolean },
): Promise<PersonalPulseResponse> {
  const params = new URLSearchParams();
  if (options?.momentTypeCode) params.set("moment_type_code", options.momentTypeCode);
  if (options?.forceRefresh) params.set("force_refresh", "true");
  const qs = params.toString();
  const spanId = startSpan("pulse.refresh", { momentTypeCode: options?.momentTypeCode });
  try {
    return await requestWithRetry<PersonalPulseResponse>(
      `api/v1/personal/pulse${qs ? `?${qs}` : ""}`,
      { method: "GET", telemetrySpanId: spanId },
    );
  } finally {
    endSpan(spanId);
  }
}

export async function getPersonalMomentsHome(
  options?: { momentTypeCode?: string; forceRefresh?: boolean },
): Promise<PersonalMomentsHomeResponse> {
  const params = new URLSearchParams();
  if (options?.momentTypeCode) params.set("moment_type_code", options.momentTypeCode);
  if (options?.forceRefresh) params.set("force_refresh", "true");
  const qs = params.toString();
  return requestWithRetry<PersonalMomentsHomeResponse>(
    `api/v1/personal/moments/home${qs ? `?${qs}` : ""}`,
    { method: "GET" },
  );
}

export type PersonalSessionBootstrapResponse = {
  pulse: PersonalPulseResponse;
  moments_home: PersonalMomentsHomeResponse;
};

export type PersonalTypeHint = {
  moment_type_code: string;
  linked_moment_id?: string | null;
  linked_moment_status?: string | null;
  has_draft?: boolean;
  is_active?: boolean;
};

export type PersonalSessionResponse = {
  is_empty: boolean;
  active_moment_count: number;
  has_draft?: boolean;
  type_hints?: PersonalTypeHint[];
};

export type PersonalInventoryResponse = {
  pulse: PersonalPulseResponse;
  moments_home: PersonalMomentsHomeResponse;
};

export async function getPersonalSession(): Promise<PersonalSessionResponse> {
  return requestWithRetry<PersonalSessionResponse>(`api/v1/personal/session`, {
    method: "GET",
  });
}

export async function getPersonalInventory(
  options?: { momentTypeCode?: string },
): Promise<PersonalInventoryResponse> {
  const params = new URLSearchParams();
  if (options?.momentTypeCode) params.set("moment_type_code", options.momentTypeCode);
  const qs = params.toString();
  return requestWithRetry<PersonalInventoryResponse>(
    `api/v1/personal/inventory${qs ? `?${qs}` : ""}`,
    { method: "GET" },
  );
}

export async function getPersonalSessionBootstrap(
  options?: { momentTypeCode?: string; forceRefresh?: boolean },
): Promise<PersonalSessionBootstrapResponse> {
  const params = new URLSearchParams();
  if (options?.momentTypeCode) params.set("moment_type_code", options.momentTypeCode);
  if (options?.forceRefresh) params.set("force_refresh", "true");
  const qs = params.toString();
  return requestWithRetry<PersonalSessionBootstrapResponse>(
    `api/v1/personal/session/bootstrap${qs ? `?${qs}` : ""}`,
    { method: "GET" },
  );
}

export async function getPersonalMemory(
  options?: { momentTypeCode?: string; forceRefresh?: boolean },
): Promise<PersonalMemoryResponse> {
  const params = new URLSearchParams();
  if (options?.momentTypeCode) params.set("moment_type_code", options.momentTypeCode);
  if (options?.forceRefresh) params.set("force_refresh", "true");
  const qs = params.toString();
  return requestWithRetry<PersonalMemoryResponse>(
    `api/v1/personal/memory${qs ? `?${qs}` : ""}`,
    { method: "GET" },
  );
}

export async function getPersonalLife(
  options?: { forceRefresh?: boolean },
): Promise<PersonalLifeResponse> {
  const params = new URLSearchParams();
  if (options?.forceRefresh) params.set("force_refresh", "true");
  const qs = params.toString();
  return requestWithRetry<PersonalLifeResponse>(
    `api/v1/personal/life${qs ? `?${qs}` : ""}`,
    { method: "GET" },
  );
}

function templatePath(momentTypeCode: string, suffix: string): string {
  const code = encodeURIComponent(momentTypeCode);
  return `api/v1/personal/templates/${code}${suffix}`;
}

export async function getTemplateMoments(
  momentTypeCode: string,
): Promise<TemplateMomentsResponse> {
  const spanId = startSpan("template.moments.load", { moment_type_code: momentTypeCode });
  try {
    return await requestWithRetry<TemplateMomentsResponse>(
      templatePath(momentTypeCode, "/moments"),
      { method: "GET", telemetrySpanId: spanId },
    );
  } finally {
    endSpan(spanId);
  }
}

export async function getTemplatePulse(
  momentTypeCode: string,
): Promise<Record<string, unknown>> {
  const spanId = startSpan("template.pulse.load", {
    moment_type_code: momentTypeCode,
  });
  try {
    return await requestWithRetry<Record<string, unknown>>(
      templatePath(momentTypeCode, "/pulse"),
      { method: "GET", telemetrySpanId: spanId },
    );
  } finally {
    endSpan(spanId);
  }
}

export async function getTemplateLife(momentTypeCode: string): Promise<TemplateLifeResponse> {
  const spanId = startSpan("template.life.load", { moment_type_code: momentTypeCode });
  try {
    return await requestWithRetry<TemplateLifeResponse>(
      templatePath(momentTypeCode, "/life"),
      { method: "GET", telemetrySpanId: spanId },
    );
  } finally {
    endSpan(spanId);
  }
}

export async function getTemplateMemory(
  momentTypeCode: string,
): Promise<TemplateMemoryResponse> {
  const spanId = startSpan("template.memory.load", { moment_type_code: momentTypeCode });
  try {
    return await requestWithRetry<TemplateMemoryResponse>(
      templatePath(momentTypeCode, "/memory"),
      { method: "GET", telemetrySpanId: spanId },
    );
  } finally {
    endSpan(spanId);
  }
}

export async function updateTemplateMoment(
  momentTypeCode: string,
  momentId: string,
  body: PersonalMomentUpdateRequest,
): Promise<PersonalMomentResponse> {
  return requestWithRetry<PersonalMomentResponse>(
    templatePath(momentTypeCode, `/moments/${momentId}`),
    { method: "PATCH", body: JSON.stringify(body) },
  );
}

export async function archiveTemplateMoment(
  momentTypeCode: string,
  momentId: string,
): Promise<PersonalMomentResponse> {
  const spanId = startSpan("template.moment.archive", { moment_type_code: momentTypeCode });
  try {
    return await requestWithRetry<PersonalMomentResponse>(
      templatePath(momentTypeCode, `/moments/${momentId}/archive`),
      { method: "POST", telemetrySpanId: spanId },
    );
  } finally {
    endSpan(spanId);
  }
}

export async function completeTemplateMoment(
  momentTypeCode: string,
  momentId: string,
): Promise<PersonalMomentResponse> {
  const spanId = startSpan("template.moment.complete", { moment_type_code: momentTypeCode });
  try {
    return await requestWithRetry<PersonalMomentResponse>(
      templatePath(momentTypeCode, `/moments/${momentId}/complete`),
      { method: "POST", telemetrySpanId: spanId },
    );
  } finally {
    endSpan(spanId);
  }
}

export type PersonalQuickAddMomentOption = {
  moment_id: string;
  moment_name: string;
  moment_type_code: string;
};

export type PersonalQuickAddTab = {
  event_type: string;
  label: string;
  description: string;
  tab_code?: string | null;
  hero_title?: string | null;
  hero_subtitle?: string | null;
  cta_label?: string | null;
  guiding_question?: string | null;
  teaches_items?: string[];
  insight_title?: string | null;
  insight_body?: string | null;
  context_banner?: string | null;
};

export type PersonalQuickAddFieldOption = {
  value: string;
  label: string;
  icon_name?: string | null;
};

export type PersonalFutureBuildingQuickAddFieldGroup = {
  group_key: string;
  label: string;
  field_type: string;
  options?: PersonalQuickAddFieldOption[];
};

export type PersonalFutureBuildingQuickAddTabFields = {
  event_type: string;
  field_groups: PersonalFutureBuildingQuickAddFieldGroup[];
};

export type PersonalEmotionalSecurityQuickAddFieldGroup = PersonalFutureBuildingQuickAddFieldGroup;

export type PersonalEmotionalSecurityQuickAddTabFields = {
  event_type: string;
  field_groups: PersonalEmotionalSecurityQuickAddFieldGroup[];
};

export type PersonalQuickAddAccount = {
  account_id: string;
  account_name: string;
  account_type: string;
  account_type_label?: string;
  currency_code: string;
  current_balance: string;
  current_balance_minor?: number;
  is_primary: boolean;
  is_default?: boolean;
  is_archived?: boolean;
  transaction_count?: number;
  id?: string;
};

export type PersonalRuntimeSignalDimension = {
  key: string;
  label: string;
  description: string;
};

export type PersonalQuickAddMetadata = {
  expense_entry_types?: PersonalQuickAddFieldOption[];
  pressure_impact_chips?: string[];
  mood_feeling_options?: PersonalQuickAddFieldOption[];
  reflection_tags?: string[];
  recovery_types?: PersonalQuickAddFieldOption[];
  recovery_duration_options?: PersonalQuickAddFieldOption[];
  energy_impact_options?: string[];
  expense_category_names?: string[];
  attention_focus_areas?: string[];
  commitment_types?: PersonalQuickAddFieldOption[];
  commitment_status_options?: PersonalQuickAddFieldOption[];
  rhythm_actions?: PersonalQuickAddFieldOption[];
  runtime_modes?: string[];
  runtime_signal_dimensions?: PersonalRuntimeSignalDimension[];
  milestone_nature_options?: string[];
  impact_level_options?: string[];
  celebration_level_options?: string[];
  outcome_value_options?: string[];
  opportunity_source_options?: string[];
  opportunity_status_options?: string[];
  potential_level_options?: string[];
  confidence_level_options?: string[];
  pivot_change_options?: string[];
  pivot_reason_options?: string[];
  progress_type_options?: string[];
  time_invested_options?: string[] | PersonalQuickAddFieldOption[];
  effort_level_options?: string[];
  learning_type_options?: string[];
  relevance_level_options?: string[];
  spend_category_options?: string[];
  experience_type_options?: string[];
  experience_quality_options?: string[];
  energy_impact_options?: string[];
  people_context_options?: string[];
  location_context_options?: string[];
  value_received_options?: string[];
  wellbeing_area_options?: string[];
  wellbeing_state_options?: string[];
  contributor_options?: string[];
  discovery_type_options?: string[];
  curiosity_level_options?: string[];
  discovery_impact_options?: string[];
  creation_type_options?: string[];
  satisfaction_level_options?: string[];
  adjustment_area_options?: string[];
  priority_level_options?: string[];
  future_building_tabs?: PersonalFutureBuildingQuickAddTabFields[];
  emotional_security_tabs?: PersonalEmotionalSecurityQuickAddTabFields[];
  lifestyle_tabs?: PersonalFutureBuildingQuickAddTabFields[];
};

export type PersonalQuickAddOptionsResponse = {
  moments: PersonalQuickAddMomentOption[];
  tabs?: PersonalQuickAddTab[];
  accounts?: PersonalQuickAddAccount[];
  entries_today_count?: number;
  default_currency_code?: string;
  currencies?: Array<Record<string, unknown>>;
  expense_categories?: Array<Record<string, unknown>>;
  income_categories?: Array<Record<string, unknown>>;
  account_types?: Array<Record<string, unknown>>;
  recovery_activities?: Array<Record<string, unknown>>;
  mood_tags?: Array<Record<string, unknown>>;
  commitment_types?: Array<Record<string, unknown>>;
  metadata?: PersonalQuickAddMetadata | null;
};

export async function getPersonalQuickAddOptions(
  momentId?: string,
): Promise<PersonalQuickAddOptionsResponse> {
  const params = new URLSearchParams();
  if (momentId) params.set("moment_id", momentId);
  const qs = params.toString();
  return requestWithRetry<PersonalQuickAddOptionsResponse>(
    `api/v1/personal/live/quick-add/options${qs ? `?${qs}` : ""}`,
    { method: "GET" },
  );
}

export async function createPersonalQuickAdd(
  body: Record<string, unknown>,
  options?: { clientRequestId?: string },
): Promise<unknown> {
  const clientRequestId = options?.clientRequestId ?? createClientRequestId();
  const spanId = startSpan("quick_add.save", { clientRequestId });
  try {
    return await requestWithRetry("api/v1/personal/live/quick-add", {
      method: "POST",
      body: JSON.stringify({ ...body, client_request_id: clientRequestId }),
      telemetrySpanId: spanId,
    });
  } finally {
    endSpan(spanId, { metadata: { clientRequestId } });
  }
}

export async function getLifeOpsActivity(momentId: string): Promise<import("@/lib/api/personal").PersonalLifeOpsActivityResponse> {
  const params = new URLSearchParams({ moment_id: momentId });
  return requestWithRetry(
    `api/v1/personal/life-operations/activity?${params.toString()}`,
    { method: "GET" },
  );
}

export async function getTemplateActivity(
  momentType: string,
  momentId: string,
): Promise<import("@/lib/personal/template/activity/types").TemplateActivityListResponse> {
  const params = new URLSearchParams({ moment_id: momentId });
  return requestWithRetry(
    `api/v1/personal/templates/${momentType}/activity?${params.toString()}`,
    { method: "GET" },
  );
}

export type UnifiedPersonalActivityParams = {
  range?: string;
  domain?: string;
  kind?: string;
  q?: string;
  cursor?: string;
  limit?: number;
};

export async function getUnifiedPersonalActivity(
  params: UnifiedPersonalActivityParams = {},
): Promise<import("@/lib/personal/template/activity/types").UnifiedPersonalActivityResponse> {
  const qs = new URLSearchParams();
  if (params.range) qs.set("range", params.range);
  if (params.domain) qs.set("domain", params.domain);
  if (params.kind) qs.set("kind", params.kind);
  if (params.q) qs.set("q", params.q);
  if (params.cursor) qs.set("cursor", params.cursor);
  if (params.limit) qs.set("limit", String(params.limit));
  const suffix = qs.toString() ? `?${qs.toString()}` : "";
  return requestWithRetry(`api/v1/personal/activity${suffix}`, { method: "GET" });
}

export async function getTemplateActivityDetail(
  momentType: string,
  eventId: string,
): Promise<import("@/lib/personal/template/activity/types").TemplateActivityDetail> {
  return requestWithRetry(
    `api/v1/personal/templates/${momentType}/activity/${eventId}`,
    { method: "GET" },
  );
}

export async function patchTemplateActivity(
  momentType: string,
  eventId: string,
  body: Record<string, unknown>,
): Promise<import("@/lib/personal/template/activity/types").TemplateActivityDetail> {
  return requestWithRetry(
    `api/v1/personal/templates/${momentType}/activity/${eventId}`,
    {
      method: "PATCH",
      body: JSON.stringify(body),
    },
  );
}

export async function deleteTemplateActivity(
  momentType: string,
  eventId: string,
): Promise<void> {
  await requestWithRetry(
    `api/v1/personal/templates/${momentType}/activity/${eventId}`,
    { method: "DELETE" },
  );
}

export async function deletePersonalQuickAddEvent(eventId: string): Promise<void> {
  await requestWithRetry(`api/v1/personal/live/quick-add/${eventId}`, { method: "DELETE" });
}

export async function getPersonalQuickAddEvent(
  eventId: string,
): Promise<import("@/lib/api/personal").PersonalQuickAddDetail> {
  return requestWithRetry(`api/v1/personal/live/quick-add/${eventId}`, { method: "GET" });
}

export async function patchPersonalQuickAddEvent(
  eventId: string,
  body: Record<string, unknown>,
): Promise<unknown> {
  return requestWithRetry(`api/v1/personal/live/quick-add/${eventId}`, {
    method: "PATCH",
    body: JSON.stringify(body),
  });
}

export type PersonalAccountCreateRequest = {
  account_name: string;
  account_type: string;
  currency_code?: string;
  opening_balance?: string | null;
  opening_balance_minor?: number | null;
  is_primary?: boolean;
};

export type PersonalAccountPatchRequest = {
  account_name?: string;
  account_type?: string;
  currency_code?: string;
  current_balance_minor?: number;
  is_default?: boolean;
};

export async function getPersonalAccount(accountId: string): Promise<PersonalQuickAddAccount> {
  return requestWithRetry<PersonalQuickAddAccount>(`api/v1/personal/accounts/${accountId}`, {
    method: "GET",
  });
}

export async function patchPersonalAccount(
  accountId: string,
  body: PersonalAccountPatchRequest,
): Promise<PersonalQuickAddAccount> {
  return requestWithRetry<PersonalQuickAddAccount>(`api/v1/personal/accounts/${accountId}`, {
    method: "PATCH",
    body: JSON.stringify(body),
  });
}

export async function archivePersonalAccount(accountId: string): Promise<PersonalQuickAddAccount> {
  return requestWithRetry<PersonalQuickAddAccount>(
    `api/v1/personal/accounts/${accountId}/archive`,
    { method: "POST" },
  );
}

export async function deletePersonalAccount(accountId: string): Promise<void> {
  await requestWithRetry(`api/v1/personal/accounts/${accountId}`, { method: "DELETE" });
}

export async function listPersonalAccounts(
  includeArchived = false,
): Promise<PersonalQuickAddAccount[]> {
  const qs = includeArchived ? "?include_archived=true" : "";
  return requestWithRetry<PersonalQuickAddAccount[]>(`api/v1/personal/accounts${qs}`, {
    method: "GET",
  });
}

export async function createPersonalAccount(
  body: PersonalAccountCreateRequest,
): Promise<PersonalQuickAddAccount> {
  return requestWithRetry<PersonalQuickAddAccount>("api/v1/personal/accounts", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export type PersonalMasterExpenseOptionsResponse = {
  accounts: PersonalQuickAddAccount[];
  categories: Array<{
    category_id: string;
    category_name: string;
    category_group: string;
    children?: Array<{ category_id: string; category_name: string }>;
  }>;
  feelings: PersonalQuickAddFieldOption[];
  scale_levels: PersonalQuickAddFieldOption[];
  shared_with: PersonalQuickAddFieldOption[];
  relationship_impacts: PersonalQuickAddFieldOption[];
  context_reasons: PersonalQuickAddFieldOption[];
  life_operations_moment_id: string | null;
  lifestyle_moment_id: string | null;
  emotional_security_moment_id: string | null;
};

export type PersonalMasterExpenseRequest = {
  client_request_id?: string;
  title?: string;
  amount_minor?: number;
  currency_code?: string;
  account_id?: string;
  category_code?: string;
  subcategory_code?: string | null;
  occurred_at?: string | null;
  expense: {
    title: string;
    amount: string;
    account_id: string;
    category_code?: string | null;
    subcategory_code?: string | null;
    category_name?: string | null;
    category_id?: string | null;
    pressure_impact?: string | null;
    description?: string | null;
    transaction_date?: string | null;
  };
  experience?: {
    feeling?: string | null;
    meaningfulness?: string | null;
    memorability?: string | null;
  } | null;
  shared_experience?: {
    enabled?: boolean;
    shared_with?: string[];
    relationship_impact?: string | null;
  } | null;
  shared?: {
    is_shared?: boolean;
    shared_with?: string[];
    relationship_impact?: string[];
  } | null;
  context?: { reason?: string | null } | null;
  notes?: string | null;
};

export type PersonalMasterExpenseResponse = {
  id?: string;
  master_expense_id?: string;
  created_events?: {
    life_operations?: string | null;
    lifestyle?: string | null;
    relationships?: string | null;
  };
  impact_preview?: Record<string, string>;
  idempotent_replay?: boolean;
  master_expense_group_id: string;
  transaction_id: string;
  account_id: string;
  amount_minor: number;
  events: Array<{
    quick_add_event_id: string;
    moment_id: string;
    moment_type_code: string;
    event_type: string;
  }>;
};

export async function getMasterExpenseOptions(): Promise<PersonalMasterExpenseOptionsResponse> {
  return requestWithRetry<PersonalMasterExpenseOptionsResponse>(
    "api/v1/personal/master-expense/options",
    { method: "GET" },
  );
}

export async function createMasterExpense(
  body: PersonalMasterExpenseRequest,
): Promise<PersonalMasterExpenseResponse> {
  return requestWithRetry<PersonalMasterExpenseResponse>("api/v1/personal/master-expense", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export { requestWithRetry, recordResponseHeaders };
