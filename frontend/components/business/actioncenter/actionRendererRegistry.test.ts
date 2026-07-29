import { describe, expect, it } from "vitest";
import { ALL_BUSINESS_RENDERER_IDS, BUSINESS_RENDERER_REGISTRY } from "./actionRendererRegistry";
import {
  moneyPayload,
  req,
  reqAmount,
  schemaAmountToMinor,
} from "./renderers/dedicatedHelpers";

const REQUIRED_RENDERER_IDS = [
  "team_ops.team_update",
  "team_ops.recognition",
  "team_ops.meeting",
  "team_ops.issue",
  "team_ops.approval",
  "team_ops.review",
  "team_ops.escalation",
  "team_ops.participation",
  "team_ops.member_update",
  "team_ops.note",

  "runway.cash_inflow",
  "runway.expense_burn",
  "runway.runway_risk",
  "runway.financial_update",
  "runway.strategic_decision",

  "ops.spend_entry",
  "ops.vendor_update",
  "ops.approval",
  "ops.issue",
  "ops.operational_improvement",
] as const;

export const DEDICATED_RENDERER_IDS = [
  "runway.cash_inflow",
  "runway.expense_burn",
  "runway.runway_risk",
  "runway.financial_update",
  "runway.strategic_decision",
  "ops.spend_entry",
  "ops.vendor_update",
  "ops.approval",
  "ops.issue",
  "ops.operational_improvement",
  "team_ops.approval",
  "team_ops.issue",
  "team_ops.escalation",
  "team_ops.member_update",
  "team_ops.meeting",
] as const;

export const SCHEMA_RENDERER_IDS = [
  "team_ops.note",
  "team_ops.recognition",
  "team_ops.team_update",
  "team_ops.participation",
  "team_ops.review",
] as const;

describe("BusinessActionRendererRegistry", () => {
  it("has all 20 required renderer_ids registered", () => {
    expect(ALL_BUSINESS_RENDERER_IDS).toHaveLength(20);

    for (const id of REQUIRED_RENDERER_IDS) {
      expect(
        BUSINESS_RENDERER_REGISTRY[id],
        `Missing renderer for ${id}`,
      ).toBeDefined();
    }
  });

  it("has no extra renderers beyond the required 20", () => {
    const registeredSet = new Set(ALL_BUSINESS_RENDERER_IDS);
    const requiredSet = new Set<string>(REQUIRED_RENDERER_IDS);
    const extra = [...registeredSet].filter((id) => !requiredSet.has(id));
    expect(extra).toEqual([]);
  });

  it("ALL_BUSINESS_RENDERER_IDS matches BUSINESS_RENDERER_REGISTRY keys", () => {
    expect(ALL_BUSINESS_RENDERER_IDS.sort()).toEqual(
      Object.keys(BUSINESS_RENDERER_REGISTRY).sort(),
    );
  });

  it("partitions dedicated vs schema renderer sets without overlap", () => {
    const dedicated = new Set<string>(DEDICATED_RENDERER_IDS);
    const schema = new Set<string>(SCHEMA_RENDERER_IDS);
    for (const id of dedicated) expect(schema.has(id)).toBe(false);
    expect(dedicated.size + schema.size).toBe(20);
    for (const id of [...dedicated, ...schema]) {
      expect(BUSINESS_RENDERER_REGISTRY[id]).toBeDefined();
    }
  });
});

describe("dedicatedHelpers validation and money payload", () => {
  it("req marks blank fields", () => {
    expect(req({}, "title", "Title")).toEqual({ title: "Title is required" });
    expect(req({ title: "x" }, "title", "Title")).toEqual({});
  });

  it("reqAmount rejects non-positive amounts", () => {
    expect(reqAmount({ amount: "" })).toHaveProperty("amount");
    expect(reqAmount({ amount: "0" })).toHaveProperty("amount");
    expect(reqAmount({ amount: "12.50" })).toEqual({});
  });

  it("moneyPayload converts major display amount to amount_minor", () => {
    const payload = moneyPayload({ amount: "10.00", currency_code: "INR" });
    expect(payload.amount_minor).toBe(1000);
    expect(payload.currency_code).toBe("INR");
  });

  it("schemaAmountToMinor normalizes amount_minor from major string", () => {
    const out = schemaAmountToMinor({ title: "x", amount_minor: "5.00", currency: "USD" });
    expect(out.amount_minor).toBe(500);
    expect(out.currency_code).toBe("USD");
    expect(out.currency).toBeUndefined();
  });
});
