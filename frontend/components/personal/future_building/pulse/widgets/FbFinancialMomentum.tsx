"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { personalGlassCardStyle, personalTypography } from "@/components/personal/empty/shared/emptyStyles";
import { PersonalWidgetSectionHeader } from "@/components/personal/shared/WidgetInfoButton";
import { DonutChart } from "@/components/personal/life_operations/pulse/widgets/DonutChart";
import { SegmentShareBar } from "@/components/personal/life_operations/pulse/widgets/SegmentShareBar";
import type { PersonalFutureBuildingPulseMetrics } from "@/lib/api/personalDomainTypes";
import { fbPulseCopy } from "@/lib/personal/future_building/pulse/fbPulseCopy";
import { FB_SEGMENT_COLORS } from "@/lib/personal/future_building/pulse/fbPulseUtils";

const MOMENT_TYPE = "FUTURE_BUILDING";

type Props = {
  segments: PersonalFutureBuildingPulseMetrics["financial_segments"];
  fallbackTotalMinor: number;
};

export function FbFinancialMomentum({ segments, fallbackTotalMinor }: Props) {
  const tokens = useThemeTokens();
  const { colors } = tokens;

  return (
    <section style={{ ...personalGlassCardStyle(tokens), borderRadius: 20, padding: 16 }}>
      <PersonalWidgetSectionHeader title={fbPulseCopy.financialTitle} explainerId="PULSE-006" momentTypeCode={MOMENT_TYPE} className="mb-3" />
      <div className="flex gap-6">
        <DonutChart segments={segments} fallbackTotalMinor={fallbackTotalMinor} />
        <div className="min-w-0 flex-1 pt-2">
          {segments.length > 0 ? (
            segments.map((seg, i) => (
              <div key={seg.category_id} className="mb-3">
                <div className="flex justify-between text-[10px] font-bold">
                  <span style={{ opacity: 0.8 }}>{seg.category_name ?? "Investment"}</span>
                  <span>{fbPulseCopy.formatInrMinor(seg.amount_minor)}</span>
                </div>
                <SegmentShareBar percent={seg.share_percent} color={FB_SEGMENT_COLORS[i % FB_SEGMENT_COLORS.length]} />
              </div>
            ))
          ) : (
            <p style={{ ...personalTypography.bodyMd, opacity: 0.7 }}>{fbPulseCopy.financialEmptyHint}</p>
          )}
        </div>
      </div>
    </section>
  );
}
