import { describe, expect, it } from "vitest";
import type {
  PersonalLifeOpsPulseMetrics,
  PersonalLifestylePulseMetrics,
  PersonalLifeOpsMemoryMetrics,
  PersonalLifeMetrics,
  PersonalLifeOpsActivityResponse,
} from "@/lib/api/personal";
import type {
  PersonalFutureBuildingPulseMetrics,
  PersonalEmotionalSecurityPulseMetrics,
} from "@/lib/api/personalDomainTypes";
import type {
  PersonalMasterExpenseOptionsResponse,
  PersonalMasterExpenseResponse,
} from "@/lib/api/client";

import loPulse from "@/lib/personal/fixtures/dto/lo_pulse_sparse.json";
import fbPulse from "@/lib/personal/fixtures/dto/fb_pulse_sparse.json";
import lifestylePulse from "@/lib/personal/fixtures/dto/lifestyle_pulse_sparse.json";
import relationshipsPulse from "@/lib/personal/fixtures/dto/relationships_pulse_sparse.json";
import sharedLife from "@/lib/personal/fixtures/dto/shared_life_sparse.json";
import memory from "@/lib/personal/fixtures/dto/memory_sparse.json";
import meOptions from "@/lib/personal/fixtures/dto/master_expense_options_sparse.json";
import meCreate from "@/lib/personal/fixtures/dto/master_expense_create_idempotent.json";
import activity from "@/lib/personal/fixtures/dto/activity_list_sparse.json";

describe("Personal DTO contracts (sparse projections)", () => {
  it("parses LO Pulse sparse without invented signals", () => {
    const d = loPulse as PersonalLifeOpsPulseMetrics;
    expect(d.ops_index).toBe(null);
    expect(d.data_sufficient).toBe(false);
    expect(d.signals).toHaveLength(0);
    expect(d.trends_30d.recovery).toHaveLength(0);
  });

  it("parses FB Pulse sparse without invented trends", () => {
    const d = fbPulse as PersonalFutureBuildingPulseMetrics;
    expect(d.momentum_index).toBe(0);
    expect(d.signals).toHaveLength(0);
    expect(d.recent_activity).toHaveLength(0);
  });

  it("parses Lifestyle Pulse sparse with empty trend series", () => {
    const d = lifestylePulse as PersonalLifestylePulseMetrics;
    expect(d.vitality_index).toBe(0);
    expect(d.trends_30d.joy).toHaveLength(0);
    expect(d.trends_30d.vitality).toHaveLength(0);
  });

  it("parses Relationships Pulse sparse", () => {
    const d = relationshipsPulse as PersonalEmotionalSecurityPulseMetrics;
    expect(d.bond_index).toBe(0);
    expect(d.signal_chips).toHaveLength(0);
    expect(d.recent_activity).toHaveLength(0);
  });

  it("parses shared Life sparse (honest empty)", () => {
    const d = sharedLife as PersonalLifeMetrics;
    expect(d.life_health.life_score).toBe(0);
    expect(d.emotional_trend.is_sparse).toBe(true);
    expect(d.emotional_trend.series).toHaveLength(0);
  });

  it("parses Memory sparse with empty AI quote", () => {
    const m = memory.metrics as PersonalLifeOpsMemoryMetrics;
    expect(m.ai_interpretation.quote).toBe("");
    expect(m.best_drivers).toHaveLength(0);
  });

  it("parses Master Expense options sparse", () => {
    const o = meOptions as PersonalMasterExpenseOptionsResponse;
    expect(o.accounts).toHaveLength(0);
    expect(o.life_operations_moment_id).toBeNull();
  });

  it("parses Master Expense create idempotent response with honest impact", () => {
    const r = meCreate as PersonalMasterExpenseResponse;
    expect(r.idempotent_replay).toBe(true);
    expect(r.impact_preview?.relationships).toMatch(/Skipped/i);
    expect(r.impact_preview?.life_operations).not.toMatch(/₹/);
    expect(r.events).toHaveLength(2);
  });

  it("parses Activity list sparse", () => {
    const a = activity as PersonalLifeOpsActivityResponse;
    expect(a.items).toHaveLength(0);
    expect(a.summary.total_logs).toBe(0);
  });
});
