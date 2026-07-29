"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { SetupField } from "@/components/setup/shared/SetupField";
import { GuidedSetupExplainer } from "@/components/setup/GuidedSetupExplainer";

const PRESETS = [50, 70, 80, 90, 100];

type Props = {
  label: string;
  helper?: string;
  optionalLabel?: string;
  error?: string | null;
  value: number | null;
  onChange: (value: number | null) => void;
  disabled?: boolean;
  explainer?: { title: string; body: string } | null;
  min?: number;
  max?: number;
};

/** Chips + slider for percentage fields such as collection rate. */
export function SetupPercentField({
  label,
  helper,
  optionalLabel,
  error,
  value,
  onChange,
  disabled,
  explainer,
  min = 0,
  max = 100,
}: Props) {
  const { colors } = useThemeTokens();
  const current = value == null || !Number.isFinite(value) ? null : Math.round(value);

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
      <div className="space-y-3">
        <div className="flex flex-wrap gap-2">
          {PRESETS.map((p) => {
            const selected = current === p;
            return (
              <button
                key={p}
                type="button"
                disabled={disabled}
                onClick={() => onChange(p)}
                className="min-h-11 rounded-xl px-3 py-2 text-sm font-semibold disabled:opacity-50"
                style={{
                  background: selected ? colors.primaryContainer : colors.surfaceContainer,
                  color: selected ? colors.brandOnPrimary : colors.textPrimary,
                }}
                aria-pressed={selected}
              >
                {p}%
              </button>
            );
          })}
        </div>
        <div className="flex items-center gap-3">
          <input
            type="range"
            min={min}
            max={max}
            step={1}
            disabled={disabled}
            value={current ?? 80}
            onChange={(e) => onChange(Number(e.target.value))}
            className="min-h-11 w-full accent-current"
            aria-valuemin={min}
            aria-valuemax={max}
            aria-valuenow={current ?? 80}
            aria-label={label}
          />
          <span className="w-12 shrink-0 text-right text-sm font-semibold tabular-nums">
            {current == null ? "—" : `${current}%`}
          </span>
        </div>
      </div>
    </SetupField>
  );
}
