"use client";

import { LifeOperationsLife, LifeOperationsLifeSkeleton, LifeOperationsLifeEmpty } from "@/components/personal/life_operations/life/LifeOperationsLife";
import type { TemplateLifeResponse } from "@/lib/api/personal";
import type { PersonalMomentTypeCode } from "@/lib/personal/personalMomentSession";

type TemplateLifeScreenProps = {
  data: TemplateLifeResponse;
  momentTypeCode: PersonalMomentTypeCode;
  bottomPadding?: number;
};

/** Shared My Money operating view — same projection shape for all personal templates. */
export function TemplateLifeScreen({ data, momentTypeCode, bottomPadding = 0 }: TemplateLifeScreenProps) {
  void momentTypeCode;
  return <LifeOperationsLife data={data} bottomPadding={bottomPadding} />;
}

export { LifeOperationsLifeSkeleton as TemplateLifeSkeleton, LifeOperationsLifeEmpty as TemplateLifeEmpty };
