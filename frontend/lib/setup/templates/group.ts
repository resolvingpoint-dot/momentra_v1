import {
  groupCurrencyOptions,
  option,
  type MomentSetupTemplate,
  type SetupBackendMapping,
  type SetupSection,
} from "./types";

function groupBackendMapping(
  momentTypeCode: string,
  category: "experience" | "purchase" | "living",
  payloadKeys: string[],
  createBodyKey: string,
): SetupBackendMapping {
  const base = `api/v1/group/shared-${category}`;
  const setupPath = `${base}/moments/{momentId}/setup`;
  return {
    moment_type_code: momentTypeCode,
    createDraft: {
      method: "POST",
      path: `${base}/moments`,
      bodyKeys: [createBodyKey],
    },
    saveDraft: { method: "PUT", path: `${setupPath}/draft`, bodyKeys: ["answers"] },
    preview: { method: "GET", path: `${setupPath}/preview`, bodyKeys: [] },
    activate: { method: "POST", path: `${setupPath}/activate`, bodyKeys: [] },
    payloadKeys: [...payloadKeys, "template_id", "template_version"],
  };
}

function groupTemplate(
  templateId: string,
  momentTypeCode: string,
  category: "experience" | "purchase" | "living",
  createBodyKey: string,
  title: string,
  subtitle: string,
  badgeLabel: string,
  sections: SetupSection[],
  ctaLabel: string,
): MomentSetupTemplate {
  const payloadKeys = sections.map((s) => s.field_key);
  return {
    template_id: templateId,
    template_version: 1,
    context: "GROUP",
    title,
    subtitle,
    hero: { badge_label: badgeLabel, title, body: subtitle },
    sections,
    preview_cards: [{ card_id: "preview", title: "Setup Preview" }],
    identity_card: { title: "Group Profile", badge_label: "Preview" },
    projection_card: { title: "Coordination Summary" },
    activation_cta: { label: ctaLabel, footer_note: "You can refine details after activation" },
    backend_mapping: groupBackendMapping(momentTypeCode, category, payloadKeys, createBodyKey),
    quick_add_modules: [],
    active_dashboard: { screen: "pulse" },
  };
}

/** Product field keys; backend aliases: experience_type→experience_profile, experience_name→moment_name. */
const tripSections: SetupSection[] = [
  {
    section_id: "experience_type",
    title: "Shared Experience Type",
    type: "card_grid",
    field_key: "experience_type",
    options: [
      option("TRIP_VACATION", "Trip / Vacation"),
      option("WEDDING", "Wedding"),
      option("CELEBRATION", "Celebration"),
      option("OFFICE_OUTING", "Office Outing"),
    ],
    required: true,
  },
  {
    section_id: "experience_name",
    title: "Shared Experience Name",
    type: "text",
    field_key: "experience_name",
    options: [],
    required: true,
  },
  {
    section_id: "destination",
    title: "Destination",
    type: "location",
    field_key: "destination",
    options: [],
    required: false,
  },
  {
    section_id: "start_date",
    title: "Start date",
    type: "date",
    field_key: "start_date",
    options: [],
    required: false,
  },
  {
    section_id: "end_date",
    title: "End date",
    type: "date",
    field_key: "end_date",
    options: [],
    required: false,
  },
  {
    section_id: "participants",
    title: "Participants",
    type: "number",
    field_key: "participants",
    options: [],
    required: false,
  },
  {
    section_id: "budget_currency",
    title: "Default currency",
    type: "single_choice",
    field_key: "budget_currency",
    options: groupCurrencyOptions(),
    required: false,
  },
  {
    section_id: "allow_multi_currency",
    title: "Allow multi-currency expenses",
    type: "single_choice",
    field_key: "allow_multi_currency",
    options: [
      option("true", "Yes — members can log expenses in other currencies"),
      option("false", "No — lock to default currency"),
    ],
    required: false,
    default_value: "true",
  },
  {
    section_id: "estimated_budget",
    title: "Estimated budget",
    type: "money",
    field_key: "estimated_budget",
    options: [],
    required: false,
  },
  {
    section_id: "split_style",
    title: "How will you handle money?",
    type: "single_choice",
    field_key: "split_style",
    options: [
      option("NO_MONEY", "Plan only — track money later"),
      option("SPLIT_LATER", "Split expenses as you go"),
      option("SHARED_POOL", "Shared pool / kitty"),
    ],
    required: true,
  },
];

export const groupTripTemplate = groupTemplate(
  "group_trip",
  "SHARED_EXPERIENCE",
  "experience",
  "experience_profile",
  "Shared Experience Setup",
  "Create a shared moment for trips, weddings, celebrations, outings, and more.",
  "SHARED EXPERIENCE",
  tripSections,
  "Activate Shared Experience",
);

const purchaseSections: SetupSection[] = [
  {
    section_id: "purchase_profile",
    title: "Purchase type",
    type: "card_grid",
    field_key: "purchase_profile",
    options: [
      option("GIFT_POOL", "Gift Pool"),
      option("GROUP_PURCHASE", "Group Purchase"),
      option("SHARED_ASSET", "Shared Asset"),
      option("CUSTOM_PURCHASE", "Custom Purchase"),
    ],
    required: true,
  },
  {
    section_id: "purchase_name",
    title: "Purchase name",
    type: "text",
    field_key: "purchase_name",
    options: [],
    required: true,
  },
  {
    section_id: "item_or_goal",
    title: "Item or goal",
    type: "text",
    field_key: "item_or_goal",
    options: [],
    required: false,
  },
  {
    section_id: "expected_amount",
    title: "Expected amount",
    type: "money",
    field_key: "expected_amount",
    options: [],
    required: true,
  },
  {
    section_id: "currency_code",
    title: "Default currency",
    type: "single_choice",
    field_key: "currency_code",
    options: groupCurrencyOptions(),
    required: true,
  },
  {
    section_id: "allow_multi_currency",
    title: "Allow multi-currency expenses",
    type: "single_choice",
    field_key: "allow_multi_currency",
    options: [
      option("true", "Yes — members can log expenses in other currencies"),
      option("false", "No — lock to default currency"),
    ],
    required: false,
    default_value: "true",
  },
  {
    section_id: "contributors",
    title: "Contributors",
    type: "number",
    field_key: "contributors",
    options: [],
    required: false,
  },
  {
    section_id: "ownership_style",
    title: "Ownership style",
    type: "single_choice",
    field_key: "ownership_style",
    options: [
      option("SHARED", "Shared"),
      option("EQUAL", "Equal"),
      option("CUSTOM", "Custom"),
    ],
    required: false,
  },
  {
    section_id: "payment_plan",
    title: "Payment plan",
    type: "single_choice",
    field_key: "payment_plan",
    options: [
      option("SUGGESTED", "Suggested amounts"),
      option("EQUAL", "Equal split"),
      option("OPEN", "Open contributions"),
    ],
    required: true,
  },
  {
    section_id: "decision_deadline",
    title: "Decision deadline",
    type: "date",
    field_key: "decision_deadline",
    options: [],
    required: false,
  },
];

export const groupPurchaseTemplate = groupTemplate(
  "group_purchase",
  "SHARED_PURCHASE",
  "purchase",
  "purchase_profile",
  "Shared Purchase Setup",
  "Plan a purchase your group is funding together.",
  "SHARED PURCHASE",
  purchaseSections,
  "Activate Purchase",
);

const colivingSections: SetupSection[] = [
  {
    section_id: "living_type",
    title: "Living type",
    type: "card_grid",
    field_key: "living_type",
    options: [
      option("FLATMATES", "Flatmates"),
      option("FAMILY_HOUSEHOLD", "Family Household"),
      option("COLIVING", "Co-Living"),
      option("CUSTOM_LIVING", "Custom Living"),
    ],
    required: true,
  },
  {
    section_id: "home_name",
    title: "Home name",
    type: "text",
    field_key: "home_name",
    options: [],
    required: true,
  },
  {
    section_id: "members",
    title: "Members",
    type: "number",
    field_key: "members",
    options: [],
    required: false,
  },
  {
    section_id: "monthly_budget",
    title: "Monthly budget",
    type: "money",
    field_key: "monthly_budget",
    options: [],
    required: false,
  },
  {
    section_id: "currency_code",
    title: "Default currency",
    type: "single_choice",
    field_key: "currency_code",
    options: groupCurrencyOptions(),
    required: false,
  },
  {
    section_id: "allow_multi_currency",
    title: "Allow multi-currency expenses",
    type: "single_choice",
    field_key: "allow_multi_currency",
    options: [
      option("true", "Yes — members can log expenses in other currencies"),
      option("false", "No — lock to default currency"),
    ],
    required: false,
    default_value: "true",
  },
  {
    section_id: "rent_split_style",
    title: "Rent split style",
    type: "single_choice",
    field_key: "rent_split_style",
    options: [
      option("SHARED", "Shared equally"),
      option("LEAD", "Lead-managed"),
      option("ROTATION", "Rotating"),
    ],
    required: true,
  },
  {
    section_id: "chores_style",
    title: "Chores style",
    type: "single_choice",
    field_key: "chores_style",
    options: [
      option("SHARED", "Shared"),
      option("ROTATION", "Rotation"),
      option("ASSIGNED", "Assigned"),
    ],
    required: false,
  },
  {
    section_id: "rules_or_notes",
    title: "Rules or notes",
    type: "text",
    field_key: "rules_or_notes",
    options: [],
    required: false,
  },
];

export const groupColivingTemplate = groupTemplate(
  "group_coliving",
  "SHARED_LIVING",
  "living",
  "living_type",
  "Shared Living Setup",
  "Set up how your group will live together.",
  "SHARED LIVING",
  colivingSections,
  "Activate Home",
);

export const GROUP_TEMPLATES = [groupTripTemplate, groupPurchaseTemplate, groupColivingTemplate];

export const GROUP_DEFAULT_PROFILES: Record<string, string> = {
  SHARED_EXPERIENCE: "TRIP_VACATION",
  SHARED_PURCHASE: "GIFT_POOL",
  SHARED_LIVING: "FLATMATES",
};

export const GROUP_MOMENT_TYPES = new Set([
  "SHARED_EXPERIENCE",
  "SHARED_PURCHASE",
  "SHARED_LIVING",
]);

export function groupCategoryForType(
  momentTypeCode: string,
): "experience" | "purchase" | "living" | null {
  if (momentTypeCode === "SHARED_EXPERIENCE") return "experience";
  if (momentTypeCode === "SHARED_PURCHASE") return "purchase";
  if (momentTypeCode === "SHARED_LIVING") return "living";
  return null;
}
