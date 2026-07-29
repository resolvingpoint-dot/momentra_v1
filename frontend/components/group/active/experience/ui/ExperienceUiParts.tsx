"use client";

import type { CSSProperties, ReactNode } from "react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { PullToRefresh } from "@/components/shared/PullToRefresh";
import { WidgetInfoButton } from "@/components/personal/shared/WidgetInfoButton";
import { groupSectionLabel } from "@/lib/group/groupTypography";
import { MaterialIcon } from "./MaterialIcon";

export function SectionLabel({
  children,
  icon,
  action,
  onAction,
  explainerId,
  momentTypeCode,
}: {
  children: ReactNode;
  icon?: string;
  action?: string;
  onAction?: () => void;
  explainerId?: string;
  momentTypeCode?: string | null;
}) {
  const tokens = useThemeTokens();
  return (
    <div className="mb-4 flex items-center justify-between">
      <div className="flex items-center gap-2">
        {icon && <MaterialIcon name={icon} className="text-[18px]" style={{ color: tokens.colors.brandPrimary }} />}
        <span style={groupSectionLabel(tokens)}>{children}</span>
        {explainerId ? (
          <WidgetInfoButton
            explainerId={explainerId}
            momentTypeCode={momentTypeCode}
            domain="group"
          />
        ) : null}
      </div>
      {action && (
        <button
          type="button"
          onClick={onAction}
          className="text-[10px] font-bold uppercase tracking-wider"
          style={{ color: tokens.colors.brandPrimary }}
        >
          {action}
        </button>
      )}
    </div>
  );
}

export function MetricTile({
  label,
  value,
  chip,
  valueColor,
}: {
  label: string;
  value: string;
  chip?: string;
  valueColor?: string;
}) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  return (
    <div className="rounded-xl p-3" style={{ background: colors.surfaceContainerLow ?? colors.surfaceContainer }}>
      <span className="mb-1 block text-[10px] font-medium uppercase tracking-wider" style={{ color: colors.textSecondary }}>
        {label}
      </span>
      <div className="flex items-center gap-2">
        <span className="text-[32px] font-bold leading-none" style={{ color: valueColor ?? colors.textPrimary }}>
          {value}
        </span>
        {chip && (
          <span
            className="inline-flex items-center gap-0.5 rounded-full px-1.5 py-0.5 text-[10px] uppercase tracking-tighter"
            style={{ background: `${colors.brandPrimary}18`, color: colors.brandPrimary }}
          >
            <MaterialIcon name="trending_up" className="text-[12px]" />
            {chip.replace("↑ ", "")}
          </span>
        )}
      </div>
    </div>
  );
}

export function ChipRow({ chips, variant = "muted" }: { chips: string[]; variant?: "muted" | "primary" }) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  return (
    <div className="flex flex-wrap justify-center gap-2">
      {chips.map((chip) => (
        <span
          key={chip}
          className="rounded-full px-2 py-0.5 text-[10px] uppercase tracking-tighter"
          style={
            variant === "primary"
              ? { background: `${colors.brandPrimary}18`, color: colors.brandPrimary }
              : { background: colors.surfaceContainerHigh ?? colors.surfaceContainer, color: colors.textSecondary }
          }
        >
          {chip}
        </span>
      ))}
    </div>
  );
}

export function HealthRing({ value, label, size = 160 }: { value: number; label: string; size?: number }) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  const stroke = 10;
  const radius = (size - stroke) / 2;
  const circumference = radius * 2 * Math.PI;
  const offset = circumference - (value / 100) * circumference;

  return (
    <div className="relative flex items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} className="-rotate-90">
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={colors.surfaceContainerHigh ?? colors.surfaceContainer}
          strokeWidth={stroke}
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          fill="none"
          stroke={colors.primaryContainer}
          strokeWidth={stroke}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
        />
      </svg>
      <div className="absolute text-center">
        <span className="block text-[32px] font-bold" style={{ color: colors.textPrimary }}>
          {value}%
        </span>
        <span className="text-[10px] uppercase tracking-wider" style={{ color: colors.textSecondary }}>
          {label}
        </span>
      </div>
    </div>
  );
}

type SignalTone = "error" | "tertiary" | "primary";

const toneIcon: Record<SignalTone, string> = {
  error: "hotel",
  tertiary: "payments",
  primary: "how_to_vote",
};

export function SignalRow({
  title,
  tone,
  icon,
  onClick,
}: {
  title: string;
  tone: SignalTone;
  icon?: string;
  onClick?: () => void;
}) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  const toneColor =
    tone === "error" ? colors.error : tone === "tertiary" ? colors.warning ?? colors.brandSecondary : colors.brandPrimary;
  const interactive = Boolean(onClick);

  return (
    <div
      className={`flex items-center gap-4 rounded-xl p-4 transition-transform ${interactive ? "cursor-pointer hover:scale-[1.02]" : ""}`}
      style={{
        background: `${toneColor}14`,
        borderTop: `1px solid ${toneColor}33`,
        borderRight: `1px solid ${toneColor}33`,
        borderBottom: `1px solid ${toneColor}33`,
        borderLeft: `4px solid ${toneColor}`,
      }}
      role={interactive ? "button" : undefined}
      tabIndex={interactive ? 0 : undefined}
      onClick={onClick}
      onKeyDown={
        interactive
          ? (e) => {
              if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                onClick?.();
              }
            }
          : undefined
      }
    >
      <MaterialIcon name={icon ?? toneIcon[tone]} style={{ color: toneColor }} />
      <p className="flex-1 text-sm font-medium" style={{ color: colors.textPrimary }}>
        {title}
      </p>
      {interactive ? <MaterialIcon name="chevron_right" style={{ color: colors.textSecondary }} /> : null}
    </div>
  );
}

export function TimelineRow({
  icon,
  category,
  title,
  time,
  categoryColor,
  onClick,
}: {
  icon: string;
  category: string;
  title: string;
  time: string;
  categoryColor?: string;
  onClick?: () => void;
}) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  const interactive = Boolean(onClick);
  return (
    <div
      className={`group relative z-10 flex gap-4 ${interactive ? "cursor-pointer" : ""}`}
      role={interactive ? "button" : undefined}
      tabIndex={interactive ? 0 : undefined}
      onClick={onClick}
      onKeyDown={
        interactive
          ? (e) => {
              if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                onClick?.();
              }
            }
          : undefined
      }
    >
      <div
        className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full border border-white/10"
        style={{ background: colors.surfaceContainerHigh ?? colors.surfaceContainer }}
      >
        <MaterialIcon name={icon} className="text-[18px]" style={{ color: colors.textPrimary }} />
      </div>
      <div className="min-w-0 flex-1">
        <span className="mb-1 block text-[10px] font-bold uppercase tracking-wider" style={{ color: categoryColor ?? colors.brandPrimary }}>
          {category}
        </span>
        <p className="text-base" style={{ color: colors.textPrimary }}>
          {title}
        </p>
        <p className="text-xs" style={{ color: colors.textSecondary }}>
          {time}
        </p>
      </div>
      <MaterialIcon
        name="chevron_right"
        className="self-center transition-transform group-hover:translate-x-1"
        style={{ color: colors.textSecondary }}
      />
    </div>
  );
}

export function SunsetCta({
  eyebrow,
  title,
  subtitle,
  onClick,
  impacts,
  icon = "bolt",
  explainerId,
  momentTypeCode,
}: {
  eyebrow: string;
  title: string;
  subtitle?: string;
  onClick?: () => void;
  impacts?: string[];
  icon?: string;
  explainerId?: string;
  momentTypeCode?: string | null;
}) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  return (
    <div
      className="group w-full rounded-[24px] transition-all hover:-translate-y-0.5"
      style={{
        background: `linear-gradient(135deg, ${colors.primaryContainer} 0%, ${colors.brandPrimary} 100%)`,
        boxShadow: "0 10px 40px rgba(255,122,61,0.20)",
        color: colors.brandOnPrimary,
      }}
    >
      <div className="flex items-center gap-3 px-5 pt-5">
        <div className="rounded-lg bg-white/20 p-2">
          <MaterialIcon name={icon} className="text-[20px]" />
        </div>
        <span className="min-w-0 flex-1 text-xs font-semibold uppercase tracking-wider">{eyebrow}</span>
        {explainerId ? (
          <WidgetInfoButton
            explainerId={explainerId}
            momentTypeCode={momentTypeCode}
            domain="group"
          />
        ) : null}
      </div>
      <button type="button" onClick={onClick} className="w-full p-5 pt-4 text-left">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-2xl font-bold leading-tight">{title}</p>
            {subtitle ? <p className="mt-1 text-sm opacity-90">{subtitle}</p> : null}
          </div>
          <MaterialIcon name="arrow_forward" className="transition-transform group-hover:translate-x-1" />
        </div>
        {impacts && impacts.length > 0 && (
          <div className="mt-6 border-t border-white/20 pt-4">
            <p className="mb-2 text-[10px] font-bold uppercase tracking-wider opacity-80">Expected Impact</p>
            <div className="flex flex-wrap gap-2">
              {impacts.map((impact) => (
                <span key={impact} className="rounded-lg bg-white/20 px-2 py-1 text-[10px] font-bold uppercase tracking-tighter">
                  {impact}
                </span>
              ))}
            </div>
          </div>
        )}
      </button>
    </div>
  );
}

export function InsightCard({
  title,
  icon,
  tone = "primary",
}: {
  title: string;
  icon: string;
  tone?: "primary" | "secondary" | "tertiary";
}) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  const toneColor =
    tone === "secondary" ? colors.brandSecondary ?? colors.warning : tone === "tertiary" ? colors.warning : colors.brandPrimary;

  return (
    <div
      className="flex flex-col gap-2 rounded-2xl p-4"
      style={{
        background: colors.surfaceContainer,
        border: `1px solid ${toneColor}4D`,
        boxShadow: tone === "primary" ? "0 10px 40px rgba(255,122,61,0.05)" : undefined,
      }}
    >
      <div className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-wider" style={{ color: toneColor }}>
        <MaterialIcon name="auto_awesome" className="animate-pulse text-[14px]" />
        Momentra Insight
      </div>
      <div className="flex items-center gap-3">
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg" style={{ background: `${toneColor}18` }}>
          <MaterialIcon name={icon} style={{ color: toneColor }} />
        </div>
        <p className="text-sm" style={{ color: colors.textPrimary }}>
          {title}
        </p>
      </div>
    </div>
  );
}

export function ProgressBar({ percent }: { percent: number }) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  const clamped = Math.max(0, Math.min(100, percent));
  return (
    <div
      className="h-1 w-full overflow-hidden rounded-full"
      style={{ background: colors.surfaceContainerHigh ?? colors.surfaceContainer }}
      role="progressbar"
      aria-valuenow={clamped}
      aria-valuemin={0}
      aria-valuemax={100}
    >
      <div
        className="h-full rounded-full transition-[width] duration-300"
        style={{
          width: `${clamped}%`,
          background: `linear-gradient(90deg, ${colors.primaryContainer}, ${colors.brandPrimary})`,
        }}
      />
    </div>
  );
}

export function ExperienceScrollShell({
  children,
  bottomPadding = 0,
  className,
  style,
  onRefresh,
}: {
  children: ReactNode;
  bottomPadding?: number;
  className?: string;
  style?: CSSProperties;
  onRefresh?: () => void | Promise<void>;
}) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  const contentPad = bottomPadding || tokens.spacing.md;
  const shellStyle: CSSProperties = {
    background: colors.background,
    color: colors.textPrimary,
    ...style,
  };
  const inner = (
    <div
      className="mx-auto w-full max-w-[600px] space-y-6 px-5 py-4 md:max-w-[1080px] md:px-20 md:py-6"
      style={{ paddingBottom: contentPad }}
    >
      {children}
    </div>
  );

  if (onRefresh) {
    return (
      <div
        data-momentra-context="group"
        className={["relative flex min-h-0 flex-1 flex-col", className].filter(Boolean).join(" ")}
        style={shellStyle}
      >
        <PullToRefresh onRefresh={onRefresh}>{inner}</PullToRefresh>
      </div>
    );
  }

  return (
    <div
      data-momentra-context="group"
      className={["relative min-h-0 flex-1 overflow-y-auto", className].filter(Boolean).join(" ")}
      style={shellStyle}
    >
      {inner}
    </div>
  );
}
