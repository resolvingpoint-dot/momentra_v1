/** Quick Add v1 boundary normalizers — mirror backend contract aliases. */

export const MOMENT_TYPE_ALIASES: Record<string, string> = {
  TRIP: "SHARED_EXPERIENCE",
  EMOTIONAL_SECURITY: "RELATIONSHIPS",
};

export const ACTION_ID_ALIASES: Record<string, string> = {
  RENT: "EXPENSE",
  UTILITY: "EXPENSE",
  CAPTURE_MEMORY: "MEMORY",
  HOME_MEMORY: "MEMORY",
  PURCHASE_EXPENSE: "EXPENSE",
  RELATIONSHIP_ADJUST: "ADJUST",
};

/** Reserved future money contribution — never alias to CONTRIBUTOR. */
export const RESERVED_ACTION_IDS = new Set(["PURCHASE_CONTRIBUTION"]);

const PAYER_KEYS = [
  "paid_by_participant_id",
  "paid_by",
  "paidBy",
  "payer",
  "paid_by_user_id",
  "paid_by_member_id",
  "paid_by_member",
] as const;

export function normalizeMomentTypeCode(code: string | null | undefined): string {
  if (!code) return "";
  const raw = String(code).trim();
  return MOMENT_TYPE_ALIASES[raw] ?? raw;
}

export function normalizeActionId(actionId: string | null | undefined): string {
  if (!actionId) return "";
  const raw = String(actionId).trim().toUpperCase();
  if (raw === "CONTRIBUTOR") return "CONTRIBUTOR";
  if (RESERVED_ACTION_IDS.has(raw)) return raw;
  return ACTION_ID_ALIASES[raw] ?? raw;
}

export function rentCategoryForAlias(actionId: string | null | undefined): string | null {
  const raw = String(actionId ?? "")
    .trim()
    .toUpperCase();
  if (raw === "RENT") return "rent";
  if (raw === "UTILITY") return "utility";
  return null;
}

function toAmountMinor(value: unknown, fromMajor = false): number | null {
  if (value == null || value === "") return null;
  if (typeof value === "number" && Number.isFinite(value)) {
    return fromMajor ? Math.round(value * 100) : Math.round(value);
  }
  const raw = String(value).replace(/,/g, "").trim();
  if (!raw) return null;
  const parsed = Number.parseFloat(raw);
  if (!Number.isFinite(parsed)) return null;
  if (fromMajor || raw.includes(".")) return Math.round(parsed * 100);
  return Math.round(parsed);
}

export function normalizeQuickAddPayload(
  data: Record<string, unknown>,
  opts?: { momentTypeCode?: string; actionId?: string },
): Record<string, unknown> {
  const src = { ...data };
  const out: Record<string, unknown> = { ...src };
  const mt = normalizeMomentTypeCode(
    opts?.momentTypeCode ?? (typeof src.moment_type_code === "string" ? src.moment_type_code : ""),
  );
  if (mt) out.moment_type_code = mt;

  const rawAction =
    opts?.actionId ??
    (typeof src.action_id === "string" ? src.action_id : null) ??
    (typeof src.event_type === "string" ? src.event_type : null);
  const rentCat = rentCategoryForAlias(rawAction);
  const action = normalizeActionId(rawAction);
  if (action) {
    out.action_id = action;
    if ("event_type" in src || opts?.actionId) out.event_type = action;
  }

  for (const key of PAYER_KEYS) {
    if (src[key] != null && src[key] !== "") {
      out.paid_by_participant_id = String(src[key]);
      break;
    }
  }
  for (const key of PAYER_KEYS) {
    if (key !== "paid_by_participant_id") delete out[key];
  }

  if (src.amount_minor != null && src.amount_minor !== "") {
    out.amount_minor = toAmountMinor(src.amount_minor) ?? 0;
  } else if (src.amount_major != null && src.amount_major !== "") {
    out.amount_minor = toAmountMinor(src.amount_major, true) ?? 0;
    delete out.amount_major;
  } else if (src.amount != null && src.amount !== "") {
    out.amount_minor = toAmountMinor(src.amount, true) ?? 0;
    delete out.amount;
  }

  const currency = src.currency_code ?? src.currency ?? src.currencyCode;
  if (currency != null && currency !== "") {
    out.currency_code = String(currency).toUpperCase().trim();
    delete out.currency;
    delete out.currencyCode;
  }

  if (rentCat) {
    out.category_code = rentCat;
    out.subcategory_code = null;
  } else {
    const category = src.category_code ?? src.category ?? src.expense_category ?? src.category_name;
    if (category != null && category !== "") {
      const raw = String(category).trim();
      const legacy = new Set(["rent", "utility", "utilities", "other"]);
      out.category_code = legacy.has(raw.toLowerCase()) ? raw.toLowerCase() : raw.toUpperCase();
    }
  }
  delete out.category;
  delete out.expense_category;
  delete out.category_name;

  if ("subcategory_code" in src && src.subcategory_code === null) {
    out.subcategory_code = null;
  } else {
    const sub =
      src.subcategory_code ?? src.subcategory ?? src.sub_category ?? src.expense_subcategory;
    if (sub != null && sub !== "") {
      const cat = String(out.category_code ?? "").toLowerCase();
      if (["rent", "utility", "utilities", "other"].includes(cat)) {
        out.subcategory_code = null;
      } else {
        out.subcategory_code = String(sub).trim().toUpperCase();
      }
    }
  }
  delete out.subcategory;
  delete out.sub_category;
  delete out.expense_subcategory;

  if (out.split_type != null && out.split_style == null) {
    out.split_style = String(out.split_type).toUpperCase();
    delete out.split_type;
  } else if (out.split_style != null) {
    out.split_style = String(out.split_style).toUpperCase();
  }

  if ("subcategory_code" in out || "subcategory" in src || "expense_subcategory" in src) {
    out.contract_version = "v2";
  } else {
    out.contract_version = "v1";
  }
  return out;
}
