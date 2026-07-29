"use client";

import { useEffect, useState } from "react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { personalGlassCardStyle, personalTypography } from "@/components/personal/empty/shared/emptyStyles";
import { PersonalWidgetSectionHeader } from "@/components/personal/shared/WidgetInfoButton";
import type { PulseDashboardRecentItem } from "@/lib/api/personal";
import { lifeOpsPulseCopy } from "@/lib/personal/life_operations/pulse/lifeOpsPulseCopy";
import { resolveActivityIcon } from "@/lib/personal/life_operations/pulse/pulseIcons";
import {
  formatRelativeTime,
  groupActivitiesByDate,
  recentActivityContextLine,
  recentActivityIsEditable,
  recentActivityMoodLabel,
  recentActivityMoodTone,
  recentActivityPrimaryMetric,
  recentActivityTitle,
} from "@/lib/personal/life_operations/pulse/recentActivityDisplay";
import { resolveExpenseCategoryColor } from "@/lib/personal/life_operations/expenseCategoryIcons";
import { MoreHorizontal } from "lucide-react";

type RecentActivityListProps = {
  items: PulseDashboardRecentItem[];
  emptyMessage?: string | null;
  onViewAll?: () => void;
  onEditActivity?: (id: string, eventType: string) => void;
  title?: string;
  subtitle?: string;
  explainerId?: string;
  momentTypeCode?: string | null;
};

function moodDotColor(
  tone: ReturnType<typeof recentActivityMoodTone>,
  colors: ReturnType<typeof useThemeTokens>["colors"],
): string {
  switch (tone) {
    case "good":
      return "#34D399";
    case "calm":
      return "#60A5FA";
    case "focus":
      return colors.brandPrimary;
    case "tired":
      return "#94A3B8";
    default:
      return colors.textSecondary;
  }
}

/**
 * Ship layout:
 * [icon] Title                              ₹517
 *        Expense · Planned · ● Happy     Just now
 */
export function RecentActivityList({
  items,
  emptyMessage,
  onViewAll,
  onEditActivity,
  title = lifeOpsPulseCopy.recentActivityListTitle,
  subtitle = lifeOpsPulseCopy.recentActivityListSubtitle,
  explainerId,
  momentTypeCode,
}: RecentActivityListProps) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  const [, setTick] = useState(0);
  useEffect(() => {
    const id = window.setInterval(() => setTick((n) => n + 1), 60_000);
    return () => window.clearInterval(id);
  }, []);
  const visible = items.slice(0, 5);
  const grouped = groupActivitiesByDate(visible);

  return (
    <section style={{ ...personalGlassCardStyle(tokens), borderRadius: 16, padding: 12 }}>
      <div className="mb-4 flex items-start justify-between gap-3">
        <div className="min-w-0">
          {explainerId ? (
            <PersonalWidgetSectionHeader title={title} explainerId={explainerId} momentTypeCode={momentTypeCode} />
          ) : (
            <h3 style={{ ...personalTypography.sectionHeader, color: colors.textPrimary }}>{title}</h3>
          )}
          <p style={{ ...personalTypography.labelSm, fontSize: 11, color: colors.textSecondary, opacity: 0.6, marginTop: 1 }}>
            {subtitle}
          </p>
        </div>
        <button
          type="button"
          onClick={onViewAll}
          style={{
            ...personalTypography.labelSm,
            fontWeight: 700,
            fontSize: 10,
            textTransform: "uppercase",
            color: colors.brandPrimary,
            background: "none",
            border: "none",
            flexShrink: 0,
          }}
        >
          {lifeOpsPulseCopy.viewAll}
        </button>
      </div>

      {visible.length > 0 ? (
        <div className="space-y-4">
          {grouped.map((group) => (
            <div key={group.label}>
              <p
                className="mb-2 uppercase"
                style={{
                  fontSize: 10,
                  fontWeight: 700,
                  letterSpacing: "0.12em",
                  color: colors.textSecondary,
                  opacity: 0.45,
                }}
              >
                {group.label}
              </p>
              <div className="space-y-0">
                {group.items.map((item, index) => {
                  const Icon = resolveActivityIcon(
                    item.activity_type,
                    item.icon,
                    item.category_code,
                    item.subcategory_code,
                  );
                  const catColor =
                    resolveExpenseCategoryColor(item.color, item.category_code, item.subcategory_code) ||
                    colors.brandPrimary;
                  const isLast = index === group.items.length - 1;
                  const context = recentActivityContextLine(item);
                  const mood = recentActivityMoodLabel(item);
                  const moodTone = recentActivityMoodTone(item);
                  const metric = recentActivityPrimaryMetric(item);
                  const editable = recentActivityIsEditable(item);
                  const titleText = recentActivityTitle(item);
                  const eventType = item.edit_event_type ?? item.activity_type.toUpperCase();

                  return (
                    <div
                      key={item.id}
                      className={`group relative flex items-center gap-3 ${isLast ? "" : "border-b pb-3"} ${index > 0 ? "pt-3" : ""}`}
                      style={{ borderColor: "rgba(255,255,255,0.05)" }}
                      onContextMenu={(e) => {
                        if (!editable) return;
                        e.preventDefault();
                        onEditActivity?.(item.id, eventType);
                      }}
                    >
                      <div
                        className="flex size-10 shrink-0 items-center justify-center rounded-xl"
                        style={{
                          background: `linear-gradient(160deg, ${catColor}55 0%, ${catColor}22 100%)`,
                          boxShadow: `inset 0 0 0 1px ${catColor}33`,
                        }}
                        aria-label={context ?? item.activity_type}
                      >
                        <Icon size={18} color={catColor} aria-hidden />
                      </div>

                      <div className="min-w-0 flex-1">
                        <div className="flex items-baseline justify-between gap-3">
                          <p
                            className="min-w-0 truncate"
                            style={{ fontSize: 14, fontWeight: 700, color: colors.textPrimary, lineHeight: 1.25 }}
                          >
                            {titleText}
                          </p>
                          {metric ? (
                            <span
                              className="shrink-0"
                              style={{ fontSize: 14, fontWeight: 700, color: colors.textPrimary, lineHeight: 1.25 }}
                            >
                              {metric}
                            </span>
                          ) : null}
                        </div>

                        <div className="mt-0.5 flex items-center justify-between gap-3">
                          <p
                            className="min-w-0 truncate"
                            style={{ fontSize: 12, fontWeight: 500, color: colors.textSecondary, opacity: 0.72 }}
                          >
                            {context}
                            {context && mood ? " · " : null}
                            {mood ? (
                              <span className="inline-flex items-center gap-1">
                                <span
                                  aria-hidden
                                  className="inline-block size-1.5 rounded-full"
                                  style={{ background: moodDotColor(moodTone, colors) }}
                                />
                                {mood}
                              </span>
                            ) : null}
                            {!context && !mood ? "\u00A0" : null}
                          </p>
                          <div className="flex shrink-0 items-center gap-2">
                            <span
                              style={{ fontSize: 11, fontWeight: 500, color: colors.textSecondary, opacity: 0.45 }}
                            >
                              {formatRelativeTime(item.occurred_at)}
                            </span>
                            {editable ? (
                              <button
                                type="button"
                                onClick={() => onEditActivity?.(item.id, eventType)}
                                className="border-0 bg-transparent p-1 opacity-0 transition-opacity focus-visible:opacity-100 group-hover:opacity-100 group-focus-within:opacity-100"
                                aria-label={`Edit ${titleText}`}
                              >
                                <MoreHorizontal size={16} color={colors.textSecondary} style={{ opacity: 0.55 }} />
                              </button>
                            ) : null}
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <p style={{ ...personalTypography.bodyMd, color: colors.textSecondary, opacity: 0.7 }}>
          {emptyMessage ?? lifeOpsPulseCopy.recentActivityEmptyFallback}
        </p>
      )}
    </section>
  );
}
