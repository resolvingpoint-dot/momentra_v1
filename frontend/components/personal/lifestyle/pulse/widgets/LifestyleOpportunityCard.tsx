"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { personalGlowWrapperStyle } from "@/components/personal/empty/shared/emptyStyles";
import { WidgetInfoButton } from "@/components/personal/shared/WidgetInfoButton";
import type { PersonalLifestylePulseMetrics } from "@/lib/api/personal";
import { lifestylePulseCopy } from "@/lib/personal/lifestyle/pulse/lifestylePulseCopy";
import { ArrowRight, Mountain } from "lucide-react";

const MOMENT_TYPE = "LIFESTYLE";

type Props = {
  opportunity: PersonalLifestylePulseMetrics["opportunity"];
  onCta?: () => void;
};

export function LifestyleOpportunityCard({ opportunity, onCta }: Props) {
  const tokens = useThemeTokens();
  const { colors } = tokens;

  return (
    <section style={personalGlowWrapperStyle(tokens)}>
      <div
        className="relative overflow-hidden rounded-2xl p-4 transition-transform hover:scale-[1.02] active:scale-95"
        style={{
          background: colors.primaryContainer,
          boxShadow: "0 20px 50px rgba(108,78,242,0.3)",
        }}
      >
        <div className="pointer-events-none absolute -right-10 -top-10 opacity-30">
          <Mountain size={180} color="#fff" fill="#fff" />
        </div>
        <div className="relative z-10 flex flex-col gap-4">
          <div>
            <div className="flex items-center gap-0.5">
              <span className="text-[10px] font-black uppercase tracking-[0.2em] opacity-70">{lifestylePulseCopy.highPriorityOpportunity}</span>
              <WidgetInfoButton explainerId="PULSE-009" momentTypeCode={MOMENT_TYPE} />
            </div>
            <h3 className="mt-1 text-2xl font-bold text-white">{opportunity.title}</h3>
            <p className="mt-2 max-w-[85%] text-sm leading-relaxed opacity-80">{opportunity.body}</p>
          </div>
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex gap-2">
              <span className="rounded-full bg-white/10 px-3 py-1 text-[10px] font-bold text-white">+6 Fulfillment</span>
              <span className="rounded-full bg-white/10 px-3 py-1 text-[10px] font-bold text-white">+4 Vitality</span>
            </div>
            <button
              type="button"
              onClick={onCta}
              className="flex items-center gap-2 rounded-xl bg-white px-4 py-2.5 text-xs font-black active:scale-95"
              style={{ color: colors.brandPrimary, border: "none" }}
            >
              {opportunity.cta_label}
              <ArrowRight size={14} />
            </button>
          </div>
        </div>
      </div>
    </section>
  );
}
