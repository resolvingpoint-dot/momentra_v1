"use client";

import { GroupActionCenterShell } from "@/components/group/action-center/GroupActionCenterShell";

type TripQuickAddSheetProps = {
  momentId: string;
  actionId: string;
  onClose: () => void;
  onSuccess?: () => void;
};

export function TripQuickAddSheet({ momentId, onClose, onSuccess }: TripQuickAddSheetProps) {
  return (
    <GroupActionCenterShell
      momentId={momentId}
      momentTypeCode="SHARED_EXPERIENCE"
      onClose={onClose}
      onSuccess={onSuccess}
    />
  );
}
