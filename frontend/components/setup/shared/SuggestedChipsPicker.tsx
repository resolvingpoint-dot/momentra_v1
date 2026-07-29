"use client";

import { useMemo, useState } from "react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import type { SetupChoice } from "@/components/setup/shared/setupControlTypes";
import { SetupField } from "@/components/setup/shared/SetupField";
import { SetupSearchPicker } from "@/components/setup/shared/SetupSearchPicker";

type Props = {
  label: string;
  helper?: string;
  optionalLabel?: string;
  error?: string | null;
  value: string;
  options: SetupChoice[];
  suggested?: string[];
  onChange: (value: string) => void;
  disabled?: boolean;
  viewAllLabel?: string;
};

/** Suggested chips for compact defaults + searchable picker for the full list. */
export function SuggestedChipsPicker({
  label,
  helper,
  optionalLabel,
  error,
  value,
  options,
  suggested = [],
  onChange,
  disabled,
  viewAllLabel = "View all…",
}: Props) {
  const { colors } = useThemeTokens();
  const [showAll, setShowAll] = useState(false);

  const suggestedOptions = useMemo(() => {
    const fromSuggested = suggested
      .map((code) => options.find((o) => o.value === code))
      .filter(Boolean) as SetupChoice[];
    if (fromSuggested.length > 0) return fromSuggested;
    return options.slice(0, 4);
  }, [options, suggested]);

  if (showAll) {
    return (
      <div className="space-y-2">
        <SetupSearchPicker
          label={label}
          helper={helper}
          optionalLabel={optionalLabel}
          error={error}
          value={value}
          options={options}
          onChange={(next) => {
            onChange(next);
            setShowAll(false);
          }}
          disabled={disabled}
        />
        <button
          type="button"
          className="text-xs font-semibold underline opacity-70"
          onClick={() => setShowAll(false)}
        >
          Show suggestions
        </button>
      </div>
    );
  }

  return (
    <SetupField label={label} helper={helper} optionalLabel={optionalLabel} error={error}>
      <div className="flex flex-wrap gap-2">
        {suggestedOptions.map((opt) => {
          const selected = value === opt.value;
          return (
            <button
              key={opt.value}
              type="button"
              disabled={disabled}
              onClick={() => onChange(opt.value)}
              className="min-h-9 rounded-full px-3 py-1.5 text-xs font-semibold disabled:opacity-50"
              style={{
                background: selected ? colors.primaryContainer : colors.surfaceContainer,
                color: selected ? colors.brandOnPrimary : colors.textPrimary,
                ...(error && !selected
                  ? { outline: `1px solid ${colors.error}`, outlineOffset: 1 }
                  : {}),
              }}
              aria-pressed={selected}
            >
              {opt.label}
            </button>
          );
        })}
        <button
          type="button"
          disabled={disabled}
          onClick={() => setShowAll(true)}
          className="min-h-9 rounded-full border px-3 py-1.5 text-xs font-semibold disabled:opacity-50"
          style={{ borderColor: `color-mix(in srgb, ${colors.border} 40%, transparent)` }}
        >
          {viewAllLabel}
        </button>
      </div>
    </SetupField>
  );
}
