"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { PULSE_BAR_PROPS } from "@/lib/personal/life_operations/pulse/pulseChartTheme";
import { BarChart } from "react-gifted-charts";

type UtilizationBarProps = {
  percent: number;
};

export function UtilizationBar({ percent }: UtilizationBarProps) {
  const { colors } = useThemeTokens();

  return (
    <BarChart
      data={[{ value: percent, frontColor: colors.brandPrimary }]}
      height={6}
      barWidth={6}
      backgroundColor={colors.surfaceHigh}
      frontColor={colors.brandPrimary}
      {...PULSE_BAR_PROPS}
    />
  );
}
