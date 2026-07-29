/**
 * Business Runway API parsers — components must not reshape backend payloads.
 */
import type {
  RunwayMomentsResponse,
  RunwayPulseResponse,
  TeamOpsEventItem,
  RunwayHealth,
} from "@/lib/api/businessActive";
import { RUNWAY_MOMENTS_SECTION_KEYS, RUNWAY_PULSE_SECTION_KEYS } from "@/lib/api/businessActive";

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function asRecord(value: unknown): Record<string, unknown> {
  return isRecord(value) ? value : {};
}

function asString(value: unknown, fallback = ""): string {
  return typeof value === "string" ? value : fallback;
}

function asNumber(value: unknown, fallback = 0): number {
  return typeof value === "number" && Number.isFinite(value) ? value : fallback;
}

function asNullableNumber(value: unknown): number | null {
  return typeof value === "number" && Number.isFinite(value) ? value : null;
}

function asBool(value: unknown, fallback = false): boolean {
  return typeof value === "boolean" ? value : fallback;
}

function asArray(value: unknown): unknown[] {
  return Array.isArray(value) ? value : [];
}

function parseEvent(raw: unknown): TeamOpsEventItem {
  const o = asRecord(raw);
  return {
    event_id: asString(o.event_id),
    action_type: asString(o.action_type),
    title: asString(o.title),
    subtitle: typeof o.subtitle === "string" ? o.subtitle : null,
    occurred_at: typeof o.occurred_at === "string" ? o.occurred_at : undefined,
    source_moment_id: typeof o.source_moment_id === "string" ? o.source_moment_id : null,
  };
}

function parseHealth(raw: unknown): RunwayHealth {
  const o = asRecord(raw);
  return {
    label: asString(o.label, "Not started"),
    band: asString(o.band, "empty"),
    rule: typeof o.rule === "string" ? o.rule : undefined,
    inputs: isRecord(o.inputs)
      ? Object.fromEntries(
          Object.entries(o.inputs).map(([k, v]) => [
            k,
            typeof v === "number" ? v : v === null ? null : asNumber(v),
          ]),
        )
      : undefined,
  };
}

function parseEventItems(raw: unknown): TeamOpsEventItem[] {
  return asArray(asRecord(raw).items).map(parseEvent);
}

function sectionState(raw: unknown): string {
  return asString(asRecord(raw).state, "empty");
}

export function parseRunwayPulseResponse(raw: unknown): RunwayPulseResponse {
  const o = asRecord(raw);
  const hero = asRecord(o.hero);
  const healthSection = asRecord(o.runway_health);
  const healthInner = asRecord(healthSection.health);

  const pulse: RunwayPulseResponse = {
    moment_id: asString(o.moment_id),
    moment_type: asString(o.moment_type, "BUSINESS_RUNWAY"),
    moment_name: typeof o.moment_name === "string" ? o.moment_name : null,
    runway_name: typeof o.runway_name === "string" ? o.runway_name : null,
    status: asString(o.status),
    is_active: asBool(o.is_active),
    operating_currency: asString(o.operating_currency, "INR"),
    stats: isRecord(o.stats)
      ? Object.fromEntries(
          Object.entries(o.stats).map(([k, v]) => [
            k,
            typeof v === "number" ? v : v === null ? null : asNumber(v),
          ]),
        )
      : undefined,
    hero: {
      state: sectionState(hero),
      title: asString(hero.title, "Business Runway"),
      subtitle: typeof hero.subtitle === "string" ? hero.subtitle : undefined,
      runway_health: parseHealth(hero.runway_health),
    },
    runway_health: {
      state: sectionState(healthSection),
      health: parseHealth(healthInner.label ? healthInner : hero.runway_health),
    },
    cash_position: {
      state: sectionState(o.cash_position),
      cash_available_minor: asNumber(asRecord(o.cash_position).cash_available_minor),
      operating_currency: asString(asRecord(o.cash_position).operating_currency, "INR"),
    },
    monthly_burn: {
      state: sectionState(o.monthly_burn),
      monthly_burn_minor: asNumber(asRecord(o.monthly_burn).monthly_burn_minor),
      activity_burn_minor: asNumber(asRecord(o.monthly_burn).activity_burn_minor),
    },
    revenue_trend: {
      state: sectionState(o.revenue_trend),
      monthly_revenue_minor: asNumber(asRecord(o.revenue_trend).monthly_revenue_minor),
      revenue_status:
        typeof asRecord(o.revenue_trend).revenue_status === "string"
          ? (asRecord(o.revenue_trend).revenue_status as string)
          : null,
    },
    collection_rate: {
      state: sectionState(o.collection_rate),
      collection_rate_percent: asNullableNumber(asRecord(o.collection_rate).collection_rate_percent),
    },
    runway_months: {
      state: sectionState(o.runway_months),
      runway_months: asNullableNumber(asRecord(o.runway_months).runway_months),
      runway_goal_months: asNullableNumber(asRecord(o.runway_months).runway_goal_months),
      alert_threshold_months: asNullableNumber(asRecord(o.runway_months).alert_threshold_months),
    },
    cash_movement: {
      state: sectionState(o.cash_movement),
      total_inflow_minor: asNumber(asRecord(o.cash_movement).total_inflow_minor),
      total_burn_minor: asNumber(asRecord(o.cash_movement).total_burn_minor),
      net_burn_minor: asNumber(asRecord(o.cash_movement).net_burn_minor),
    },
    kpis: {
      state: sectionState(o.kpis),
      ...(isRecord(o.kpis)
        ? Object.fromEntries(
            Object.entries(o.kpis)
              .filter(([k]) => k !== "state")
              .map(([k, v]) => [k, typeof v === "number" ? v : null]),
          )
        : {}),
    },
    forecast: {
      state: sectionState(o.forecast),
      runway_goal_months: asNullableNumber(asRecord(o.forecast).runway_goal_months),
      projected_runway_months: asNullableNumber(asRecord(o.forecast).projected_runway_months),
      alert_threshold_months: asNullableNumber(asRecord(o.forecast).alert_threshold_months),
    },
    attention_items: {
      state: sectionState(o.attention_items),
      items: asArray(asRecord(o.attention_items).items).map((item) => {
        const i = asRecord(item);
        return {
          kind: asString(i.kind),
          label: asString(i.label),
          count: asNumber(i.count),
          severity: typeof i.severity === "string" ? i.severity : undefined,
          description: typeof i.description === "string" ? i.description : undefined,
        };
      }),
    },
    trends: {
      state: sectionState(o.trends),
      items: asArray(asRecord(o.trends).items).map((item) => {
        const i = asRecord(item);
        return {
          trend_code: asString(i.trend_code),
          label: asString(i.label),
          count: asNumber(i.count),
          window_days: asNumber(i.window_days, 7),
        };
      }),
    },
    signals: {
      state: sectionState(o.signals),
      items: asArray(asRecord(o.signals).items).map((item) => {
        const i = asRecord(item);
        return {
          signal_type: asString(i.signal_type),
          label: asString(i.label || i.title),
          title: asString(i.title || i.label),
          summary: typeof i.summary === "string" ? i.summary : undefined,
          change_percent: typeof i.change_percent === "number" ? i.change_percent : undefined,
          severity: typeof i.severity === "string" ? i.severity : undefined,
        };
      }),
    },
    recent_activity: {
      state: sectionState(o.recent_activity),
      items: parseEventItems(o.recent_activity),
    },
    next_best_action: {
      state: sectionState(o.next_best_action),
      item: isRecord(asRecord(o.next_best_action).item)
        ? {
            action_id: asString(asRecord(asRecord(o.next_best_action).item).action_id),
            label: asString(asRecord(asRecord(o.next_best_action).item).label),
            reason: asString(asRecord(asRecord(o.next_best_action).item).reason),
            cta_label:
              typeof asRecord(asRecord(o.next_best_action).item).cta_label === "string"
                ? (asRecord(asRecord(o.next_best_action).item).cta_label as string)
                : undefined,
            target_screen:
              typeof asRecord(asRecord(o.next_best_action).item).target_screen === "string"
                ? (asRecord(asRecord(o.next_best_action).item).target_screen as string)
                : undefined,
            priority:
              typeof asRecord(asRecord(o.next_best_action).item).priority === "string"
                ? (asRecord(asRecord(o.next_best_action).item).priority as string)
                : undefined,
          }
        : null,
    },
  };

  for (const key of RUNWAY_PULSE_SECTION_KEYS) {
    if (!(key in pulse)) {
      throw new Error(`parseRunwayPulseResponse: missing section ${key}`);
    }
  }
  return pulse;
}

export function parseRunwayMomentsResponse(raw: unknown): RunwayMomentsResponse {
  const o = asRecord(raw);
  const journey = asRecord(o.journey_hero);
  const emptyItems = { state: "empty" as const, items: [] as TeamOpsEventItem[] };

  const moments: RunwayMomentsResponse = {
    moment_id: asString(o.moment_id),
    moment_type: asString(o.moment_type, "BUSINESS_RUNWAY"),
    moment_name: typeof o.moment_name === "string" ? o.moment_name : null,
    runway_name: typeof o.runway_name === "string" ? o.runway_name : null,
    status: asString(o.status),
    runway_hub: isRecord(o.runway_hub)
      ? {
          cash_available_minor: asNullableNumber(o.runway_hub.cash_available_minor),
          monthly_burn_minor: asNullableNumber(o.runway_hub.monthly_burn_minor),
          runway_months: asNullableNumber(o.runway_hub.runway_months),
          risk_count: asNullableNumber(o.runway_hub.risk_count),
          decision_count: asNullableNumber(o.runway_hub.decision_count),
          operating_currency:
            typeof o.runway_hub.operating_currency === "string"
              ? o.runway_hub.operating_currency
              : null,
        }
      : undefined,
    journey_hero: {
      state: sectionState(journey),
      title: asString(journey.title, "Business Runway"),
      subtitle: typeof journey.subtitle === "string" ? journey.subtitle : undefined,
      activity_count: asNumber(journey.activity_count),
      is_active: typeof journey.is_active === "boolean" ? journey.is_active : undefined,
      runway_months: asNullableNumber(journey.runway_months),
    },
    cash_available: {
      state: sectionState(o.cash_available),
      cash_available_minor: asNumber(asRecord(o.cash_available).cash_available_minor),
      operating_currency:
        typeof asRecord(o.cash_available).operating_currency === "string"
          ? (asRecord(o.cash_available).operating_currency as string)
          : undefined,
    },
    runway_months: {
      state: sectionState(o.runway_months),
      runway_months: asNullableNumber(asRecord(o.runway_months).runway_months),
      runway_goal_months: asNullableNumber(asRecord(o.runway_months).runway_goal_months),
    },
    timeline: {
      state: sectionState(o.timeline),
      items: parseEventItems(o.timeline),
    },
    revenue_updates: {
      state: sectionState(o.revenue_updates),
      items: parseEventItems(o.revenue_updates),
    },
    forecast_changes: {
      state: sectionState(o.forecast_changes),
      items: parseEventItems(o.forecast_changes),
    },
    expense_events: {
      state: sectionState(o.expense_events),
      items: parseEventItems(o.expense_events),
    },
    inflow_events: {
      state: sectionState(o.inflow_events),
      items: parseEventItems(o.inflow_events),
    },
    funding_events: {
      state: sectionState(o.funding_events),
      items: parseEventItems(o.funding_events),
    },
    invoices: isRecord(o.invoices)
      ? {
          state: sectionState(o.invoices),
          items: parseEventItems(o.invoices),
          empty_reason:
            typeof o.invoices.empty_reason === "string" ? o.invoices.empty_reason : undefined,
        }
      : emptyItems,
    payroll: isRecord(o.payroll)
      ? {
          state: sectionState(o.payroll),
          items: parseEventItems(o.payroll),
          empty_reason:
            typeof o.payroll.empty_reason === "string" ? o.payroll.empty_reason : undefined,
        }
      : emptyItems,
    milestones: {
      state: sectionState(o.milestones),
      items: parseEventItems(o.milestones),
    },
    recent_activity: {
      state: sectionState(o.recent_activity),
      items: parseEventItems(o.recent_activity),
    },
  };

  for (const key of RUNWAY_MOMENTS_SECTION_KEYS) {
    if (!(key in moments)) {
      throw new Error(`parseRunwayMomentsResponse: missing section ${key}`);
    }
  }
  return moments;
}

export function mergeOptimisticRunwayEvents(
  items: TeamOpsEventItem[],
  optimistic: TeamOpsEventItem[],
): TeamOpsEventItem[] {
  if (!optimistic.length) return items;
  const ids = new Set(items.map((i) => i.event_id));
  const extra = optimistic.filter((o) => !ids.has(o.event_id));
  return [...extra, ...items].slice(0, 25);
}

export function formatMinorCurrency(minor: number, currency = "INR"): string {
  return `${currency} ${(minor / 100).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}
