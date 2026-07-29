import type { ReferenceItem } from "@/lib/reference_data/types";
import { getReferenceData } from "@/lib/reference_data/referenceDataStore";

/** Seed fallback when reference bootstrap is missing or stale (no nested children). */
export const EXPENSE_CATEGORY_SEED: ReferenceItem[] = [
  {
    code: "FOOD",
    label: "Food",
    taxonomy: "EXPENSE",
    children: [
      { code: "GROCERIES", label: "Groceries", taxonomy: "EXPENSE" },
      { code: "DINING_OUT", label: "Dining out", taxonomy: "EXPENSE" },
      { code: "COFFEE", label: "Coffee", taxonomy: "EXPENSE" },
    ],
  },
  {
    code: "TRANSPORT",
    label: "Transport",
    taxonomy: "EXPENSE",
    children: [
      { code: "FUEL", label: "Fuel", taxonomy: "EXPENSE" },
      { code: "RIDESHARE", label: "Rideshare", taxonomy: "EXPENSE" },
      { code: "TRANSIT", label: "Transit", taxonomy: "EXPENSE" },
    ],
  },
  {
    code: "HOUSING",
    label: "Housing",
    taxonomy: "EXPENSE",
    children: [
      { code: "RESIDENTIAL_RENT", label: "Residential rent", taxonomy: "EXPENSE" },
      { code: "UTILITIES", label: "Utilities", taxonomy: "EXPENSE" },
      { code: "MAINTENANCE", label: "Maintenance", taxonomy: "EXPENSE" },
    ],
  },
  {
    code: "HEALTH",
    label: "Health",
    taxonomy: "EXPENSE",
    children: [
      { code: "PHARMACY", label: "Pharmacy", taxonomy: "EXPENSE" },
      { code: "CLINIC", label: "Clinic", taxonomy: "EXPENSE" },
    ],
  },
  {
    code: "ENTERTAINMENT",
    label: "Entertainment",
    taxonomy: "EXPENSE",
    children: [
      { code: "MOVIES", label: "Movies", taxonomy: "EXPENSE" },
      { code: "SUBSCRIPTIONS", label: "Subscriptions", taxonomy: "EXPENSE" },
    ],
  },
  { code: "OTHER", label: "Other", taxonomy: "EXPENSE", children: [] },
];

const KEY_ALIASES: Record<string, string[]> = {
  expense_categories: ["expense_categories", "expense"],
  income_categories: ["income_categories", "income"],
};

function nestFlatExpenseParents(rows: ReferenceItem[]): ReferenceItem[] {
  const parents = rows.filter((r) => !r.parent_code);
  if (parents.some((p) => (p.children?.length ?? 0) > 0)) {
    return parents;
  }
  const byParent = new Map<string, ReferenceItem[]>();
  for (const row of rows) {
    if (!row.parent_code) continue;
    const key = String(row.parent_code).toUpperCase();
    const list = byParent.get(key) ?? [];
    list.push(row);
    byParent.set(key, list);
  }
  if (byParent.size === 0) return parents.length ? parents : rows;
  return parents.map((p) => ({
    ...p,
    children: byParent.get(String(p.code).toUpperCase()) ?? p.children ?? [],
  }));
}

export function resolveExpenseCategories(
  quickAddOptions?: Record<string, unknown> | null,
): ReferenceItem[] {
  const resolved = resolveOptionsRef("reference_data.expense_categories", quickAddOptions);
  const nested = nestFlatExpenseParents(resolved);
  const withChildren = nested.filter((p) => !p.parent_code);
  if (withChildren.some((p) => (p.children?.length ?? 0) > 0)) {
    return withChildren;
  }
  if (withChildren.length > 0) {
    // Parents present but no children (stale cache) — merge seed children by code.
    return EXPENSE_CATEGORY_SEED.map((seed) => {
      const match = withChildren.find((p) => p.code === seed.code);
      return match
        ? { ...match, children: match.children?.length ? match.children : seed.children }
        : seed;
    });
  }
  return EXPENSE_CATEGORY_SEED;
}

export function resolveOptionsRef(
  optionsRef: string,
  quickAddOptions?: Record<string, unknown> | null,
): ReferenceItem[] {
  const key = optionsRef.replace(/^reference_data\./, "").replace(/^metadata\./, "");
  const aliases = KEY_ALIASES[key] ?? [key];

  for (const alias of aliases) {
    const fromQuickAdd = quickAddOptions?.[alias];
    if (Array.isArray(fromQuickAdd) && fromQuickAdd.length > 0) {
      return fromQuickAdd as ReferenceItem[];
    }
  }

  const store = getReferenceData();
  if (store) {
    for (const alias of aliases) {
      if (alias in store.categories) {
        const rows = store.categories[alias] ?? [];
        if (rows.length > 0) return rows;
      }
    }
    for (const alias of aliases) {
      const collection = (store as Record<string, unknown>)[alias];
      if (Array.isArray(collection) && collection.length > 0) {
        return collection as ReferenceItem[];
      }
    }
  }

  return [];
}
