import { describe, expect, it } from "vitest";
import { formatAccountBalance } from "@/lib/metadata/money";
import type { PersonalAccountRecord } from "@/lib/metadata/money";

const inr = { code: "INR", label: "Indian Rupee", minor_unit: 2, symbol: "₹" };

describe("formatAccountBalance", () => {
  it("formats account balance from minor units", () => {
    const account: Pick<PersonalAccountRecord, "current_balance_minor" | "currency_code"> = {
      current_balance_minor: 450000,
      currency_code: "INR",
    };
    expect(formatAccountBalance(account, [inr], "en-IN")).toContain("4,500");
  });

  it("falls back when reference row missing", () => {
    const account = {
      current_balance_minor: 100,
      currency_code: "EUR",
    };
    const formatted = formatAccountBalance(account, [], "en-GB");
    expect(formatted).toMatch(/1(\.00)?/);
  });
});
