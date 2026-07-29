import {
  clearTokens,
  getAccessToken,
  getRefreshToken,
  saveTokens,
} from "@/lib/auth/tokens";
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
} from "@/lib/api/personal";

const baseUrl = (
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8002"
).replace(/\/$/, "");

const REQUEST_TIMEOUT_MS = 15_000;

class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function parseError(res: Response): Promise<string> {
  try {
    const body = (await res.json()) as { detail?: string | { msg?: string }[] };
    if (typeof body.detail === "string") return body.detail;
    if (Array.isArray(body.detail) && body.detail[0]?.msg) {
      return body.detail[0].msg;
    }
  } catch {
    // ignore
  }
  return `Request failed (${res.status})`;
}

async function fetchWithTimeout(
  url: string,
  init: RequestInit,
): Promise<Response> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
  try {
    return await fetch(url, { ...init, signal: controller.signal });
  } catch (err) {
    if (err instanceof Error && err.name === "AbortError") {
      throw new ApiError("Request timed out", 408);
    }
    throw err;
  } finally {
    clearTimeout(timeoutId);
  }
}

async function request<T>(
  path: string,
  options: RequestInit & { authenticated?: boolean } = {},
): Promise<T> {
  const { authenticated = false, ...init } = options;
  const headers = new Headers(init.headers);
  headers.set("Content-Type", "application/json");

  if (authenticated) {
    const token = getAccessToken();
    if (!token) throw new ApiError("Not signed in", 401);
    headers.set("Authorization", `Bearer ${token}`);
  }

  const res = await fetchWithTimeout(`${baseUrl}/${path}`, { ...init, headers });

  if (!res.ok) {
    throw new ApiError(await parseError(res), res.status);
  }

  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

async function requestWithRetry<T>(
  path: string,
  init: RequestInit = {},
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
    "api/v1/auth/firebase/exchange",
    { method: "POST", body: JSON.stringify(body) },
  );
  saveTokens(
    response.tokens.access_token,
    response.tokens.refresh_token,
    response.tokens.expires_in,
  );
  return response;
}

export async function refreshAccessToken(): Promise<TokenResponse> {
  const refreshToken = getRefreshToken();
  if (!refreshToken) throw new ApiError("No refresh token", 401);

  const body: RefreshTokenRequest = { refresh_token: refreshToken };
  const response = await request<TokenResponse>("api/v1/auth/refresh", {
    method: "POST",
    body: JSON.stringify(body),
  });
  saveTokens(
    response.access_token,
    response.refresh_token,
    response.expires_in,
  );
  return response;
}

export async function fetchMe(): Promise<UserResponse> {
  return requestWithRetry<UserResponse>("api/v1/me", { method: "GET" });
}

export async function logout(): Promise<void> {
  try {
    await requestWithRetry<{ message: string }>("api/v1/auth/logout", {
      method: "POST",
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
  const res = await fetchWithTimeout(uploadUrl, {
    method: "PUT",
    headers: {
      "Content-Type": contentType,
      "x-upsert": "true",
    },
    body: data,
  });
  if (!res.ok) {
    throw new ApiError(`Upload failed (${res.status})`, res.status);
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
  return requestWithRetry<PersonalPulseResponse>(
    `api/v1/personal/pulse${qs ? `?${qs}` : ""}`,
    { method: "GET" },
  );
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

export type PersonalQuickAddMetadata = {
  future_building_tabs?: PersonalFutureBuildingQuickAddTabFields[];
  lifestyle_tabs?: PersonalFutureBuildingQuickAddTabFields[];
};

export type PersonalQuickAddOptionsResponse = {
  moments: PersonalQuickAddMomentOption[];
  tabs?: PersonalQuickAddTab[];
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

export async function createPersonalQuickAdd(body: Record<string, unknown>): Promise<unknown> {
  return requestWithRetry("api/v1/personal/live/quick-add", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export { ApiError };
