"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { personalGlassCardStyle } from "@/components/personal/empty/shared/emptyStyles";
import { LifestyleSectionBadge } from "@/components/personal/lifestyle/shared/LifestyleSectionBadge";
import type { PersonalLifeOpsEmotionalDna } from "@/lib/api/personal";

type Props = { dna: PersonalLifeOpsEmotionalDna };

const SEGMENT_COLORS = ["#6c4ef2", "#4cd6ff", "#cabeff"];

export function LifestyleEmotionalDna({ dna }: Props) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  let offset = 0;
  const r = 16;
  const c = 2 * Math.PI * r;

  return (
    <section style={{ ...personalGlassCardStyle(tokens), borderRadius: 16, padding: 16 }}>
      <div className="mb-4 flex items-center gap-2">
        <LifestyleSectionBadge index={6} label="Emotional DNA" explainerId="MEMORY-007" />
      </div>
      <div className="flex items-center gap-8">
        <div className="relative size-32">
          <svg className="-rotate-90" viewBox="0 0 36 36" width={128} height={128}>
            {dna.segments.map((seg, i) => {
              const dash = (seg.percent / 100) * c;
              const el = (
                <circle
                  key={seg.segment_id}
                  cx="18"
                  cy="18"
                  r={r}
                  fill="none"
                  stroke={SEGMENT_COLORS[i % SEGMENT_COLORS.length]}
                  strokeWidth="3"
                  strokeDasharray={`${dash} ${c}`}
                  strokeDashoffset={-offset}
                />
              );
              offset += dash;
              return el;
            })}
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-[10px] font-bold uppercase tracking-tighter opacity-60">Peak</span>
            <span className="text-lg font-bold">{dna.dominant_label}</span>
          </div>
        </div>
        <div className="flex-1 space-y-2">
          {dna.segments.map((seg, i) => (
            <div key={seg.segment_id} className="flex items-center gap-2">
              <div className="size-2 rounded-full" style={{ background: SEGMENT_COLORS[i % SEGMENT_COLORS.length] }} />
              <span className="text-xs">{seg.label}</span>
              <span className="ml-auto text-xs font-bold">{seg.percent}%</span>
            </div>
          ))}
        </div>
      </div>
      {dna.insight_body ? (
        <p className="mt-4 border-t pt-3 text-xs italic opacity-60" style={{ borderColor: "rgba(255,255,255,0.05)" }}>
          &ldquo;{dna.insight_body}&rdquo;
        </p>
      ) : null}
    </section>
  );
}
