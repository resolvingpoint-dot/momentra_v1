/**
 * ViewModels for Team Ops screens — mapping lives here, not in components.
 */
import type {
  BusinessActivityListItem,
  BusinessLifeResponse,
  BusinessMemoryResponse,
  TeamOpsEventItem,
  TeamOpsPulseResponse,
} from "@/lib/api/businessActive";
import {
  filterEventsByMoment,
  filterMemoryByMoment,
  mergeOptimisticEvents,
  MEMORY_BUCKET_ORDER,
} from "@/lib/business/teamOpsApiMappers";

export function toPulseViewModel(
  data: TeamOpsPulseResponse,
  optimisticItems: TeamOpsEventItem[] = [],
): TeamOpsPulseResponse {
  return {
    ...data,
    recent_activity: {
      ...data.recent_activity,
      items: mergeOptimisticEvents(data.recent_activity.items, optimisticItems),
    },
  };
}

export function toLifeViewModel(
  data: BusinessLifeResponse,
  sourceMomentId: string | null | undefined,
): BusinessLifeResponse {
  const slices = Object.fromEntries(
    Object.entries(data.slices).map(([key, slice]) => [
      key,
      {
        ...slice,
        items: filterEventsByMoment(slice.items ?? [], sourceMomentId),
      },
    ]),
  );
  return { ...data, slices };
}

export function toMemoryViewModel(
  data: BusinessMemoryResponse,
  sourceMomentId: string | null | undefined,
): BusinessMemoryResponse {
  const buckets = Object.fromEntries(
    Object.entries(data.buckets ?? {}).map(([key, bucket]) => [
      key,
      {
        ...bucket,
        items: filterMemoryByMoment(bucket.items ?? [], sourceMomentId),
      },
    ]),
  );
  return {
    ...data,
    events: filterMemoryByMoment(data.events ?? [], sourceMomentId),
    buckets,
  };
}

export function toActivityViewModel(
  data: BusinessActivityListItem[] | null,
  optimisticItems: TeamOpsEventItem[] = [],
): BusinessActivityListItem[] {
  const server = data ?? [];
  const optimisticAsList: BusinessActivityListItem[] = optimisticItems.map((o) => ({
    event_id: o.event_id,
    action_type: o.action_type,
    title: o.title,
    subtitle: o.subtitle,
    occurred_at: o.occurred_at,
    created_at: o.occurred_at,
    is_editable: false,
    is_deletable: false,
    supported_actions: [],
  }));
  const ordered = mergeOptimisticEvents(
    server.map((s) => ({
      event_id: s.event_id,
      action_type: s.action_type,
      title: s.title,
      subtitle: s.subtitle,
      occurred_at: s.occurred_at ?? s.created_at,
    })),
    optimisticItems,
  );
  const byId = new Map(server.map((s) => [s.event_id, s]));
  for (const o of optimisticAsList) {
    if (!byId.has(o.event_id)) byId.set(o.event_id, o);
  }
  return ordered.map((e) => byId.get(e.event_id)!).filter(Boolean);
}

export { MEMORY_BUCKET_ORDER };
