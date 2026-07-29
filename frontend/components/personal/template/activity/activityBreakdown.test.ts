import { describe, expect, it } from "vitest";
import {
  ACTIVITY_FILTER_ALL,
  ACTIVITY_UNCATEGORIZED_ID,
  ACTIVITY_UNCATEGORIZED_LABEL,
  buildCategoryChipOptions,
  buildCategorySegments,
  buildSubcategoryChipOptions,
  buildSubcategorySegments,
  categoryIdentity,
  sanitizeFilterId,
  subcategoryIdentity,
} from "@/components/personal/template/activity/activityBreakdown";

describe("activityBreakdown", () => {
  it("amount-weights categories when totals are positive", () => {
    const segments = buildCategorySegments([
      { category_code: "FOOD", category_label: "Food", amount_minor: 50000 },
      { category_code: "FOOD", category_label: "Food", amount_minor: 20000 },
      { category_code: "TRAVEL", category_label: "Travel", amount_minor: 10000 },
    ]);
    expect(segments[0]).toMatchObject({ id: "FOOD", value: 70000, eventCount: 2, amountMinor: 70000 });
    expect(segments[1]).toMatchObject({ id: "TRAVEL", value: 10000, eventCount: 1 });
  });

  it("count-weights categories when amounts are zero", () => {
    const segments = buildCategorySegments([
      { category_code: "MOOD", category_label: "Mood", amount_minor: 0 },
      { category_code: "MOOD", category_label: "Mood", amount_minor: 0 },
      { category_code: "BOND", category_label: "Bond", amount_minor: 0 },
    ]);
    expect(segments[0]).toMatchObject({ id: "MOOD", value: 2, eventCount: 2, amountMinor: 0 });
    expect(segments[1]).toMatchObject({ id: "BOND", value: 1, eventCount: 1 });
  });

  it("uses amount for mixed money and non-money buckets when sum > 0", () => {
    const segments = buildCategorySegments([
      { category_code: "FOOD", category_label: "Food", amount_minor: 30000 },
      { category_code: "FOOD", category_label: "Food", amount_minor: 0 },
    ]);
    expect(segments[0]).toMatchObject({ id: "FOOD", value: 30000, eventCount: 2, amountMinor: 30000 });
  });

  it("falls back to Uncategorized for missing category", () => {
    expect(categoryIdentity({})).toEqual({
      id: ACTIVITY_UNCATEGORIZED_ID,
      label: ACTIVITY_UNCATEGORIZED_LABEL,
    });
    const segments = buildCategorySegments([{ amount_minor: 0 }]);
    expect(segments[0].id).toBe(ACTIVITY_UNCATEGORIZED_ID);
    expect(segments[0].label).toBe(ACTIVITY_UNCATEGORIZED_LABEL);
  });

  it("falls back to Uncategorized for missing subcategory", () => {
    expect(subcategoryIdentity({ category_code: "FOOD" })).toEqual({
      id: ACTIVITY_UNCATEGORIZED_ID,
      label: ACTIVITY_UNCATEGORIZED_LABEL,
    });
  });

  it("deduplicates category chips by code", () => {
    const chips = buildCategoryChipOptions([
      { category_code: "FOOD", category_label: "Food", amount_minor: 1 },
      { category_code: "FOOD", category_label: "Food & Drink", amount_minor: 2 },
      { category_code: "TRAVEL", category_label: "Travel", amount_minor: 3 },
    ]);
    expect(chips[0]).toEqual({ id: ACTIVITY_FILTER_ALL, label: "All" });
    expect(chips.filter((c) => c.id === "FOOD")).toHaveLength(1);
    expect(chips.some((c) => c.id === "TRAVEL")).toBe(true);
  });

  it("scopes subcategory options to selected category", () => {
    const items = [
      {
        category_code: "FOOD",
        category_label: "Food",
        subcategory_code: "DINING",
        subcategory_label: "Dining",
        amount_minor: 100,
      },
      {
        category_code: "FOOD",
        category_label: "Food",
        subcategory_code: "GROCERY",
        subcategory_label: "Grocery",
        amount_minor: 200,
      },
      {
        category_code: "TRAVEL",
        category_label: "Travel",
        subcategory_code: "CAB",
        subcategory_label: "Cab",
        amount_minor: 300,
      },
    ];
    const scoped = buildSubcategoryChipOptions(items, "FOOD");
    expect(scoped.map((c) => c.id)).toEqual([ACTIVITY_FILTER_ALL, "GROCERY", "DINING"]);
    const all = buildSubcategorySegments(items, ACTIVITY_FILTER_ALL);
    expect(all.map((s) => s.id).sort()).toEqual(["CAB", "DINING", "GROCERY"]);
  });

  it("builds segments from a search-filtered subset", () => {
    const all = [
      { category_code: "FOOD", category_label: "Food", amount_minor: 100 },
      { category_code: "TRAVEL", category_label: "Travel", amount_minor: 200 },
    ];
    const searchFiltered = all.filter((i) => i.category_label.toLowerCase().includes("food"));
    const segments = buildCategorySegments(searchFiltered);
    expect(segments).toHaveLength(1);
    expect(segments[0].id).toBe("FOOD");
  });

  it("sorts by value desc then label asc", () => {
    const segments = buildCategorySegments([
      { category_code: "B", category_label: "Beta", amount_minor: 50 },
      { category_code: "A", category_label: "Alpha", amount_minor: 50 },
      { category_code: "C", category_label: "Charlie", amount_minor: 100 },
    ]);
    expect(segments.map((s) => s.id)).toEqual(["C", "A", "B"]);
  });

  it("sanitizes invalid subcategory after category or search change", () => {
    const foodOnly = buildSubcategoryChipOptions(
      [
        {
          category_code: "FOOD",
          subcategory_code: "DINING",
          subcategory_label: "Dining",
          amount_minor: 1,
        },
      ],
      "FOOD",
    );
    expect(sanitizeFilterId("CAB", foodOnly)).toBe(ACTIVITY_FILTER_ALL);
    expect(sanitizeFilterId("DINING", foodOnly)).toBe("DINING");
  });
});
