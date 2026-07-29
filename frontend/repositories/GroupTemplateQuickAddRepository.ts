import { requestWithRetry } from "@/lib/api/client";
import type { TripQuickAddCategory, TripQuickAddConfigResponse } from "@/repositories/GroupTripQuickAddRepository";

export type { TripQuickAddCategory, TripQuickAddConfigResponse };

export type TemplateQuickAddKind = "purchase" | "living";

const CONTEXT_CACHE_TTL_MS = 2 * 60 * 1000;
const purchaseLivingContextCache = new Map<string, { data: Record<string, unknown>; at: number }>();

/** Backend hub module_code → registry action_id */
const PURCHASE_MODULE_TO_ACTION: Record<string, string> = {
  CONTRIBUTORS: "CONTRIBUTOR",
  PARTICIPANTS: "PARTICIPANTS",
  PURCHASE_ITEMS: "PURCHASE_ITEM",
  VENDORS: "VENDOR",
  EXPENSES: "EXPENSE",
  POLLS: "POLL",
  UPDATES: "UPDATE",
  OWNERSHIP: "OWNERSHIP",
  DELIVERY: "DELIVERY",
  MEMORIES: "MEMORY",
};

const LIVING_MODULE_TO_ACTION: Record<string, string> = {
  RESIDENTS: "RESIDENT",
  EXPENSES: "EXPENSE",
  CONTRIBUTIONS: "CONTRIBUTION",
  TASKS: "TASK",
  RULES: "RULE",
  ASSETS: "ASSET",
  MAINTENANCE: "MAINTENANCE",
  UPDATES: "UPDATE",
  POLLS: "POLL",
  MEMORIES: "MEMORY",
};

/** Registry action_id → API path slug */
const PURCHASE_ACTION_SLUG: Record<string, string> = {
  CONTRIBUTOR: "contributors",
  PARTICIPANTS: "participants",
  PURCHASE_ITEM: "purchase-items",
  VENDOR: "vendors",
  EXPENSE: "expenses",
  POLL: "polls",
  UPDATE: "updates",
  OWNERSHIP: "ownership",
  DELIVERY: "delivery",
  MEMORY: "memories",
};

const LIVING_ACTION_SLUG: Record<string, string> = {
  RESIDENT: "residents",
  EXPENSE: "expenses",
  CONTRIBUTION: "contributions",
  TASK: "tasks",
  RULE: "rules",
  ASSET: "assets",
  MAINTENANCE: "maintenance",
  UPDATE: "updates",
  POLL: "polls",
  MEMORY: "memories",
};

export function moduleCodeToActionId(kind: TemplateQuickAddKind, moduleCode: string): string {
  const upper = moduleCode.toUpperCase();
  const map = kind === "purchase" ? PURCHASE_MODULE_TO_ACTION : LIVING_MODULE_TO_ACTION;
  return map[upper] ?? upper;
}

export function actionIdToSlug(kind: TemplateQuickAddKind, actionId: string): string {
  const map = kind === "purchase" ? PURCHASE_ACTION_SLUG : LIVING_ACTION_SLUG;
  return map[actionId] ?? actionId.toLowerCase().replace(/_/g, "-");
}

function basePath(kind: TemplateQuickAddKind, momentId: string): string {
  const prefix = kind === "purchase" ? "shared-purchase" : "shared-living";
  return `/api/v1/group/${prefix}/moments/${momentId}/quick-add`;
}

export async function fetchGroupTemplateQuickAddConfig(momentId: string): Promise<TripQuickAddConfigResponse> {
  return requestWithRetry<TripQuickAddConfigResponse>(`/api/v1/group/quickadd/${momentId}`);
}

export async function fetchGroupTemplateQuickAddContext(
  kind: TemplateQuickAddKind,
  momentId: string,
  actionId: string,
): Promise<Record<string, unknown>> {
  const cacheKey = `${kind}:${momentId}:${actionId}`;
  const cached = purchaseLivingContextCache.get(cacheKey);
  if (cached && Date.now() - cached.at < CONTEXT_CACHE_TTL_MS) {
    return cached.data;
  }
  const slug = actionIdToSlug(kind, actionId);
  const result = await requestWithRetry<Record<string, unknown>>(
    `${basePath(kind, momentId)}/${slug}/context`,
  );
  purchaseLivingContextCache.set(cacheKey, { data: result, at: Date.now() });
  return result;
}

export async function prefetchPurchaseQuickAddContexts(
  momentId: string,
  actionIds: string[],
): Promise<void> {
  const uniqueIds = Array.from(new Set(actionIds));
  await Promise.all(
    uniqueIds.map(async (actionId) => {
      try {
        await fetchGroupTemplateQuickAddContext("purchase", momentId, actionId);
      } catch {
        // Best-effort warmup only.
      }
    }),
  );
}

export async function prefetchLivingQuickAddContexts(
  momentId: string,
  actionIds: string[],
): Promise<void> {
  const uniqueIds = Array.from(new Set(actionIds));
  await Promise.all(
    uniqueIds.map(async (actionId) => {
      try {
        await fetchGroupTemplateQuickAddContext("living", momentId, actionId);
      } catch {
        // Best-effort warmup only.
      }
    }),
  );
}

export async function submitGroupTemplateQuickAdd(
  kind: TemplateQuickAddKind,
  momentId: string,
  actionId: string,
  body: Record<string, unknown>,
): Promise<unknown> {
  const slug = actionIdToSlug(kind, actionId);
  return requestWithRetry(`${basePath(kind, momentId)}/${slug}`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}
