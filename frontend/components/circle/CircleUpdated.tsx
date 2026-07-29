"use client";

import { useMemo, useState } from "react";
import {
  Briefcase,
  ChevronRight,
  Plane,
  PlusCircle,
  Search,
  Sparkles,
  Users,
  Utensils,
} from "lucide-react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import type {
  CircleParticipantEntry,
  CircleRecentActivity,
  CircleSuggestion,
} from "@/repositories/CircleRepository";

type CircleFilter = "all" | "active" | "recent" | "groups" | "business";

type CircleUpdatedProps = {
  participants: CircleParticipantEntry[];
  suggestions: CircleSuggestion[];
  recentActivity: CircleRecentActivity[];
  participantCount: number;
  onCreateGroupMoment: () => void;
  onCreateBusinessWorkspace: () => void;
  onAddToMoment: () => void;
};

const FILTERS: { id: CircleFilter; label: string }[] = [
  { id: "all", label: "All" },
  { id: "active", label: "Active" },
  { id: "recent", label: "Recent" },
  { id: "groups", label: "Groups" },
  { id: "business", label: "Business" },
];

function initials(name: string): string {
  const parts = name.trim().split(/\s+/).filter(Boolean);
  if (parts.length === 0) return "?";
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
}

function activityIcon(type: string | null | undefined) {
  const t = (type ?? "").toUpperCase();
  if (t.includes("TRIP") || t.includes("TRAVEL") || t.includes("FLIGHT")) {
    return Plane;
  }
  if (t.includes("DINNER") || t.includes("FOOD") || t.includes("MEAL")) {
    return Utensils;
  }
  if (t.includes("BUSINESS") || t.includes("BUDGET") || t.includes("WORK")) {
    return Briefcase;
  }
  return Users;
}

export function CircleUpdated({
  participants,
  suggestions,
  recentActivity,
  participantCount,
  onCreateGroupMoment,
  onCreateBusinessWorkspace,
  onAddToMoment,
}: CircleUpdatedProps) {
  const tokens = useThemeTokens();
  const accent = tokens.colors.brandPrimary;
  const accentEnd = tokens.colors.brandSecondary;
  const [filter, setFilter] = useState<CircleFilter>("all");
  const [query, setQuery] = useState("");

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    return participants.filter((entry) => {
      const { participant, stats } = entry;
      if (q && !participant.participant_name.toLowerCase().includes(q)) {
        return false;
      }
      if (filter === "active" && participant.is_active === false) return false;
      if (filter === "recent") {
        const recent = stats?.recent_activity_count ?? 0;
        if (recent <= 0) return false;
      }
      if (filter === "groups" && !entry.is_group_participant) return false;
      if (filter === "business" && !entry.is_business_participant) return false;
      return true;
    });
  }, [participants, filter, query]);

  const recentStack = useMemo(() => {
    return participants
      .slice()
      .sort((a, b) => {
        const ad = a.stats?.last_activity_date ?? a.participant.last_seen_date ?? "";
        const bd = b.stats?.last_activity_date ?? b.participant.last_seen_date ?? "";
        return bd.localeCompare(ad);
      })
      .slice(0, 12);
  }, [participants]);

  const overflowCount = Math.max(0, participants.length - 3);

  function handleSuggestionCta(suggestion: CircleSuggestion) {
    const flow = (suggestion.target_create_flow ?? "").toUpperCase();
    if (flow.includes("BUSINESS")) {
      onCreateBusinessWorkspace();
    } else {
      onCreateGroupMoment();
    }
  }

  function FilterChips({ className = "" }: { className?: string }) {
    return (
      <div className={`flex gap-2 overflow-x-auto pb-1 ${className}`}>
        {FILTERS.map((f) => {
          const selected = filter === f.id;
          return (
            <button
              key={f.id}
              type="button"
              onClick={() => setFilter(f.id)}
              className="shrink-0 rounded-full px-5 py-2 text-xs font-bold whitespace-nowrap"
              style={
                selected
                  ? {
                      background: accent,
                      color: tokens.colors.brandOnPrimary,
                    }
                  : {
                      background: tokens.colors.surfaceContainer,
                      color: tokens.colors.textSubtle,
                      border: `1px solid ${tokens.colors.border}`,
                    }
              }
            >
              {f.label}
            </button>
          );
        })}
      </div>
    );
  }

  return (
    <div className="mx-auto flex w-full max-w-2xl flex-col px-5 pb-10 pt-2">
      <section
        className="relative mb-8 flex min-h-[280px] w-full items-center justify-center overflow-hidden rounded-[2.5rem] sm:min-h-[360px]"
        style={{
          background: `radial-gradient(ellipse at center, ${tokens.colors.surfaceVariant} 0%, ${tokens.colors.background} 75%)`,
        }}
      >
        <div
          className="absolute inset-0 opacity-60"
          style={{
            background: `radial-gradient(circle at 50% 45%, ${accent}55 0%, transparent 58%)`,
          }}
        />
        <div className="relative z-10 text-center">
          <h2
            className="text-5xl font-extrabold tracking-tighter"
            style={{ color: tokens.colors.textPrimary }}
          >
            {participantCount}
          </h2>
          <p
            className="mt-1 text-xs font-bold uppercase tracking-[0.2em]"
            style={{ color: accent }}
          >
            Participants
          </p>
        </div>
      </section>

      <FilterChips className="mb-8" />

      <section className="mb-8">
        <h2
          className="mb-4 text-xs font-bold uppercase tracking-[0.2em]"
          style={{ color: tokens.colors.textSubtle }}
        >
          Participants
        </h2>
        <div className="flex gap-6 overflow-x-auto pb-2">
          {filtered.slice(0, 24).map(({ participant, stats }) => {
            const moments = stats?.shared_moment_count ?? 0;
            return (
              <div
                key={participant.circle_participant_id}
                className="flex w-20 shrink-0 flex-col items-center gap-2"
              >
                <div className="relative h-20 w-20">
                  <div
                    className="flex h-full w-full items-center justify-center rounded-full text-base font-bold"
                    style={{
                      background: tokens.colors.primaryContainer,
                      color: tokens.colors.onPrimaryContainer,
                      boxShadow: `0 0 0 2px ${tokens.colors.background}, 0 0 0 4px ${accent}`,
                    }}
                  >
                    {initials(participant.participant_name)}
                  </div>
                  {moments > 0 ? (
                    <span
                      className="absolute -bottom-1 -right-1 flex h-5 min-w-5 items-center justify-center rounded-full border-2 px-1.5 text-[10px] font-bold"
                      style={{
                        background: accent,
                        color: tokens.colors.brandOnPrimary,
                        borderColor: tokens.colors.background,
                      }}
                    >
                      {moments}
                    </span>
                  ) : null}
                </div>
                <span
                  className="w-full truncate text-center text-sm font-semibold"
                  style={{ color: tokens.colors.textPrimary }}
                >
                  {participant.participant_name.split(" ")[0]}
                </span>
                <span
                  className="text-[10px] uppercase tracking-wide"
                  style={{ color: tokens.colors.textSubtle }}
                >
                  {moments} moment{moments === 1 ? "" : "s"}
                </span>
              </div>
            );
          })}
          {filtered.length === 0 ? (
            <p className="text-sm" style={{ color: tokens.colors.textSubtle }}>
              No participants match this filter.
            </p>
          ) : null}
        </div>
      </section>

      {suggestions.length > 0 ? (
        <section className="mb-8">
          <h2
            className="mb-4 text-xs font-bold uppercase tracking-[0.2em]"
            style={{ color: tokens.colors.textSubtle }}
          >
            Suggested Moments
          </h2>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
            {suggestions.slice(0, 4).map((suggestion) => {
              const isBiz = (suggestion.target_create_flow ?? "")
                .toUpperCase()
                .includes("BUSINESS");
              return (
                <div
                  key={suggestion.suggestion_id}
                  className="flex flex-col justify-between rounded-3xl p-6"
                  style={{
                    background: `linear-gradient(145deg, ${accent}1A, ${accentEnd}0D)`,
                    border: `1px solid ${accent}33`,
                    boxShadow: `0 8px 32px ${tokens.shadows.glowColor}`,
                  }}
                >
                  <div>
                    <div
                      className="mb-4 flex h-10 w-10 items-center justify-center rounded-xl"
                      style={{
                        background: `${accent}33`,
                        color: accent,
                      }}
                    >
                      {isBiz ? (
                        <Briefcase className="h-5 w-5" />
                      ) : (
                        <Sparkles className="h-5 w-5" />
                      )}
                    </div>
                    <p
                      className="mb-6 text-base leading-snug"
                      style={{ color: tokens.colors.textPrimary }}
                    >
                      {suggestion.suggestion_description ||
                        suggestion.suggestion_title}
                    </p>
                  </div>
                  <button
                    type="button"
                    onClick={() => handleSuggestionCta(suggestion)}
                    className="w-full rounded-2xl py-3.5 text-sm font-bold transition-transform active:scale-95"
                    style={{
                      background: isBiz ? accentEnd : accent,
                      color: tokens.colors.brandOnPrimary,
                    }}
                  >
                    {suggestion.cta_label ??
                      (isBiz
                        ? "Create Business Workspace"
                        : "Create Shared Experience")}
                  </button>
                </div>
              );
            })}
          </div>
        </section>
      ) : null}

      <section className="mb-8">
        <h2
          className="mb-4 text-xs font-bold uppercase tracking-[0.2em]"
          style={{ color: tokens.colors.textSubtle }}
        >
          Quick Add Participants
        </h2>
        <div className="relative mb-4">
          <Search
            className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2"
            style={{ color: tokens.colors.textSubtle }}
          />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search Circle"
            className="w-full rounded-2xl border py-4 pl-12 pr-4 text-sm outline-none"
            style={{
              background: tokens.colors.surfaceContainerLow,
              borderColor: tokens.colors.border,
              color: tokens.colors.textPrimary,
            }}
          />
        </div>
        <FilterChips className="mb-4" />
        <div className="flex items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <span
              className="text-xs font-bold uppercase tracking-wider"
              style={{ color: tokens.colors.textSubtle }}
            >
              Recent:
            </span>
            <div className="flex items-center -space-x-3">
              {recentStack.slice(0, 3).map(({ participant }) => (
                <div
                  key={participant.circle_participant_id}
                  className="flex h-10 w-10 items-center justify-center rounded-full border-2 text-[10px] font-bold"
                  style={{
                    background: tokens.colors.primaryContainer,
                    color: tokens.colors.onPrimaryContainer,
                    borderColor: tokens.colors.background,
                  }}
                  title={participant.participant_name}
                >
                  {initials(participant.participant_name)}
                </div>
              ))}
              {overflowCount > 0 ? (
                <div
                  className="flex h-10 w-10 items-center justify-center rounded-full border-2 text-[10px] font-bold"
                  style={{
                    background: tokens.colors.surfaceContainer,
                    color: tokens.colors.textSubtle,
                    borderColor: tokens.colors.background,
                  }}
                >
                  +{overflowCount}
                </div>
              ) : null}
            </div>
          </div>
          <button
            type="button"
            onClick={onAddToMoment}
            className="flex shrink-0 items-center gap-2 rounded-xl px-4 py-2.5 text-xs font-bold"
            style={{
              color: accent,
              background: `${accent}1A`,
            }}
          >
            <PlusCircle className="h-4 w-4" />
            Add to New Moment
          </button>
        </div>
      </section>

      {recentActivity.length > 0 ? (
        <section className="mb-4">
          <h2
            className="mb-4 text-xs font-bold uppercase tracking-[0.2em]"
            style={{ color: tokens.colors.textSubtle }}
          >
            Recent People Activity
          </h2>
          <div className="space-y-2">
            {recentActivity.map((item) => {
              const Icon = activityIcon(item.source_moment_type ?? item.source_type);
              const title =
                item.source_moment_name?.trim() ||
                item.source_moment_type ||
                "Shared moment";
              const count = item.participant_count ?? 0;
              return (
                <div
                  key={`${item.source_type}-${item.source_moment_id}`}
                  className="flex items-center justify-between rounded-2xl border p-4"
                  style={{
                    background: tokens.colors.surfaceContainerLow,
                    borderColor: `${tokens.colors.border}`,
                  }}
                >
                  <div className="flex items-center gap-4">
                    <div
                      className="flex h-10 w-10 items-center justify-center rounded-xl"
                      style={{
                        background: `${accent}1A`,
                        color: accent,
                      }}
                    >
                      <Icon className="h-5 w-5" />
                    </div>
                    <div>
                      <h3
                        className="text-sm font-bold"
                        style={{ color: tokens.colors.textPrimary }}
                      >
                        {title}
                      </h3>
                      <span
                        className="text-[11px]"
                        style={{ color: tokens.colors.textSubtle }}
                      >
                        {count} participant{count === 1 ? "" : "s"}
                      </span>
                    </div>
                  </div>
                  <ChevronRight
                    className="h-5 w-5"
                    style={{ color: tokens.colors.textSubtle }}
                  />
                </div>
              );
            })}
          </div>
        </section>
      ) : null}
    </div>
  );
}
