export type QuickAddContext =
  | "LIFE_OPERATIONS"
  | "FUTURE_BUILDING"
  | "LIFESTYLE"
  | "EMOTIONAL_SECURITY"
  | "SHARED_EXPERIENCE"
  | "SHARED_PURCHASE"
  | "SHARED_LIVING"
  | "team_operations"
  | "business_runway"
  | "business_operations";

export type QuickAddShell = "tabbed_hub" | "sectioned_hub" | "sub_flow";

export type ReusableActionType =
  | "expense"
  | "mood"
  | "recovery"
  | "task"
  | "update"
  | "milestone"
  | "participant"
  | "contribution"
  | "booking"
  | "risk"
  | "decision"
  | "memory";

export type QuickAddFieldType =
  | "amount"
  | "text"
  | "textarea"
  | "single_select"
  | "multi_select"
  | "segmented"
  | "chip_grid"
  | "icon_grid"
  | "date"
  | "toggle"
  | "account_picker"
  | "member_picker"
  | "media_upload"
  | "runtime_signals";

export interface QuickAddFieldOption {
  value: string;
  label: string;
  icon?: string;
}

export interface QuickAddField {
  key: string;
  label: string;
  field_type: QuickAddFieldType;
  required?: boolean;
  options_ref?: string;
  options?: QuickAddFieldOption[];
  visible_when?: { field: string; equals: string };
}

export interface QuickAddValidation {
  required_fields: string[];
  min_length?: Record<string, number>;
  custom_rule?: string;
}

export interface QuickAddImpactPreview {
  modules: string[];
  summary_template: string;
  teaches_items?: string[];
  insight?: { title: string; body: string };
}

export interface QuickAddBackendEndpoint {
  context_get?: string;
  create_post: string;
  method?: "POST" | "PUT";
}

export interface QuickAddOutputEvent {
  event_type: string;
  ref_table?: string;
  ref_id_field?: string;
  fan_out?: QuickAddOutputEvent[];
}

export interface QuickAddActionTemplate {
  template_id: string;
  context: QuickAddContext;
  action_id: string;
  reusable_type: ReusableActionType;
  label: string;
  icon: string;
  shell: QuickAddShell;
  section?: string;
  tab_code?: string;
  display_order: number;
  cta_label: string;
  fields: QuickAddField[];
  validation: QuickAddValidation;
  impact_preview: QuickAddImpactPreview;
  backend_endpoint: QuickAddBackendEndpoint;
  output_event: QuickAddOutputEvent;
  affects_modules: string[];
  /** Action Center metadata (optional — enriched for Group) */
  subtitle?: string;
  category?: ActionCenterCategory;
  accent?: string;
  priority?: number;
  estimated_time_sec?: number;
  tags?: string[];
  synonyms?: string[];
  renderer_id?: string;
  analytics_id?: string;
  supports?: ActionCapabilities;
}

export type ActionCenterCategory =
  | "money"
  | "planning"
  | "people"
  | "capture"
  | "administration"
  | "support";

export type ActionCapabilities = {
  create?: boolean;
  edit?: boolean;
  delete?: boolean;
  archive?: boolean;
  duplicate?: boolean;
  share?: boolean;
  affects_money?: boolean;
  affects_memory?: boolean;
  affects_life?: boolean;
  affects_settlement?: boolean;
  drafts?: boolean;
  favorites?: boolean;
  search?: boolean;
  attachments?: boolean;
  participants?: boolean;
  location?: boolean;
  offline?: boolean;
  notifications?: boolean;
  approval?: boolean;
  settlement?: boolean;
};

export interface QuickAddTemplateBundle {
  template_id: string;
  context: QuickAddContext;
  shell: QuickAddShell;
  default_action_id?: string;
  actions: QuickAddActionTemplate[];
  sub_flows?: QuickAddActionTemplate[];
}

export type QuickAddAffectedModule =
  | "pulse"
  | "live"
  | "memory"
  | "moments"
  | "operations_hub"
  | "budget"
  | "runway"
  | "life";

export const REUSABLE_ACTION_TYPES: ReusableActionType[] = [
  "expense",
  "mood",
  "recovery",
  "task",
  "update",
  "milestone",
  "participant",
  "contribution",
  "booking",
  "risk",
  "decision",
  "memory",
];

export const QUICK_ADD_FIELD_TYPES: QuickAddFieldType[] = [
  "amount",
  "text",
  "textarea",
  "single_select",
  "multi_select",
  "segmented",
  "chip_grid",
  "icon_grid",
  "date",
  "toggle",
  "account_picker",
  "member_picker",
  "media_upload",
  "runtime_signals",
];
