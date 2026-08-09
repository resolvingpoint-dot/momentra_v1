"use client";

import { useEffect, useMemo, useState } from "react";
import { Image } from "lucide-react";
import { GroupSkeletonBlocks } from "@/components/group/shared/skeleton/GroupSkeletonBlocks";
import { useGroupLivingMoments, useGroupMoments, useGroupPurchaseMoments } from "@/hooks/useGroupTabCache";
import {
  deleteLivingActivity,
  deleteTripActivity,
  type GroupMomentsStatTile,
  type LivingMomentsViewResponse,
  type PurchaseMomentsViewResponse,
  type TripMomentsViewResponse,
  type TripPulseResponse,
} from "@/lib/api/group";
import { WidgetInfoButton } from "@/components/personal/shared/WidgetInfoButton";
import { resolveMediaUrl } from "@/lib/api/client";
import { ExperienceGlassCard } from "./ui/ExperienceGlassCard";
import { MaterialIcon } from "./ui/MaterialIcon";
import { MetricTile, SectionLabel, ExperienceScrollShell } from "./ui/ExperienceUiParts";
import { tripStitchShellStyle, tripStitchTheme } from "./ui/tripStitchTheme";

type ActiveMomentsProps = {
  momentId: string;
  onQuickAdd?: () => void;
  bottomPadding?: number;
  reloadKey?: number;
  source?: "trip" | "purchase" | "living";
};

type ItineraryItem = {
  id: string;
  title: string;
  time: string;
  icon: string;
  isFirst: boolean;
};

type GalleryItem = {
  id: string;
  label: string;
  imageUrl?: string | null;
};

type EventItem = {
  id: string;
  title: string;
  time: string;
  icon: string;
  accent: string;
};

export function ActiveMoments({
  momentId,
  onQuickAdd,
  bottomPadding = 0,
  reloadKey = 0,
  source = "trip",
}: ActiveMomentsProps) {
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

  useEffect(() => {
    if (reloadKey > 0) {
      void revalidate();
    }
  }, [reloadKey, revalidate]);

  if (loading && !moments) {
    return (
      <ExperienceScrollShell bottomPadding={bottomPadding} onRefresh={reload}>
        <GroupSkeletonBlocks variant="moments" />
      </ExperienceScrollShell>
    );
  }

  if (error && !moments) {
    return (
      <div className="flex flex-col items-center justify-center p-10 text-center" style={tripStitchShellStyle}>
        <Image size={40} style={{ color: tripStitchTheme.onSurfaceVariant }} />
        <p className="mt-3 text-sm" style={{ color: tripStitchTheme.onSurfaceVariant }}>
          {error || "Unable to load this section."}
        </p>
        <button type="button" className="mt-3 text-sm font-semibold underline" onClick={() => void reload()}>
          Retry
        </button>
      </div>
    );
  }

  if (!moments) return null;

  if (isTrip) {
    return (
      <TripMomentsMockBody
        momentId={momentId}
        source={source}
        moments={moments as TripMomentsViewResponse}
        pulse={null}
        onQuickAdd={onQuickAdd}
        bottomPadding={bottomPadding}
        onRefresh={reload}
        momentTypeCode={momentTypeCode}
      />
    );
  }

  return (
    <OpsHubBody
      moments={moments}
      isPurchase={isPurchase}
      isLiving={isLiving}
      onQuickAdd={onQuickAdd}
      bottomPadding={bottomPadding}
      onRefresh={reload}
      momentTypeCode={momentTypeCode}
    />
  );
}

function TripMomentsMockBody({
  momentId,
  source = "trip",
  moments,
  pulse,
  onQuickAdd,
  bottomPadding,
  onRefresh,
  momentTypeCode,
}: {
  momentId: string;
  source?: "trip" | "purchase" | "living";
  moments: TripMomentsViewResponse;
  pulse: TripPulseResponse | null;
  onQuickAdd?: () => void;
  bottomPadding: number;
  onRefresh?: () => void | Promise<void>;
  momentTypeCode: string;
}) {
  const hub = moments.operations_hub;
  const displayName = moments.trip_name || hub.core_summary.moment_name || "Untitled moment";
  const eyebrow = hub.core_summary.eyebrow || "Shared Experience";
  const statTiles = useMemo(() => tripHeroStatTiles(moments, pulse), [moments, pulse]);
  const itinerary = useMemo(() => tripItineraryItems(moments), [moments]);
  const gallery = useMemo(() => tripGalleryItems(moments), [moments]);
  const events = useMemo(() => tripUpcomingEvents(moments), [moments]);
  const overflowCount = Math.max(0, gallery.length - 3);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  async function handleDeleteMemory(memoryId: string) {
    if (!memoryId || memoryId.startsWith("gallery-")) return;
    if (!window.confirm("Delete this memory photo? This cannot be undone.")) return;
    setDeletingId(memoryId);
    try {
      if (source === "living") await deleteLivingActivity(momentId, memoryId);
      else await deleteTripActivity(momentId, memoryId);
      await onRefresh?.();
    } catch (err: unknown) {
      window.alert(err instanceof Error ? err.message : "Could not delete memory photo");
    } finally {
      setDeletingId(null);
    }
  }

  return (
    <ExperienceScrollShell
      bottomPadding={bottomPadding}
      className="font-[family-name:var(--font-plus-jakarta)]"
      style={tripStitchShellStyle}
      onRefresh={onRefresh}
    >
      <ExperienceGlassCard glow accentBorder="left" className="relative overflow-hidden">
        <div className="pointer-events-none absolute right-4 top-2 opacity-10">
          <MaterialIcon name="flight_takeoff" className="text-[120px]" style={{ color: tripStitchTheme.primary }} />
        </div>
        <div className="relative z-10">
          <div className="mb-6 flex items-start justify-between gap-3">
            <div>
              <div className="mb-1 flex items-center gap-2">
                <MaterialIcon name="palette" className="text-[16px]" style={{ color: tripStitchTheme.primary }} />
                <span
                  className="text-[10px] font-bold uppercase tracking-widest"
                  style={{ color: tripStitchTheme.primary }}
                >
                  {eyebrow.toUpperCase()}
                </span>
              </div>
              <h2 className="text-2xl font-semibold" style={{ color: tripStitchTheme.onSurface }}>
                {displayName}
              </h2>
            </div>
            <span
              className="shrink-0 rounded-full px-3 py-1 text-[10px] font-medium uppercase"
              style={{ background: `${tripStitchTheme.primary}33`, color: tripStitchTheme.primary }}
            >
              {moments.stage_badge}
            </span>
          </div>
          <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
            {statTiles.map((tile) => (
              <MetricTile
                key={`${tile.label}-${tile.value}`}
                label={tile.label}
                value={tile.value}
                valueColor={tile.highlight ? tripStitchTheme.primary : undefined}
              />
            ))}
          </div>
        </div>
      </ExperienceGlassCard>

      <SectionLabel icon="calendar_month" action={itinerary.length > 0 ? "View all" : undefined} explainerId="MOMENT-ITINERARY" momentTypeCode={momentTypeCode}>
        Itinerary
      </SectionLabel>
      {itinerary.length === 0 ? (
        <EmptyMomentsCard
          icon="calendar_month"
          message="No itinerary yet"
          actionLabel="Plan your trip"
          onAction={onQuickAdd}
        />
      ) : (
        <ExperienceGlassCard className="relative">
          <div
            className="absolute bottom-8 left-[27px] top-8 w-px"
            style={{ background: "rgba(255,255,255,0.10)" }}
          />
          <div className="relative z-10 space-y-6">
            {itinerary.map((item) => (
              <div key={item.id} className="flex gap-4">
                <div
                  className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full"
                  style={{
                    background: item.isFirst ? tripStitchTheme.primaryContainer : tripStitchTheme.surfaceContainerHigh,
                    border: item.isFirst ? undefined : `1px solid ${tripStitchTheme.primary}4D`,
                  }}
                >
                  <MaterialIcon
                    name={item.icon}
                    className="text-[16px]"
                    style={{ color: item.isFirst ? tripStitchTheme.onPrimaryContainer : tripStitchTheme.primary }}
                  />
                </div>
                <div className="min-w-0 flex-1">
                  <p className="font-semibold" style={{ color: tripStitchTheme.onSurface }}>
                    {item.title}
                  </p>
                  {item.time ? (
                    <p className="text-[12px]" style={{ color: tripStitchTheme.onSurfaceVariant }}>
                      {item.time}
                    </p>
                  ) : null}
                </div>
              </div>
            ))}
          </div>
        </ExperienceGlassCard>
      )}

      <SectionLabel
        icon="photo_library"
        action={overflowCount > 0 ? `+${overflowCount} More` : undefined}
        explainerId="MOMENT-GRID"
        momentTypeCode={momentTypeCode}
      >
        Moments Grid
      </SectionLabel>
      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        {gallery.slice(0, 3).map((item) => (
          <div
            key={item.id}
            className="relative aspect-[4/5] overflow-hidden rounded-2xl"
            style={{ background: tripStitchTheme.surfaceContainerHigh }}
          >
            {item.imageUrl ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                src={resolveMediaUrl(item.imageUrl) ?? item.imageUrl}
                alt={item.label}
                className="h-full w-full object-cover"
              />
            ) : (
              <div className="flex h-full items-center justify-center">
                <MaterialIcon
                  name="photo"
                  className="text-[48px]"
                  style={{ color: `${tripStitchTheme.onSurfaceVariant}33` }}
                />
              </div>
            )}
            {item.label ? (
              <div className="absolute inset-x-0 bottom-0 bg-gradient-to-t from-black/70 to-transparent p-3">
                <p className="text-[10px] font-bold uppercase tracking-wider text-white">{item.label}</p>
              </div>
            ) : null}
            {item.id && !item.id.startsWith("gallery-") ? (
              <button
                type="button"
                aria-label={`Delete ${item.label || "memory"}`}
                disabled={deletingId === item.id}
                onClick={() => void handleDeleteMemory(item.id)}
                className="absolute right-2 top-2 flex h-8 w-8 items-center justify-center rounded-full bg-black/55 text-white transition-opacity hover:bg-black/75 disabled:opacity-50"
              >
                <MaterialIcon name="delete" className="text-[16px]" />
              </button>
            ) : null}
          </div>
        ))}
        <button
          type="button"
          onClick={onQuickAdd}
          className="flex aspect-[4/5] flex-col items-center justify-center rounded-2xl transition-colors hover:bg-white/5"
          style={{ border: `1px solid ${tripStitchTheme.primary}4D` }}
        >
          <MaterialIcon name="add_photo_alternate" className="text-[40px]" style={{ color: tripStitchTheme.primary }} />
          <p className="mt-2 text-[12px] font-medium uppercase tracking-wider" style={{ color: tripStitchTheme.primary }}>
            Add
          </p>
        </button>
      </div>

      <SectionLabel icon="event" explainerId="MOMENT-UPCOMING" momentTypeCode={momentTypeCode}>Upcoming Events</SectionLabel>
      {events.length === 0 ? (
        <EmptyMomentsCard icon="event" message="No upcoming events" />
      ) : (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          {events.map((event) => {
            const tone =
              event.accent === "secondary"
                ? tripStitchTheme.secondary
                : event.accent === "tertiary"
                  ? tripStitchTheme.tertiary
                  : tripStitchTheme.primary;
            return (
              <ExperienceGlassCard key={event.id} className="!p-4">
                <div className="flex items-center gap-4">
                  <div
                    className="flex h-14 w-14 shrink-0 items-center justify-center rounded-xl"
                    style={{ background: `${tone}1A`, color: tone }}
                  >
                    <MaterialIcon name={event.icon} />
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="font-semibold" style={{ color: tripStitchTheme.onSurface }}>
                      {event.title}
                    </p>
                    {event.time ? (
                      <p className="text-[12px]" style={{ color: tripStitchTheme.onSurfaceVariant }}>
                        {event.time}
                      </p>
                    ) : null}
                  </div>
                  <MaterialIcon name="chevron_right" style={{ color: tripStitchTheme.onSurfaceVariant }} />
                </div>
              </ExperienceGlassCard>
            );
          })}
        </div>
      )}

      <button
        type="button"
        onClick={onQuickAdd}
        className="flex w-full items-center justify-between rounded-[24px] p-6 text-left transition-transform hover:-translate-y-0.5"
        style={{
          background: `linear-gradient(135deg, ${tripStitchTheme.primaryContainer} 0%, ${tripStitchTheme.primary} 100%)`,
          boxShadow: "0 10px 40px rgba(255,122,61,0.20)",
          color: tripStitchTheme.onPrimary,
        }}
      >
        <div>
          <p className="text-[12px] font-semibold uppercase tracking-wider opacity-80">Create Moment</p>
          <p className="text-2xl font-bold">Capture this trip</p>
        </div>
        <div className="flex h-12 w-12 items-center justify-center rounded-full bg-white/20">
          <MaterialIcon name="add" className="text-[28px]" />
        </div>
      </button>
    </ExperienceScrollShell>
  );
}

function EmptyMomentsCard({
  icon,
  message,
  actionLabel,
  onAction,
}: {
  icon: string;
  message: string;
  actionLabel?: string;
  onAction?: () => void;
}) {
  return (
    <ExperienceGlassCard>
      <div className="flex flex-col items-center gap-3 py-6 text-center">
        <MaterialIcon name={icon} className="text-[32px]" style={{ color: `${tripStitchTheme.onSurfaceVariant}80` }} />
        <p className="text-sm" style={{ color: tripStitchTheme.onSurfaceVariant }}>
          {message}
        </p>
        {actionLabel && onAction ? (
          <button
            type="button"
            onClick={onAction}
            className="text-[10px] font-bold uppercase tracking-wider"
            style={{ color: tripStitchTheme.primary }}
          >
            {actionLabel}
          </button>
        ) : null}
      </div>
    </ExperienceGlassCard>
  );
}

function OpsHubBody({
  moments,
  isPurchase,
  isLiving,
  onQuickAdd,
  bottomPadding,
  onRefresh,
  momentTypeCode,
}: {
  moments: PurchaseMomentsViewResponse | LivingMomentsViewResponse | TripMomentsViewResponse;
  isPurchase: boolean;
  isLiving: boolean;
  onQuickAdd?: () => void;
  bottomPadding: number;
  onRefresh?: () => void | Promise<void>;
  momentTypeCode: string;
}) {
  const hub = moments.operations_hub;
  const displayName =
    "trip_name" in moments && moments.trip_name
      ? moments.trip_name
      : "moment_name" in moments
        ? moments.moment_name
        : "Untitled moment";
  const statTiles = heroStatTiles(moments);
  const eyebrow = hub.core_summary.eyebrow;

  return (
    <ExperienceScrollShell
      bottomPadding={bottomPadding}
      className="font-[family-name:var(--font-plus-jakarta)]"
      style={tripStitchShellStyle}
      onRefresh={onRefresh}
    >
      <ExperienceGlassCard glow accentBorder="left" className="relative overflow-hidden">
        <div className="relative z-10">
          <div className="mb-6 flex items-start justify-between">
            <div>
              <span
                className="text-[10px] font-bold uppercase tracking-widest"
                style={{ color: tripStitchTheme.primary }}
              >
                {(eyebrow || (isPurchase ? "Shared Purchase" : isLiving ? "Shared Living" : "Shared Experience")).toUpperCase()}
              </span>
              <h2 className="text-2xl font-semibold" style={{ color: tripStitchTheme.onSurface }}>
                {displayName}
              </h2>
            </div>
            <span
              className="rounded-full px-3 py-1 text-[10px] font-medium uppercase"
              style={{ background: `${tripStitchTheme.primary}33`, color: tripStitchTheme.primary }}
            >
              {moments.stage_badge}
            </span>
          </div>
          <div className="grid grid-cols-2 gap-4">
            {statTiles.map((tile) => (
              <MetricTile
                key={`${tile.label}-${tile.value}`}
                label={tile.label}
                value={tile.value}
                valueColor={tile.highlight ? tripStitchTheme.primary : undefined}
              />
            ))}
          </div>
        </div>
      </ExperienceGlassCard>

      <SectionLabel action="View all" explainerId="MOMENT-002" momentTypeCode={momentTypeCode}>People & Roles</SectionLabel>
      <ExperienceGlassCard>
        {hub.people_roles?.primary ? (
          <div className="mb-4 flex items-center gap-3">
            <div
              className="flex h-12 w-12 items-center justify-center rounded-full"
              style={{ background: tripStitchTheme.surfaceContainerHigh }}
            >
              <MaterialIcon name="star" style={{ color: tripStitchTheme.primary }} />
            </div>
            <div>
              <p className="font-semibold" style={{ color: tripStitchTheme.onSurface }}>
                {hub.people_roles.primary.display_name}
              </p>
              <p
                className="text-[10px] font-bold uppercase tracking-wider"
                style={{ color: tripStitchTheme.primary }}
              >
                {hub.people_roles.primary.role_label}
              </p>
            </div>
          </div>
        ) : null}
        <div className="flex gap-4">
          {(hub.people_roles?.role_counts ?? []).map((role) => (
            <div
              key={role.label}
              className="rounded-full px-5 py-3 text-center"
              style={{ background: tripStitchTheme.surfaceContainerHigh }}
            >
              <p className="text-lg font-bold" style={{ color: tripStitchTheme.onSurface }}>
                {role.count}
              </p>
              <p
                className="text-[10px] uppercase tracking-wider"
                style={{ color: tripStitchTheme.onSurfaceVariant }}
              >
                {role.label}
              </p>
            </div>
          ))}
        </div>
      </ExperienceGlassCard>

      <SectionLabel action="View all" explainerId="MOMENT-003" momentTypeCode={momentTypeCode}>Money Status</SectionLabel>
      <ExperienceGlassCard>
        <p className="mb-3 text-sm" style={{ color: tripStitchTheme.onSurfaceVariant }}>
          {hub.money_status?.progress_label}
        </p>
        <div className="mb-4 h-2 overflow-hidden rounded-full" style={{ background: tripStitchTheme.surfaceContainerHigh }}>
          <div
            className="h-full rounded-full"
            style={{ width: `${hub.money_status?.progress_percent ?? 0}%`, background: tripStitchTheme.primary }}
          />
        </div>
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          {(hub.money_status?.columns ?? []).map((col) => (
            <div key={col.label} className="text-center">
              <p
                className="text-[10px] uppercase tracking-wider"
                style={{ color: tripStitchTheme.onSurfaceVariant }}
              >
                {col.label}
              </p>
              <p
                className="font-semibold"
                style={{ color: col.highlight ? tripStitchTheme.primary : tripStitchTheme.onSurface }}
              >
                {col.value}
              </p>
            </div>
          ))}
        </div>
      </ExperienceGlassCard>

      <SectionLabel action="View all" explainerId="MOMENT-004" momentTypeCode={momentTypeCode}>Activity & Operations</SectionLabel>
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3">
        {(hub.activity_ops ?? []).map((tile) => (
          <ExperienceGlassCard key={tile.tile_id ?? tile.label} className="!p-4 text-center">
            <MaterialIcon name={tile.icon ?? "event"} style={{ color: tripStitchTheme.primary }} />
            <p className="mt-2 text-xl font-bold" style={{ color: tripStitchTheme.onSurface }}>
              {tile.value}
            </p>
            <p
              className="text-[10px] uppercase tracking-wider"
              style={{ color: tripStitchTheme.onSurfaceVariant }}
            >
              {tile.label}
            </p>
          </ExperienceGlassCard>
        ))}
      </div>

      {(hub.assets ?? []).length > 0 ? (
        <>
          <SectionLabel action="View all" explainerId="MOMENT-005" momentTypeCode={momentTypeCode}>Assets & Resources</SectionLabel>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            {hub.assets!.map((asset) => (
              <div key={asset.asset_id ?? asset.label} className="text-center">
                <div
                  className="mx-auto flex h-14 w-14 items-center justify-center rounded-full"
                  style={{ background: tripStitchTheme.surfaceContainerHigh }}
                >
                  <MaterialIcon name={asset.icon ?? "folder"} style={{ color: tripStitchTheme.primary }} />
                </div>
                <p className="mt-2 text-[10px]" style={{ color: tripStitchTheme.onSurfaceVariant }}>
                  {asset.label}
                </p>
              </div>
            ))}
          </div>
        </>
      ) : null}

      {(hub.decisions ?? []).length > 0 ? (
        <>
          <SectionLabel action="VIEW ALL" explainerId="MOMENT-006" momentTypeCode={momentTypeCode}>Decisions & Governance</SectionLabel>
          <div className="space-y-3">
            {hub.decisions!.map((d) => (
              <ExperienceGlassCard key={d.decision_id ?? d.title} className="!p-4">
                <div className="flex items-center gap-3">
                  <MaterialIcon
                    name={d.icon ?? "how_to_vote"}
                    style={{ color: d.is_active ? tripStitchTheme.primary : tripStitchTheme.onSurfaceVariant }}
                  />
                  <div className="flex-1">
                    <p className="font-semibold" style={{ color: tripStitchTheme.onSurface }}>
                      {d.title}
                    </p>
                    <p
                      className="text-[10px] uppercase tracking-wider"
                      style={{
                        color: d.is_active ? tripStitchTheme.primary : tripStitchTheme.onSurfaceVariant,
                      }}
                    >
                      {d.status_label}
                    </p>
                  </div>
                </div>
              </ExperienceGlassCard>
            ))}
          </div>
        </>
      ) : null}

      <ExperienceGlassCard glow accentBorder="left">
        <div className="mb-2 flex items-center gap-0.5">
          <h3 className="text-lg font-bold" style={{ color: tripStitchTheme.onSurface }}>
            Current State Snapshot
          </h3>
          <WidgetInfoButton
            explainerId="MOMENT-007"
            momentTypeCode={momentTypeCode}
            domain="group"
          />
        </div>
        <p className="mb-4 text-sm" style={{ color: tripStitchTheme.onSurfaceVariant }}>
          Stage: {hub.current_state?.stage_label}
        </p>
        <ul className="mb-4 space-y-2">
          {(hub.current_state?.focus_items ?? []).map((item) => (
            <li key={item.label} className="flex items-center gap-2 text-sm" style={{ color: tripStitchTheme.onSurface }}>
              <MaterialIcon
                name={item.is_complete ? "check_circle" : "radio_button_unchecked"}
                style={{
                  color: item.is_complete ? tripStitchTheme.primary : tripStitchTheme.onSurfaceVariant,
                }}
              />
              {item.label}
            </li>
          ))}
        </ul>
        <button
          type="button"
          onClick={onQuickAdd}
          className="w-full rounded-2xl py-3 text-sm font-bold uppercase tracking-wide"
          style={{ background: `${tripStitchTheme.primary}22`, color: tripStitchTheme.primary }}
        >
          {hub.current_state?.cta_label || "TAKE NEXT ACTION"}
        </button>
      </ExperienceGlassCard>
    </ExperienceScrollShell>
  );
}

function tripHeroStatTiles(
  moments: TripMomentsViewResponse,
  pulse: TripPulseResponse | null,
): GroupMomentsStatTile[] {
  const tiles = moments.operations_hub.core_summary.stat_tiles ?? [];
  if (tiles.length > 0) return tiles;
  const stats = pulse?.stats;
  if (!stats) return defaultStatTiles();
  const expenseMinor = stats.total_expenses_minor ?? 0;
  const expenseLabel = expenseMinor > 0 ? `₹${Math.round(expenseMinor / 100)}` : "—";
  const participants = Math.max(stats.guests_joined ?? 0, stats.participants_joined ?? 0);
  return [
    { label: "Participants", value: String(participants) },
    { label: "Bookings", value: String(stats.confirmed_bookings ?? 0) },
    { label: "Activities", value: String(stats.active_plan_items ?? 0) },
    { label: "Expenses", value: expenseLabel, highlight: expenseMinor > 0 },
  ];
}

function tripItineraryItems(moments: TripMomentsViewResponse): ItineraryItem[] {
  return (moments.memory_hub?.timeline ?? []).map((item, index) => ({
    id: item.event_id || `timeline-${index}`,
    title: item.title,
    time: item.date_label ?? "",
    icon: itineraryIconFor(item.title, index === 0),
    isFirst: index === 0 || Boolean(item.is_complete && index === 0),
  }));
}

function tripGalleryItems(moments: TripMomentsViewResponse): GalleryItem[] {
  const fromHub = (moments.memory_hub?.gallery ?? []).map((item, index) => ({
    id: item.memory_id || `gallery-${index}`,
    label: item.title || "Memory",
    imageUrl: item.image_url,
  }));
  const fromCaptured = (moments.captured_memories ?? [])
    .filter((m) => Boolean(m.title || m.image_url))
    .map((m) => ({
      id: m.id,
      label: m.title || "Memory",
      imageUrl: m.image_url,
    }));
  return [...fromHub, ...fromCaptured];
}

function tripUpcomingEvents(moments: TripMomentsViewResponse): EventItem[] {
  const feed = moments.memory_feed ?? [];
  if (feed.length > 0) {
    return feed.map((item, index) => ({
      id: item.id || `feed-${index}`,
      title: item.title,
      time: item.timestamp_label || item.subtitle || "",
      icon: item.icon || item.activity_type || "event",
      accent: item.accent || "primary",
    }));
  }
  // Incomplete timeline rows can stand in as upcoming when feed is empty.
  return (moments.memory_hub?.timeline ?? [])
    .filter((item) => item.is_complete === false)
    .map((item, index) => ({
      id: item.event_id || `upcoming-${index}`,
      title: item.title,
      time: item.date_label ?? "",
      icon: itineraryIconFor(item.title, false),
      accent: index % 2 === 0 ? "primary" : "secondary",
    }));
}

function itineraryIconFor(title: string, isFirst: boolean): string {
  if (isFirst) return "flag";
  const lower = title.toLowerCase();
  if (lower.includes("beach")) return "beach_access";
  if (lower.includes("dinner") || lower.includes("food") || lower.includes("restaurant")) return "restaurant";
  if (lower.includes("boat") || lower.includes("cruise")) return "directions_boat";
  if (lower.includes("book")) return "hotel";
  return "event";
}

function heroStatTiles(moments: {
  operations_hub: { core_summary: { stat_tiles?: GroupMomentsStatTile[] } };
}): GroupMomentsStatTile[] {
  const tiles = moments.operations_hub.core_summary.stat_tiles ?? [];
  if (tiles.length > 0) return tiles;
  return defaultStatTiles();
}

function defaultStatTiles(): GroupMomentsStatTile[] {
  return [
    { label: "Participants", value: "0" },
    { label: "Bookings", value: "0" },
    { label: "Activities", value: "0" },
    { label: "Expenses", value: "—" },
  ];
}
