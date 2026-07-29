import { buildBundle, field, personalEndpoint, type ActionDef } from "../builders";
import type { QuickAddTemplateBundle } from "../types";

const TEMPLATE_ID = "personal.life_operations";
const CONTEXT = "LIFE_OPERATIONS" as const;
const MODULES = ["pulse", "live", "memory", "life"];

const actions: ActionDef[] = [
  {
    action_id: "EXPENSE",
    reusable_type: "expense",
    label: "Money",
    icon: "payments",
    tab_code: "MONEY",
    display_order: 1,
    cta_label: "Save Expense",
    fields: [
      field("transaction_type", "Entry type", "segmented", {
        options: [
          { value: "EXPENSE", label: "Expense" },
          { value: "INCOME", label: "Income" },
          { value: "TRANSFER", label: "Transfer" },
          { value: "CONTRIBUTION", label: "Contribution" },
          { value: "SAVINGS", label: "Savings" },
          { value: "INVESTMENT", label: "Investment" },
        ],
      }),
      field("amount", "Amount", "amount", { required: true }),
      field("account_id", "Account", "account_picker", { required: true }),
      field("category_name", "Category", "text", { options_ref: "reference_data.expense_categories" }),
      field("pressure_impact", "Financial impact", "chip_grid", {
        options_ref: "metadata.pressure_impact_chips",
      }),
      field("description", "Notes", "textarea"),
    ],
    validation: { required_fields: ["amount", "account_id"] },
    impact_preview: {
      modules: MODULES,
      summary_template: "Records {transaction_type} of {amount} in {category_name}",
    },
    backend_endpoint: personalEndpoint("POST /api/v1/personal/live/quick-add"),
    output_event: { event_type: "EXPENSE", ref_table: "personal_quick_add_events" },
    affects_modules: MODULES,
  },
  {
    action_id: "COMMITMENT",
    reusable_type: "task",
    label: "Attention",
    icon: "task_alt",
    tab_code: "ATTENTION",
    display_order: 2,
    cta_label: "Log Attention State",
    fields: [
      field("commitment_name", "Attention name", "text", { required: true }),
      field("commitment_type", "Attention type", "segmented", {
        options_ref: "metadata.commitment_types",
      }),
      field("focus_area", "Focus area", "chip_grid", {
        options_ref: "metadata.attention_focus_areas",
      }),
      field("intensity", "Intensity", "single_select", { options_ref: "metadata.intensity_options" }),
      field("commitment_status", "Status", "segmented", {
        options_ref: "metadata.commitment_status_options",
      }),
    ],
    validation: { required_fields: ["commitment_name", "commitment_type", "commitment_status"] },
    impact_preview: {
      modules: MODULES,
      summary_template: "Logs attention on {commitment_name}",
    },
    backend_endpoint: personalEndpoint("POST /api/v1/personal/live/quick-add"),
    output_event: { event_type: "COMMITMENT", ref_table: "personal_quick_add_events" },
    affects_modules: MODULES,
  },
  {
    action_id: "RECOVERY",
    reusable_type: "recovery",
    label: "Recovery",
    icon: "self_improvement",
    tab_code: "RECOVERY",
    display_order: 3,
    cta_label: "Log Recovery",
    fields: [
      field("recovery_type", "Recovery type", "chip_grid", {
        required: true,
        options_ref: "metadata.recovery_types",
      }),
      field("duration_minutes", "Duration", "single_select", {
        options_ref: "metadata.recovery_duration_options",
      }),
      field("recovery_intensity", "Energy level", "segmented", {
        options_ref: "metadata.energy_impact_options",
      }),
      field("notes", "Notes", "textarea"),
    ],
    validation: { required_fields: ["recovery_type"] },
    impact_preview: {
      modules: MODULES,
      summary_template: "Logs {recovery_type} recovery",
    },
    backend_endpoint: personalEndpoint("POST /api/v1/personal/live/quick-add"),
    output_event: {
      event_type: "RECOVERY",
      ref_table: "personal_quick_add_events",
      fan_out: [{ event_type: "RECOVERY_CHILD", ref_table: "personal_life_recovery_events" }],
    },
    affects_modules: MODULES,
  },
  {
    action_id: "REFLECTION",
    reusable_type: "mood",
    label: "Mood",
    icon: "mood",
    tab_code: "MOOD",
    display_order: 4,
    cta_label: "Save Mood",
    fields: [
      field("feeling_state", "Mood", "icon_grid", {
        required: true,
        options_ref: "metadata.mood_feeling_options",
      }),
      field("reflection_tag", "Reflection tags", "chip_grid", {
        options_ref: "metadata.reflection_tags",
      }),
      field("reflection_note", "Notes", "textarea"),
    ],
    validation: { required_fields: ["feeling_state"] },
    impact_preview: {
      modules: MODULES,
      summary_template: "Captures mood: {feeling_state}",
    },
    backend_endpoint: personalEndpoint("POST /api/v1/personal/live/quick-add"),
    output_event: {
      event_type: "REFLECTION",
      ref_table: "personal_quick_add_events",
      fan_out: [{ event_type: "MOOD_CHILD", ref_table: "personal_life_mood_events" }],
    },
    affects_modules: MODULES,
  },
  {
    action_id: "RHYTHM",
    reusable_type: "update",
    label: "Adjust",
    icon: "tune",
    tab_code: "ADJUST",
    display_order: 5,
    cta_label: "Update Rhythm",
    fields: [
      field("rhythm_actions", "Rhythm actions", "chip_grid", {
        options_ref: "metadata.rhythm_actions",
      }),
      field("runtime_signals", "Runtime signals", "runtime_signals", {
        options_ref: "metadata.runtime_signal_dimensions",
      }),
      field("new_runtime_mode", "Runtime mode", "chip_grid", {
        required: true,
        options_ref: "metadata.runtime_modes",
      }),
      field("new_runtime_priority", "Runtime priority", "chip_grid", {
        required: true,
        options_ref: "metadata.runtime_priorities",
      }),
    ],
    validation: { required_fields: ["new_runtime_mode", "new_runtime_priority"] },
    impact_preview: {
      modules: MODULES,
      summary_template: "Updates rhythm mode to {new_runtime_mode}",
    },
    backend_endpoint: personalEndpoint("POST /api/v1/personal/live/quick-add"),
    output_event: { event_type: "RHYTHM", ref_table: "personal_quick_add_events" },
    affects_modules: MODULES,
  },
];

const addAccountSubFlow: ActionDef = {
  action_id: "ADD_ACCOUNT",
  reusable_type: "expense",
  label: "Add Account",
  icon: "account_balance",
  display_order: 0,
  cta_label: "Save Account",
  fields: [
    field("account_name", "Account name", "text", { required: true }),
    field("account_type", "Account type", "single_select"),
    field("currency_code", "Currency", "text", { required: true }),
    field("opening_balance", "Opening balance", "amount"),
    field("is_primary", "Primary account", "toggle"),
  ],
  validation: { required_fields: ["account_name", "currency_code"] },
  impact_preview: {
    modules: ["pulse", "live"],
    summary_template: "Adds account {account_name}",
  },
  backend_endpoint: personalEndpoint("POST /api/v1/personal/accounts"),
  output_event: { event_type: "ACCOUNT_CREATED" },
  affects_modules: ["pulse", "live"],
};

export const LIFE_OPERATIONS_QUICK_ADD: QuickAddTemplateBundle = buildBundle(
  TEMPLATE_ID,
  CONTEXT,
  "tabbed_hub",
  actions,
  { default_action_id: "EXPENSE", sub_flows: [addAccountSubFlow] },
);
