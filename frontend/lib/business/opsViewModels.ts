import type {
  BusinessLifeResponse,
  BusinessMemoryResponse,
  OpsMomentsResponse,
  OpsPulseResponse,
  TeamOpsEventItem,
} from "@/lib/api/businessActive";
import { mergeOptimisticOpsEvents } from "@/lib/business/opsApiMappers";
import {
  filterEventsByMoment,
  filterMemoryByMoment,
  MEMORY_BUCKET_ORDER,
} from "@/lib/business/teamOpsApiMappers";

export function toOpsPulseViewModel(
  data: OpsPulseResponse,
  optimisticItems: TeamOpsEventItem[] = [],
): OpsPulseResponse {
  return {
    ...data,
    recent_activity: {
      ...data.recent_activity,
      items: mergeOptimisticOpsEvents(data.recent_activity.items, optimisticItems),
    },
  };
}

export function toOpsLifeViewModel(
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

export function toOpsMemoryViewModel(
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

export type { OpsMomentsResponse };
export { MEMORY_BUCKET_ORDER };
