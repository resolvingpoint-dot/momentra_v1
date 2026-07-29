"use client";

import { motion } from "framer-motion";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { personalGlassCardStyle, personalTypography } from "@/components/personal/empty/shared/emptyStyles";
import type { PersonalLiveRecentActivityItem } from "@/lib/api/personal";
import { lifeOpsMomentsCopy } from "@/lib/personal/life_operations/moments/lifeOpsMomentsCopy";
import { resolveActivityIcon } from "@/lib/personal/life_operations/pulse/pulseIcons";
import { MOTION_DURATION_S } from "@/lib/motion/tokens";
import { useReducedMotion } from "@/lib/motion/useReducedMotion";
import { PersonalWidgetSectionHeader } from "@/components/personal/shared/WidgetInfoButton";

type JourneyTimelineProps = {
  items: PersonalLiveRecentActivityItem[];
};

export function JourneyTimeline({ items }: JourneyTimelineProps) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  const reducedMotion = useReducedMotion();

  return (
    <section>
      <PersonalWidgetSectionHeader title={lifeOpsMomentsCopy.journeyTimelineTitle} explainerId="MOMENT-004" momentTypeCode="LIFE_OPERATIONS" className="mb-3" />
      {items.length === 0 ? (
        <p style={{ ...personalTypography.bodyMd, color: colors.textSecondary, opacity: 0.7 }}>
          {lifeOpsMomentsCopy.journeyTimelineEmpty}
        </p>
      ) : (
        <div className="relative space-y-0 pl-6">
          <svg className="absolute bottom-2 left-0 top-2 h-[calc(100%-16px)] w-6 overflow-visible" aria-hidden>
            <motion.line
              x1={11}
              y1={0}
              x2={11}
              y2="100%"
              stroke={`${colors.brandPrimary}44`}
              strokeWidth={1}
              initial={{ pathLength: reducedMotion ? 1 : 0 }}
              animate={{ pathLength: 1 }}
              transition={{ duration: reducedMotion ? 0 : MOTION_DURATION_S.slow }}
            />
          </svg>
          {items.map((item, index) => {
            const Icon = resolveActivityIcon(item.event_type);
            return (
              <motion.div
                key={item.id}
                className="relative pb-4"
                initial={reducedMotion ? false : { opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: reducedMotion ? 0 : index * 0.08, duration: MOTION_DURATION_S.normal }}
              >
                <div
                  className="absolute -left-6 flex size-6 items-center justify-center rounded-full border"
                  style={{
                    background: colors.surfaceContainer,
                    borderColor: `${colors.brandPrimary}55`,
                  }}
                >
                  <Icon className="size-3" style={{ color: colors.brandPrimary }} />
                </div>
                <div style={{ ...personalGlassCardStyle(tokens), borderRadius: 16, padding: 12 }}>
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <p className="text-sm font-semibold" style={{ color: colors.textPrimary }}>
                        {item.category_label}
                      </p>
                      <p className="mt-0.5 text-xs" style={{ color: colors.textSecondary }}>
                        {item.detail_line}
                      </p>
                    </div>
                    <span className="shrink-0 text-[10px] font-medium opacity-60">{item.relative_time}</span>
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>
      )}
    </section>
  );
}
