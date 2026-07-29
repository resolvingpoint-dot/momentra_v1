"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import type { SetupChoice } from "@/components/setup/shared/setupControlTypes";
import { SetupField } from "@/components/setup/shared/SetupField";
import { GuidedSetupExplainer } from "@/components/setup/GuidedSetupExplainer";

type Props = {
  label: string;
  helper?: string;
  optionalLabel?: string;
  error?: string | null;
  value: string;
  options: SetupChoice[];
  onChange: (value: string) => void;
  disabled?: boolean;
  explainer?: { title: string; body: string } | null;
};

/** Single-select chips for 2–7 finite choices. Stores canonical enum values. */
export function SetupChoiceChips({
  label,
  helper,
  optionalLabel,
  error,
  value,
  options,
  onChange,
  disabled,
  explainer,
}: Props) {
  const { colors } = useThemeTokens();
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
      <div className="flex flex-wrap gap-2" role="listbox" aria-label={label}>
        {options.map((opt) => {
          const selected = value === opt.value;
          return (
            <button
              key={opt.value}
              type="button"
              disabled={disabled}
              title={opt.description}
              onClick={() => onChange(opt.value)}
              className="min-h-9 rounded-full border px-3 py-1.5 text-xs font-semibold transition-colors disabled:opacity-50"
              style={{
                borderColor: selected
                  ? colors.primary
                  : error
                    ? colors.error
                    : `color-mix(in srgb, ${colors.border} 45%, transparent)`,
                background: selected
                  ? `color-mix(in srgb, ${colors.primary} 18%, transparent)`
                  : colors.background,
                color: selected ? colors.primary : colors.textPrimary,
              }}
              role="option"
              aria-selected={selected}
            >
              {opt.label}
            </button>
          );
        })}
      </div>
      {value ? (
        (() => {
          const desc = options.find((o) => o.value === value)?.description;
          return desc ? (
            <p className="mt-1 text-xs opacity-70" style={{ color: colors.textSecondary }}>
              {desc}
            </p>
          ) : null;
        })()
      ) : null}
    </SetupField>
  );
}
