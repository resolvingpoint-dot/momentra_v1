import { requestWithRetry } from "@/lib/api/client";
import {
  parseBusinessActivityItem,
  parseBusinessActivityListResponse,
  parseBusinessLifeResponse,
  parseBusinessMemoryResponse,
  parseTeamOpsMomentsResponse,
  parseTeamOpsPulseResponse,
} from "@/lib/business/teamOpsApiMappers";
import {
  parseRunwayMomentsResponse,
  parseRunwayPulseResponse,
} from "@/lib/business/runwayApiMappers";
import {
  parseOpsMomentsResponse,
  parseOpsPulseResponse,
} from "@/lib/business/opsApiMappers";
import type {
  BusinessActivityListItem,
  BusinessLifeResponse,
  BusinessMemoryResponse,
  OpsMomentsResponse,
  OpsPulseResponse,
  RunwayMomentsResponse,
  RunwayPulseResponse,
  TeamOpsMomentsResponse,
  TeamOpsPulseResponse,
} from "@/lib/api/businessActive";
import {
  activityFilterKey,
  buildActivityQuery,
  DEFAULT_ACTIVITY_PAGE_SIZE,
  type BusinessActivityFilters,
  type BusinessActivityPage,
} from "@/lib/business/activityFilters";
import {
  deleteAction,
  patchAction,
  type BusinessActivityPayload,
  type BusinessActivityResponse,
} from "@/repositories/BusinessActionRepository";
import { BusinessRepository } from "@/repositories/BusinessRepository";

function withForce(url: string, forceRefresh?: boolean): string {
  if (!forceRefresh) return url;
  const sep = url.includes("?") ? "&" : "?";
  return `${url}${sep}force_refresh=true`;
}

/**
 * Prefer API is_editable / is_deletable / supported_actions.
 * Registry fallback only when API omits flags (legacy).
 */
export function normalizeActivity(item: BusinessActivityListItem): BusinessActivityListItem {
  if (item._flags_from_api) {
    const supported =
      item.supported_actions?.length
        ? item.supported_actions
        : [
            ...(item.is_editable ? (["edit"] as const) : []),
            ...(item.is_deletable ? (["delete"] as const) : []),
          ];
    return {
      ...item,
      is_editable: Boolean(item.is_editable),
      is_deletable: Boolean(item.is_deletable),
      supported_actions: supported,
    };
  }
  // Legacy wire without flags — keep false (do not guess). Server owns auth.
  return {
    ...item,
    is_editable: false,
    is_deletable: false,
    supported_actions: item.supported_actions ?? [],
  };
}

export type ActivityListResult = {
  items: BusinessActivityListItem[];
  total: number;
  page: number;
  pageSize: number;
  filterKey: string;
};

export async function getPulse(
  momentId: string,
  forceRefresh = false,
): Promise<TeamOpsPulseResponse> {
  const raw = await requestWithRetry<unknown>(
    withForce(`/api/v1/business/active/${momentId}/pulse`, forceRefresh),
    { method: "GET" },
  );
  return parseTeamOpsPulseResponse(raw);
}

export async function getMoments(
  momentId: string,
  forceRefresh = false,
): Promise<TeamOpsMomentsResponse> {
  const raw = await requestWithRetry<unknown>(
    withForce(`/api/v1/business/active/${momentId}/moments`, forceRefresh),
    { method: "GET" },
  );
  return parseTeamOpsMomentsResponse(raw);
}

export async function getRunwayPulse(
  momentId: string,
  forceRefresh = false,
): Promise<RunwayPulseResponse> {
  const raw = await requestWithRetry<unknown>(
    withForce(`/api/v1/business/active/${momentId}/pulse`, forceRefresh),
    { method: "GET" },
  );
  return parseRunwayPulseResponse(raw);
}

export async function getRunwayMoments(
  momentId: string,
  forceRefresh = false,
): Promise<RunwayMomentsResponse> {
  const raw = await requestWithRetry<unknown>(
    withForce(`/api/v1/business/active/${momentId}/moments`, forceRefresh),
    { method: "GET" },
  );
  return parseRunwayMomentsResponse(raw);
}

export async function getOpsPulse(
  momentId: string,
  forceRefresh = false,
): Promise<OpsPulseResponse> {
  const raw = await requestWithRetry<unknown>(
    withForce(`/api/v1/business/active/${momentId}/pulse`, forceRefresh),
    { method: "GET" },
  );
  return parseOpsPulseResponse(raw);
}

export async function getOpsMoments(
  momentId: string,
  forceRefresh = false,
): Promise<OpsMomentsResponse> {
  const raw = await requestWithRetry<unknown>(
    withForce(`/api/v1/business/active/${momentId}/moments`, forceRefresh),
    { method: "GET" },
  );
  return parseOpsMomentsResponse(raw);
}

/** Server-filtered list — repository only forwards query params. */
export async function listActivity(
  momentId: string,
  filters?: BusinessActivityFilters | null,
  page?: BusinessActivityPage | null,
  forceRefresh = false,
): Promise<ActivityListResult> {
  const qs = buildActivityQuery(filters, page);
  const raw = await requestWithRetry<unknown>(
    withForce(`/api/v1/business/active/${momentId}/activity${qs}`, forceRefresh),
    { method: "GET" },
  );
  const parsed = parseBusinessActivityListResponse(raw);
  const pageNum = Math.max(1, page?.page ?? parsed.page ?? 1);
  const pageSize = page?.pageSize ?? parsed.page_size ?? DEFAULT_ACTIVITY_PAGE_SIZE;
  return {
    items: parsed.items.map(normalizeActivity),
    total: parsed.total,
    page: pageNum,
    pageSize,
    filterKey: activityFilterKey(filters, { page: pageNum, pageSize }),
  };
}

export async function getActivity(
  momentId: string,
  eventId: string,
  forceRefresh = false,
): Promise<BusinessActivityListItem> {
  const raw = await requestWithRetry<unknown>(
    withForce(`/api/v1/business/active/${momentId}/activity/${eventId}`, forceRefresh),
    { method: "GET" },
  );
  return normalizeActivity(parseBusinessActivityItem(raw));
}

export async function getLife(forceRefresh = false): Promise<BusinessLifeResponse> {
  const raw = await requestWithRetry<unknown>(
    withForce(`/api/v1/business/life`, forceRefresh),
    { method: "GET" },
  );
  return parseBusinessLifeResponse(raw);
}

export async function getMemory(forceRefresh = false): Promise<BusinessMemoryResponse> {
  const raw = await requestWithRetry<unknown>(
    withForce(`/api/v1/business/memory`, forceRefresh),
    { method: "GET" },
  );
  return parseBusinessMemoryResponse(raw);
}

export async function patchActivity(
  momentId: string,
  eventId: string,
  body: Partial<BusinessActivityPayload>,
): Promise<BusinessActivityResponse> {
  return patchAction(momentId, eventId, body);
}

export async function deleteActivity(momentId: string, eventId: string): Promise<void> {
  return deleteAction(momentId, eventId);
}

export async function archiveMoment(momentId: string) {
  return BusinessRepository.archiveMoment(momentId);
}

export async function completeMoment(momentId: string) {
  return BusinessRepository.completeMoment(momentId);
}

export const BusinessActiveRepository = {
  getPulse,
  getMoments,
  getRunwayPulse,
  getRunwayMoments,
  getOpsPulse,
  getOpsMoments,
  listActivity,
  getActivity,
  getLife,
  getMemory,
  patchActivity,
  deleteActivity,
  archiveMoment,
  completeMoment,
};
