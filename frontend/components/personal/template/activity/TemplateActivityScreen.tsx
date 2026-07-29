"use client";

import { useMemo, useState, type ReactNode } from "react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { PersonalAtmosphericOrbs } from "@/components/personal/empty/shared/PersonalAtmosphericOrbs";
import { personalGlassCardStyle, personalTypography } from "@/components/personal/empty/shared/emptyStyles";
import { resolveActivityIcon } from "@/lib/personal/life_operations/pulse/pulseIcons";
import type { PersonalMomentTypeCode } from "@/lib/personal/personalMomentSession";
import { useUnifiedActivity } from "@/hooks/useUnifiedActivity";
import type { UnifiedPersonalActivityItem } from "@/lib/personal/template/activity/types";
import { formatRelativeTime } from "@/lib/personal/life_operations/pulse/recentActivityDisplay";
import {
  chapterizeDay,
  formatInrMinor,
  groupLifeActivities,
  lifeActivityContextLine,
  lifeActivityDomain,
  lifeActivityMetric,
  lifeActivityMood,
  lifeActivityTitle,
} from "@/lib/personal/lifeActivityDisplay";
import { lifeDomainColor, moodDotColor } from "@/lib/personal/lifeDomainColors";
import {
  ArrowLeft,
  Heart,
  Leaf,
  Rocket,
  Search,
  Sparkles,
  Wallet,
} from "lucide-react";

type TemplateActivityScreenProps = {
  momentTypeCode: PersonalMomentTypeCode;
  momentId: string;
  onBack: () => void;
  onEditActivity: (id: string, eventType: string, momentTypeCode?: string) => void;
};

const DOMAIN_CHIPS = [
  { id: "all", label: "All", Icon: Sparkles },
  { id: "money", label: "Money", Icon: Wallet },
  { id: "lifestyle", label: "Lifestyle", Icon: Leaf },
  { id: "relationships", label: "Relationships", Icon: Heart },
  { id: "future", label: "Future", Icon: Rocket },
] as const;

const RANGE_CHIPS = [
  { id: "all", label: "All time" },
  { id: "today", label: "Today" },
  { id: "yesterday", label: "Yesterday" },
  { id: "week", label: "Week" },
  { id: "month", label: "Month" },
  { id: "year", label: "Year" },
] as const;

const KIND_CHIPS = [
  { id: "all", label: "All kinds" },
  { id: "expense", label: "Expenses" },
  { id: "experience", label: "Experiences" },
  { id: "mood", label: "Mood" },
  { id: "learning", label: "Learning" },
  { id: "investment", label: "Investments" },
  { id: "milestone", label: "Milestones" },
] as const;

function ChipRow<T extends { id: string; label: string }>({
  chips,
  selected,
  onSelect,
  renderLabel,
  ariaLabel,
}: {
  chips: readonly T[];
  selected: string;
  onSelect: (id: string) => void;
  renderLabel?: (chip: T) => ReactNode;
  ariaLabel: string;
}) {
  const { colors } = useThemeTokens();
  return (
    <div className="flex gap-2 overflow-x-auto pb-1" role="listbox" aria-label={ariaLabel}>
      {chips.map((chip) => {
        const active = selected === chip.id;
        return (
          <button
            key={chip.id}
            type="button"
            role="option"
            aria-selected={active}
            onClick={() => onSelect(chip.id)}
            className="inline-flex min-h-10 shrink-0 items-center gap-1.5 rounded-full px-4 py-2 text-xs font-bold"
            style={{
              background: active ? colors.brandPrimary : colors.surfaceContainerHigh,
              color: active ? colors.brandOnPrimary : colors.textSecondary,
              border: "1px solid rgba(255,255,255,0.05)",
            }}
          >
            {renderLabel ? renderLabel(chip) : chip.label}
          </button>
        );
      })}
    </div>
  );
}

function TimelineRow({
  item,
  isLast,
  expanded,
  onToggle,
  onEdit,
}: {
  item: UnifiedPersonalActivityItem;
  isLast: boolean;
  expanded: boolean;
  onToggle: () => void;
  onEdit: () => void;
}) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  const domain = lifeActivityDomain(item);
  const domainColor = lifeDomainColor(domain);
  const title = lifeActivityTitle(item);
  const metric = lifeActivityMetric(item);
  const context = lifeActivityContextLine(item);
  const mood = lifeActivityMood(item);
  const Icon = resolveActivityIcon(
    item.activity_type,
    item.icon,
    item.category_code,
    item.subcategory_code,
  );
  const editable = item.editable ?? item.can_edit ?? true;

  return (
    <div className="relative flex gap-3">
      <div className="relative flex w-10 shrink-0 flex-col items-center">
        <span
          className="mt-3 size-2.5 shrink-0 rounded-full"
          style={{ background: domainColor, opacity: 0.85 }}
          aria-hidden
        />
        {!isLast ? (
          <span
            className="mt-1 w-px flex-1"
            style={{ background: "rgba(255,255,255,0.08)", minHeight: 28 }}
            aria-hidden
          />
        ) : null}
      </div>
      <div className={`min-w-0 flex-1 ${isLast ? "pb-2" : "pb-4"}`}>
        <button
          type="button"
          onClick={onToggle}
          className="w-full border-0 bg-transparent p-0 text-left"
          aria-expanded={expanded}
        >
          <div className="flex items-start gap-3">
            <div
              className="flex size-10 shrink-0 items-center justify-center rounded-xl"
              style={{
                background: `linear-gradient(160deg, ${domainColor}55 0%, ${domainColor}18 100%)`,
                boxShadow: `inset 0 0 0 1px ${domainColor}33`,
              }}
              aria-hidden
            >
              <Icon size={18} color={domainColor} />
            </div>
            <div className="min-w-0 flex-1">
              <div className="flex items-baseline justify-between gap-3">
                <p
                  className="min-w-0 truncate"
                  style={{ fontSize: 14, fontWeight: 700, color: colors.textPrimary }}
                >
                  {title}
                </p>
                {metric ? (
                  <span className="shrink-0" style={{ fontSize: 14, fontWeight: 700 }}>
                    {metric}
                  </span>
                ) : null}
              </div>
              <p
                className="mt-0.5 truncate"
                style={{ fontSize: 12, color: colors.textSecondary, opacity: 0.75 }}
              >
                {context}
              </p>
              <div className="mt-0.5 flex items-center justify-between gap-3">
                <p
                  className="min-w-0 truncate"
                  style={{ fontSize: 12, color: colors.textSecondary, opacity: 0.7 }}
                >
                  {mood ? (
                    <span className="inline-flex items-center gap-1.5">
                      <span
                        className="inline-block size-1.5 rounded-full"
                        style={{ background: moodDotColor(mood) }}
                        aria-hidden
                      />
                      {mood}
                    </span>
                  ) : (
                    "\u00A0"
                  )}
                </p>
                <span style={{ fontSize: 11, opacity: 0.45 }}>
                  {formatRelativeTime(item.occurred_at)}
                </span>
              </div>
            </div>
          </div>
        </button>

        <div
          className="overflow-hidden transition-[max-height,opacity] duration-300 ease-out"
          style={{
            maxHeight: expanded ? 220 : 0,
            opacity: expanded ? 1 : 0,
          }}
        >
          <div
            className="mt-3 space-y-2 rounded-2xl p-3"
            style={{ ...personalGlassCardStyle(tokens), borderRadius: 14 }}
          >
            <p style={{ fontSize: 12, opacity: 0.7 }}>
              <span style={{ opacity: 0.55 }}>Type</span> · {item.type_label || item.activity_type}
            </p>
            {item.category_label ? (
              <p style={{ fontSize: 12, opacity: 0.7 }}>
                <span style={{ opacity: 0.55 }}>Category</span> · {item.category_label}
                {item.subcategory_label ? ` · ${item.subcategory_label}` : ""}
              </p>
            ) : null}
            {mood ? (
              <p style={{ fontSize: 12, opacity: 0.7 }}>
                <span style={{ opacity: 0.55 }}>Mood</span> · {mood}
              </p>
            ) : null}
            {editable ? (
              <button
                type="button"
                onClick={onEdit}
                className="mt-1 text-xs font-bold underline"
                style={{ color: colors.brandPrimary, background: "none", border: "none", padding: 0 }}
              >
                Edit
              </button>
            ) : null}
          </div>
        </div>
      </div>
    </div>
  );
}

export function TemplateActivityScreen({
  momentTypeCode: _momentTypeCode,
  momentId: _momentId,
  onBack,
  onEditActivity,
}: TemplateActivityScreenProps) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  const [search, setSearch] = useState("");
  const [domain, setDomain] = useState("all");
  const [range, setRange] = useState("all");
  const [kind, setKind] = useState("all");
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const { loading, error, items, snapshot, insights, reload } = useUnifiedActivity({
    range,
    domain,
    kind,
    q: search,
  });

  const grouped = useMemo(() => groupLifeActivities(items), [items]);

  return (
    <div
      className="fixed inset-0 z-50 flex flex-col"
      style={{ background: colors.background, color: colors.textPrimary }}
    >
      <PersonalAtmosphericOrbs />
      <header
        className="relative z-10 flex shrink-0 items-center gap-3 border-b px-5 py-4"
        style={{ borderColor: "rgba(255,255,255,0.1)", background: `${colors.background}ee` }}
      >
        <button type="button" onClick={onBack} className="border-0 bg-transparent p-0" aria-label="Back">
          <ArrowLeft size={22} color={colors.brandPrimary} />
        </button>
        <div>
          <h1 style={{ ...personalTypography.screenTitle, color: colors.textPrimary }}>Activity</h1>
          <p style={{ ...personalTypography.labelSm, opacity: 0.6 }}>Your life across every moment</p>
        </div>
      </header>

      {loading ? (
        <p className="relative z-10 px-5 py-6" style={{ opacity: 0.7 }}>
          Opening your life story…
        </p>
      ) : error ? (
        <div className="relative z-10 space-y-3 px-5 py-6">
          <p style={{ color: colors.error }}>{error}</p>
          <button type="button" onClick={() => void reload()} className="text-sm underline">
            Retry
          </button>
        </div>
      ) : (
        <>
          <div
            className="relative z-10 shrink-0 space-y-4 border-b px-5 py-4"
            style={{ borderColor: "rgba(255,255,255,0.06)", background: `${colors.background}f2` }}
          >
            <section style={{ ...personalGlassCardStyle(tokens), borderRadius: 18, padding: 14 }}>
              <p
                style={{
                  fontSize: 10,
                  fontWeight: 700,
                  letterSpacing: "0.14em",
                  textTransform: "uppercase",
                  opacity: 0.5,
                }}
              >
                Today&apos;s Story
              </p>
              <p style={{ fontSize: 16, fontWeight: 700, marginTop: 6 }}>{snapshot.headline}</p>
              {snapshot.today_activity_count > 0 ? (
                <div className="mt-3 flex flex-wrap items-center gap-x-3 gap-y-1" style={{ fontSize: 13, opacity: 0.8 }}>
                  {snapshot.today_amount_minor > 0 ? (
                    <span>{formatInrMinor(snapshot.today_amount_minor)} spent</span>
                  ) : null}
                  {snapshot.today_mood_label ? (
                    <span className="inline-flex items-center gap-1.5">
                      <span
                        className="inline-block size-1.5 rounded-full"
                        style={{ background: moodDotColor(snapshot.today_mood_label) }}
                      />
                      {snapshot.today_mood_label}
                    </span>
                  ) : null}
                  {(snapshot.today_domain_labels ?? []).length > 0 ? (
                    <span>{(snapshot.today_domain_labels ?? []).join(" · ")}</span>
                  ) : null}
                </div>
              ) : null}
            </section>

            <div className="relative">
              <Search
                size={18}
                className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2"
                color={colors.textSecondary}
              />
              <input
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                placeholder="Search anything..."
                className="w-full rounded-2xl border-0 py-3.5 pl-12 pr-4"
                style={{
                  background: colors.surfaceContainerLowest,
                  color: colors.textPrimary,
                  ...personalTypography.bodyMd,
                }}
              />
            </div>

            <ChipRow
              chips={DOMAIN_CHIPS}
              selected={domain}
              onSelect={setDomain}
              ariaLabel="Domain filters"
              renderLabel={(chip) => (
                <>
                  <chip.Icon size={14} aria-hidden />
                  {chip.label}
                </>
              )}
            />
            <ChipRow chips={RANGE_CHIPS} selected={range} onSelect={setRange} ariaLabel="Time range" />
            <ChipRow chips={KIND_CHIPS} selected={kind} onSelect={setKind} ariaLabel="Activity kinds" />

            {insights.length > 0 ? (
              <div className="flex gap-2 overflow-x-auto pb-1">
                {insights.map((insight) => (
                  <div
                    key={insight.id}
                    className="min-w-[128px] shrink-0 rounded-2xl p-3"
                    style={{ ...personalGlassCardStyle(tokens), borderRadius: 14 }}
                  >
                    <p style={{ fontSize: 10, fontWeight: 700, opacity: 0.5, textTransform: "uppercase" }}>
                      {insight.title}
                    </p>
                    <p style={{ fontSize: 14, fontWeight: 700, marginTop: 4 }}>{insight.value}</p>
                  </div>
                ))}
              </div>
            ) : null}
          </div>

          <div className="relative z-10 flex-1 overflow-y-auto px-5 py-4">
            <div className="mx-auto max-w-2xl">
              {items.length === 0 ? (
                <p style={{ ...personalTypography.bodyMd, opacity: 0.7, paddingTop: 24 }}>
                  Start logging moments and your life story will appear here.
                </p>
              ) : (
                grouped.map((group) => {
                  const chapters = chapterizeDay(group.items);
                  const showChapters = chapters.length > 1;
                  return (
                    <section key={group.label} className="mb-6">
                      <h3
                        className="mb-3 uppercase"
                        style={{
                          fontSize: 10,
                          fontWeight: 700,
                          letterSpacing: "0.14em",
                          opacity: 0.45,
                        }}
                      >
                        {group.label}
                      </h3>
                      {chapters.map((chapter) => (
                        <div key={`${group.label}-${chapter.chapter}`} className="mb-2">
                          {showChapters ? (
                            <p
                              className="mb-2"
                              style={{ fontSize: 11, fontWeight: 600, opacity: 0.45 }}
                            >
                              {chapter.chapter}
                            </p>
                          ) : null}
                          {chapter.items.map((item, index) => (
                            <TimelineRow
                              key={item.id}
                              item={item}
                              isLast={index === chapter.items.length - 1 && !showChapters}
                              expanded={expandedId === item.id}
                              onToggle={() =>
                                setExpandedId((cur) => (cur === item.id ? null : item.id))
                              }
                              onEdit={() =>
                                onEditActivity(
                                  item.id,
                                  item.edit_event_type || item.activity_type || "EXPENSE",
                                  item.moment_type_code || undefined,
                                )
                              }
                            />
                          ))}
                        </div>
                      ))}
                    </section>
                  );
                })
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
