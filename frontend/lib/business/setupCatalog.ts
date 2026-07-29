/**
 * Presentation catalog for Business setup (copy only — not a validation engine).
 * Mirrors docs/business/business_setup_copy.json for runtime use on web.
 */

import copyJson from "@/lib/business/business_setup_copy.json";
import type { SetupChoice } from "@/components/setup/shared/setupControlTypes";

export type { SetupChoice };

export type SetupFieldPresentation = {
  label: string;
  helper?: string;
  placeholder?: string;
  optionalLabel?: string;
  control:
    | "chips"
    | "cards"
    | "multi_chips"
    | "search_picker"
    | "suggested_picker"
    | "money"
    | "text"
    | "toggle"
    | "date";
};

export type GuidedCatalogStep = {
  id: string;
  title: string;
  shortTitle: string;
  description: string;
  optional?: boolean;
  hiddenWhen?: string;
};

export type SetupTemplateId = "team_ops" | "business_runway" | "business_operations";

type CopyRoot = typeof copyJson;

export const BUSINESS_SETUP_COPY = copyJson as CopyRoot;

export const SETUP_ESTIMATED_MINUTES = BUSINESS_SETUP_COPY.estimated_minutes;

export function setupChoices(key: keyof CopyRoot["choices"]): SetupChoice[] {
  return BUSINESS_SETUP_COPY.choices[key] as SetupChoice[];
}

export function setupTemplate(id: SetupTemplateId) {
  return BUSINESS_SETUP_COPY.templates[id];
}

export function setupStepMeta(id: SetupTemplateId, step: number) {
  return setupTemplate(id).steps.find((s) => s.step === step);
}

export function businessGuidedSteps(id: SetupTemplateId): GuidedCatalogStep[] {
  return setupTemplate(id).steps.map((s) => ({
    id: s.id,
    title: s.title,
    shortTitle: s.shortTitle,
    description: (s as { description?: string }).description ?? s.intro ?? s.title,
  }));
}

export function choiceLabel(
  choicesKey: keyof CopyRoot["choices"],
  value: string | null | undefined,
): string {
  if (!value) return "";
  const hit = setupChoices(choicesKey).find((c) => c.value === value);
  return hit?.label ?? value.replaceAll("_", " ");
}

export function roleDescription(
  rolesKey: "team_roles" | "runway_roles" | "ops_roles",
  role: string,
): string {
  const hit = setupChoices(rolesKey).find((c) => c.value === role);
  return hit?.description ?? "";
}

/** Re-export identity fallbacks used by searchable pickers. */
export {
  SETUP_COUNTRY_FALLBACK,
  SETUP_CURRENCY_FALLBACK,
  SETUP_FY_START_OPTIONS,
  SETUP_LOCALE_FALLBACK,
  SETUP_TIMEZONE_FALLBACK,
  curatedChoices,
  enumChoices,
} from "@/lib/business/setupIdentityOptions";

export type { SetupChoice as IdentitySetupChoice } from "@/lib/business/setupIdentityOptions";
