import { describe, expect, it } from "vitest";
import {
  composeOccurredAt,
  defaultOccurredAt,
  nowISOTime,
  todayISODate,
} from "@/lib/quick_add/dateTimeDefaults";

describe("dateTimeDefaults", () => {
  it("formats local today and now", () => {
    const fixed = new Date(2026, 6, 13, 14, 5); // Jul 13 2026 14:05 local
    expect(todayISODate(fixed)).toBe("2026-07-13");
    expect(nowISOTime(fixed)).toBe("14:05");
    expect(defaultOccurredAt(fixed)).toBe("2026-07-13T14:05");
  });

  it("composes occurred_at from date and time", () => {
    expect(composeOccurredAt("2026-07-13", "09:30")).toBe("2026-07-13T09:30");
    expect(composeOccurredAt("2026-07-13", "")).toBe("2026-07-13");
    expect(composeOccurredAt("", "09:30")).toBeUndefined();
  });
});
