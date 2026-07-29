/**
 * Business Operations API parsers — components must not reshape backend payloads.
 */
import type {
  OpsHealthBand,
  OpsMilestoneItem,
  OpsMomentsResponse,
  OpsPulseResponse,
  TeamOpsEventItem,
} from "@/lib/api/businessActive";
import { OPS_MOMENTS_SECTION_KEYS, OPS_PULSE_SECTION_KEYS } from "@/lib/api/businessActive";

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

function sectionState(raw: unknown): string {
  return asString(asRecord(raw).state, "empty");
}

function normalizeBand(raw: unknown): OpsHealthBand {
  const band = asString(raw, "EMPTY").toUpperCase();
  if (band === "HEALTHY" || band === "NEEDS_ATTENTION" || band === "AT_RISK" || band === "EMPTY") {
    return band;
  }
  // Tolerate legacy lowercase from other templates; never invent a score.
  if (band === "ATTENTION") return "NEEDS_ATTENTION";
  if (band === "CRITICAL") return "AT_RISK";
  return band || "EMPTY";
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

function parseEventItems(raw: unknown): TeamOpsEventItem[] {
  return asArray(asRecord(raw).items).map(parseEvent);
}

function parseMilestone(raw: unknown): OpsMilestoneItem {
  const o = asRecord(raw);
  return {
    kind: typeof o.kind === "string" ? o.kind : undefined,
    title: asString(o.title),
    occurred_at: typeof o.occurred_at === "string" ? o.occurred_at : null,
    event_id: typeof o.event_id === "string" ? o.event_id : undefined,
  };
}

function parseNullableString(value: unknown): string | null {
  return typeof value === "string" ? value : null;
}

export function parseOpsPulseResponse(raw: unknown): OpsPulseResponse {
  const o = asRecord(raw);
  const hero = asRecord(o.hero);
  const health = asRecord(o.operations_health);
  const nba = asRecord(o.next_best_action);
  const nbaItem = asRecord(nba.item);

  const pulse: OpsPulseResponse = {
    moment_id: asString(o.moment_id),
    moment_type: asString(o.moment_type, "BUSINESS_OPERATIONS"),
    moment_name: parseNullableString(o.moment_name),
    operations_name: parseNullableString(o.operations_name),
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
      moment_name: asString(hero.moment_name || o.moment_name),
      operations_name: asString(hero.operations_name || o.operations_name),
      operations_scope: parseNullableString(hero.operations_scope),
      operating_model: parseNullableString(hero.operating_model),
      owner: parseNullableString(hero.owner),
      last_updated: parseNullableString(hero.last_updated),
      title: typeof hero.title === "string" ? hero.title : undefined,
      subtitle: typeof hero.subtitle === "string" ? hero.subtitle : undefined,
    },
    operations_health: {
      state: sectionState(health),
      label: asString(health.label, "Not started"),
      band: normalizeBand(health.band),
      rule: typeof health.rule === "string" ? health.rule : undefined,
      drivers: isRecord(health.drivers)
        ? Object.fromEntries(
            Object.entries(health.drivers).map(([k, v]) => [
              k,
              typeof v === "number" ? v : v === null ? null : asNumber(v),
            ]),
          )
        : undefined,
    },
    kpis: {
      state: sectionState(o.kpis),
      monthly_budget_minor: asNullableNumber(asRecord(o.kpis).monthly_budget_minor),
      spent_minor: asNullableNumber(asRecord(o.kpis).spent_minor),
      remaining_minor: asNullableNumber(asRecord(o.kpis).remaining_minor),
      budget_usage_percent: asNullableNumber(asRecord(o.kpis).budget_usage_percent),
      pending_approval_count: asNullableNumber(asRecord(o.kpis).pending_approval_count),
      open_issue_count: asNullableNumber(asRecord(o.kpis).open_issue_count),
      active_vendor_count: asNullableNumber(asRecord(o.kpis).active_vendor_count),
      completed_improvement_count: asNullableNumber(
        asRecord(o.kpis).completed_improvement_count,
      ),
    },
    budget_usage: {
      state: sectionState(o.budget_usage),
      total_budget_minor: asNumber(asRecord(o.budget_usage).total_budget_minor),
      total_spend_minor: asNumber(asRecord(o.budget_usage).total_spend_minor),
      remaining_minor: asNumber(asRecord(o.budget_usage).remaining_minor),
      allocations: asArray(asRecord(o.budget_usage).allocations),
      over_budget_allocations: asArray(asRecord(o.budget_usage).over_budget_allocations),
      unallocated_minor: asNumber(asRecord(o.budget_usage).unallocated_minor),
      operating_currency: asString(
        asRecord(o.budget_usage).operating_currency,
        asString(o.operating_currency, "INR"),
      ),
    },
    approvals: {
      state: sectionState(o.approvals),
      pending: asNumber(asRecord(o.approvals).pending),
      overdue: asNumber(asRecord(o.approvals).overdue),
      approved_recently: asNumber(asRecord(o.approvals).approved_recently),
      rejected_recently: asNumber(asRecord(o.approvals).rejected_recently),
      amount_awaiting_minor: asNullableNumber(asRecord(o.approvals).amount_awaiting_minor),
    },
    issues: {
      state: sectionState(o.issues),
      open: asNumber(asRecord(o.issues).open),
      critical: asNumber(asRecord(o.issues).critical),
      overdue: asNumber(asRecord(o.issues).overdue),
      unassigned: asNumber(asRecord(o.issues).unassigned),
      resolved_recently: asNumber(asRecord(o.issues).resolved_recently),
    },
    vendors: {
      state: sectionState(o.vendors),
      active: asNumber(asRecord(o.vendors).active),
      status_changes: asNumber(asRecord(o.vendors).status_changes),
      critical_dependencies: asNumber(asRecord(o.vendors).critical_dependencies),
      unresolved_events: asNumber(asRecord(o.vendors).unresolved_events),
    },
    improvements: {
      state: sectionState(o.improvements),
      planned: asNumber(asRecord(o.improvements).planned),
      in_progress: asNumber(asRecord(o.improvements).in_progress),
      completed: asNumber(asRecord(o.improvements).completed),
      overdue: asNumber(asRecord(o.improvements).overdue),
    },
    monitoring: {
      state: sectionState(o.monitoring),
      level: parseNullableString(asRecord(o.monitoring).level),
      active_alerts: asArray(asRecord(o.monitoring).active_alerts),
      recipients: asArray(asRecord(o.monitoring).recipients),
    },
    attention_items: {
      state: sectionState(o.attention_items),
      items: asArray(asRecord(o.attention_items).items).map((item) => {
        const i = asRecord(item);
        return {
          kind: asString(i.kind),
          label: asString(i.label),
          count: typeof i.count === "number" ? i.count : undefined,
          severity: typeof i.severity === "string" ? i.severity : undefined,
          description: typeof i.description === "string" ? i.description : undefined,
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
      state: sectionState(nba),
      item: isRecord(nba.item)
        ? {
            action_id: asString(nbaItem.action_id),
            renderer_id: typeof nbaItem.renderer_id === "string" ? nbaItem.renderer_id : undefined,
            title: typeof nbaItem.title === "string" ? nbaItem.title : undefined,
            label: asString(nbaItem.label || nbaItem.title),
            subtitle: typeof nbaItem.subtitle === "string" ? nbaItem.subtitle : undefined,
            reason: typeof nbaItem.reason === "string" ? nbaItem.reason : undefined,
            cta_label: typeof nbaItem.cta_label === "string" ? nbaItem.cta_label : undefined,
            metadata: isRecord(nbaItem.metadata) ? nbaItem.metadata : undefined,
          }
        : null,
    },
  };

  for (const key of OPS_PULSE_SECTION_KEYS) {
    if (!(key in pulse)) {
      throw new Error(`parseOpsPulseResponse: missing section ${key}`);
    }
  }
  return pulse;
}

export function parseOpsMomentsResponse(raw: unknown): OpsMomentsResponse {
  const o = asRecord(raw);
  const journey = asRecord(o.journey_hero);
  const summary = asRecord(o.summary_stats);

  const moments: OpsMomentsResponse = {
    moment_id: asString(o.moment_id),
    moment_type: asString(o.moment_type, "BUSINESS_OPERATIONS"),
    moment_name: parseNullableString(o.moment_name),
    operations_name: parseNullableString(o.operations_name),
    status: asString(o.status),
    journey_hero: {
      state: sectionState(journey),
      title: asString(journey.title, "Business Operations"),
      start_date: parseNullableString(journey.start_date),
      current_phase: parseNullableString(journey.current_phase),
      progress_percent: asNullableNumber(journey.progress_percent),
      subtitle: typeof journey.subtitle === "string" ? journey.subtitle : undefined,
    },
    summary_stats: {
      state: sectionState(summary),
      budget_used_percent: asNumber(summary.budget_used_percent),
      approvals: asNumber(summary.approvals),
      open_issues: asNumber(summary.open_issues),
      vendors: asNumber(summary.vendors),
      improvements: asNumber(summary.improvements),
    },
    spend_timeline: {
      state: sectionState(o.spend_timeline),
      items: parseEventItems(o.spend_timeline),
    },
    approval_timeline: {
      state: sectionState(o.approval_timeline),
      items: parseEventItems(o.approval_timeline),
    },
    issue_timeline: {
      state: sectionState(o.issue_timeline),
      items: parseEventItems(o.issue_timeline),
    },
    vendor_timeline: {
      state: sectionState(o.vendor_timeline),
      items: parseEventItems(o.vendor_timeline),
    },
    improvement_timeline: {
      state: sectionState(o.improvement_timeline),
      items: parseEventItems(o.improvement_timeline),
    },
    milestones: {
      state: sectionState(o.milestones),
      items: asArray(asRecord(o.milestones).items).map(parseMilestone),
    },
    key_decisions: {
      state: sectionState(o.key_decisions),
      items: parseEventItems(o.key_decisions),
    },
    timeline: {
      state: sectionState(o.timeline),
      items: parseEventItems(o.timeline),
    },
    recent_activity: {
      state: sectionState(o.recent_activity),
      items: parseEventItems(o.recent_activity),
    },
  };

  for (const key of OPS_MOMENTS_SECTION_KEYS) {
    if (!(key in moments)) {
      throw new Error(`parseOpsMomentsResponse: missing section ${key}`);
    }
  }
  return moments;
}

export function mergeOptimisticOpsEvents(
  items: TeamOpsEventItem[],
  optimistic: TeamOpsEventItem[],
): TeamOpsEventItem[] {
  if (!optimistic.length) return items;
  const ids = new Set(items.map((i) => i.event_id));
  const extra = optimistic.filter((o) => !ids.has(o.event_id));
  return [...extra, ...items].slice(0, 25);
}

export function formatMinorCurrency(minor: number, currency = "INR"): string {
  return `${currency} ${(minor / 100).toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
}
