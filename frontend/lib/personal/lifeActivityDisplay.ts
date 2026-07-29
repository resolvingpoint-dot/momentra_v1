/** Display helpers for Life OS unified Activity timeline. */

export type LifeActivityItem = {
  id: string;
  title?: string | null;
  subtitle?: string | null;
  occurred_at: string;
  amount_minor?: number | null;
  amount_label?: string | null;
  category_label?: string | null;
  subcategory_label?: string | null;
  mood_label?: string | null;
  mood?: { label?: string | null; code?: string | null } | null;
  domain_label?: string | null;
  type_label?: string | null;
  life_domain?: string | null;
  primary_metric?: { display?: string | null; kind?: string | null } | null;
  impact_label?: string | null;
  activity_type?: string | null;
  moment_type_code?: string | null;
  icon?: string | null;
  color?: string | null;
  category_code?: string | null;
  subcategory_code?: string | null;
  can_edit?: boolean;
  editable?: boolean;
  edit_event_type?: string;
};

export type LifeDayGroup = "Today" | "Yesterday" | string | "Last Week" | "Earlier";

export type LifeChapter = "Morning" | "Afternoon" | "Evening";

export function lifeActivityTitle(item: LifeActivityItem): string {
  const raw = ((item.title ?? "").trim() || (item.subtitle ?? "").trim());
  if (!raw) return "Moment";
  if (raw === raw.toLowerCase() || raw === raw.toUpperCase()) {
    return raw
      .toLowerCase()
      .split(/\s+/)
      .map((w) => (w.length ? w[0].toUpperCase() + w.slice(1) : w))
      .join(" ");
  }
  return raw;
}

export function lifeActivityDomain(item: LifeActivityItem): string {
  return (item.life_domain || item.domain_label || "Personal").trim() || "Personal";
}

export function lifeActivityMetric(item: LifeActivityItem): string | null {
  const fromPrimary = (item.primary_metric?.display ?? "").trim();
  if (fromPrimary) return fromPrimary;
  const amount = (item.amount_label ?? "").trim();
  if (amount) return amount;
  const minor = item.amount_minor ?? 0;
  if (minor > 0) {
    return `₹${(minor / 100).toLocaleString("en-IN", { maximumFractionDigits: 0 })}`;
  }
  return null;
}

export function lifeActivityContextLine(item: LifeActivityItem): string {
  const type = (item.type_label ?? "").trim();
  const category = (item.category_label ?? "").trim();
  const subcategory = (item.subcategory_label ?? "").trim();
  const impact = (item.impact_label ?? "").trim();
  const parts: string[] = [];
  if (type) parts.push(type);
  else if (category) parts.push(category);
  const second = subcategory || (category && type && category.toLowerCase() !== type.toLowerCase() ? category : "") || impact;
  if (second && !parts.some((p) => p.toLowerCase() === second.toLowerCase())) {
    parts.push(second);
  }
  return parts.slice(0, 2).join(" · ") || "Moment";
}

export function lifeActivityMood(item: LifeActivityItem): string | null {
  const fromObj = (item.mood?.label ?? "").trim();
  if (fromObj) return fromObj;
  const legacy = (item.mood_label ?? "").trim();
  return legacy || null;
}

export function lifeDayGroupLabel(iso: string, now = new Date()): LifeDayGroup {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "Earlier";
  const startToday = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const startYesterday = new Date(startToday);
  startYesterday.setDate(startYesterday.getDate() - 1);
  const startWeek = new Date(startToday);
  startWeek.setDate(startWeek.getDate() - 6);
  const startLastWeek = new Date(startToday);
  startLastWeek.setDate(startLastWeek.getDate() - 13);

  if (d >= startToday) return "Today";
  if (d >= startYesterday) return "Yesterday";
  if (d >= startWeek) {
    return d.toLocaleDateString("en-US", { weekday: "long" });
  }
  if (d >= startLastWeek) return "Last Week";
  return "Earlier";
}

export function lifeChapter(iso: string): LifeChapter {
  const d = new Date(iso);
  const hour = Number.isNaN(d.getTime()) ? 12 : d.getHours();
  if (hour < 12) return "Morning";
  if (hour < 17) return "Afternoon";
  return "Evening";
}

export function groupLifeActivities<T extends { occurred_at: string }>(
  items: T[],
  now = new Date(),
): Array<{ label: LifeDayGroup; items: T[] }> {
  const map = new Map<string, T[]>();
  const order: string[] = [];
  for (const item of items) {
    const label = lifeDayGroupLabel(item.occurred_at, now);
    if (!map.has(label)) {
      map.set(label, []);
      order.push(label);
    }
    map.get(label)!.push(item);
  }
  // Stable preferred order for known labels; weekdays keep insertion order among themselves
  const preferred = ["Today", "Yesterday"];
  const tail = ["Last Week", "Earlier"];
  const weekdays = order.filter((l) => !preferred.includes(l) && !tail.includes(l));
  const sorted = [
    ...preferred.filter((l) => map.has(l)),
    ...weekdays,
    ...tail.filter((l) => map.has(l)),
  ];
  return sorted.map((label) => ({ label, items: map.get(label)! }));
}

export function chapterizeDay<T extends { occurred_at: string }>(
  items: T[],
): Array<{ chapter: LifeChapter; items: T[] }> {
  const buckets: Record<LifeChapter, T[]> = {
    Morning: [],
    Afternoon: [],
    Evening: [],
  };
  for (const item of items) {
    buckets[lifeChapter(item.occurred_at)].push(item);
  }
  const present = (["Morning", "Afternoon", "Evening"] as LifeChapter[]).filter(
    (c) => buckets[c].length > 0,
  );
  if (present.length <= 1) {
    return [{ chapter: present[0] ?? "Morning", items }];
  }
  return present.map((chapter) => ({ chapter, items: buckets[chapter] }));
}

export function formatInrMinor(minor: number): string {
  if (minor <= 0) return "₹0";
  return `₹${(minor / 100).toLocaleString("en-IN", { maximumFractionDigits: 0 })}`;
}
