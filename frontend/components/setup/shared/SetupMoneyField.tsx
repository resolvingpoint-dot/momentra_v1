"use client";

import { useEffect, useState } from "react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { SetupField } from "@/components/setup/shared/SetupField";
import { GuidedSetupExplainer } from "@/components/setup/GuidedSetupExplainer";
import {
  findCurrency,
  minorToDisplayInput,
  parseUserInputToMinor,
} from "@/lib/reference_data/money";
import type { CurrencyReference } from "@/lib/reference_data/types";

type Props = {
  label: string;
  helper?: string;
  optionalLabel?: string;
  error?: string | null;
  amountMinor: number | null;
  currencyCode: string;
  currencies?: CurrencyReference[];
  onChange: (amountMinor: number | null) => void;
  disabled?: boolean;
  allowEmpty?: boolean;
  explainer?: { title: string; body: string } | null;
};

const FALLBACK: CurrencyReference = {
  code: "INR",
  label: "Indian Rupee",
  symbol: "₹",
  minor_unit: 2,
};

export function SetupMoneyField({
  label,
  helper,
  optionalLabel,
  error,
  amountMinor,
  currencyCode,
  currencies = [],
  onChange,
  disabled,
  allowEmpty = true,
  explainer,
}: Props) {
  const { colors } = useThemeTokens();
  const currency =
    findCurrency(currencies, currencyCode) ??
    ({ ...FALLBACK, code: currencyCode || "INR" } as CurrencyReference);
  const minorUnit = currency.minor_unit ?? 2;
  const symbol = currency.symbol || currencyCode || "";

  const [display, setDisplay] = useState(() =>
    amountMinor == null ? "" : minorToDisplayInput(amountMinor, minorUnit),
  );

  useEffect(() => {
    if (amountMinor == null) {
      setDisplay("");
      return;
    }
    setDisplay(minorToDisplayInput(amountMinor, minorUnit));
  }, [amountMinor, minorUnit, currencyCode]);

  function handleChange(raw: string) {
    setDisplay(raw);
    if (raw.trim() === "") {
      onChange(allowEmpty ? null : 0);
      return;
    }
    onChange(parseUserInputToMinor(raw, currency));
  }

  return (
    <SetupField
      label={label}
      helper={helper}
      optionalLabel={optionalLabel}
      error={error}
      explainer={
        explainer ? (
          <GuidedSetupExplainer title={explainer.title} body={explainer.body} />
        ) : undefined
      }
    >
      <div
        className="flex min-h-11 items-center gap-2 rounded-xl border px-3 py-2.5"
        style={{
          borderColor: error
            ? colors.error
            : `color-mix(in srgb, ${colors.border} 40%, transparent)`,
          background: colors.background,
        }}
      >
        <span className="text-sm font-semibold opacity-70">{symbol}</span>
        <input
          type="text"
          inputMode="decimal"
          disabled={disabled}
          value={display}
          onChange={(e) => handleChange(e.target.value)}
          placeholder={minorUnit === 0 ? "0" : "0.00"}
          className="w-full bg-transparent text-sm font-semibold outline-none disabled:opacity-50"
          aria-label={`${label} in ${currencyCode}`}
        />
        <span className="text-xs font-medium opacity-50">{currencyCode}</span>
      </div>
    </SetupField>
  );
}
