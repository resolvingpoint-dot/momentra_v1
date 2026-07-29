import type { PersonalMomentTypeCode } from "@/lib/personal/personalMomentSession";

export type TemplateActivityFilter = string;

export type TemplateActivityItem = {
  id: string;
  activity_type: string;
  title: string;
  subtitle: string;
  occurred_at: string;
  amount_minor: number;
  amount_label?: string | null;
  currency_code?: string;
  category_code?: string | null;
  subcategory_code?: string | null;
  category_label?: string | null;
  subcategory_label?: string | null;
  mood_label?: string | null;
  mood?: {
    code?: string | null;
    label?: string | null;
    intensity?: string | null;
    source?: string | null;
  } | null;
  domain_label?: string | null;
  type_label?: string | null;
  domain_type_subtitle?: string | null;
  primary_metric?: {
    kind?: string | null;
    display?: string | null;
    amount_minor?: number | null;
    currency_code?: string | null;
  } | null;
  chips?: Array<{ code?: string | null; label?: string | null }> | null;
  icon?: string | null;
  color?: string | null;
  impact_label?: string | null;
  impact_direction?: string | null;
  relative_time?: string | null;
  edit_event_type: string;
  can_edit: boolean;
  can_delete: boolean;
  editable?: boolean;
};

export type TemplateActivitySummary = {
  total_logs: number;
  this_month: number;
  total_amount_minor: number;
};

export type TemplateActivityListResponse = {
  items: TemplateActivityItem[];
  summary?: TemplateActivitySummary;
  filters?: TemplateActivityFilter[];
};

export type UnifiedActivitySnapshot = {
  headline: string;
  today_activity_count: number;
  today_amount_minor: number;
  today_mood_label?: string | null;
  today_domain_labels?: string[];
};

export type UnifiedActivityInsight = {
  id: string;
  kind: string;
  title: string;
  value: string;
};

export type UnifiedPersonalActivityItem = TemplateActivityItem & {
  moment_id?: string;
  moment_type_code?: string;
  life_domain?: string | null;
  raw_payload?: Record<string, unknown>;
};

export type UnifiedPersonalActivityResponse = {
  snapshot: UnifiedActivitySnapshot;
  insights: UnifiedActivityInsight[];
  items: UnifiedPersonalActivityItem[];
  next_cursor?: string | null;
};

export type TemplateActivityEditField = {
  key: string;
  label: string;
  field_type: string;
  required?: boolean;
  path?: string;
  options?: Array<{ value: string; label: string }>;
};

export type TemplateActivityEditSchema = {
  event_type: string;
  fields: TemplateActivityEditField[];
  allowed_actions?: string[];
};

export type TemplateActivityDetail = {
  id?: string;
  quick_add_event_id?: string;
  moment_id?: string;
  event_type?: string;
  event_title?: string;
  event_summary?: string | null;
  edit_schema?: TemplateActivityEditSchema;
  values?: Record<string, unknown>;
  expense?: Record<string, unknown> | null;
  future_building?: Record<string, unknown> | null;
  [key: string]: unknown;
};

export type TemplateActivityAdapter = {
  momentTypeCode: PersonalMomentTypeCode;
  screenTitle: string;
  screenSubtitle: string;
  searchPlaceholder: string;
  emptyMessage: string;
  editTitle: string;
  editSubtitle: string;
  saveChanges: string;
  cancel: string;
  deleteLabel: string;
  deleteConfirm: string;
  filters: Array<{ id: TemplateActivityFilter; label: string }>;
  filterMatches: (filterId: TemplateActivityFilter, activityType: string) => boolean;
  formatAmount: (minor: number) => string;
  groupToday: string;
  groupYesterday: string;
  groupThisWeek: string;
  groupEarlier: string;
};
