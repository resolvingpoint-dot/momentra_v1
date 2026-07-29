"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import type { SetupChoice } from "@/components/setup/shared/setupControlTypes";
import { SetupField } from "@/components/setup/shared/SetupField";

type Props = {
  label: string;
  helper?: string;
  optionalLabel?: string;
  error?: string | null;
  values: string[];
  options: SetupChoice[];
  onChange: (values: string[]) => void;
  disabled?: boolean;
};

/**
 * @deprecated Prefer SetupMultiCards for guided funding/scope multi-select.
 * Still fine for compact burn-category chips.
 */
export function SetupMultiChips({
  label,
  helper,
  optionalLabel,
  error,
  values,
  options,
  onChange,
  disabled,
}: Props) {
  const { colors } = useThemeTokens();
  const selected = new Set(values);

  function toggle(value: string) {
    const next = new Set(selected);
    if (next.has(value)) next.delete(value);
    else next.add(value);
    onChange(Array.from(next));
  }

  return (
    <SetupField label={label} helper={helper} optionalLabel={optionalLabel} error={error}>
      <div className="flex flex-wrap gap-2">
        {options.map((opt) => {
          const on = selected.has(opt.value);
          return (
            <button
              key={opt.value}
              type="button"
              disabled={disabled}
              onClick={() => toggle(opt.value)}
              className="rounded-full border px-3.5 py-2 text-xs font-semibold transition-colors disabled:opacity-50"
              style={{
                borderColor: on
                  ? colors.primary
                  : `color-mix(in srgb, ${colors.border} 45%, transparent)`,
                background: on
                  ? `color-mix(in srgb, ${colors.primary} 18%, transparent)`
                  : colors.background,
                color: on ? colors.primary : colors.textPrimary,
              }}
            >
              {opt.label}
            </button>
          );
        })}
      </div>
    </SetupField>
  );
}
