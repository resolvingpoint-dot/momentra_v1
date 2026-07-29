"use client";

import { Fragment } from "react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { PersonalGlassGlowSection } from "@/components/personal/empty/shared/PersonalGlassGlowSection";
import { WidgetInfoButton } from "@/components/personal/shared/WidgetInfoButton";
import {
  memoryMicroLabelStyle,
  personalTypography,
} from "@/components/personal/empty/shared/emptyStyles";
import type { PersonalLifeOpsCorePattern } from "@/lib/api/personal";
import { lifeOpsMemoryCopy, type PersonalMemoryCopy } from "@/lib/personal/life_operations/memory/lifeOpsMemoryCopy";

type Props = {copy?: PersonalMemoryCopy;  pattern: PersonalLifeOpsCorePattern; momentTypeCode?: string | null };

export function CorePatternSection({ pattern, copy, momentTypeCode = "LIFE_OPERATIONS" }: Props) {
  const tokens = useThemeTokens();
  const memoryCopy = copy ?? lifeOpsMemoryCopy;
  const { colors } = tokens;

  return (
    <PersonalGlassGlowSection
      tokens={tokens}
      cornerRadius={16}
      innerStyle={{ padding: tokens.spacing.lg, position: "relative" }}
    >
      <span
        className="absolute right-6 top-6 rounded border px-2 py-0.5 uppercase"
        style={{
          ...personalTypography.microLabel,
          fontSize: 9,
          borderColor: `${colors.brandPrimary}33`,
          background: `${colors.brandPrimary}1a`,
          color: colors.brandPrimary,
        }}
      >
        {memoryCopy.patternConfidence(pattern.pattern_confidence_percent)}
      </span>
      <div className="flex items-center gap-0.5">
        <p style={memoryMicroLabelStyle(tokens)}>{memoryCopy.sectionLabels.corePattern}</p>
        <WidgetInfoButton explainerId="MEMORY-002" momentTypeCode={momentTypeCode} />
      </div>
      <div className="mt-4 flex items-center justify-between">
        {pattern.nodes.map((node, i) => (
          <Fragment key={node.node_id}>
            {i > 0 ? (
              <span
                className="material-symbols-outlined shrink-0 text-lg"
                style={{ color: colors.textSecondary, opacity: 0.3 }}
              >
                trending_flat
              </span>
            ) : null}
            <div className="flex flex-1 flex-col items-center gap-2 text-center">
              <div
                className="flex h-12 w-12 items-center justify-center rounded-full"
                style={{ background: colors.surfaceHigh ?? `${colors.textSecondary}22` }}
              >
                <span className="material-symbols-outlined text-xl" style={{ color: colors.brandPrimary }}>
                  {node.icon}
                </span>
              </div>
              <p style={{ ...personalTypography.labelSm, fontWeight: 700, color: colors.textPrimary }}>
                {node.label}
              </p>
              <p style={{ ...personalTypography.microLabel, opacity: 0.4, color: colors.textSecondary }}>
                {node.subtitle}
              </p>
            </div>
          </Fragment>
        ))}
      </div>
    </PersonalGlassGlowSection>
  );
}

