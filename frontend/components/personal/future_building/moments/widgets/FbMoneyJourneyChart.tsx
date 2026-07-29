"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { personalGlassCardStyle, personalTypography } from "@/components/personal/empty/shared/emptyStyles";
import type { PersonalFutureBuildingMoneyJourney } from "@/lib/api/personalDomainTypes";
import { fbMomentsCopy } from "@/lib/personal/future_building/moments/fbMomentsCopy";
import { FbSectionBadge } from "@/components/personal/future_building/moments/widgets/FbSectionBadge";
import { PULSE_LINE_PROPS } from "@/lib/personal/life_operations/pulse/pulseChartTheme";
import { LineChart } from "react-gifted-charts";
import { WidgetInfoButton } from "@/components/personal/shared/WidgetInfoButton";

type FbMoneyJourneyChartProps = {
  money: PersonalFutureBuildingMoneyJourney;
};

export function FbMoneyJourneyChart({ money }: FbMoneyJourneyChartProps) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  if (!money) return null;

  const totalMinor =
    money.total_invested_minor ??
    (money as { total_spend_minor?: number }).total_spend_minor ??
    0;
  const highestMonth = {
    label: money.highest_month?.label ?? "—",
    amount_minor: money.highest_month?.amount_minor ?? 0,
  };
  const highestArea = {
    label: money.highest_area?.label ?? "—",
    amount_minor: money.highest_area?.amount_minor ?? 0,
  };
  const primarySeries = money.series?.[0]?.points ?? [];
  const data = primarySeries.map((p) => ({ value: Math.max(1, p.value_minor / 10000) }));
  const data2 = (money.series?.[1]?.points ?? []).map((p) => ({ value: Math.max(1, p.value_minor / 10000) }));
  const data3 = (money.series?.[2]?.points ?? []).map((p) => ({ value: Math.max(1, p.value_minor / 10000) }));

  return (
    <section style={{ ...personalGlassCardStyle(tokens), borderRadius: 16, padding: 16 }}>
      <div className="mb-6 flex items-start justify-between">
        <div>
          <div className="mb-0.5 flex items-center gap-2">
            <FbSectionBadge number={3} />
            <h2 style={{ ...personalTypography.labelSm, textTransform: "uppercase", letterSpacing: "0.12em", opacity: 0.6 }}>
              {fbMomentsCopy.moneyJourneyTitle}
            </h2>
            <WidgetInfoButton explainerId="MOMENT-005" momentTypeCode="FUTURE_BUILDING" />
          </div>
          <h3 style={{ fontSize: 20, fontWeight: 700, color: colors.textPrimary }}>{money.title}</h3>
        </div>
        <p style={{ fontSize: 10, fontWeight: 700, textTransform: "uppercase", color: colors.textSecondary }}>{money.period_label}</p>
      </div>
      <div className="mb-6 grid grid-cols-1 gap-2">
        <div className="flex items-end justify-between border-b pb-3" style={{ borderColor: "rgba(255,255,255,0.1)" }}>
          <div>
            <p style={{ fontSize: 12, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.08em", color: colors.textSecondary }}>Total Invested</p>
            <p style={{ fontSize: 36, fontWeight: 900, marginTop: 4, color: colors.textPrimary }}>
              {fbMomentsCopy.formatInrMinor(totalMinor)}
            </p>
          </div>
          <div className="text-right">
            <p style={{ fontSize: 10, fontWeight: 700, textTransform: "uppercase", color: colors.textSecondary }}>Best Month</p>
            <p style={{ fontSize: 18, fontWeight: 700, color: "#4ade80" }}>
              {highestMonth.label}{" "}
              <span style={{ fontSize: 12 }}>{fbMomentsCopy.formatInrMinor(highestMonth.amount_minor)}</span>
            </p>
          </div>
        </div>
        <div className="flex items-center justify-between">
          <p style={{ fontSize: 12, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.08em", color: colors.textSecondary }}>Highest Area</p>
          <p style={{ fontSize: 18, fontWeight: 700, color: colors.brandPrimary }}>
            {highestArea.label}{" "}
            <span style={{ fontSize: 12, opacity: 0.6 }}>{fbMomentsCopy.formatInrMinor(highestArea.amount_minor)}</span>
          </p>
        </div>
      </div>
      <div className="pointer-events-none h-32">
        <LineChart
          data={data.length ? data : [{ value: 1 }]}
          data2={data2.length ? data2 : undefined}
          data3={data3.length ? data3 : undefined}
          height={128}
          spacing={data.length > 1 ? 48 : 8}
          color1={colors.brandPrimary}
          color2={colors.brandSecondary}
          color3="#ec4899"
          curved
          {...PULSE_LINE_PROPS}
          pointerConfig={undefined}
        />
      </div>
    </section>
  );
}
