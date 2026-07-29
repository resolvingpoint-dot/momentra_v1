"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { personalGlassCardStyle, personalTypography } from "@/components/personal/empty/shared/emptyStyles";
import {
  PULSE_PIE_PROPS,
} from "@/lib/personal/life_operations/pulse/pulseChartTheme";
import { SEGMENT_COLORS } from "@/lib/personal/life_operations/pulse/pulseIcons";
import { colorIndexForSegmentId } from "@/components/personal/template/activity/activityBreakdown";
import { PieChart } from "react-gifted-charts";

const COMPACT_SIZE = 112;
const COMPACT_RADIUS = 48;
const COMPACT_INNER = 36;

export type ActivityBreakdownChartSegment = {
  id: string;
  label: string;
  value: number;
};

type ActivityBreakdownDonutProps = {
  title: string;
  segments: ActivityBreakdownChartSegment[];
  selectedId?: string;
  onSegmentPress?: (id: string) => void;
  centerLabel?: string;
  centerValue?: string;
};

export function ActivityBreakdownDonut({
  title,
  segments,
  selectedId,
  onSegmentPress,
  centerLabel = "Total",
  centerValue,
}: ActivityBreakdownDonutProps) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  const total = segments.reduce((sum, s) => sum + s.value, 0);
  const pieData =
    segments.length > 0
      ? segments.map((seg) => {
          const base = SEGMENT_COLORS[colorIndexForSegmentId(seg.id, SEGMENT_COLORS.length)];
          const isSelected = selectedId === seg.id;
          const dimOthers = Boolean(selectedId) && !isSelected;
          return {
            value: Math.max(seg.value, 0.0001),
            color: dimOthers ? `${base}99` : base,
            onPress: onSegmentPress ? () => onSegmentPress(seg.id) : undefined,
          };
        })
      : [{ value: 100, color: colors.surfaceContainer }];

  const displayCenter =
    centerValue ??
    (segments.length === 0 ? "—" : total >= 1000 ? `${(total / 1000).toFixed(1)}k` : String(Math.round(total)));

  const ariaLabel =
    segments.length > 0
      ? `${title}: ${segments.map((s) => `${s.label} ${s.value}`).join(", ")}`
      : `${title}: no data`;

  return (
    <div
      className="flex min-w-0 flex-1 flex-col items-center gap-2 rounded-2xl p-3"
      style={personalGlassCardStyle(tokens)}
    >
      <p
        style={{
          ...personalTypography.labelSm,
          fontSize: 10,
          fontWeight: 700,
          letterSpacing: "0.12em",
          textTransform: "uppercase",
          opacity: 0.55,
        }}
      >
        {title}
      </p>
      <div
        className="relative shrink-0"
        style={{ width: COMPACT_SIZE, height: COMPACT_SIZE }}
        role="img"
        aria-label={ariaLabel}
      >
        <PieChart
          data={pieData}
          donut
          radius={COMPACT_RADIUS}
          innerRadius={COMPACT_INNER}
          innerCircleColor={colors.surfaceContainer}
          backgroundColor={colors.surfaceContainer}
          strokeWidth={0}
          startAngle={90}
          {...PULSE_PIE_PROPS}
          focusOnPress={Boolean(onSegmentPress)}
          toggleFocusOnPress={Boolean(onSegmentPress)}
        />
        <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center text-center">
          <span style={{ fontSize: 9, fontWeight: 700, opacity: 0.55, textTransform: "uppercase" }}>
            {centerLabel}
          </span>
          <span className="text-xs font-black">{displayCenter}</span>
        </div>
      </div>
      {segments.length === 0 ? (
        <p style={{ fontSize: 11, opacity: 0.5 }}>No data</p>
      ) : (
        <ul className="m-0 flex max-h-16 w-full list-none flex-col gap-0.5 overflow-hidden p-0">
          {segments.slice(0, 3).map((seg) => (
            <li key={seg.id} className="truncate text-center" style={{ fontSize: 10, opacity: 0.65 }}>
              {seg.label}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
