/**
 * Business optimistic mutation coordinator — patch Pulse/Moments/Activity caches
 * from mutation response projection_hint; silent SWR reconcile; rollback on failure.
 */
import type { TeamOpsEventItem, TeamOpsPulseResponse } from "@/lib/api/businessActive";
import {
  seedBusinessMomentsCache,
  seedBusinessPulseCache,
  seedOpsMomentsCache,
  seedOpsPulseCache,
  seedRunwayMomentsCache,
  seedRunwayPulseCache,
  peekBusinessPulseCache,
  peekBusinessMomentsCache,
} from "@/hooks/useBusinessActiveTabs";

export type BusinessProjectionHint = {
  op?: "create" | "patch" | "delete";
  activity_event?: Record<string, unknown> | null;
  counters?: Record<string, number>;
  pulse?: { recent_activity_prepend?: Record<string, unknown> | null };
  moments?: { timeline_prepend?: Record<string, unknown> | null };
};

export type BusinessMutationResponse = {
  activity: Record<string, unknown>;
  projection_hint?: BusinessProjectionHint;
};

type Snapshot = {
  clientRequestId: string;
  momentId: string;
  momentTypeCode: string;
  userId?: string | null;
  previousPulse: unknown | null;
  previousMoments: unknown | null;
};

const pending = new Map<string, Snapshot>();

function eventFromActivity(activity: Record<string, unknown>): TeamOpsEventItem {
  return {
    event_id: String(activity.event_id ?? ""),
    action_type: String(activity.action_type ?? ""),
    title: String(activity.title ?? ""),
    occurred_at: String(activity.occurred_at ?? new Date().toISOString()),
    source_moment_id: String(activity.business_moment_id ?? ""),
  };
}

function prependRecent(
  pulse: TeamOpsPulseResponse,
  item: TeamOpsEventItem,
): TeamOpsPulseResponse {
  const section = pulse.recent_activity;
  if (!section || typeof section !== "object") return pulse;
  const data = (section as { data?: { items?: TeamOpsEventItem[] } }).data;
  const items = data?.items ?? [];
  const filtered = items.filter((e) => e.event_id !== item.event_id);
  return {
    ...pulse,
    recent_activity: {
      ...section,
      data: { ...data, items: [item, ...filtered].slice(0, 20) },
    },
  } as TeamOpsPulseResponse;
}

function bumpCounters(
  pulse: Record<string, unknown>,
  counters: Record<string, number> | undefined,
): Record<string, unknown> {
  if (!counters) return pulse;
  // Best-effort: if pulse has a numeric field matching known keys, bump it.
  // Template shapes vary; silent no-op when field absent.
  const next = { ...pulse };
  const map: Record<string, string[]> = {
    open_issues_delta: ["open_issues", "issues_open"],
    pending_approvals_delta: ["pending_approvals", "approvals_pending"],
    escalation_delta: ["escalation_count", "escalations"],
    recognition_delta: ["recognition_count", "recognitions"],
  };
  for (const [deltaKey, fields] of Object.entries(map)) {
    const delta = counters[deltaKey];
    if (typeof delta !== "number" || delta === 0) continue;
    for (const field of fields) {
      const cur = next[field];
      if (typeof cur === "number") next[field] = Math.max(0, cur + delta);
    }
  }
  return next;
}

export function normalizeMutationResponse(
  raw: unknown,
): BusinessMutationResponse | null {
  if (!raw || typeof raw !== "object") return null;
  const obj = raw as Record<string, unknown>;
  if (obj.activity && typeof obj.activity === "object") {
    return {
      activity: obj.activity as Record<string, unknown>,
      projection_hint: obj.projection_hint as BusinessProjectionHint | undefined,
    };
  }
  // Legacy flat ActivityDTO
  if (obj.event_id) {
    return { activity: obj, projection_hint: undefined };
  }
  return null;
}

/**
 * Apply server mutation result to client caches immediately (no clearing).
 * Snapshot for rollback keyed by clientRequestId.
 */
export function applyBusinessMutationSuccess(options: {
  momentId: string;
  momentTypeCode: string;
  userId?: string | null;
  response: unknown;
}): TeamOpsEventItem | null {
  const normalized = normalizeMutationResponse(options.response);
  if (!normalized) return null;

  const { activity, projection_hint } = normalized;
  const clientRequestId =
    String(activity.client_request_id ?? "") ||
    String(activity.event_id ?? `local-${Date.now()}`);
  const code = (options.momentTypeCode || "TEAM_OPERATIONS").toUpperCase();
  const item = eventFromActivity(activity);
  const op = projection_hint?.op ?? "create";

  const previousPulse = peekBusinessPulseCache(
    options.momentId,
    code,
    options.userId,
  );
  const previousMoments = peekBusinessMomentsCache(
    options.momentId,
    code,
    options.userId,
  );

  pending.set(clientRequestId, {
    clientRequestId,
    momentId: options.momentId,
    momentTypeCode: code,
    userId: options.userId,
    previousPulse,
    previousMoments,
  });

  if (op !== "delete" && previousPulse) {
    let patched = prependRecent(
      previousPulse as TeamOpsPulseResponse,
      item,
    ) as unknown as Record<string, unknown>;
    patched = bumpCounters(patched, projection_hint?.counters);
    seedPulse(code, options.momentId, patched, options.userId);
  }

  if (op !== "delete" && previousMoments && typeof previousMoments === "object") {
    // Moments shapes vary; prepend into common timeline arrays when present.
    const m = { ...(previousMoments as Record<string, unknown>) };
    for (const key of ["timeline", "recent_activity", "moments"]) {
      const section = m[key];
      if (!section || typeof section !== "object") continue;
      const s = section as { data?: { items?: TeamOpsEventItem[] }; items?: TeamOpsEventItem[] };
      if (Array.isArray(s.items)) {
        m[key] = {
          ...s,
          items: [item, ...s.items.filter((e) => e.event_id !== item.event_id)].slice(0, 30),
        };
        break;
      }
      if (s.data && Array.isArray(s.data.items)) {
        m[key] = {
          ...s,
          data: {
            ...s.data,
            items: [
              item,
              ...s.data.items.filter((e) => e.event_id !== item.event_id),
            ].slice(0, 30),
          },
        };
        break;
      }
    }
    seedMoments(code, options.momentId, m, options.userId);
  }

  return item;
}

export function rollbackBusinessMutation(clientRequestId: string): void {
  const snap = pending.get(clientRequestId);
  if (!snap) return;
  pending.delete(clientRequestId);
  const code = snap.momentTypeCode;
  if (snap.previousPulse) {
    seedPulse(code, snap.momentId, snap.previousPulse as Record<string, unknown>, snap.userId);
  }
  if (snap.previousMoments) {
    seedMoments(
      code,
      snap.momentId,
      snap.previousMoments as Record<string, unknown>,
      snap.userId,
    );
  }
}

export function clearBusinessMutation(clientRequestId: string): void {
  pending.delete(clientRequestId);
}

function seedPulse(
  code: string,
  momentId: string,
  data: Record<string, unknown>,
  userId?: string | null,
) {
  if (code === "BUSINESS_RUNWAY") {
    seedRunwayPulseCache(momentId, data as never, userId);
  } else if (code === "BUSINESS_OPERATIONS" || code === "DEPARTMENT_OPERATIONS") {
    seedOpsPulseCache(momentId, data as never, userId);
  } else {
    seedBusinessPulseCache(momentId, data as never, userId);
  }
}

function seedMoments(
  code: string,
  momentId: string,
  data: Record<string, unknown>,
  userId?: string | null,
) {
  if (code === "BUSINESS_RUNWAY") {
    seedRunwayMomentsCache(momentId, data as never, userId);
  } else if (code === "BUSINESS_OPERATIONS" || code === "DEPARTMENT_OPERATIONS") {
    seedOpsMomentsCache(momentId, data as never, userId);
  } else {
    seedBusinessMomentsCache(momentId, data as never, userId);
  }
}
