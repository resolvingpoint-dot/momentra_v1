import type { PersonalSetupField, PersonalSetupOption } from "@/lib/api/personal";

export type SetupContext = "MY_MONEY" | "GROUP" | "BUSINESS";

export type SetupSectionType =
  | "single_choice"
  | "multi_choice"
  | "chips"
  | "card_grid"
  | "text"
  | "number"
  | "date"
  | "people"
  | "money"
  | "location"
  | "timeline";

export interface SetupSectionOption {
  value: string;
  label: string;
  description?: string | null;
  bar_level?: number | null;
  accent?: string | null;
}

export interface SetupSection {
  section_id: string;
  title: string;
  subtitle?: string | null;
  type: SetupSectionType;
  field_key: string;
  options: SetupSectionOption[];
  required: boolean;
  min_selected?: number | null;
  max_selected?: number | null;
  validation?: Record<string, unknown> | null;
  default_value?: string | string[] | null;
}

export interface SetupHero {
  badge_label: string;
  title: string;
  body: string;
  image_url?: string | null;
}

export interface SetupPreviewCard {
  card_id: string;
  title: string;
  subtitle?: string | null;
}

export interface SetupIdentityCard {
  title: string;
  subtitle?: string | null;
  badge_label?: string | null;
}

export interface SetupProjectionCard {
  title: string;
  body?: string | null;
}

export interface SetupActivationCta {
  label: string;
  footer_note?: string | null;
}

export interface SetupBackendEndpoint {
  method: string;
  path: string;
  bodyKeys?: string[];
}

export interface SetupBackendMapping {
  moment_type_code: string;
  createDraft: SetupBackendEndpoint;
  saveDraft: SetupBackendEndpoint;
  preview: SetupBackendEndpoint;
  activate: SetupBackendEndpoint;
  payloadKeys: string[];
}

export interface SetupQuickAddModulePlaceholder {
  module_code: string;
  label: string;
}

export interface SetupActiveDashboardPlaceholder {
  screen: string;
}

export interface MomentSetupTemplate {
  template_id: string;
  template_version: number;
  context: SetupContext;
  title: string;
  subtitle: string;
  hero: SetupHero;
  sections: SetupSection[];
  preview_cards: SetupPreviewCard[];
  identity_card: SetupIdentityCard;
  projection_card: SetupProjectionCard;
  activation_cta: SetupActivationCta;
  backend_mapping: SetupBackendMapping;
  quick_add_modules: SetupQuickAddModulePlaceholder[];
  active_dashboard: SetupActiveDashboardPlaceholder;
}

export const TEMPLATE_META_KEYS = {
  templateId: "template_id",
  templateVersion: "template_version",
} as const;

/** Legacy field key alias — normalize on load/save. */
export const LEGACY_FIELD_ALIASES: Record<string, string> = {
  stress_sources: "pressure_sources",
  lifestyle_style: "lifestyle_vision",
  current_lifestyle_state: "current_lifestyle",
  current_energy: "health_energy",
  want_more: "personal_priorities",
  trip_name: "experience_name",
  trip_style: "experience_type",
  experience_profile: "experience_type",
};

export function option(
  value: string,
  label: string,
  extra?: Partial<SetupSectionOption>,
): SetupSectionOption {
  return { value, label, ...extra };
}

export function groupCurrencyOptions(): SetupSectionOption[] {
  try {
    // Prefer live reference catalog when bootstrap has loaded.
    // eslint-disable-next-line @typescript-eslint/no-require-imports
    const { getReferenceData } = require("@/lib/reference_data/referenceDataStore") as {
      getReferenceData: () => { currencies?: Array<{ code: string; label: string; is_active?: boolean }> } | null;
    };
    const currencies = getReferenceData()?.currencies?.filter((c) => c.is_active !== false) ?? [];
    if (currencies.length) {
      return currencies.map((c) => option(c.code, `${c.code} — ${c.label || c.code}`));
    }
  } catch {
    /* fall through */
  }
  return [
    option("INR", "INR — Indian Rupee"),
    option("USD", "USD — US Dollar"),
    option("EUR", "EUR — Euro"),
    option("GBP", "GBP — British Pound"),
    option("AED", "AED — UAE Dirham"),
    option("AUD", "AUD — Australian Dollar"),
    option("CAD", "CAD — Canadian Dollar"),
    option("SGD", "SGD — Singapore Dollar"),
    option("JPY", "JPY — Japanese Yen"),
    option("KWD", "KWD — Kuwaiti Dinar"),
    option("CHF", "CHF — Swiss Franc"),
  ];
}

export type SetupFieldType =
  | "single_select"
  | "multi_select"
  | "text"
  | "number"
  | "date"
  | "money"
  | "location";

export function sectionTypeToFieldType(type: SetupSectionType): SetupFieldType {
  if (type === "multi_choice" || type === "chips") return "multi_select";
  if (type === "date") return "date";
  if (type === "number") return "number";
  if (type === "money") return "money";
  if (type === "location") return "location";
  if (type === "text" || type === "timeline" || type === "people") return "text";
  return "single_select";
}

export function templateSectionToSetupField(section: SetupSection): PersonalSetupField {
  const options: PersonalSetupOption[] = section.options.map((o) => ({
    value: o.value,
    label: o.label,
    description: o.description ?? null,
    bar_level: o.bar_level ?? null,
    accent: o.accent ?? null,
  }));
  return {
    field_key: section.field_key,
    label: section.title,
    helper_text: section.subtitle ?? null,
    field_type: sectionTypeToFieldType(section.type),
    options,
    required: section.required,
  };
}

function personalBackendMapping(
  momentTypeCode: string,
  payloadKeys: string[],
): SetupBackendMapping {
  const setupPath = "api/v1/personal/moments/{momentId}/setup";
  return {
    moment_type_code: momentTypeCode,
    createDraft: {
      method: "POST",
      path: "api/v1/personal/moments",
      bodyKeys: ["moment_type_code"],
    },
    saveDraft: { method: "PUT", path: `${setupPath}/draft`, bodyKeys: ["answers"] },
    preview: { method: "POST", path: `${setupPath}/preview`, bodyKeys: ["answers"] },
    activate: { method: "POST", path: setupPath, bodyKeys: ["answers"] },
    payloadKeys: [...payloadKeys, "template_id", "template_version"],
  };
}

export function personalTemplateBase(
  templateId: string,
  momentTypeCode: string,
  title: string,
  subtitle: string,
  hero: SetupHero,
  sections: SetupSection[],
  activationCta: SetupActivationCta,
  identityCard: SetupIdentityCard,
): MomentSetupTemplate {
  const payloadKeys = sections.map((s) => s.field_key);
  return {
    template_id: templateId,
    template_version: 1,
    context: "MY_MONEY",
    title,
    subtitle,
    hero,
    sections,
    preview_cards: [
      { card_id: "runtime", title: "Runtime Simulation" },
      { card_id: "identity", title: identityCard.title },
    ],
    identity_card: identityCard,
    projection_card: { title: "Intelligence Profile" },
    activation_cta: activationCta,
    backend_mapping: personalBackendMapping(momentTypeCode, payloadKeys),
    quick_add_modules: [],
    active_dashboard: { screen: "pulse" },
  };
}
