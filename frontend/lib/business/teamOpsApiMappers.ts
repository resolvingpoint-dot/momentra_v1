/**
 * Team Ops API parsers + view models.
 * Components must NOT reshape backend payloads — use these helpers only.
 */
import type {
  BusinessActivityListItem,
  BusinessLifeResponse,
  BusinessLifeSlice,
  BusinessMemoryEvent,
  BusinessMemoryResponse,
  TeamOpsEventItem,
  TeamOpsHealth,
  TeamOpsMomentsResponse,
  TeamOpsPulseResponse,
} from "@/lib/api/businessActive";
import {
  TEAM_OPS_LIFE_SLICE_KEYS,
  TEAM_OPS_MOMENTS_SECTION_KEYS,
  TEAM_OPS_PULSE_SECTION_KEYS,
} from "@/lib/api/businessActive";

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}

function asRecord(value: unknown): Record<string, unknown> {
  return isRecord(value) ? value : {};
}

function asNumber(value: unknown, fallback = 0): number {
  return typeof value === "number" && Number.isFinite(value) ? value : fallback;
}

function asString(value: unknown, fallback = ""): string {
  return typeof value === "string" ? value : fallback;
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

function parseHealth(raw: unknown): TeamOpsHealth | undefined {
  if (!isRecord(raw)) return undefined;
  return {
    label: asString(raw.label, "Not started"),
    band: asString(raw.band, "empty"),
    rule: typeof raw.rule === "string" ? raw.rule : undefined,
    score: typeof raw.score === "number" ? raw.score : undefined,
    max_score: typeof raw.max_score === "number" ? raw.max_score : undefined,
    inputs: isRecord(raw.inputs)
      ? Object.fromEntries(
          Object.entries(raw.inputs).map(([k, v]) => [k, asNumber(v)]),
        )
      : undefined,
  };
}

function parseEventItems(raw: unknown): TeamOpsEventItem[] {
  return asArray(asRecord(raw).items).map(parseEvent);
}

function parseState(raw: unknown, fallback = "empty"): string {
  return asString(asRecord(raw).state, fallback);
}

/** Ensure every Pulse section key exists — never invent metric values. */
export function parseTeamOpsPulseResponse(raw: unknown): TeamOpsPulseResponse {
  const o = asRecord(raw);
  const hero = asRecord(o.hero);
  const kpis = asRecord(o.kpis);
  const approvals = asRecord(o.approvals);
  const participation = asRecord(o.participation);
  const issues = asRecord(o.issues);
  const recognition = asRecord(o.recognition);
  const attention = asRecord(o.attention);
  const signals = asRecord(o.signals);
  const healthDrivers = asRecord(o.health_drivers);
  const next = asRecord(o.next_action);
  const nextItem = isRecord(next.item) ? next.item : null;

  const pulse: TeamOpsPulseResponse = {
    moment_id: asString(o.moment_id),
    moment_type: asString(o.moment_type, "TEAM_OPERATIONS"),
    moment_name: typeof o.moment_name === "string" ? o.moment_name : null,
    team_name: typeof o.team_name === "string" ? o.team_name : null,
    status: asString(o.status),
    is_active: asBool(o.is_active),
    member_count: asNumber(o.member_count),
    activity_count: asNumber(o.activity_count),
    operating_currency: asString(o.operating_currency, "INR"),
    stats: isRecord(o.stats)
      ? Object.fromEntries(Object.entries(o.stats).map(([k, v]) => [k, asNumber(v)]))
      : undefined,
    hero: {
      state: asString(hero.state, "empty"),
      title: asString(hero.title, "Team Operations"),
      subtitle: typeof hero.subtitle === "string" ? hero.subtitle : undefined,
      status: typeof hero.status === "string" ? hero.status : undefined,
      is_active: typeof hero.is_active === "boolean" ? hero.is_active : undefined,
      overall_team_health: parseHealth(hero.overall_team_health),
    },
    health_drivers: {
      state: asString(healthDrivers.state, "empty"),
      items: asArray(healthDrivers.items).map((item) => {
        const d = asRecord(item);
        return {
          driver_code: asString(d.driver_code),
          driver_name: asString(d.driver_name),
          score: asNumber(d.score),
          status: asString(d.status, "stable"),
          delta: typeof d.delta === "number" ? d.delta : undefined,
          trend: typeof d.trend === "string" ? d.trend : undefined,
          weight: typeof d.weight === "number" ? d.weight : undefined,
        };
      }),
    },
    kpis: {
      state: asString(kpis.state, "empty"),
      members: asNumber(kpis.members),
      open_issues: asNumber(kpis.open_issues),
      pending_approvals: asNumber(kpis.pending_approvals),
      recognitions: asNumber(kpis.recognitions),
      meetings: asNumber(kpis.meetings),
      escalations: asNumber(kpis.escalations),
      participation: asNumber(kpis.participation),
      overall_team_health: parseHealth(kpis.overall_team_health),
    },
    approvals: {
      state: parseState(approvals),
      pending_count: asNumber(approvals.pending_count),
      items: parseEventItems(approvals),
    },
    participation: {
      state: parseState(participation),
      count: asNumber(participation.count),
      items: parseEventItems(participation),
    },
    issues: {
      state: parseState(issues),
      open_count: asNumber(issues.open_count),
      escalation_count: asNumber(issues.escalation_count),
      items: parseEventItems(issues),
    },
    recognition: {
      state: parseState(recognition),
      count: asNumber(recognition.count),
      items: parseEventItems(recognition),
    },
    recent_activity: {
      state: parseState(o.recent_activity),
      items: parseEventItems(o.recent_activity),
    },
    attention: {
      state: asString(attention.state, "empty"),
      items: asArray(attention.items).map((item) => {
        const a = asRecord(item);
        return {
          kind: asString(a.kind),
          label: asString(a.label),
          count: asNumber(a.count),
          severity: typeof a.severity === "string" ? a.severity : undefined,
          description: typeof a.description === "string" ? a.description : undefined,
        };
      }),
    },
    signals: {
      state: asString(signals.state, "empty"),
      items: asArray(signals.items).map((item) => {
        const s = asRecord(item);
        return {
          signal_id: typeof s.signal_id === "string" ? s.signal_id : undefined,
          signal_type: typeof s.signal_type === "string" ? s.signal_type : undefined,
          title: typeof s.title === "string" ? s.title : undefined,
          label: typeof s.label === "string" ? s.label : undefined,
          summary: typeof s.summary === "string" ? s.summary : undefined,
          change_percent: typeof s.change_percent === "number" ? s.change_percent : undefined,
          priority: typeof s.priority === "string" ? s.priority : undefined,
          severity: typeof s.severity === "string" ? s.severity : undefined,
        };
      }),
    },
    next_action: {
      state: asString(next.state, "empty"),
      item: nextItem
        ? {
            action_id: asString(nextItem.action_id),
            label: asString(nextItem.label),
            reason: asString(nextItem.reason),
            cta_label: typeof nextItem.cta_label === "string" ? nextItem.cta_label : undefined,
            target_screen: typeof nextItem.target_screen === "string" ? nextItem.target_screen : undefined,
            priority: typeof nextItem.priority === "string" ? nextItem.priority : undefined,
          }
        : null,
    },
  };

  for (const key of TEAM_OPS_PULSE_SECTION_KEYS) {
    if (!(key in pulse)) {
      throw new Error(`Pulse parser missing section ${key}`);
    }
  }
  return pulse;
}

function parseMomentsItemsSection(raw: unknown) {
  return {
    state: parseState(raw),
    items: parseEventItems(raw),
    count: typeof asRecord(raw).count === "number" ? asNumber(asRecord(raw).count) : undefined,
    pending_count:
      typeof asRecord(raw).pending_count === "number" ? asNumber(asRecord(raw).pending_count) : undefined,
    open_count:
      typeof asRecord(raw).open_count === "number" ? asNumber(asRecord(raw).open_count) : undefined,
  };
}

function parseProgressItems(raw: unknown) {
  return {
    state: parseState(raw),
    items: asArray(asRecord(raw).items).map((item) => {
      const m = asRecord(item);
      return {
        metric_code: asString(m.metric_code),
        metric_name: asString(m.metric_name),
        score: asNumber(m.score),
        delta: typeof m.delta === "number" ? m.delta : undefined,
        status: typeof m.status === "string" ? m.status : undefined,
        trend: typeof m.trend === "string" ? m.trend : undefined,
      };
    }),
  };
}

export function parseTeamOpsMomentsResponse(raw: unknown): TeamOpsMomentsResponse {
  const o = asRecord(raw);
  const journey = asRecord(o.journey_hero);
  const moments: TeamOpsMomentsResponse = {
    moment_id: asString(o.moment_id),
    moment_type: asString(o.moment_type, "TEAM_OPERATIONS"),
    moment_name: typeof o.moment_name === "string" ? o.moment_name : null,
    team_name: typeof o.team_name === "string" ? o.team_name : null,
    status: asString(o.status),
    operations_hub: isRecord(o.operations_hub)
      ? Object.fromEntries(Object.entries(o.operations_hub).map(([k, v]) => [k, asNumber(v)]))
      : undefined,
    journey_hero: {
      state: asString(journey.state, "empty"),
      title: asString(journey.title, "Team Operations"),
      subtitle: typeof journey.subtitle === "string" ? journey.subtitle : undefined,
      member_count: asNumber(journey.member_count),
      activity_count: asNumber(journey.activity_count),
      is_active: typeof journey.is_active === "boolean" ? journey.is_active : undefined,
    },
    progress_snapshot: parseProgressItems(o.progress_snapshot),
    highlights: parseMomentsItemsSection(o.highlights),
    milestones: parseMomentsItemsSection(o.milestones),
    meetings: parseMomentsItemsSection(o.meetings),
    approvals: parseMomentsItemsSection(o.approvals),
    recognition: parseMomentsItemsSection(o.recognition),
    issues: parseMomentsItemsSection(o.issues),
    team_changes: parseMomentsItemsSection(o.team_changes),
    timeline: parseMomentsItemsSection(o.timeline),
    recent_activity: parseMomentsItemsSection(o.recent_activity),
  };
  for (const key of TEAM_OPS_MOMENTS_SECTION_KEYS) {
    if (!(key in moments)) {
      throw new Error(`Moments parser missing section ${key}`);
    }
  }
  return moments;
}

export function parseBusinessLifeResponse(raw: unknown): BusinessLifeResponse {
  const o = asRecord(raw);
  const slicesRaw = asRecord(o.slices);
  const slices: Record<string, BusinessLifeSlice> = {};
  for (const key of TEAM_OPS_LIFE_SLICE_KEYS) {
    const s = asRecord(slicesRaw[key]);
    slices[key] = {
      key: asString(s.key, key),
      label: asString(s.label, key.replace(/_/g, " ")),
      state: asString(s.state, "empty"),
      count: asNumber(s.count),
      band: typeof s.band === "string" ? s.band : undefined,
      items: asArray(s.items).map(parseEvent),
      inputs: isRecord(s.inputs)
        ? Object.fromEntries(Object.entries(s.inputs).map(([k, v]) => [k, asNumber(v)]))
        : undefined,
      source_moment_id: typeof s.source_moment_id === "string" ? s.source_moment_id : undefined,
      source_moment_name: typeof s.source_moment_name === "string" ? s.source_moment_name : undefined,
    };
  }
  return {
    active_moment_count: asNumber(o.active_moment_count),
    moments: asArray(o.moments).map((m) => {
      const r = asRecord(m);
      return {
        moment_id: asString(r.moment_id),
        moment_type: asString(r.moment_type),
        moment_name: asString(r.moment_name),
        status: asString(r.status),
      };
    }),
    signals: asArray(o.signals),
    dimensions: asArray(o.dimensions),
    slices,
  };
}

export function parseBusinessMemoryResponse(raw: unknown): BusinessMemoryResponse {
  const o = asRecord(raw);
  const parseMemEvent = (rawEvent: unknown): BusinessMemoryEvent => {
    const e = asRecord(rawEvent);
    return {
      event_id: asString(e.event_id),
      action_type: asString(e.action_type),
      title: asString(e.title),
      occurred_at: typeof e.occurred_at === "string" ? e.occurred_at : undefined,
      source_moment_id: typeof e.source_moment_id === "string" ? e.source_moment_id : undefined,
      source_moment_name: typeof e.source_moment_name === "string" ? e.source_moment_name : undefined,
      source_moment_type: typeof e.source_moment_type === "string" ? e.source_moment_type : undefined,
    };
  };
  const bucketsRaw = asRecord(o.buckets);
  const buckets: BusinessMemoryResponse["buckets"] = {};
  for (const [key, value] of Object.entries(bucketsRaw)) {
    const b = asRecord(value);
    buckets[key] = {
      state: asString(b.state, "empty"),
      items: asArray(b.items).map(parseMemEvent),
    };
  }
  return {
    active_moment_count: asNumber(o.active_moment_count),
    moments: asArray(o.moments).map((m) => {
      const r = asRecord(m);
      return {
        moment_id: asString(r.moment_id),
        moment_type: asString(r.moment_type),
        moment_name: asString(r.moment_name),
        status: asString(r.status),
      };
    }),
    patterns: asArray(o.patterns),
    events: asArray(o.events).map(parseMemEvent),
    buckets,
  };
}

export function parseBusinessActivityItem(raw: unknown): BusinessActivityListItem {
  const o = asRecord(raw);
  const actionType = asString(o.action_type);
  const hasApiEditable = typeof o.is_editable === "boolean";
  const hasApiDeletable = typeof o.is_deletable === "boolean";
  const supportedRaw = asArray(o.supported_actions).filter(
    (x): x is string => typeof x === "string",
  );
  return {
    event_id: asString(o.event_id),
    action_type: actionType,
    title: asString(o.title),
    subtitle: typeof o.subtitle === "string" ? o.subtitle : null,
    created_at: typeof o.created_at === "string" ? o.created_at : undefined,
    occurred_at: typeof o.occurred_at === "string" ? o.occurred_at : undefined,
    created_by: typeof o.created_by === "string" ? o.created_by : null,
    source: typeof o.source === "string" ? o.source : null,
    is_voided: typeof o.is_voided === "boolean" ? o.is_voided : false,
    payload: isRecord(o.payload) ? o.payload : undefined,
    is_editable: hasApiEditable ? Boolean(o.is_editable) : false,
    is_deletable: hasApiDeletable ? Boolean(o.is_deletable) : false,
    supported_actions: supportedRaw,
    _flags_from_api: hasApiEditable || hasApiDeletable || supportedRaw.length > 0,
  };
}

export function parseBusinessActivityList(raw: unknown): BusinessActivityListItem[] {
  return asArray(raw).map(parseBusinessActivityItem);
}

export function parseBusinessActivityListResponse(raw: unknown): {
  items: BusinessActivityListItem[];
  total: number;
  page: number;
  page_size: number;
} {
  // Envelope: { items, total, page, page_size }
  if (isRecord(raw) && Array.isArray(raw.items)) {
    return {
      items: asArray(raw.items).map(parseBusinessActivityItem),
      total: typeof raw.total === "number" ? raw.total : asArray(raw.items).length,
      page: typeof raw.page === "number" ? raw.page : 1,
      page_size:
        typeof raw.page_size === "number"
          ? raw.page_size
          : typeof raw.pageSize === "number"
            ? raw.pageSize
            : 20,
    };
  }
  // Legacy bare array (should not happen after Run 8.2 patch)
  const items = parseBusinessActivityList(raw);
  return { items, total: items.length, page: 1, page_size: items.length || 20 };
}

/** Hook/mapper helpers — keep optimistic + source filters out of components. */

export function mergeOptimisticEvents(
  server: TeamOpsEventItem[],
  optimistic: TeamOpsEventItem[],
): TeamOpsEventItem[] {
  const rest = server.filter(
    (e) => !optimistic.some((o) => o.event_id && o.event_id === e.event_id),
  );
  return [...optimistic, ...rest];
}

export function filterEventsByMoment(
  items: TeamOpsEventItem[],
  sourceMomentId: string | null | undefined,
): TeamOpsEventItem[] {
  if (!sourceMomentId) return items;
  return items.filter(
    (i) => !i.source_moment_id || i.source_moment_id === sourceMomentId,
  );
}

export function filterMemoryByMoment(
  items: BusinessMemoryEvent[],
  sourceMomentId: string | null | undefined,
): BusinessMemoryEvent[] {
  if (!sourceMomentId) return items;
  return items.filter(
    (i) => !i.source_moment_id || i.source_moment_id === sourceMomentId,
  );
}

/** Presentation order for Memory contribution buckets (backend allowlist). */
export const MEMORY_BUCKET_ORDER = [
  "milestones",
  "recognitions",
  "resolved_issues",
  "meetings",
  "important_approvals",
  "team_updates",
  "funding",
  "large_payments",
  "revenue_milestones",
  "major_expenses",
  "loans",
  "investments",
  "forecast_changes",
  "runway_risks",
  "major_spend",
  "approval_decisions",
  "vendor_changes",
  "completed_improvements",
  "operational_milestones",
  "key_decisions",
  "recurring_issue_patterns",
  "budget_patterns",
] as const;

export const MEMORY_BUCKET_LABELS: Record<(typeof MEMORY_BUCKET_ORDER)[number], string> = {
  milestones: "Milestones",
  recognitions: "Recognition",
  resolved_issues: "Resolved Issues",
  meetings: "Meetings",
  important_approvals: "Important Approvals",
  team_updates: "Team updates",
  funding: "Funding",
  large_payments: "Large payments",
  revenue_milestones: "Revenue milestones",
  major_expenses: "Major expenses",
  loans: "Loans",
  investments: "Investments",
  forecast_changes: "Forecast changes",
  runway_risks: "Runway risks",
  major_spend: "Major spend",
  approval_decisions: "Approval decisions",
  vendor_changes: "Vendor changes",
  completed_improvements: "Completed improvements",
  operational_milestones: "Operational milestones",
  key_decisions: "Key decisions",
  recurring_issue_patterns: "Recurring issue patterns",
  budget_patterns: "Budget patterns",
};
