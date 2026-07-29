"use client";

import { ExperiencePulse } from "@/components/group/active/experience/ExperiencePulse";

type SharedPurchasePulseProps = {
  momentId: string;
  onQuickAdd: (actionId?: string) => void;
  bottomPadding?: number;
  reloadKey?: number;
};

/** Live Shared Purchase pulse from `/shared-purchase/.../pulse` with Stitch tokens. */
export function SharedPurchasePulse({ momentId, onQuickAdd, bottomPadding, reloadKey }: SharedPurchasePulseProps) {
  return (
    <ExperiencePulse
      momentId={momentId}
      onQuickAdd={onQuickAdd}
      bottomPadding={bottomPadding}
      reloadKey={reloadKey}
      template="purchase"
    />
  );
}
