import type { QuickAddActionTemplate } from "../types";
import { getQuickAddAction } from "../registry";
import { buildSharedPollPayload } from "./sharedPoll";

export type TemplateQuickAddFormState = Record<string, string | string[] | number | boolean>;

type TemplateId = "group.purchase" | "group.living";

export function defaultTemplateFormState(templateId: TemplateId, actionId: string): TemplateQuickAddFormState {
  const action = getQuickAddAction(templateId, actionId);
  if (!action) return {};
  const state: TemplateQuickAddFormState = {};
  for (const field of action.fields) {
    if (field.field_type === "multi_select") state[field.key] = [];
    else if (field.field_type === "toggle") state[field.key] = false;
    else state[field.key] = "";
  }
  return state;
}

export function canSubmitTemplateAction(
  templateId: TemplateId,
  actionId: string,
  state: TemplateQuickAddFormState,
): boolean {
  const action = getQuickAddAction(templateId, actionId);
  if (!action) return false;
  for (const key of action.validation.required_fields ?? []) {
    const value = state[key];
    if (value == null || value === "") return false;
    if (Array.isArray(value) && value.length === 0) return false;
  }
  if (actionId === "POLL") {
    const options = state.options;
    if (Array.isArray(options)) {
      if (options.map((x) => String(x).trim()).filter(Boolean).length < 2) return false;
    } else if (
      String(options ?? "")
        .split(/[\n,]/)
        .map((s) => s.trim())
        .filter(Boolean).length < 2
    ) {
      return false;
    }
  }
  return true;
}

function parseAmountMinor(value: unknown): number {
  if (typeof value === "number") return Math.round(value);
  const raw = String(value ?? "").replace(/[^\d.]/g, "");
  const parsed = Number.parseFloat(raw);
  if (!Number.isFinite(parsed)) return 0;
  return Math.round(parsed * 100);
}

export function templateAction(templateId: TemplateId, actionId: string): QuickAddActionTemplate | undefined {
  return getQuickAddAction(templateId, actionId) ?? undefined;
}

export function buildPurchaseQuickAddPayload(
  actionId: string,
  state: TemplateQuickAddFormState,
): Record<string, unknown> {
  switch (actionId) {
    case "CONTRIBUTOR":
      return {
        name: state.name,
        role: state.role || undefined,
        invite_method: state.invite_method || undefined,
      };
    case "PARTICIPANTS":
      return {
        member_ids: state.member_ids,
        invite_status: state.invite_status || undefined,
      };
    case "PURCHASE_ITEM":
      return {
        item_name: state.item_name,
        product_link: state.product_link || undefined,
        target_price_minor: parseAmountMinor(state.target_price_minor),
        is_wishlist: Boolean(state.is_wishlist),
      };
    case "VENDOR":
      return {
        vendor_name: state.vendor_name,
        vendor_type: state.vendor_type || undefined,
        comparison_notes: state.comparison_notes || undefined,
        contact: state.contact || undefined,
      };
    case "EXPENSE":
      return {
        amount_minor: parseAmountMinor(state.amount_minor),
        shipping_minor: parseAmountMinor(state.shipping_minor),
        tax_minor: parseAmountMinor(state.tax_minor),
        warranty_notes: state.warranty_notes || undefined,
      };
    case "POLL":
      return buildSharedPollPayload(state);
    case "UPDATE":
      return {
        update_type: state.update_type || undefined,
        visibility: state.visibility || undefined,
        body: state.body,
      };
    case "OWNERSHIP":
      return {
        usage_rights: state.usage_rights,
        allocation_pct: state.allocation_pct || undefined,
        responsibility: state.responsibility || undefined,
      };
    case "DELIVERY":
      return {
        event_type: state.event_type,
        status: state.status || undefined,
        delivery_date: state.delivery_date || undefined,
        notes: state.notes || undefined,
      };
    case "MEMORY":
      return {
        memory_category: state.memory_category,
        caption: state.caption || undefined,
        title: state.caption ? String(state.caption).slice(0, 80) : "Purchase memory",
      };
    default:
      return { ...state };
  }
}

export function buildLivingQuickAddPayload(
  actionId: string,
  state: TemplateQuickAddFormState,
): Record<string, unknown> {
  switch (actionId) {
    case "RESIDENT":
      return {
        full_name: state.full_name,
        resident_role: state.resident_role || undefined,
        relationship_type: state.relationship_type || undefined,
        status: state.status || "invited",
      };
    case "EXPENSE":
      return {
        amount_minor: parseAmountMinor(state.amount_minor),
        expense_category: state.expense_category,
        split_type: state.split_type || "equal",
        expense_date: state.expense_date || undefined,
        currency_code: String(state.currency_code || state.currency || "").toUpperCase() || undefined,
        paid_by_participant_id:
          state.paid_by_participant_id || state.paid_by || state.paid_by_user_id || undefined,
        client_request_id: state.client_request_id || undefined,
        contract_version: "v1",
      };
    case "CONTRIBUTION":
      return {
        amount_minor: parseAmountMinor(state.amount_minor),
        contribution_category: state.contribution_category || undefined,
        payment_method: state.payment_method || undefined,
        status: state.status || undefined,
        currency_code: String(state.currency_code || state.currency || "").toUpperCase() || undefined,
        client_request_id: state.client_request_id || undefined,
        contract_version: "v1",
      };
    case "TASK":
      return {
        title: state.title,
        task_category: state.task_category || undefined,
        frequency: state.frequency || undefined,
        priority: state.priority || undefined,
        assignee_id: state.assignee_id || undefined,
      };
    case "ASSET":
      return {
        asset_type: state.asset_type || undefined,
        name: state.name,
        condition: state.condition || undefined,
        location: state.location || undefined,
      };
    case "RULE":
      return {
        rule_type: state.rule_type || undefined,
        text: state.text,
        visibility: state.visibility || undefined,
      };
    case "MAINTENANCE":
      return {
        maintenance_type: state.maintenance_type,
        severity: state.severity || undefined,
        description: state.description,
        due_date: state.due_date || undefined,
      };
    case "UPDATE":
      return {
        update_type: state.update_type || undefined,
        visibility: state.visibility || undefined,
        body: state.body,
      };
    case "POLL":
      return buildSharedPollPayload(state);
    case "MEMORY":
      return {
        memory_category: state.memory_category,
        memory_format: state.memory_format || undefined,
        caption: state.caption || undefined,
        title: state.caption ? String(state.caption).slice(0, 80) : "Home memory",
      };
    default:
      return { ...state };
  }
}
