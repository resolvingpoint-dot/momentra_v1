"use client";

import { useEffect, useMemo, useState } from "react";
import { usePersonalDomainTokens } from "@/lib/personal/personalDomainPalette";
import { personalTypography } from "@/components/personal/empty/shared/emptyStyles";
import {
  findCurrency,
  formatMinor,
  minorToDisplayInput,
  parseUserInputToMinor,
} from "@/lib/reference_data/money";
import type { CurrencyReference, MoneyValue } from "@/lib/reference_data/types";

type MoneyInputProps = {
  label?: string;
  value: MoneyValue;
  onChange: (value: MoneyValue) => void;
  currencies: CurrencyReference[];
  defaultCurrencyCode: string;
  locale?: string;
  className?: string;
};

export function MoneyInput({
  label = "Amount",
  value,
  onChange,
  currencies,
  defaultCurrencyCode,
  locale = "en-IN",
  className,
}: MoneyInputProps) {
  const { colors } = usePersonalDomainTokens();
  const activeCurrency =
    findCurrency(currencies, value.currency_code) ??
    findCurrency(currencies, defaultCurrencyCode) ??
    currencies[0];

  const minorUnit = activeCurrency?.minor_unit ?? 2;
  const [displayValue, setDisplayValue] = useState(() =>
    minorToDisplayInput(value.amount_minor, minorUnit),
  );

  useEffect(() => {
    setDisplayValue(minorToDisplayInput(value.amount_minor, minorUnit));
  }, [value.amount_minor, minorUnit, value.currency_code]);

  const formattedHint = useMemo(() => {
    if (!activeCurrency || value.amount_minor <= 0) return null;
    return formatMinor(value.amount_minor, activeCurrency, locale);
  }, [activeCurrency, locale, value.amount_minor]);

  function handleAmountChange(next: string) {
    setDisplayValue(next);
    if (!activeCurrency) return;
    onChange({
      currency_code: value.currency_code,
      amount_minor: parseUserInputToMinor(next, activeCurrency),
    });
  }

  function handleCurrencyChange(code: string) {
    const currency = findCurrency(currencies, code);
    if (!currency) return;
    const amountMinor = parseUserInputToMinor(displayValue, currency);
    onChange({ currency_code: code, amount_minor: amountMinor });
  }

  return (
    <div className={className ?? "space-y-2"}>
      <label style={{ ...personalTypography.sectionHeader, color: colors.textSecondary }}>
        {label}
      </label>
      <div className="flex gap-2">
        <select
          value={value.currency_code}
          onChange={(e) => handleCurrencyChange(e.target.value)}
          className="rounded-2xl border-none px-3 py-4 text-sm font-semibold"
          style={{
            background: colors.surfaceContainerLowest ?? "#0e0d16",
            color: colors.brandPrimary,
          }}
          aria-label="Currency"
        >
          {currencies.map((c) => (
            <option key={c.code} value={c.code}>
              {c.symbol} {c.code}
            </option>
          ))}
        </select>
        <div className="relative flex-1">
          <input
            type="text"
            inputMode="decimal"
            value={displayValue}
            onChange={(e) => handleAmountChange(e.target.value)}
            placeholder={minorUnit === 0 ? "0" : "0.00"}
            className="w-full rounded-2xl border-none py-6 px-4 text-3xl font-bold"
            style={{
              background: colors.surfaceContainerLowest ?? "#0e0d16",
              color: colors.textPrimary,
            }}
          />
        </div>
      </div>
      {formattedHint ? (
        <p className="text-xs" style={{ color: colors.textSecondary }}>
          {formattedHint}
        </p>
      ) : null}
    </div>
  );
}
