import { describe, expect, it } from "vitest";
import {
  activityDateGroupLabel,
  formatRelativeTime,
  recentActivityContextLine,
  recentActivityIsEditable,
  recentActivityMoodLabel,
  recentActivityPrimaryMetric,
  recentActivityTitle,
} from "@/lib/personal/life_operations/pulse/recentActivityDisplay";

describe("recentActivityDisplay timeline IA", () => {
  it("title-cases messy lowercase titles", () => {
    expect(recentActivityTitle({ title: "coffee with kiran" })).toBe("Coffee With Kiran");
  });

  it("builds a single context line without duplicating Expense", () => {
    expect(
      recentActivityContextLine({
        type_label: "Expense",
        impact_label: "Planned",
        category_label: "Expense",
        domain_type_subtitle: "My Money · Expense",
      }),
    ).toBe("Expense · Planned");
  });

  it("omits mood when absent", () => {
    expect(recentActivityMoodLabel({})).toBeNull();
    expect(recentActivityMoodLabel({ mood: { label: "Good" } })).toBe("Good");
  });

  it("prefers primary metric", () => {
    expect(
      recentActivityPrimaryMetric({
        primary_metric: { display: "₹517" },
        amount_label: "₹1",
      }),
    ).toBe("₹517");
  });

  it("respects editable flags", () => {
    expect(recentActivityIsEditable({ editable: false })).toBe(false);
  });

  it("groups dates into human buckets", () => {
    const now = new Date("2026-07-27T12:00:00Z");
    expect(activityDateGroupLabel("2026-07-27T08:00:00Z", now)).toBe("Today");
    expect(activityDateGroupLabel("2026-07-26T08:00:00Z", now)).toBe("Yesterday");
  });

  it("formats relative time from occurred_at", () => {
    const now = new Date("2026-07-27T12:00:00Z");
    expect(formatRelativeTime("2026-07-27T12:00:00Z", now)).toBe("Just now");
    expect(formatRelativeTime("2026-07-27T11:45:00Z", now)).toBe("15m ago");
    expect(formatRelativeTime("2026-07-27T10:00:00Z", now)).toBe("2h ago");
    expect(formatRelativeTime("2026-07-24T12:00:00Z", now)).toBe("3d ago");
  });

  it("clamps future timestamps to Just now", () => {
    const now = new Date("2026-07-27T12:00:00Z");
    expect(formatRelativeTime("2026-07-27T12:15:00Z", now)).toBe("Just now");
  });
});
