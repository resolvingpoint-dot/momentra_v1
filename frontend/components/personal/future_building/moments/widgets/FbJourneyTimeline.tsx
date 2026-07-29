"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { personalGlassCardStyle, personalTypography } from "@/components/personal/empty/shared/emptyStyles";
import type { PersonalLiveRecentActivityItem } from "@/lib/api/personal";
import { fbMomentsCopy } from "@/lib/personal/future_building/moments/fbMomentsCopy";
import { fbActivityCategoryLabel, fbTimelineImpactLine } from "@/lib/personal/future_building/pulse/fbPulseUtils";
import { FbSectionBadge } from "@/components/personal/future_building/moments/widgets/FbSectionBadge";
import { Flag, GraduationCap, Rocket, Star } from "lucide-react";
import { WidgetInfoButton } from "@/components/personal/shared/WidgetInfoButton";

const NODE_STYLES: Record<string, { bg: string; Icon: typeof GraduationCap }> = {
  LEARNING: { bg: "#4f46e5", Icon: GraduationCap },
  PROGRESS: { bg: "#7c3aed", Icon: Rocket },
  MILESTONE: { bg: "#eab308", Icon: Star },
  OPPORTUNITY: { bg: "#eab308", Icon: Star },
};

type Props = { items: PersonalLiveRecentActivityItem[] };

export function FbJourneyTimeline({ items }: Props) {
  const tokens = useThemeTokens();
  const { colors } = tokens;

  return (
    <section>
      <div className="mb-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <FbSectionBadge number={2} />
          <h2 style={{ ...personalTypography.labelSm, textTransform: "uppercase", letterSpacing: "0.12em", opacity: 0.6 }}>
            {fbMomentsCopy.journeyTimelineTitle}
          </h2>
          <WidgetInfoButton explainerId="MOMENT-004" momentTypeCode="FUTURE_BUILDING" />
        </div>
        <button type="button" style={{ fontSize: 12, color: colors.brandPrimary, background: "none", border: "none" }}>
          {fbMomentsCopy.viewAll}
        </button>
      </div>
      {items.length === 0 ? (
        <p style={{ ...personalTypography.bodyMd, opacity: 0.7 }}>Your journey timeline fills in as you log progress.</p>
      ) : (
        <div className="relative ml-3 space-y-4 border-l pb-3 pl-6" style={{ borderColor: "rgba(255,255,255,0.15)" }}>
          {items.map((item) => {
            const node = NODE_STYLES[item.event_type.toUpperCase()] ?? NODE_STYLES.LEARNING;
            const impact = fbTimelineImpactLine(item.event_type);
            const accent = impact.accent === "secondary" ? colors.brandSecondary : impact.accent === "tertiary" ? colors.brandTertiary : colors.brandPrimary;
            return (
              <div key={item.id} className="relative">
                <div
                  className="absolute -left-[45px] top-0 flex size-8 items-center justify-center rounded-full border-2 shadow-lg"
                  style={{ background: node.bg, borderColor: colors.background, boxShadow: `0 0 12px ${node.bg}66` }}
                >
                  <node.Icon size={14} color="#fff" />
                </div>
                <div style={{ ...personalGlassCardStyle(tokens), borderRadius: 16, padding: 12, borderColor: "rgba(255,255,255,0.06)" }}>
                  <p style={{ fontSize: 10, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.12em", color: accent, marginBottom: 2 }}>
                    {item.relative_time}
                  </p>
                  <h4 style={{ fontSize: 16, fontWeight: 700, color: colors.textPrimary }}>
                    {fbActivityCategoryLabel(item.event_type, item.category_label, item.amount_label)}
                  </h4>
                  <p style={{ fontSize: 12, marginTop: 4, color: colors.textSecondary }}>
                    Impact: <span style={{ color: accent, fontWeight: 600 }}>{impact.label}</span>
                  </p>
                  <p style={{ fontSize: 11, marginTop: 4, opacity: 0.7 }}>{item.detail_line}</p>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
}
