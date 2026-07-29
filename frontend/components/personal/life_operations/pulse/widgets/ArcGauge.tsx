"use client";

import { GAUGE_COLORS } from "@/lib/personal/life_operations/pulse/pulseIcons";
import { arcGaugePieData } from "@/lib/personal/life_operations/pulse/pulseChartData";
import { ARC_GAUGE_TRACK, PULSE_PIE_PROPS } from "@/lib/personal/life_operations/pulse/pulseChartTheme";
import { PieChart } from "react-gifted-charts";

type ArcGaugeProps = {
  gaugeId: string;
  percent: number;
  label: string;
  size?: number;
};

export function ArcGauge({ gaugeId, percent, label, size = 56 }: ArcGaugeProps) {
  const color = GAUGE_COLORS[gaugeId] ?? "#6c4ef2";
  const inner = (size - 6) / 2 - 3;
  const outer = size / 2 - 1.5;
  const pieData = arcGaugePieData(percent, color, ARC_GAUGE_TRACK);

  return (
    <div className="flex flex-col items-center gap-2" role="img" aria-label={`${label} gauge at ${percent} percent`}>
      <div className="relative" style={{ width: size, height: size }}>
        <PieChart
          data={pieData}
          donut
          radius={outer}
          innerRadius={inner}
          innerCircleColor={ARC_GAUGE_TRACK}
          backgroundColor={ARC_GAUGE_TRACK}
          strokeWidth={0}
          startAngle={90}
          {...PULSE_PIE_PROPS}
        />
        <div className="pointer-events-none absolute inset-0 flex items-center justify-center text-xs font-bold">{percent}</div>
      </div>
      <span className="text-[9px] font-bold uppercase opacity-60">{label}</span>
    </div>
  );
}
