import { describe, expect, it } from "vitest";

/** Pure helpers mirrored from SharedExperienceSetup money conversion. */
const MONEY_EXPONENT = 2;

function majorToMinor(major: string | number | null | undefined): number | null {
  if (major == null || major === "") return null;
  const n = typeof major === "number" ? major : Number(major);
  if (!Number.isFinite(n)) return null;
  return Math.round(n * 10 ** MONEY_EXPONENT);
}

function minorToMajorString(minor: number | null): string {
  if (minor == null) return "";
  const major = minor / 10 ** MONEY_EXPONENT;
  return String(major);
}

describe("Shared Experience money major/minor conversion", () => {
  it("converts major display amount to minor for SetupMoneyField", () => {
    expect(majorToMinor("10000")).toBe(1_000_000);
    expect(majorToMinor(99.5)).toBe(9950);
    expect(majorToMinor("")).toBeNull();
  });

  it("stores major units back into estimated_budget (not raw minor)", () => {
    expect(minorToMajorString(1_000_000)).toBe("10000");
    expect(minorToMajorString(9950)).toBe("99.5");
    expect(minorToMajorString(null)).toBe("");
  });
});
