"use client";

import { useMemo } from "react";
import { PieChart } from "react-gifted-charts";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { PersonalGlassGlowSection } from "@/components/personal/empty/shared/PersonalGlassGlowSection";
import { WidgetInfoButton } from "@/components/personal/shared/WidgetInfoButton";
import {
  memoryMicroLabelStyle,
  personalTypography,
} from "@/components/personal/empty/shared/emptyStyles";
import type { PersonalLifeOpsEmotionalDna } from "@/lib/api/personal";
import { lifeOpsMemoryCopy, type PersonalMemoryCopy } from "@/lib/personal/life_operations/memory/lifeOpsMemoryCopy";
import {
  HERO_DONUT_INNER_CIRCLE_COLOR,
  MEMORY_DONUT_INNER_RADIUS,
  MEMORY_DONUT_RADIUS,
  MEMORY_DONUT_SIZE,
  PULSE_PIE_PROPS,
} from "@/lib/personal/life_operations/pulse/pulseChartTheme";

type Props = {copy?: PersonalMemoryCopy;  dna: PersonalLifeOpsEmotionalDna; momentTypeCode?: string | null };

export function EmotionalDnaSection({ dna, copy, momentTypeCode = "LIFE_OPERATIONS" }: Props) {
  const tokens = useThemeTokens();
  const memoryCopy = copy ?? lifeOpsMemoryCopy;
  const { colors } = tokens;

  const pieData = useMemo(
    () =>
      dna.segments.map((seg) => ({
        value: seg.percent,
        color: memoryCopy.segmentColor(seg.color_token, colors),
      })),
    [dna.segments, colors],
  );

  return (
    <PersonalGlassGlowSection tokens={tokens} cornerRadius={16} innerStyle={{ padding: tokens.spacing.md }}>
      <div className="flex items-center gap-0.5">
        <p style={memoryMicroLabelStyle(tokens)}>{memoryCopy.sectionLabels.emotionalDna}</p>
        <WidgetInfoButton explainerId="MEMORY-007" momentTypeCode={momentTypeCode} />
      </div>
      <div className="mt-3 flex flex-col items-center">
        <div className="relative" style={{ width: MEMORY_DONUT_SIZE, height: MEMORY_DONUT_SIZE }}>
          <PieChart
            data={pieData}
            donut
            radius={MEMORY_DONUT_RADIUS}
            innerRadius={MEMORY_DONUT_INNER_RADIUS}
            innerCircleColor={HERO_DONUT_INNER_CIRCLE_COLOR}
            backgroundColor={HERO_DONUT_INNER_CIRCLE_COLOR}
            strokeWidth={0}
            startAngle={90}
            {...PULSE_PIE_PROPS}
          />
          <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
            <span style={{ ...personalTypography.labelSm, fontWeight: 700, color: colors.textPrimary }}>
              {dna.dominant_label}
            </span>
          </div>
        </div>
        <div className="mt-2 w-full space-y-1">
          {dna.segments.map((seg) => (
            <div key={seg.segment_id} className="flex justify-between" style={personalTypography.microLabel}>
              <span className="flex items-center gap-1" style={{ color: colors.textPrimary }}>
                <span
                  className="h-1.5 w-1.5 rounded-full"
                  style={{ background: memoryCopy.segmentColor(seg.color_token, colors) }}
                />
                {seg.label}
              </span>
              <span style={{ opacity: 0.6, color: colors.textSecondary }}>{seg.percent}%</span>
            </div>
          ))}
        </div>
      </div>
      <p style={{ ...personalTypography.microLabel, marginTop: tokens.spacing.md, opacity: 0.7, color: colors.textSecondary }}>
        {dna.insight_body}
      </p>
    </PersonalGlassGlowSection>
  );
}

