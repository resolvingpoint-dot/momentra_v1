"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { WidgetInfoButton } from "@/components/personal/shared/WidgetInfoButton";
import { lifestylePulseCopy } from "@/lib/personal/lifestyle/pulse/lifestylePulseCopy";
import { lifestyleQuickAddIcon } from "@/lib/personal/lifestyle/pulse/lifestylePulseIcons";

const MOMENT_TYPE = "LIFESTYLE";

type Props = { onQuickAdd?: (action: string) => void };

const QUICK_ADD_IDS = [
  "LIFESTYLE_EXPENSE",
  "EXPERIENCE",
  "WELLBEING",
  "DISCOVERY",
  "CREATIVE",
  "LIFESTYLE_ADJUST",
];

export function LifestyleQuickLauncher({ onQuickAdd }: Props) {
  const tokens = useThemeTokens();
  const { colors } = tokens;

  return (
    <section className="space-y-3 pt-3">
      <div className="flex items-center gap-0.5 px-1">
        <h3 className="text-[10px] font-bold uppercase tracking-[0.2em] opacity-60">{lifestylePulseCopy.quickAddTitle}</h3>
        <WidgetInfoButton explainerId="PULSE-010" momentTypeCode={MOMENT_TYPE} />
      </div>
      <div className="grid grid-cols-3 gap-2 sm:flex sm:justify-between sm:gap-2 sm:overflow-x-auto sm:pb-3">
        {lifestylePulseCopy.quickAddActions.map((label, index) => {
          const Icon = lifestyleQuickAddIcon(index);
          return (
            <button
              key={label}
              type="button"
              onClick={() => onQuickAdd?.(QUICK_ADD_IDS[index] ?? "LIFESTYLE_EXPENSE")}
              className="flex min-w-0 flex-col items-center gap-1.5 border-0 bg-transparent p-0 sm:min-w-[72px]"
            >
              <div
                className="flex size-14 items-center justify-center rounded-2xl border transition-transform active:scale-90 sm:size-16"
                style={{ background: colors.surfaceContainer, borderColor: "rgba(255,255,255,0.05)" }}
              >
                <Icon className="size-6 sm:size-8" color={colors.brandPrimary} />
              </div>
              <span className="whitespace-pre-line text-center text-[9px] font-bold uppercase">{label}</span>
            </button>
          );
        })}
      </div>
    </section>
  );
}
