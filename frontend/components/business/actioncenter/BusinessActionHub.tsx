"use client";

import { useMemo, useState, type ReactNode } from "react";
import {
  Briefcase,
  ChevronRight,
  Clock,
  DollarSign,
  FileText,
  Search,
  Shield,
  Star,
  TrendingUp,
  UserCheck,
  Users,
  Wrench,
  AlertTriangle,
  Award,
  Calendar,
  CheckCircle,
  ClipboardList,
  MessageSquare,
  ArrowUpCircle,
  Banknote,
} from "lucide-react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import { BUSINESS_ACCENT } from "@/components/business/actioncenter/ui/BusinessActionDesignSystem";
import type { BusinessCatalogAction, BusinessCatalogCategory } from "@/repositories/BusinessActionRepository";

type BusinessActionHubProps = {
  categories: BusinessCatalogCategory[];
  actions: BusinessCatalogAction[];
  favorites: string[];
  recentIds: string[];
  contextChips?: string[];
  momentName?: string | null;
  onSelect: (actionId: string) => void;
  onToggleFavorite: (actionId: string) => void;
};

const ICON_MAP: Record<string, typeof Briefcase> = {
  team_update: Users,
  recognition: Award,
  meeting: Calendar,
  issue: AlertTriangle,
  approval: CheckCircle,
  review: ClipboardList,
  escalation: ArrowUpCircle,
  participation: UserCheck,
  member_update: Users,
  note: FileText,
  cash_inflow: DollarSign,
  expense_burn: TrendingUp,
  runway_risk: Shield,
  financial_update: Banknote,
  strategic_decision: Briefcase,
  spend_entry: DollarSign,
  vendor_update: Wrench,
  operational_improvement: TrendingUp,
};

function ActionGlyph({ actionType }: { actionType: string }) {
  const suffix = actionType.split(".").pop() ?? actionType;
  const Icon = ICON_MAP[suffix] ?? MessageSquare;
  return <Icon className="size-5" style={{ color: BUSINESS_ACCENT.teal }} />;
}

function searchActions(actions: BusinessCatalogAction[], query: string): BusinessCatalogAction[] {
  const q = query.trim().toLowerCase();
  if (!q) return actions;
  return actions.filter((a) => {
    const hay = [a.label, a.subtitle ?? "", a.action_type, ...(a.tags ?? []), ...(a.synonyms ?? "")].join(" ").toLowerCase();
    return hay.includes(q);
  });
}

export function BusinessActionHub({
  categories,
  actions,
  favorites,
  recentIds,
  contextChips,
  momentName,
  onSelect,
  onToggleFavorite,
}: BusinessActionHubProps) {
  const { colors } = useThemeTokens();
  const [query, setQuery] = useState("");

  const filtered = useMemo(() => searchActions(actions, query), [actions, query]);
  const byId = useMemo(() => new Map(actions.map((a) => [a.action_id, a])), [actions]);

  const frequentlyUsed = useMemo(() => {
    const ids = [...new Set([...favorites, ...recentIds])];
    return ids.map((id) => byId.get(id)).filter(Boolean) as BusinessCatalogAction[];
  }, [favorites, recentIds, byId]);

  const grouped = useMemo(() => {
    return categories
      .map((cat) => ({
        id: cat.id,
        label: cat.label,
        items: filtered.filter((a) => a.category_id === cat.id),
      }))
      .filter((g) => g.items.length > 0);
  }, [filtered, categories]);

  const chips = useMemo(() => {
    const raw = contextChips?.length ? contextChips : [momentName ?? "Action Center"];
    return Array.from(new Set(raw.filter(Boolean)));
  }, [contextChips, momentName]);

  function tile(action: BusinessCatalogAction) {
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
              style={{ background: `${BUSINESS_ACCENT.teal}1A` }}
            >
              <ActionGlyph actionType={action.action_type} />
            </div>
            <div>
              <p
                className="text-lg font-semibold"
                style={{ color: colors.textPrimary, fontFamily: "'Plus Jakarta Sans', sans-serif" }}
              >
                {action.label}
              </p>
              {action.subtitle ? (
                <p className="text-sm" style={{ color: colors.textSecondary }}>
                  {action.subtitle}
                </p>
              ) : null}
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
            onClick={() => onToggleFavorite(action.action_id)}
          >
            <Star
              className="size-4"
              fill={fav ? BUSINESS_ACCENT.teal : "transparent"}
              style={{ color: BUSINESS_ACCENT.teal }}
            />
          </button>
        ) : null}
      </div>
    );
  }

  return (
    <div className="space-y-8 pb-6">
      <div className="flex gap-2 overflow-x-auto pb-1">
        {chips.map((chip, i) => (
          <span
            key={`${i}-${chip}`}
            className="whitespace-nowrap rounded-full border px-3 py-1 text-xs font-medium"
            style={{
              borderColor: `${BUSINESS_ACCENT.teal}33`,
              background: `${BUSINESS_ACCENT.teal}1A`,
              color: BUSINESS_ACCENT.teal,
            }}
          >
            {chip}
          </span>
        ))}
      </div>

      <div className="relative h-[180px] overflow-hidden rounded-3xl md:h-[220px]">
        <div
          className="h-full w-full"
          style={{
            background: `linear-gradient(135deg, ${BUSINESS_ACCENT.navy} 0%, ${BUSINESS_ACCENT.teal}88 40%, ${colors.surfaceContainer} 100%)`,
          }}
        />
        <div
          className="absolute inset-0"
          style={{ background: `linear-gradient(to top, ${colors.background} 0%, transparent 55%)` }}
        />
        <div className="absolute inset-x-0 bottom-0 p-6">
          <h3
            className="text-2xl font-semibold md:text-3xl"
            style={{ color: "#fff", fontFamily: "'Plus Jakarta Sans', sans-serif" }}
          >
            Action Center
          </h3>
          <p className="mt-2 max-w-[85%] text-sm md:text-base" style={{ color: "rgba(255,255,255,0.8)" }}>
            Record activity, approvals, and operational updates.
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

      {!query && frequentlyUsed.length > 0 ? (
        <HubSection title="Frequently Used">{frequentlyUsed.map(tile)}</HubSection>
      ) : null}

      {grouped.map((g) => (
        <HubSection key={g.id} title={g.label}>
          {g.items.map(tile)}
        </HubSection>
      ))}

      {filtered.length === 0 ? (
        <p className="py-8 text-center text-sm" style={{ color: colors.textSecondary }}>
          No actions match &ldquo;{query}&rdquo;.
        </p>
      ) : null}
    </div>
  );
}

function HubSection({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section className="space-y-4">
      <h4
        className="text-xs font-semibold uppercase tracking-widest"
        style={{ color: BUSINESS_ACCENT.teal }}
      >
        {title}
      </h4>
      <div className="space-y-3">{children}</div>
    </section>
  );
}
