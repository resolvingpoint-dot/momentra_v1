"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { personalGlassCardStyle } from "@/components/personal/empty/shared/emptyStyles";
import type { PersonalLifestylePulseMetrics } from "@/lib/api/personal";
import { lifestylePulseCopy } from "@/lib/personal/lifestyle/pulse/lifestylePulseCopy";

type Props = { metrics: PersonalLifestylePulseMetrics };

function buildPills(metrics: PersonalLifestylePulseMetrics) {
  const fulfillment = metrics.signals.find((s) => s.signal_id === "fulfillment");
  const exploration = metrics.signals.find((s) => s.signal_id === "exploration");
  const creativity = metrics.score_drivers.find((d) => d.driver_id === "creativity");
  const joy = metrics.signals.find((s) => s.signal_id === "joy");
  const keys = ["fulfillmentRising", "creativityStrong", "explorationImproving", "lifestyleDriftLow"] as const;
  return keys.map((key, i) => ({
    key,
    label: lifestylePulseCopy.statusPillLabels[key],
    arrow:
      i === 1
        ? (creativity?.impact ?? 0) >= 0
          ? "→"
          : "↓"
        : lifestylePulseCopy.trendArrow(
            (i === 0 ? fulfillment : i === 2 ? exploration : joy)?.trend ?? "FLAT",
          ),
    accent: i === 0,
  }));
}

export function LifestyleSignalPills({ metrics }: Props) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  const pills = buildPills(metrics);

  return (
    <section className="flex flex-wrap gap-2">
      {pills.map((pill) => (
        <div
          key={pill.key}
          className="flex items-center gap-2 rounded-full border px-3 py-2 text-[10px] font-bold"
          style={{
            background: colors.surfaceContainer,
            borderColor: "rgba(255,255,255,0.05)",
            color: pill.accent ? colors.tertiary : colors.textPrimary,
            opacity: pill.key === "lifestyleDriftLow" ? 0.5 : 1,
          }}
        >
          <div
            className="size-1.5 rounded-full"
            style={{
              background: pill.accent ? colors.tertiary : colors.brandSecondary,
              animation: pill.accent ? "pulse 2s infinite" : undefined,
            }}
          />
          {pill.label} {pill.arrow}
        </div>
      ))}
    </section>
  );
}
