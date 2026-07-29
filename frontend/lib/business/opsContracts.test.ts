import { describe, expect, it } from "vitest";
import { OPS_MOMENTS_SECTION_KEYS, OPS_PULSE_SECTION_KEYS } from "@/lib/api/businessActive";
import {
  parseOpsMomentsResponse,
  parseOpsPulseResponse,
} from "@/lib/business/opsApiMappers";
import { OPS_ACTION_TYPES } from "@/lib/business/opsActionRegistry";

describe("opsContracts", () => {
  it("parses sparse pulse with all section keys and UPPERCASE health band", () => {
    const pulse = parseOpsPulseResponse({
      moment_id: "m1",
      moment_type: "BUSINESS_OPERATIONS",
      hero: { state: "empty", operations_name: "Ops" },
      operations_health: {
        state: "empty",
        label: "Not started",
        band: "EMPTY",
        rule: "budget_issues_approvals_thresholds",
        drivers: {},
      },
      kpis: { state: "empty" },
      budget_usage: {
        state: "empty",
        total_budget_minor: 0,
        total_spend_minor: 0,
        remaining_minor: 0,
        allocations: [],
        over_budget_allocations: [],
        unallocated_minor: 0,
      },
      approvals: {
        state: "empty",
        pending: 0,
        overdue: 0,
        approved_recently: 0,
        rejected_recently: 0,
        amount_awaiting_minor: null,
      },
      issues: {
        state: "empty",
        open: 0,
        critical: 0,
        overdue: 0,
        unassigned: 0,
        resolved_recently: 0,
      },
      vendors: {
        state: "empty",
        active: 0,
        status_changes: 0,
        critical_dependencies: 0,
        unresolved_events: 0,
      },
      improvements: {
        state: "empty",
        planned: 0,
        in_progress: 0,
        completed: 0,
        overdue: 0,
      },
      monitoring: { state: "empty", level: null, active_alerts: [], recipients: [] },
      attention_items: { state: "empty", items: [] },
      signals: { state: "empty", items: [] },
      recent_activity: { state: "empty", items: [] },
      next_best_action: { state: "empty", item: null },
    });
    for (const key of OPS_PULSE_SECTION_KEYS) {
      expect(key in pulse).toBe(true);
    }
    expect(pulse.operations_health.band).toBe("EMPTY");
    expect(pulse.next_best_action.item).toBeNull();
  });

  it("normalizes lowercase health bands without inventing scores", () => {
    const pulse = parseOpsPulseResponse({
      moment_id: "m1",
      operations_health: { state: "complete", label: "Healthy", band: "healthy" },
      hero: { state: "empty" },
      kpis: { state: "empty" },
      budget_usage: { state: "empty", total_budget_minor: 0, total_spend_minor: 0, remaining_minor: 0 },
      approvals: { state: "empty", pending: 0, overdue: 0, approved_recently: 0, rejected_recently: 0 },
      issues: { state: "empty", open: 0, critical: 0, overdue: 0, unassigned: 0, resolved_recently: 0 },
      vendors: { state: "empty", active: 0, status_changes: 0, critical_dependencies: 0, unresolved_events: 0 },
      improvements: { state: "empty", planned: 0, in_progress: 0, completed: 0, overdue: 0 },
      monitoring: { state: "empty" },
      attention_items: { state: "empty", items: [] },
      signals: { state: "empty", items: [] },
      recent_activity: { state: "empty", items: [] },
      next_best_action: { state: "empty", item: null },
    });
    expect(pulse.operations_health.band).toBe("HEALTHY");
    expect(
      (pulse.operations_health as { score?: number }).score,
    ).toBeUndefined();
  });

  it("parses moments lanes and exposes Ops action types", () => {
    const moments = parseOpsMomentsResponse({
      moment_id: "m1",
      journey_hero: { state: "empty", title: "Ops" },
      summary_stats: { state: "empty", budget_used_percent: 0 },
      spend_timeline: { state: "empty", items: [] },
      approval_timeline: { state: "empty", items: [] },
      issue_timeline: { state: "empty", items: [] },
      vendor_timeline: { state: "empty", items: [] },
      improvement_timeline: { state: "empty", items: [] },
      milestones: { state: "empty", items: [] },
      key_decisions: { state: "empty", items: [] },
      timeline: { state: "empty", items: [] },
      recent_activity: { state: "empty", items: [] },
    });
    for (const key of OPS_MOMENTS_SECTION_KEYS) {
      expect(key in moments).toBe(true);
    }
    expect([...OPS_ACTION_TYPES]).toEqual([
      "SPEND_ENTRY",
      "VENDOR_UPDATE",
      "OPS_APPROVAL_REQUEST",
      "ISSUE_RISK",
      "OPERATIONAL_IMPROVEMENT",
    ]);
  });
});
