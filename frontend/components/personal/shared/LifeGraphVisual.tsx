"use client";

import { Lock } from "lucide-react";
import type { ContextThemeTokens } from "@/lib/contextTokens";
import type { PersonalLifeSatelliteScore } from "@/lib/api/personal";
import { satelliteColor } from "@/lib/personal/life/personalLifeCopy";
const SATELLITE_POSITIONS: Record<string, { x: string; y: string }> = {
  LIFE_OPERATIONS: { x: "8%", y: "6%" },
  FUTURE_BUILDING: { x: "72%", y: "6%" },
  LIFESTYLE: { x: "8%", y: "68%" },
  RELATIONSHIPS: { x: "72%", y: "68%" },
};

type LifeGraphVisualProps = {
  tokens: ContextThemeTokens;
  centerScore?: number;
  satelliteScores?: PersonalLifeSatelliteScore[];
  empty?: boolean;
};

export function LifeGraphVisual({
  tokens,
  centerScore,
  satelliteScores,
  empty = false,
}: LifeGraphVisualProps) {
  const { colors } = tokens;
  const nodes = satelliteScores ?? [];

  return (
    <div className="relative mx-auto h-[220px] w-full max-w-[400px] md:h-[260px]">
      <div
        className="absolute left-1/2 top-1/2 z-20 flex size-16 -translate-x-1/2 -translate-y-1/2 flex-col items-center justify-center rounded-full text-white shadow-[0_0_40px_rgba(108,78,242,0.6)] md:size-20"
        style={{ background: colors.primaryContainer }}
      >
        <span className="text-2xl font-bold md:text-3xl">{empty ? "M" : centerScore ?? "—"}</span>
        {!empty && (
          <span className="text-[8px] uppercase tracking-tight opacity-70">Life Health</span>
        )}
      </div>
      <div
        className="absolute left-1/2 top-1/2 h-px w-[120px] -translate-x-1/2 -translate-y-1/2 rotate-45"
        style={{ background: `color-mix(in srgb, ${colors.brandPrimary} 20%, transparent)` }}
      />
      <div
        className="absolute left-1/2 top-1/2 h-px w-[120px] -translate-x-1/2 -translate-y-1/2 -rotate-45"
        style={{ background: `color-mix(in srgb, ${colors.brandPrimary} 20%, transparent)` }}
      />
      {nodes.map((node) => {
        const pos = SATELLITE_POSITIONS[node.moment_type_code] ?? { x: "50%", y: "50%" };
        const accent = satelliteColor(node.color_token, colors);
        const locked = empty || node.score == null;
        return (
          <div
            key={node.moment_type_code}
            className="absolute flex flex-col items-center gap-1"
            style={{ left: pos.x, top: pos.y }}
          >
            <div
              className="flex size-12 items-center justify-center rounded-full border text-lg font-bold md:size-14"
              style={{
                borderColor: `color-mix(in srgb, ${accent} 50%, transparent)`,
                background: `color-mix(in srgb, ${accent} 15%, transparent)`,
                color: accent,
                opacity: locked ? 0.5 : 1,
              }}
            >
              {locked ? <Lock className="size-5 opacity-40" /> : node.score}
            </div>
            <span
              className="max-w-[80px] text-center text-[9px] font-bold uppercase tracking-wide"
              style={{ opacity: locked ? 0.4 : 0.7, color: colors.textSecondary }}
            >
              {node.label}
            </span>
          </div>
        );
      })}
    </div>
  );
}
