import type {
  PersonalFutureBuildingQuickAddFieldGroup,
  PersonalQuickAddFieldOption,
  PersonalQuickAddMetadata,
  PersonalQuickAddOptionsResponse,
} from "@/lib/api/client";
import { normalizeLifestyleEventType } from "@/lib/quick_add/lifestyleCopy";

const GROUP_TO_META: Record<string, string> = {
  spend_category: "spend_category_options",
  experience_type: "experience_type_options",
  experience_quality: "experience_quality_options",
  energy_impact: "energy_impact_options",
  people_context: "people_context_options",
  location_context: "location_context_options",
  value_received: "value_received_options",
  wellbeing_areas: "wellbeing_area_options",
  wellbeing_state: "wellbeing_state_options",
  contributors: "contributor_options",
  discovery_type: "discovery_type_options",
  curiosity_level: "curiosity_level_options",
  discovery_impact: "discovery_impact_options",
  creation_type: "creation_type_options",
  satisfaction_level: "satisfaction_level_options",
  time_invested: "time_invested_options",
  adjustment_area: "adjustment_area_options",
  priority_level: "priority_level_options",
  confidence_level: "confidence_level_options",
};

function metaList(metadata: PersonalQuickAddMetadata | null | undefined, key: string): PersonalQuickAddFieldOption[] {
  if (!metadata) return [];
  const raw = (metadata as Record<string, unknown>)[key];
  if (!Array.isArray(raw)) return [];
  return raw
    .map((item) => {
      if (typeof item === "string") return { value: item, label: item };
      if (item && typeof item === "object") {
        const obj = item as { value?: string; label?: string };
        const value = String(obj.value ?? obj.label ?? "").trim();
        if (!value) return null;
        return { value, label: String(obj.label ?? value) };
      }
      return null;
    })
    .filter((x): x is PersonalQuickAddFieldOption => Boolean(x));
}

export function resolveLsFieldOptions(
  group: PersonalFutureBuildingQuickAddFieldGroup,
  options: PersonalQuickAddOptionsResponse,
): PersonalQuickAddFieldOption[] {
  if (group.options?.length) return group.options;
  const metaKey = GROUP_TO_META[group.group_key];
  if (!metaKey) return [];
  return metaList(options.metadata, metaKey);
}

export function canSubmitLifestyle(
  tab: string,
  values: Record<string, string>,
  multi: Record<string, Set<string>>,
  eventTitle: string,
): boolean {
  if (!eventTitle.trim()) return false;
  const normalized = normalizeLifestyleEventType(tab);
  switch (normalized) {
    case "LIFESTYLE_EXPENSE":
      return Boolean(values.amount?.trim()) && Number(values.amount) > 0;
    case "EXPERIENCE":
      return Boolean(values.experience_type);
    case "WELLBEING":
      return Boolean(values.wellbeing_state) && (multi.wellbeing_areas?.size ?? 0) > 0;
    case "DISCOVERY":
      return Boolean(values.discovery_type);
    case "EXPRESSION":
      return Boolean(values.creation_type);
    case "ADJUST":
      return Boolean(values.adjustment_area);
    default:
      return Boolean(values.notes?.trim());
  }
}

export function buildLifestylePayload(
  values: Record<string, string>,
  multi: Record<string, Set<string>>,
) {
  const trim = (key: string) => values[key]?.trim() || undefined;
  const raw = (key: string) => values[key] || undefined;
  const wellbeingAreas = Array.from(multi.wellbeing_areas ?? []).sort();
  return {
    notes: trim("notes"),
    amount: trim("amount"),
    spend_category: raw("spend_category"),
    experience_type: raw("experience_type"),
    experience_quality: raw("experience_quality"),
    energy_impact: raw("energy_impact"),
    people_context: raw("people_context"),
    location_context: raw("location_context"),
    value_received: raw("value_received"),
    wellbeing_area: wellbeingAreas[0],
    wellbeing_areas: wellbeingAreas,
    wellbeing_state: raw("wellbeing_state"),
    contributors: Array.from(multi.contributors ?? []).sort(),
    discovery_type: raw("discovery_type"),
    discovery_impact: raw("discovery_impact"),
    curiosity_level: raw("curiosity_level"),
    creation_type: raw("creation_type"),
    satisfaction_level: raw("satisfaction_level"),
    time_invested: raw("time_invested"),
    adjustment_area: raw("adjustment_area"),
    priority_level: raw("priority_level"),
    confidence_level: raw("confidence_level"),
  };
}
