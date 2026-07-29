"use client";

import { useCallback, useEffect, useState } from "react";
import { Scale } from "lucide-react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import {
  getSettlementPreview,
  listSettlements,
  markSettlementSettled,
  type SettlementPreview,
  type SettlementRecord,
} from "@/lib/api/group";
import { dedupeFetch } from "@/lib/cache/cacheStore";

type GroupSettlementPanelProps = {
  momentId: string;
};

function formatMinor(amountMinor: number, currency = "INR") {
  const value = (amountMinor / 100).toLocaleString(undefined, {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  });
  return currency === "INR" ? `₹${value}` : `${value} ${currency}`;
}

export function GroupSettlementPanel({ momentId }: GroupSettlementPanelProps) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  const [preview, setPreview] = useState<SettlementPreview | null>(null);
  const [records, setRecords] = useState<SettlementRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [busyId, setBusyId] = useState<string | null>(null);

  const load = useCallback(async (opts?: { soft?: boolean }) => {
    try {
      if (opts?.soft) setRefreshing(true);
      else setLoading(true);
      const key = `group:settlement:${momentId}`;
      const [p, list] = await Promise.all([
        dedupeFetch(`${key}:preview`, () => getSettlementPreview(momentId)),
        dedupeFetch(`${key}:list`, () => listSettlements(momentId)),
      ]);
      setPreview(p);
      setRecords(list.settlements ?? []);
      setError(null);
    } catch {
      setError("Unable to load this section.");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [momentId]);

  useEffect(() => {
    void load();
  }, [load]);

  async function handleMarkSettled(id: string) {
    setBusyId(id);
    const previous = records;
    setRecords((rows) =>
      rows.map((r) => (r.id === id ? { ...r, status: "SETTLED" } : r)),
    );
    try {
      await markSettlementSettled(momentId, id);
      await load({ soft: true });
    } catch {
      setRecords(previous);
      setError("Unable to mark settlement. Try again.");
    } finally {
      setBusyId(null);
    }
  }

  if (loading && !preview) {
    return (
      <div
        className="rounded-2xl p-4 text-sm"
        style={{ background: colors.surfaceContainer, color: colors.textSecondary }}
        role="status"
        aria-live="polite"
      >
        Loading settlements…
      </div>
    );
  }

  if (error && !preview) {
    return (
      <div className="rounded-2xl p-4 text-sm space-y-2" style={{ background: colors.surfaceContainer }}>
        <p style={{ color: colors.error }}>{error}</p>
        <button
          type="button"
          className="text-sm font-semibold underline"
          style={{ color: colors.brandPrimary }}
          onClick={() => void load()}
        >
          Retry
        </button>
      </div>
    );
  }

  if (!preview) return null;

  return (
    <div
      className="rounded-2xl p-4 space-y-4"
      style={{ background: colors.surfaceContainer, opacity: refreshing ? 0.92 : 1 }}
      aria-busy={refreshing}
    >
      <div className="flex items-center gap-2">
        <Scale size={16} style={{ color: colors.brandPrimary }} aria-hidden />
        <h4 className="text-sm font-semibold" style={{ color: colors.textPrimary }}>
          Settlement · {preview.harmony_label}
        </h4>
      </div>
      <p className="text-xs" style={{ color: colors.textSecondary }}>{preview.balance_insight}</p>

      {preview.suggestions.length > 0 && (
        <div className="space-y-2">
          <p className="text-[10px] font-bold uppercase tracking-widest" style={{ color: colors.textSecondary }}>
            Suggested transfers
          </p>
          {preview.suggestions.map((s, i) => (
            <div
              key={`${s.from_member_id}-${s.to_member_id}-${i}`}
              className="flex items-center justify-between rounded-xl px-3 py-2 text-sm"
              style={{ background: `${colors.brandPrimary}12` }}
            >
              <span style={{ color: colors.textPrimary }}>
                {s.from_display_name || s.from_member_id} → {s.to_display_name || s.to_member_id}
              </span>
              <span className="font-semibold" style={{ color: colors.brandPrimary }}>
                {formatMinor(s.amount_minor, s.currency_code)}
              </span>
            </div>
          ))}
        </div>
      )}

      {records.length > 0 && (
        <div className="space-y-2">
          <p className="text-[10px] font-bold uppercase tracking-widest" style={{ color: colors.textSecondary }}>
            History
          </p>
          {records.map((r) => (
            <div
              key={r.id}
              className="flex items-center justify-between gap-2 rounded-xl px-3 py-2 text-sm"
              style={{ background: colors.surfaceContainerHigh ?? colors.surfaceContainer }}
            >
              <div>
                <p style={{ color: colors.textPrimary }}>
                  {formatMinor(r.amount_minor, r.currency_code)} · {r.status}
                </p>
              </div>
              {r.status !== "SETTLED" ? (
                <button
                  type="button"
                  disabled={busyId === r.id}
                  aria-label="Mark settlement as settled"
                  className="rounded-full px-3 py-1 text-xs font-semibold disabled:opacity-50"
                  style={{ background: colors.primaryContainer, color: colors.brandOnPrimary }}
                  onClick={() => void handleMarkSettled(r.id)}
                >
                  {busyId === r.id ? "Saving…" : "Mark settled"}
                </button>
              ) : null}
            </div>
          ))}
        </div>
      )}

      {preview.suggestions.length === 0 && records.length === 0 ? (
        <p className="text-xs" style={{ color: colors.textSecondary }}>
          Everyone is settled up.
        </p>
      ) : null}
    </div>
  );
}
