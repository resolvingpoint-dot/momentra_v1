"use client";

import { useEffect, useRef, useState } from "react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { PersonalAtmosphericOrbs } from "@/components/personal/empty/shared/PersonalAtmosphericOrbs";
import {
  neuralLineBackground,
  personalGlassCardStyle,
  personalGlowWrapperStyle,
  personalPulseContainerStyle,
  personalTypography,
  scrollShellStyle,
} from "@/components/personal/empty/shared/emptyStyles";
import { PersonalPremiumGlowSection } from "@/components/personal/empty/shared/PersonalGlassGlowSection";
import { ArcGauge } from "@/components/personal/life_operations/pulse/widgets/ArcGauge";
import { DonutChart } from "@/components/personal/life_operations/pulse/widgets/DonutChart";
import { DriverImpactBar } from "@/components/personal/life_operations/pulse/widgets/DriverImpactBar";
import { AxisHealthDonut } from "@/components/personal/life_operations/pulse/widgets/AxisHealthDonut";
import { SegmentShareBar } from "@/components/personal/life_operations/pulse/widgets/SegmentShareBar";
import { TrendLineChart } from "@/components/personal/life_operations/pulse/widgets/TrendLineChart";
import { UtilizationBar } from "@/components/personal/life_operations/pulse/widgets/UtilizationBar";
import { MotionStaggerRoot, MotionSection } from "@/components/shared/MotionStagger";
import { AnimatedNumber } from "@/lib/motion/AnimatedNumber";
import { pressableMotionClass } from "@/lib/motion/pressable";
import { useReducedMotion } from "@/lib/motion/useReducedMotion";
import { AccountsCard } from "@/components/personal/life_operations/accounts/AccountsCard";
import type { PersonalLifeOperationsPulse, PersonalLifeOpsPulseMetrics } from "@/lib/api/personal";
import { lifeOpsPulseCopy } from "@/lib/personal/life_operations/pulse/lifeOpsPulseCopy";
import { quickAddIcon, resolveActivityIcon, SEGMENT_COLORS } from "@/lib/personal/life_operations/pulse/pulseIcons";
import {
  resolveExpenseCategoryColor,
  resolveExpenseCategoryIcon,
  resolveImpactIcon,
} from "@/lib/personal/life_operations/expenseCategoryIcons";
import {
  formatRelativeTime,
  recentActivityContextLine,
  recentActivityMoodLabel,
  recentActivityPrimaryMetric,
  recentActivityTitle,
} from "@/lib/personal/life_operations/pulse/recentActivityDisplay";
import { Brain, Sparkles } from "lucide-react";
import {
  PersonalWidgetSectionHeader,
  WidgetInfoButton,
} from "@/components/personal/shared/WidgetInfoButton";

const MOMENT_TYPE = "LIFE_OPERATIONS";

type LifeOperationsPulseProps = {
  pulse: PersonalLifeOperationsPulse;
  bottomPadding?: number;
  hideScreenHeader?: boolean;
  onQuickAdd?: (action: string) => void;
  onViewAllActivity?: () => void;
  onEditActivity?: (id: string, eventType: string) => void;
  /** Called once when metrics are missing so parent can force-refresh. */
  onRetryLoad?: () => void;
};

function impactColor(direction: string | null | undefined, colors: ReturnType<typeof useThemeTokens>["colors"]) {
  const d = (direction ?? "").toLowerCase();
  if (d === "negative" || d === "down") return colors.error;
  if (d === "neutral") return colors.brandTertiary;
  return colors.brandPrimary;
}

function segmentLabel(seg: { category_id: string; category_name?: string | null }) {
  return seg.category_name?.trim() || seg.category_id.slice(0, 8);
}

function buildStatusPills(metrics: PersonalLifeOpsPulseMetrics) {
  const recovery = metrics.signals.find((s) => s.signal_id === "recovery");
  const pressure = metrics.signals.find((s) => s.signal_id === "pressure");
  const money = metrics.signals.find((s) => s.signal_id === "money");
  const mood = metrics.score_drivers.find((d) => d.driver_id === "mood");
  const pills: Array<{ key: "recoveryRising" | "pressureStable" | "moodImproving" | "budgetStrong"; arrow: string }> = [];
  // No invented trends — only render pills when API provides the signal/driver.
  if (recovery?.trend) {
    pills.push({ key: "recoveryRising", arrow: lifeOpsPulseCopy.trendArrow(recovery.trend) });
  }
  if (pressure?.trend) {
    pills.push({ key: "pressureStable", arrow: lifeOpsPulseCopy.trendArrow(pressure.trend) });
  }
  if (mood) {
    pills.push({ key: "moodImproving", arrow: mood.impact >= 0 ? "↑" : "↓" });
  }
  if (money?.trend) {
    pills.push({ key: "budgetStrong", arrow: lifeOpsPulseCopy.trendArrow(money.trend) });
  }
  return pills;
}

export function LifeOperationsPulse({
  pulse,
  bottomPadding = 0,
  hideScreenHeader = false,
  onQuickAdd,
  onViewAllActivity,
  onEditActivity,
  onRetryLoad,
}: LifeOperationsPulseProps) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  const reducedMotion = useReducedMotion();
  const metrics = pulse.metrics;
  const didAutoRetry = useRef(false);
  const [, setRelativeTick] = useState(0);

  useEffect(() => {
    if (metrics || !onRetryLoad || didAutoRetry.current) return;
    didAutoRetry.current = true;
    const timer = window.setTimeout(() => onRetryLoad(), 400);
    return () => window.clearTimeout(timer);
  }, [metrics, onRetryLoad]);

  useEffect(() => {
    const id = window.setInterval(() => setRelativeTick((n) => n + 1), 60_000);
    return () => window.clearInterval(id);
  }, []);

  if (!metrics) {
    return (
      <div
        data-momentra-context="personal"
        className="relative flex min-h-0 flex-1 flex-col items-center justify-center gap-3"
        style={scrollShellStyle(tokens, bottomPadding)}
      >
        <PersonalAtmosphericOrbs />
        <p style={{ ...personalTypography.bodyMd, opacity: 0.7 }}>Loading your pulse…</p>
        {onRetryLoad ? (
          <button
            type="button"
            onClick={() => onRetryLoad()}
            className="rounded-xl px-6 py-2 text-sm font-semibold"
            style={{
              background: colors.primaryContainer,
              color: colors.brandOnPrimary,
            }}
          >
            Retry
          </button>
        ) : null}
      </div>
    );
  }

  const heroInnerStyle = {
    ...personalGlassCardStyle(tokens),
    ...neuralLineBackground(),
    borderRadius: 20,
    padding: 16,
  };

  const statusPills = buildStatusPills(metrics);
  const dataSufficient = metrics.data_sufficient !== false;
  const hasBudget = metrics.capacity.has_budget ?? metrics.capacity.budget_minor > 0;

  return (
    <div
      data-momentra-context="personal"
      className="relative min-h-0 flex-1 overflow-y-auto"
      style={scrollShellStyle(tokens, bottomPadding)}
    >
      <PersonalAtmosphericOrbs />

      <div style={personalPulseContainerStyle(tokens)}>
        <MotionStaggerRoot animateOnceKey="life-operations-pulse">
        {!hideScreenHeader ? (
        <MotionSection>
        <header>
          <p style={{ ...personalTypography.breadcrumb, color: colors.textSecondary, opacity: 0.6 }}>
            {lifeOpsPulseCopy.screenBreadcrumb}
          </p>
          <h1 style={{ ...personalTypography.screenTitle, color: colors.textPrimary }}>
            {lifeOpsPulseCopy.screenTitle}
          </h1>
        </header>
        </MotionSection>
        ) : null}

        <MotionSection>
        <section style={personalGlowWrapperStyle(tokens)}>
          <div style={heroInnerStyle}>
            <div className="mb-6 flex items-start justify-between">
              <div>
                <div className="flex items-center gap-0.5">
                  <h2 style={{ ...personalTypography.heroTitle, color: colors.textPrimary, fontSize: 22 }}>
                    {lifeOpsPulseCopy.opsIndexTitle}
                  </h2>
                  <WidgetInfoButton explainerId="PULSE-001" momentTypeCode={MOMENT_TYPE} />
                </div>
                <p style={{ fontSize: 48, fontWeight: 800, lineHeight: 1, color: colors.textPrimary }}>
                  {dataSufficient && metrics.ops_index != null ? (
                    <>
                      <AnimatedNumber value={metrics.ops_index} />
                      <span style={{ fontSize: 20, fontWeight: 500, opacity: 0.4 }}>{lifeOpsPulseCopy.opsIndexSuffix}</span>
                    </>
                  ) : (
                    <span>{lifeOpsPulseCopy.dash}</span>
                  )}
                </p>
                {dataSufficient && metrics.ops_index_delta_month != null && metrics.ops_index_delta_month !== 0 ? (
                  <span
                    className="mt-2 inline-flex items-center gap-1 rounded-full px-3 py-1"
                    style={{ background: `${colors.primaryContainer}33`, color: colors.brandPrimary, ...personalTypography.labelSm, fontWeight: 700 }}
                  >
                    ↑ {metrics.ops_index_delta_month} this month
                  </span>
                ) : null}
                <p style={{ ...personalTypography.bodyMd, color: colors.brandPrimary, marginTop: 8 }}>
                  {dataSufficient
                    ? (lifeOpsPulseCopy.statusBands[metrics.status_band] ?? metrics.status_band)
                    : lifeOpsPulseCopy.insufficientDataLabel}
                </p>
              </div>
              <span
                className="rounded-lg border px-2 py-1 uppercase"
                style={{
                  ...personalTypography.labelSm,
                  fontWeight: 700,
                  fontSize: 10,
                  borderColor: `${colors.brandPrimary}44`,
                  color: colors.brandPrimary,
                }}
              >
                {lifeOpsPulseCopy.liveMetricsBadge}
              </span>
            </div>

            <div className="mb-1 flex justify-end">
              <WidgetInfoButton explainerId="PULSE-002" momentTypeCode={MOMENT_TYPE} />
            </div>
            <AxisHealthDonut
              opsIndex={metrics.ops_index}
              axisScores={metrics.axis_scores}
              dataSufficient={dataSufficient}
            />

            <div className="grid grid-cols-2 gap-3 border-t pt-4 sm:grid-cols-4" style={{ borderColor: "rgba(255,255,255,0.08)" }}>
              <div className="col-span-2 flex items-center gap-0.5 sm:col-span-4">
                <p style={{ ...personalTypography.labelSm, textTransform: "uppercase", opacity: 0.5 }}>Capacity</p>
                <WidgetInfoButton explainerId="PULSE-003" momentTypeCode={MOMENT_TYPE} />
              </div>
              <div>
                <p style={{ ...personalTypography.labelSm, textTransform: "uppercase", opacity: 0.5 }}>{lifeOpsPulseCopy.capacityMonthly}</p>
                <p className="text-lg font-semibold sm:text-xl" style={{ color: colors.textPrimary }}>
                  {lifeOpsPulseCopy.formatCapacityMinor(metrics.capacity.budget_minor, hasBudget)}
                </p>
              </div>
              <div>
                <p style={{ ...personalTypography.labelSm, textTransform: "uppercase", opacity: 0.5 }}>{lifeOpsPulseCopy.capacityUsed}</p>
                <p className="text-lg font-semibold sm:text-xl" style={{ color: colors.brandPrimary }}>{lifeOpsPulseCopy.formatInrMinor(metrics.capacity.used_minor)}</p>
              </div>
              <div>
                <p style={{ ...personalTypography.labelSm, textTransform: "uppercase", opacity: 0.5 }}>{lifeOpsPulseCopy.capacityRemaining}</p>
                <p className="text-lg font-semibold sm:text-xl" style={{ color: colors.brandTertiary }}>
                  {lifeOpsPulseCopy.formatCapacityMinor(metrics.capacity.remaining_minor, hasBudget)}
                </p>
              </div>
              <div>
                <p style={{ ...personalTypography.labelSm, textTransform: "uppercase", opacity: 0.5 }}>{lifeOpsPulseCopy.capacityUtilization}</p>
                <p className="text-lg font-semibold sm:text-xl">
                  {hasBudget && metrics.capacity.utilization_percent != null ? (
                    <>
                      <AnimatedNumber value={metrics.capacity.utilization_percent} />%
                    </>
                  ) : (
                    lifeOpsPulseCopy.dash
                  )}
                </p>
                {hasBudget && metrics.capacity.utilization_percent != null ? (
                  <div className="mt-1">
                    <UtilizationBar percent={metrics.capacity.utilization_percent} />
                  </div>
                ) : null}
              </div>
            </div>
          </div>
        </section>
        </MotionSection>

        <MotionSection>
        <section
          className="flex flex-wrap justify-evenly gap-2 px-3 py-2"
          style={{ ...personalGlassCardStyle(tokens), borderRadius: 16 }}
        >
          {metrics.signals.map((signal) => (
            <span key={signal.signal_id} style={{ ...personalTypography.labelSm, fontWeight: 700 }}>
              {lifeOpsPulseCopy.signalLabels[signal.signal_id] ?? signal.signal_id}{" "}
              {lifeOpsPulseCopy.trendArrow(signal.trend)}
            </span>
          ))}
        </section>
        </MotionSection>

        <MotionSection>
        <section style={{ ...personalGlassCardStyle(tokens), borderRadius: 16, padding: 12 }}>
          <PersonalWidgetSectionHeader
            title={lifeOpsPulseCopy.recentActivityFeedTitle}
            explainerId="PULSE-004"
            momentTypeCode={MOMENT_TYPE}
            className="mb-2"
            trailing={
              <button type="button" onClick={onViewAllActivity} style={{ ...personalTypography.labelSm, fontWeight: 700, color: colors.brandPrimary, background: "none", border: "none" }}>
                {lifeOpsPulseCopy.viewAll}
              </button>
            }
          />
          {(pulse.dashboard_card?.recent_items ?? []).length > 0 ? (
            <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
              {(pulse.dashboard_card?.recent_items ?? []).slice(0, 4).map((item) => {
                const Icon = resolveActivityIcon(
                  item.activity_type,
                  item.icon,
                  item.category_code,
                  item.subcategory_code,
                );
                const catColor =
                  resolveExpenseCategoryColor(item.color, item.category_code, item.subcategory_code) ||
                  colors.brandPrimary;
                const context = recentActivityContextLine(item);
                const mood = recentActivityMoodLabel(item);
                const metric = recentActivityPrimaryMetric(item);
                return (
                  <div
                    key={item.id}
                    className="flex items-center gap-3 rounded-xl border p-2.5"
                    style={{ background: "rgba(255,255,255,0.05)", borderColor: "rgba(255,255,255,0.05)" }}
                  >
                    <div
                      className="flex size-9 shrink-0 items-center justify-center rounded-xl"
                      style={{ background: `linear-gradient(160deg, ${catColor}55 0%, ${catColor}22 100%)` }}
                    >
                      <Icon size={16} color={catColor} aria-hidden />
                    </div>
                    <div className="min-w-0 flex-1">
                      <div className="flex items-baseline justify-between gap-2">
                        <p className="truncate" style={{ fontSize: 12, fontWeight: 700 }}>
                          {recentActivityTitle(item)}
                        </p>
                        {metric ? (
                          <span className="shrink-0" style={{ fontSize: 12, fontWeight: 700 }}>
                            {metric}
                          </span>
                        ) : null}
                      </div>
                      <div className="mt-0.5 flex items-center justify-between gap-2">
                        <p className="truncate" style={{ fontSize: 10, opacity: 0.65 }}>
                          {[context, mood].filter(Boolean).join(" · ")}
                        </p>
                        <span className="shrink-0" style={{ fontSize: 10, opacity: 0.45 }}>
                          {formatRelativeTime(item.occurred_at)}
                        </span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <p style={{ ...personalTypography.bodyMd, color: colors.textSecondary, opacity: 0.7 }}>
              {pulse.dashboard_card?.empty_recent_message ?? lifeOpsPulseCopy.recentActivityEmptyFallback}
            </p>
          )}
        </section>
        </MotionSection>

        <MotionSection>
        <section style={{ ...personalGlassCardStyle(tokens), borderRadius: 16, padding: 12 }}>
          <PersonalWidgetSectionHeader title={lifeOpsPulseCopy.financialTitle} explainerId="PULSE-006" momentTypeCode={MOMENT_TYPE} uppercase />
          <div className="mt-3 flex flex-col gap-3 sm:flex-row">
            <div className="mx-auto sm:mx-0">
              <DonutChart
                segments={metrics.financial_segments}
                fallbackTotalMinor={metrics.capacity.used_minor}
              />
            </div>
            <div className="min-w-0 flex-1">
              {metrics.financial_segments.length > 0 ? (
                metrics.financial_segments.map((seg, i) => {
                  const SegIcon = resolveExpenseCategoryIcon(seg.icon, seg.category_id);
                  const segColor =
                    resolveExpenseCategoryColor(seg.color, seg.category_id) ||
                    SEGMENT_COLORS[i % SEGMENT_COLORS.length];
                  return (
                  <div key={seg.category_id} className="mb-3">
                    <div className="flex items-center gap-2" style={personalTypography.labelSm}>
                      <SegIcon size={14} color={segColor} aria-hidden />
                      <span className="min-w-0 flex-1 truncate">{segmentLabel(seg)}</span>
                      <span className="font-bold">
                        {lifeOpsPulseCopy.formatInrMinor(seg.amount_minor)} ({seg.share_percent}%)
                      </span>
                    </div>
                    <div className="mt-1">
                      <SegmentShareBar
                        percent={seg.share_percent}
                        color={segColor}
                      />
                    </div>
                  </div>
                  );
                })
              ) : (
                <p style={{ ...personalTypography.bodyMd, color: colors.textSecondary, opacity: 0.7 }}>
                  {lifeOpsPulseCopy.financialEmptyHint}
                </p>
              )}
            </div>
          </div>
        </section>
        </MotionSection>

        <MotionSection>
        <AccountsCard momentId={pulse.dashboard_card?.moment_id} />
        </MotionSection>

        <MotionSection>
        <section style={{ ...personalGlassCardStyle(tokens), borderRadius: 16, padding: 12 }}>
          <PersonalWidgetSectionHeader title={lifeOpsPulseCopy.trendsTitle} explainerId="PULSE-007" momentTypeCode={MOMENT_TYPE} uppercase />
          <div className="mt-3">
            <TrendLineChart recovery={metrics.trends_30d.recovery} pressure={metrics.trends_30d.pressure} />
          </div>
        </section>
        </MotionSection>

        <MotionSection>
        <section style={{ ...personalGlassCardStyle(tokens), borderRadius: 16, padding: 12 }}>
          <PersonalWidgetSectionHeader title={lifeOpsPulseCopy.scoreDriversTitle} explainerId="PULSE-002" momentTypeCode={MOMENT_TYPE} uppercase />
          {metrics.score_drivers.map((driver) => {
            const barColor = driver.impact < 0 ? colors.error : colors.brandPrimary;
            return (
              <div key={driver.driver_id} className="mt-2 flex items-center gap-2">
                <span className="w-24" style={personalTypography.labelSm}>
                  {lifeOpsPulseCopy.driverLabels[driver.driver_id] ?? driver.driver_id}
                </span>
                <DriverImpactBar impact={driver.impact} />
                <span className="w-8 text-right font-bold" style={{ ...personalTypography.labelSm, color: barColor }}>
                  {driver.impact >= 0 ? `+${driver.impact}` : driver.impact}
                </span>
              </div>
            );
          })}
        </section>
        </MotionSection>

        <MotionSection>
        <section style={{ ...personalGlassCardStyle(tokens), borderRadius: 16, padding: 12, textAlign: "center" }}>
          <PersonalWidgetSectionHeader title={lifeOpsPulseCopy.stateGaugesTitle} explainerId="PULSE-008" momentTypeCode={MOMENT_TYPE} uppercase />
          <div className="mt-3 grid grid-cols-2 gap-2 sm:grid-cols-4">
            {metrics.gauges.map((gauge) => (
              <ArcGauge
                key={gauge.gauge_id}
                gaugeId={gauge.gauge_id}
                percent={gauge.percent}
                label={lifeOpsPulseCopy.gaugeLabels[gauge.gauge_id] ?? gauge.gauge_id}
              />
            ))}
          </div>
        </section>
        </MotionSection>

        <MotionSection>
        <section style={personalGlowWrapperStyle(tokens)}>
          <div
            style={{
              ...personalGlassCardStyle(tokens),
              borderRadius: 20,
              padding: 16,
              border: `2px solid ${colors.brandPrimary}66`,
              background: `linear-gradient(135deg, ${colors.primaryContainer}66, #1a1728)`,
            }}
          >
            <div className="flex flex-col gap-3 sm:flex-row">
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-0.5">
                  <p style={{ ...personalTypography.labelSm, color: colors.brandPrimary, fontWeight: 700, textTransform: "uppercase" }}>
                    {lifeOpsPulseCopy.highPriorityOpportunity}
                  </p>
                  <WidgetInfoButton explainerId="PULSE-009" momentTypeCode={MOMENT_TYPE} />
                </div>
                <h3 style={{ fontSize: 24, fontWeight: 900, color: colors.textPrimary }}>
                  {lifeOpsPulseCopy.opportunityTitles[metrics.opportunity.priority_id] ?? metrics.opportunity.priority_id}
                </h3>
                <p className="mt-2" style={{ ...personalTypography.bodyMd, color: colors.textSecondary }}>
                  {lifeOpsPulseCopy.opportunityBodies[metrics.opportunity.priority_id] ?? ""}
                </p>
                <div className="mt-3 flex flex-wrap gap-2">
                  <span className="rounded-lg px-2 py-1 text-[10px] font-bold" style={{ background: `${colors.error}26`, color: colors.error }}>
                    {lifeOpsPulseCopy.stressImpactLabel(metrics.opportunity.stress_impact)}
                  </span>
                  <span className="rounded-lg px-2 py-1 text-[10px] font-bold" style={{ background: `${colors.brandPrimary}26`, color: colors.brandPrimary }}>
                    {lifeOpsPulseCopy.capacityBoostLabel(metrics.opportunity.capacity_boost)}
                  </span>
                </div>
                <button
                  type="button"
                  onClick={() => onQuickAdd?.("RECOVERY")}
                  className={`mt-3 w-full rounded-xl py-3 font-black ${reducedMotion ? "" : pressableMotionClass}`}
                  style={{ background: colors.brandPrimary, color: "#fff", border: "none", fontSize: 14 }}
                >
                  {lifeOpsPulseCopy.logRecoveryNow}
                </button>
              </div>
              <div
                className="flex size-14 shrink-0 animate-pulse items-center justify-center rounded-full"
                style={{ background: `${colors.brandPrimary}1a`, border: `1px solid ${colors.brandPrimary}1a` }}
              >
                <Sparkles size={28} color={colors.brandPrimary} />
              </div>
            </div>
          </div>
        </section>
        </MotionSection>

        <MotionSection>
        {statusPills.length > 0 ? (
        <section className="flex flex-wrap gap-2">
          {statusPills.map((pill) => {
            const isBudgetStrong = pill.key === "budgetStrong";
            return (
              <div
                key={pill.key}
                className="rounded-full border px-3 py-1.5 text-[10px] font-black uppercase tracking-wider"
                style={{
                  background: isBudgetStrong ? `${colors.brandPrimary}1a` : colors.surfaceContainer,
                  borderColor: isBudgetStrong ? `${colors.brandPrimary}33` : "rgba(255,255,255,0.1)",
                  color: isBudgetStrong ? colors.brandPrimary : colors.textPrimary,
                }}
              >
                {lifeOpsPulseCopy.statusPillLabels[pill.key]} {pill.arrow}
              </div>
            );
          })}
        </section>
        ) : null}
        </MotionSection>

        <MotionSection>
        <PersonalPremiumGlowSection tokens={tokens} cornerRadius={16} innerStyle={{ padding: 12 }}>
          <div className="flex items-center gap-2">
            <div
              className="flex size-10 items-center justify-center rounded-lg"
              style={{ background: `linear-gradient(135deg, ${colors.brandPrimary}, ${colors.brandSecondary})` }}
            >
              <Brain size={18} color="#fff" />
            </div>
            <div>
              <div className="flex items-center gap-0.5">
                <p style={{ ...personalTypography.breadcrumb, color: colors.brandPrimary, opacity: 0.6 }}>
                  {lifeOpsPulseCopy.intelligenceInsightTitle} • {lifeOpsPulseCopy.intelligenceActive}
                </p>
                <WidgetInfoButton explainerId="PULSE-011" momentTypeCode={MOMENT_TYPE} />
              </div>
              <p className="mt-0.5" style={{ ...personalTypography.sectionHeader, color: colors.textPrimary, fontSize: 15 }}>
                {lifeOpsPulseCopy.intelligencePatterns[metrics.intelligence.pattern_id] ??
                  metrics.intelligence.pattern_id}
              </p>
            </div>
          </div>
        </PersonalPremiumGlowSection>
        </MotionSection>

        <MotionSection>
        <section>
          <PersonalWidgetSectionHeader title={lifeOpsPulseCopy.quickAddTitle} explainerId="PULSE-010" momentTypeCode={MOMENT_TYPE} uppercase />
          <div className="mt-3 grid grid-cols-3 gap-2 sm:grid-cols-5 sm:gap-3">
            {lifeOpsPulseCopy.quickAddActions.map((label, index) => {
              const Icon = quickAddIcon(index);
              const actionIds = ["RECOVERY", "COMMITMENT", "REFLECTION", "EXPENSE", "RHYTHM"];
              return (
                <button
                  key={label}
                  type="button"
                  onClick={() => onQuickAdd?.(actionIds[index] ?? "RECOVERY")}
                  className={`flex flex-col items-center gap-2 border-0 bg-transparent p-0 ${reducedMotion ? "" : pressableMotionClass}`}
                >
                  <div
                    className="flex size-14 items-center justify-center rounded-2xl sm:size-16 sm:rounded-3xl"
                    style={{ background: colors.surfaceContainer, border: "1px solid rgba(255,255,255,0.08)" }}
                  >
                    <Icon className="size-6 sm:size-8" color={colors.brandPrimary} />
                  </div>
                  <span className="whitespace-pre-line text-center uppercase" style={{ ...personalTypography.labelSm, fontSize: 9, fontWeight: 700 }}>
                    {label.replace(" ", "\n")}
                  </span>
                </button>
              );
            })}
          </div>
        </section>
        </MotionSection>
        </MotionStaggerRoot>
      </div>
    </div>
  );
}
