import { describe, expect, it } from "vitest";
import {
  accountLabelForEntryType,
  compactInsightBody,
  filterMoneyEntryTypes,
  humanizeEnumLabel,
  INTENTION_SIGNAL_PRESETS,
  LO_SELECTOR_HELPER,
  LO_SHEET_SUPPORTING,
  loSelectorBlurb,
  moneySaveLabel,
  runtimeModeHint,
  runtimeModeLabel,
  signalDirectionLabel,
  tabSaveLabel,
  tabSuccessMessage,
} from "@/lib/quick_add/lifeOpsCopy";

describe("lifeOpsCopy", () => {
  it("maps account labels by entry type", () => {
    expect(accountLabelForEntryType("EXPENSE")).toBe("Paid from");
    expect(accountLabelForEntryType("INCOME")).toBe("Received in");
    expect(accountLabelForEntryType("TRANSFER")).toBe("From account");
  });

  it("provides intention presets for signals", () => {
    expect(INTENTION_SIGNAL_PRESETS["More Rest"]?.recovery).toBe("UP");
    expect(INTENTION_SIGNAL_PRESETS["More Focus"]?.focus).toBe("UP");
  });

  it("humanizes insight titles without exposing raw enums alone", () => {
    const body = compactInsightBody("QUIET_TIME", "QUIET_TIME appears to help");
    expect(body).toContain("Quiet Time");
    expect(body).not.toMatch(/QUIET_TIME/);
  });

  it("exposes mode hints and signal labels", () => {
    expect(runtimeModeLabel("BUILD_MODE")).toBe("Build");
    expect(runtimeModeHint("FLOW_MODE").length).toBeGreaterThan(0);
    expect(signalDirectionLabel("DOWN")).toBe("Decrease");
    expect(tabSaveLabel("RHYTHM")).toBe("Update Rhythm");
    expect(moneySaveLabel("CONTRIBUTION")).toBe("Save Contribution");
    expect(tabSuccessMessage("RECOVERY")).toBe("Recovery logged");
    expect(humanizeEnumLabel("IN_PROGRESS")).toBe("In Progress");
    expect(filterMoneyEntryTypes([{ value: "SAVINGS", label: "Savings" }]).length).toBeGreaterThan(0);
  });

  it("exposes Intelligence OS header supporting copy and selector blurbs", () => {
    expect(LO_SHEET_SUPPORTING).toContain("day runs");
    expect(LO_SELECTOR_HELPER).toContain("log");
    expect(loSelectorBlurb("EXPENSE")).toBe("Track spending and pressure");
    expect(loSelectorBlurb("COMMITMENT")).toBe("Log where focus is going");
    expect(loSelectorBlurb("RECOVERY")).toBe("Capture rest and recharge");
    expect(loSelectorBlurb("REFLECTION")).toBe("Reflect how you feel");
    expect(loSelectorBlurb("RHYTHM")).toBe("Tune rhythm and priorities");
  });
});
