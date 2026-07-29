"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { PersonalGlassGlowSection } from "@/components/personal/empty/shared/PersonalGlassGlowSection";
import { WidgetInfoButton } from "@/components/personal/shared/WidgetInfoButton";
import {
  memoryMicroLabelStyle,
  personalTypography,
} from "@/components/personal/empty/shared/emptyStyles";
import type { PersonalLifeOpsBehavioralPattern } from "@/lib/api/personal";
import { lifeOpsMemoryCopy, type PersonalMemoryCopy } from "@/lib/personal/life_operations/memory/lifeOpsMemoryCopy";

type Props = {copy?: PersonalMemoryCopy;  patterns: PersonalLifeOpsBehavioralPattern[]; momentTypeCode?: string | null };

export function BehavioralPatternsSection({ patterns, copy, momentTypeCode = "LIFE_OPERATIONS" }: Props) {
  const tokens = useThemeTokens();
  const memoryCopy = copy ?? lifeOpsMemoryCopy;
  const { colors } = tokens;

  if (patterns.length === 0) return null;

  return (
    <PersonalGlassGlowSection tokens={tokens} cornerRadius={16} innerStyle={{ padding: tokens.spacing.lg }}>
      <div className="flex items-center gap-0.5">
        <p style={memoryMicroLabelStyle(tokens)}>{memoryCopy.sectionLabels.behavioralPatterns}</p>
        <WidgetInfoButton explainerId="MEMORY-005" momentTypeCode={momentTypeCode} />
      </div>
      <div className="mt-3 space-y-2">
        {patterns.map((p) => (
          <div
            key={p.pattern_id}
            className="flex items-center gap-3 rounded-2xl border p-2"
            style={{ background: `${colors.textSecondary}0d`, borderColor: `${colors.textSecondary}14` }}
          >
            <span className="material-symbols-outlined text-2xl" style={{ color: colors.brandPrimary }}>
              {p.icon}
            </span>
            <div className="flex-1">
              <p style={{ ...personalTypography.labelSm, fontWeight: 600, color: colors.textPrimary }}>
                {p.title}
              </p>
              <p style={{ ...personalTypography.labelSm, color: colors.textSecondary, opacity: 0.6 }}>
                {p.subtitle}
              </p>
            </div>
            <span style={{ ...personalTypography.microLabel, color: colors.brandPrimary }}>{p.confidence_percent}%</span>
          </div>
        ))}
      </div>
    </PersonalGlassGlowSection>
  );
}

