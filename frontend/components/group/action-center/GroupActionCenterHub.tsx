"use client";

import { useMemo, useState, type ReactNode } from "react";
import {
  Camera,
  CheckSquare,
  ChevronRight,
  Clock,
  Handshake,
  Megaphone,
  PlaneTakeoff,
  Search,
  Star,
  UserPlus,
  Vote,
  Wallet,
  PiggyBank,
  ListTodo,
} from "lucide-react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import {
  ACTION_CENTER_CATEGORY_LABELS,
  TRIP_HUB_CATEGORY_ORDER,
  searchActionCenterActions,
} from "@/lib/action-center/actionCenterMeta";
import { getFavoriteActionIds, toggleFavoriteAction } from "@/lib/action-center/actionCenterPrefs";
import type { ActionCenterCategory, QuickAddActionTemplate } from "@/lib/quick_add/types";

type HubProps = {
  templateId: string;
  templateLabel: string;
  heroTitle: string;
  heroSubtitle: string;
  /** Optional moment / stage chips (e.g. trip name) */
  contextChips?: string[];
  heroImageUrl?: string | null;
  actions: QuickAddActionTemplate[];
  suggested: QuickAddActionTemplate[];
  recentIds: string[];
  userId?: string;
  onSelect: (actionId: string) => void;
};

function ActionGlyph({ actionId }: { actionId: string }) {
  const { colors } = useThemeTokens();
  const props = { className: "size-5", style: { color: colors.primaryContainer } as const };
  switch (actionId) {
    case "PARTICIPANT":
      return <UserPlus {...props} />;
    case "PLANNING_ITEM":
      return <ListTodo {...props} />;
    case "BOOKING":
      return <PlaneTakeoff {...props} />;
    case "EXPENSE":
      return <Wallet {...props} />;
    case "CONTRIBUTION":
      return <PiggyBank {...props} />;
    case "BUDGET":
      return <Wallet {...props} />;
    case "VENDOR":
      return <Handshake {...props} />;
    case "ATTENDANCE":
      return <CheckSquare {...props} />;
    case "UPDATE":
      return <Megaphone {...props} />;
    case "MEMORY":
      return <Camera {...props} />;
    case "POLL":
      return <Vote {...props} />;
    default:
      return <ListTodo {...props} />;
  }
}

export function GroupActionCenterHub({
  templateId,
  templateLabel,
  heroTitle,
  heroSubtitle,
  contextChips,
  heroImageUrl,
  actions,
  suggested,
  recentIds,
  userId = "local",
  onSelect,
}: HubProps) {
  const { colors } = useThemeTokens();
  const [query, setQuery] = useState("");
  const [favorites, setFavorites] = useState(() => getFavoriteActionIds(userId, templateId));

  const filtered = useMemo(() => searchActionCenterActions(actions, query), [actions, query]);
  const byId = useMemo(() => new Map(actions.map((a) => [a.action_id, a])), [actions]);

  const frequentlyUsed = useMemo(() => {
    const ids = [...new Set([...favorites, ...recentIds])];
    return ids.map((id) => byId.get(id)).filter(Boolean) as QuickAddActionTemplate[];
  }, [favorites, recentIds, byId]);

  const isTrip = templateId === "group.trip";
  const categoryOrder: ActionCenterCategory[] = isTrip
    ? TRIP_HUB_CATEGORY_ORDER
    : ["money", "planning", "people", "capture", "administration", "support"];

  const chips = useMemo(() => {
    const raw = contextChips?.length
      ? contextChips
      : [templateLabel, isTrip ? "Trip Experience" : "Action Center"];
    return Array.from(new Set(raw.filter(Boolean)));
  }, [contextChips, templateLabel, isTrip]);

  const grouped = useMemo(() => {
    return categoryOrder
      .map((cat) => ({
        id: cat,
        label: ACTION_CENTER_CATEGORY_LABELS[cat],
        items: filtered.filter((a) => (a.category ?? "administration") === cat),
      }))
      .filter((g) => g.items.length > 0);
  }, [filtered, categoryOrder]);

  function tile(action: QuickAddActionTemplate) {
    const fav = favorites.includes(action.action_id);
    return (
      <div
        key={action.action_id}
        className="flex w-full items-center gap-2 rounded-3xl border p-4 transition active:scale-[0.98]"
        style={{
          background: `${colors.surfaceContainer}A6`,
          borderColor: `${colors.textSecondary}14`,
          backdropFilter: "blur(16px)",
        }}
      >
        <button
          type="button"
          className="flex flex-1 items-center justify-between text-left"
          onClick={() => onSelect(action.action_id)}
        >
          <div className="flex items-center gap-4">
            <div
              className="flex size-12 items-center justify-center rounded-xl"
              style={{ background: `${colors.primaryContainer}1A` }}
            >
              <ActionGlyph actionId={action.action_id} />
            </div>
            <div>
              <p className="text-lg font-semibold" style={{ color: colors.textPrimary }}>
                {action.label}
              </p>
              <p className="text-sm" style={{ color: colors.textSecondary }}>
                {action.subtitle ?? ""}
              </p>
              {action.estimated_time_sec != null ? (
                <p className="mt-0.5 flex items-center gap-1 text-[10px]" style={{ color: colors.textSecondary }}>
                  <Clock className="size-3" /> ~{action.estimated_time_sec} sec
                </p>
              ) : null}
            </div>
          </div>
          <ChevronRight className="size-5 shrink-0" style={{ color: colors.textSecondary }} />
        </button>
        {action.supports?.favorites !== false ? (
          <button
            type="button"
            aria-label={fav ? "Unpin favorite" : "Pin favorite"}
            className="rounded-full p-2"
            onClick={() => setFavorites(toggleFavoriteAction(userId, templateId, action.action_id))}
          >
            <Star
              className="size-4"
              fill={fav ? colors.primaryContainer : "transparent"}
              style={{ color: colors.primaryContainer }}
            />
          </button>
        ) : null}
      </div>
    );
  }

  return (
    <div className="space-y-8 pb-6">
      <div className="flex gap-2 overflow-x-auto pb-1">
        {chips.map((chip, index) => (
          <span
            key={`${index}-${chip}`}
            className="whitespace-nowrap rounded-full border px-3 py-1 text-xs font-medium"
            style={{
              borderColor: `${colors.primaryContainer}33`,
              background: `${colors.primaryContainer}1A`,
              color: colors.primaryContainer,
            }}
          >
            {chip}
          </span>
        ))}
      </div>

      <div className="relative h-[220px] overflow-hidden rounded-3xl md:h-[280px]">
        {heroImageUrl ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img src={heroImageUrl} alt="" className="h-full w-full object-cover" />
        ) : (
          <div
            className="h-full w-full"
            style={{
              background: `linear-gradient(135deg, ${colors.primaryContainer} 0%, ${colors.primaryContainer}88 40%, ${colors.surfaceContainer} 100%)`,
            }}
          />
        )}
        <div
          className="absolute inset-0"
          style={{
            background: `linear-gradient(to top, ${colors.background} 0%, transparent 55%)`,
          }}
        />
        <div className="absolute inset-x-0 bottom-0 p-6">
          <h3 className="text-2xl font-semibold md:text-3xl" style={{ color: colors.textPrimary }}>
            {heroTitle}
          </h3>
          <p className="mt-2 max-w-[85%] text-sm md:text-base" style={{ color: colors.textSecondary }}>
            {heroSubtitle}
          </p>
        </div>
      </div>

      <div className="relative">
        <Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2" style={{ color: colors.textSecondary }} />
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search actions…"
          className="w-full rounded-2xl py-3.5 pl-10 pr-3 text-sm"
          style={{
            background: colors.surfaceContainer,
            color: colors.textPrimary,
            border: `1px solid ${colors.textSecondary}20`,
          }}
          aria-label="Search actions"
        />
      </div>

      {!query && suggested.length > 0 ? (
        <HubSection title="Suggested">{suggested.map(tile)}</HubSection>
      ) : null}

      {!query && frequentlyUsed.length > 0 ? (
        <HubSection title="Frequently used">{frequentlyUsed.map(tile)}</HubSection>
      ) : null}

      {grouped.map((g) => (
        <HubSection key={g.id} title={g.label}>
          {g.items.map(tile)}
        </HubSection>
      ))}

      {filtered.length === 0 ? (
        <p className="py-8 text-center text-sm" style={{ color: colors.textSecondary }}>
          No actions match “{query}”.
        </p>
      ) : null}
    </div>
  );
}

function HubSection({ title, children }: { title: string; children: ReactNode }) {
  const { colors } = useThemeTokens();
  return (
    <section className="space-y-4">
      <h4 className="text-xs font-semibold uppercase tracking-widest" style={{ color: colors.primaryContainer }}>
        {title}
      </h4>
      <div className="space-y-3">{children}</div>
    </section>
  );
}
