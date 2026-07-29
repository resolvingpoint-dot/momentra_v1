"use client";

import { ActiveMoments } from "@/components/group/active/experience/ActiveMoments";

type SharedPurchaseMomentsProps = {
  momentId: string;
  onQuickAdd?: () => void;
  bottomPadding?: number;
  reloadKey?: number;
};

/** Live Shared Purchase operations hub from `/shared-purchase/.../moments-view`. */
export function SharedPurchaseMoments({ momentId, onQuickAdd, bottomPadding, reloadKey }: SharedPurchaseMomentsProps) {
  return (
    <ActiveMoments
      momentId={momentId}
      onQuickAdd={onQuickAdd}
      bottomPadding={bottomPadding}
      reloadKey={reloadKey}
      source="purchase"
    />
  );
}
