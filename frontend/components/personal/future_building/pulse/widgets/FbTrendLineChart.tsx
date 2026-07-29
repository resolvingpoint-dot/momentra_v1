"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { personalTypography } from "@/components/personal/empty/shared/emptyStyles";
import { fbPulseCopy } from "@/lib/personal/future_building/pulse/fbPulseCopy";
import { toTrendLineData } from "@/lib/personal/life_operations/pulse/pulseChartData";
import { PULSE_LINE_PROPS } from "@/lib/personal/life_operations/pulse/pulseChartTheme";
import { LineChart } from "react-gifted-charts";

type Point = { date: string; value: number };

type FbTrendLineChartProps = {
  learning?: Point[] | null;
  execution?: Point[] | null;
  progress?: Point[] | null;
};

function normalizeTrendSeries(series: Point[] | null | undefined): Point[] {
  if (!Array.isArray(series)) return [];
  return series.map((point) => ({
    date: typeof point?.date === "string" ? point.date : "",
    value: typeof point?.value === "number" && Number.isFinite(point.value) ? point.value : 0,
  }));
}

function alignThreeSeries(
  a: Point[],
  b: Point[],
  c: Point[],
): { a: number[]; b: number[]; c: number[]; count: number } {
  const count = Math.max(a.length, b.length, c.length);
  const pad = (src: Point[]) => {
    const values = src.map((p) => p.value);
    while (values.length < count) {
      values.push(values[values.length - 1] ?? 0);
    }
    return values;
  };
  return { a: pad(a), b: pad(b), c: pad(c), count };
}

export function FbTrendLineChart({ learning, execution, progress }: FbTrendLineChartProps) {
  const { colors } = useThemeTokens();
  const learningSeries = normalizeTrendSeries(learning);
  const executionSeries = normalizeTrendSeries(execution);
  const progressSeries = normalizeTrendSeries(progress);
  const { a: learningValues, b: executionValues, c: progressValues, count } = alignThreeSeries(
    learningSeries,
    executionSeries,
    progressSeries,
  );
  const showChart = count >= Math.max(2, fbPulseCopy.trendsSparseThreshold);
  const spacing = count > 1 ? Math.max(4, Math.floor(320 / (count - 1))) : 8;
  const data = toTrendLineData(learningValues);
  const data2 = toTrendLineData(executionValues);
  const data3 = toTrendLineData(progressValues);

  return (
    <div role="img" aria-label="Learning, execution, and progress trends">
      <div className="mb-4 flex flex-wrap gap-3 text-[9px] font-bold uppercase tracking-widest opacity-70">
        <span className="flex items-center gap-1">
          <span className="h-0.5 w-3" style={{ background: colors.brandPrimary }} />
          {fbPulseCopy.trendsLearningLegend}
        </span>
        <span className="flex items-center gap-1">
          <span className="h-0.5 w-3 border border-dashed" style={{ borderColor: colors.brandSecondary }} />
          {fbPulseCopy.trendsExecutionLegend}
        </span>
        <span className="flex items-center gap-1">
          <span className="h-0.5 w-3" style={{ background: colors.brandTertiary }} />
          {fbPulseCopy.trendsProgressLegend}
        </span>
      </div>
      {showChart && data.length >= 2 && data2.length >= 2 && data3.length >= 2 ? (
        <div className="relative h-48 w-full pointer-events-none">
          <LineChart
            data={data}
            data2={data2}
            data3={data3}
            height={192}
            spacing={spacing}
            initialSpacing={0}
            endSpacing={0}
            thickness={2}
            thickness1={2}
            thickness2={2}
            thickness3={2}
            color1={colors.brandPrimary}
            color2={colors.brandSecondary}
            color3={colors.brandTertiary}
            strokeDashArray2={[4, 3]}
            curved
            {...PULSE_LINE_PROPS}
            isAnimated={false}
            pointerConfig={undefined}
          />
        </div>
      ) : (
        <p style={{ ...personalTypography.bodyMd, opacity: 0.7 }}>
          Log more building activity to see learning, execution, and progress trends.
        </p>
      )}
    </div>
  );
}
