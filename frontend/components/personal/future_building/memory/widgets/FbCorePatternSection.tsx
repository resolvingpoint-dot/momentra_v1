"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { personalGlassCardStyle, personalTypography } from "@/components/personal/empty/shared/emptyStyles";
import type { PersonalLifeOpsCorePattern } from "@/lib/api/personal";
import { fbMemoryCopy } from "@/lib/personal/future_building/memory/fbMemoryCopy";
import { ArrowRight, Brain, Rocket, Star } from "lucide-react";
import { WidgetInfoButton } from "@/components/personal/shared/WidgetInfoButton";

const NODE_ICONS: Record<string, typeof Brain> = {
  school: Brain,
  star: Star,
  rocket_launch: Rocket,
};

type Props = { pattern: PersonalLifeOpsCorePattern };

export function FbCorePatternSection({ pattern }: Props) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  const accents = [colors.brandPrimary, colors.brandSecondary, colors.brandTertiary];

  return (
    <section style={{ ...personalGlassCardStyle(tokens), borderRadius: 16, padding: 16 }}>
      <div className="mb-4 flex items-center gap-2">
        <span style={{ ...personalTypography.labelSm, fontSize: 11, fontWeight: 700, letterSpacing: "0.12em", opacity: 0.7 }}>
          {fbMemoryCopy.sections.corePattern}
        </span>
        <WidgetInfoButton explainerId="MEMORY-002" momentTypeCode="FUTURE_BUILDING" />
        <span
          className="ml-auto rounded border px-2 py-0.5 text-[10px] font-bold"
          style={{ color: colors.brandSecondary, background: `${colors.brandSecondary}1a`, borderColor: `${colors.brandSecondary}33` }}
        >
          {fbMemoryCopy.patternConfidence(pattern.pattern_confidence_percent)}
        </span>
      </div>
      <div className="relative flex items-center justify-between px-2">
        <div className="absolute left-[20%] right-[20%] top-[30px] z-0 h-px" style={{ background: "rgba(255,255,255,0.1)" }} />
        {pattern.nodes.map((node, i) => {
          const Icon = NODE_ICONS[node.icon] ?? Brain;
          const accent = accents[i % accents.length];
          return (
            <div key={node.node_id} className="relative z-10 flex flex-1 flex-col items-center gap-2">
              {i > 0 ? <ArrowRight size={16} className="absolute -left-4 top-4 opacity-30" color={colors.textSecondary} /> : null}
              <div
                className="flex size-14 items-center justify-center rounded-2xl border shadow-lg"
                style={{ background: `${accent}33`, borderColor: `${accent}4d`, boxShadow: `0 0 12px ${accent}33` }}
              >
                <Icon size={28} color={accent} />
              </div>
              <div className="text-center">
                <p style={{ fontSize: 12, fontWeight: 700, color: colors.textPrimary }}>{node.label}</p>
                <p style={{ fontSize: 10, color: colors.textSecondary }}>{node.subtitle}</p>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
