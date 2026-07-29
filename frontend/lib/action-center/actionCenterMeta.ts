/**
 * Action Center metadata overlay — extends registry actions without replacing them.
 * Shell only consumes renderer_id + capabilities; never hardcodes Expense/Booking.
 */
import type {
  ActionCapabilities,
  ActionCenterCategory,
  QuickAddActionTemplate,
} from "@/lib/quick_add/types";
import { getQuickAddActionsForTemplate } from "@/lib/quick_add/registry";

export type ActionCenterMeta = {
  subtitle: string;
  category: ActionCenterCategory;
  estimated_time_sec: number;
  tags: string[];
  synonyms: string[];
  renderer_id: string;
  analytics_id: string;
  priority?: number;
  accent?: string;
  supports?: ActionCapabilities;
};

const DEFAULT_SUPPORTS: ActionCapabilities = {
  drafts: true,
  favorites: true,
  search: true,
  attachments: false,
  participants: false,
  location: false,
  offline: true,
  notifications: false,
  approval: false,
  settlement: false,
};

const TRIP_META: Record<string, ActionCenterMeta> = {
  PARTICIPANT: {
    subtitle: "Invite people and assign roles",
    category: "people",
    estimated_time_sec: 20,
    tags: ["invite", "crew"],
    synonyms: ["guest", "member", "friend"],
    renderer_id: "experience.participant",
    analytics_id: "group.trip.participant",
    priority: 10,
    supports: { ...DEFAULT_SUPPORTS, participants: true },
  },
  PLANNING_ITEM: {
    subtitle: "Tasks, reminders, and milestones",
    category: "planning",
    estimated_time_sec: 20,
    tags: ["task", "todo"],
    synonyms: ["todo", "checklist", "plan"],
    renderer_id: "experience.planning_item",
    analytics_id: "group.trip.planning_item",
    priority: 15,
  },
  BOOKING: {
    subtitle: "Flights, hotels, and venues",
    category: "planning",
    estimated_time_sec: 30,
    tags: ["travel", "stay"],
    synonyms: ["hotel", "flight", "stay", "accommodation", "reservation"],
    renderer_id: "experience.booking",
    analytics_id: "group.trip.booking",
    priority: 20,
  },
  EXPENSE: {
    subtitle: "Record spending and split transactions",
    category: "money",
    estimated_time_sec: 25,
    tags: ["money", "spend", "split"],
    synonyms: ["hotel", "accommodation", "food", "taxi", "receipt"],
    renderer_id: "experience.expense",
    analytics_id: "group.trip.expense",
    priority: 25,
    supports: { ...DEFAULT_SUPPORTS, participants: true, attachments: true, location: true, settlement: true },
  },
  CONTRIBUTION: {
    subtitle: "Track money collected for experience",
    category: "money",
    estimated_time_sec: 20,
    tags: ["money", "pool"],
    synonyms: ["deposit", "fund", "pay in"],
    renderer_id: "experience.contribution",
    analytics_id: "group.trip.contribution",
    priority: 30,
    supports: { ...DEFAULT_SUPPORTS, participants: true, settlement: true },
  },
  BUDGET: {
    subtitle: "Plan expected costs and contribution share",
    category: "money",
    estimated_time_sec: 25,
    tags: ["money", "plan", "ceiling"],
    synonyms: ["budget", "allocation", "planning budget"],
    renderer_id: "experience.budget",
    analytics_id: "group.trip.budget",
    priority: 28,
    supports: { ...DEFAULT_SUPPORTS, settlement: true },
  },
  VENDOR: {
    subtitle: "Service providers and sponsors",
    category: "support",
    estimated_time_sec: 25,
    tags: ["vendor", "supplier"],
    synonyms: ["agent", "provider", "gst"],
    renderer_id: "experience.vendor",
    analytics_id: "group.trip.vendor",
    priority: 35,
  },
  ATTENDANCE: {
    subtitle: "RSVPs and guest participation",
    category: "support",
    estimated_time_sec: 15,
    tags: ["rsvp"],
    synonyms: ["coming", "rsvp"],
    renderer_id: "experience.attendance",
    analytics_id: "group.trip.attendance",
    priority: 40,
    supports: { ...DEFAULT_SUPPORTS, participants: true },
  },
  UPDATE: {
    subtitle: "Announcements and decisions",
    category: "support",
    estimated_time_sec: 15,
    tags: ["announce"],
    synonyms: ["announce", "news", "post"],
    renderer_id: "experience.update",
    analytics_id: "group.trip.update",
    priority: 45,
    supports: { ...DEFAULT_SUPPORTS, notifications: true },
  },
  MEMORY: {
    subtitle: "Capture photos and highlights",
    category: "capture",
    estimated_time_sec: 20,
    tags: ["photo", "moment"],
    synonyms: ["photo", "album", "highlight"],
    renderer_id: "experience.memory",
    analytics_id: "group.trip.memory",
    priority: 50,
    supports: { ...DEFAULT_SUPPORTS, attachments: true, location: true },
  },
  POLL: {
    subtitle: "Let the group vote and decide",
    category: "capture",
    estimated_time_sec: 20,
    tags: ["vote", "decision"],
    synonyms: ["vote", "choose"],
    renderer_id: "experience.poll",
    analytics_id: "group.trip.poll",
    priority: 55,
  },
};

const PURCHASE_META: Record<string, ActionCenterMeta> = {
  CONTRIBUTOR: {
    subtitle: "Invite people funding this purchase.",
    category: "people",
    estimated_time_sec: 20,
    tags: ["contributor", "invite"],
    synonyms: ["member", "funder", "participant"],
    renderer_id: "purchase.contribution",
    analytics_id: "group.purchase.contributor",
    priority: 10,
    supports: { ...DEFAULT_SUPPORTS, participants: true },
  },
  PARTICIPANTS: {
    subtitle: "Manage who is involved.",
    category: "people",
    estimated_time_sec: 20,
    tags: ["people"],
    synonyms: ["members", "team"],
    renderer_id: "purchase.participant",
    analytics_id: "group.purchase.participants",
    supports: { ...DEFAULT_SUPPORTS, participants: true },
  },
  PURCHASE_ITEM: {
    subtitle: "Add items and price targets.",
    category: "money",
    estimated_time_sec: 25,
    tags: ["item", "cart"],
    synonyms: ["product", "wishlist", "buy"],
    renderer_id: "purchase.purchase",
    analytics_id: "group.purchase.item",
    priority: 15,
  },
  VENDOR: {
    subtitle: "Compare vendors and quotes.",
    category: "administration",
    estimated_time_sec: 25,
    tags: ["vendor"],
    synonyms: ["shop", "store", "gst"],
    renderer_id: "purchase.vendor",
    analytics_id: "group.purchase.vendor",
  },
  EXPENSE: {
    subtitle: "Record purchase spend.",
    category: "money",
    estimated_time_sec: 25,
    tags: ["spend"],
    synonyms: ["cost", "receipt", "payment"],
    renderer_id: "purchase.expense",
    analytics_id: "group.purchase.expense",
    priority: 20,
    supports: { ...DEFAULT_SUPPORTS, attachments: true, location: true, settlement: true },
  },
  POLL: {
    subtitle: "Decide together.",
    category: "capture",
    estimated_time_sec: 20,
    tags: ["vote"],
    synonyms: ["vote", "choose"],
    renderer_id: "purchase.poll",
    analytics_id: "group.purchase.poll",
  },
  UPDATE: {
    subtitle: "Share progress with the group.",
    category: "capture",
    estimated_time_sec: 15,
    tags: ["news"],
    synonyms: ["announce", "status"],
    renderer_id: "purchase.update",
    analytics_id: "group.purchase.update",
    supports: { ...DEFAULT_SUPPORTS, notifications: true },
  },
  OWNERSHIP: {
    subtitle: "Assign shares and usage rights.",
    category: "administration",
    estimated_time_sec: 30,
    tags: ["ownership", "share"],
    synonyms: ["equity", "share", "rights"],
    renderer_id: "purchase.ownership",
    analytics_id: "group.purchase.ownership",
  },
  DELIVERY: {
    subtitle: "Track shipping and handover.",
    category: "planning",
    estimated_time_sec: 20,
    tags: ["delivery"],
    synonyms: ["shipping", "handover", "courier"],
    renderer_id: "purchase.delivery",
    analytics_id: "group.purchase.delivery",
  },
  MEMORY: {
    subtitle: "Capture purchase highlights.",
    category: "capture",
    estimated_time_sec: 20,
    tags: ["memory"],
    synonyms: ["photo", "unboxing"],
    renderer_id: "purchase.memory",
    analytics_id: "group.purchase.memory",
    supports: { ...DEFAULT_SUPPORTS, attachments: true },
  },
};

const LIVING_META: Record<string, ActionCenterMeta> = {
  RESIDENT: {
    subtitle: "Invite people who live here.",
    category: "people",
    estimated_time_sec: 20,
    tags: ["resident"],
    synonyms: ["roommate", "flatmate", "tenant"],
    renderer_id: "living.resident",
    analytics_id: "group.living.resident",
    priority: 15,
    supports: { ...DEFAULT_SUPPORTS, participants: true },
  },
  EXPENSE: {
    subtitle: "Log rent, utilities, groceries, and more.",
    category: "money",
    estimated_time_sec: 25,
    tags: ["expense"],
    synonyms: ["spend", "bill", "grocery"],
    renderer_id: "living.expense",
    analytics_id: "group.living.expense",
    priority: 20,
    supports: { ...DEFAULT_SUPPORTS, participants: true, settlement: true, attachments: true },
  },
  RENT: {
    subtitle: "Record this month’s rent.",
    category: "money",
    estimated_time_sec: 20,
    tags: ["rent", "housing"],
    synonyms: ["lease", "landlord", "overdue"],
    renderer_id: "living.rent",
    analytics_id: "group.living.rent",
    priority: 5,
    supports: { ...DEFAULT_SUPPORTS, participants: true, settlement: true },
  },
  UTILITY: {
    subtitle: "Log electricity, water, internet, and more.",
    category: "money",
    estimated_time_sec: 20,
    tags: ["utility", "bill"],
    synonyms: ["electricity", "water", "wifi", "gas"],
    renderer_id: "living.utility",
    analytics_id: "group.living.utility",
    priority: 12,
    supports: { ...DEFAULT_SUPPORTS, settlement: true },
  },
  CONTRIBUTION: {
    subtitle: "Record money put into the house pool.",
    category: "money",
    estimated_time_sec: 20,
    tags: ["contribution"],
    synonyms: ["pay in", "fund"],
    renderer_id: "living.contributor",
    analytics_id: "group.living.contribution",
    supports: { ...DEFAULT_SUPPORTS, participants: true },
  },
  TASK: {
    subtitle: "Chores and household tasks.",
    category: "planning",
    estimated_time_sec: 20,
    tags: ["chore", "task"],
    synonyms: ["chore", "cleaning", "todo"],
    renderer_id: "living.task",
    analytics_id: "group.living.task",
    supports: { ...DEFAULT_SUPPORTS, participants: true, notifications: true },
  },
  ASSET: {
    subtitle: "Register shared belongings.",
    category: "administration",
    estimated_time_sec: 20,
    tags: ["asset"],
    synonyms: ["appliance", "furniture"],
    renderer_id: "living.asset",
    analytics_id: "group.living.asset",
  },
  RULE: {
    subtitle: "House agreements that stick.",
    category: "administration",
    estimated_time_sec: 15,
    tags: ["rule"],
    synonyms: ["policy", "agreement"],
    renderer_id: "living.rule",
    analytics_id: "group.living.rule",
  },
  MAINTENANCE: {
    subtitle: "Repairs and upkeep.",
    category: "planning",
    estimated_time_sec: 25,
    tags: ["repair"],
    synonyms: ["fix", "plumber", "broken"],
    renderer_id: "living.maintenance",
    analytics_id: "group.living.maintenance",
  },
  UPDATE: {
    subtitle: "Share news with residents.",
    category: "capture",
    estimated_time_sec: 15,
    tags: ["announce"],
    synonyms: ["news", "post"],
    renderer_id: "living.update",
    analytics_id: "group.living.update",
    supports: { ...DEFAULT_SUPPORTS, notifications: true },
  },
  POLL: {
    subtitle: "Decide together at home.",
    category: "capture",
    estimated_time_sec: 20,
    tags: ["vote"],
    synonyms: ["vote", "choose"],
    renderer_id: "living.poll",
    analytics_id: "group.living.poll",
  },
  MEMORY: {
    subtitle: "Capture home moments.",
    category: "capture",
    estimated_time_sec: 20,
    tags: ["memory"],
    synonyms: ["photo", "party"],
    renderer_id: "living.memory",
    analytics_id: "group.living.memory",
    supports: { ...DEFAULT_SUPPORTS, attachments: true, location: true },
  },
};

const META_BY_TEMPLATE: Record<string, Record<string, ActionCenterMeta>> = {
  "group.trip": TRIP_META,
  "group.purchase": PURCHASE_META,
  "group.living": LIVING_META,
};

function mergeMeta(action: QuickAddActionTemplate, meta?: ActionCenterMeta): QuickAddActionTemplate {
  if (!meta) return action;
  return {
    ...action,
    subtitle: action.subtitle ?? meta.subtitle,
    category: action.category ?? meta.category,
    estimated_time_sec: action.estimated_time_sec ?? meta.estimated_time_sec,
    tags: action.tags ?? meta.tags,
    synonyms: action.synonyms ?? meta.synonyms,
    renderer_id: action.renderer_id ?? meta.renderer_id,
    analytics_id: action.analytics_id ?? meta.analytics_id,
    priority: action.priority ?? meta.priority,
    accent: action.accent ?? meta.accent,
    supports: { ...DEFAULT_SUPPORTS, ...meta.supports, ...action.supports },
  };
}

/** Synthetic Living Rent/Utility — same expenses endpoint, dedicated renderers. */
function livingAliases(actions: QuickAddActionTemplate[]): QuickAddActionTemplate[] {
  const expense = actions.find((a) => a.action_id === "EXPENSE");
  if (!expense) return actions;
  const base = { ...expense };
  delete base.renderer_id;
  delete base.subtitle;
  delete base.analytics_id;
  delete base.tags;
  delete base.synonyms;
  delete base.category;
  delete base.estimated_time_sec;
  delete base.priority;
  delete base.supports;
  const rent = mergeMeta(
    {
      ...base,
      action_id: "RENT",
      label: "Rent",
      icon: "home",
      cta_label: "Record Rent",
      display_order: 1.5,
    },
    LIVING_META.RENT,
  );
  const utility = mergeMeta(
    {
      ...base,
      action_id: "UTILITY",
      label: "Utility",
      icon: "bolt",
      cta_label: "Log Utility",
      display_order: 1.6,
    },
    LIVING_META.UTILITY,
  );
  return [...actions, rent, utility];
}

export function getActionCenterActions(templateId: string): QuickAddActionTemplate[] {
  const base = getQuickAddActionsForTemplate(templateId);
  const metaMap = META_BY_TEMPLATE[templateId] ?? {};
  let enriched = base.map((a) => mergeMeta(a, metaMap[a.action_id]));
  if (templateId === "group.living") enriched = livingAliases(enriched);
  return enriched.sort((a, b) => (a.priority ?? 100 + a.display_order) - (b.priority ?? 100 + b.display_order));
}

export function getActionCenterAction(
  templateId: string,
  actionId: string,
): QuickAddActionTemplate | null {
  return getActionCenterActions(templateId).find((a) => a.action_id === actionId) ?? null;
}

export function searchActionCenterActions(
  actions: QuickAddActionTemplate[],
  query: string,
): QuickAddActionTemplate[] {
  const q = query.trim().toLowerCase();
  if (!q) return actions;
  return actions.filter((a) => {
    const hay = [
      a.label,
      a.subtitle ?? "",
      ...(a.tags ?? []),
      ...(a.synonyms ?? []),
      a.action_id,
    ]
      .join(" ")
      .toLowerCase();
    return hay.includes(q);
  });
}

export const ACTION_CENTER_CATEGORY_LABELS: Record<ActionCenterCategory, string> = {
  money: "Money",
  planning: "Planning",
  people: "People",
  capture: "Memory & Decisions",
  administration: "Administration",
  support: "Support",
};

/** Stitch Trip Quick Add hub section order */
export const TRIP_HUB_CATEGORY_ORDER: ActionCenterCategory[] = [
  "people",
  "planning",
  "money",
  "support",
  "capture",
  "administration",
];

export const TRIP_ACTION_ICON: Record<string, string> = {
  PARTICIPANT: "person_add",
  PLANNING_ITEM: "task_alt",
  BOOKING: "flight_takeoff",
  EXPENSE: "payments",
  CONTRIBUTION: "savings",
  BUDGET: "account_balance_wallet",
  VENDOR: "handshake",
  ATTENDANCE: "checklist",
  UPDATE: "campaign",
  MEMORY: "photo_library",
  POLL: "how_to_vote",
};
