"use client";

import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { WidgetInfoButton } from "@/components/personal/shared/WidgetInfoButton";
import {
  memoryMicroLabelStyle,
  neuralLineBackground,
  personalGlassInnerStyle,
  personalGlowWrapperStyle,
  personalTypography,
} from "@/components/personal/empty/shared/emptyStyles";
import type { PersonalLifeOpsIdentitySnapshot } from "@/lib/api/personal";
import { lifeOpsMemoryCopy, type PersonalMemoryCopy } from "@/lib/personal/life_operations/memory/lifeOpsMemoryCopy";

type Props = {copy?: PersonalMemoryCopy;  snapshot: PersonalLifeOpsIdentitySnapshot; momentTypeCode?: string | null };

export function IdentitySnapshotSection({ snapshot, copy, momentTypeCode = "LIFE_OPERATIONS" }: Props) {
  const tokens = useThemeTokens();
  const memoryCopy = copy ?? lifeOpsMemoryCopy;
  const { colors } = tokens;

  return (
    <section style={personalGlowWrapperStyle(tokens, 16)}>
      <div
        style={personalGlassInnerStyle(tokens, 16, {
          position: "relative",
          overflow: "hidden",
        })}
      >
        <div
          aria-hidden
          style={{
            position: "absolute",
            inset: 0,
            ...neuralLineBackground(),
            pointerEvents: "none",
          }}
        />
        <div style={{ position: "relative", padding: tokens.spacing.lg }}>
          <div className="flex items-start justify-between gap-3">
            <div>
              <div className="flex items-center gap-0.5">
              <p style={memoryMicroLabelStyle(tokens)}>{memoryCopy.sectionLabels.identity}</p>
              <WidgetInfoButton explainerId="MEMORY-001" momentTypeCode={momentTypeCode} />
            </div>
              <h2 style={{ ...personalTypography.screenTitle, color: colors.textPrimary, marginTop: 4 }}>
                {snapshot.title}
              </h2>
              <p
                style={{
                  ...personalTypography.labelSm,
                  color: colors.brandPrimary,
                  marginTop: 4,
                  fontWeight: 700,
                }}
              >
                {snapshot.trend_label}
              </p>
            </div>
            <div className="text-right">
              <p style={{ ...personalTypography.labelSm, opacity: 0.6, textTransform: "uppercase" }}>
                {memoryCopy.confidenceLabel}
              </p>
              <p style={{ fontSize: 28, fontWeight: 700, color: colors.brandPrimary }}>
                {snapshot.confidence_percent}%
              </p>
            </div>
          </div>
          <div className="mt-3 flex items-center gap-3">
            <p style={{ ...personalTypography.bodyMd, color: colors.textSecondary, flex: 2 }}>{snapshot.body}</p>
            {snapshot.image_url ? (
              <div className="relative w-1/3 max-w-[120px] shrink-0">
                <div
                  aria-hidden
                  className="absolute inset-0 rounded-2xl blur-2xl"
                  style={{ background: `${colors.brandPrimary}33` }}
                />
                <img
                  src={snapshot.image_url}
                  alt=""
                  className="relative rounded-2xl object-cover"
                  style={{ width: "100%", aspectRatio: "1" }}
                />
              </div>
            ) : null}
          </div>
        </div>
      </div>
    </section>
  );
}

