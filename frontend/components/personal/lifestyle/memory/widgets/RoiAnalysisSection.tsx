"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { personalGlassCardStyle } from "@/components/personal/empty/shared/emptyStyles";
import { LifestyleSectionBadge } from "@/components/personal/lifestyle/shared/LifestyleSectionBadge";
import type { PersonalLifestyleRoiAnalysis } from "@/lib/api/personal";
import { lifestyleMemoryCopy } from "@/lib/personal/lifestyle/memory/lifestyleMemoryCopy";
import { TrendingUp } from "lucide-react";

type Props = { roi?: PersonalLifestyleRoiAnalysis | null; momentTypeCode?: string | null };

const BAR_COLORS = ["primary", "secondary", "tertiary"] as const;

export function RoiAnalysisSection({ roi, momentTypeCode = "LIFESTYLE" }: Props) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  if (!roi) return null;
  const barBg = [colors.brandPrimary, colors.brandSecondary, colors.tertiary];

  return (
    <section style={{ ...personalGlassCardStyle(tokens), borderRadius: 16, padding: 16 }}>
      <LifestyleSectionBadge index={5} label={lifestyleMemoryCopy.sectionLabels.roiAnalysis} explainerId="MEMORY-ROI" momentTypeCode={momentTypeCode} />
      <div className="flex items-center justify-between">
        <div>
          <h4 className="text-lg font-semibold">{roi.title}</h4>
          <p className="text-xs opacity-60">{roi.roi_label}</p>
        </div>
        <div className="flex items-center gap-1" style={{ color: colors.brandPrimary }}>
          <TrendingUp size={14} />
          <span className="text-xs font-bold">Peak Return</span>
        </div>
      </div>
      <div className="mt-3 flex h-28 items-end gap-2">
        {roi.bars.map((bar, i) => (
          <div key={bar.behavior_code} className="group relative flex-1">
            <div
              className="rounded-t-lg border-t"
              style={{
                height: `${Math.max(20, bar.height_fraction * 100)}%`,
                background: `${barBg[i % barBg.length]}66`,
                borderColor: `${barBg[i % barBg.length]}66`,
              }}
            />
            <div className="mt-2 text-center text-[8px] font-bold uppercase tracking-tighter opacity-60">{bar.label}</div>
          </div>
        ))}
      </div>
    </section>
  );
}
