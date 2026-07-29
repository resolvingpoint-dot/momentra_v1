import type { QuickAddActionTemplate } from "../types";
import { getQuickAddAction } from "../registry";
import { buildSharedPollPayload } from "./sharedPoll";

export type TripQuickAddFormState = Record<string, string | string[] | number | boolean>;

export function defaultTripFormState(actionId: string): TripQuickAddFormState {
  const action = getQuickAddAction("group.trip", actionId);
  if (!action) return {};
  const state: TripQuickAddFormState = {};
  for (const field of action.fields) {
    if (field.field_type === "multi_select") {
      state[field.key] = [];
    } else if (field.field_type === "toggle") {
      state[field.key] = false;
    } else if (field.field_type === "amount") {
      state[field.key] = "";
    } else {
      state[field.key] = "";
    }
  }
  return state;
}

export function canSubmitTripAction(actionId: string, state: TripQuickAddFormState): boolean {
  const action = getQuickAddAction("group.trip", actionId);
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

/**
 * Normalize amount_minor for trip quick-add payloads.
 * - number → already minor units (do not multiply)
 * - string → major currency units (rupees) → multiply by 100
 */
export function parseAmountMinor(value: unknown): number {
  if (typeof value === "number" && Number.isFinite(value)) return Math.round(value);
  const raw = String(value ?? "").replace(/[^\d.]/g, "");
  const parsed = Number.parseFloat(raw);
  if (!Number.isFinite(parsed)) return 0;
  return Math.round(parsed * 100);
}

export function buildTripQuickAddPayload(actionId: string, state: TripQuickAddFormState): Record<string, unknown> {
  switch (actionId) {
    case "PARTICIPANT":
      return {
        full_name: state.full_name,
        phone: state.phone || undefined,
        email: state.email || undefined,
        relationship_type: state.relationship_type,
        assigned_role: state.assigned_role || undefined,
        status: state.status || "invited",
      };
    case "PLANNING_ITEM":
      return {
        title: state.title,
        category: state.planning_category || "stay",
        details: {
          planning_category: state.planning_category,
          due_date: state.due_date,
          planning_status: state.planning_status,
        },
      };
    case "BOOKING":
      return {
        booking_type: state.booking_type,
        provider: state.provider || undefined,
        booking_status: state.booking_status || "planned",
        amount_minor: parseAmountMinor(state.amount_minor),
        description: state.description || undefined,
      };
    case "EXPENSE":
      return {
        amount_minor: parseAmountMinor(state.amount_minor),
        category: state.category,
        split_type: state.split_type || "EQUAL",
        split_style: String(state.split_type || state.split_style || "EQUAL").toUpperCase(),
        paid_by_user_id: state.paid_by_user_id || undefined,
        paid_by_participant_id: state.paid_by_participant_id || state.paid_by_user_id || undefined,
        description: state.description || undefined,
        title: state.title || state.description || undefined,
        currency_code: state.currency_code || undefined,
        participant_ids: state.participant_ids,
        notes: state.notes || undefined,
      };
    case "CONTRIBUTION":
      return {
        amount_minor: parseAmountMinor(state.amount_minor),
        contributor_user_id: state.contributor_id || undefined,
        title: state.payment_method ? String(state.payment_method) : undefined,
        currency_code: state.currency_code || undefined,
        allocation_category: state.allocation_category || undefined,
        payment_method: state.payment_method || undefined,
      };
    case "VENDOR":
      return {
        vendor_name: state.vendor_name,
        vendor_type: state.vendor_type || undefined,
        contact: state.contact || undefined,
        notes: state.notes || undefined,
      };
    case "ATTENDANCE":
      return {
        member_id: state.member_id,
        attendance_type: state.attendance_type,
        status: state.status || "CONFIRMED",
        notes: state.notes || undefined,
      };
    case "UPDATE":
      return {
        title: state.title,
        body: state.body,
        update_type: state.update_type || undefined,
        visibility: state.visibility || undefined,
      };
    case "MEMORY": {
      const title =
        (typeof state.title === "string" && state.title.trim()) ||
        (typeof state.caption === "string" && state.caption.trim().slice(0, 80)) ||
        "Trip memory";
      const noteParts = [
        typeof state.caption === "string" ? state.caption.trim() : "",
        typeof state.description === "string" ? state.description.trim() : "",
      ].filter(Boolean);
      const paths = Array.isArray(state.media_storage_paths)
        ? state.media_storage_paths.map(String).filter(Boolean)
        : typeof state.media_storage_paths === "string" && state.media_storage_paths
          ? state.media_storage_paths.split(",").map((p) => p.trim()).filter(Boolean)
          : [];
      return {
        title,
        note: noteParts[0] || undefined,
        media_storage_paths: paths,
        memory_format: state.memory_format || undefined,
        memory_category: state.memory_category || undefined,
      };
    }
    case "POLL":
      return buildSharedPollPayload(state);
    default:
      return { ...state };
  }
}

export function tripActionTemplate(actionId: string): QuickAddActionTemplate | null {
  return getQuickAddAction("group.trip", actionId);
}
