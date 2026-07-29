"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { personalGlassCardStyle, personalTypography } from "@/components/personal/empty/shared/emptyStyles";
import { fbMemoryCopy } from "@/lib/personal/future_building/memory/fbMemoryCopy";
import { Brain, Sparkles } from "lucide-react";
import { WidgetInfoButton } from "@/components/personal/shared/WidgetInfoButton";

type Props = { quote: string };

export function FbAiInterpretationSection({ quote }: Props) {
  const tokens = useThemeTokens();
  const { colors } = tokens;

  return (
    <section className="relative">
      <div
        aria-hidden
        className="absolute -inset-1 rounded-2xl opacity-30 blur-xl"
        style={{ background: `linear-gradient(90deg, ${colors.brandPrimary}4d, ${colors.brandTertiary}4d)` }}
      />
      <div
        className="relative flex items-center gap-6 rounded-2xl border p-6"
        style={{ ...personalGlassCardStyle(tokens), borderColor: `${colors.brandPrimary}4d` }}
      >
        <div className="min-w-0 flex-1">
          <div className="mb-2 flex items-center gap-2">
            <Sparkles size={14} color={colors.brandPrimary} />
            <span style={{ fontSize: 10, fontWeight: 700, textTransform: "uppercase", letterSpacing: "0.12em", color: colors.brandPrimary }}>
              {fbMemoryCopy.sections.aiInterpretation}
            </span>
            <WidgetInfoButton explainerId="MEMORY-009" momentTypeCode="FUTURE_BUILDING" />
          </div>
          <p style={{ ...personalTypography.bodyMd, fontStyle: "italic", color: colors.textPrimary }}>&ldquo;{quote}&rdquo;</p>
        </div>
        <div
          className="relative flex size-16 shrink-0 items-center justify-center overflow-hidden rounded-xl border"
          style={{ background: `${colors.primaryContainer}33`, borderColor: `${colors.brandPrimary}66` }}
        >
          <Brain size={28} color={colors.brandPrimary} />
        </div>
      </div>
    </section>
  );
}
