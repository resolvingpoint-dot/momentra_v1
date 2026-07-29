import { buildBundle, field, personalEndpoint, type ActionDef } from "../builders";
import type { QuickAddTemplateBundle } from "../types";

const TEMPLATE_ID = "personal.relationships";
const CONTEXT = "EMOTIONAL_SECURITY" as const;
const MODULES = ["pulse", "live", "memory", "moments"];

/** v1 hub exposes 5 actions; backend supports full handler mapping for future expansion. */
const actions: ActionDef[] = [
  {
    action_id: "CONNECTION",
    reusable_type: "update",
    label: "Conversation",
    icon: "group",
    display_order: 1,
    cta_label: "Log Conversation",
    fields: [
      field("connection_type", "Connection type", "single_select", { required: true }),
      field("relationship_type", "Relationship type", "single_select"),
      field("connection_quality", "Connection quality", "chip_grid"),
      field("emotional_tone", "Emotional tone", "chip_grid"),
      field("time_invested", "Time invested", "text"),
    ],
    validation: { required_fields: ["connection_type"] },
    impact_preview: { modules: MODULES, summary_template: "Logs {connection_type} conversation" },
    backend_endpoint: personalEndpoint("POST /api/v1/personal/live/quick-add"),
    output_event: { event_type: "CONNECTION", ref_table: "personal_quick_add_events" },
    affects_modules: MODULES,
  },
  {
    action_id: "SUPPORT",
    reusable_type: "update",
    label: "Support",
    icon: "volunteer_activism",
    display_order: 2,
    cta_label: "Log Support",
    fields: [
      field("support_type", "Support type", "single_select", { required: true }),
      field("support_direction", "Direction", "single_select", { required: true }),
      field("support_impact", "Impact", "chip_grid"),
      field("notes", "Notes", "textarea"),
    ],
    validation: { required_fields: ["support_type", "support_direction"] },
    impact_preview: { modules: MODULES, summary_template: "Logs {support_type} support" },
    backend_endpoint: personalEndpoint("POST /api/v1/personal/live/quick-add"),
    output_event: { event_type: "SUPPORT", ref_table: "personal_quick_add_events" },
    affects_modules: MODULES,
  },
  {
    action_id: "SHARED_EXPERIENCE",
    reusable_type: "expense",
    label: "Shared Experience",
    icon: "favorite",
    display_order: 3,
    cta_label: "Save Experience",
    fields: [
      field("amount", "Amount", "amount"),
      field("spend_category", "Category", "chip_grid"),
      field("experience_type", "Experience type", "single_select", { required: true }),
      field("value_received", "Value received", "text"),
      field("notes", "Notes", "textarea", { required: true }),
    ],
    validation: { required_fields: ["experience_type", "notes"] },
    impact_preview: {
      modules: MODULES,
      summary_template: "Logs shared experience: {experience_type}",
    },
    backend_endpoint: personalEndpoint("POST /api/v1/personal/live/quick-add"),
    output_event: {
      event_type: "SHARED_EXPERIENCE",
      ref_table: "personal_quick_add_events",
      fan_out: [
        { event_type: "EXPENSE_FANOUT", ref_table: "personal_quick_add_events" },
        { event_type: "MEMORY_FANOUT", ref_table: "personal_quick_add_events" },
      ],
    },
    affects_modules: MODULES,
  },
  {
    action_id: "RELATIONSHIP_INVESTMENT",
    reusable_type: "contribution",
    label: "Gift",
    icon: "card_giftcard",
    display_order: 4,
    cta_label: "Log Gift",
    fields: [
      field("investment_type", "Gift type", "single_select", { required: true }),
      field("investment_purpose", "Purpose", "text"),
      field("perceived_value", "Perceived value", "chip_grid"),
      field("amount", "Amount", "amount"),
      field("notes", "Notes", "textarea"),
    ],
    validation: { required_fields: ["investment_type"] },
    impact_preview: { modules: MODULES, summary_template: "Logs {investment_type} gift" },
    backend_endpoint: personalEndpoint("POST /api/v1/personal/live/quick-add"),
    output_event: { event_type: "RELATIONSHIP_INVESTMENT", ref_table: "personal_quick_add_events" },
    affects_modules: MODULES,
  },
  {
    action_id: "ADJUST",
    reusable_type: "update",
    label: "Reflection",
    icon: "psychology",
    display_order: 5,
    cta_label: "Save Reflection",
    fields: [
      field("adjustment_area", "Reflection area", "single_select", { required: true }),
      field("relationship_focus", "Focus", "text"),
      field("priority_level", "Priority", "chip_grid"),
      field("confidence_level", "Confidence", "chip_grid"),
      field("notes", "Notes", "textarea", { required: true }),
    ],
    validation: { required_fields: ["adjustment_area", "notes"] },
    impact_preview: { modules: MODULES, summary_template: "Reflects on: {adjustment_area}" },
    backend_endpoint: personalEndpoint("POST /api/v1/personal/live/quick-add"),
    output_event: { event_type: "ADJUST", ref_table: "personal_quick_add_events" },
    affects_modules: MODULES,
  },
];

export const RELATIONSHIPS_QUICK_ADD: QuickAddTemplateBundle = buildBundle(
  TEMPLATE_ID,
  CONTEXT,
  "tabbed_hub",
  actions,
  { default_action_id: "CONNECTION" },
);
