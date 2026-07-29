import { describe, expect, it } from "vitest";
import {
  buildCommitmentPayload,
  buildExpensePayload,
  buildReflectionPayload,
  buildRhythmPayload,
  canSubmitLifeOpsTab,
  defaultLifeOpsFormState,
  isLifeOpsTabDirty,
} from "@/lib/quick_add/payloadBuilders/lifeOperations";
import {
  filterMoneyEntryTypes,
  humanizeEnumLabel,
  moneySaveLabel,
  runtimeModeLabel,
  tabSuccessMessage,
} from "@/lib/quick_add/lifeOpsCopy";

describe("buildExpensePayload", () => {
  it("sends amount_minor, currency_code, and category_code", () => {
    const state = {
      ...defaultLifeOpsFormState("INR"),
      amountMinor: 450000,
      currencyCode: "INR",
      accountId: "acc-1",
      categoryCode: "FOOD",
      transactionType: "EXPENSE",
      expenseTitle: "Coffee",
      occurredDate: "2026-07-13",
      occurredTime: "14:05",
    };
    const payload = buildExpensePayload("moment-1", "Coffee", state);
    expect(payload.event_title).toBe("Coffee");
    expect(payload.expense).toEqual({
      transaction_type: "EXPENSE",
      title: "Coffee",
      amount_minor: 450000,
      currency_code: "INR",
      account_id: "acc-1",
      category_code: "FOOD",
      subcategory_code: null,
      pressure_impact: undefined,
      transaction_date: "2026-07-13T14:05",
      notes: undefined,
    });
    expect(payload.occurred_at).toBe("2026-07-13T14:05");
  });

  it("falls back event_title when expenseTitle is empty", () => {
    const state = {
      ...defaultLifeOpsFormState("INR"),
      amountMinor: 100,
      accountId: "acc-1",
      categoryCode: "FOOD",
      expenseTitle: "  ",
    };
    const payload = buildExpensePayload("moment-1", "Money entry", state);
    expect(payload.event_title).toBe("Money entry");
    expect(payload.expense.title).toBeUndefined();
  });

  it("includes subcategory_code when selected", () => {
    const state = {
      ...defaultLifeOpsFormState("INR"),
      amountMinor: 100,
      accountId: "acc-1",
      categoryCode: "FOOD",
      subcategoryCode: "GROCERIES",
    };
    const payload = buildExpensePayload("moment-1", "Groceries", state);
    expect(payload.expense.subcategory_code).toBe("GROCERIES");
  });

  it("defaults occurred date and time on new form state", () => {
    const state = defaultLifeOpsFormState();
    expect(state.occurredDate).toMatch(/^\d{4}-\d{2}-\d{2}$/);
    expect(state.occurredTime).toMatch(/^\d{2}:\d{2}$/);
  });
});

describe("canSubmitLifeOpsTab", () => {
  it("requires amount_minor, account, and category for EXPENSE", () => {
    const state = defaultLifeOpsFormState();
    expect(canSubmitLifeOpsTab("EXPENSE", state)).toBe(false);
    state.amountMinor = 100;
    state.accountId = "x";
    expect(canSubmitLifeOpsTab("EXPENSE", state)).toBe(false);
    state.categoryCode = "FOOD";
    expect(canSubmitLifeOpsTab("EXPENSE", state)).toBe(true);
  });

  it("requires commitment name for COMMITMENT", () => {
    const state = defaultLifeOpsFormState();
    expect(canSubmitLifeOpsTab("COMMITMENT", state)).toBe(false);
    state.commitmentName = "Ship launch";
    expect(canSubmitLifeOpsTab("COMMITMENT", state)).toBe(true);
  });

  it("requires feeling state for REFLECTION", () => {
    const state = defaultLifeOpsFormState();
    expect(canSubmitLifeOpsTab("REFLECTION", state)).toBe(true);
    state.feelingState = "";
    expect(canSubmitLifeOpsTab("REFLECTION", state)).toBe(false);
  });

  it("requires recovery type for RECOVERY", () => {
    const state = defaultLifeOpsFormState();
    expect(canSubmitLifeOpsTab("RECOVERY", state)).toBe(false);
    state.recoveryType = "REST";
    expect(canSubmitLifeOpsTab("RECOVERY", state)).toBe(true);
  });
});

describe("commitment and rhythm payloads", () => {
  it("includes intensity and omits empty expected amount", () => {
    const state = {
      ...defaultLifeOpsFormState(),
      commitmentName: "Proposal",
      intensity: "HEAVY",
      showExpectedAmount: false,
    };
    const payload = buildCommitmentPayload("m1", "Attention", state);
    expect(payload.commitment.intensity).toBe("HEAVY");
    expect(payload.commitment.expected_amount).toBeUndefined();
  });

  it("sends runtime_signals on rhythm", () => {
    const state = {
      ...defaultLifeOpsFormState(),
      runtimeMode: "FLOW_MODE",
      runtimeSignals: {
        pressure: "DOWN" as const,
        recovery: "UP" as const,
        focus: "STABLE" as const,
        momentum: "STABLE" as const,
      },
    };
    const payload = buildRhythmPayload("m1", "Rhythm", state);
    expect(payload.rhythm.runtime_signals).toEqual({
      pressure: "DOWN",
      recovery: "UP",
      focus: "STABLE",
      momentum: "STABLE",
    });
  });

  it("sends reflection tags as list when multiple", () => {
    const state = {
      ...defaultLifeOpsFormState(),
      feelingState: "GOOD",
      reflectionTags: ["Grateful", "Focused"],
    };
    const payload = buildReflectionPayload("m1", "Mood", state);
    expect(payload.reflection.reflection_tag).toEqual(["Grateful", "Focused"]);
  });
});

describe("lifeOpsCopy", () => {
  it("humanizes enums and never returns raw underscores for modes", () => {
    expect(humanizeEnumLabel("QUIET_TIME")).toBe("Quiet Time");
    expect(runtimeModeLabel("FLOW_MODE")).toBe("Flow");
    expect(moneySaveLabel("INCOME")).toBe("Save Income");
    expect(tabSuccessMessage("COMMITMENT")).toBe("Attention entry saved");
  });

  it("filters money entry types to production set", () => {
    const filtered = filterMoneyEntryTypes([
      { value: "EXPENSE", label: "Expense" },
      { value: "SAVINGS", label: "Savings" },
      { value: "INCOME", label: "Income" },
    ]);
    expect(filtered.map((f) => f.value)).toEqual(["EXPENSE", "INCOME"]);
  });
});

describe("isLifeOpsTabDirty", () => {
  it("is false for defaults and true after meaningful edit", () => {
    const state = defaultLifeOpsFormState();
    expect(isLifeOpsTabDirty("EXPENSE", state)).toBe(false);
    state.amountMinor = 50;
    expect(isLifeOpsTabDirty("EXPENSE", state)).toBe(true);
  });
});
