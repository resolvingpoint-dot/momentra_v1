"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { personalGlassCardStyle, personalTypography } from "@/components/personal/empty/shared/emptyStyles";
import type { PersonalLifeOpsBehavioralPattern } from "@/lib/api/personal";
import { fbMemoryCopy } from "@/lib/personal/future_building/memory/fbMemoryCopy";
import { Calendar, Sun } from "lucide-react";
import { WidgetInfoButton } from "@/components/personal/shared/WidgetInfoButton";

const ICONS = [Calendar, Sun];

type Props = { patterns: PersonalLifeOpsBehavioralPattern[] };

export function FbBehavioralPatternsSection({ patterns }: Props) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  if (patterns.length === 0) return null;

  return (
    <section className="space-y-2">
      <div className="mb-2 flex items-center gap-0.5">
        <span style={{ ...personalTypography.labelSm, fontSize: 11, fontWeight: 700, letterSpacing: "0.12em", textTransform: "uppercase", opacity: 0.7 }}>
          {fbMemoryCopy.sections.behavioralPatterns}
        </span>
        <WidgetInfoButton explainerId="MEMORY-005" momentTypeCode="FUTURE_BUILDING" />
      </div>
      <div className="grid grid-cols-1 gap-2">
        {patterns.map((pattern, i) => {
          const Icon = ICONS[i % ICONS.length];
          const accent = i % 2 === 0 ? colors.brandPrimary : colors.brandSecondary;
          return (
            <div
              key={pattern.pattern_id}
              className="flex items-center gap-3 rounded-xl p-3 transition-colors hover:opacity-90"
              style={{ ...personalGlassCardStyle(tokens), borderRadius: 12 }}
            >
              <div
                className="flex size-10 items-center justify-center rounded-full border"
                style={{ background: `${accent}1a`, borderColor: `${accent}33` }}
              >
                <Icon size={20} color={accent} />
              </div>
              <div className="flex-1">
                <p style={{ fontSize: 14, fontWeight: 700, color: colors.textPrimary }}>{pattern.title}</p>
                <p style={{ fontSize: 11, color: colors.textSecondary }}>{pattern.subtitle}</p>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
