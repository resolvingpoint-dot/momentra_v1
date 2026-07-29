"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { driverBarWidth } from "@/lib/personal/life_operations/pulse/pulseChartData";
import { PULSE_BAR_PROPS } from "@/lib/personal/life_operations/pulse/pulseChartTheme";
import { BarChart } from "react-gifted-charts";

type DriverImpactBarProps = {
  impact: number;
};

export function DriverImpactBar({ impact }: DriverImpactBarProps) {
  const { colors } = useThemeTokens();
  const width = driverBarWidth(impact);
  const barColor = impact < 0 ? colors.error : colors.brandPrimary;

  return (
    <div
      className="relative flex-1"
      style={{ display: "flex", justifyContent: impact < 0 ? "flex-end" : "flex-start" }}
    >
      <div className="w-full">
        <BarChart
          data={[{ value: width, frontColor: barColor }]}
          height={8}
          barWidth={8}
          backgroundColor={colors.surfaceHigh}
          frontColor={barColor}
          {...PULSE_BAR_PROPS}
        />
      </div>
    </div>
  );
}
