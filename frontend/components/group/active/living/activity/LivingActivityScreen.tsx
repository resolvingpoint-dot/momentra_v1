"use client";

import { useEffect, useMemo, useState } from "react";
import { ArrowLeft, Pencil, Search } from "lucide-react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import {
  listLivingActivity,
  type LivingActivityItem,
  type LivingActivityListResponse,
} from "@/lib/api/group";

type LivingActivityScreenProps = {
  momentId: string;
  onBack: () => void;
  onEditActivity: (id: string, eventType: string) => void;
  reloadToken?: number;
  title?: string;
  subtitle?: string;
  listActivity?: (momentId: string) => Promise<LivingActivityListResponse>;
};

function groupLabel(iso: string): string {
  const d = new Date(iso);
  const now = new Date();
  const startOfToday = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  const startOfYesterday = new Date(startOfToday);
  startOfYesterday.setDate(startOfYesterday.getDate() - 1);
  const startOfWeek = new Date(startOfToday);
  startOfWeek.setDate(startOfWeek.getDate() - 7);
  if (d >= startOfToday) return "Today";
  if (d >= startOfYesterday) return "Yesterday";
  if (d >= startOfWeek) return "This week";
  return "Earlier";
}

export function LivingActivityScreen({
  momentId,
  onBack,
  onEditActivity,
  reloadToken = 0,
  title = "Home activity",
  subtitle = "View and edit household updates",
  listActivity = listLivingActivity,
}: LivingActivityScreenProps) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [items, setItems] = useState<LivingActivityItem[]>([]);
  const [search, setSearch] = useState("");

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    void listActivity(momentId)
      .then((data) => {
        if (!cancelled) setItems(data.items ?? []);
      })
      .catch((err: unknown) => {
        if (!cancelled) setError(err instanceof Error ? err.message : "Could not load activity");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [momentId, reloadToken, listActivity]);

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    if (!q) return items;
    return items.filter((item) =>
      `${item.title} ${item.subtitle} ${item.activity_type}`.toLowerCase().includes(q),
    );
  }, [items, search]);

  const grouped = useMemo(() => {
    const map = new Map<string, LivingActivityItem[]>();
    for (const item of filtered) {
      const key = groupLabel(item.occurred_at || new Date().toISOString());
      if (!map.has(key)) map.set(key, []);
      map.get(key)!.push(item);
    }
    return ["Today", "Yesterday", "This week", "Earlier"]
      .filter((k) => map.has(k))
      .map((k) => ({ label: k, items: map.get(k)! }));
  }, [filtered]);

  return (
    <div
      className="fixed inset-0 z-50 flex flex-col"
      style={{ background: colors.background, color: colors.textPrimary }}
    >
      <header
        className="relative z-10 flex items-center gap-3 border-b px-5 py-4"
        style={{ borderColor: "rgba(255,255,255,0.1)", background: `${colors.background}cc` }}
      >
        <button type="button" onClick={onBack} className="border-0 bg-transparent p-0" aria-label="Back">
          <ArrowLeft size={22} color={colors.brandPrimary} />
        </button>
        <div>
          <h1 className="text-lg font-semibold">{title}</h1>
          <p className="text-xs opacity-60">{subtitle}</p>
        </div>
      </header>

      <div className="relative z-10 flex-1 overflow-y-auto px-5 py-4">
        <div
          className="mb-4 flex items-center gap-2 rounded-xl px-3 py-2"
          style={{ background: colors.surfaceContainerLow ?? colors.surfaceContainer }}
        >
          <Search size={16} style={{ color: colors.textSecondary }} />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search activity"
            className="w-full border-0 bg-transparent text-sm outline-none"
            style={{ color: colors.textPrimary }}
          />
        </div>

        {loading ? (
          <p className="text-sm opacity-60">Loading activity…</p>
        ) : error ? (
          <p className="text-sm" style={{ color: colors.error }}>
            {error}
          </p>
        ) : filtered.length === 0 ? (
          <p className="text-sm opacity-60">No activity yet. Use Quick Add to log something.</p>
        ) : (
          grouped.map((group) => (
            <section key={group.label} className="mb-6">
              <h2 className="mb-3 text-[11px] font-bold uppercase tracking-wider opacity-50">
                {group.label}
              </h2>
              <div className="space-y-2">
                {group.items.map((item) => (
                  <button
                    key={item.id}
                    type="button"
                    className="flex w-full items-center gap-3 rounded-2xl px-4 py-3 text-left"
                    style={{ background: colors.surfaceContainerLow ?? colors.surfaceContainer }}
                    onClick={() => {
                      if (item.can_edit) onEditActivity(item.id, item.edit_event_type || item.activity_type);
                    }}
                  >
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-sm font-semibold">{item.title || "Activity"}</p>
                      <p className="truncate text-xs opacity-60">
                        {item.subtitle || item.relative_time || item.activity_type}
                      </p>
                    </div>
                    {item.can_edit ? <Pencil size={16} style={{ color: colors.brandPrimary }} /> : null}
                  </button>
                ))}
              </div>
            </section>
          ))
        )}
      </div>
    </div>
  );
}
