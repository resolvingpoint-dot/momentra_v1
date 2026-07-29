import { describe, expect, it } from "vitest";
import { formatMinor, parseUserInputToMinor } from "@/lib/reference_data/money";

const inr = { code: "INR", minor_unit: 2, symbol: "₹" };
const usd = { code: "USD", minor_unit: 2, symbol: "$" };
const jpy = { code: "JPY", minor_unit: 0, symbol: "¥" };
const kwd = { code: "KWD", minor_unit: 3, symbol: "د.ك" };

describe("parseUserInputToMinor", () => {
  it("converts INR 4500 to 450000 minor", () => {
    expect(parseUserInputToMinor("4500", inr)).toBe(450000);
  });

  it("converts USD 45.99 to 4599 minor", () => {
    expect(parseUserInputToMinor("45.99", usd)).toBe(4599);
  });

  it("handles JPY minor_unit 0", () => {
    expect(parseUserInputToMinor("1999", jpy)).toBe(1999);
  });

  it("handles KWD minor_unit 3", () => {
    expect(parseUserInputToMinor("4.123", kwd)).toBe(4123);
  });

  it("formats KWD minor round-trip", () => {
    const minor = parseUserInputToMinor("4.123", kwd);
    expect(minor).toBe(4123);
    expect(formatMinor(minor, kwd, "en-KW")).toContain("4.123");
  });
});
