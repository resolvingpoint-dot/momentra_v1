import { option, type MomentSetupTemplate, type SetupBackendMapping, type SetupSection } from "./types";

function businessBackendMapping(
  momentTypeCode: string,
  payloadKeys: string[],
): SetupBackendMapping {
  const setupPath = "api/v1/business/moments/{momentId}/setup";
  return {
    moment_type_code: momentTypeCode,
    createDraft: {
      method: "POST",
      path: "api/v1/business/moments",
      bodyKeys: ["moment_type_code", "title", "template_id", "template_version"],
    },
    saveDraft: {
      method: "PUT",
      path: `${setupPath}/draft`,
      bodyKeys: ["answers", "progress", "template_id", "template_version", "setup_version"],
    },
    preview: {
      method: "POST",
      path: `${setupPath}/preview`,
      bodyKeys: ["answers"],
    },
    activate: {
      method: "POST",
      path: `${setupPath}/activate`,
      bodyKeys: [],
    },
    payloadKeys: [...payloadKeys, "template_id", "template_version"],
  };
}

function businessTemplate(
  templateId: string,
  momentTypeCode: string,
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
    context: "BUSINESS",
    title,
    subtitle,
    hero: { badge_label: badgeLabel, title, body: subtitle },
    sections,
    preview_cards: [{ card_id: "workspace", title: "Workspace Preview" }],
    identity_card: { title: "Operating Profile", badge_label: "Preview" },
    projection_card: { title: "Operational Summary" },
    activation_cta: { label: ctaLabel, footer_note: "You can refine workspace settings after activation" },
    backend_mapping: businessBackendMapping(momentTypeCode, payloadKeys),
    quick_add_modules: [],
    active_dashboard: { screen: "pulse" },
  };
}

const teamOpsSections: SetupSection[] = [
  {
    section_id: "purpose",
    title: "Team purpose",
    type: "text",
    field_key: "team_purpose",
    options: [],
    required: true,
  },
  {
    section_id: "team_size",
    title: "Team size",
    type: "single_choice",
    field_key: "team_size",
    options: [
      option("SOLO", "Just Me"),
      option("SMALL", "2–5"),
      option("MEDIUM", "6–15"),
      option("LARGE", "16–50"),
      option("XLARGE", "50+"),
    ],
    required: true,
  },
  {
    section_id: "work_style",
    title: "Work style",
    type: "single_choice",
    field_key: "work_style",
    options: [
      option("REMOTE", "Remote"),
      option("HYBRID", "Hybrid"),
      option("IN_PERSON", "In Person"),
    ],
    required: true,
  },
  {
    section_id: "visibility",
    title: "Visibility",
    type: "single_choice",
    field_key: "visibility",
    options: [
      option("PRIVATE", "Private"),
      option("TEAM", "Team Only"),
      option("ORG", "Organization"),
    ],
    required: true,
  },
];

export const teamOpsTemplate = businessTemplate(
  "team_ops",
  "TEAM_OPERATIONS",
  "Team Operations Setup",
  "Configure how your team operates day to day.",
  "TEAM OPERATIONS",
  teamOpsSections,
  "Activate Team Operations",
);

const runwaySections: SetupSection[] = [
  {
    section_id: "runway_horizon",
    title: "Runway horizon",
    type: "single_choice",
    field_key: "runway_horizon",
    options: [
      option("3_MONTHS", "3 Months"),
      option("6_MONTHS", "6 Months"),
      option("12_MONTHS", "12 Months"),
      option("18_MONTHS", "18+ Months"),
    ],
    required: true,
  },
  {
    section_id: "cash_target",
    title: "Cash target",
    type: "money",
    field_key: "cash_target",
    options: [],
    required: false,
  },
  {
    section_id: "risk_tolerance",
    title: "Risk tolerance",
    type: "single_choice",
    field_key: "risk_tolerance",
    options: [
      option("CONSERVATIVE", "Conservative"),
      option("BALANCED", "Balanced"),
      option("AGGRESSIVE", "Aggressive"),
    ],
    required: true,
  },
  {
    section_id: "burn_tracking",
    title: "Track burn rate",
    type: "single_choice",
    field_key: "burn_tracking",
    options: [
      option("YES", "Yes"),
      option("NO", "No"),
    ],
    required: true,
  },
];

export const businessRunwayTemplate = businessTemplate(
  "business_runway",
  "BUSINESS_RUNWAY",
  "Business Runway Setup",
  "Configure your financial runway and risk posture.",
  "BUSINESS RUNWAY",
  runwaySections,
  "Activate Runway",
);

const businessOpsSections: SetupSection[] = [
  {
    section_id: "ops_focus",
    title: "Operations focus",
    type: "single_choice",
    field_key: "ops_focus",
    options: [
      option("SPEND", "Spend Management"),
      option("VENDORS", "Vendor Management"),
      option("APPROVALS", "Approvals"),
      option("IMPROVEMENTS", "Process Improvements"),
    ],
    required: true,
  },
  {
    section_id: "approval_flow",
    title: "Approval flow",
    type: "single_choice",
    field_key: "approval_flow",
    options: [
      option("SIMPLE", "Simple"),
      option("TIERED", "Tiered"),
      option("STRICT", "Strict"),
    ],
    required: true,
  },
  {
    section_id: "spend_categories",
    title: "Spend categories",
    type: "multi_choice",
    field_key: "spend_categories",
    options: [
      option("SOFTWARE", "Software"),
      option("MARKETING", "Marketing"),
      option("OPERATIONS", "Operations"),
      option("PEOPLE", "People"),
      option("OTHER", "Other"),
    ],
    required: true,
    min_selected: 1,
  },
  {
    section_id: "budget_enabled",
    title: "Enable budgets",
    type: "single_choice",
    field_key: "budget_enabled",
    options: [
      option("YES", "Yes"),
      option("NO", "No"),
    ],
    required: true,
  },
];

export const businessOperationsTemplate = businessTemplate(
  "business_operations",
  "BUSINESS_OPERATIONS",
  "Business Operations Setup",
  "Configure how operational work flows through your business.",
  "BUSINESS OPERATIONS",
  businessOpsSections,
  "Activate Operations",
);

export const BUSINESS_TEMPLATES = [
  teamOpsTemplate,
  businessRunwayTemplate,
  businessOperationsTemplate,
];
