"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { personalTypography } from "@/components/personal/empty/shared/emptyStyles";
import { lifeOpsPulseCopy } from "@/lib/personal/life_operations/pulse/lifeOpsPulseCopy";
import {
  DONUT_INNER_RADIUS,
  DONUT_RADIUS,
  DONUT_SIZE,
  PULSE_PIE_PROPS,
} from "@/lib/personal/life_operations/pulse/pulseChartTheme";
import { SEGMENT_COLORS } from "@/lib/personal/life_operations/pulse/pulseIcons";
import { PieChart } from "react-gifted-charts";

type Segment = {
  category_id: string;
  category_name?: string | null;
  amount_minor: number;
  share_percent: number;
};

type DonutChartProps = {
  segments: Segment[];
  fallbackTotalMinor?: number;
};

export function DonutChart({ segments, fallbackTotalMinor = 0 }: DonutChartProps) {
  const { colors } = useThemeTokens();
  const totalMinor = segments.length > 0
    ? segments.reduce((sum, s) => sum + s.amount_minor, 0)
    : fallbackTotalMinor;

  const pieData = segments.length > 0
    ? segments.map((seg, i) => ({
        value: seg.share_percent,
        color: SEGMENT_COLORS[i % SEGMENT_COLORS.length],
      }))
    : [{ value: 100, color: colors.surfaceContainer }];

  const ariaLabel =
    segments.length > 0
      ? `Spending breakdown: ${segments.map((s) => `${s.category_name ?? s.category_id} ${s.share_percent}%`).join(", ")}`
      : `Spending breakdown: ${lifeOpsPulseCopy.formatInrMinor(totalMinor)} total`;

  return (
    <div
      className="relative shrink-0"
      style={{ width: DONUT_SIZE, height: DONUT_SIZE }}
      role="img"
      aria-label={ariaLabel}
    >
      <PieChart
        data={pieData}
        donut
        radius={DONUT_RADIUS}
        innerRadius={DONUT_INNER_RADIUS}
        innerCircleColor={colors.surfaceContainer}
        backgroundColor={colors.surfaceContainer}
        strokeWidth={0}
        startAngle={90}
        {...PULSE_PIE_PROPS}
      />
      <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center text-center">
        <span style={{ ...personalTypography.labelSm, fontSize: 10, opacity: 0.6, textTransform: "uppercase" }}>
          {lifeOpsPulseCopy.financialTotalLabel}
        </span>
        <span className="text-sm font-black">{formatCompact(totalMinor)}</span>
      </div>
    </div>
  );
}

function formatCompact(minor: number): string {
  const rupees = minor / 100;
  if (rupees >= 1000) return `${(rupees / 1000).toFixed(1)}k`;
  return lifeOpsPulseCopy.formatInrMinor(minor);
}
