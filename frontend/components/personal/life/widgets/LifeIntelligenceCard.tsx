"use client";

import { useState } from "react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { personalTypography } from "@/components/personal/empty/shared/emptyStyles";
import { personalLifeCopy } from "@/lib/personal/life/personalLifeCopy";
import { pressableMotionClass } from "@/lib/motion/pressable";
import type { PersonalLifeMetrics } from "@/lib/api/personal";
import { Brain, ChevronDown } from "lucide-react";
import { LifeCard } from "./LifeCard";
import { LifeSectionLabel } from "./LifeSectionLabel";

type LifeIntelligenceCardProps = {
  intelligence: PersonalLifeMetrics["intelligence"];
  onQuickAdd?: (eventType: string) => void;
};

export function LifeIntelligenceCard({ intelligence, onQuickAdd }: LifeIntelligenceCardProps) {
  const { colors } = useThemeTokens();
  const [expanded, setExpanded] = useState(false);

  return (
    <LifeCard className="relative overflow-hidden">
      <LifeSectionLabel explainerId="LIFE-010">{personalLifeCopy.sections.intelligence}</LifeSectionLabel>
      <p className="mt-3" style={{ ...personalTypography.labelSm, opacity: 0.7, color: colors.textSecondary }}>
        {intelligence.preamble}
      </p>
      <h4 className="mt-2 leading-snug" style={{ ...personalTypography.sectionHeader, color: colors.textPrimary }}>
        {intelligence.insight_text}
      </h4>
      <button
        type="button"
        className={`mt-3 flex items-center gap-1 text-xs font-semibold ${pressableMotionClass}`}
        onClick={() => setExpanded((v) => !v)}
        style={{ color: colors.brandPrimary, background: "none", border: "none", padding: 0 }}
        aria-expanded={expanded}
      >
        Why this insight?
        <ChevronDown className={`size-3.5 transition-transform ${expanded ? "rotate-180" : ""}`} />
      </button>
      {expanded ? (
        <p className="mt-2 text-sm leading-relaxed" style={{ color: colors.textSecondary }}>
          {intelligence.preamble}
        </p>
      ) : null}
      <button
        type="button"
        className={`mt-6 rounded-xl border px-4 py-2 ${pressableMotionClass}`}
        onClick={() => onQuickAdd?.(intelligence.cta_action_code ?? "REFLECTION")}
        style={{
          ...personalTypography.labelSm,
          fontWeight: 700,
          borderColor: colors.brandPrimary,
          color: colors.brandPrimary,
        }}
      >
        {intelligence.cta_label}
      </button>
      <Brain
        className="absolute -bottom-4 -right-4 size-24 opacity-10"
        style={{ color: colors.brandPrimary }}
      />
    </LifeCard>
  );
}
