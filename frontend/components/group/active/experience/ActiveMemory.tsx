"use client";

import { useEffect, useState } from "react";
import { Brain, ChevronDown } from "lucide-react";
import { GroupSkeletonBlocks } from "@/components/group/shared/skeleton/GroupSkeletonBlocks";
import { useGroupLivingMoments, useGroupMoments, useGroupPurchaseMoments } from "@/hooks/useGroupTabCache";
import {
  deleteLivingActivity,
  deleteTripActivity,
  type LivingMomentsViewResponse,
  type PurchaseMomentsViewResponse,
  type TripMomentsViewResponse,
} from "@/lib/api/group";
import { resolveMediaUrl } from "@/lib/api/client";
import { ExperienceGlassCard } from "./ui/ExperienceGlassCard";
import { MaterialIcon } from "./ui/MaterialIcon";
import { SectionLabel, SunsetCta, ExperienceScrollShell } from "./ui/ExperienceUiParts";
import { tripStitchShellStyle, tripStitchTheme } from "./ui/tripStitchTheme";

type ActiveMemoryProps = {
  momentId: string;
  onQuickAdd?: () => void;
  bottomPadding?: number;
  reloadKey?: number;
  source?: "trip" | "purchase" | "living";
};

export function ActiveMemory({
  momentId,
  onQuickAdd,
  bottomPadding = 0,
  reloadKey = 0,
  source = "trip",
}: ActiveMemoryProps) {
  const isPurchase = source === "purchase";
  const isLiving = source === "living";
  const isTrip = !isPurchase && !isLiving;
  const momentTypeCode = isPurchase
    ? "SHARED_PURCHASE"
    : isLiving
      ? "SHARED_LIVING"
      : "SHARED_EXPERIENCE";
  const tripHook = useGroupMoments(isTrip ? momentId : null, isTrip);
  const purchaseHook = useGroupPurchaseMoments(isPurchase ? momentId : null, isPurchase);
  const livingHook = useGroupLivingMoments(isLiving ? momentId : null, isLiving);
  const moments = (isPurchase ? purchaseHook.data : isLiving ? livingHook.data : tripHook.data) as
    | TripMomentsViewResponse
    | PurchaseMomentsViewResponse
    | LivingMomentsViewResponse
    | null
    | undefined;
  const loading = isPurchase ? purchaseHook.loading : isLiving ? livingHook.loading : tripHook.loading;
  const error = isPurchase ? purchaseHook.error : isLiving ? livingHook.error : tripHook.error;
  const reload = isPurchase ? purchaseHook.reload : isLiving ? livingHook.reload : tripHook.reload;
  const revalidate = isPurchase
    ? purchaseHook.revalidate
    : isLiving
      ? livingHook.revalidate
      : tripHook.revalidate;
  const [showExtras, setShowExtras] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  useEffect(() => {
    if (reloadKey > 0) void revalidate();
  }, [reloadKey, revalidate]);

  async function handleDeleteMemory(memoryId: string) {
    if (!memoryId) return;
    if (!window.confirm("Delete this memory photo? This cannot be undone.")) return;
    setDeletingId(memoryId);
    try {
      if (isLiving) await deleteLivingActivity(momentId, memoryId);
      else await deleteTripActivity(momentId, memoryId);
      await reload();
    } catch (err: unknown) {
      window.alert(err instanceof Error ? err.message : "Could not delete memory photo");
    } finally {
      setDeletingId(null);
    }
  }

  if (loading && !moments) {
    return (
      <ExperienceScrollShell bottomPadding={bottomPadding} onRefresh={reload}>
        <GroupSkeletonBlocks variant="memory" />
      </ExperienceScrollShell>
    );
  }

  if (error && !moments) {
    return (
      <div className="flex flex-col items-center justify-center p-10 text-center" style={tripStitchShellStyle}>
        <Brain size={40} style={{ color: tripStitchTheme.onSurfaceVariant }} />
        <p className="mt-3 text-sm" style={{ color: tripStitchTheme.onSurfaceVariant }}>
          {error || "Unable to load this section."}
        </p>
        <button type="button" className="mt-3 text-sm font-semibold underline" onClick={() => void reload()}>
          Retry
        </button>
      </div>
    );
  }

  const hub = moments?.memory_hub;
  const fallbackName =
    moments && "trip_name" in moments && moments.trip_name
      ? moments.trip_name
      : moments && "moment_name" in moments
        ? moments.moment_name
        : "Untitled moment";
  const tripName = hub?.hero?.moment_name?.trim() || fallbackName;
  const timeline = hub?.timeline ?? [];
  const milestones = hub?.milestone_wall ?? [];
  const people = hub?.people_impact ?? [];
  const gallery = hub?.gallery ?? [];
  const highlights = hub?.highlights ?? [];
  const intelligence = hub?.intelligence;
  const budget = hub?.budget_reflection;
  const chips =
    hub?.hero?.chips && hub.hero.chips.length > 0
      ? hub.hero.chips
      : [
          { icon: "photo_library", label: `${gallery.length} Memories` },
          { icon: "group", label: `${people.length} Participants` },
          { icon: "military_tech", label: `${milestones.length} Milestones` },
        ];
  const galleryOverflow = Math.max(0, gallery.length - 3);
  const hasExtras =
    Boolean(intelligence?.insight) ||
    people.length > 0 ||
    Boolean(hub?.lessons_pattern) ||
    Boolean(hub?.group_identity) ||
    Boolean(budget);

  return (
    <ExperienceScrollShell bottomPadding={bottomPadding} style={tripStitchShellStyle} onRefresh={reload}>
      <ExperienceGlassCard glow accentBorder="left" className="relative min-h-[280px] overflow-hidden">
        <div className="relative z-10 flex h-full flex-col justify-end">
          <h2 className="mb-4 text-4xl font-bold" style={{ color: tripStitchTheme.onSurface }}>
            {tripName}
          </h2>
          <div className="flex flex-wrap gap-2">
            {chips.map((chip) => (
              <span
                key={chip.label}
                className="inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-medium"
                style={{
                  background: `${tripStitchTheme.primary}1A`,
                  borderColor: `${tripStitchTheme.primary}33`,
                  color: tripStitchTheme.primary,
                }}
              >
                {chip.icon ? <MaterialIcon name={chip.icon} className="text-[16px]" /> : null}
                {chip.label}
              </span>
            ))}
          </div>
        </div>
        <MaterialIcon
          name="travel_explore"
          className="pointer-events-none absolute bottom-4 right-4 text-[64px] opacity-20"
          style={{ color: tripStitchTheme.primary }}
        />
      </ExperienceGlassCard>

      <div>
        <SectionLabel action="VIEW ALL" explainerId="MEMORY-001" momentTypeCode={momentTypeCode}>Memory Timeline</SectionLabel>
        <ExperienceGlassCard>
          {timeline.length === 0 ? (
            <p className="text-sm" style={{ color: tripStitchTheme.onSurfaceVariant }}>
              No timeline events yet
            </p>
          ) : (
            <div className="space-y-4">
              {timeline.map((item, index) => (
                <div key={item.event_id ?? item.title} className="flex items-center gap-3">
                  <MaterialIcon
                    name={item.is_complete || index === 0 ? "check_circle" : "radio_button_unchecked"}
                    style={{ color: tripStitchTheme.primary }}
                  />
                  <div>
                    <p className="font-semibold" style={{ color: tripStitchTheme.onSurface }}>
                      {item.title}
                    </p>
                    {item.date_label ? (
                      <p className="text-xs" style={{ color: tripStitchTheme.onSurfaceVariant }}>
                        {item.date_label}
                      </p>
                    ) : null}
                  </div>
                </div>
              ))}
            </div>
          )}
        </ExperienceGlassCard>
      </div>

      <div>
        <SectionLabel explainerId="MEMORY-002" momentTypeCode={momentTypeCode}>Milestone Wall</SectionLabel>
        {milestones.length === 0 ? (
          <ExperienceGlassCard>
            <p className="text-sm" style={{ color: tripStitchTheme.onSurfaceVariant }}>
              No milestones yet
            </p>
          </ExperienceGlassCard>
        ) : (
          <div className="flex flex-wrap gap-4">
            {milestones.map((m) => (
              <div key={m.milestone_id ?? m.label} className="text-center">
                <div
                  className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl border"
                  style={{
                    background: tripStitchTheme.surfaceContainerHigh,
                    borderColor: "rgba(255,255,255,0.05)",
                  }}
                >
                  <MaterialIcon name={m.icon ?? "star"} style={{ color: tripStitchTheme.primary }} />
                </div>
                <p className="mt-2 text-xs" style={{ color: tripStitchTheme.onSurface }}>
                  {m.label}
                </p>
              </div>
            ))}
          </div>
        )}
      </div>

      <div>
        <SectionLabel explainerId="MEMORY-007" momentTypeCode={momentTypeCode}>Memory Highlights</SectionLabel>
        <ExperienceGlassCard>
          {highlights.length === 0 ? (
            <p className="text-sm" style={{ color: tripStitchTheme.onSurfaceVariant }}>
              No highlights yet
            </p>
          ) : (
            <div className="space-y-3">
              {highlights.map((h) => (
                <div
                  key={h.highlight_id ?? h.label}
                  className="flex items-center gap-3 rounded-xl p-3"
                  style={{ background: `${tripStitchTheme.surfaceContainerHigh}80` }}
                >
                  <MaterialIcon name={h.icon ?? "favorite"} style={{ color: tripStitchTheme.primary }} />
                  <p className="text-sm" style={{ color: tripStitchTheme.onSurface }}>
                    {h.label}
                  </p>
                </div>
              ))}
            </div>
          )}
        </ExperienceGlassCard>
      </div>

      <div>
        <SectionLabel action={galleryOverflow > 0 ? `+${galleryOverflow} More` : undefined} explainerId="MEMORY-004" momentTypeCode={momentTypeCode}>
          Moments Captured
        </SectionLabel>
        <ExperienceGlassCard>
          {gallery.length === 0 ? (
            <p className="text-sm" style={{ color: tripStitchTheme.onSurfaceVariant }}>
              No memories captured yet
            </p>
          ) : (
            <div className="grid grid-cols-2 gap-2 sm:grid-cols-4">
              {gallery.slice(0, 3).map((item) => (
                <div
                  key={item.memory_id ?? item.title}
                  className="relative aspect-square overflow-hidden rounded-xl"
                  style={{ background: tripStitchTheme.surfaceContainerHigh }}
                >
                  {item.image_url ? (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img
                      src={resolveMediaUrl(item.image_url) ?? item.image_url}
                      alt={item.title || "Memory"}
                      className="h-full w-full object-cover transition-transform duration-500 hover:scale-110"
                    />
                  ) : null}
                  {item.memory_id ? (
                    <button
                      type="button"
                      aria-label={`Delete ${item.title || "memory"}`}
                      disabled={deletingId === item.memory_id}
                      onClick={() => void handleDeleteMemory(item.memory_id!)}
                      className="absolute right-1.5 top-1.5 flex h-7 w-7 items-center justify-center rounded-full bg-black/55 text-white transition-opacity hover:bg-black/75 disabled:opacity-50"
                    >
                      <MaterialIcon name="delete" className="text-[14px]" />
                    </button>
                  ) : null}
                </div>
              ))}
              {galleryOverflow > 0 && gallery[3] ? (
                <div
                  className="relative aspect-square overflow-hidden rounded-xl"
                  style={{ background: tripStitchTheme.surfaceContainerHigh }}
                >
                  {gallery[3].image_url ? (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img
                      src={resolveMediaUrl(gallery[3].image_url) ?? gallery[3].image_url}
                      alt={gallery[3].title || "More memories"}
                      className="h-full w-full object-cover"
                    />
                  ) : null}
                  <div className="absolute inset-0 flex items-center justify-center bg-black/50">
                    <span className="text-sm font-semibold text-white">+{galleryOverflow}</span>
                  </div>
                </div>
              ) : null}
            </div>
          )}
        </ExperienceGlassCard>
      </div>

      <SunsetCta eyebrow="Add Memory" title="Preserve this moment" icon="add" onClick={onQuickAdd} />

      {hasExtras ? (
        <div>
          <button
            type="button"
            className="flex w-full items-center justify-between rounded-2xl px-4 py-3 text-left text-sm font-medium"
            style={{
              background: "rgba(255,255,255,0.03)",
              border: "1px solid rgba(255,255,255,0.08)",
              color: tripStitchTheme.onSurfaceVariant,
            }}
            onClick={() => setShowExtras((v) => !v)}
            aria-expanded={showExtras}
          >
            More insights
            <ChevronDown
              size={18}
              className={`transition-transform ${showExtras ? "rotate-180" : ""}`}
            />
          </button>
          {showExtras ? (
            <div className="mt-4 space-y-4">
              {intelligence?.insight ? (
                <ExperienceGlassCard>
                  <SectionLabel icon="auto_awesome" explainerId="MEMORY-010" momentTypeCode={momentTypeCode}>Memory Intelligence</SectionLabel>
                  <p className="text-sm leading-relaxed" style={{ color: tripStitchTheme.onSurface }}>
                    {intelligence.insight}
                  </p>
                  <div className="mt-4 flex gap-6">
                    {(intelligence.metrics ?? []).map((m) => (
                      <div key={m.label}>
                        <p
                          className="text-[10px] uppercase tracking-wider"
                          style={{ color: tripStitchTheme.onSurfaceVariant }}
                        >
                          {m.label}
                        </p>
                        <p className="font-bold" style={{ color: tripStitchTheme.primary }}>
                          {m.value}
                        </p>
                      </div>
                    ))}
                  </div>
                </ExperienceGlassCard>
              ) : null}

              {people.length > 0 ? (
                <div>
                  <SectionLabel explainerId="MEMORY-003" momentTypeCode={momentTypeCode}>People Impact</SectionLabel>
                  <ExperienceGlassCard>
                    <div className="space-y-3">
                      {people.map((person) => (
                        <div key={person.display_name} className="flex items-center gap-3">
                          <div
                            className="flex h-10 w-10 items-center justify-center rounded-full"
                            style={{ background: tripStitchTheme.surfaceContainerHigh }}
                          >
                            <MaterialIcon name="person" style={{ color: tripStitchTheme.primary }} />
                          </div>
                          <div>
                            <p className="font-semibold" style={{ color: tripStitchTheme.onSurface }}>
                              {person.display_name}
                            </p>
                            <p
                              className="text-[10px] uppercase tracking-wider"
                              style={{ color: tripStitchTheme.primary }}
                            >
                              {person.impact_label}
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </ExperienceGlassCard>
                </div>
              ) : null}

              {hub?.lessons_pattern ? (
                <ExperienceGlassCard>
                  <p
                    className="text-[10px] font-bold uppercase tracking-wider"
                    style={{ color: tripStitchTheme.onSurfaceVariant }}
                  >
                    Lessons & Patterns
                  </p>
                  <p className="mt-2 italic" style={{ color: tripStitchTheme.onSurface }}>
                    {hub.lessons_pattern}
                  </p>
                </ExperienceGlassCard>
              ) : null}

              {hub?.group_identity ? (
                <ExperienceGlassCard>
                  <p
                    className="text-[10px] font-bold uppercase tracking-wider"
                    style={{ color: tripStitchTheme.onSurfaceVariant }}
                  >
                    Group Identity
                  </p>
                  <p className="mt-2 text-xl font-bold" style={{ color: tripStitchTheme.onSurface }}>
                    {hub.group_identity}
                  </p>
                </ExperienceGlassCard>
              ) : null}

              {budget ? (
                <ExperienceGlassCard>
                  <p
                    className="text-[10px] font-bold uppercase tracking-wider"
                    style={{ color: tripStitchTheme.onSurfaceVariant }}
                  >
                    Budget Reflection
                  </p>
                  <div className="mt-3 grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-xs" style={{ color: tripStitchTheme.onSurfaceVariant }}>
                        Planned
                      </p>
                      <p style={{ color: tripStitchTheme.onSurface }}>{budget.planned_budget}</p>
                    </div>
                    <div>
                      <p className="text-xs" style={{ color: tripStitchTheme.onSurfaceVariant }}>
                        Actual
                      </p>
                      <p style={{ color: tripStitchTheme.primary }}>{budget.actual_spend}</p>
                    </div>
                  </div>
                  <p className="mt-2 text-sm" style={{ color: tripStitchTheme.onSurface }}>
                    Accuracy: {budget.budget_accuracy}
                  </p>
                  {budget.summary ? (
                    <p className="mt-1 text-sm" style={{ color: tripStitchTheme.primary }}>
                      {budget.summary}
                    </p>
                  ) : null}
                </ExperienceGlassCard>
              ) : null}
            </div>
          ) : null}
        </div>
      ) : null}
    </ExperienceScrollShell>
  );
}
