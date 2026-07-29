"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { personalGlassCardStyle } from "@/components/personal/empty/shared/emptyStyles";
import { LifestyleSectionBadge } from "@/components/personal/lifestyle/shared/LifestyleSectionBadge";
import type { PersonalLifeOpsBehavioralPattern } from "@/lib/api/personal";
import { Calendar, Brain } from "lucide-react";

type Props = { patterns: PersonalLifeOpsBehavioralPattern[] };

export function LifestyleBehavioralPatterns({ patterns }: Props) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  const icons = [Calendar, Brain];

  return (
    <section className="space-y-2">
      <LifestyleSectionBadge index={7} label="Behavioral Patterns" explainerId="MEMORY-005" />
      {patterns.map((pattern, i) => {
        const Icon = icons[i % icons.length];
        return (
          <div key={pattern.pattern_id} className="flex items-start gap-3" style={{ ...personalGlassCardStyle(tokens), borderRadius: 16, padding: 16 }}>
            <div className="flex size-10 items-center justify-center rounded-xl" style={{ background: `${colors.brandPrimary}1a`, color: colors.brandPrimary }}>
              <Icon size={20} />
            </div>
            <div className="min-w-0 flex-1">
              <div className="flex items-center justify-between gap-2">
                <p className="font-bold">{pattern.title}</p>
                {pattern.confidence_percent != null ? (
                  <span className="text-[10px] font-bold" style={{ color: colors.brandPrimary }}>
                    {pattern.confidence_percent}% Confidence
                  </span>
                ) : null}
              </div>
              <p className="mt-1 text-xs opacity-60">{pattern.subtitle}</p>
            </div>
          </div>
        );
      })}
    </section>
  );
}
