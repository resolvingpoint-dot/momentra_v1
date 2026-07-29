"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { WidgetInfoButton } from "@/components/personal/shared/WidgetInfoButton";
import { fbPulseCopy } from "@/lib/personal/future_building/pulse/fbPulseCopy";
import { Flag, GraduationCap, IndianRupee, Rocket, Star, TrendingUp } from "lucide-react";

const MOMENT_TYPE = "FUTURE_BUILDING";

const QUICK_ADD_ICONS: Record<string, typeof TrendingUp> = {
  CONTRIBUTION: IndianRupee,
  PROGRESS: TrendingUp,
  MILESTONE: Star,
  OPPORTUNITY: Rocket,
  LEARNING: GraduationCap,
  PIVOT: Flag,
};

const ICON_COLORS = ["primary", "secondary", "tertiary", "primary", "secondary"] as const;

type Props = { onQuickAdd?: (action: string) => void };

export function FbQuickAddGrid({ onQuickAdd }: Props) {
  const { colors } = useThemeTokens();

  return (
    <section className="pb-6">
      <div className="mb-6 flex items-center justify-center gap-0.5">
        <h3
          className="text-center text-[10px] font-bold uppercase tracking-widest"
          style={{ color: colors.textSecondary, opacity: 0.4 }}
        >
          {fbPulseCopy.quickAddTitle}
        </h3>
        <WidgetInfoButton explainerId="PULSE-010" momentTypeCode={MOMENT_TYPE} />
      </div>
      <div className="grid grid-cols-3 gap-2 sm:grid-cols-6">
        {fbPulseCopy.quickAddActions.map((action, i) => {
          const Icon = QUICK_ADD_ICONS[action.code] ?? TrendingUp;
          const colorKey = ICON_COLORS[i % ICON_COLORS.length];
          const iconColor =
            colorKey === "secondary" ? colors.brandSecondary : colorKey === "tertiary" ? colors.brandTertiary : colors.brandPrimary;
          return (
            <button
              key={action.code}
              type="button"
              onClick={() => onQuickAdd?.(action.code)}
              className="group flex min-w-0 flex-col items-center gap-3 border-none bg-transparent p-0"
            >
              <div
                className="flex size-12 items-center justify-center rounded-2xl border transition-transform group-active:scale-90 sm:size-14"
                style={{ background: "rgba(255,255,255,0.05)", borderColor: "rgba(255,255,255,0.1)", boxShadow: "inset 0 1px 0 rgba(255,255,255,0.05)" }}
              >
                <Icon className="size-5 sm:size-6" color={iconColor} />
              </div>
              <span className="text-center text-[9px] font-bold leading-tight" style={{ color: colors.textSecondary, opacity: 0.8 }}>
                {action.label.split(" ").map((word, wi) => (
                  <span key={wi} className="block">
                    {word}
                  </span>
                ))}
              </span>
            </button>
          );
        })}
      </div>
    </section>
  );
}
