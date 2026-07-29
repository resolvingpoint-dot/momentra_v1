"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { personalTypography } from "@/components/personal/empty/shared/emptyStyles";
import type { PersonalLifeOpsMoneyJourney } from "@/lib/api/personal";
import { WidgetInfoButton } from "@/components/personal/shared/WidgetInfoButton";
import {
  relationshipsMomentsAccent,
  relationshipsMomentsCopy,
} from "@/lib/personal/emotional_security/moments/relationshipsMomentsCopy";
import { PULSE_LINE_PROPS } from "@/lib/personal/life_operations/pulse/pulseChartTheme";
import { LineChart } from "react-gifted-charts";

type RelationshipMoneyJourneyChartProps = {
  money: PersonalLifeOpsMoneyJourney;
};

export function RelationshipMoneyJourneyChart({ money }: RelationshipMoneyJourneyChartProps) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  const series = money.series.slice(0, 3);
  const seriesValues = series.map((s) => s.points.map((p) => p.value_minor));
  const maxVal = Math.max(1, ...seriesValues.flat());
  const toLineData = (values: number[]) =>
    values.map((v) => ({ value: Math.max(0, v / 100), dataPointText: "" }));

  const chartProps: Record<string, unknown> = {
    ...PULSE_LINE_PROPS,
    height: 180,
    thickness: 2.5,
    curved: true,
    hideRules: false,
    rulesColor: `${colors.textSecondary}22`,
    yAxisColor: "transparent",
    xAxisColor: `${colors.textSecondary}33`,
    maxValue: maxVal / 100,
  };
  if (series[0]) {
    chartProps.data = toLineData(seriesValues[0]);
    chartProps.color1 = relationshipsMomentsCopy.moneySeriesColors[0];
  }
  if (series[1]) {
    chartProps.data2 = toLineData(seriesValues[1]);
    chartProps.color2 = relationshipsMomentsCopy.moneySeriesColors[1];
  }
  if (series[2]) {
    chartProps.data3 = toLineData(seriesValues[2]);
    chartProps.color3 = relationshipsMomentsCopy.moneySeriesColors[2];
  }

  const highestArea =
    series[0]?.category_name ??
    (money as { highest_area_label?: string }).highest_area_label ??
    "—";
  const highestMonthLabel = money.highest_month?.label ?? "—";

  return (
    <section
      style={{
        borderRadius: 20,
        padding: 16,
        background: relationshipsMomentsAccent.cardBg,
        border: "1px solid rgba(255,255,255,0.1)",
      }}
    >
      <div className="flex items-center gap-0.5">
        <h3 style={{ ...personalTypography.sectionHeader, color: colors.textPrimary }}>{money.title}</h3>
        <WidgetInfoButton explainerId="MOMENT-005" momentTypeCode="RELATIONSHIPS" />
      </div>
      <p className="text-xs opacity-60">{money.period_label}</p>
      {series.length === 0 ? (
        <p className="mt-3 text-sm opacity-70">{relationshipsMomentsCopy.moneyJourneyEmpty}</p>
      ) : (
        <>
          <div className="mb-2 mt-3 flex flex-wrap gap-2">
            {series.map((s, i) => (
              <span key={s.category_id} className="flex items-center gap-2 text-[10px] font-bold">
                <span
                  className="size-2.5 rounded-full"
                  style={{ background: relationshipsMomentsCopy.moneySeriesColors[i] }}
                />
                {s.category_name}
              </span>
            ))}
          </div>
          <div className="pointer-events-none">
            <LineChart {...chartProps} pointerConfig={undefined} />
          </div>
          <div className="mt-3 grid grid-cols-1 gap-2 text-center sm:grid-cols-3">
            <div>
              <p className="text-[9px] font-bold uppercase opacity-50">{relationshipsMomentsCopy.totalSpend}</p>
              <p className="text-sm font-bold">{relationshipsMomentsCopy.formatInrFull(money.total_spend_minor)}</p>
            </div>
            <div>
              <p className="text-[9px] font-bold uppercase opacity-50">{relationshipsMomentsCopy.highestArea}</p>
              <p className="text-sm font-bold">{highestArea}</p>
            </div>
            <div>
              <p className="text-[9px] font-bold uppercase opacity-50">{relationshipsMomentsCopy.bestMonth}</p>
              <p className="text-sm font-bold">{highestMonthLabel}</p>
            </div>
          </div>
        </>
      )}
    </section>
  );
}
