"use client";

import Image from "next/image";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { personalGlassCardStyle } from "@/components/personal/empty/shared/emptyStyles";
import { LifestyleSectionBadge } from "@/components/personal/lifestyle/shared/LifestyleSectionBadge";
import type { PersonalLifestyleTimelineItem } from "@/lib/api/personal";
import { lifestyleMomentsCopy } from "@/lib/personal/lifestyle/moments/lifestyleMomentsCopy";

type Props = { items: PersonalLifestyleTimelineItem[] };

const IMPACT_COLORS: Record<string, string> = {
  positive: "#10b981",
  vitality: "#eab308",
  fulfillment: "#10b981",
  neutral: "#94a3b8",
};

export function LifestyleJourneyTimeline({ items }: Props) {
  const tokens = useThemeTokens();
  const { colors } = tokens;

  let lastGroup = "";

  return (
    <section>
      <div className="mb-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <LifestyleSectionBadge index={2} label="Journey Timeline" explainerId="MOMENT-004" />
        </div>
        <button type="button" className="text-xs" style={{ color: "#60a5fa", background: "none", border: "none" }}>
          View all
        </button>
      </div>
      {items.length === 0 ? (
        <p className="text-sm opacity-70">{lifestyleMomentsCopy.journeyTimelineEmpty}</p>
      ) : (
        <div className="space-y-2">
          {items.map((item) => {
            const showGroup = item.group_label !== lastGroup;
            lastGroup = item.group_label;
            const impactColor = IMPACT_COLORS[item.impact_tone ?? "neutral"] ?? colors.textSecondary;
            return (
              <div key={item.id} className="mb-3">
                {showGroup ? (
                  <span
                    className="text-[10px] font-bold uppercase tracking-widest"
                    style={{ color: item.group_label === "Today" ? colors.brandSecondary : colors.textSecondary }}
                  >
                    {item.group_label}
                  </span>
                ) : null}
                <div
                  className="mt-2 flex items-center gap-3"
                  style={{ ...personalGlassCardStyle(tokens), borderRadius: 16, padding: 12, opacity: item.group_label === "Today" ? 1 : 0.9 }}
                >
                  <div className="relative size-16 shrink-0 overflow-hidden rounded-xl" style={{ background: colors.surfaceContainer }}>
                    {item.thumbnail_url ? (
                      <Image src={item.thumbnail_url} alt="" fill className="object-cover" unoptimized />
                    ) : null}
                  </div>
                  <div className="min-w-0">
                    <h4 className="font-semibold">{item.title}</h4>
                    {item.impact_line ? (
                      <p className="mt-1 text-xs" style={{ color: impactColor }}>
                        {item.impact_line}
                      </p>
                    ) : null}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
}
