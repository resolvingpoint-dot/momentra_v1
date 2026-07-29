"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { personalTypography } from "@/components/personal/empty/shared/emptyStyles";
import { alignEmotionalSeries, toLineData } from "@/lib/personal/life/lifeChartData";
import { emotionalSeriesColors, personalLifeCopy } from "@/lib/personal/life/personalLifeCopy";
import { LIFE_TREND_CHART_HEIGHT, PULSE_LINE_PROPS } from "@/lib/personal/life/lifeChartTheme";
import type { PersonalLifeTrendPoint } from "@/lib/api/personal";
import { LineChart } from "react-gifted-charts";
import { LifeCard } from "./LifeCard";
import { LifeSectionLabel } from "./LifeSectionLabel";

type EmotionalTrendChartProps = {
  windowLabel: string;
  series: PersonalLifeTrendPoint[];
  isSparse?: boolean;
  onQuickAdd?: (eventType: string) => void;
};

function SeriesLegend() {
  const { colors } = useThemeTokens();
  const seriesColors = emotionalSeriesColors(colors);
  const items = [
    { key: "connection", label: personalLifeCopy.series.connection, color: seriesColors.connection },
    { key: "joy", label: personalLifeCopy.series.joy, color: seriesColors.joy },
    { key: "stress", label: personalLifeCopy.series.stress, color: seriesColors.stress },
    { key: "fulfillment", label: personalLifeCopy.series.fulfillment, color: seriesColors.fulfillment },
  ] as const;

  return (
    <div className="mt-4 grid grid-cols-2 gap-2">
      {items.map((item) => (
        <span
          key={item.key}
          className="flex items-center gap-1.5"
          style={{ ...personalTypography.microLabel, opacity: 0.8, color: colors.textSecondary }}
        >
          <span className="size-2 rounded-full" style={{ background: item.color }} />
          {item.label}
        </span>
      ))}
    </div>
  );
}

export function EmotionalTrendChart({
  windowLabel,
  series,
  isSparse = false,
  onQuickAdd,
}: EmotionalTrendChartProps) {
  const { colors } = useThemeTokens();
  const { connection, joy, stress, fulfillment, count } = alignEmotionalSeries(series);
  const spacing = count > 1 ? Math.max(4, Math.floor(280 / (count - 1))) : 8;
  const seriesColors = emotionalSeriesColors(colors);

  return (
    <LifeCard>
      <div className="mb-4 flex items-center justify-between gap-2">
        <LifeSectionLabel explainerId="LIFE-004">{personalLifeCopy.sections.emotionalTrend}</LifeSectionLabel>
        <span style={{ ...personalTypography.microLabel, opacity: 0.5, color: colors.textSecondary }}>
          {windowLabel}
        </span>
      </div>
      {isSparse ? (
        <div className="space-y-3">
          <p style={{ ...personalTypography.labelSm, fontWeight: 600, color: colors.textPrimary }}>
            {personalLifeCopy.emotionalTrendSparseTitle}
          </p>
          <p style={{ ...personalTypography.labelSm, opacity: 0.85, color: colors.textSecondary }}>
            {personalLifeCopy.emotionalTrendSparseBody}
          </p>
          <button
            type="button"
            onClick={() => onQuickAdd?.("REFLECTION")}
            className="rounded-xl px-4 py-2"
            style={{
              ...personalTypography.labelSm,
              fontWeight: 700,
              background: colors.brandPrimary,
              color: colors.brandOnPrimary,
            }}
          >
            {personalLifeCopy.sparseCta}
          </button>
        </div>
      ) : (
        <>
          <div className="relative w-full pointer-events-none" style={{ height: LIFE_TREND_CHART_HEIGHT }}>
            {count > 0 ? (
              <LineChart
                data={toLineData(connection)}
                data2={toLineData(joy)}
                data3={toLineData(stress)}
                data4={toLineData(fulfillment)}
                height={LIFE_TREND_CHART_HEIGHT}
                spacing={spacing}
                initialSpacing={0}
                endSpacing={0}
                thickness={2}
                thickness1={2}
                thickness2={2}
                thickness3={2}
                thickness4={2}
                color1={seriesColors.connection}
                color2={seriesColors.joy}
                color3={seriesColors.stress}
                color4={seriesColors.fulfillment}
                curved
                {...PULSE_LINE_PROPS}
                pointerConfig={undefined}
              />
            ) : null}
          </div>
          {count > 0 ? (
            <div className="mt-2 flex justify-between px-1">
              {series.map((pt) => (
                <span
                  key={pt.week_label}
                  style={{ ...personalTypography.microLabel, fontSize: 8, opacity: 0.4, color: colors.textSecondary }}
                >
                  {pt.week_label}
                </span>
              ))}
            </div>
          ) : null}
          <SeriesLegend />
        </>
      )}
    </LifeCard>
  );
}
