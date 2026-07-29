import type { CurrencyReference } from "@/lib/reference_data/types";

export function parseUserInputToMinor(
  input: string,
  currency: Pick<CurrencyReference, "minor_unit">,
): number {
  const trimmed = input.trim();
  if (!trimmed) return 0;
  const normalized = trimmed.replace(/,/g, "");
  const parts = normalized.split(".");
  const whole = parts[0]?.replace(/\D/g, "") || "0";
  const fraction = (parts[1] ?? "").replace(/\D/g, "");
  const minorUnit = currency.minor_unit ?? 2;
  if (minorUnit === 0) {
    return parseInt(whole, 10) || 0;
  }
  const fracPadded = fraction.padEnd(minorUnit, "0").slice(0, minorUnit);
  const combined = `${whole}${fracPadded}`;
  return parseInt(combined, 10) || 0;
}

export function formatMinor(
  amountMinor: number,
  currency: Pick<CurrencyReference, "code" | "minor_unit" | "symbol">,
  locale: string,
): string {
  const minorUnit = currency.minor_unit ?? 2;
  const divisor = 10 ** minorUnit;
  const major = amountMinor / divisor;
  try {
    return new Intl.NumberFormat(locale, {
      style: "currency",
      currency: currency.code,
      minimumFractionDigits: minorUnit,
      maximumFractionDigits: minorUnit,
    }).format(major);
  } catch {
    return `${currency.symbol}${major.toFixed(minorUnit)}`;
  }
}

export function minorToDisplayInput(
  amountMinor: number,
  minorUnit: number,
): string {
  if (amountMinor <= 0) return "";
  if (minorUnit === 0) return String(amountMinor);
  const divisor = 10 ** minorUnit;
  const major = amountMinor / divisor;
  return major.toFixed(minorUnit).replace(/\.?0+$/, "") || String(major);
}

export function findCurrency(
  currencies: CurrencyReference[],
  code: string,
): CurrencyReference | undefined {
  return currencies.find((c) => c.code === code);
}
