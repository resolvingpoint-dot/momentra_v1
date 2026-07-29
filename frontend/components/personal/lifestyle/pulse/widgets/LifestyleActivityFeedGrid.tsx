"use client";

import { RecentActivityList } from "@/components/personal/life_operations/pulse/widgets/RecentActivityList";
import type { PulseDashboardRecentItem } from "@/lib/api/personal";
import { lifestylePulseCopy } from "@/lib/personal/lifestyle/pulse/lifestylePulseCopy";

type Props = {
  items: PulseDashboardRecentItem[];
  emptyMessage?: string | null;
  onViewAll?: () => void;
  onEditActivity?: (id: string, eventType: string) => void;
};

/** Lifestyle pulse recent activity — same canonical card as Life Ops. */
export function LifestyleActivityFeedGrid({ items, emptyMessage, onViewAll, onEditActivity }: Props) {
  return (
    <RecentActivityList
      items={items}
      emptyMessage={emptyMessage ?? lifestylePulseCopy.recentActivityEmptyFallback}
      onViewAll={onViewAll}
      onEditActivity={onEditActivity}
      title={lifestylePulseCopy.recentActivityFeedTitle}
      subtitle="Latest lifestyle moments"
      explainerId="PULSE-004"
      momentTypeCode="LIFESTYLE"
    />
  );
}
