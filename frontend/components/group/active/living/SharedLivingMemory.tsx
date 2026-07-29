"use client";

import { ActiveMemory } from "@/components/group/active/experience/ActiveMemory";

type SharedLivingMemoryProps = {
  momentId: string;
  onQuickAdd?: () => void;
  bottomPadding?: number;
  reloadKey?: number;
};

/** Live Shared Living memory hub from `/shared-living/.../moments-view`. */
export function SharedLivingMemory({ momentId, onQuickAdd, bottomPadding, reloadKey }: SharedLivingMemoryProps) {
  return (
    <ActiveMemory
      momentId={momentId}
      onQuickAdd={onQuickAdd}
      bottomPadding={bottomPadding}
      reloadKey={reloadKey}
      source="living"
    />
  );
}
