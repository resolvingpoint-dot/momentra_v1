/** Shared display helpers for personal Recent Activity timeline rows. */

export type RecentActivityMood = {
  code?: string | null;
  label?: string | null;
  intensity?: string | null;
  source?: string | null;
};

export type RecentActivityPrimaryMetric = {
  kind?: string | null;
  display?: string | null;
  amount_minor?: number | null;
  currency_code?: string | null;
};

export type RecentActivityChip = {
  code?: string | null;
  label?: string | null;
};

export type RecentActivityDisplayFields = {
  title?: string | null;
  subtitle?: string | null;
  detail_line?: string | null;
  category_label?: string | null;
  subcategory_label?: string | null;
  mood_label?: string | null;
  mood?: RecentActivityMood | null;
  amount_label?: string | null;
  impact_label?: string | null;
  domain_label?: string | null;
  type_label?: string | null;
  domain_type_subtitle?: string | null;
  primary_metric?: RecentActivityPrimaryMetric | null;
  chips?: RecentActivityChip[] | null;
  activity_type?: string | null;
  event_type?: string | null;
  can_edit?: boolean | null;
  editable?: boolean | null;
  occurred_at?: string | null;
  captured_at?: string | null;
  relative_time?: string | null;
};

/** Light title-case for display; preserves intentional ALL CAPS words. */
export function recentActivityTitle(item: RecentActivityDisplayFields): string {
  const raw = ((item.title ?? "").trim() || (item.subtitle ?? item.detail_line ?? "").trim());
  if (!raw) return "";
  // Only auto-case when the whole string is lowercase / messy.
  if (raw === raw.toLowerCase() || raw === raw.toUpperCase()) {
    return raw
      .toLowerCase()
      .split(/\s+/)
      .map((w) => (w.length ? w[0].toUpperCase() + w.slice(1) : w))
      .join(" ");
  }
  return raw;
}

export function recentActivityDomainTypeLine(item: RecentActivityDisplayFields): string | null {
  const composed = (item.domain_type_subtitle ?? "").trim();
  if (composed) return composed;
  const domain = (item.domain_label ?? "").trim();
  const type = (item.type_label ?? "").trim();
  if (domain && type) return `${domain} · ${type}`;
  if (domain) return domain;
  if (type) return type;
  return recentActivityCategoryLine(item);
}

export function recentActivityCategoryLine(item: RecentActivityDisplayFields): string | null {
  const category = (item.category_label ?? "").trim();
  const subcategory = (item.subcategory_label ?? "").trim();
  if (category && subcategory) return `${category} · ${subcategory}`;
  if (category) return category;
  if (subcategory) return subcategory;
  return null;
}

/**
 * Single compressed context line for the timeline row:
 * Type • Status  (mood rendered separately with a status dot)
 * Never repeats the same token twice.
 */
export function recentActivityContextParts(item: RecentActivityDisplayFields): string[] {
  const parts: string[] = [];
  const seen = new Set<string>();

  const push = (value: string | null | undefined) => {
    const v = (value ?? "").trim();
    if (!v) return;
    const key = v.toLowerCase();
    if (seen.has(key)) return;
    // Skip tokens already contained in a previous part (e.g. "Expense" after "My Money · Expense")
    for (const existing of seen) {
      if (existing.includes(key) || key.includes(existing)) return;
    }
    seen.add(key);
    parts.push(v);
  };

  // Prefer human type label; fall back to category when type missing.
  const type = (item.type_label ?? "").trim();
  const category = (item.category_label ?? "").trim();
  if (type) {
    push(type);
  } else if (category) {
    push(category);
  } else {
    const domainType = recentActivityDomainTypeLine(item);
    if (domainType) {
      // Prefer the right-hand side of "Domain · Type"
      const bits = domainType.split("·").map((s) => s.trim()).filter(Boolean);
      push(bits[bits.length - 1] ?? domainType);
    }
  }

  const impact = (item.impact_label ?? "").trim();
  if (impact) push(impact);

  return parts.slice(0, 3);
}

export function recentActivityContextLine(item: RecentActivityDisplayFields): string | null {
  const parts = recentActivityContextParts(item);
  return parts.length > 0 ? parts.join(" · ") : null;
}

export function recentActivityMoodLabel(item: RecentActivityDisplayFields): string | null {
  const fromObj = (item.mood?.label ?? "").trim();
  if (fromObj) {
    const intensity = (item.mood?.intensity ?? "").trim();
    return intensity ? `${fromObj} · ${intensity}` : fromObj;
  }
  const legacy = (item.mood_label ?? "").trim();
  return legacy || null;
}

export function recentActivityMoodTone(
  item: RecentActivityDisplayFields,
): "good" | "calm" | "focus" | "tired" | "neutral" {
  const code = (item.mood?.code ?? item.mood_label ?? "").toUpperCase();
  if (!code) return "neutral";
  if (/(GOOD|HAPPY|ENERG|MOTIV|PROUD|GREAT)/.test(code)) return "good";
  if (/(CALM|OKAY|OK|PEACE|RELAX)/.test(code)) return "calm";
  if (/(FOCUS|PRODUCTIV|FLOW)/.test(code)) return "focus";
  if (/(TIRED|STRESS|SAD|LOW|ANX)/.test(code)) return "tired";
  return "neutral";
}

export function recentActivityPrimaryMetric(item: RecentActivityDisplayFields): string | null {
  const fromObj = (item.primary_metric?.display ?? "").trim();
  if (fromObj) return fromObj;
  const amount = (item.amount_label ?? "").trim();
  return amount || null;
}

/** @deprecated Prefer context line + mood + metric. */
export function recentActivityMetaLine(item: RecentActivityDisplayFields): string | null {
  const parts = [...recentActivityContextParts(item)];
  const mood = recentActivityMoodLabel(item);
  if (mood) parts.push(mood);
  return parts.length > 0 ? parts.join(" · ") : null;
}

export function recentActivityChips(item: RecentActivityDisplayFields, max = 2): string[] {
  return recentActivityContextParts(item).slice(0, max);
}

export function recentActivityIsEditable(item: RecentActivityDisplayFields): boolean {
  if (typeof item.editable === "boolean") return item.editable;
  if (typeof item.can_edit === "boolean") return item.can_edit;
  return true;
}

/**
 * Client-side relative age from an ISO timestamp (source of truth for UI).
 * Thresholds match backend: <1m Just now, <60m Nm ago, <24h Nh ago, else Nd ago.
 * Negative / future deltas clamp to "Just now".
 */
export function formatRelativeTime(iso: string, now: Date = new Date()): string {
  const when = new Date(iso);
  if (Number.isNaN(when.getTime())) return "Just now";
  let seconds = (now.getTime() - when.getTime()) / 1000;
  if (seconds < 0) seconds = 0;
  const minutes = Math.floor(seconds / 60);
  if (minutes < 1) return "Just now";
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  return `${Math.floor(hours / 24)}d ago`;
}

export type ActivityDateGroup = "Today" | "Yesterday" | "This Week" | "Earlier";

export function activityDateGroupLabel(iso: string, now = new Date()): ActivityDateGroup {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "Earlier";
  const startOfToday = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const startOfYesterday = new Date(startOfToday);
  startOfYesterday.setDate(startOfYesterday.getDate() - 1);
  const startOfWeek = new Date(startOfToday);
  startOfWeek.setDate(startOfWeek.getDate() - 6);
  if (d >= startOfToday) return "Today";
  if (d >= startOfYesterday) return "Yesterday";
  if (d >= startOfWeek) return "This Week";
  return "Earlier";
}

export function groupActivitiesByDate<T extends { occurred_at?: string; captured_at?: string }>(
  items: T[],
): Array<{ label: ActivityDateGroup; items: T[] }> {
  const order: ActivityDateGroup[] = ["Today", "Yesterday", "This Week", "Earlier"];
  const map = new Map<ActivityDateGroup, T[]>();
  for (const item of items) {
    const iso = item.occurred_at || item.captured_at || "";
    const label = activityDateGroupLabel(iso);
    if (!map.has(label)) map.set(label, []);
    map.get(label)!.push(item);
  }
  return order.filter((k) => map.has(k)).map((k) => ({ label: k, items: map.get(k)! }));
}
