"use client";

import {
  RelationshipsMemory,
  RelationshipsMemorySkeleton,
} from "@/components/personal/emotional_security/memory/RelationshipsMemory";
import {
  FutureBuildingMemory,
  FutureBuildingMemorySkeleton,
} from "@/components/personal/future_building/memory/FutureBuildingMemory";
import {
  LifeOperationsMemory,
  LifeOperationsMemorySkeleton,
  LifeOperationsMemoryEmpty,
} from "@/components/personal/life_operations/memory/LifeOperationsMemory";
import {
  LifestyleMemory,
  LifestyleMemorySkeleton,
} from "@/components/personal/lifestyle/memory/LifestyleMemory";
import type { TemplateMemoryResponse } from "@/lib/api/personal";
import type { PersonalMomentTypeCode } from "@/lib/personal/personalMomentSession";

type TemplateMemoryScreenProps = {
  data: TemplateMemoryResponse;
  momentTypeCode: PersonalMomentTypeCode;
  bottomPadding?: number;
  hideScreenHeader?: boolean;
};

/** Template memory projection — dispatches by moment type. */
export function TemplateMemoryScreen({
  data,
  momentTypeCode,
  bottomPadding = 0,
  hideScreenHeader = false,
}: TemplateMemoryScreenProps) {
  if (momentTypeCode === "FUTURE_BUILDING") {
    if (!data.memory_projection) {
      return <FutureBuildingMemorySkeleton bottomPadding={bottomPadding} />;
    }
    return (
      <FutureBuildingMemory
        memory={
          {
            metrics: data.memory_projection,
          } as import("@/lib/api/personalDomainTypes").PersonalFutureBuildingMemory
        }
        bottomPadding={bottomPadding}
        hideScreenHeader={hideScreenHeader}
      />
    );
  }

  if (momentTypeCode === "LIFE_OPERATIONS") {
    return (
      <LifeOperationsMemory
        data={data}
        bottomPadding={bottomPadding}
        hideScreenHeader={hideScreenHeader}
      />
    );
  }

  if (momentTypeCode === "LIFESTYLE") {
    if (!data.memory_projection) {
      return <LifestyleMemorySkeleton bottomPadding={bottomPadding} />;
    }
    return (
      <LifestyleMemory
        metrics={
          data.memory_projection as unknown as import("@/lib/api/personal").PersonalLifestyleMemoryMetrics
        }
        bottomPadding={bottomPadding}
        hideScreenHeader={hideScreenHeader}
      />
    );
  }

  if (momentTypeCode === "RELATIONSHIPS") {
    if (!data.memory_projection) {
      return <RelationshipsMemorySkeleton bottomPadding={bottomPadding} />;
    }
    return (
      <RelationshipsMemory
        memory={
          {
            metrics: data.memory_projection,
          } as import("@/lib/api/personalDomainTypes").PersonalEmotionalSecurityMemory
        }
        bottomPadding={bottomPadding}
        hideScreenHeader={hideScreenHeader}
      />
    );
  }

  return <LifeOperationsMemoryEmpty bottomPadding={bottomPadding} />;
}

export {
  LifeOperationsMemorySkeleton as TemplateMemorySkeleton,
  LifeOperationsMemoryEmpty as TemplateMemoryEmpty,
};
