"use client";

import { getActionCenterActions } from "@/lib/action-center/actionCenterMeta";
import { GroupActionCenterHub } from "@/components/group/action-center/GroupActionCenterHub";

type TripQuickAddHubProps = {
  categories?: unknown[];
  tripName?: string;
  onModuleSelect: (moduleCode: string) => void;
};

export function TripQuickAddHub({ tripName, onModuleSelect }: TripQuickAddHubProps) {
  return (
    <GroupActionCenterHub
      templateId="group.trip"
      templateLabel="Shared Experience"
      heroTitle="Bring your experience to life"
      heroSubtitle="Add people, plans, money, memories and decisions as your trip evolves."
      contextChips={[tripName ?? "Trip", "Shared Experience", "Quick Add"]}
      actions={getActionCenterActions("group.trip")}
      suggested={[]}
      recentIds={[]}
      onSelect={onModuleSelect}
    />
  );
}
