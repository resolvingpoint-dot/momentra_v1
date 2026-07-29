/** Pure aggregation helpers for Template Activity category/subcategory pies + chips. */

export const ACTIVITY_FILTER_ALL = "all";
export const ACTIVITY_UNCATEGORIZED_ID = "uncategorized";
export const ACTIVITY_UNCATEGORIZED_LABEL = "Uncategorized";

export type ActivityBreakdownFields = {
  category_code?: string | null;
  category_label?: string | null;
  subcategory_code?: string | null;
  subcategory_label?: string | null;
  amount_minor?: number | null;
};

export type ActivityBreakdownSegment = {
  id: string;
  label: string;
  value: number;
  eventCount: number;
  amountMinor: number;
};

export type ActivityChipOption = {
  id: string;
  label: string;
};

function normalizeToken(raw: string | null | undefined): string {
  return (raw ?? "").trim();
}

function normalizeLabelKey(label: string): string {
  return label.trim().toLowerCase().replace(/\s+/g, " ");
}

export function categoryIdentity(item: ActivityBreakdownFields): { id: string; label: string } {
  const code = normalizeToken(item.category_code);
  if (code) {
    const label = normalizeToken(item.category_label) || code;
    return { id: code, label };
  }
  const label = normalizeToken(item.category_label);
  if (label) return { id: `label:${normalizeLabelKey(label)}`, label };
  return { id: ACTIVITY_UNCATEGORIZED_ID, label: ACTIVITY_UNCATEGORIZED_LABEL };
}

export function subcategoryIdentity(item: ActivityBreakdownFields): { id: string; label: string } {
  const code = normalizeToken(item.subcategory_code);
  if (code) {
    const label = normalizeToken(item.subcategory_label) || code;
    return { id: code, label };
  }
  const label = normalizeToken(item.subcategory_label);
  if (label) return { id: `label:${normalizeLabelKey(label)}`, label };
  return { id: ACTIVITY_UNCATEGORIZED_ID, label: ACTIVITY_UNCATEGORIZED_LABEL };
}

function amountContribution(amountMinor: number | null | undefined): number {
  const n = typeof amountMinor === "number" && Number.isFinite(amountMinor) ? amountMinor : 0;
  return n > 0 ? n : 0;
}

type BucketAcc = { label: string; eventCount: number; amountMinor: number };

function sortSegments(segments: ActivityBreakdownSegment[]): ActivityBreakdownSegment[] {
  return [...segments].sort((a, b) => {
    if (b.value !== a.value) return b.value - a.value;
    return a.label.localeCompare(b.label, undefined, { sensitivity: "base" });
  });
}

function finalizeBuckets(map: Map<string, BucketAcc>): ActivityBreakdownSegment[] {
  const segments: ActivityBreakdownSegment[] = [];
  for (const [id, bucket] of map) {
    const value = bucket.amountMinor > 0 ? bucket.amountMinor : bucket.eventCount;
    segments.push({
      id,
      label: bucket.label,
      value,
      eventCount: bucket.eventCount,
      amountMinor: bucket.amountMinor,
    });
  }
  return sortSegments(segments);
}

function accumulate(
  map: Map<string, BucketAcc>,
  id: string,
  label: string,
  amountMinor: number,
): void {
  const existing = map.get(id);
  if (existing) {
    existing.eventCount += 1;
    existing.amountMinor += amountMinor;
    return;
  }
  map.set(id, { label, eventCount: 1, amountMinor });
}

export function buildCategorySegments(items: ActivityBreakdownFields[]): ActivityBreakdownSegment[] {
  const map = new Map<string, BucketAcc>();
  for (const item of items) {
    const { id, label } = categoryIdentity(item);
    accumulate(map, id, label, amountContribution(item.amount_minor));
  }
  return finalizeBuckets(map);
}

export function buildSubcategorySegments(
  items: ActivityBreakdownFields[],
  categoryFilter: string = ACTIVITY_FILTER_ALL,
): ActivityBreakdownSegment[] {
  const map = new Map<string, BucketAcc>();
  for (const item of items) {
    if (categoryFilter !== ACTIVITY_FILTER_ALL) {
      const cat = categoryIdentity(item);
      if (cat.id !== categoryFilter) continue;
    }
    const { id, label } = subcategoryIdentity(item);
    accumulate(map, id, label, amountContribution(item.amount_minor));
  }
  return finalizeBuckets(map);
}

function chipsFromSegments(segments: ActivityBreakdownSegment[]): ActivityChipOption[] {
  return [
    { id: ACTIVITY_FILTER_ALL, label: "All" },
    ...segments.map((s) => ({ id: s.id, label: s.label })),
  ];
}

export function buildCategoryChipOptions(items: ActivityBreakdownFields[]): ActivityChipOption[] {
  return chipsFromSegments(buildCategorySegments(items));
}

export function buildSubcategoryChipOptions(
  items: ActivityBreakdownFields[],
  categoryFilter: string = ACTIVITY_FILTER_ALL,
): ActivityChipOption[] {
  return chipsFromSegments(buildSubcategorySegments(items, categoryFilter));
}

export function sanitizeFilterId(
  selectedId: string,
  options: ActivityChipOption[],
): string {
  if (selectedId === ACTIVITY_FILTER_ALL) return ACTIVITY_FILTER_ALL;
  return options.some((o) => o.id === selectedId) ? selectedId : ACTIVITY_FILTER_ALL;
}

export function itemMatchesCategory(
  item: ActivityBreakdownFields,
  categoryFilter: string,
): boolean {
  if (categoryFilter === ACTIVITY_FILTER_ALL) return true;
  return categoryIdentity(item).id === categoryFilter;
}

export function itemMatchesSubcategory(
  item: ActivityBreakdownFields,
  subcategoryFilter: string,
): boolean {
  if (subcategoryFilter === ACTIVITY_FILTER_ALL) return true;
  return subcategoryIdentity(item).id === subcategoryFilter;
}

export function colorIndexForSegmentId(id: string, paletteSize: number): number {
  if (paletteSize <= 0) return 0;
  let hash = 0;
  for (let i = 0; i < id.length; i += 1) {
    hash = (hash * 31 + id.charCodeAt(i)) >>> 0;
  }
  return hash % paletteSize;
}
