import { describe, expect, it } from "vitest";
import type { ActivePulseResponse, ActiveMemoryResponse } from "@/lib/api/group";
import experiencePulse from "@/lib/group/fixtures/dto/experience_pulse_sparse.json";
import purchasePulse from "@/lib/group/fixtures/dto/purchase_pulse_sparse.json";
import livingPulse from "@/lib/group/fixtures/dto/living_pulse_sparse.json";
import settlementEmpty from "@/lib/group/fixtures/dto/settlement_preview_empty.json";
import experienceMemory from "@/lib/group/fixtures/dto/experience_memory_sparse.json";

function assertActivePulse(raw: unknown): ActivePulseResponse {
  const d = raw as ActivePulseResponse;
  expect(typeof d.moment_id).toBe("string");
  expect(typeof d.moment_type).toBe("string");
  expect(typeof d.moment_name).toBe("string");
  expect(d.pulse_data).toBeTypeOf("object");
  expect(d.health_data).toBeTypeOf("object");
  expect(Array.isArray(d.signals)).toBe(true);
  expect(Array.isArray(d.recommendations)).toBe(true);
  expect(Array.isArray(d.recent_events)).toBe(true);
  return d;
}

describe("Group DTO contracts (sparse projections)", () => {
  it("parses Shared Experience Pulse sparse fixture", () => {
    const d = assertActivePulse(experiencePulse);
    expect(d.signals).toHaveLength(0);
    expect(d.recent_events).toHaveLength(0);
    expect(Number(d.pulse_data.active_members ?? 0)).toBe(0);
  });

  it("parses Shared Living Pulse sparse fixture as ActivePulse shape", () => {
    assertActivePulse(livingPulse);
  });

  it("parses Shared Purchase Pulse settlement_preview without invented pending", () => {
    const p = purchasePulse as {
      settlement_preview: { pending_count?: number; harmony_label: string; total_spent_minor: number };
    };
    expect(p.settlement_preview.pending_count ?? 0).toBe(0);
    expect(p.settlement_preview.total_spent_minor).toBe(0);
    expect(p.settlement_preview.harmony_label).toBeTruthy();
  });

  it("parses settlement context empty fixture", () => {
    expect(settlementEmpty.pending_balances).toEqual([]);
    expect(settlementEmpty.balance_sync_percent).toBe(100);
  });

  it("parses Experience Memory sparse fixture", () => {
    const m = experienceMemory as unknown as ActiveMemoryResponse;
    expect(m.moment_id).toBeTruthy();
    expect(Array.isArray(m.memories)).toBe(true);
    expect(m.memories).toHaveLength(0);
  });
});
