"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { personalGlassCardStyle, personalTypography } from "@/components/personal/empty/shared/emptyStyles";
import { PersonalWidgetSectionHeader } from "@/components/personal/shared/WidgetInfoButton";
import type { PersonalLifestylePulseMetrics } from "@/lib/api/personal";
import { lifestylePulseCopy } from "@/lib/personal/lifestyle/pulse/lifestylePulseCopy";
import { LIFESTYLE_SEGMENT_COLORS } from "@/lib/personal/lifestyle/pulse/lifestylePulseIcons";

const MOMENT_TYPE = "LIFESTYLE";

type Segment = PersonalLifestylePulseMetrics["financial_segments"][number];

type Props = {
  segments: Segment[];
  totalSpendMinor: number;
};

function Donut({ segments }: { segments: Segment[] }) {
  const tokens = useThemeTokens();
  const sum = segments.reduce((a, s) => a + s.share_percent, 0) || 100;
  let offset = 0;
  const r = 40;
  const c = 2 * Math.PI * r;

  return (
    <div className="relative aspect-square w-full">
      <svg viewBox="0 0 100 100" className="h-full w-full -rotate-90">
        {segments.length === 0 ? (
          <circle cx="50" cy="50" r={r} fill="none" stroke={tokens.colors.surfaceContainer} strokeWidth="12" />
        ) : (
          segments.map((seg, i) => {
            const dash = (seg.share_percent / sum) * c;
            const el = (
              <circle
                key={seg.category_id}
                cx="50"
                cy="50"
                r={r}
                fill="none"
                stroke={LIFESTYLE_SEGMENT_COLORS[i % LIFESTYLE_SEGMENT_COLORS.length]}
                strokeWidth="12"
                strokeDasharray={`${dash} ${c - dash}`}
                strokeDashoffset={-offset}
              />
            );
            offset += dash;
            return el;
          })
        )}
      </svg>
      <div className="pointer-events-none absolute inset-0 flex items-center justify-center">
        <span className="text-[9px] font-bold opacity-40">{segments.length || 0} Cats</span>
      </div>
    </div>
  );
}

function segmentLabel(seg: Segment) {
  return seg.category_name?.trim() || seg.category_id.slice(0, 8);
}

export function LifestyleFinancialPulse({ segments, totalSpendMinor }: Props) {
  const tokens = useThemeTokens();
  const { colors } = tokens;

  return (
    <section style={{ ...personalGlassCardStyle(tokens), borderRadius: 16, padding: 12 }}>
      <div className="mb-4 flex items-center justify-between">
        <PersonalWidgetSectionHeader title={lifestylePulseCopy.financialTitle} explainerId="PULSE-006" momentTypeCode={MOMENT_TYPE} />
        <div className="text-right">
          <div className="text-[9px] font-bold uppercase tracking-wider opacity-40">Total Spend</div>
          <div className="text-sm font-bold">{lifestylePulseCopy.formatInrMinor(totalSpendMinor)}</div>
        </div>
      </div>
      <div className="grid grid-cols-12 items-center gap-4">
        <div className="col-span-4">
          <Donut segments={segments} />
        </div>
        <div className="col-span-8 space-y-2">
          {segments.length > 0 ? (
            segments.map((seg, i) => (
              <div key={seg.category_id}>
                <div className="flex justify-between text-[10px] font-bold">
                  <span style={{ color: colors.textSecondary }}>
                    {segmentLabel(seg)} ({seg.share_percent}%)
                  </span>
                  <span>{lifestylePulseCopy.formatInrMinor(seg.amount_minor)}</span>
                </div>
                <div className="mt-1 h-1.5 overflow-hidden rounded-full" style={{ background: colors.surfaceContainer }}>
                  <div
                    className="h-full rounded-full"
                    style={{
                      width: `${Math.min(100, seg.share_percent)}%`,
                      background: LIFESTYLE_SEGMENT_COLORS[i % LIFESTYLE_SEGMENT_COLORS.length],
                    }}
                  />
                </div>
              </div>
            ))
          ) : (
            <p style={{ ...personalTypography.bodyMd, color: colors.textSecondary, opacity: 0.7 }}>
              {lifestylePulseCopy.financialEmptyHint}
            </p>
          )}
        </div>
      </div>
    </section>
  );
}
