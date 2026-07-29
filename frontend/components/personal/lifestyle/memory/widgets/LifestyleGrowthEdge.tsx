"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { personalGlassCardStyle } from "@/components/personal/empty/shared/emptyStyles";
import type { PersonalLifeOpsGrowthEdge } from "@/lib/api/personal";
import { ArrowUpRight } from "lucide-react";
import { WidgetInfoButton } from "@/components/personal/shared/WidgetInfoButton";

type Props = { edge: PersonalLifeOpsGrowthEdge };

export function LifestyleGrowthEdge({ edge }: Props) {
  const tokens = useThemeTokens();
  const { colors } = tokens;

  return (
    <section style={{ ...personalGlassCardStyle(tokens), borderRadius: 16, padding: 16 }}>
      <div className="flex items-start justify-between gap-3">
        <div>
          <div className="flex items-center gap-0.5">
            <p className="text-[10px] font-bold uppercase tracking-widest opacity-60">Next Growth Edge</p>
            <WidgetInfoButton explainerId="MEMORY-010" momentTypeCode="LIFESTYLE" />
          </div>
          <h3 className="mt-1 text-lg font-bold">{edge.title}</h3>
          <p className="mt-2 text-sm opacity-70">{edge.body}</p>
        </div>
        <ArrowUpRight size={24} color={colors.brandPrimary} />
      </div>
    </section>
  );
}
