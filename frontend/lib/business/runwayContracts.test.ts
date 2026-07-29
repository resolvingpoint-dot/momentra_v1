import { describe, expect, it } from "vitest";
import { RUNWAY_MOMENTS_SECTION_KEYS, RUNWAY_PULSE_SECTION_KEYS } from "@/lib/api/businessActive";
import {
  parseRunwayMomentsResponse,
  parseRunwayPulseResponse,
} from "@/lib/business/runwayApiMappers";

describe("runwayContracts", () => {
  it("parses sparse pulse with all section keys", () => {
    const pulse = parseRunwayPulseResponse({
      moment_id: "m1",
      moment_type: "BUSINESS_RUNWAY",
      hero: { state: "empty", title: "Runway", runway_health: { label: "Not started", band: "empty" } },
      runway_health: { state: "empty", health: { label: "Not started", band: "empty" } },
      cash_position: { state: "empty", cash_available_minor: 0 },
      monthly_burn: { state: "empty", monthly_burn_minor: 0 },
      revenue_trend: { state: "empty", monthly_revenue_minor: 0 },
      collection_rate: { state: "empty", collection_rate_percent: null },
      runway_months: { state: "empty", runway_months: null },
      cash_movement: { state: "empty", total_inflow_minor: 0, total_burn_minor: 0, net_burn_minor: 0 },
      kpis: { state: "empty" },
      forecast: { state: "empty" },
      attention_items: { state: "empty", items: [] },
      trends: { state: "empty", items: [] },
      signals: { state: "empty", items: [] },
      recent_activity: { state: "empty", items: [] },
      next_best_action: { state: "empty", item: null },
    });
    for (const key of RUNWAY_PULSE_SECTION_KEYS) {
      expect(key in pulse).toBe(true);
    }
  });

  it("parses sparse moments with invoice/payroll empty lanes", () => {
    const moments = parseRunwayMomentsResponse({
      moment_id: "m1",
      journey_hero: { state: "empty", title: "Runway" },
      cash_available: { state: "empty", cash_available_minor: 0 },
      runway_months: { state: "empty", runway_months: null },
      timeline: { state: "empty", items: [] },
      revenue_updates: { state: "empty", items: [] },
      forecast_changes: { state: "empty", items: [] },
      expense_events: { state: "empty", items: [] },
      inflow_events: { state: "empty", items: [] },
      funding_events: { state: "empty", items: [] },
      invoices: { state: "empty", items: [], empty_reason: "no_invoice_handler_v1" },
      payroll: { state: "empty", items: [], empty_reason: "no_payroll_handler_v1" },
      milestones: { state: "empty", items: [] },
      recent_activity: { state: "empty", items: [] },
    });
    for (const key of RUNWAY_MOMENTS_SECTION_KEYS) {
      expect(key in moments).toBe(true);
    }
    expect(moments.invoices.empty_reason).toBe("no_invoice_handler_v1");
  });
});
