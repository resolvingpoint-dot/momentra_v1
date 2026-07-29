"use client";

import { ActiveMoments } from "@/components/group/active/experience/ActiveMoments";

type SharedLivingMomentsProps = {
  momentId: string;
  onQuickAdd?: () => void;
  bottomPadding?: number;
  reloadKey?: number;
};

/** Live Shared Living operations hub from `/shared-living/.../moments-view`. */
export function SharedLivingMoments({ momentId, onQuickAdd, bottomPadding, reloadKey }: SharedLivingMomentsProps) {
  return (
    <ActiveMoments
      momentId={momentId}
      onQuickAdd={onQuickAdd}
      bottomPadding={bottomPadding}
      reloadKey={reloadKey}
      source="living"
    />
  );
}
