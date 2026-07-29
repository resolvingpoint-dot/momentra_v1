"use client";

import type { ReactNode } from "react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { personalGlassCardStyle } from "@/components/personal/empty/shared/emptyStyles";
import { WidgetInfoButton } from "@/components/personal/shared/WidgetInfoButton";

export function DomainGlassSection({
  children,
  className = "",
}: {
  children: ReactNode;
  className?: string;
}) {
  const tokens = useThemeTokens();
  return (
    <div className={`rounded-xl p-3 ${className}`} style={personalGlassCardStyle(tokens)}>
      {children}
    </div>
  );
}

export function DomainSectionHeader({
  title,
  explainerId,
  momentTypeCode,
}: {
  title: string;
  explainerId?: string;
  momentTypeCode?: string | null;
}) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  return (
    <div className="flex items-center gap-0.5">
      <h4 className="text-sm font-semibold tracking-wide" style={{ color: colors.textPrimary }}>
        {title}
      </h4>
      {explainerId ? (
        <WidgetInfoButton explainerId={explainerId} momentTypeCode={momentTypeCode} />
      ) : null}
    </div>
  );
}

export function DomainKvRow({
  label,
  value,
  accent,
}: {
  label: string;
  value: string;
  accent?: string;
}) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  return (
    <div className="mb-1 flex justify-between gap-3 text-sm">
      <span style={{ color: colors.textSecondary }}>{label}</span>
      <span className="text-right font-medium" style={{ color: accent ?? colors.textPrimary }}>
        {value}
      </span>
    </div>
  );
}

export function DomainMetricTile({
  sectionLabel,
  value,
  trend,
  accent,
}: {
  sectionLabel: string;
  value: string;
  trend: string;
  accent: string;
}) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  return (
    <DomainGlassSection>
      <p className="text-[10px] font-bold uppercase tracking-widest opacity-70" style={{ color: colors.textSecondary }}>
        {sectionLabel}
      </p>
      <p className="mt-1 text-2xl font-bold" style={{ color: accent }}>
        {value}
      </p>
      <p className="mt-0.5 text-xs opacity-70" style={{ color: colors.textSecondary }}>
        {trend}
      </p>
    </DomainGlassSection>
  );
}

export function DomainProgressGlow({ percent }: { percent: number }) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  const clamped = Math.max(0, Math.min(100, percent));
  return (
    <div className="relative my-2 h-1.5 overflow-hidden rounded-full" style={{ background: colors.surfaceContainer }}>
      <div
        className="h-full rounded-full transition-all"
        style={{
          width: `${clamped}%`,
          background: `linear-gradient(90deg, ${colors.brandPrimary}, ${colors.brandTertiary})`,
          boxShadow: `0 0 12px ${colors.brandPrimary}66`,
        }}
      />
    </div>
  );
}

export function DomainInsightCard({ title, body }: { title: string; body: string }) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  return (
    <DomainGlassSection>
      <p className="text-sm font-semibold" style={{ color: colors.brandPrimary }}>
        {title}
      </p>
      <p className="mt-1 text-sm leading-relaxed opacity-80" style={{ color: colors.textSecondary }}>
        {body}
      </p>
    </DomainGlassSection>
  );
}

export function DomainIdentityCard({
  badgeLabel,
  title,
  body,
}: {
  badgeLabel: string;
  title: string;
  body: string;
}) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  return (
    <DomainGlassSection>
      <span
        className="mb-1 inline-block rounded-full px-2 py-0.5 text-[10px] font-bold tracking-widest"
        style={{
          color: colors.brandPrimary,
          background: `color-mix(in srgb, ${colors.brandPrimary} 12%, transparent)`,
        }}
      >
        {badgeLabel.toUpperCase()}
      </span>
      <h3 className="text-base font-semibold">{title}</h3>
      <p className="mt-1 text-sm leading-relaxed opacity-80" style={{ color: colors.textSecondary }}>
        {body}
      </p>
    </DomainGlassSection>
  );
}

export function accentFromToken(
  accent: string | null | undefined,
  colors: ReturnType<typeof useThemeTokens>["colors"],
): string | undefined {
  if (accent === "error") return colors.error;
  if (accent === "tertiary") return colors.brandTertiary;
  if (accent === "secondary") return colors.brandSecondary ?? colors.brandTertiary;
  if (accent === "primary") return colors.brandPrimary;
  return undefined;
}
