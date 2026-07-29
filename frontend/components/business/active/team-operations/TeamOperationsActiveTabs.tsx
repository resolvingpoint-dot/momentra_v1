"use client";

/**
 * Hook-owning Team Ops ACTIVE shell — ViewModels + selected-tab-only hooks.
 */
import { useCallback, useMemo, useState } from "react";
import { TeamOperationsPulse } from "@/components/business/active/team-operations/pulse/TeamOperationsPulse";
import { TeamOperationsMoments } from "@/components/business/active/team-operations/moments/TeamOperationsMoments";
import { TeamOperationsActivity } from "@/components/business/active/team-operations/activity/TeamOperationsActivity";
import { BusinessLife } from "@/components/business/life/BusinessLife";
import { BusinessMemory } from "@/components/business/memory/BusinessMemory";
import type { TeamOpsEventItem } from "@/lib/api/businessActive";
import type { BusinessActivityFilters } from "@/lib/business/activityFilters";
import {
  toActivityViewModel,
  toLifeViewModel,
  toMemoryViewModel,
  toPulseViewModel,
} from "@/lib/business/teamOpsViewModels";
import {
  useBusinessActivity,
  useBusinessActivityDetail,
  useBusinessLife,
  useBusinessMemory,
  useBusinessMoments,
  useBusinessPulse,
} from "@/hooks/useBusinessActiveTabs";
import { BusinessActiveRepository } from "@/repositories/BusinessActiveRepository";

type Tab = "pulse" | "moments" | "life" | "memory" | "activity";

type Props = {
  momentId: string;
  tab: Tab;
  bottomPadding?: number;
  reloadKey?: number;
  userId?: string | null;
  optimisticItems?: TeamOpsEventItem[];
  activityEventId?: string | null;
  onQuickAdd?: () => void;
  onOpenActivity?: (eventId?: string | null) => void;
  onCloseActivity?: () => void;
  onChanged?: () => void;
};

export function TeamOperationsActiveTabs({
  momentId,
  tab,
  bottomPadding = 0,
  reloadKey = 0,
  userId = null,
  optimisticItems = [],
  activityEventId = null,
  onQuickAdd,
  onOpenActivity,
  onCloseActivity,
  onChanged,
}: Props) {
  const [filters, setFilters] = useState<BusinessActivityFilters>({
    sort: "newest",
    status: "active",
  });
  const [page, setPage] = useState(1);
  const [selectedEventId, setSelectedEventId] = useState<string | null>(activityEventId);

  const pulse = useBusinessPulse(momentId, tab === "pulse", reloadKey, userId);
  const moments = useBusinessMoments(momentId, tab === "moments", reloadKey, userId);
  const activity = useBusinessActivity(
    momentId,
    tab === "activity",
    reloadKey,
    userId,
    filters,
    { page, pageSize: 20 },
  );
  const detail = useBusinessActivityDetail(
    momentId,
    selectedEventId,
    tab === "activity" && Boolean(selectedEventId),
    reloadKey,
    userId,
  );
  const life = useBusinessLife(tab === "life", reloadKey, userId);
  const memory = useBusinessMemory(tab === "memory", reloadKey, userId);

  const pulseVm = useMemo(
    () => (pulse.data ? toPulseViewModel(pulse.data, optimisticItems) : null),
    [pulse.data, optimisticItems],
  );
  const lifeVm = useMemo(
    () => (life.data ? toLifeViewModel(life.data, momentId) : null),
    [life.data, momentId],
  );
  const memoryVm = useMemo(
    () => (memory.data ? toMemoryViewModel(memory.data, momentId) : null),
    [memory.data, momentId],
  );
  const activityItems = useMemo(
    () => toActivityViewModel(activity.items, optimisticItems),
    [activity.items, optimisticItems],
  );

  const onSelectEvent = useCallback((eventId: string | null) => {
    setSelectedEventId(eventId);
  }, []);

  if (tab === "activity") {
    return (
      <TeamOperationsActivity
        items={activityItems}
        total={activity.total}
        page={page}
        loading={activity.loading}
        refreshing={activity.refreshing}
        error={activity.error}
        filters={filters}
        detail={detail.data}
        detailLoading={detail.loading}
        detailError={detail.error}
        initialEventId={activityEventId}
        bottomPadding={bottomPadding}
        onFiltersChange={setFilters}
        onPageChange={setPage}
        onSelectEvent={onSelectEvent}
        onRetry={() => void activity.reload()}
        onClose={onCloseActivity}
        onSaveTitle={async (eventId, title) => {
          await BusinessActiveRepository.patchActivity(momentId, eventId, { title });
          onChanged?.();
        }}
        onDelete={async (eventId) => {
          await BusinessActiveRepository.deleteActivity(momentId, eventId);
          onChanged?.();
        }}
      />
    );
  }

  if (tab === "pulse") {
    return (
      <TeamOperationsPulse
        data={pulseVm}
        loading={pulse.loading}
        refreshing={pulse.refreshing}
        error={pulse.error}
        bottomPadding={bottomPadding}
        onRetry={() => void pulse.reload()}
        onQuickAdd={onQuickAdd}
        onViewActivity={() => onOpenActivity?.(null)}
        onSelectActivity={(item) => onOpenActivity?.(item.event_id || null)}
      />
    );
  }

  if (tab === "moments") {
    return (
      <TeamOperationsMoments
        data={moments.data}
        loading={moments.loading}
        refreshing={moments.refreshing}
        error={moments.error}
        bottomPadding={bottomPadding}
        onRetry={() => void moments.reload()}
        onQuickAdd={onQuickAdd}
      />
    );
  }

  if (tab === "life") {
    return (
      <BusinessLife
        data={lifeVm}
        loading={life.loading}
        refreshing={life.refreshing}
        error={life.error}
        bottomPadding={bottomPadding}
        onRetry={() => void life.reload()}
      />
    );
  }

  return (
    <BusinessMemory
      data={memoryVm}
      loading={memory.loading}
      refreshing={memory.refreshing}
      error={memory.error}
      bottomPadding={bottomPadding}
      onRetry={() => void memory.reload()}
    />
  );
}
