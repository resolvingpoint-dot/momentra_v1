"use client";

import { useCallback, useMemo, useState } from "react";
import { BusinessOperationsMoments } from "@/components/business/active/business-operations/moments/BusinessOperationsMoments";
import { BusinessOperationsPulse } from "@/components/business/active/business-operations/pulse/BusinessOperationsPulse";
import { TeamOperationsActivity } from "@/components/business/active/team-operations/activity/TeamOperationsActivity";
import { BusinessLife } from "@/components/business/life/BusinessLife";
import { BusinessMemory } from "@/components/business/memory/BusinessMemory";
import type { TeamOpsEventItem } from "@/lib/api/businessActive";
import type { BusinessActivityFilters } from "@/lib/business/activityFilters";
import { OPS_ACTION_META, OPS_ACTION_TYPES } from "@/lib/business/opsActionRegistry";
import {
  toOpsLifeViewModel,
  toOpsMemoryViewModel,
  toOpsPulseViewModel,
} from "@/lib/business/opsViewModels";
import { toActivityViewModel } from "@/lib/business/teamOpsViewModels";
import {
  useBusinessActivity,
  useBusinessActivityDetail,
  useBusinessLife,
  useBusinessMemory,
  useOpsMoments,
  useOpsPulse,
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

export function BusinessOperationsActiveTabs({
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

  const pulse = useOpsPulse(momentId, tab === "pulse", reloadKey, userId);
  const moments = useOpsMoments(momentId, tab === "moments", reloadKey, userId);
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
    () => (pulse.data ? toOpsPulseViewModel(pulse.data, optimisticItems) : null),
    [pulse.data, optimisticItems],
  );

  const handleChanged = useCallback(() => {
    onChanged?.();
    void pulse.reload(true);
    void moments.reload(true);
  }, [onChanged, pulse, moments]);

  if (tab === "pulse") {
    return (
      <BusinessOperationsPulse
        data={pulseVm}
        loading={pulse.loading}
        refreshing={pulse.refreshing}
        error={pulse.error}
        bottomPadding={bottomPadding}
        onRetry={() => void pulse.reload(true)}
        onQuickAdd={onQuickAdd}
        onViewActivity={() => onOpenActivity?.(null)}
      />
    );
  }

  if (tab === "moments") {
    return (
      <BusinessOperationsMoments
        data={moments.data}
        loading={moments.loading}
        refreshing={moments.refreshing}
        error={moments.error}
        bottomPadding={bottomPadding}
        onRetry={() => void moments.reload(true)}
        onQuickAdd={onQuickAdd}
      />
    );
  }

  if (tab === "life") {
    const vm = life.data ? toOpsLifeViewModel(life.data, momentId) : null;
    return (
      <BusinessLife
        data={vm}
        loading={life.loading}
        refreshing={life.refreshing}
        error={life.error}
        bottomPadding={bottomPadding}
        onRetry={() => void life.reload(true)}
      />
    );
  }

  if (tab === "memory") {
    const vm = memory.data ? toOpsMemoryViewModel(memory.data, momentId) : null;
    return (
      <BusinessMemory
        data={vm}
        loading={memory.loading}
        refreshing={memory.refreshing}
        error={memory.error}
        bottomPadding={bottomPadding}
        onRetry={() => void memory.reload(true)}
      />
    );
  }

  return (
    <TeamOperationsActivity
      items={toActivityViewModel(activity.data?.items ?? null, optimisticItems)}
      total={activity.total}
      page={page}
      pageSize={20}
      loading={activity.loading}
      refreshing={activity.refreshing}
      error={activity.error}
      filters={filters}
      bottomPadding={bottomPadding}
      initialEventId={selectedEventId ?? activityEventId}
      detail={detail.data}
      detailLoading={detail.loading}
      actionTypes={[...OPS_ACTION_TYPES]}
      actionMeta={OPS_ACTION_META}
      onRetry={() => void activity.reload(true)}
      onFiltersChange={setFilters}
      onPageChange={setPage}
      onSelectEvent={(id) => {
        setSelectedEventId(id);
        onOpenActivity?.(id);
      }}
      onClose={onCloseActivity}
      onSaveTitle={async (eventId, title) => {
        await BusinessActiveRepository.patchActivity(momentId, eventId, { title });
        handleChanged();
      }}
      onDelete={async (eventId) => {
        await BusinessActiveRepository.deleteActivity(momentId, eventId);
        handleChanged();
      }}
    />
  );
}
