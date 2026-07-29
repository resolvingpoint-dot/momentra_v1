"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { personalGlassCardStyle, personalGlowWrapperStyle, personalTypography } from "@/components/personal/empty/shared/emptyStyles";
import { WidgetInfoButton } from "@/components/personal/shared/WidgetInfoButton";
import { fbPulseCopy } from "@/lib/personal/future_building/pulse/fbPulseCopy";
import { Rocket } from "lucide-react";

const MOMENT_TYPE = "FUTURE_BUILDING";

type Opportunity = {
  title: string;
  body: string;
  cta_label: string;
  cta_event_type?: string;
  growth_impact: number;
  confidence_impact: number;
};

type Props = {
  opportunity: Opportunity;
  onQuickAdd?: (action: string) => void;
};

export function FbOpportunityCard({ opportunity, onQuickAdd }: Props) {
  const tokens = useThemeTokens();
  const { colors } = tokens;

  return (
    <section style={personalGlowWrapperStyle(tokens)}>
      <div
        className="relative overflow-hidden transition-transform hover:scale-[1.02] active:scale-95"
        style={{
          ...personalGlassCardStyle(tokens),
          borderRadius: 24,
          padding: 20,
          border: `1px solid ${colors.brandPrimary}66`,
          background: `linear-gradient(135deg, ${colors.primaryContainer}4d, rgba(26,23,40,0.95))`,
          boxShadow: `0 0 30px ${colors.brandPrimary}33`,
        }}
      >
        <div className="relative z-10 flex items-start justify-between gap-4">
          <div className="max-w-[65%] space-y-1">
            <div className="flex items-center gap-0.5">
              <p style={{ fontSize: 10, fontWeight: 900, letterSpacing: "0.2em", textTransform: "uppercase", color: colors.brandPrimary }}>
                {fbPulseCopy.highPriorityOpportunity}
              </p>
              <WidgetInfoButton explainerId="PULSE-009" momentTypeCode={MOMENT_TYPE} />
            </div>
            <h4 style={{ fontSize: 16, fontWeight: 700, color: colors.textPrimary }}>{opportunity.title}</h4>
            <p style={{ ...personalTypography.bodyMd, fontSize: 12, opacity: 0.8, marginTop: 8 }}>{opportunity.body}</p>
          </div>
          <div className="flex size-16 items-center justify-center" style={{ color: colors.brandPrimary, filter: `drop-shadow(0 0 15px ${colors.brandPrimary}99)` }}>
            <Rocket size={40} className="animate-pulse" />
          </div>
        </div>
        <div className="relative z-10 mt-6 flex flex-col gap-4">
          <div className="flex gap-2">
            {opportunity.growth_impact !== 0 ? (
              <span className="rounded-full border px-3 py-1.5 text-[9px] font-bold" style={{ background: "rgba(255,255,255,0.08)", borderColor: "rgba(255,255,255,0.1)" }}>
                <span style={{ color: colors.brandTertiary }}>+{opportunity.growth_impact}</span> Growth
              </span>
            ) : null}
            {opportunity.confidence_impact !== 0 ? (
              <span className="rounded-full border px-3 py-1.5 text-[9px] font-bold" style={{ background: "rgba(255,255,255,0.08)", borderColor: "rgba(255,255,255,0.1)" }}>
                <span style={{ color: colors.brandTertiary }}>+{opportunity.confidence_impact}</span> Confidence
              </span>
            ) : null}
          </div>
          <button
            type="button"
            onClick={() => onQuickAdd?.(opportunity.cta_event_type ?? "OPPORTUNITY")}
            className="w-full rounded-2xl py-3.5 text-xs font-bold uppercase tracking-widest shadow-xl"
            style={{ background: colors.brandPrimary, color: colors.brandOnPrimary, border: "none" }}
          >
            {opportunity.cta_label}
          </button>
        </div>
        <div
          aria-hidden
          className="absolute -bottom-10 -right-10 size-48 rounded-full blur-3xl"
          style={{ background: `${colors.brandPrimary}4d` }}
        />
      </div>
    </section>
  );
}
