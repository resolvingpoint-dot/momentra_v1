"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import {
  neuralLineBackground,
  personalGlassCardStyle,
  personalGlowWrapperStyle,
  personalTypography,
} from "@/components/personal/empty/shared/emptyStyles";
import { WidgetInfoButton } from "@/components/personal/shared/WidgetInfoButton";
import { FbAxisRadar } from "@/components/personal/future_building/pulse/widgets/FbAxisRadar";
import type { PersonalFutureBuildingPulseMetrics } from "@/lib/api/personalDomainTypes";
import { fbPulseCopy } from "@/lib/personal/future_building/pulse/fbPulseCopy";
import { TrendingUp } from "lucide-react";

const MOMENT_TYPE = "FUTURE_BUILDING";

type Props = { metrics: PersonalFutureBuildingPulseMetrics };

export function FbPulseHero({ metrics }: Props) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  const stats = metrics.capacity_stats;

  return (
    <section style={personalGlowWrapperStyle(tokens)}>
      <div
        style={{
          ...personalGlassCardStyle(tokens),
          ...neuralLineBackground(),
          borderRadius: 24,
          padding: 24,
          position: "relative",
          overflow: "hidden",
        }}
      >
        <div className="relative z-10 text-center">
          <div className="flex items-center justify-center gap-0.5">
            <p style={{ ...personalTypography.labelSm, color: colors.brandPrimary, fontWeight: 700, letterSpacing: "0.2em", textTransform: "uppercase", fontSize: 10 }}>
              {fbPulseCopy.momentumIndexTitle}
            </p>
            <WidgetInfoButton explainerId="PULSE-001" momentTypeCode={MOMENT_TYPE} />
          </div>
          <div className="mt-2 flex items-baseline justify-center gap-1">
            <span style={{ fontSize: 64, fontWeight: 800, lineHeight: 1, color: colors.textPrimary }}>{metrics.momentum_index}</span>
            <span style={{ fontSize: 24, opacity: 0.4, color: colors.textSecondary }}>{fbPulseCopy.momentumIndexSuffix}</span>
          </div>
          <div className="mt-2 flex items-center justify-center gap-2">
            <span style={{ color: colors.brandPrimary, fontWeight: 700, fontSize: 14 }}>{metrics.status_label}</span>
            {metrics.momentum_index_delta_month != null && metrics.momentum_index_delta_month !== 0 ? (
              <span
                className="flex items-center gap-1 rounded-full border px-3 py-1 text-xs font-bold"
                style={{ background: `${colors.brandTertiary}1a`, color: colors.brandTertiary, borderColor: `${colors.brandTertiary}33` }}
              >
                <TrendingUp size={12} /> ↑ {metrics.momentum_index_delta_month} this month
              </span>
            ) : null}
          </div>
        </div>
        <div className="relative z-10 mt-4">
          <div className="mb-1 flex justify-end">
            <WidgetInfoButton explainerId="PULSE-002" momentTypeCode={MOMENT_TYPE} />
          </div>
          <FbAxisRadar scores={metrics.axis_scores} />
        </div>
        <div
          className="relative z-10 mt-8 grid grid-cols-2 gap-2 border-t pt-6 sm:grid-cols-4"
          style={{ borderColor: "rgba(255,255,255,0.06)" }}
        >
          <div className="col-span-2 flex items-center justify-center gap-0.5 sm:col-span-4">
            <p className="text-[8px] sm:text-[10px]" style={{ fontWeight: 700, textTransform: "uppercase", opacity: 0.5, letterSpacing: "-0.02em" }}>
              Capacity
            </p>
            <WidgetInfoButton explainerId="PULSE-003" momentTypeCode={MOMENT_TYPE} />
          </div>
          {[
            { label: "Investments", value: fbPulseCopy.formatInrMinor(stats.investments_minor), border: false },
            { label: "Milestones", value: `${stats.milestones}`, border: true },
            { label: "Learning", value: `${stats.learning_events}`, border: true },
            { label: "Opportunities", value: `${stats.opportunities}`, border: true },
          ].map((stat, i) => (
            <div key={stat.label} className="flex flex-col items-center" style={stat.border && i !== 0 ? { borderLeft: "1px solid rgba(255,255,255,0.06)" } : undefined}>
              <p className="text-[8px] sm:text-[10px]" style={{ fontWeight: 700, textTransform: "uppercase", opacity: 0.5, letterSpacing: "-0.02em" }}>{stat.label}</p>
              <p className="text-xs sm:text-sm" style={{ fontWeight: 700, color: colors.textPrimary }}>{stat.value}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
