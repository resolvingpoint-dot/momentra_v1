/** Payload builder contract: validate → normalize → build → serialize. */
import { normalizeQuickAddPayload } from "../normalize";

export type PayloadBuilder = {
  builderId: string;
  validate: (form: Record<string, unknown>) => void;
  normalize: (form: Record<string, unknown>) => Record<string, unknown>;
  build: (form: Record<string, unknown>) => Record<string, unknown>;
  serialize: (payload: Record<string, unknown>) => Record<string, unknown>;
};

export function requireFields(
  form: Record<string, unknown>,
  fields: string[],
  builderId: string,
): void {
  const missing = fields.filter((f) => {
    const v = form[f];
    return v == null || v === "" || (Array.isArray(v) && v.length === 0);
  });
  if (missing.length) {
    throw new Error(`${builderId} missing required fields: ${missing.join(", ")}`);
  }
}

export function createPayloadBuilder(opts: {
  builderId: string;
  momentTypeCode: string;
  actionId: string;
  required: string[];
  mapForm?: (form: Record<string, unknown>) => Record<string, unknown>;
}): PayloadBuilder {
  const map = opts.mapForm ?? ((f) => f);
  return {
    builderId: opts.builderId,
    validate(form) {
      requireFields(map(form), opts.required, opts.builderId);
    },
    normalize(form) {
      return normalizeQuickAddPayload(map(form), {
        momentTypeCode: opts.momentTypeCode,
        actionId: opts.actionId,
      });
    },
    build(form) {
      this.validate(form);
      return this.normalize(form);
    },
    serialize(payload) {
      return { ...payload, contract_version: "v1" };
    },
  };
}

export const REFERENCE_PAYLOAD_BUILDERS: Record<string, PayloadBuilder> = {
  "personal.life_operations.expense": createPayloadBuilder({
    builderId: "personal.life_operations.expense",
    momentTypeCode: "LIFE_OPERATIONS",
    actionId: "EXPENSE",
    required: ["amount_minor", "currency_code", "account_id"],
  }),
  "personal.future_building.contribution": createPayloadBuilder({
    builderId: "personal.future_building.contribution",
    momentTypeCode: "FUTURE_BUILDING",
    actionId: "CONTRIBUTION",
    required: ["amount_minor", "currency_code"],
  }),
  "personal.lifestyle.experience": createPayloadBuilder({
    builderId: "personal.lifestyle.experience",
    momentTypeCode: "LIFESTYLE",
    actionId: "EXPERIENCE",
    required: ["title"],
  }),
  "personal.relationships.connection": createPayloadBuilder({
    builderId: "personal.relationships.connection",
    momentTypeCode: "RELATIONSHIPS",
    actionId: "CONNECTION",
    required: ["title"],
  }),
  "group.experience.expense": createPayloadBuilder({
    builderId: "group.experience.expense",
    momentTypeCode: "SHARED_EXPERIENCE",
    actionId: "EXPENSE",
    required: ["amount_minor", "currency_code", "paid_by_participant_id"],
  }),
  "group.purchase.contributor": createPayloadBuilder({
    builderId: "group.purchase.contributor",
    momentTypeCode: "SHARED_PURCHASE",
    actionId: "CONTRIBUTOR",
    required: ["title"],
    mapForm: (f) => ({
      ...f,
      title: f.title ?? f.name ?? f.full_name ?? f.display_name,
    }),
  }),
  "group.living.rent": createPayloadBuilder({
    builderId: "group.living.rent",
    momentTypeCode: "SHARED_LIVING",
    actionId: "RENT",
    required: ["amount_minor", "currency_code"],
  }),
};
