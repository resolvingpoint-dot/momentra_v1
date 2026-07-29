import { readFileSync } from "fs";
import { join } from "path";
import { describe, expect, it } from "vitest";
import { normalizeActionId, normalizeMomentTypeCode, normalizeQuickAddPayload } from "./normalize";
import { REFERENCE_PAYLOAD_BUILDERS } from "./payloadBuilders/contract";
import { computeRegistryHash, loadReferenceActions, validateReferenceRegistry } from "./registryValidator";

const FIXTURES = join(__dirname, "../../../fixtures/quick_add");

describe("Quick Add registry validator", () => {
  it("passes reference registry + hash lock", () => {
    const result = validateReferenceRegistry(FIXTURES);
    expect(result.issues).toEqual([]);
    expect(result.ok).toBe(true);
    expect(result.registryHash).toHaveLength(64);
  });

  it("matches lockfile hash", () => {
    const actions = loadReferenceActions(FIXTURES);
    const hash = computeRegistryHash(actions);
    const lock = readFileSync(join(FIXTURES, "registry_hash.lock"), "utf8").trim();
    expect(hash).toBe(lock);
  });
});

describe("Quick Add normalize", () => {
  it("maps aliases", () => {
    expect(normalizeMomentTypeCode("TRIP")).toBe("SHARED_EXPERIENCE");
    expect(normalizeActionId("RENT")).toBe("EXPENSE");
    expect(normalizeActionId("CONTRIBUTOR")).toBe("CONTRIBUTOR");
  });

  it("does not collapse reserved PURCHASE_CONTRIBUTION into CONTRIBUTOR", () => {
    expect(normalizeActionId("PURCHASE_CONTRIBUTION")).toBe("PURCHASE_CONTRIBUTION");
    expect(normalizeActionId("PURCHASE_CONTRIBUTION")).not.toBe("CONTRIBUTOR");
    expect(normalizeActionId("CONTRIBUTOR")).not.toBe("PURCHASE_CONTRIBUTION");
  });

  it("normalizes payer and amount", () => {
    const out = normalizeQuickAddPayload(
      { amount: "12.50", paid_by: "abc", currency: "usd" },
      { momentTypeCode: "TRIP", actionId: "EXPENSE" },
    );
    expect(out.amount_minor).toBe(1250);
    expect(out.paid_by_participant_id).toBe("abc");
    expect(out.currency_code).toBe("USD");
  });
});

describe("shared fixtures", () => {
  const names = [
    "personal_life_ops_expense.json",
    "personal_future_contribution.json",
    "personal_lifestyle_experience.json",
    "personal_relationship_connection.json",
    "group_experience_expense.json",
    "group_purchase_contribution.json",
    "group_living_rent.json",
  ];

  it.each(names)("loads %s", (name) => {
    const data = JSON.parse(readFileSync(join(FIXTURES, name), "utf8"));
    const expected =
      name === "personal_life_ops_expense.json" || name === "group_experience_expense.json"
        ? "v2"
        : "v1";
    expect(data.contract_version).toBe(expected);
    expect(data.wire).toBeTruthy();
  });
});

describe("payload builders", () => {
  it("builds living rent with category", () => {
    const builder = REFERENCE_PAYLOAD_BUILDERS["group.living.rent"];
    const payload = builder.build({
      amount_minor: 120000,
      currency_code: "USD",
      title: "April rent",
    });
    expect(payload.action_id).toBe("EXPENSE");
    expect(payload.category_code).toBe("rent");
    expect(builder.serialize(payload).contract_version).toBe("v1");
  });
});
