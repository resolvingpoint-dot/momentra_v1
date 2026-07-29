"use client";

import { useEffect, useState } from "react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { WidgetInfoButton } from "@/components/personal/shared/WidgetInfoButton";
import {
  memoryMicroLabelStyle,
  personalGlowWrapperStyle,
  personalTypography,
} from "@/components/personal/empty/shared/emptyStyles";
import type { PersonalLifeOpsAiInterpretation } from "@/lib/api/personal";
import { lifeOpsMemoryCopy, type PersonalMemoryCopy } from "@/lib/personal/life_operations/memory/lifeOpsMemoryCopy";
import { MOTION_STAGGER } from "@/lib/motion/tokens";
import { useReducedMotion } from "@/lib/motion/useReducedMotion";

type Props = {copy?: PersonalMemoryCopy; interpretation: PersonalLifeOpsAiInterpretation; momentTypeCode?: string | null };

export function AiInterpretationSection({ interpretation, copy, momentTypeCode = "LIFE_OPERATIONS" }: Props) {
  const tokens = useThemeTokens();
  const memoryCopy = copy ?? lifeOpsMemoryCopy;
  const { colors } = tokens;
  const reducedMotion = useReducedMotion();
  const fullQuote = interpretation.quote;
  const [displayed, setDisplayed] = useState(reducedMotion ? fullQuote : "");
  const [highlight, setHighlight] = useState(false);

  useEffect(() => {
    if (reducedMotion) {
      setDisplayed(fullQuote);
      setHighlight(true);
      return;
    }
    setDisplayed("");
    setHighlight(false);
    let i = 0;
    const step = Math.max(1, Math.floor(fullQuote.length / 40));
    const id = window.setInterval(() => {
      i += step;
      if (i >= fullQuote.length) {
        setDisplayed(fullQuote);
        setHighlight(true);
        window.clearInterval(id);
      } else {
        setDisplayed(fullQuote.slice(0, i));
      }
    }, MOTION_STAGGER.field * 1000);
    return () => window.clearInterval(id);
  }, [fullQuote, reducedMotion]);

  return (
    <section style={personalGlowWrapperStyle(tokens)}>
      <div
        className="relative overflow-hidden rounded-[2rem] border p-6 transition-shadow duration-500"
        style={{
          borderColor: `${colors.textSecondary}1a`,
          background: `linear-gradient(135deg, ${colors.primaryContainer ?? colors.brandPrimary}66, transparent)`,
          boxShadow: highlight ? `0 0 24px ${colors.brandPrimary}22` : undefined,
        }}
      >
        <div className="relative z-10 flex flex-col gap-3 sm:flex-row">
          <div
            className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl border"
            style={{ background: `${colors.brandPrimary}33`, borderColor: `${colors.brandPrimary}4d`, color: colors.brandPrimary }}
          >
            <span className="material-symbols-outlined text-3xl" style={{ fontVariationSettings: "'FILL' 1" }}>
              auto_awesome
            </span>
          </div>
          <div className="space-y-2">
            <div className="flex items-center gap-0.5">
              <p style={memoryMicroLabelStyle(tokens)}>{memoryCopy.sectionLabels.aiInterpretation}</p>
              <WidgetInfoButton explainerId="MEMORY-009" momentTypeCode={momentTypeCode} />
            </div>
            <p style={{ ...personalTypography.sectionHeader, color: colors.textPrimary }} aria-live="polite">
              &ldquo;{displayed}&rdquo;
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
