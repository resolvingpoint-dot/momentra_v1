import type { RunwayMomentsResponse, RunwayPulseResponse, TeamOpsEventItem } from "@/lib/api/businessActive";
import { mergeOptimisticRunwayEvents } from "@/lib/business/runwayApiMappers";
import {
  filterEventsByMoment,
  filterMemoryByMoment,
  MEMORY_BUCKET_ORDER,
} from "@/lib/business/teamOpsApiMappers";
import type { BusinessLifeResponse, BusinessMemoryResponse } from "@/lib/api/businessActive";

export function toRunwayPulseViewModel(
  data: RunwayPulseResponse,
  optimisticItems: TeamOpsEventItem[] = [],
): RunwayPulseResponse {
  return {
    ...data,
    recent_activity: {
      ...data.recent_activity,
      items: mergeOptimisticRunwayEvents(data.recent_activity.items, optimisticItems),
    },
  };
}

export function toRunwayLifeViewModel(
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

export function toRunwayMemoryViewModel(
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

export { MEMORY_BUCKET_ORDER };
