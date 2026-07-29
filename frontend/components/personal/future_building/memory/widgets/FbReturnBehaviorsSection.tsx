"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { personalGlassCardStyle, personalTypography } from "@/components/personal/empty/shared/emptyStyles";
import type { PersonalLifeOpsReturnBehaviors } from "@/lib/api/personal";
import { fbMemoryCopy } from "@/lib/personal/future_building/memory/fbMemoryCopy";
import { WidgetInfoButton } from "@/components/personal/shared/WidgetInfoButton";

type Props = { behaviors?: PersonalLifeOpsReturnBehaviors | null };

export function FbReturnBehaviorsSection({ behaviors }: Props) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  if (!behaviors) return null;

  const bars = behaviors.bars ?? [];
  const roiDigits = (behaviors.roi_label ?? "").replace(/[^0-9.]/g, "").slice(0, 3) || "—";

  return (
    <section className="group flex-1" style={{ ...personalGlassCardStyle(tokens), borderRadius: 16, padding: 16 }}>
      <div className="mb-4 flex items-center gap-0.5">
        <span style={{ ...personalTypography.labelSm, fontSize: 11, fontWeight: 700, letterSpacing: "0.12em", opacity: 0.7 }}>
          {fbMemoryCopy.sections.returnBehaviors}
        </span>
        <WidgetInfoButton explainerId="MEMORY-ROI" momentTypeCode="FUTURE_BUILDING" />
      </div>
      <div className="mb-2 flex items-center justify-between">
        <div>
          <p style={{ fontSize: 14, fontWeight: 700, color: colors.textPrimary }}>{behaviors.title}</p>
          <p style={{ fontSize: 10, color: colors.textSecondary }}>Highest Return Activity</p>
        </div>
        <div className="text-right">
          <p style={{ fontSize: 24, fontWeight: 700, color: colors.brandPrimary }}>{roiDigits}x</p>
          <p style={{ fontSize: 10, color: `${colors.brandPrimary}99` }}>growth return</p>
        </div>
      </div>
      <div className="flex h-24 items-end justify-around gap-1 pt-3">
        {bars.map((bar, i) => (
          <div
            key={bar.behavior_code}
            className="w-full rounded-t-sm transition-all group-hover:opacity-100"
            style={{
              height: `${Math.max(12, bar.height_fraction * 100)}%`,
              background: colors.brandPrimary,
              opacity: 0.2 + (i / Math.max(bars.length, 1)) * 0.8,
              boxShadow: i === bars.length - 1 ? `0 0 15px ${colors.brandPrimary}66` : undefined,
            }}
          />
        ))}
      </div>
    </section>
  );
}
