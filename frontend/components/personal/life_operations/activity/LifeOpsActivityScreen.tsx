"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { PersonalAtmosphericOrbs } from "@/components/personal/empty/shared/PersonalAtmosphericOrbs";
import { personalGlassCardStyle, personalTypography } from "@/components/personal/empty/shared/emptyStyles";
import { resolveActivityIcon } from "@/lib/personal/life_operations/pulse/pulseIcons";
import {
  resolveExpenseCategoryColor,
  resolveImpactIcon,
} from "@/lib/personal/life_operations/expenseCategoryIcons";
import { lifeOpsPulseCopy } from "@/lib/personal/life_operations/pulse/lifeOpsPulseCopy";
import {
  filterMatchesEventType,
  lifeOpsActivityCopy,
  type LifeOpsActivityFilter,
} from "@/lib/personal/life_operations/activity/lifeOpsActivityCopy";
import type { PersonalLifeOpsActivityItem } from "@/lib/api/personal";
import { getLifeOpsActivity } from "@/lib/api/client";
import {
  recentActivityCategoryLine,
  recentActivityMetaLine,
  recentActivityTitle,
} from "@/lib/personal/life_operations/pulse/recentActivityDisplay";
import { ArrowLeft, Pencil, Search } from "lucide-react";

type LifeOpsActivityScreenProps = {
  momentId: string;
  onBack: () => void;
  onEditActivity: (id: string, eventType: string) => void;
};

function groupLabel(iso: string): string {
  const d = new Date(iso);
  const now = new Date();
  const startOfToday = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const startOfYesterday = new Date(startOfToday);
  startOfYesterday.setDate(startOfYesterday.getDate() - 1);
  const startOfWeek = new Date(startOfToday);
  startOfWeek.setDate(startOfWeek.getDate() - 7);
  if (d >= startOfToday) return lifeOpsActivityCopy.groupToday;
  if (d >= startOfYesterday) return lifeOpsActivityCopy.groupYesterday;
  if (d >= startOfWeek) return lifeOpsActivityCopy.groupThisWeek;
  return lifeOpsActivityCopy.groupEarlier;
}

function formatInrMinor(minor: number) {
  return lifeOpsPulseCopy.formatInrMinor(minor);
}

export function LifeOpsActivityScreen({ momentId, onBack, onEditActivity }: LifeOpsActivityScreenProps) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [items, setItems] = useState<PersonalLifeOpsActivityItem[]>([]);
  const [summary, setSummary] = useState({ total_logs: 0, this_month: 0, total_amount_minor: 0 });
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState<LifeOpsActivityFilter>("all");

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getLifeOpsActivity(momentId);
      setItems(data.items);
      setSummary(data.summary);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not load activity.");
    } finally {
      setLoading(false);
    }
  }, [momentId]);

  useEffect(() => {
    void load();
  }, [load]);

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    const monthStart = new Date();
    monthStart.setDate(1);
    monthStart.setHours(0, 0, 0, 0);
    return items.filter((item) => {
      if (!filterMatchesEventType(filter, item.event_type)) return false;
      if (filter === "thisMonth" && new Date(item.captured_at) < monthStart) return false;
      if (!q) return true;
      const hay = `${item.title ?? ""} ${item.category_label} ${item.subcategory_label ?? ""} ${item.detail_line} ${item.mood_label ?? ""} ${item.amount_label ?? ""}`.toLowerCase();
      return hay.includes(q);
    });
  }, [items, search, filter]);

  const grouped = useMemo(() => {
    const map = new Map<string, PersonalLifeOpsActivityItem[]>();
    for (const item of filtered) {
      const key = groupLabel(item.captured_at);
      if (!map.has(key)) map.set(key, []);
      map.get(key)!.push(item);
    }
    const order = [
      lifeOpsActivityCopy.groupToday,
      lifeOpsActivityCopy.groupYesterday,
      lifeOpsActivityCopy.groupThisWeek,
      lifeOpsActivityCopy.groupEarlier,
    ];
    return order.filter((k) => map.has(k)).map((k) => ({ label: k, items: map.get(k)! }));
  }, [filtered]);

  const filterChips: LifeOpsActivityFilter[] = [
    "all",
    "money",
    "edited",
    "thisMonth",
    "attention",
    "recovery",
    "mood",
    "account",
    "adjust",
  ];

  return (
    <div
      className="fixed inset-0 z-50 flex flex-col"
      style={{ background: colors.background, color: colors.textPrimary }}
    >
      <PersonalAtmosphericOrbs />
      <header
        className="relative z-10 flex items-center gap-3 border-b px-5 py-4"
        style={{ borderColor: "rgba(255,255,255,0.1)", background: `${colors.background}cc` }}
      >
        <button type="button" onClick={onBack} className="border-0 bg-transparent p-0" aria-label="Back to Pulse">
          <ArrowLeft size={22} color={colors.brandPrimary} />
        </button>
        <div>
          <h1 style={{ ...personalTypography.screenTitle, color: colors.textPrimary }}>
            {lifeOpsActivityCopy.screenTitle}
          </h1>
          <p style={{ ...personalTypography.labelSm, opacity: 0.6 }}>{lifeOpsActivityCopy.screenSubtitle}</p>
        </div>
      </header>

      <div className="relative z-10 flex-1 overflow-y-auto px-5 py-4">
        {loading ? (
          <p style={{ opacity: 0.7 }}>Loading activity…</p>
        ) : error ? (
          <div className="space-y-3">
            <p style={{ color: colors.error }}>{error}</p>
            <button type="button" onClick={() => void load()} className="text-sm underline">
              Retry
            </button>
          </div>
        ) : (
          <div className="mx-auto flex max-w-2xl flex-col gap-6">
            <div className="relative">
              <Search
                size={18}
                className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2"
                color={colors.textSecondary}
              />
              <input
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder={lifeOpsActivityCopy.searchPlaceholder}
                className="w-full rounded-2xl border-0 py-4 pl-12 pr-4"
                style={{
                  background: colors.surfaceContainerLowest,
                  color: colors.textPrimary,
                  ...personalTypography.bodyMd,
                }}
              />
            </div>

            <div className="grid grid-cols-3 gap-3">
              {[
                [lifeOpsActivityCopy.totalLogs, String(summary.total_logs), colors.brandPrimary],
                [lifeOpsActivityCopy.thisMonth, String(summary.this_month), colors.brandTertiary],
                [lifeOpsActivityCopy.totalAmount, formatInrMinor(summary.total_amount_minor), colors.brandSecondary],
              ].map(([label, value, accent]) => (
                <div
                  key={label}
                  className="rounded-2xl p-4 text-center"
                  style={{ ...personalGlassCardStyle(tokens) }}
                >
                  <p style={{ fontSize: 10, fontWeight: 700, opacity: 0.6, textTransform: "uppercase" }}>{label}</p>
                  <p style={{ fontSize: 20, fontWeight: 800, color: accent }}>{value}</p>
                </div>
              ))}
            </div>

            <div className="flex gap-2 overflow-x-auto pb-1">
              {filterChips.map((chip) => {
                const active = filter === chip;
                return (
                  <button
                    key={chip}
                    type="button"
                    onClick={() => setFilter(chip)}
                    className="shrink-0 rounded-full px-5 py-2 text-xs font-bold"
                    style={{
                      background: active ? colors.brandPrimary : colors.surfaceContainerHigh,
                      color: active ? colors.brandOnPrimary : colors.textSecondary,
                      border: "1px solid rgba(255,255,255,0.05)",
                    }}
                  >
                    {lifeOpsActivityCopy.filters[chip]}
                  </button>
                );
              })}
            </div>

            {grouped.length === 0 ? (
              <p style={{ ...personalTypography.bodyMd, opacity: 0.7 }}>{lifeOpsActivityCopy.empty}</p>
            ) : (
              grouped.map((group) => (
                <section key={group.label}>
                  <h3
                    className="mb-4 flex items-center gap-3 uppercase"
                    style={{ fontSize: 11, fontWeight: 700, letterSpacing: "0.2em", opacity: 0.4 }}
                  >
                    <span>{group.label}</span>
                    <span className="h-px flex-1" style={{ background: "rgba(255,255,255,0.05)" }} />
                  </h3>
                  <div className="space-y-3">
                    {group.items.map((item) => {
                      const Icon = resolveActivityIcon(
                        item.event_type,
                        item.icon,
                        item.category_code,
                        item.subcategory_code,
                      );
                      const ImpactIcon = item.impact_label ? resolveImpactIcon(item.impact_label) : null;
                      const catColor =
                        resolveExpenseCategoryColor(item.color, item.category_code, item.subcategory_code) ||
                        colors.brandPrimary;
                      const categoryLine = recentActivityCategoryLine(item);
                      const metaLine = recentActivityMetaLine(item);
                      return (
                        <button
                          key={item.id}
                          type="button"
                          onClick={() => item.can_edit && onEditActivity(item.id, item.edit_event_type)}
                          className="flex w-full items-center justify-between rounded-2xl p-4 text-left"
                          style={{ ...personalGlassCardStyle(tokens), border: "none" }}
                        >
                          <div className="flex min-w-0 items-center gap-4">
                            <div
                              className="flex size-10 shrink-0 items-center justify-center rounded-xl"
                              style={{ background: `${catColor}33` }}
                            >
                              <Icon size={18} color={catColor} />
                            </div>
                            <div className="min-w-0">
                              <p className="truncate font-semibold" style={{ fontSize: 14 }}>
                                {recentActivityTitle({
                                  title: item.title,
                                  subtitle: item.detail_line,
                                })}
                              </p>
                              {categoryLine ? (
                                <p style={{ fontSize: 11, opacity: 0.6, marginTop: 4 }}>{categoryLine}</p>
                              ) : null}
                              {item.impact_label || metaLine ? (
                                <p
                                  className="mt-1 inline-flex items-center gap-1"
                                  style={{ fontSize: 11, color: item.impact_label ? colors.error : colors.textSecondary }}
                                >
                                  {item.impact_label && ImpactIcon ? <ImpactIcon size={12} aria-hidden /> : null}
                                  {[item.impact_label, metaLine].filter(Boolean).join(" · ")}
                                </p>
                              ) : null}
                              <p style={{ fontSize: 11, opacity: 0.5, marginTop: 4 }}>{item.relative_time}</p>
                            </div>
                          </div>
                          {item.can_edit ? (
                            <Pencil size={16} color={colors.textSecondary} style={{ opacity: 0.4 }} />
                          ) : null}
                        </button>
                      );
                    })}
                  </div>
                </section>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  );
}
