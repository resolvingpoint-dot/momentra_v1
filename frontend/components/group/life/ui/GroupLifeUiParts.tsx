"use client";

import type { ReactNode } from "react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { GroupLifeGraphVisual } from "@/components/group/shared/GroupLifeGraphVisual";
import { ExperienceGlassCard } from "@/components/group/active/experience/ui/ExperienceGlassCard";
import { MaterialIcon } from "@/components/group/active/experience/ui/MaterialIcon";
import { WidgetInfoButton } from "@/components/personal/shared/WidgetInfoButton";
import { groupSectionLabel } from "@/lib/group/groupTypography";
import type {
  GroupLifeBalanceDimension,
  GroupLifeDriver,
  GroupLifeDriftAlert,
  GroupLifeEvolutionSeries,
  GroupLifeHealthHero,
  GroupLifeIntelligence,
  GroupLifeJourneyItem,
  GroupLifeLeverage,
  GroupLifeMetrics,
  GroupLifeMonthlyChange,
  GroupLifeQuickAction,
} from "@/lib/api/groupLife";
import type { ContextThemeTokens } from "@/lib/contextTokens";

export function lifeColorToken(tokens: ContextThemeTokens, token: string): string {
  const { colors } = tokens;
  switch (token) {
    case "primary_container":
      return colors.primaryContainer ?? colors.brandPrimary;
    case "secondary":
      return colors.brandSecondary ?? colors.secondary ?? colors.brandPrimary;
    case "tertiary":
      return colors.warning ?? colors.brandPrimary;
    case "indigo":
      return "#818CF8";
    default:
      return colors.brandPrimary;
  }
}

function SectionHeading({
  children,
  explainerId,
}: {
  children: ReactNode;
  explainerId?: string;
}) {
  const tokens = useThemeTokens();
  return (
    <div className="flex items-center gap-0.5">
      <h3
        className="text-[11px] font-bold uppercase tracking-widest opacity-80"
        style={{ color: tokens.colors.textSecondary }}
      >
        {children}
      </h3>
      {explainerId ? (
        <WidgetInfoButton explainerId={explainerId} domain="group" />
      ) : null}
    </div>
  );
}

export function GroupLifeHeroSection({ health }: { health: GroupLifeHealthHero }) {
  const tokens = useThemeTokens();
  const { colors } = tokens;

  return (
    <section
      className="relative flex min-h-[320px] items-center justify-center overflow-hidden rounded-3xl"
      style={{
        background: `linear-gradient(to bottom, color-mix(in srgb, ${colors.primaryContainer ?? colors.brandPrimary} 8%, transparent), transparent)`,
      }}
    >
      <div className="h-[320px] w-full max-w-md">
        <GroupLifeGraphVisual
          lifeScore={health.life_score}
          deltaMonth={health.delta_month}
          satelliteScores={health.satellite_scores}
        />
      </div>
    </section>
  );
}

export function GroupLifeBalanceSection({ dimensions }: { dimensions: GroupLifeBalanceDimension[] }) {
  const tokens = useThemeTokens();
  if (dimensions.length === 0) return null;

  return (
    <section className="space-y-4">
      <SectionHeading explainerId="LIFE-002">Balance Model</SectionHeading>
      <ExperienceGlassCard>
        <div className="space-y-4">
          {dimensions.map((dim) => {
            const color = lifeColorToken(tokens, dim.badge_color_token);
            return (
              <div key={dim.dimension_code} className="flex items-center gap-3">
                <span className="w-24 text-[10px] font-bold uppercase" style={{ color: tokens.colors.textSecondary }}>
                  {dim.label}
                </span>
                <div className="h-2 flex-1 overflow-hidden rounded-full" style={{ background: "rgba(255,255,255,0.05)" }}>
                  <div className="h-full rounded-full" style={{ width: `${dim.score}%`, background: color }} />
                </div>
                <span className="w-20 text-right text-[10px] font-bold" style={{ color }}>
                  {dim.badge_label}
                </span>
              </div>
            );
          })}
        </div>
      </ExperienceGlassCard>
    </section>
  );
}

export function GroupLifeDriversSection({ drivers }: { drivers: GroupLifeDriver[] }) {
  const tokens = useThemeTokens();
  if (drivers.length === 0) return null;

  return (
    <section className="space-y-3">
      <SectionHeading explainerId="LIFE-003">What Drives Your Group</SectionHeading>
      {drivers.map((driver) => {
        const color = lifeColorToken(tokens, driver.accent_token);
        return (
          <ExperienceGlassCard key={driver.source_type_code}>
            <div className="flex items-start gap-4">
              <div
                className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl"
                style={{ background: `${color}18`, color }}
              >
                <MaterialIcon name={driver.icon} />
              </div>
              <div className="min-w-0 flex-1">
                <div className="flex items-start justify-between gap-2">
                  <h4 className="text-xs font-bold" style={{ color: tokens.colors.textPrimary }}>
                    {driver.title}{" "}
                    <span className="font-normal opacity-60">{driver.relation}</span>
                  </h4>
                  <span className="shrink-0 text-xs font-bold text-green-400">+{driver.impact_percent}%</span>
                </div>
                <p className="mt-1 text-[10px] opacity-80" style={{ color: tokens.colors.textSecondary }}>
                  {driver.body}
                </p>
              </div>
              <span
                className="shrink-0 rounded px-1.5 py-0.5 text-[8px] font-bold uppercase"
                style={{ background: `${color}22`, color }}
              >
                {driver.priority}
              </span>
            </div>
          </ExperienceGlassCard>
        );
      })}
    </section>
  );
}

export function GroupLifeAlertsSection({
  drift,
  leverage,
}: {
  drift: GroupLifeDriftAlert | null;
  leverage: GroupLifeLeverage | null;
}) {
  const tokens = useThemeTokens();
  if (!drift && !leverage) return null;

  return (
    <section className="grid grid-cols-1 gap-3 sm:grid-cols-2">
      {drift && (
        <div
          className="space-y-3 rounded-2xl border p-4"
          style={{
            background: `${lifeColorToken(tokens, "primary_container")}10`,
            borderColor: `${lifeColorToken(tokens, "primary_container")}33`,
          }}
        >
          <div className="flex items-center justify-between">
            <span className="text-[9px] font-bold uppercase" style={{ color: lifeColorToken(tokens, "primary_container") }}>
              Group Drift Alert
            </span>
            <MaterialIcon name="warning" className="text-sm" style={{ color: tokens.colors.warning }} />
          </div>
          <p className="text-xs font-bold" style={{ color: tokens.colors.textPrimary }}>{drift.title}</p>
          <p className="text-[10px]" style={{ color: tokens.colors.textSecondary }}>{drift.body}</p>
          <div className="border-t pt-2" style={{ borderColor: `${lifeColorToken(tokens, "primary_container")}22` }}>
            <p className="text-[9px] font-bold uppercase" style={{ color: lifeColorToken(tokens, "primary_container") }}>
              {drift.impact_label}
            </p>
            <p className="text-[10px]" style={{ color: tokens.colors.textSecondary }}>{drift.impact_body}</p>
          </div>
        </div>
      )}
      {leverage && (
        <div
          className="space-y-3 rounded-2xl border p-4"
          style={{
            background: `${tokens.colors.brandPrimary}10`,
            borderColor: `${tokens.colors.brandPrimary}33`,
          }}
        >
          <div className="flex items-center justify-between">
            <span className="flex items-center gap-0.5 text-[9px] font-bold uppercase" style={{ color: tokens.colors.brandPrimary }}>
              Highest Group Leverage
              <WidgetInfoButton explainerId="LIFE-005" domain="group" />
            </span>
            <MaterialIcon name="star" className="text-sm" style={{ color: tokens.colors.brandPrimary }} />
          </div>
          <p className="text-xs font-bold" style={{ color: tokens.colors.textPrimary }}>{leverage.title}</p>
          {leverage.impact_lines.map((line) => (
            <p key={line} className="text-[10px]" style={{ color: tokens.colors.textSecondary }}>
              {line}
            </p>
          ))}
          <div className="flex items-end justify-between border-t pt-2" style={{ borderColor: `${tokens.colors.brandPrimary}22` }}>
            <div>
              <p className="text-[9px]" style={{ color: tokens.colors.textSecondary }}>Impact Score</p>
              <p className="text-lg font-bold" style={{ color: tokens.colors.textPrimary }}>
                {leverage.impact_score} / 100
              </p>
            </div>
            <span
              className="rounded px-2 py-1 text-[8px] font-bold"
              style={{ background: `${tokens.colors.brandPrimary}22`, color: tokens.colors.brandPrimary }}
            >
              {leverage.confidence_label}
            </span>
          </div>
        </div>
      )}
    </section>
  );
}

function Sparkline({ points, color }: { points: GroupLifeEvolutionSeries["points"]; color: string }) {
  if (points.length < 2) return null;
  const values = points.map((p) => p.value);
  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min || 1;
  const d = points
    .map((p, i) => {
      const x = (i / (points.length - 1)) * 100;
      const y = 30 - ((p.value - min) / range) * 24;
      return `${i === 0 ? "M" : "L"}${x},${y}`;
    })
    .join(" ");
  return (
    <svg className="h-12 w-full" viewBox="0 0 100 30" preserveAspectRatio="none">
      <path d={d} fill="none" stroke={color} strokeWidth="2" />
    </svg>
  );
}

export function GroupLifeEvolutionSection({ series }: { series: GroupLifeEvolutionSeries[] }) {
  const tokens = useThemeTokens();
  if (series.length === 0) return null;

  return (
    <section className="space-y-3">
      <SectionHeading explainerId="LIFE-006">Evolution</SectionHeading>
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
        {series.map((item) => {
          const color = lifeColorToken(tokens, item.color_token);
          return (
            <div key={item.dimension_code} className="space-y-2">
              <div className="flex justify-between text-[9px] font-bold uppercase">
                <span style={{ color: tokens.colors.textSecondary }}>{item.label}</span>
                <span style={{ color }}>
                  {item.delta_percent >= 0 ? "+" : ""}
                  {item.delta_percent}%
                </span>
              </div>
              <Sparkline points={item.points} color={color} />
            </div>
          );
        })}
      </div>
    </section>
  );
}

export function GroupLifeMonthlySection({ changes }: { changes: GroupLifeMonthlyChange[] }) {
  const tokens = useThemeTokens();
  if (changes.length === 0) return null;

  return (
    <section className="space-y-3">
      <SectionHeading explainerId="LIFE-007">What Changed This Month</SectionHeading>
      <div className="grid grid-cols-2 gap-2 sm:grid-cols-5">
        {changes.map((change) => {
          const color = lifeColorToken(tokens, change.color_token);
          return (
            <ExperienceGlassCard key={change.change_code} className="!p-2 text-center">
              <p className="mb-1 text-[8px] uppercase" style={{ color: tokens.colors.textSecondary }}>
                {change.label}
              </p>
              <p className="text-xs font-bold" style={{ color }}>
                {change.delta_percent >= 0 ? "+" : ""}
                {change.delta_percent}%
              </p>
            </ExperienceGlassCard>
          );
        })}
      </div>
    </section>
  );
}

export function GroupLifeJourneySection({ journey }: { journey: GroupLifeJourneyItem[] }) {
  const tokens = useThemeTokens();
  if (journey.length === 0) return null;

  return (
    <section className="space-y-4">
      <SectionHeading explainerId="LIFE-008">Group Journey</SectionHeading>
      <div className="relative flex justify-between px-2">
        <div className="absolute left-0 top-4 z-0 h-px w-full bg-white/10" />
        {journey.map((item) => {
          const color = lifeColorToken(tokens, item.accent_token);
          return (
            <div key={item.event_key} className="relative z-10 flex max-w-[4.5rem] flex-col items-center gap-2">
              <div
                className="flex h-8 w-8 items-center justify-center rounded-full border"
                style={{ background: `${color}22`, borderColor: `${color}44`, color }}
              >
                <MaterialIcon name={item.icon} className="text-sm" />
              </div>
              <p className="text-center text-[8px] uppercase leading-tight" style={{ color: tokens.colors.textSecondary }}>
                {item.title}
                {item.subtitle ? ` · ${item.subtitle}` : ""}
              </p>
            </div>
          );
        })}
      </div>
    </section>
  );
}

export function GroupLifeIntelligenceSection({ intelligence }: { intelligence: GroupLifeIntelligence }) {
  const tokens = useThemeTokens();
  const accent = tokens.colors.primaryContainer ?? tokens.colors.brandPrimary;

  return (
    <ExperienceGlassCard
      glow
      className="relative overflow-hidden"
      style={{ background: tokens.colors.surfaceContainer }}
    >
      <div className="mb-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="rounded-xl p-2" style={{ background: `${accent}22`, color: accent }}>
            <MaterialIcon name="psychology" style={{ fontVariationSettings: "'FILL' 1" }} />
          </div>
          <span className="flex items-center gap-0.5" style={groupSectionLabel(tokens)}>
            Momentra Intelligence
            <WidgetInfoButton explainerId="LIFE-009" domain="group" />
          </span>
        </div>
        <span className="rounded-full px-2 py-1 text-[9px] font-bold" style={{ background: `${accent}22`, color: accent }}>
          {intelligence.confidence_label}
        </span>
      </div>
      <p className="mb-4 text-sm font-medium leading-relaxed" style={{ color: tokens.colors.textPrimary }}>
        {intelligence.insight_text}
      </p>
      {intelligence.dimension_pills.length > 0 && (
        <div className="flex flex-wrap gap-2">
          {intelligence.dimension_pills.map((pill) => (
            <span
              key={pill}
              className="rounded px-2 py-1 text-[8px] font-bold uppercase"
              style={{ background: `${tokens.colors.brandPrimary}18`, color: tokens.colors.brandPrimary }}
            >
              {pill}
            </span>
          ))}
        </div>
      )}
    </ExperienceGlassCard>
  );
}

export function GroupLifeQuickActionsSection({
  actions,
  onAction,
}: {
  actions: GroupLifeQuickAction[];
  onAction?: (momentTypeCode: string) => void;
}) {
  const tokens = useThemeTokens();
  if (actions.length === 0) return null;

  return (
    <section className="overflow-x-auto pb-2">
      <div className="flex gap-2">
        {actions.map((action) => {
          const color = lifeColorToken(tokens, action.color_token);
          return (
            <button
              key={action.action_code}
              type="button"
              onClick={() => onAction?.(action.moment_type_code)}
              className="flex shrink-0 items-center gap-2 rounded-full border px-5 py-3 text-xs font-bold transition-transform active:scale-95"
              style={{ background: `${color}18`, borderColor: `${color}44`, color }}
            >
              <MaterialIcon name="add" className="text-sm" />
              {action.label}
            </button>
          );
        })}
      </div>
    </section>
  );
}

export function GroupLifeMetricsView({
  metrics,
  onQuickAction,
}: {
  metrics: GroupLifeMetrics;
  onQuickAction?: (momentTypeCode: string) => void;
}) {
  return (
    <div className="space-y-6">
      <GroupLifeHeroSection health={metrics.life_health} />
      <GroupLifeBalanceSection dimensions={metrics.balance_model.dimensions} />
      <GroupLifeDriversSection drivers={metrics.drivers} />
      <GroupLifeAlertsSection drift={metrics.drift_alert} leverage={metrics.leverage} />
      <GroupLifeEvolutionSection series={metrics.evolution} />
      <GroupLifeMonthlySection changes={metrics.monthly_changes} />
      <GroupLifeJourneySection journey={metrics.journey} />
      <GroupLifeIntelligenceSection intelligence={metrics.intelligence} />
      <GroupLifeQuickActionsSection actions={metrics.quick_actions} onAction={onQuickAction} />
    </div>
  );
}
