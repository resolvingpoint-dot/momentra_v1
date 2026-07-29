import type {
  PersonalFutureBuildingQuickAddFieldGroup,
  PersonalQuickAddFieldOption,
  PersonalQuickAddMetadata,
  PersonalQuickAddOptionsResponse,
} from "@/lib/api/client";

const GROUP_TO_META: Record<string, keyof PersonalQuickAddMetadata | string> = {
  milestone_nature: "milestone_nature_options",
  impact_level: "impact_level_options",
  celebration_level: "celebration_level_options",
  outcome_value: "outcome_value_options",
  opportunity_source: "opportunity_source_options",
  opportunity_status: "opportunity_status_options",
  pivot_change: "pivot_change_options",
  pivot_reason: "pivot_reason_options",
  progress_type: "progress_type_options",
  time_invested: "time_invested_options",
  effort_level: "effort_level_options",
  learning_type: "learning_type_options",
  relevance: "relevance_level_options",
};

function labelsToOptions(labels: string[] | undefined): PersonalQuickAddFieldOption[] {
  if (!labels?.length) return [];
  return labels.map((label) => ({ value: label, label }));
}

function metaList(
  metadata: PersonalQuickAddMetadata | null | undefined,
  key: string,
): string[] {
  if (!metadata) return [];
  const raw = (metadata as Record<string, unknown>)[key];
  return Array.isArray(raw) ? (raw as string[]) : [];
}

/** Resolve chip/select options for a field group from group.options or metadata. */
export function resolveFbFieldOptions(
  group: PersonalFutureBuildingQuickAddFieldGroup,
  options: PersonalQuickAddOptionsResponse,
  eventType: string,
): PersonalQuickAddFieldOption[] {
  if (group.options?.length) return group.options;

  const metadata = options.metadata;
  if (group.group_key === "category_name") {
    const fromExpense = (options.expense_categories ?? [])
      .map((cat) => {
        const value = String(
          (cat as { name?: string; code?: string; label?: string }).name ??
            (cat as { code?: string }).code ??
            (cat as { label?: string }).label ??
            "",
        ).trim();
        if (!value) return null;
        const label = String(
          (cat as { label?: string; name?: string }).label ??
            (cat as { name?: string }).name ??
            value,
        ).trim();
        return { value, label };
      })
      .filter((x): x is PersonalQuickAddFieldOption => Boolean(x));
    if (fromExpense.length) return fromExpense;
  }

  if (group.group_key === "confidence_level") {
    const key =
      eventType === "PIVOT" ? "confidence_level_options" : "potential_level_options";
    return labelsToOptions(metaList(metadata, key));
  }

  const metaKey = GROUP_TO_META[group.group_key];
  if (metaKey) return labelsToOptions(metaList(metadata, metaKey));
  return [];
}

export const FIELD_TO_PAYLOAD_KEY: Record<string, string> = {
  notes: "notes",
  amount: "amount",
  category_name: "category_name",
  impact_level: "impact_level",
  learning_type: "learning_type",
  learning_topic: "learning_topic",
  relevance: "relevance",
  application: "application",
  milestone_nature: "milestone_nature",
  celebration_level: "celebration_level",
  outcome_value: "outcome_value",
  opportunity_source: "opportunity_source",
  opportunity_status: "opportunity_status",
  pivot_change: "pivot_change",
  pivot_reason: "pivot_reason",
  confidence_level: "confidence_level",
  progress_type: "progress_type",
  time_invested: "time_invested",
  effort_level: "effort_level",
};

export function buildFutureBuildingPayload(
  values: Record<string, string>,
): Record<string, string> {
  const payload: Record<string, string> = {};
  for (const [fieldKey, payloadKey] of Object.entries(FIELD_TO_PAYLOAD_KEY)) {
    const trimmed = values[fieldKey]?.trim();
    if (trimmed) payload[payloadKey] = trimmed;
  }
  return payload;
}

export function requiredKeysForFbTab(tab: string): Set<string> {
  switch (tab) {
    case "CONTRIBUTION":
      return new Set(["amount"]);
    case "LEARNING":
      return new Set(["learning_type"]);
    case "MILESTONE":
      return new Set(["milestone_nature"]);
    case "OPPORTUNITY":
      return new Set(["opportunity_source"]);
    case "PIVOT":
      return new Set(["pivot_change", "notes"]);
    case "PROGRESS":
      return new Set(["progress_type"]);
    default:
      return new Set();
  }
}

export function canSubmitFb(
  tab: string,
  groups: PersonalFutureBuildingQuickAddFieldGroup[],
  values: Record<string, string>,
  eventTitle: string,
): boolean {
  if (!eventTitle.trim()) return false;
  if (groups.length === 0) return Boolean(values.notes?.trim());
  return [...requiredKeysForFbTab(tab)].every((key) => Boolean(values[key]?.trim()));
}

const REQUIRED_FIELD_LABELS: Record<string, string> = {
  pivot_change: "What changed?",
  notes: "Notes",
  amount: "Amount",
  learning_type: "Learning type",
  milestone_nature: "Milestone nature",
  opportunity_source: "Opportunity source",
  progress_type: "Progress type",
};

export function missingFbRequiredHint(
  tab: string,
  groups: PersonalFutureBuildingQuickAddFieldGroup[],
  values: Record<string, string>,
  eventTitle: string,
): string | null {
  if (canSubmitFb(tab, groups, values, eventTitle)) return null;
  const missing: string[] = [];
  if (!eventTitle.trim()) missing.push("title");
  for (const key of [...requiredKeysForFbTab(tab)].sort()) {
    if (!values[key]?.trim()) {
      missing.push(REQUIRED_FIELD_LABELS[key] ?? key.replaceAll("_", " "));
    }
  }
  if (missing.length === 0) return null;
  return `Required: ${missing.join(", ")}`;
}
