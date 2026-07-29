"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { personalGlassCardStyle } from "@/components/personal/empty/shared/emptyStyles";
import { LifestyleSectionBadge } from "@/components/personal/lifestyle/shared/LifestyleSectionBadge";
import type { PersonalLifeOpsCorePattern } from "@/lib/api/personal";
import { Bolt, ChevronRight, Compass, Heart } from "lucide-react";

const NODE_ICONS: Record<string, typeof Compass> = {
  experiences: Compass,
  fulfillment: Heart,
  vitality: Bolt,
  explore: Compass,
  favorite: Heart,
};

export function LifestyleCorePattern({ pattern }: { pattern: PersonalLifeOpsCorePattern }) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  const nodes = pattern.nodes;

  return (
    <section style={{ ...personalGlassCardStyle(tokens), borderRadius: 16, padding: 16 }}>
      <div className="mb-4 flex items-center gap-2">
        <LifestyleSectionBadge index={2} label="Core Pattern" explainerId="MEMORY-002" />
        {pattern.pattern_confidence_percent != null ? (
          <span
            className="ml-auto rounded-full border px-2 py-0.5 text-[10px] font-bold"
            style={{ color: colors.brandSecondary, borderColor: `${colors.brandSecondary}33`, background: `${colors.brandSecondary}1a` }}
          >
            Pattern Confidence {pattern.pattern_confidence_percent}%
          </span>
        ) : null}
      </div>
      <div className="relative flex items-center justify-between py-4">
        {nodes.map((node, i) => {
          const Icon = NODE_ICONS[node.node_id] ?? NODE_ICONS[node.icon ?? ""] ?? Compass;
          const nodeColors = [colors.brandPrimary, colors.brandSecondary, colors.tertiary];
          const c = nodeColors[i % nodeColors.length];
          return (
            <div key={node.node_id} className="contents">
              {i > 0 ? (
                <div className="relative mx-1 h-0.5 flex-1" style={{ background: `linear-gradient(90deg, ${nodeColors[i - 1]}66, ${c}66)` }}>
                  <ChevronRight className="absolute left-1/2 top-1/2 size-3 -translate-x-1/2 -translate-y-1/2 opacity-40" />
                </div>
              ) : null}
              <div className="z-10 flex flex-col items-center gap-2">
                <div
                  className="flex size-12 items-center justify-center rounded-full border"
                  style={{ background: `${c}33`, borderColor: `${c}4d` }}
                >
                  <Icon size={22} color={c} />
                </div>
                <span className="text-[10px] font-bold">{node.label}</span>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
