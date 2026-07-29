import { requestWithRetry } from "@/lib/api/client";

export type TripQuickAddModule = {
  module_code: string;
  label: string;
  icon: string;
  description?: string;
};

export type TripQuickAddCategory = {
  id: string;
  label: string;
  modules: TripQuickAddModule[];
};

export type TripQuickAddConfigResponse = {
  moment_id: string;
  moment_type: string;
  moment_profile: string;
  categories: TripQuickAddCategory[];
};

export type TripQuickAddContext = Record<string, unknown>;

type CachedContext = {
  data: TripQuickAddContext;
  at: number;
};

const CONTEXT_CACHE_TTL_MS = 2 * 60 * 1000;
const contextCache = new Map<string, CachedContext>();

const CONTEXT_SLUG: Record<string, string> = {
  PARTICIPANT: "participant",
  PLANNING_ITEM: "planning-item",
  BOOKING: "booking",
  EXPENSE: "expense",
  BUDGET: "budget",
  MEMORY: "memory",
  POLL: "poll",
  ATTENDANCE: "attendance",
  VENDOR: "vendor",
  UPDATE: "update",
};

export async function fetchTripQuickAddConfig(momentId: string): Promise<TripQuickAddConfigResponse> {
  return requestWithRetry<TripQuickAddConfigResponse>(`/api/v1/group/quickadd/${momentId}`);
}

export async function fetchTripQuickAddContext(
  momentId: string,
  actionId: string,
): Promise<TripQuickAddContext> {
  const cacheKey = `${momentId}:${actionId}`;
  const cached = contextCache.get(cacheKey);
  if (cached && Date.now() - cached.at < CONTEXT_CACHE_TTL_MS) {
    return cached.data;
  }

  let result: TripQuickAddContext;
  if (actionId === "CONTRIBUTION") {
    result = await requestWithRetry<TripQuickAddContext>(
      `/api/v1/group/trips/${momentId}/contributions/context?pool=stay`,
    );
  } else {
    const slug = CONTEXT_SLUG[actionId];
    if (!slug) throw new Error(`Unknown quick-add action: ${actionId}`);
    result = await requestWithRetry<TripQuickAddContext>(
      `/api/v1/group/trips/${momentId}/quick-add/${slug}/context`,
    );
  }
  contextCache.set(cacheKey, { data: result, at: Date.now() });
  return result;
}

export async function prefetchTripQuickAddContexts(
  momentId: string,
  actionIds: string[],
): Promise<void> {
  const uniqueIds = Array.from(new Set(actionIds));
  await Promise.all(
    uniqueIds.map(async (actionId) => {
      try {
        await fetchTripQuickAddContext(momentId, actionId);
      } catch {
        // Best-effort warmup only.
      }
    }),
  );
}

export async function submitTripQuickAdd(
  momentId: string,
  actionId: string,
  body: Record<string, unknown>,
): Promise<unknown> {
  switch (actionId) {
    case "PARTICIPANT":
      return requestWithRetry(`/api/v1/group/trips/${momentId}/guests`, {
        method: "POST",
        body: JSON.stringify(body),
      });
    case "PLANNING_ITEM":
      return requestWithRetry(`/api/v1/group/trips/${momentId}/plans`, {
        method: "POST",
        body: JSON.stringify(body),
      });
    case "BOOKING":
      return requestWithRetry(`/api/v1/group/trips/${momentId}/quick-add/booking`, {
        method: "POST",
        body: JSON.stringify(body),
      });
    case "EXPENSE":
      return requestWithRetry(`/api/v1/group/trips/${momentId}/expenses`, {
        method: "POST",
        body: JSON.stringify(body),
      });
    case "CONTRIBUTION":
      return requestWithRetry(`/api/v1/group/trips/${momentId}/contributions`, {
        method: "POST",
        body: JSON.stringify(body),
      });
    case "BUDGET":
      return requestWithRetry(`/api/v1/group/trips/${momentId}/quick-add/budget/plans`, {
        method: "POST",
        body: JSON.stringify(body),
      });
    case "VENDOR":
      return requestWithRetry(`/api/v1/group/trips/${momentId}/quick-add/vendor`, {
        method: "POST",
        body: JSON.stringify(body),
      });
    case "ATTENDANCE":
      return requestWithRetry(`/api/v1/group/trips/${momentId}/quick-add/attendance`, {
        method: "POST",
        body: JSON.stringify(body),
      });
    case "UPDATE":
      return requestWithRetry(`/api/v1/group/trips/${momentId}/quick-add/update`, {
        method: "POST",
        body: JSON.stringify(body),
      });
    case "MEMORY":
      return requestWithRetry(`/api/v1/group/trips/${momentId}/memories`, {
        method: "POST",
        body: JSON.stringify(body),
      });
    case "POLL":
      return requestWithRetry(`/api/v1/group/trips/${momentId}/quick-add/poll`, {
        method: "POST",
        body: JSON.stringify(body),
      });
    default:
      throw new Error(`Unsupported quick-add action: ${actionId}`);
  }
}

export type TripAttachmentUploadUrlRequest = {
  content_type: string;
  byte_size: number;
  purpose: string;
};

export type TripAttachmentUploadUrlResponse = {
  upload_url: string;
  storage_path: string;
  token?: string | null;
};

export type TripAttachmentConfirmRequest = {
  storage_path: string;
  purpose: string;
};

export type TripAttachmentConfirmResponse = {
  storage_path: string;
};

export async function createTripAttachmentUploadUrl(
  momentId: string,
  body: TripAttachmentUploadUrlRequest,
): Promise<TripAttachmentUploadUrlResponse> {
  return requestWithRetry<TripAttachmentUploadUrlResponse>(
    `/api/v1/group/trips/${momentId}/attachments/upload-url`,
    { method: "POST", body: JSON.stringify(body) },
  );
}

export async function confirmTripAttachment(
  momentId: string,
  body: TripAttachmentConfirmRequest,
): Promise<TripAttachmentConfirmResponse> {
  return requestWithRetry<TripAttachmentConfirmResponse>(
    `/api/v1/group/trips/${momentId}/attachments/confirm`,
    { method: "POST", body: JSON.stringify(body) },
  );
}
