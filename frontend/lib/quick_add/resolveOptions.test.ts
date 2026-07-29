import { describe, expect, it } from "vitest";
import { EXPENSE_CATEGORY_SEED, resolveExpenseCategories } from "@/lib/quick_add/resolveOptions";

describe("resolveExpenseCategories", () => {
  it("falls back to seed with nested children", () => {
    const cats = resolveExpenseCategories(null);
    expect(cats.length).toBeGreaterThan(0);
    const food = cats.find((c) => c.code === "FOOD");
    expect(food?.children?.map((c) => c.code)).toEqual(
      expect.arrayContaining(["GROCERIES", "DINING_OUT", "COFFEE"]),
    );
  });

  it("uses quick-add expense_categories when nested", () => {
    const cats = resolveExpenseCategories({
      expense_categories: [
        {
          code: "FOOD",
          label: "Food",
          children: [{ code: "GROCERIES", label: "Groceries" }],
        },
      ],
    });
    expect(cats[0].code).toBe("FOOD");
    expect(cats[0].children?.[0].code).toBe("GROCERIES");
  });

  it("seed matches EXPENSE taxonomy parents", () => {
    expect(EXPENSE_CATEGORY_SEED.map((c) => c.code)).toEqual([
      "FOOD",
      "TRANSPORT",
      "HOUSING",
      "HEALTH",
      "ENTERTAINMENT",
      "OTHER",
    ]);
  });
});
