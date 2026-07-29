import type { ReactNode } from "react";
import type { PersonalMomentTypeCode } from "@/lib/personal/personalMomentSession";
import { FutureBuildingMemorySkeleton } from "@/components/personal/future_building/memory/FutureBuildingMemory";
import { FutureBuildingMomentsSkeleton } from "@/components/personal/future_building/moments/FutureBuildingMoments";
import { FutureBuildingPulseSkeleton } from "@/components/personal/future_building/pulse/FutureBuildingPulse";
import { RelationshipsMemorySkeleton } from "@/components/personal/emotional_security/memory/RelationshipsMemory";
import { RelationshipsMomentsSkeleton } from "@/components/personal/emotional_security/moments/RelationshipsMoments";
import { RelationshipsPulseSkeleton } from "@/components/personal/emotional_security/pulse/RelationshipsPulse";
import { LifestyleMemorySkeleton } from "@/components/personal/lifestyle/memory/LifestyleMemory";
import { LifestyleMomentsSkeleton } from "@/components/personal/lifestyle/moments/LifestyleMoments";
import { LifestylePulseSkeleton } from "@/components/personal/lifestyle/pulse/LifestylePulse";
import { LifeOperationsMemorySkeleton } from "@/components/personal/life_operations/memory/LifeOperationsMemory";
import { LifeOperationsMomentsSkeleton } from "@/components/personal/life_operations/moments/LifeOperationsMoments";
import { LifeOperationsPulseSkeleton } from "@/components/personal/life_operations/pulse/LifeOperationsPulseSkeleton";
import { TemplateMemorySkeleton } from "@/components/personal/template/TemplateMemoryScreen";

type SkeletonProps = { bottomPadding?: number };

export function pulseSkeletonForType(
  typeCode: PersonalMomentTypeCode,
  props: SkeletonProps = {},
): ReactNode {
  switch (typeCode) {
    case "FUTURE_BUILDING":
      return <FutureBuildingPulseSkeleton {...props} />;
    case "LIFESTYLE":
      return <LifestylePulseSkeleton {...props} />;
    case "RELATIONSHIPS":
      return <RelationshipsPulseSkeleton {...props} />;
    default:
      return <LifeOperationsPulseSkeleton />;
  }
}

export function momentsSkeletonForType(
  typeCode: PersonalMomentTypeCode,
  props: SkeletonProps = {},
): ReactNode {
  switch (typeCode) {
    case "FUTURE_BUILDING":
      return <FutureBuildingMomentsSkeleton {...props} />;
    case "LIFESTYLE":
      return <LifestyleMomentsSkeleton {...props} />;
    case "RELATIONSHIPS":
      return <RelationshipsMomentsSkeleton {...props} />;
    default:
      return <LifeOperationsMomentsSkeleton {...props} />;
  }
}

export function memorySkeletonForType(
  typeCode: PersonalMomentTypeCode,
  props: SkeletonProps = {},
): ReactNode {
  switch (typeCode) {
    case "FUTURE_BUILDING":
      return <FutureBuildingMemorySkeleton {...props} />;
    case "LIFESTYLE":
      return <LifestyleMemorySkeleton {...props} />;
    case "RELATIONSHIPS":
      return <RelationshipsMemorySkeleton {...props} />;
    default:
      return <TemplateMemorySkeleton {...props} />;
  }
}
