"use client";

import { useMemo, useState } from "react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { personalTypography } from "@/components/personal/empty/shared/emptyStyles";
import {
  type AxisDonutSlice,
  type AxisId,
  type AxisScores,
  axisColorForId,
  axisDonutSlices,
} from "@/lib/personal/life_operations/pulse/axisDonutData";
import { lifeOpsPulseCopy } from "@/lib/personal/life_operations/pulse/lifeOpsPulseCopy";
import {
  HERO_DONUT_INNER_CIRCLE_COLOR,
  HERO_DONUT_INNER_RADIUS,
  HERO_DONUT_RADIUS,
  HERO_DONUT_SIZE,
  HERO_PIE_PROPS,
} from "@/lib/personal/life_operations/pulse/pulseChartTheme";
import { PieChart } from "react-gifted-charts";

type AxisHealthDonutProps = {
  opsIndex: number | null;
  axisScores: AxisScores;
  dataSufficient?: boolean;
};

function sliceOpacity(selectedId: AxisId | null, sliceId: AxisId): number {
  if (selectedId == null) return 0.85;
  return selectedId === sliceId ? 1 : 0.45;
}

export function AxisHealthDonut({
  opsIndex,
  axisScores,
  dataSufficient = true,
}: AxisHealthDonutProps) {
  const { colors } = useThemeTokens();
  const slices = useMemo(() => axisDonutSlices(axisScores), [axisScores]);
  const [selectedId, setSelectedId] = useState<AxisId | null>(null);

  const selectedSlice = slices.find((s) => s.id === selectedId) ?? null;
  const selectedIndex = selectedId ? slices.findIndex((s) => s.id === selectedId) : -1;

  const pieData = slices.map((slice) => ({
    value: slice.value,
    color: axisColorForId(slice.id, colors),
    opacity: dataSufficient ? sliceOpacity(selectedId, slice.id) : 0.45,
    onPress: () => setSelectedId((prev) => (prev === slice.id ? null : slice.id)),
  }));

  return (
    <div className="relative mx-auto flex flex-col items-center py-1">
      <div className="relative" style={{ width: HERO_DONUT_SIZE, height: HERO_DONUT_SIZE }}>
        <PieChart
          data={pieData}
          donut
          radius={HERO_DONUT_RADIUS}
          innerRadius={HERO_DONUT_INNER_RADIUS}
          innerCircleColor={HERO_DONUT_INNER_CIRCLE_COLOR}
          backgroundColor={HERO_DONUT_INNER_CIRCLE_COLOR}
          strokeWidth={0}
          startAngle={90}
          selectedIndex={selectedIndex >= 0 ? selectedIndex : undefined}
          {...HERO_PIE_PROPS}
        />
        <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center text-center">
          {selectedSlice && dataSufficient ? (
            <>
              <span style={{ ...personalTypography.labelSm, textTransform: "uppercase", opacity: 0.7, letterSpacing: "0.1em", fontSize: 10 }}>
                {selectedSlice.label}
              </span>
              <span
                style={{
                  fontSize: 32,
                  fontWeight: 900,
                  color: axisColorForId(selectedSlice.id, colors),
                  lineHeight: 1,
                }}
              >
                {selectedSlice.score}
              </span>
            </>
          ) : (
            <>
              <span style={{ fontSize: 40, fontWeight: 900, color: colors.textPrimary, lineHeight: 1 }}>
                {dataSufficient && opsIndex != null ? opsIndex : lifeOpsPulseCopy.dash}
              </span>
              <span style={{ ...personalTypography.labelSm, textTransform: "uppercase", opacity: 0.6, letterSpacing: "0.12em", fontSize: 10 }}>
                {lifeOpsPulseCopy.opsIndexLabel}
              </span>
            </>
          )}
        </div>
      </div>
      <AxisLegend
        slices={slices}
        selectedId={selectedId}
        dataSufficient={dataSufficient}
        onSelect={(id) => setSelectedId((prev) => (prev === id ? null : id))}
        colorForId={(id) => axisColorForId(id, colors)}
      />
    </div>
  );
}

function AxisLegend({
  slices,
  selectedId,
  dataSufficient,
  onSelect,
  colorForId,
}: {
  slices: AxisDonutSlice[];
  selectedId: AxisId | null;
  dataSufficient: boolean;
  onSelect: (id: AxisId) => void;
  colorForId: (id: AxisId) => string;
}) {
  return (
    <div className="mt-3 grid w-full max-w-sm grid-cols-4 gap-2 text-center text-[10px] font-bold uppercase tracking-tight">
      {slices.map((slice) => {
        const active = selectedId === slice.id;
        return (
          <button
            key={slice.id}
            type="button"
            onClick={() => onSelect(slice.id)}
            className="rounded-lg border border-transparent px-1 py-1.5 transition-colors"
            style={{
              opacity: selectedId == null || active ? 1 : 0.5,
              borderColor: active ? `${colorForId(slice.id)}66` : "transparent",
              background: active ? "rgba(255,255,255,0.06)" : "transparent",
            }}
          >
            {slice.label}
            <br />
            <span style={{ color: colorForId(slice.id) }}>
              {dataSufficient ? slice.score : lifeOpsPulseCopy.dash}
            </span>
          </button>
        );
      })}
    </div>
  );
}
