import { describe, expect, it } from "vitest";
import {
  canSaveMasterExpense,
  formatWhenLabel,
  isMasterExpenseFormDirty,
  masterExpenseCoreFieldOrder,
  resolveSubcategoryForCategory,
  whenPresetValue,
} from "@/lib/master_expense/formHelpers";
import { buildMasterExpensePayload } from "@/lib/master_expense/payloadBuilder";

const categories = [
  {
    category_id: "FOOD",
    category_name: "Food",
    children: [
      { category_id: "GROCERIES", category_name: "Groceries" },
      { category_id: "DINING_OUT", category_name: "Dining Out" },
    ],
  },
  {
    category_id: "TRANSPORT",
    category_name: "Transport",
    children: [{ category_id: "FUEL", category_name: "Fuel" }],
  },
];

describe("master expense form helpers", () => {
  it("exposes core field order before more details", () => {
    const order = masterExpenseCoreFieldOrder();
    expect(order.indexOf("description")).toBeLessThan(order.indexOf("amount"));
    expect(order.indexOf("amount")).toBeLessThan(order.indexOf("category"));
    expect(order.indexOf("category")).toBeLessThan(order.indexOf("subcategory"));
    expect(order.indexOf("subcategory")).toBeLessThan(order.indexOf("paid_from"));
    expect(order.indexOf("more_details")).toBe(order.length - 1);
  });

  it("clears incompatible subcategory when category changes", () => {
    expect(resolveSubcategoryForCategory(categories, "TRANSPORT", "GROCERIES")).toBe("");
  });

  it("preserves compatible subcategory when category changes", () => {
    expect(resolveSubcategoryForCategory(categories, "FOOD", "GROCERIES")).toBe("GROCERIES");
  });

  it("requires title amount account category for save", () => {
    expect(
      canSaveMasterExpense({
        lifeOperationsMomentId: "lo",
        lifestyleMomentId: "ls",
        title: "Dinner",
        amountMinor: 100,
        accountId: "a1",
        categoryCode: "FOOD",
      }),
    ).toBe(true);
    expect(
      canSaveMasterExpense({
        lifeOperationsMomentId: "lo",
        lifestyleMomentId: "ls",
        title: "  ",
        amountMinor: 100,
        accountId: "a1",
        categoryCode: "FOOD",
      }),
    ).toBe(false);
    expect(
      canSaveMasterExpense({
        lifeOperationsMomentId: "lo",
        lifestyleMomentId: "ls",
        title: "Dinner",
        amountMinor: 0,
        accountId: "a1",
        categoryCode: "FOOD",
      }),
    ).toBe(false);
  });

  it("detects dirty form state", () => {
    expect(
      isMasterExpenseFormDirty({
        title: "",
        amountMinor: 0,
        subcategoryCode: "",
        feeling: "",
        meaningfulness: "",
        memorability: "",
        sharedWith: [],
        relationshipImpact: [],
        contextReason: "",
        notes: "",
      }),
    ).toBe(false);
    expect(
      isMasterExpenseFormDirty({
        title: "x",
        amountMinor: 0,
        subcategoryCode: "",
        feeling: "",
        meaningfulness: "",
        memorability: "",
        sharedWith: [],
        relationshipImpact: [],
        contextReason: "",
        notes: "",
      }),
    ).toBe(true);
  });

  it("formats when label for today", () => {
    const now = new Date(2026, 6, 24, 20, 45);
    expect(formatWhenLabel("2026-07-24T20:45", now)).toBe("Today, 20:45");
  });

  it("builds when presets in local time", () => {
    const now = new Date(2026, 6, 24, 8, 45);
    expect(whenPresetValue("now", now)).toBe("2026-07-24T08:45");
    expect(whenPresetValue("today", now)).toBe("2026-07-24T12:00");
    expect(whenPresetValue("yesterday", now)).toBe("2026-07-23T12:00");
  });
});

describe("buildMasterExpensePayload subcategory", () => {
  it("serializes subcategory_code with stable keys", () => {
    const payload = buildMasterExpensePayload(
      {
        title: "Dinner",
        amountMinor: 45000,
        currencyCode: "INR",
        accountId: "acc-1",
        categoryCode: "FOOD",
        subcategoryCode: "DINING_OUT",
        occurredAt: "2026-07-08T12:00",
        feeling: "",
        meaningfulness: "",
        memorability: "",
        sharedEnabled: false,
        sharedWith: [],
        relationshipImpact: [],
        contextReason: "",
        notes: "",
      },
      "req-sub",
    );
    expect(payload.category_code).toBe("FOOD");
    expect(payload.subcategory_code).toBe("DINING_OUT");
    expect(payload.expense.subcategory_code).toBe("DINING_OUT");
    expect(payload.amount_minor).toBe(45000);
  });

  it("sends null subcategory when empty", () => {
    const payload = buildMasterExpensePayload(
      {
        title: "Ride",
        amountMinor: 1000,
        currencyCode: "INR",
        accountId: "acc-1",
        categoryCode: "TRANSPORT",
        subcategoryCode: "",
        occurredAt: "",
        feeling: "",
        meaningfulness: "",
        memorability: "",
        sharedEnabled: false,
        sharedWith: [],
        relationshipImpact: [],
        contextReason: "",
        notes: "",
      },
      "req-empty-sub",
    );
    expect(payload.subcategory_code).toBeNull();
  });
});
