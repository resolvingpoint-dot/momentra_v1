"use client";

import { RelationshipsQuickAddSheet } from "@/components/personal/emotional_security/quickadd/RelationshipsQuickAddSheet";
import { FutureBuildingQuickAddSheet } from "@/components/personal/future_building/quickadd/FutureBuildingQuickAddSheet";
import { LifestyleQuickAddHub } from "@/components/personal/lifestyle/quick_add/LifestyleQuickAddHub";
import { LifeOperationsQuickAddSheet } from "@/components/personal/life_operations/quickadd/LifeOperationsQuickAddSheet";
import { PersonalQuickAddFallbackSheet } from "@/components/personal/shared/PersonalQuickAddFallbackSheet";
import type { PersonalMomentTypeCode } from "@/lib/personal/personalMomentSession";

export type PersonalMomentQuickAddRouterProps = {
  momentTypeCode: PersonalMomentTypeCode;
  momentId?: string | null;
  hasActiveMoment: boolean;
  initialEventType?: string | null;
  open?: boolean;
  onClose: () => void;
  onSuccess?: () => void;
  onBeginSetup?: () => void;
};

export function PersonalMomentQuickAddRouter({
  momentTypeCode,
  momentId,
  hasActiveMoment,
  initialEventType,
  open = true,
  onClose,
  onSuccess,
  onBeginSetup,
}: PersonalMomentQuickAddRouterProps) {
  if (!hasActiveMoment) {
    if (process.env.NODE_ENV === "development") {
      console.debug("QuickAddGate blocked:", {
        selectedType: momentTypeCode,
        resolverState: "router_fallback",
        activeMomentId: momentId ?? null,
        bootstrapState: "unknown",
      });
    }
    return (
      <PersonalQuickAddFallbackSheet
        momentTypeCode={momentTypeCode}
        onClose={onClose}
        onBeginSetup={onBeginSetup}
      />
    );
  }

  const shared = { initialEventType, open, onClose, onSuccess };

  switch (momentTypeCode) {
    case "RELATIONSHIPS":
      return <RelationshipsQuickAddSheet defaultMomentId={momentId} {...shared} />;
    case "FUTURE_BUILDING":
      return <FutureBuildingQuickAddSheet defaultMomentId={momentId} {...shared} />;
    case "LIFESTYLE":
      return <LifestyleQuickAddHub momentId={momentId} {...shared} />;
    case "LIFE_OPERATIONS":
      return <LifeOperationsQuickAddSheet defaultMomentId={momentId} onBeginSetup={onBeginSetup} {...shared} />;
    default:
      return (
        <PersonalQuickAddFallbackSheet
          momentTypeCode={momentTypeCode}
          onClose={onClose}
          onBeginSetup={onBeginSetup}
        />
      );
  }
}
