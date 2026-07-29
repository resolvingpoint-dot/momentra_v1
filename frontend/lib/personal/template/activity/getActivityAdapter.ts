import type { PersonalMomentTypeCode } from "@/lib/personal/personalMomentSession";
import { futureBuildingActivityAdapter } from "@/lib/personal/template/activity/futureBuildingActivityAdapter";
import { lifeOperationsActivityAdapter } from "@/lib/personal/template/activity/lifeOperationsActivityAdapter";
import { lifestyleActivityAdapter } from "@/lib/personal/template/activity/lifestyleActivityAdapter";
import { relationshipsActivityAdapter } from "@/lib/personal/template/activity/relationshipsActivityAdapter";
import type { TemplateActivityAdapter } from "@/lib/personal/template/activity/types";

const ADAPTERS: Partial<Record<PersonalMomentTypeCode, TemplateActivityAdapter>> = {
  LIFE_OPERATIONS: lifeOperationsActivityAdapter,
  FUTURE_BUILDING: futureBuildingActivityAdapter,
  LIFESTYLE: lifestyleActivityAdapter,
  RELATIONSHIPS: relationshipsActivityAdapter,
};

export function getActivityAdapter(momentTypeCode: PersonalMomentTypeCode): TemplateActivityAdapter {
  const adapter = ADAPTERS[momentTypeCode];
  if (!adapter) {
    return lifeOperationsActivityAdapter;
  }
  return adapter;
}
