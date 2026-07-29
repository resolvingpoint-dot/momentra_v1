"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { personalGlassCardStyle } from "@/components/personal/empty/shared/emptyStyles";
import { LifestyleSectionBadge } from "@/components/personal/lifestyle/shared/LifestyleSectionBadge";
import type { PersonalLifestyleTurningPoint } from "@/lib/api/personal";
import { Flag, PiggyBank, Sparkles } from "lucide-react";

type Props = { points: PersonalLifestyleTurningPoint[] };

function turningIcon(icon: string) {
  if (icon === "savings") return PiggyBank;
  if (icon === "travel_explore") return Sparkles;
  return Flag;
}

const ICON_BG: Record<string, string> = {
  savings: "rgba(59,130,246,0.2)",
  travel_explore: "rgba(16,185,129,0.2)",
  flag: "rgba(59,130,246,0.2)",
};

const ICON_COLOR: Record<string, string> = {
  savings: "#60a5fa",
  travel_explore: "#10b981",
  flag: "#60a5fa",
};

export function LifestyleTurningPointsList({ points }: Props) {
  const tokens = useThemeTokens();

  return (
    <section className="pb-6">
      <div className="mb-3 flex items-center justify-between">
        <LifestyleSectionBadge index={5} label="Turning Points" explainerId="MOMENT-TP" />
        <button type="button" className="text-xs" style={{ color: "#60a5fa", background: "none", border: "none" }}>
          View all
        </button>
      </div>
      <div className="space-y-3">
        {points.map((point) => {
          const Icon = turningIcon(point.icon);
          return (
            <div
              key={point.turning_point_id}
              className="flex cursor-pointer items-start gap-3 transition-transform hover:scale-[1.02] active:scale-95"
              style={{ ...personalGlassCardStyle(tokens), borderRadius: 16, padding: 16, borderColor: "rgba(255,255,255,0.1)" }}
            >
              <div
                className="flex size-12 shrink-0 items-center justify-center rounded-full"
                style={{ background: ICON_BG[point.icon] ?? ICON_BG.flag }}
              >
                <Icon size={24} color={ICON_COLOR[point.icon] ?? ICON_COLOR.flag} />
              </div>
              <div className="min-w-0 flex-1">
                <div className="mb-0.5 flex items-baseline justify-between gap-2">
                  <h4 className="font-bold">{point.title}</h4>
                  {point.occurred_label ? (
                    <span className="shrink-0 text-[10px] opacity-60">{point.occurred_label}</span>
                  ) : null}
                </div>
                <p className="text-xs leading-relaxed opacity-60">{point.subtitle}</p>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}
