"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { personalGlassCardStyle } from "@/components/personal/empty/shared/emptyStyles";
import type { PersonalLifeOpsAiInterpretation } from "@/lib/api/personal";
import { Sparkles } from "lucide-react";
import { WidgetInfoButton } from "@/components/personal/shared/WidgetInfoButton";

type Props = { interpretation: PersonalLifeOpsAiInterpretation };

export function LifestyleAiInterpretation({ interpretation }: Props) {
  const tokens = useThemeTokens();
  const { colors } = tokens;

  return (
    <section style={{ ...personalGlassCardStyle(tokens), borderRadius: 16, padding: 16, border: `1px solid ${colors.brandPrimary}33` }}>
      <div className="flex items-start gap-2">
        <Sparkles size={20} color={colors.brandPrimary} />
        <div>
          <div className="flex items-center gap-0.5">
            <p className="text-[10px] font-bold uppercase tracking-widest" style={{ color: colors.brandPrimary }}>
              Momentra Interpretation
            </p>
            <WidgetInfoButton explainerId="MEMORY-009" momentTypeCode="LIFESTYLE" />
          </div>
          <p className="mt-2 text-sm leading-relaxed opacity-80 italic">&ldquo;{interpretation.quote}&rdquo;</p>
        </div>
      </div>
    </section>
  );
}
