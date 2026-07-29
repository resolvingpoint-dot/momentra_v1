"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { personalGlassCardStyle } from "@/components/personal/empty/shared/emptyStyles";
import { LifestyleSectionBadge } from "@/components/personal/lifestyle/shared/LifestyleSectionBadge";
import type { PersonalLifestyleMoneyJourney } from "@/lib/api/personal";
import { lifestyleMomentsCopy } from "@/lib/personal/lifestyle/moments/lifestyleMomentsCopy";
import { PULSE_LINE_PROPS } from "@/lib/personal/life_operations/pulse/pulseChartTheme";
import { LineChart } from "react-gifted-charts";

type Props = { money: PersonalLifestyleMoneyJourney };

const SERIES_COLORS = ["#8b5cf6", "#3b82f6", "#ec4899"];

const toLineData = (values: number[]) =>
  values.map((v) => ({ value: Math.max(0, v / 100) }));

export function LifestyleSpendJourney({ money }: Props) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  const series = money.series.slice(0, 3);
  const monthLabels = series[0]?.points.map((p) => p.date) ?? [];

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
    color1: SERIES_COLORS[0],
  };

  if (series[0]) chartProps.data = toLineData(seriesValues[0]);
  if (series[1]) {
    chartProps.data2 = toLineData(seriesValues[1]);
    chartProps.color2 = SERIES_COLORS[1];
  }
  if (series[2]) {
    chartProps.data3 = toLineData(seriesValues[2]);
    chartProps.color3 = SERIES_COLORS[2];
  }

  return (
    <section style={{ ...personalGlassCardStyle(tokens), borderRadius: 20, padding: 16 }}>
      <LifestyleSectionBadge index={3} label="Money Journey" explainerId="MOMENT-005" />

      <div className="mb-6 grid grid-cols-1 gap-2">
        <div className="flex items-end justify-between">
          <div>
            <span className="text-[10px] font-bold uppercase tracking-widest opacity-60">Total Lifestyle Spend</span>
            <div className="text-2xl font-bold">{lifestyleMomentsCopy.formatInrMinor(money.total_spend_minor)}</div>
          </div>
          <div className="text-right">
            <span className="text-[10px] font-bold uppercase tracking-widest opacity-60">Highest Area</span>
            <div className="text-sm font-semibold" style={{ color: colors.brandSecondary }}>
              {money.highest_area_label} • {lifestyleMomentsCopy.formatInrMinor(money.highest_area_amount_minor)}
            </div>
          </div>
        </div>
        <div
          className="flex items-center justify-between rounded-xl border p-2"
          style={{ background: "rgba(255,255,255,0.05)", borderColor: "rgba(255,255,255,0.05)" }}
        >
          <span className="text-[10px] font-bold uppercase opacity-60">Lowest Return</span>
          <span className="text-xs font-bold">
            {money.lowest_return_label} • {lifestyleMomentsCopy.formatInrMinor(money.lowest_return_amount_minor)}
          </span>
        </div>
      </div>

      {series.length > 0 && (
        <div className="mb-2 flex flex-wrap gap-2">
          {series.map((s, i) => (
            <span key={s.category_id} className="flex items-center gap-2 text-[10px] font-bold">
              <span
                className="size-2.5 rounded-full"
                style={{ background: SERIES_COLORS[i % SERIES_COLORS.length] }}
              />
              {s.category_name}
            </span>
          ))}
        </div>
      )}

      <div className="pointer-events-none">
        <LineChart {...chartProps} pointerConfig={undefined} />
      </div>
      <div className="mt-2 flex justify-between px-1 text-[10px] font-bold uppercase tracking-widest opacity-40">
        {monthLabels.map((m) => (
          <span key={m}>{m}</span>
        ))}
      </div>
    </section>
  );
}
