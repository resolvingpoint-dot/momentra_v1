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
  values: string[];
  options: SetupChoice[];
  onChange: (values: string[]) => void;
  disabled?: boolean;
  explainer?: { title: string; body: string } | null;
};

/** Multi-select cards (e.g. funding sources) — replaces long checkbox lists. */
export function SetupMultiCards({
  label,
  helper,
  optionalLabel,
  error,
  values,
  options,
  onChange,
  disabled,
  explainer,
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
      <div className="grid grid-cols-2 gap-2">
        {options.map((opt) => {
          const on = selected.has(opt.value);
          return (
            <button
              key={opt.value}
              type="button"
              disabled={disabled}
              onClick={() => toggle(opt.value)}
              className="min-h-11 rounded-2xl border px-3 py-3 text-left text-sm font-semibold transition-colors disabled:opacity-50"
              style={{
                borderColor: on
                  ? colors.primary
                  : `color-mix(in srgb, ${colors.border} 45%, transparent)`,
                background: on
                  ? `color-mix(in srgb, ${colors.primary} 14%, transparent)`
                  : colors.background,
              }}
              aria-pressed={on}
            >
              {opt.label}
            </button>
          );
        })}
      </div>
    </SetupField>
  );
}
