"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { PersonalGlassGlowSection } from "@/components/personal/empty/shared/PersonalGlassGlowSection";
import { WidgetInfoButton } from "@/components/personal/shared/WidgetInfoButton";
import {
  memoryMicroLabelStyle,
  personalTypography,
} from "@/components/personal/empty/shared/emptyStyles";
import type { PersonalLifeOpsGrowthEdge } from "@/lib/api/personal";
import { lifeOpsMemoryCopy, type PersonalMemoryCopy } from "@/lib/personal/life_operations/memory/lifeOpsMemoryCopy";

type Props = {copy?: PersonalMemoryCopy;  edge: PersonalLifeOpsGrowthEdge; momentTypeCode?: string | null };

export function GrowthEdgeSection({ edge, copy, momentTypeCode = "LIFE_OPERATIONS" }: Props) {
  const tokens = useThemeTokens();
  const memoryCopy = copy ?? lifeOpsMemoryCopy;
  const { colors } = tokens;

  return (
    <PersonalGlassGlowSection
      tokens={tokens}
      cornerRadius={16}
      innerStyle={{
        padding: tokens.spacing.lg,
        borderLeft: `4px solid ${colors.brandPrimary}`,
      }}
    >
      <div className="flex items-center gap-0.5">
        <p style={memoryMicroLabelStyle(tokens)}>{memoryCopy.sectionLabels.growthEdge}</p>
        <WidgetInfoButton explainerId="MEMORY-010" momentTypeCode={momentTypeCode} />
      </div>
      <h3 style={{ ...personalTypography.screenTitle, color: colors.textPrimary, marginTop: 4 }}>{edge.title}</h3>
      <p style={{ ...personalTypography.bodyMd, color: colors.textSecondary, marginTop: tokens.spacing.sm }}>
        {edge.body}
      </p>
      <button
        type="button"
        className="mt-4 w-full rounded-2xl py-3 active:scale-[0.98]"
        style={{
          ...personalTypography.labelSm,
          fontWeight: 700,
          background: colors.brandPrimary,
          color: colors.brandOnPrimary ?? "#2f009c",
        }}
      >
        {edge.cta_label}
      </button>
    </PersonalGlassGlowSection>
  );
}

