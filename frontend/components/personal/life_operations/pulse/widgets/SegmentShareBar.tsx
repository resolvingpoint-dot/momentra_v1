"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { PULSE_BAR_PROPS } from "@/lib/personal/life_operations/pulse/pulseChartTheme";
import { BarChart } from "react-gifted-charts";

type SegmentShareBarProps = {
  percent: number;
  color: string;
};

export function SegmentShareBar({ percent, color }: SegmentShareBarProps) {
  const { colors } = useThemeTokens();

  return (
    <BarChart
      data={[{ value: percent, frontColor: color }]}
      height={8}
      barWidth={8}
      backgroundColor={colors.surfaceHigh}
      frontColor={color}
      {...PULSE_BAR_PROPS}
    />
  );
}
