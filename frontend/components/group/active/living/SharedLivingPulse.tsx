"use client";

import { ExperiencePulse } from "@/components/group/active/experience/ExperiencePulse";

type SharedLivingPulseProps = {
  momentId: string;
  onQuickAdd: (actionId?: string) => void;
  bottomPadding?: number;
  reloadKey?: number;
  onViewAllActivity?: () => void;
  onEditActivity?: (id: string, eventType: string) => void;
};

/** Live Shared Living pulse from `/shared-living/.../pulse` with Stitch tokens. */
export function SharedLivingPulse({
  momentId,
  onQuickAdd,
  bottomPadding,
  reloadKey,
  onViewAllActivity,
  onEditActivity,
}: SharedLivingPulseProps) {
  return (
    <ExperiencePulse
      momentId={momentId}
      onQuickAdd={onQuickAdd}
      bottomPadding={bottomPadding}
      reloadKey={reloadKey}
      template="living"
      onViewAllActivity={onViewAllActivity}
      onEditActivity={onEditActivity}
    />
  );
}
