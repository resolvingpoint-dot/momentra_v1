"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { PersonalGlassGlowSection } from "@/components/personal/empty/shared/PersonalGlassGlowSection";
import { WidgetInfoButton } from "@/components/personal/shared/WidgetInfoButton";
import {
  memoryMicroLabelStyle,
  personalTypography,
} from "@/components/personal/empty/shared/emptyStyles";
import type { PersonalLifeOpsEvolutionPhase } from "@/lib/api/personal";
import { lifeOpsMemoryCopy, type PersonalMemoryCopy } from "@/lib/personal/life_operations/memory/lifeOpsMemoryCopy";

type Props = {copy?: PersonalMemoryCopy;  phases: PersonalLifeOpsEvolutionPhase[]; momentTypeCode?: string | null };

export function EvolutionTimelineSection({ phases, copy, momentTypeCode = "LIFE_OPERATIONS" }: Props) {
  const tokens = useThemeTokens();
  const memoryCopy = copy ?? lifeOpsMemoryCopy;
  const { colors } = tokens;

  return (
    <PersonalGlassGlowSection tokens={tokens} cornerRadius={16} innerStyle={{ padding: tokens.spacing.lg }}>
      <div className="flex items-center gap-0.5">
        <p style={memoryMicroLabelStyle(tokens)}>{memoryCopy.sectionLabels.evolution}</p>
        <WidgetInfoButton explainerId="MEMORY-008" momentTypeCode={momentTypeCode} />
      </div>
      <div className="relative mt-8 flex items-center justify-between px-4">
        <div className="absolute left-0 top-1/2 -z-10 h-px w-full" style={{ background: `${colors.textSecondary}22` }} />
        {phases.map((phase) => (
          <div key={phase.phase_id} className="flex flex-col items-center gap-2" style={{ opacity: phase.is_active ? 1 : 0.35 }}>
            <div
              className="flex items-center justify-center rounded-full border-2"
              style={{
                width: phase.is_active ? 24 : 16,
                height: phase.is_active ? 24 : 16,
                borderColor: phase.is_active ? colors.brandPrimary : colors.textSecondary,
                background: phase.is_active ? `${colors.brandPrimary}33` : colors.background,
              }}
            >
              {phase.is_active ? <div className="h-2 w-2 rounded-full" style={{ background: colors.brandPrimary }} /> : null}
            </div>
            <span
              style={{
                ...personalTypography.labelSm,
                fontWeight: 700,
                textTransform: "uppercase",
                color: phase.is_active ? colors.brandPrimary : colors.textSecondary,
              }}
            >
              {phase.label}
            </span>
          </div>
        ))}
      </div>
    </PersonalGlassGlowSection>
  );
}

