"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import type { PersonalEmotionalSecurityJourneyTimelineItem } from "@/lib/api/personalDomainTypes";
import { relationshipsMomentsCopy } from "@/lib/personal/emotional_security/moments/relationshipsMomentsCopy";
import { WidgetInfoButton } from "@/components/personal/shared/WidgetInfoButton";

type RelationshipJourneyTimelineProps = {
  items: PersonalEmotionalSecurityJourneyTimelineItem[];
};

export function RelationshipJourneyTimeline({ items }: RelationshipJourneyTimelineProps) {
  const { colors } = useThemeTokens();

  return (
    <section>
      <div className="mb-2 flex items-center justify-between">
        <div className="flex items-center gap-0.5">
          <h3 className="text-[10px] font-bold uppercase tracking-widest opacity-50">
            {relationshipsMomentsCopy.journeyTimelineTitle}
          </h3>
          <WidgetInfoButton explainerId="MOMENT-004" momentTypeCode="RELATIONSHIPS" />
        </div>
        <button type="button" className="text-[10px] font-bold" style={{ color: "#818cf8" }}>
          {relationshipsMomentsCopy.viewAll}
        </button>
      </div>
      {items.length === 0 ? (
        <p className="text-sm opacity-70" style={{ color: colors.textSecondary }}>
          {relationshipsMomentsCopy.journeyTimelineEmpty}
        </p>
      ) : (
        <div className="space-y-2">
          {items.map((item) => (
            <div
              key={item.id}
              className="flex items-center gap-3 rounded-xl p-2"
              style={{ background: "rgba(20, 22, 48, 0.4)" }}
            >
              {item.image_url ? (
                <img
                  src={item.image_url}
                  alt=""
                  className="size-16 shrink-0 rounded-lg object-cover"
                />
              ) : (
                <div className="size-16 shrink-0 rounded-lg bg-white/10" />
              )}
              <div className="min-w-0 flex-1">
                <p className="text-[10px] opacity-60">{item.relative_time}</p>
                <h4 className="text-sm font-semibold" style={{ color: colors.textPrimary }}>
                  {item.category_label}
                </h4>
                <p className="mt-0.5 text-[10px] opacity-70" style={{ color: colors.textSecondary }}>
                  {item.detail_line}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
