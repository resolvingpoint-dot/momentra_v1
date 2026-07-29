"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { personalTypography } from "@/components/personal/empty/shared/emptyStyles";
import { PULSE_BAR_PROPS } from "@/lib/personal/life/lifeChartTheme";
import { BarChart } from "react-gifted-charts";

type LifeHappinessBarProps = {
  label: string;
  fraction: number;
  variant: "high" | "low";
};

export function LifeHappinessBar({ label, fraction, variant }: LifeHappinessBarProps) {
  const { colors } = useThemeTokens();
  const width = Math.round(Math.min(1, Math.max(0, fraction)) * 100);
  const barColor = variant === "high" ? colors.brandTertiary : colors.error;

  return (
    <div className="mt-2 flex items-center justify-between gap-3">
      <span style={{ ...personalTypography.microLabel, flex: 1, color: colors.textSecondary }}>{label}</span>
      <div className="w-24">
        <BarChart
          data={[{ value: width, frontColor: barColor }]}
          height={6}
          barWidth={6}
          backgroundColor={colors.surfaceHigh}
          frontColor={barColor}
          {...PULSE_BAR_PROPS}
        />
      </div>
    </div>
  );
}
