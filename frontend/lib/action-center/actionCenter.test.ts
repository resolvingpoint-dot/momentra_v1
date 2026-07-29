import { beforeEach, describe, expect, it } from "vitest";
import {
  emitActionAnalytics,
  getFavoriteActionIds,
  getRecentActionIds,
  pushRecentAction,
  subscribeActionAnalytics,
  toggleFavoriteAction,
} from "@/lib/action-center/actionCenterPrefs";
import {
  getActionCenterActions,
  searchActionCenterActions,
} from "@/lib/action-center/actionCenterMeta";
import {
  deriveSuggestionSignals,
  rankSmartSuggestions,
} from "@/lib/action-center/smartSuggestions";
import {
  clearQuickAddDraft,
  loadQuickAddDraft,
  saveQuickAddDraft,
} from "@/lib/quick_add/draftStore";

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
  Object.defineProperty(globalThis, "window", {
    value: { localStorage: memory },
    configurable: true,
  });
}

describe("actionCenterPrefs", () => {
  beforeEach(() => {
    installMemoryStorage();
  });

  it("toggles favorites per user/template", () => {
    expect(getFavoriteActionIds("u1", "group.trip")).toEqual([]);
    toggleFavoriteAction("u1", "group.trip", "EXPENSE");
    expect(getFavoriteActionIds("u1", "group.trip")).toEqual(["EXPENSE"]);
    toggleFavoriteAction("u1", "group.trip", "EXPENSE");
    expect(getFavoriteActionIds("u1", "group.trip")).toEqual([]);
  });

  it("caps recent at 8 and dedupes", () => {
    for (let i = 0; i < 10; i += 1) {
      pushRecentAction("u1", "group.trip", `A${i}`);
    }
    const recent = getRecentActionIds("u1", "group.trip");
    expect(recent).toHaveLength(8);
    expect(recent[0]).toBe("A9");
    pushRecentAction("u1", "group.trip", "A9");
    expect(getRecentActionIds("u1", "group.trip")[0]).toBe("A9");
    expect(getRecentActionIds("u1", "group.trip").filter((x) => x === "A9")).toHaveLength(1);
  });

  it("emits analytics event shapes", () => {
    const events: unknown[] = [];
    const unsub = subscribeActionAnalytics((p) => events.push(p));
    emitActionAnalytics({
      analytics_id: "group.trip.expense",
      event: "started",
      action_id: "EXPENSE",
      template_id: "group.trip",
    });
    emitActionAnalytics({
      analytics_id: "group.trip.expense",
      event: "completed",
      duration_ms: 1200,
      action_id: "EXPENSE",
      template_id: "group.trip",
    });
    unsub();
    expect(events).toEqual([
      {
        analytics_id: "group.trip.expense",
        event: "started",
        action_id: "EXPENSE",
        template_id: "group.trip",
      },
      {
        analytics_id: "group.trip.expense",
        event: "completed",
        duration_ms: 1200,
        action_id: "EXPENSE",
        template_id: "group.trip",
      },
    ]);
  });
});

describe("actionCenterMeta search", () => {
  it("matches synonyms (hotel → booking/expense)", () => {
    const actions = getActionCenterActions("group.trip");
    const hits = searchActionCenterActions(actions, "hotel");
    const ids = hits.map((a) => a.action_id);
    expect(ids).toContain("BOOKING");
    expect(ids).toContain("EXPENSE");
  });

  it("enriches living with RENT and UTILITY aliases", () => {
    const actions = getActionCenterActions("group.living");
    expect(actions.some((a) => a.action_id === "RENT")).toBe(true);
    expect(actions.some((a) => a.action_id === "UTILITY")).toBe(true);
    expect(actions.find((a) => a.action_id === "RENT")?.renderer_id).toBe("living.rent");
  });

  it("exposes estimated_time_sec and renderer_id", () => {
    const expense = getActionCenterActions("group.trip").find((a) => a.action_id === "EXPENSE");
    expect(expense?.estimated_time_sec).toBeGreaterThan(0);
    expect(expense?.renderer_id).toBe("experience.expense");
    expect(expense?.subtitle).toMatch(/spend|split|paid/i);
  });
});

describe("smartSuggestions", () => {
  it("suggests booking when experience has no bookings", () => {
    const actions = getActionCenterActions("group.trip");
    const signals = deriveSuggestionSignals("group.trip", {
      stats: { confirmed_bookings: 0 },
    });
    const ranked = rankSmartSuggestions("group.trip", actions, signals);
    expect(ranked.map((a) => a.action_id)).toContain("BOOKING");
  });

  it("suggests rent when living rent overdue", () => {
    const actions = getActionCenterActions("group.living");
    const ranked = rankSmartSuggestions("group.living", actions, { rentOverdue: true });
    expect(ranked.map((a) => a.action_id)).toEqual(["RENT"]);
  });

  it("returns empty when signals missing", () => {
    const actions = getActionCenterActions("group.purchase");
    expect(rankSmartSuggestions("group.purchase", actions, {})).toEqual([]);
  });
});

describe("auto-draft restore", () => {
  beforeEach(() => {
    installMemoryStorage();
  });

  it("saves and restores draft by momentId+actionId", () => {
    saveQuickAddDraft({
      momentId: "m1",
      tab: "EXPENSE",
      form: { amount: "42", title: "Dinner" },
      payload: {},
      clientRequestId: "c1",
      savedAt: new Date().toISOString(),
    });
    const draft = loadQuickAddDraft("m1", "EXPENSE");
    expect(draft?.form).toMatchObject({ amount: "42", title: "Dinner" });
    clearQuickAddDraft("m1", "EXPENSE");
    expect(loadQuickAddDraft("m1", "EXPENSE")).toBeNull();
  });
});
