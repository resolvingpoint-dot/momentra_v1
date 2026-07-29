import { beforeEach, describe, expect, it } from "vitest";
import {
  clearQuickAddDraft,
  loadQuickAddDraft,
  saveQuickAddDraft,
} from "@/lib/quick_add/draftStore";
import {
  getFavoriteActionIds,
  getRecentActionIds,
  pushRecentAction,
  toggleFavoriteAction,
} from "@/lib/action-center/actionCenterPrefs";

function installMemoryStorage() {
  const store = new Map<string, string>();
  const memory: Storage = {
    get length() {
      return store.size;
    },
    clear: () => store.clear(),
    getItem: (k) => store.get(k) ?? null,
    setItem: (k, v) => {
      store.set(k, String(v));
    },
    removeItem: (k) => {
      store.delete(k);
    },
    key: (i) => Array.from(store.keys())[i] ?? null,
  };
  Object.defineProperty(globalThis, "localStorage", { value: memory, configurable: true });
}

describe("Business Action Center draft restore", () => {
  beforeEach(() => {
    installMemoryStorage();
    clearQuickAddDraft("moment-1", "cash_inflow");
  });

  it("saves and restores draft form state", () => {
    saveQuickAddDraft({
      momentId: "moment-1",
      tab: "cash_inflow",
      form: { title: "Seed round", amount: "100" },
      payload: {},
      clientRequestId: "req-1",
      savedAt: new Date().toISOString(),
    });
    const draft = loadQuickAddDraft("moment-1", "cash_inflow");
    expect(draft?.form).toMatchObject({ title: "Seed round", amount: "100" });
    clearQuickAddDraft("moment-1", "cash_inflow");
    expect(loadQuickAddDraft("moment-1", "cash_inflow")).toBeNull();
  });
});

describe("Business Action Center favorites and recent", () => {
  const userId = "biz-test-user";
  const templateId = "business.runway";

  beforeEach(() => {
    installMemoryStorage();
  });

  it("toggles favorites and tracks recent actions", () => {
    const afterFav = toggleFavoriteAction(userId, templateId, "cash_inflow");
    expect(afterFav).toContain("cash_inflow");
    expect(getFavoriteActionIds(userId, templateId)).toContain("cash_inflow");

    pushRecentAction(userId, templateId, "expense_burn");
    pushRecentAction(userId, templateId, "cash_inflow");
    const recent = getRecentActionIds(userId, templateId);
    expect(recent[0]).toBe("cash_inflow");
    expect(recent).toContain("expense_burn");

    toggleFavoriteAction(userId, templateId, "cash_inflow");
    expect(getFavoriteActionIds(userId, templateId)).not.toContain("cash_inflow");
  });
});
