"use client";

import { useEffect } from "react";
import { Activity } from "lucide-react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { GroupSkeletonBlocks } from "@/components/group/shared/skeleton/GroupSkeletonBlocks";
import { GroupFadeSections } from "@/components/group/shared/GroupFadeSections";
import { useGroupLivingPulse, useGroupPulse, useGroupPurchasePulse, useGroupTripPulse } from "@/hooks/useGroupTabCache";
import {
  attentionActionOpensActivity,
  mapAttentionActionToQuickAddId,
} from "@/lib/action-center/mapAttentionAction";
import { ExperienceGlassCard } from "./ui/ExperienceGlassCard";
import { MaterialIcon } from "./ui/MaterialIcon";
import { tripStitchShellStyle, tripStitchTheme } from "./ui/tripStitchTheme";
import {
  HealthRing,
  MetricTile,
  ProgressBar,
  SectionLabel,
  SignalRow,
  SunsetCta,
  TimelineRow,
  ExperienceScrollShell,
} from "./ui/ExperienceUiParts";

export type GroupPulseTemplate = "experience" | "purchase" | "living";

function templateToMomentType(template: GroupPulseTemplate): string {
  if (template === "purchase") return "SHARED_PURCHASE";
  if (template === "living") return "SHARED_LIVING";
  return "SHARED_EXPERIENCE";
}

function attentionSignalClick(
  action: string | undefined,
  template: GroupPulseTemplate,
  onViewAllActivity?: () => void,
  onQuickAdd?: (actionId?: string) => void,
): (() => void) | undefined {
  if (attentionActionOpensActivity(action)) {
    return onViewAllActivity ?? (() => onQuickAdd?.());
  }
  const actionId = mapAttentionActionToQuickAddId(action, templateToMomentType(template));
  if (!onQuickAdd) return onViewAllActivity;
  return () => onQuickAdd(actionId ?? undefined);
}

type ExperiencePulseProps = {
  momentId: string;
  onQuickAdd: (actionId?: string) => void;
  bottomPadding?: number;
  reloadKey?: number;
  template?: GroupPulseTemplate;
  onViewAllActivity?: () => void;
  onEditActivity?: (id: string, eventType: string) => void;
};

function metricLabels(template: GroupPulseTemplate) {
  if (template === "purchase") {
    return {
      icon: "shopping_bag",
      health: "Purchase Health",
      readiness: "Funding Progress",
      m1: "Contributors",
      m2: "Target",
      m3: "Collected",
      m4: "Remaining",
      m5: "Spent",
      m6: "Progress",
      footer: "Days to goal",
    };
  }
  if (template === "living") {
    return {
      icon: "home",
      health: "Home Health",
      readiness: "Contributions Coverage",
      m1: "Residents",
      m2: "Monthly Spend",
      m3: "Contributions",
      m4: "Open Tasks",
      m5: "Spent",
      m6: "Balance",
      footer: "Days in cycle",
    };
  }
  return {
    icon: "beach_access",
    health: "Experience Health",
    readiness: "Experience Readiness",
    m1: "Participants",
    m2: "Bookings",
    m3: "Activities",
    m4: "Budget",
    m5: "Spent",
    m6: "Readiness",
    footer: "Days Remaining",
  };
}

function formatMinor(minor: unknown, currency = "INR"): string | null {
  const n = Number(minor);
  if (!Number.isFinite(n)) return null;
  try {
    return new Intl.NumberFormat("en-IN", { style: "currency", currency, maximumFractionDigits: 0 }).format(n / 100);
  } catch {
    return `${(n / 100).toFixed(0)}`;
  }
}

function asRecord(v: unknown): Record<string, unknown> {
  return v && typeof v === "object" ? (v as Record<string, unknown>) : {};
}

/** Honest empty — never invent metrics. */
function EmptySection({ label }: { label: string }) {
  const { colors } = useThemeTokens();
  return (
    <p className="py-2 text-sm" style={{ color: colors.textSecondary }}>
      {label}
    </p>
  );
}

export function ExperiencePulse({
  momentId,
  onQuickAdd,
  bottomPadding = 0,
  reloadKey = 0,
  template = "experience",
  onViewAllActivity,
  onEditActivity,
}: ExperiencePulseProps) {
  const isTrip = template === "experience";
  const isPurchase = template === "purchase";
  const isLiving = template === "living";
  const tripHook = useGroupTripPulse(isTrip ? momentId : null, isTrip);
  const purchaseHook = useGroupPurchasePulse(isPurchase ? momentId : null, isPurchase);
  const livingHook = useGroupLivingPulse(isLiving ? momentId : null, isLiving);
  const activeHook = useGroupPulse(!isTrip && !isPurchase && !isLiving ? momentId : null, !isTrip && !isPurchase && !isLiving);
  const loading = isTrip
    ? tripHook.loading
    : isPurchase
      ? purchaseHook.loading
      : isLiving
        ? livingHook.loading
        : activeHook.loading;
  const refreshing = isTrip
    ? tripHook.refreshing
    : isPurchase
      ? purchaseHook.refreshing
      : isLiving
        ? livingHook.refreshing
        : activeHook.refreshing;
  const error = isTrip
    ? tripHook.error
    : isPurchase
      ? purchaseHook.error
      : isLiving
        ? livingHook.error
        : activeHook.error;
  const reload = isTrip
    ? tripHook.reload
    : isPurchase
      ? purchaseHook.reload
      : isLiving
        ? livingHook.reload
        : activeHook.reload;
  const tripData = tripHook.data;
  const purchaseData = purchaseHook.data;
  const livingData = livingHook.data;
  const data = isTrip || isPurchase || isLiving ? null : activeHook.data;
  const tokens = useThemeTokens();
  const { colors } = tokens;
  const labels = metricLabels(template);
  const momentTypeCode = templateToMomentType(template);

  useEffect(() => {
    if (reloadKey > 0) void reload();
  }, [reloadKey, reload]);

  if (loading && !data && !tripData && !purchaseData && !livingData) {
    return (
      <ExperienceScrollShell bottomPadding={bottomPadding} onRefresh={reload}>
        <GroupSkeletonBlocks variant="pulse" />
      </ExperienceScrollShell>
    );
  }

  if (error && !data && !tripData && !purchaseData && !livingData) {
    return (
      <div className="flex flex-col items-center justify-center p-10 text-center">
        <Activity size={40} style={{ color: colors.textSecondary }} aria-hidden />
        <p className="mt-3 text-sm" style={{ color: colors.textSecondary }}>
          {error || "Unable to load this section."}
        </p>
        <button type="button" className="mt-3 text-sm font-semibold underline" onClick={() => void reload()}>
          Retry
        </button>
      </div>
    );
  }

  if (isPurchase && purchaseData) {
    const stats = purchaseData.stats;
    const currency = purchaseData.currency_code ?? "INR";
    const healthScore = Math.round(purchaseData.experience_health_percent ?? purchaseData.readiness_score ?? 0);
    const fundingPct = Math.round(purchaseData.funding_percent ?? purchaseData.readiness_score ?? 0);
    const signals = (purchaseData.attention_items ?? []).map((item) => ({
      title: item.title,
      tone: (item.accent === "error" ? "error" : item.accent === "tertiary" ? "tertiary" : "primary") as
        | "error"
        | "tertiary"
        | "primary",
      icon: item.icon,
      onClick: attentionSignalClick(item.action, "purchase", onViewAllActivity, onQuickAdd),
    }));
    const recentActivities = (
      purchaseData.dashboard_card?.recent_items ??
      purchaseData.recent_activity ??
      []
    ).map((item) => ({
      id: item.id,
      icon: "history",
      category: item.subtitle ?? "",
      title: item.title,
      time: item.relative_time ?? "",
    }));
    const breakdown = purchaseData.participation_breakdown ?? { active: 0, pending: 0, inactive: 0 };
    const participationPct = Math.round(purchaseData.participation_percent ?? 0);

    return (
      <ExperienceScrollShell bottomPadding={bottomPadding} style={tripStitchShellStyle} onRefresh={reload}>
        <GroupFadeSections skipEntrance={refreshing}>
          <ExperienceGlassCard glow>
            <h2 className="text-2xl font-semibold" style={{ color: tripStitchTheme.onSurface }}>
              {purchaseData.moment_name}
            </h2>
            <div className="mt-4 grid grid-cols-2 gap-4">
              <MetricTile label="Contributors" value={String(purchaseData.contributor_count ?? stats.contributors_joined ?? 0)} />
              <MetricTile label="Target" value={formatMinor(purchaseData.target_amount_minor, currency) ?? "—"} />
              <MetricTile
                label="Collected"
                value={formatMinor(purchaseData.funded_amount_minor, currency) ?? "—"}
                valueColor={tripStitchTheme.primary}
              />
              <MetricTile label="Remaining" value={formatMinor(purchaseData.amount_remaining_minor, currency) ?? "—"} />
            </div>
          </ExperienceGlassCard>
          <ExperienceGlassCard>
            <HealthRing value={healthScore} label={labels.health} />
            <div className="mt-4 flex flex-wrap gap-2">
              {(purchaseData.health_dimensions ?? []).map((dim) => (
                <span
                  key={dim.label}
                  className="rounded-full px-3 py-1 text-[10px] font-bold uppercase"
                  style={{ background: tripStitchTheme.surfaceContainerHigh, color: tripStitchTheme.onSurfaceVariant }}
                >
                  {dim.label} {dim.status ?? `${Math.round(dim.percent)}%`}
                </span>
              ))}
            </div>
          </ExperienceGlassCard>
          {signals.length > 0 ? (
            <div>
              <SectionLabel icon="warning" explainerId="PULSE-006" momentTypeCode={momentTypeCode}>Attention Signals</SectionLabel>
              {signals.map((s) => (
                <SignalRow key={s.title} icon={s.icon} title={s.title} tone={s.tone} onClick={s.onClick} />
              ))}
            </div>
          ) : null}
          <ExperienceGlassCard>
            <SectionLabel explainerId="PULSE-004" momentTypeCode={momentTypeCode}>{labels.readiness}</SectionLabel>
            <ProgressBar percent={fundingPct} />
          </ExperienceGlassCard>
          <ExperienceGlassCard>
            <p className="text-2xl font-bold" style={{ color: tripStitchTheme.primary }}>
              {participationPct}%
            </p>
            <p className="text-xs" style={{ color: tripStitchTheme.onSurfaceVariant }}>
              Active {breakdown.active} · Pending {breakdown.pending} · Inactive {breakdown.inactive}
            </p>
          </ExperienceGlassCard>
          {recentActivities.length > 0 ? (
            <div>
              <SectionLabel action="View All" explainerId="PULSE-007" momentTypeCode={momentTypeCode}>Recent Activity</SectionLabel>
              {recentActivities.map((item, index) => (
                <TimelineRow
                  key={item.id || `activity-${index}`}
                  icon={item.icon}
                  category={item.category}
                  title={item.title}
                  time={item.time}
                />
              ))}
            </div>
          ) : null}
          {purchaseData.next_best_action ? (
            <SunsetCta
              eyebrow="Next Best Action"
              title={purchaseData.next_best_action.title}
              subtitle={purchaseData.next_best_action.subtitle}
              icon="bolt"
              onClick={onQuickAdd} explainerId="PULSE-008" momentTypeCode={momentTypeCode} />
          ) : null}
          {(purchaseData.insights ?? []).length > 0 ? (
            <div className="grid gap-3">
              <SectionLabel explainerId="PULSE-009" momentTypeCode={momentTypeCode}>
                AI Insights
              </SectionLabel>
              {purchaseData.insights!.map((insight) => (
                <ExperienceGlassCard key={insight.id} className="!p-4">
                  <p className="font-semibold" style={{ color: tripStitchTheme.onSurface }}>
                    {insight.title}
                  </p>
                  {insight.subtitle ? (
                    <p className="text-sm" style={{ color: tripStitchTheme.onSurfaceVariant }}>
                      {insight.subtitle}
                    </p>
                  ) : null}
                </ExperienceGlassCard>
              ))}
            </div>
          ) : null}
        </GroupFadeSections>
      </ExperienceScrollShell>
    );
  }

  if (isLiving && livingData) {
    const stats = livingData.stats;
    const currency = livingData.currency_code ?? "INR";
    const healthScore = Math.round(
      livingData.experience_health_percent ?? livingData.health_percent ?? livingData.readiness_score ?? 0,
    );
    const coveragePct = Math.round(
      livingData.operations_progress?.percent ??
        (livingData.expenses_total_minor && livingData.expenses_total_minor > 0
          ? ((livingData.contributions_total_minor ?? 0) / livingData.expenses_total_minor) * 100
          : livingData.readiness_score ?? 0),
    );
    const signals = (livingData.attention_items ?? []).map((item) => ({
      title: item.title,
      tone: (item.accent === "error" ? "error" : item.accent === "tertiary" ? "tertiary" : "primary") as
        | "error"
        | "tertiary"
        | "primary",
      icon: item.icon,
      onClick: attentionSignalClick(item.action, "living", onViewAllActivity, onQuickAdd),
    }));
    const recentActivities = (
      livingData.dashboard_card?.recent_items ??
      livingData.recent_activity ??
      []
    ).map((item) => ({
      id: item.id,
      activityType: item.activity_type ?? "UPDATE",
      icon: item.icon ?? "history",
      category: item.subtitle ?? "",
      title: item.title,
      time: item.relative_time ?? "",
    }));
    const breakdown = livingData.participation_breakdown ?? { active: 0, pending: 0, inactive: 0 };
    const participationPct = Math.round(livingData.participation_percent ?? 0);

    return (
      <ExperienceScrollShell bottomPadding={bottomPadding} style={tripStitchShellStyle} onRefresh={reload}>
        <GroupFadeSections skipEntrance={refreshing}>
          <ExperienceGlassCard glow>
            <h2 className="text-2xl font-semibold" style={{ color: tripStitchTheme.onSurface }}>
              {livingData.moment_name}
            </h2>
            <div className="mt-4 grid grid-cols-2 gap-4">
              <MetricTile label="Residents" value={String(livingData.resident_count ?? stats.residents_joined ?? 0)} />
              <MetricTile
                label="Monthly Spend"
                value={formatMinor(livingData.expenses_total_minor ?? stats.total_expenses_minor, currency) ?? "—"}
              />
              <MetricTile
                label="Contributions"
                value={formatMinor(livingData.contributions_total_minor ?? stats.contributions_minor, currency) ?? "—"}
                valueColor={tripStitchTheme.primary}
              />
              <MetricTile label="Open Tasks" value={String(stats.tasks_open ?? 0)} />
            </div>
          </ExperienceGlassCard>
          <ExperienceGlassCard>
            <HealthRing value={healthScore} label={labels.health} />
            <div className="mt-4 flex flex-wrap gap-2">
              {(livingData.health_dimensions ?? []).map((dim) => (
                <span
                  key={dim.label}
                  className="rounded-full px-3 py-1 text-[10px] font-bold uppercase"
                  style={{ background: tripStitchTheme.surfaceContainerHigh, color: tripStitchTheme.onSurfaceVariant }}
                >
                  {dim.label} {dim.status ?? `${Math.round(dim.percent)}%`}
                </span>
              ))}
            </div>
          </ExperienceGlassCard>
          {signals.length > 0 ? (
            <div>
              <SectionLabel icon="warning" explainerId="PULSE-006" momentTypeCode={momentTypeCode}>Attention Signals</SectionLabel>
              {signals.map((s) => (
                <SignalRow key={s.title} icon={s.icon} title={s.title} tone={s.tone} onClick={s.onClick} />
              ))}
            </div>
          ) : null}
          <ExperienceGlassCard>
            <SectionLabel explainerId="PULSE-004" momentTypeCode={momentTypeCode}>{labels.readiness}</SectionLabel>
            <ProgressBar percent={Math.min(100, Math.max(0, coveragePct))} />
          </ExperienceGlassCard>
          <ExperienceGlassCard>
            <p className="text-2xl font-bold" style={{ color: tripStitchTheme.primary }}>
              {participationPct}%
            </p>
            <p className="text-xs" style={{ color: tripStitchTheme.onSurfaceVariant }}>
              Active {breakdown.active} · Pending {breakdown.pending} · Inactive {breakdown.inactive}
            </p>
          </ExperienceGlassCard>
          {recentActivities.length > 0 ? (
            <div>
              <SectionLabel action="View All" onAction={onViewAllActivity} explainerId="PULSE-007" momentTypeCode={momentTypeCode}>
                Recent Activity
              </SectionLabel>
              {recentActivities.map((item, index) => (
                <TimelineRow
                  key={item.id || `activity-${index}`}
                  icon={item.icon}
                  category={item.category}
                  title={item.title}
                  time={item.time}
                  onClick={
                    item.id && onEditActivity
                      ? () => onEditActivity(item.id!, item.activityType)
                      : onViewAllActivity
                  }
                />
              ))}
            </div>
          ) : null}
          {livingData.next_best_action ? (
            <SunsetCta
              eyebrow="Next Best Action"
              title={livingData.next_best_action.title}
              subtitle={livingData.next_best_action.subtitle}
              icon="bolt"
              onClick={onQuickAdd} explainerId="PULSE-008" momentTypeCode={momentTypeCode} />
          ) : null}
          {(livingData.insights ?? []).length > 0 ? (
            <div className="grid gap-3">
              <SectionLabel explainerId="PULSE-009" momentTypeCode={momentTypeCode}>
                AI Insights
              </SectionLabel>
              {livingData.insights!.map((insight) => (
                <ExperienceGlassCard key={insight.id} className="!p-4">
                  <p className="font-semibold" style={{ color: tripStitchTheme.onSurface }}>
                    {insight.title}
                  </p>
                  {insight.subtitle ? (
                    <p className="text-sm" style={{ color: tripStitchTheme.onSurfaceVariant }}>
                      {insight.subtitle}
                    </p>
                  ) : null}
                </ExperienceGlassCard>
              ))}
            </div>
          ) : null}
        </GroupFadeSections>
      </ExperienceScrollShell>
    );
  }

  if (isTrip && tripData) {
    const stats = tripData.stats;
    const currency = stats.total_expenses_currency ?? stats.contributions_currency ?? "INR";
    const members = Math.max(stats.guests_joined ?? 0, stats.participants_joined ?? 0);
    const healthScore = Math.round(tripData.experience_health_percent ?? tripData.readiness_score ?? 0);
    const readinessPct = Math.round(tripData.readiness_score ?? 0);
    const budgetLabel = formatMinor(stats.total_budget_minor, currency) ?? "—";
    const spentLabel = formatMinor(stats.total_expenses_minor, currency) ?? "—";
    const signals = (tripData.attention_items ?? []).map((item) => ({
      title: item.title,
      tone: (item.accent === "error" ? "error" : item.accent === "tertiary" ? "tertiary" : "primary") as "error" | "tertiary" | "primary",
      icon: item.icon,
      onClick: attentionSignalClick(item.action, "experience", onViewAllActivity, onQuickAdd),
    }));
    const recentActivities = (tripData.dashboard_card?.recent_items ?? []).map((item) => ({
      id: item.id,
      icon: "history",
      category: item.subtitle ?? item.activity_type ?? "",
      title: item.title,
      time: item.relative_time ?? "",
      activityType: item.activity_type ?? "UPDATE",
    }));
    const breakdown = tripData.participation_breakdown ?? { active: 0, pending: 0, inactive: 0 };
    const participationPct = Math.round(tripData.participation_percent ?? 0);
    const updatedLabel = stats.updated_at_display?.label;
    const healthDims = tripData.health_dimensions ?? [];
    const nba = tripData.next_best_action;

    return (
      <ExperienceScrollShell bottomPadding={bottomPadding} style={tripStitchShellStyle} onRefresh={reload}>
        <GroupFadeSections skipEntrance={refreshing}>
          <ExperienceGlassCard glow>
            <div className="mb-4 flex items-center gap-2">
              <MaterialIcon name={labels.icon} style={{ color: tripStitchTheme.primary }} />
              <h2 className="text-2xl font-semibold" style={{ color: tripStitchTheme.onSurface }}>{tripData.trip_name}</h2>
            </div>
            <div className="mt-4 grid grid-cols-2 gap-4 lg:grid-cols-3">
              <MetricTile label="Participants" value={String(members)} />
              <MetricTile label="Bookings" value={String(stats.confirmed_bookings ?? 0)} />
              <MetricTile label="Activities" value={String(stats.active_plan_items ?? 0)} />
              <MetricTile label="Budget" value={budgetLabel} />
              <MetricTile label="Spent" value={spentLabel} valueColor={tripStitchTheme.primary} />
              <MetricTile label="Readiness" value={`${readinessPct}%`} />
            </div>
            <div className="mt-6 flex items-center justify-between border-t border-white/5 pt-6">
              <span className="text-xs font-medium uppercase tracking-wider" style={{ color: tripStitchTheme.onSurfaceVariant }}>
                {labels.footer}
              </span>
              <span className="text-2xl font-bold" style={{ color: tripStitchTheme.primary }}>
                {tripData.days_remaining != null ? String(tripData.days_remaining) : "—"}
              </span>
              {updatedLabel ? (
                <span className="text-[10px] italic" style={{ color: tripStitchTheme.onSurfaceVariant }}>
                  {updatedLabel}
                </span>
              ) : null}
            </div>
          </ExperienceGlassCard>
          <ExperienceGlassCard>
            <HealthRing value={healthScore} label={labels.health} />
            <div className="mt-4 flex flex-wrap justify-center gap-2">
              {healthDims.length > 0 ? (
                healthDims.map((dim) => (
                  <span
                    key={dim.label}
                    className="rounded-full px-3 py-1 text-[10px] font-bold uppercase"
                    style={{ background: tripStitchTheme.surfaceContainerHigh, color: tripStitchTheme.onSurfaceVariant }}
                  >
                    {dim.label} {dim.status ?? `${Math.round(dim.percent)}%`}
                  </span>
                ))
              ) : (
                <EmptySection label="Health dimensions will appear as the trip progresses." />
              )}
            </div>
          </ExperienceGlassCard>
          <div>
            <SectionLabel icon="warning" explainerId="PULSE-006" momentTypeCode={momentTypeCode}>Attention Signals</SectionLabel>
            {signals.length > 0 ? (
              signals.map((s) => (
                <SignalRow key={s.title} icon={s.icon} title={s.title} tone={s.tone} onClick={s.onClick} />
              ))
            ) : (
              <EmptySection label="No attention signals right now." />
            )}
          </div>
          <ExperienceGlassCard>
            <div className="mb-4 flex items-end justify-between">
              <div>
                <SectionLabel explainerId="PULSE-004" momentTypeCode={momentTypeCode}>{labels.readiness}</SectionLabel>
                <span className="text-2xl font-bold" style={{ color: tripStitchTheme.onSurface }}>{readinessPct}%</span>
              </div>
              <MaterialIcon name="trending_up" style={{ color: tripStitchTheme.primary }} />
            </div>
            <ProgressBar percent={readinessPct} />
            {tripData.readiness_narrative ? (
              <p className="mt-3 text-xs uppercase tracking-tighter" style={{ color: tripStitchTheme.onSurfaceVariant }}>
                {tripData.readiness_narrative}
              </p>
            ) : null}
            {healthDims.length > 0 ? (
              <div className="mt-3 flex flex-wrap gap-1.5">
                {healthDims.map((dim) => (
                  <span
                    key={`ready-${dim.label}`}
                    className="rounded px-1.5 py-0.5 text-[10px] font-medium uppercase"
                    style={{ background: "color-mix(in srgb, #ff7a3d 10%, transparent)", color: tripStitchTheme.primary }}
                  >
                    {dim.label} {Math.round(dim.percent)}%
                  </span>
                ))}
              </div>
            ) : null}
          </ExperienceGlassCard>
          <ExperienceGlassCard>
            <SectionLabel explainerId="PULSE-005" momentTypeCode={momentTypeCode}>Participation</SectionLabel>
            <p className="text-2xl font-bold" style={{ color: tripStitchTheme.primary }}>{participationPct}%</p>
            <div className="mt-4 grid grid-cols-3 gap-2 border-t border-white/5 pt-4">
              {(
                [
                  ["Active", breakdown.active],
                  ["Pending", breakdown.pending],
                  ["Inactive", breakdown.inactive],
                ] as const
              ).map(([label, count]) => (
                <div key={label} className="text-center">
                  <span className="block text-[10px] uppercase tracking-tighter" style={{ color: tripStitchTheme.onSurfaceVariant }}>
                    {label}
                  </span>
                  <span className="font-bold" style={{ color: tripStitchTheme.onSurface }}>{count}</span>
                </div>
              ))}
            </div>
          </ExperienceGlassCard>
          <ExperienceGlassCard>
            <SectionLabel action="View All" onAction={onViewAllActivity} explainerId="PULSE-007" momentTypeCode={momentTypeCode}>
              Recent Activity
            </SectionLabel>
            {recentActivities.length > 0 ? (
              <div className="relative space-y-6 before:absolute before:bottom-2 before:left-[19px] before:top-2 before:w-px before:bg-white/10">
                {recentActivities.map((item, index) => (
                  <TimelineRow
                    key={item.id || `activity-${index}`}
                    icon={item.icon}
                    category={item.category}
                    title={item.title}
                    time={item.time}
                    onClick={
                      item.id && onEditActivity
                        ? () => onEditActivity(item.id!, item.activityType)
                        : onViewAllActivity
                    }
                  />
                ))}
              </div>
            ) : (
              <EmptySection label="No recent activity yet." />
            )}
          </ExperienceGlassCard>
          {nba ? (
            <SunsetCta
              eyebrow="Next Best Action"
              title={nba.title}
              subtitle={nba.subtitle}
              impacts={nba.impact_labels ?? []}
              icon="bolt"
              onClick={onQuickAdd} explainerId="PULSE-008" momentTypeCode={momentTypeCode} />
          ) : null}
          <ExperienceGlassCard>
            <SectionLabel>Budget</SectionLabel>
            <p className="text-lg font-semibold" style={{ color: tripStitchTheme.onSurface }}>
              {Number(stats.total_expenses_minor ?? 0) <= Number(stats.total_budget_minor ?? 0) && Number(stats.total_budget_minor ?? 0) > 0
                ? "Budget under control"
                : Number(stats.total_budget_minor ?? 0) > 0
                  ? "Budget needs attention"
                  : "Set a trip budget"}
            </p>
            <p className="text-sm" style={{ color: tripStitchTheme.onSurfaceVariant }}>
              Spent {spentLabel} of {budgetLabel}
            </p>
          </ExperienceGlassCard>
          {(tripData.insights ?? []).length > 0 ? (
            <div className="grid gap-3">
              <SectionLabel explainerId="PULSE-009" momentTypeCode={momentTypeCode}>
                AI Insights
              </SectionLabel>
              {tripData.insights!.map((insight) => (
                <ExperienceGlassCard key={insight.id} className="!p-4">
                  <p className="font-semibold" style={{ color: tripStitchTheme.onSurface }}>{insight.title}</p>
                  {insight.subtitle ? <p className="text-sm" style={{ color: tripStitchTheme.onSurfaceVariant }}>{insight.subtitle}</p> : null}
                </ExperienceGlassCard>
              ))}
            </div>
          ) : null}
        </GroupFadeSections>
      </ExperienceScrollShell>
    );
  }

  const pulse = asRecord(data?.pulse_data);
  const health = asRecord(data?.health_data);
  const stats = asRecord(pulse.stats ?? data);
  const currency = String(pulse.currency_code ?? stats.currency_code ?? "INR");

  const tripName = data?.moment_name?.trim() || "Untitled moment";
  const healthScore = Math.round(Number(health.health_score ?? pulse.health_score ?? 0));
  const readinessPct = Math.round(
    Number(pulse.completion_percentage ?? pulse.funding_percent ?? stats.funding_percent ?? 0),
  );
  const softRefresh = Boolean(data) && refreshing;

  const members = Number(pulse.active_members ?? pulse.participant_count ?? stats.contributors_joined ?? 0);
  const bookings = Number(pulse.confirmed_bookings ?? stats.confirmed_bookings ?? pulse.vendors ?? stats.vendors ?? 0);
  const activities = Number(pulse.active_tasks ?? stats.plan_items ?? stats.chores ?? 0);
  const budget = formatMinor(pulse.budget_minor ?? pulse.target_amount_minor ?? stats.budget_minor, currency);
  const spent = formatMinor(
    pulse.spent_minor ?? pulse.total_expenses_minor ?? stats.total_expenses_minor ?? stats.expenses_minor,
    currency,
  );
  const remaining = formatMinor(pulse.amount_remaining_minor ?? stats.amount_remaining_minor, currency);
  const collected = formatMinor(pulse.funded_amount_minor ?? pulse.total_contributed_minor, currency);
  const daysRemaining =
    pulse.days_remaining != null && Number.isFinite(Number(pulse.days_remaining))
      ? String(pulse.days_remaining)
      : null;

  const metricValues =
    template === "purchase"
      ? [String(members), budget ?? "—", collected ?? "—", remaining ?? "—", spent ?? "—", `${readinessPct}%`]
      : template === "living"
        ? [String(members), String(activities), String(bookings), budget ?? "—", spent ?? "—", `${readinessPct}%`]
        : [String(members), String(bookings), String(activities), budget ?? "—", spent ?? "—", `${readinessPct}%`];

  const signals =
    data?.signals && data.signals.length > 0
      ? data.signals.slice(0, 3).map((s) => ({
          title: s.signal_title,
          tone: (s.priority === "HIGH"
            ? "error"
            : s.priority === "MEDIUM"
              ? "tertiary"
              : "primary") as "error" | "tertiary" | "primary",
          icon: "warning",
          onClick: onQuickAdd,
        }))
      : [];

  const recentActivities =
    data?.recent_events && data.recent_events.length > 0
      ? data.recent_events.slice(0, 5).map((e) => ({
          id: e.event_id,
          icon: "history",
          category: e.module_code.replace(/_/g, " "),
          title: e.event_action,
          time: e.event_time ? new Date(e.event_time).toLocaleString() : "",
        }))
      : [];

  const nba = data?.recommendations?.[0];
  const nextTitle = nba?.title?.trim() || null;

  const activeCount = Number(pulse.active_participant_count ?? health.active_count ?? members);
  const pendingCount = Number(pulse.pending_participant_count ?? health.pending_count ?? 0);
  const inactiveCount = Number(pulse.inactive_participant_count ?? health.inactive_count ?? 0);
  const participationPct = Math.round(Number(pulse.participation_percent ?? health.participation_percent ?? 0));
  const hasParticipation =
    participationPct > 0 || activeCount > 0 || pendingCount > 0 || inactiveCount > 0;

  return (
    <ExperienceScrollShell bottomPadding={bottomPadding} onRefresh={reload}>
      <GroupFadeSections skipEntrance={softRefresh}>
        <ExperienceGlassCard glow>
          <div className="mb-6 flex items-center gap-2">
            <MaterialIcon name={labels.icon} style={{ color: colors.brandPrimary }} />
            <h2 className="text-2xl font-semibold" style={{ color: colors.textPrimary }}>
              {tripName}
            </h2>
          </div>
          <div className="grid grid-cols-2 gap-4 lg:grid-cols-3">
            <MetricTile label={labels.m1} value={metricValues[0]} />
            <MetricTile label={labels.m2} value={metricValues[1]} />
            <MetricTile label={labels.m3} value={metricValues[2]} />
            <MetricTile label={labels.m4} value={metricValues[3]} />
            <MetricTile label={labels.m5} value={metricValues[4]} />
            <MetricTile label={labels.m6} value={metricValues[5]} />
          </div>
          {daysRemaining != null ? (
            <div className="mt-6 flex items-center justify-between border-t border-white/5 pt-6">
              <span className="text-xs font-medium uppercase tracking-wider" style={{ color: colors.textSecondary }}>
                {labels.footer}
              </span>
              <span className="text-2xl font-bold" style={{ color: colors.brandPrimary }}>
                {daysRemaining}
              </span>
            </div>
          ) : null}
        </ExperienceGlassCard>

        <ExperienceGlassCard>
          <SectionLabel explainerId="PULSE-001" momentTypeCode={momentTypeCode}>{labels.health}</SectionLabel>
          <div className="flex flex-col items-center">
            <HealthRing
              value={healthScore}
              label={String(health.health_status ?? pulse.health_status ?? (healthScore ? "Health" : "No score yet"))}
            />
          </div>
        </ExperienceGlassCard>

        <div className="space-y-3">
          <SectionLabel icon="warning" explainerId="PULSE-006" momentTypeCode={momentTypeCode}>Attention Signals</SectionLabel>
          {signals.length === 0 ? (
            <EmptySection label="No attention signals right now." />
          ) : (
            signals.map((s) => (
              <SignalRow key={s.title} title={s.title} tone={s.tone} icon={s.icon} onClick={s.onClick} />
            ))
          )}
        </div>

        <ExperienceGlassCard>
          <div className="mb-4 flex items-end justify-between">
            <div>
              <SectionLabel explainerId="PULSE-004" momentTypeCode={momentTypeCode}>{labels.readiness}</SectionLabel>
              <span className="text-2xl font-bold" style={{ color: colors.textPrimary }}>
                {readinessPct}%
              </span>
            </div>
            <MaterialIcon name="trending_up" style={{ color: colors.brandPrimary }} />
          </div>
          <ProgressBar percent={readinessPct} />
        </ExperienceGlassCard>

        {hasParticipation ? (
          <ExperienceGlassCard>
            <SectionLabel explainerId="PULSE-005" momentTypeCode={momentTypeCode}>Participation</SectionLabel>
            <div className="mb-4 flex items-center justify-between">
              <span className="text-2xl font-bold" style={{ color: colors.textPrimary }}>
                {participationPct}%
              </span>
            </div>
            <div className="grid grid-cols-3 gap-2 border-t border-white/5 pt-6 min-w-0">
              {(
                [
                  ["active", activeCount],
                  ["pending", pendingCount],
                  ["inactive", inactiveCount],
                ] as const
              ).map(([key, count]) => (
                <div key={key} className="min-w-0 text-center">
                  <span className="block text-[10px] uppercase tracking-tighter break-words" style={{ color: colors.textSecondary }}>
                    {key}
                  </span>
                  <span className="font-bold" style={{ color: colors.textPrimary }}>
                    {count}
                  </span>
                </div>
              ))}
            </div>
          </ExperienceGlassCard>
        ) : null}

        <ExperienceGlassCard>
          <SectionLabel explainerId="PULSE-007" momentTypeCode={momentTypeCode}>Recent Activity</SectionLabel>
          {recentActivities.length === 0 ? (
            <EmptySection label="No recent activity yet." />
          ) : (
            <div className="relative space-y-6 before:absolute before:bottom-2 before:left-[19px] before:top-2 before:w-px before:bg-white/10">
              {recentActivities.map((a, index) => (
                <TimelineRow key={a.id || `activity-${index}`} {...a} />
              ))}
            </div>
          )}
        </ExperienceGlassCard>

        {nextTitle ? (
          <SunsetCta eyebrow="Next Best Action" title={nextTitle} impacts={[]} onClick={onQuickAdd} explainerId="PULSE-008" momentTypeCode={momentTypeCode} />
        ) : (
          <SunsetCta eyebrow="Quick action" title="Add something to this moment" impacts={[]} onClick={onQuickAdd} />
        )}
      </GroupFadeSections>
    </ExperienceScrollShell>
  );
}
