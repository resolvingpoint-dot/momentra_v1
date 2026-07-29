"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { personalGlassCardStyle, personalTypography } from "@/components/personal/empty/shared/emptyStyles";
import type { PersonalLifeOpsEvolutionPhase } from "@/lib/api/personal";
import { fbMemoryCopy } from "@/lib/personal/future_building/memory/fbMemoryCopy";
import { Compass, Construction, Gauge } from "lucide-react";
import { WidgetInfoButton } from "@/components/personal/shared/WidgetInfoButton";

const PHASE_ICONS = [Compass, Construction, Gauge];

type Props = { phases: PersonalLifeOpsEvolutionPhase[] };

export function FbEvolutionTimelineSection({ phases }: Props) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  const activeIndex = phases.findIndex((p) => p.is_active);

  return (
    <section style={{ ...personalGlassCardStyle(tokens), borderRadius: 16, padding: 16 }}>
      <div className="mb-6 flex items-center gap-0.5">
        <span style={{ ...personalTypography.labelSm, fontSize: 11, fontWeight: 700, letterSpacing: "0.12em", textTransform: "uppercase", opacity: 0.7 }}>
          {fbMemoryCopy.sections.evolutionTimeline}
        </span>
        <WidgetInfoButton explainerId="MEMORY-008" momentTypeCode="FUTURE_BUILDING" />
      </div>
      <div className="flex items-center justify-between px-2 pb-2">
        {phases.map((phase, i) => {
          const Icon = PHASE_ICONS[i % PHASE_ICONS.length];
          const isActive = phase.is_active;
          const isPast = activeIndex >= 0 && i < activeIndex;
          return (
            <div key={phase.phase_id} className="flex flex-1 flex-col items-center gap-2" style={{ opacity: isActive || isPast ? 1 : 0.4 }}>
              {i > 0 ? (
                <div className="absolute hidden" />
              ) : null}
              <div
                className="flex size-8 items-center justify-center rounded-full border"
                style={{
                  background: isActive ? `${colors.brandPrimary}33` : "rgba(255,255,255,0.05)",
                  borderColor: isActive ? `${colors.brandPrimary}66` : "rgba(255,255,255,0.1)",
                }}
              >
                <Icon size={14} color={isActive ? colors.brandPrimary : colors.textSecondary} />
              </div>
              <span style={{ fontSize: 10, fontWeight: isActive ? 700 : 400, color: isActive ? colors.brandPrimary : colors.textSecondary }}>
                {phase.label}
              </span>
            </div>
          );
        })}
      </div>
      <div className="mx-6 flex items-center">
        {phases.slice(0, -1).map((phase, i) => (
          <div key={phase.phase_id} className="h-px flex-1" style={{ background: i < activeIndex ? `${colors.brandPrimary}4d` : "rgba(255,255,255,0.1)" }} />
        ))}
      </div>
    </section>
  );
}
