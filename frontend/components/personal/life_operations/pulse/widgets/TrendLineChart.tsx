"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { personalTypography } from "@/components/personal/empty/shared/emptyStyles";
import { lifeOpsPulseCopy } from "@/lib/personal/life_operations/pulse/lifeOpsPulseCopy";
import {
  alignSeriesValues,
  toTrendLineData,
  trendPointCount,
} from "@/lib/personal/life_operations/pulse/pulseChartData";
import { PULSE_LINE_PROPS } from "@/lib/personal/life_operations/pulse/pulseChartTheme";
import { LineChart } from "react-gifted-charts";

type Point = { date: string; value: number };

type TrendLineChartProps = {
  recovery: Point[];
  pressure: Point[];
};

function TrendLegend() {
  const { colors } = useThemeTokens();
  return (
    <div className="flex gap-4">
      <span className="flex items-center gap-2 text-[10px] font-bold">
        <span
          className="size-2.5 rounded-full"
          style={{ background: colors.brandPrimary, boxShadow: `0 0 8px ${colors.brandPrimary}cc` }}
        />
        {lifeOpsPulseCopy.trendsRecoveryLegend}
      </span>
      <span className="flex items-center gap-2 text-[10px] font-bold">
        <span
          className="size-2.5 rounded-full"
          style={{ background: colors.error, boxShadow: `0 0 8px ${colors.error}cc` }}
        />
        {lifeOpsPulseCopy.trendsPressureLegend}
      </span>
    </div>
  );
}

function SmoothTrendChart({ recovery, pressure }: TrendLineChartProps) {
  const { colors } = useThemeTokens();
  const { recovery: recoveryValues, pressure: pressureValues, count } = alignSeriesValues(recovery, pressure);
  const spacing = count > 1 ? Math.max(4, Math.floor(320 / (count - 1))) : 8;

  return (
    <div>
      <div className="relative h-56 w-full pointer-events-none">
        <LineChart
          data={toTrendLineData(recoveryValues)}
          data2={toTrendLineData(pressureValues)}
          height={224}
          spacing={spacing}
          initialSpacing={0}
          endSpacing={0}
          thickness={3}
          thickness1={3}
          thickness2={3}
          color1={colors.brandPrimary}
          color2={colors.error}
          areaChart
          areaChart1
          startFillColor={colors.brandPrimary}
          endFillColor={colors.brandPrimary}
          startOpacity={0.2}
          endOpacity={0}
          strokeDashArray2={[6, 4]}
          curved
          {...PULSE_LINE_PROPS}
          pointerConfig={undefined}
        />
      </div>
      <div className="mt-4 flex justify-between px-2 text-[10px] font-bold uppercase tracking-widest opacity-40">
        <span>{lifeOpsPulseCopy.trendsAxis30dAgo}</span>
        <span>{lifeOpsPulseCopy.trendsAxis15dAgo}</span>
        <span>{lifeOpsPulseCopy.trendsAxisNow}</span>
      </div>
    </div>
  );
}

function TrendDeltaCards({ recovery, pressure }: TrendLineChartProps) {
  const { colors } = useThemeTokens();

  function row(
    label: string,
    values: number[],
    accent: string,
  ) {
    if (values.length === 0) {
      return (
        <div className="flex items-center justify-between rounded-xl border p-3" style={{ borderColor: "rgba(255,255,255,0.08)" }}>
          <span style={{ ...personalTypography.labelSm, fontWeight: 700 }}>{label}</span>
          <span style={{ ...personalTypography.labelSm, opacity: 0.5 }}>—</span>
        </div>
      );
    }
    const start = values[0];
    const end = values[values.length - 1];
    const delta = end - start;
    return (
      <div className="flex items-center justify-between rounded-xl border p-3" style={{ borderColor: "rgba(255,255,255,0.08)" }}>
        <span style={{ ...personalTypography.labelSm, fontWeight: 700 }}>{label}</span>
        <div className="text-right">
          <p style={{ ...personalTypography.labelSm, fontWeight: 700 }}>{lifeOpsPulseCopy.trendsDeltaLabel(start, end)}</p>
          <p style={{ fontSize: 11, fontWeight: 700, color: accent }}>{lifeOpsPulseCopy.trendsDeltaSigned(delta)}</p>
        </div>
      </div>
    );
  }

  const { recovery: rv, pressure: pv } = alignSeriesValues(recovery, pressure);

  return (
    <div className="space-y-3">
      <p style={{ ...personalTypography.bodyMd, color: colors.textSecondary, opacity: 0.7, fontSize: 13 }}>
        {lifeOpsPulseCopy.trendsSparseEmpty}
      </p>
      {row(lifeOpsPulseCopy.trendsRecoveryLegend, rv, colors.brandPrimary)}
      {row(lifeOpsPulseCopy.trendsPressureLegend, pv, colors.error)}
    </div>
  );
}

export function TrendLineChart({ recovery, pressure }: TrendLineChartProps) {
  const count = trendPointCount(recovery, pressure);
  const showChart = count >= lifeOpsPulseCopy.trendsSparseThreshold;

  return (
    <div role="img" aria-label="Recovery and pressure trends over time">
      <div className="mb-6">
        <TrendLegend />
      </div>
      {showChart ? <SmoothTrendChart recovery={recovery} pressure={pressure} /> : <TrendDeltaCards recovery={recovery} pressure={pressure} />}
    </div>
  );
}
