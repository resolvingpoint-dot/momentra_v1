"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { personalTypography } from "@/components/personal/empty/shared/emptyStyles";
import { relationshipsPulseCopy } from "@/lib/personal/emotional_security/pulse/relationshipsPulseCopy";
import {
  alignSeriesValues,
  toTrendLineData,
  trendPointCount,
} from "@/lib/personal/life_operations/pulse/pulseChartData";
import { lifeOpsPulseCopy } from "@/lib/personal/life_operations/pulse/lifeOpsPulseCopy";
import { PULSE_LINE_PROPS } from "@/lib/personal/life_operations/pulse/pulseChartTheme";
import { LineChart } from "react-gifted-charts";

type Point = { date: string; value: number };

type RelationshipsTrendLineChartProps = {
  trust: Point[];
  connection: Point[];
};

function TrendLegend() {
  const { colors } = useThemeTokens();
  return (
    <div className="flex gap-4">
      <span className="flex items-center gap-2 text-[10px] font-bold">
        <span className="size-2.5 rounded-full" style={{ background: colors.textSecondary }} />
        {relationshipsPulseCopy.trendsTrustLegend}
      </span>
      <span className="flex items-center gap-2 text-[10px] font-bold">
        <span
          className="size-2.5 rounded-full"
          style={{ background: colors.brandPrimary, boxShadow: `0 0 8px ${colors.brandPrimary}cc` }}
        />
        {relationshipsPulseCopy.trendsConnLegend}
      </span>
    </div>
  );
}

function normalizeTrendSeries(series: Point[] | undefined): Point[] {
  if (!Array.isArray(series)) return [];
  return series.map((point) => ({
    date: typeof point?.date === "string" ? point.date : "",
    value: typeof point?.value === "number" && Number.isFinite(point.value) ? point.value : 0,
  }));
}

export function RelationshipsTrendLineChart({ trust, connection }: RelationshipsTrendLineChartProps) {
  const { colors } = useThemeTokens();
  const trustSeries = normalizeTrendSeries(trust);
  const connectionSeries = normalizeTrendSeries(connection);
  const count = trendPointCount(trustSeries, connectionSeries);
  const showChart = count >= lifeOpsPulseCopy.trendsSparseThreshold && count >= 2;
  const { recovery: trustValues, pressure: connValues } = alignSeriesValues(trustSeries, connectionSeries);
  const spacing = count > 1 ? Math.max(4, Math.floor(320 / (count - 1))) : 8;
  const chartData = toTrendLineData(trustValues);
  const chartData2 = toTrendLineData(connValues);

  return (
    <div>
      <div className="mb-6">
        <TrendLegend />
      </div>
      {showChart && chartData.length >= 2 && chartData2.length >= 2 ? (
        <div>
          <div className="relative h-56 w-full pointer-events-none">
            <LineChart
              data={chartData}
              data2={chartData2}
              height={224}
              spacing={spacing}
              initialSpacing={0}
              endSpacing={0}
              thickness={3}
              thickness1={3}
              thickness2={3}
              color1={colors.textSecondary}
              color2={colors.brandPrimary}
              areaChart
              areaChart1
              startFillColor={colors.brandPrimary}
              endFillColor={colors.brandPrimary}
              startOpacity={0.15}
              endOpacity={0}
              strokeDashArray2={[6, 4]}
              curved
              {...PULSE_LINE_PROPS}
              isAnimated={false}
              pointerConfig={undefined}
            />
          </div>
          <div className="mt-4 flex justify-between px-2 text-[10px] font-bold uppercase tracking-widest opacity-40">
            <span>30d ago</span>
            <span>15d ago</span>
            <span>Now</span>
          </div>
        </div>
      ) : (
        <p style={{ ...personalTypography.bodyMd, opacity: 0.7 }}>Log more events to see trust and connection trends.</p>
      )}
    </div>
  );
}
