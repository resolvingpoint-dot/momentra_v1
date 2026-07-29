"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import type { SetupChoice } from "@/components/setup/shared/setupControlTypes";
import { SetupField } from "@/components/setup/shared/SetupField";
import { GuidedSetupExplainer } from "@/components/setup/GuidedSetupExplainer";
import { useGuidedSetupTheme } from "@/components/setup/GuidedSetupTheme";

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
  multi?: false;
};

/** Card-style single select for short option sets (team size, stage, scope, etc.). */
export function SetupChoiceCards({
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
  const setupTheme = useGuidedSetupTheme();

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
          const selected = value === opt.value;
          return (
            <button
              key={opt.value}
              type="button"
              disabled={disabled}
              title={opt.description}
              onClick={() => onChange(opt.value)}
              className="min-h-10 rounded-xl border px-2.5 py-2 text-left transition-colors disabled:opacity-50"
              style={{
                borderColor: selected
                  ? setupTheme.accentColor
                  : error
                    ? colors.error
                    : `color-mix(in srgb, ${colors.border} 45%, transparent)`,
                background: selected ? setupTheme.selectedCard : colors.background,
              }}
              aria-pressed={selected}
            >
              <span className="block text-sm font-semibold leading-snug">{opt.label}</span>
              {opt.description ? (
                <span className="mt-0.5 block text-[10px] leading-snug opacity-65 line-clamp-2">
                  {opt.description}
                </span>
              ) : null}
            </button>
          );
        })}
      </div>
    </SetupField>
  );
}
