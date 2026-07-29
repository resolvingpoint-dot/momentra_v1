"use client";

import { ActiveMemory } from "@/components/group/active/experience/ActiveMemory";

type SharedPurchaseMemoryProps = {
  momentId: string;
  onQuickAdd?: () => void;
  bottomPadding?: number;
  reloadKey?: number;
};

/** Live Shared Purchase memory hub from `/shared-purchase/.../moments-view`. */
export function SharedPurchaseMemory({ momentId, onQuickAdd, bottomPadding, reloadKey }: SharedPurchaseMemoryProps) {
  return (
    <ActiveMemory
      momentId={momentId}
      onQuickAdd={onQuickAdd}
      bottomPadding={bottomPadding}
      reloadKey={reloadKey}
      source="purchase"
    />
  );
}
