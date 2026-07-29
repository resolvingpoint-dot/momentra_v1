/**
 * Group setup presentation catalog (copy only — not validation).
 */
import copyJson from "@/lib/group/group_setup_copy.json";

export type GroupSetupTemplateId = "shared_experience" | "shared_purchase" | "shared_living";

export type GroupSetupChoice = {
  value: string;
  label: string;
  description?: string;
  icon?: string;
};

type CopyRoot = typeof copyJson;

export const GROUP_SETUP_COPY = copyJson as CopyRoot;

export function groupSetupTemplate(id: GroupSetupTemplateId) {
  return GROUP_SETUP_COPY.templates[id];
}

export function groupChoices(key: keyof CopyRoot["choices"]): GroupSetupChoice[] {
  return GROUP_SETUP_COPY.choices[key] as GroupSetupChoice[];
}

export function groupChoiceLabel(
  choicesKey: keyof CopyRoot["choices"],
  value: string | null | undefined,
): string {
  if (!value) return "";
  const hit = groupChoices(choicesKey).find((c) => c.value === value);
  return hit?.label ?? value.replaceAll("_", " ");
}

export function groupTemplateForMomentType(momentTypeCode: string | null | undefined): GroupSetupTemplateId {
  const code = (momentTypeCode ?? "").toUpperCase();
  if (code === "SHARED_PURCHASE") return "shared_purchase";
  if (code === "SHARED_LIVING") return "shared_living";
  return "shared_experience";
}

export function groupGuidedSteps(id: GroupSetupTemplateId) {
  return groupSetupTemplate(id).steps.map((s) => ({
    id: s.id,
    title: s.title,
    shortTitle: s.shortTitle,
    description: s.description,
  }));
}
