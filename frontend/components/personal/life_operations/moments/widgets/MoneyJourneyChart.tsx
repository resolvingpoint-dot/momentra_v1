"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { PersonalGlassGlowSection } from "@/components/personal/empty/shared/PersonalGlassGlowSection";
import { personalTypography } from "@/components/personal/empty/shared/emptyStyles";
import type { PersonalLifeOpsMoneyJourney } from "@/lib/api/personal";
import { lifeOpsMomentsCopy } from "@/lib/personal/life_operations/moments/lifeOpsMomentsCopy";
import { PULSE_LINE_PROPS } from "@/lib/personal/life_operations/pulse/pulseChartTheme";
import { SEGMENT_COLORS } from "@/lib/personal/life_operations/pulse/pulseIcons";
import { LineChart } from "react-gifted-charts";
import { WidgetInfoButton } from "@/components/personal/shared/WidgetInfoButton";

type MoneyJourneyChartProps = {
  money: PersonalLifeOpsMoneyJourney;
};

export function MoneyJourneyChart({ money }: MoneyJourneyChartProps) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  const series = (money.series ?? []).slice(0, 4);
  const highestMonth = {
    label: money.highest_month?.label ?? "—",
    amount_minor: money.highest_month?.amount_minor ?? 0,
  };
  const lowestMonth = {
    label: money.lowest_month?.label ?? "—",
    amount_minor: money.lowest_month?.amount_minor ?? 0,
  };
  const monthLabels = series[0]?.points.map((p) => p.date) ?? [];

  const toLineData = (values: number[]) =>
    values.map((v) => ({ value: Math.max(0, v / 100), dataPointText: "" }));

  const seriesValues = series.map((s) => s.points.map((p) => p.value_minor));
  const maxVal = Math.max(1, ...seriesValues.flat());

  const chartProps: Record<string, unknown> = {
    ...PULSE_LINE_PROPS,
    height: 200,
    spacing: monthLabels.length > 1 ? Math.max(24, Math.floor(280 / (monthLabels.length - 1))) : 40,
    initialSpacing: 8,
    endSpacing: 8,
    thickness: 2.5,
    curved: true,
    hideRules: false,
    rulesColor: `${colors.textSecondary}22`,
    yAxisColor: "transparent",
    xAxisColor: `${colors.textSecondary}33`,
    yAxisTextStyle: { color: colors.textSecondary, fontSize: 9 },
    xAxisLabelTextStyle: { color: colors.textSecondary, fontSize: 9 },
    noOfSections: 4,
    maxValue: maxVal / 100,
  };

  if (series[0]) chartProps.data = toLineData(seriesValues[0]);
  if (series[1]) {
    chartProps.data2 = toLineData(seriesValues[1]);
    chartProps.color2 = SEGMENT_COLORS[1];
  }
  if (series[2]) {
    chartProps.data3 = toLineData(seriesValues[2]);
    chartProps.color3 = SEGMENT_COLORS[2];
  }
  if (series[3]) {
    chartProps.data4 = toLineData(seriesValues[3]);
    chartProps.color4 = SEGMENT_COLORS[3];
  }
  chartProps.color1 = SEGMENT_COLORS[0];

  return (
    <section>
      <div className="mb-2 flex items-end justify-between gap-2">
        <div>
          <div className="flex items-center gap-0.5">
            <h3 style={{ ...personalTypography.sectionHeader, color: colors.textPrimary }}>
              {money.title}
            </h3>
            <WidgetInfoButton explainerId="MOMENT-005" momentTypeCode="LIFE_OPERATIONS" />
          </div>
          <p className="text-xs opacity-60">{money.period_label}</p>
        </div>
      </div>
      <PersonalGlassGlowSection tokens={tokens} cornerRadius={20} innerStyle={{ padding: 16 }}>
        {series.length === 0 ? (
          <p style={{ ...personalTypography.bodyMd, color: colors.textSecondary, opacity: 0.7 }}>
            {lifeOpsMomentsCopy.moneyJourneyEmpty}
          </p>
        ) : (
          <>
            <div className="mb-2 flex flex-wrap gap-2">
              {series.map((s, i) => (
                <span key={s.category_id} className="flex items-center gap-2 text-[10px] font-bold">
                  <span className="size-2.5 rounded-full" style={{ background: SEGMENT_COLORS[i % SEGMENT_COLORS.length] }} />
                  {s.category_name}
                </span>
              ))}
            </div>
            <div className="pointer-events-none">
              <LineChart {...chartProps} isAnimated={false} pointerConfig={undefined} />
            </div>
            <div className="mt-2 flex justify-between px-1 text-[10px] font-bold uppercase tracking-widest opacity-40">
              {monthLabels.map((m) => (
                <span key={m}>{m}</span>
              ))}
            </div>
          </>
        )}
        <div className="mt-4 grid grid-cols-1 gap-2 border-t pt-3 sm:grid-cols-3" style={{ borderColor: `${colors.textSecondary}22` }}>
          <div>
            <p className="text-[10px] uppercase opacity-50">{lifeOpsMomentsCopy.totalSpendLabel}</p>
            <p className="font-bold">{lifeOpsMomentsCopy.formatInrFromMinor(money.total_spend_minor)}</p>
          </div>
          <div>
            <p className="text-[10px] uppercase opacity-50">{lifeOpsMomentsCopy.highestMonthLabel}</p>
            <p className="font-bold">
              {highestMonth.label} · {lifeOpsMomentsCopy.formatInrFromMinor(highestMonth.amount_minor)}
            </p>
          </div>
          <div>
            <p className="text-[10px] uppercase opacity-50">{lifeOpsMomentsCopy.lowestMonthLabel}</p>
            <p className="font-bold">
              {lowestMonth.label} · {lifeOpsMomentsCopy.formatInrFromMinor(lowestMonth.amount_minor)}
            </p>
          </div>
        </div>
      </PersonalGlassGlowSection>
    </section>
  );
}
