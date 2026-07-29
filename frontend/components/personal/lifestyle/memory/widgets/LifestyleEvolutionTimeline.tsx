"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { personalGlassCardStyle } from "@/components/personal/empty/shared/emptyStyles";
import { LifestyleSectionBadge } from "@/components/personal/lifestyle/shared/LifestyleSectionBadge";
import type { PersonalLifeOpsEvolutionPhase } from "@/lib/api/personal";

type Props = { phases: PersonalLifeOpsEvolutionPhase[] };

export function LifestyleEvolutionTimeline({ phases }: Props) {
  const tokens = useThemeTokens();
  const { colors } = tokens;

  return (
    <section style={{ ...personalGlassCardStyle(tokens), borderRadius: 16, padding: 16 }}>
      <LifestyleSectionBadge index={8} label="Evolution Timeline" explainerId="MEMORY-008" />
      <div className="mt-4 flex flex-wrap gap-2">
        {phases.map((phase) => (
          <div
            key={phase.phase_id}
            className="rounded-full border px-4 py-2 text-xs font-bold"
            style={{
              borderColor: phase.is_active ? colors.brandPrimary : "rgba(255,255,255,0.1)",
              color: phase.is_active ? colors.brandPrimary : colors.textSecondary,
              opacity: phase.is_active ? 1 : 0.6,
            }}
          >
            {phase.label}
          </div>
        ))}
      </div>
    </section>
  );
}
