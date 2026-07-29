import type { FormState } from "@/components/business/actioncenter/ProgressiveActionForm";
import { parseAmountMinor } from "@/components/business/actioncenter/fields";

export function req(state: FormState, key: string, label: string): Record<string, string> {
  const v = state[key];
  if (v == null || v === "" || (Array.isArray(v) && !v.length)) {
    return { [key]: `${label} is required` };
  }
  return {};
}

export function reqAmount(state: FormState, key = "amount", label = "Amount"): Record<string, string> {
  const n = Number.parseFloat(String(state[key] ?? ""));
  if (!Number.isFinite(n) || n <= 0) return { [key]: `Enter a valid ${label.toLowerCase()} greater than 0` };
  return {};
}

export function todayISO(): string {
  return new Date().toISOString().slice(0, 10);
}

export function moneyPayload(
  state: FormState,
  amountKey = "amount",
  currencyKey = "currency_code",
): { amount_minor: number; currency_code: string } {
  const currency = String(state[currencyKey] || state.currency || "INR");
  return {
    amount_minor: parseAmountMinor(String(state[amountKey] ?? "0")),
    currency_code: currency,
  };
}

export function memberLabel(
  members: Array<{ member_id?: string; id?: string; name?: string; display_name?: string }>,
  id: string,
): string {
  const m = members.find((x) => (x.member_id || x.id) === id);
  return m?.name || m?.display_name || id || "—";
}

export function chipLabel(options: Array<{ value: string; label: string }>, value: string): string {
  return options.find((o) => o.value === value)?.label || value || "—";
}

/** Schema forms store major units under amount field keys; convert to minor int for ActivityEngine. */
export function schemaAmountToMinor(raw: Record<string, unknown>, amountKeys: string[] = ["amount_minor", "amount"]): Record<string, unknown> {
  const out = { ...raw };
  for (const key of amountKeys) {
    if (out[key] == null || out[key] === "") continue;
    if (typeof out[key] === "number" && Number.isInteger(out[key])) continue;
    const major = String(out[key]);
    out.amount_minor = parseAmountMinor(major);
    if (key !== "amount_minor") delete out[key];
  }
  if (out.currency && !out.currency_code) {
    out.currency_code = out.currency;
    delete out.currency;
  }
  return out;
}
