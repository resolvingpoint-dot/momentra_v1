import { buildBundle, field, groupPurchaseEndpoint, type ActionDef } from "../builders";
import type { QuickAddTemplateBundle } from "../types";

const TEMPLATE_ID = "group.purchase";
const CONTEXT = "SHARED_PURCHASE" as const;
const MODULES = ["pulse", "live", "memory", "operations_hub"];

function purchaseAction(
  def: Omit<ActionDef, "backend_endpoint" | "output_event" | "affects_modules"> & {
    endpointKey: string;
    eventType: string;
    refTable?: string;
  },
): ActionDef {
  return {
    ...def,
    backend_endpoint: groupPurchaseEndpoint(def.endpointKey),
    output_event: { event_type: def.eventType, ref_table: def.refTable },
    affects_modules: MODULES,
  };
}

const actions: ActionDef[] = [
  purchaseAction({
    action_id: "CONTRIBUTOR",
    reusable_type: "participant",
    label: "Contributor",
    icon: "person_add",
    section: "Contributors",
    display_order: 1,
    cta_label: "Add Contributor",
    fields: [
      field("name", "Name", "text", { required: true }),
      field("role", "Role", "single_select"),
      field("invite_method", "Invite method", "single_select"),
    ],
    validation: { required_fields: ["name"] },
    impact_preview: { modules: MODULES, summary_template: "Adds contributor {name}" },
    endpointKey: "contributors",
    eventType: "CONTRIBUTOR_ADDED",
  }),
  purchaseAction({
    action_id: "PARTICIPANTS",
    reusable_type: "participant",
    label: "Participants",
    icon: "group_add",
    section: "Contributors",
    display_order: 2,
    cta_label: "Manage Participants",
    fields: [
      field("member_ids", "Members", "multi_select"),
      field("invite_status", "Invite status", "single_select"),
    ],
    validation: { required_fields: ["member_ids"] },
    impact_preview: { modules: MODULES, summary_template: "Updates participant list" },
    endpointKey: "participants",
    eventType: "PARTICIPANTS_UPDATED",
  }),
  purchaseAction({
    action_id: "PURCHASE_ITEM",
    reusable_type: "task",
    label: "Purchase Item",
    icon: "shopping_cart",
    section: "Purchase",
    display_order: 3,
    cta_label: "Add Purchase Item",
    fields: [
      field("item_name", "Item name", "text", { required: true }),
      field("product_link", "Product link", "text"),
      field("target_price_minor", "Target price", "amount"),
      field("is_wishlist", "Wishlist", "toggle"),
    ],
    validation: { required_fields: ["item_name"] },
    impact_preview: { modules: MODULES, summary_template: "Adds item {item_name}" },
    endpointKey: "purchase-items",
    eventType: "PURCHASE_ITEM_ADDED",
  }),
  purchaseAction({
    action_id: "VENDOR",
    reusable_type: "participant",
    label: "Vendor",
    icon: "storefront",
    section: "Purchase",
    display_order: 4,
    cta_label: "Add Vendor",
    fields: [
      field("vendor_name", "Vendor", "text", { required: true }),
      field("vendor_type", "Type", "single_select"),
      field("comparison_notes", "Comparison notes", "textarea"),
      field("contact", "Contact", "text"),
    ],
    validation: { required_fields: ["vendor_name"] },
    impact_preview: { modules: MODULES, summary_template: "Adds vendor {vendor_name}" },
    endpointKey: "vendors",
    eventType: "VENDOR_ADDED",
  }),
  purchaseAction({
    action_id: "EXPENSE",
    reusable_type: "expense",
    label: "Expense",
    icon: "receipt_long",
    section: "Purchase",
    display_order: 5,
    cta_label: "Record Expense",
    fields: [
      field("amount_minor", "Amount", "amount", { required: true }),
      field("shipping_minor", "Shipping", "amount"),
      field("tax_minor", "Tax", "amount"),
      field("warranty_notes", "Warranty", "textarea"),
    ],
    validation: { required_fields: ["amount_minor"] },
    impact_preview: { modules: MODULES, summary_template: "Records purchase expense" },
    endpointKey: "expenses",
    eventType: "PURCHASE_EXPENSE_RECORDED",
  }),
  purchaseAction({
    action_id: "POLL",
    reusable_type: "decision",
    label: "Poll",
    icon: "poll",
    display_order: 6,
    cta_label: "Create Poll",
    fields: [
      field("question", "Question", "text", { required: true }),
      field("options", "Options", "multi_select", { required: true }),
      field("allow_multiple_answers", "Allow multiple answers", "toggle"),
    ],
    validation: { required_fields: ["question", "options"] },
    impact_preview: { modules: MODULES, summary_template: "Creates poll: {question}" },
    endpointKey: "polls",
    eventType: "PURCHASE_POLL_CREATED",
  }),
  purchaseAction({
    action_id: "UPDATE",
    reusable_type: "update",
    label: "Update",
    icon: "campaign",
    display_order: 7,
    cta_label: "Post Update",
    fields: [
      field("update_type", "Update type", "single_select"),
      field("visibility", "Visibility", "single_select"),
      field("body", "Message", "textarea", { required: true }),
    ],
    validation: { required_fields: ["body"] },
    impact_preview: { modules: MODULES, summary_template: "Posts purchase update" },
    endpointKey: "updates",
    eventType: "PURCHASE_UPDATE_POSTED",
  }),
  purchaseAction({
    action_id: "OWNERSHIP",
    reusable_type: "decision",
    label: "Ownership",
    icon: "supervised_user_circle",
    section: "Ownership",
    display_order: 8,
    cta_label: "Set Ownership",
    fields: [
      field("usage_rights", "Usage rights", "single_select"),
      field("allocation_pct", "Allocation %", "text"),
      field("responsibility", "Responsibility", "textarea"),
    ],
    validation: { required_fields: ["usage_rights"] },
    impact_preview: { modules: MODULES, summary_template: "Updates ownership allocation" },
    endpointKey: "ownership",
    eventType: "OWNERSHIP_UPDATED",
  }),
  purchaseAction({
    action_id: "DELIVERY",
    reusable_type: "booking",
    label: "Delivery / Handover",
    icon: "local_shipping",
    section: "Ownership",
    display_order: 9,
    cta_label: "Track Delivery",
    fields: [
      field("event_type", "Event type", "single_select"),
      field("status", "Status", "single_select"),
      field("delivery_date", "Delivery date", "date"),
      field("notes", "Notes", "textarea"),
    ],
    validation: { required_fields: ["event_type"] },
    impact_preview: { modules: MODULES, summary_template: "Tracks delivery/handover" },
    endpointKey: "delivery",
    eventType: "DELIVERY_TRACKED",
  }),
  purchaseAction({
    action_id: "MEMORY",
    reusable_type: "memory",
    label: "Memory",
    icon: "auto_awesome",
    display_order: 10,
    cta_label: "Capture Memory",
    fields: [
      field("memory_category", "Category", "single_select"),
      field("media", "Media", "media_upload"),
      field("caption", "Caption", "textarea"),
    ],
    validation: { required_fields: ["memory_category"] },
    impact_preview: { modules: MODULES, summary_template: "Captures purchase memory" },
    endpointKey: "memories",
    eventType: "PURCHASE_MEMORY_CAPTURED",
  }),
];

export const GROUP_PURCHASE_QUICK_ADD: QuickAddTemplateBundle = buildBundle(
  TEMPLATE_ID,
  CONTEXT,
  "sectioned_hub",
  actions,
  { default_action_id: "CONTRIBUTOR" },
);
