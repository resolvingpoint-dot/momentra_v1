"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { personalGlassCardStyle, personalTypography } from "@/components/personal/empty/shared/emptyStyles";
import type { PersonalLifeOpsIdentitySnapshot } from "@/lib/api/personal";
import { fbMemoryCopy } from "@/lib/personal/future_building/memory/fbMemoryCopy";
import { WidgetInfoButton } from "@/components/personal/shared/WidgetInfoButton";

type Props = { snapshot: PersonalLifeOpsIdentitySnapshot };

export function FbIdentitySnapshotSection({ snapshot }: Props) {
  const tokens = useThemeTokens();
  const { colors } = tokens;

  return (
    <section className="relative overflow-hidden rounded-2xl" style={{ ...personalGlassCardStyle(tokens), padding: 16 }}>
      <div className="mb-3 flex items-center gap-2">
        <span
          className="rounded border px-2 py-0.5 text-[11px] font-bold tracking-widest"
          style={{ color: colors.brandPrimary, background: `${colors.brandPrimary}1a`, borderColor: `${colors.brandPrimary}33` }}
        >
          {fbMemoryCopy.interpretationBadge}
        </span>
      </div>
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <div className="mb-1 flex items-center gap-0.5">
            <h2 style={{ ...personalTypography.heroTitle, color: colors.brandPrimary }}>{snapshot.title}</h2>
            <WidgetInfoButton explainerId="MEMORY-001" momentTypeCode="FUTURE_BUILDING" />
          </div>
          <p style={{ ...personalTypography.labelSm, color: colors.brandPrimary, fontWeight: 700, marginBottom: 8 }}>{snapshot.trend_label}</p>
          <p style={{ ...personalTypography.bodyMd, color: colors.textSecondary }}>{snapshot.body}</p>
        </div>
        <div className="shrink-0 text-right">
          <span style={{ fontSize: 8, textTransform: "uppercase", color: colors.textSecondary, display: "block", marginBottom: 4 }}>
            {fbMemoryCopy.identityQuarterLabel}
          </span>
          <span style={{ fontSize: 10, textTransform: "uppercase", color: colors.textSecondary, display: "block" }}>{fbMemoryCopy.confidenceLabel}</span>
          <span style={{ fontSize: 30, fontWeight: 700, color: colors.textPrimary }}>{snapshot.confidence_percent}%</span>
        </div>
      </div>
      {snapshot.image_url ? (
        <div className="relative mt-3 h-48 overflow-hidden rounded-xl border" style={{ borderColor: "rgba(255,255,255,0.06)", background: colors.surfaceContainer }}>
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={snapshot.image_url} alt={snapshot.title} className="size-full object-cover opacity-80 transition-transform duration-700 hover:scale-110" />
          <div className="absolute inset-0 bg-gradient-to-t from-[#14121b] via-transparent to-transparent" />
          <div className="absolute bottom-4 left-4">
            <span
              className="rounded-full border px-3 py-1 text-xs backdrop-blur-md"
              style={{ color: colors.brandPrimary, background: "rgba(20,18,27,0.6)", borderColor: `${colors.brandPrimary}4d` }}
            >
              {fbMemoryCopy.identityChip}
            </span>
          </div>
        </div>
      ) : null}
    </section>
  );
}
