"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { personalGlassCardStyle } from "@/components/personal/empty/shared/emptyStyles";
import { WidgetInfoButton } from "@/components/personal/shared/WidgetInfoButton";
import type { PersonalLifestylePulseMetrics } from "@/lib/api/personal";
import { lifestylePulseCopy } from "@/lib/personal/lifestyle/pulse/lifestylePulseCopy";
import { Brain } from "lucide-react";

const MOMENT_TYPE = "LIFESTYLE";

type Props = { intelligence: PersonalLifestylePulseMetrics["intelligence"] };

export function LifestyleIntelligenceCard({ intelligence }: Props) {
  const tokens = useThemeTokens();
  const { colors } = tokens;

  return (
    <section
      className="relative overflow-hidden"
      style={{
        ...personalGlassCardStyle(tokens),
        borderRadius: 16,
        padding: 16,
        border: `1px solid ${colors.brandPrimary}4d`,
        boxShadow: "0 0 20px rgba(108, 78, 242, 0.2)",
      }}
    >
      <div className="pointer-events-none absolute -right-4 -top-4 opacity-10">
        <Brain size={64} color={colors.brandPrimary} fill={colors.brandPrimary} />
      </div>
      <div className="flex items-start gap-3">
        <div
          className="flex size-10 shrink-0 items-center justify-center rounded-lg border"
          style={{
            background: `${colors.brandPrimary}33`,
            borderColor: `${colors.brandPrimary}4d`,
            boxShadow: "0 0 15px rgba(108,78,242,0.3)",
          }}
        >
          <Brain size={20} color={colors.brandPrimary} fill={colors.brandPrimary} />
        </div>
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <span className="text-[9px] font-black uppercase tracking-[0.2em]" style={{ color: colors.brandPrimary }}>
              Intelligence Insight
            </span>
            <WidgetInfoButton explainerId="PULSE-011" momentTypeCode={MOMENT_TYPE} />
            <div className="h-px flex-1" style={{ background: `${colors.brandPrimary}33` }} />
          </div>
          <p className="mt-2 text-sm font-medium italic leading-relaxed">&ldquo;{intelligence.quote}&rdquo;</p>
        </div>
      </div>
    </section>
  );
}
