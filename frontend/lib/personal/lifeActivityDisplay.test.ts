import { describe, expect, it } from "vitest";
import {
  chapterizeDay,
  groupLifeActivities,
  lifeActivityContextLine,
  lifeDayGroupLabel,
} from "@/lib/personal/lifeActivityDisplay";

describe("lifeActivityDisplay", () => {
  it("groups Today Yesterday weekday Last Week Earlier", () => {
    const now = new Date("2026-07-27T12:00:00");
    expect(lifeDayGroupLabel("2026-07-27T08:00:00", now)).toBe("Today");
    expect(lifeDayGroupLabel("2026-07-26T08:00:00", now)).toBe("Yesterday");
    expect(lifeDayGroupLabel("2026-07-25T08:00:00", now)).toBe("Saturday");
    expect(lifeDayGroupLabel("2026-07-18T08:00:00", now)).toBe("Last Week");
    expect(lifeDayGroupLabel("2026-06-01T08:00:00", now)).toBe("Earlier");
  });

  it("orders day groups", () => {
    const now = new Date("2026-07-27T12:00:00");
    const grouped = groupLifeActivities(
      [
        { occurred_at: "2026-06-01T08:00:00", id: "e" },
        { occurred_at: "2026-07-27T08:00:00", id: "t" },
        { occurred_at: "2026-07-26T08:00:00", id: "y" },
      ],
      now,
    );
    expect(grouped.map((g) => g.label)).toEqual(["Today", "Yesterday", "Earlier"]);
  });

  it("chapterizes morning and evening when both present", () => {
    const chapters = chapterizeDay([
      { occurred_at: "2026-07-27T08:00:00", id: "a" },
      { occurred_at: "2026-07-27T20:00:00", id: "b" },
    ]);
    expect(chapters.map((c) => c.chapter)).toEqual(["Morning", "Evening"]);
  });

  it("builds context line", () => {
    expect(
      lifeActivityContextLine({
        occurred_at: "2026-07-27T08:00:00",
        type_label: "Expense",
        subcategory_label: "Coffee",
      }),
    ).toBe("Expense · Coffee");
  });
});
