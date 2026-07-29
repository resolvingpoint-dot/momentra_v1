import type { PersonalPulseResponse } from "@/lib/api/personal";
import type { LifeOpsQuickAddFormState } from "@/lib/quick_add/payloadBuilders/lifeOperations";

const OPTIMISTIC_SAFE = new Set(["EXPENSE", "RECOVERY", "REFLECTION"]);

export function isOptimisticSafeEventType(eventType: string): boolean {
  return OPTIMISTIC_SAFE.has(eventType.toUpperCase());
}

function pendingRecentItem(
  eventType: string,
  title: string,
  clientRequestId: string,
) {
  return {
    id: `pending-${clientRequestId}`,
    activity_type: eventType,
    title,
    subtitle: "Saving…",
    occurred_at: new Date().toISOString(),
    relative_time: "Just now",
    pending: true as const,
  };
}

export function buildLifeOpsOptimisticPatch(
  eventType: string,
  form: LifeOpsQuickAddFormState,
  title: string,
  momentId: string,
  clientRequestId: string,
  current: PersonalPulseResponse | null,
): Partial<PersonalPulseResponse> | null {
  if (!isOptimisticSafeEventType(eventType) || !current?.life_operations) {
    return null;
  }

  const lo = current.life_operations;
  const dashboard = lo.dashboard_card ?? {
    moment_type_code: "LIFE_OPERATIONS",
    kpis: [],
    recent_items: [],
  };
  const recentItem = pendingRecentItem(eventType, title, clientRequestId);
  const recent_items = [recentItem, ...(dashboard.recent_items ?? [])].slice(0, 8);

  const patch: Partial<PersonalPulseResponse> = {
    life_operations: {
      ...lo,
      dashboard_card: {
        ...dashboard,
        recent_items,
      },
    },
  };

  if (eventType === "EXPENSE" && lo.metrics && form.amountMinor > 0) {
    const metrics = { ...lo.metrics };
    const capacity = { ...metrics.capacity };
    const used = capacity.used_minor + form.amountMinor;
    capacity.used_minor = used;
    const hasBudget = capacity.has_budget ?? capacity.budget_minor > 0;
    if (hasBudget && capacity.budget_minor > 0) {
      capacity.remaining_minor = Math.max(0, capacity.budget_minor - used);
      capacity.utilization_percent = Math.min(
        100,
        Math.round((used / capacity.budget_minor) * 100),
      );
    } else {
      capacity.has_budget = false;
      capacity.remaining_minor = null;
      capacity.utilization_percent = null;
    }
    metrics.capacity = capacity;

    const segments = [...(metrics.financial_segments ?? [])];
    const cat = form.categoryCode || "other";
    const idx = segments.findIndex((s) => s.category_id === cat);
    if (idx >= 0) {
      segments[idx] = {
        ...segments[idx],
        amount_minor: segments[idx].amount_minor + form.amountMinor,
      };
    } else {
      segments.push({
        category_id: cat,
        category_name: cat.replace(/_/g, " "),
        amount_minor: form.amountMinor,
        share_percent: 0,
      });
    }
    const total = segments.reduce((sum, s) => sum + s.amount_minor, 0);
    metrics.financial_segments = segments.map((s) => ({
      ...s,
      share_percent: total > 0 ? Math.round((s.amount_minor / total) * 100) : 0,
    }));

    patch.life_operations = {
      ...patch.life_operations!,
      metrics,
    };
  }

  return patch;
}
