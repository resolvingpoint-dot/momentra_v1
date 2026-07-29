"use client";

import { useEffect, useState } from "react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";
import {
  deleteLivingActivity,
  getLivingActivityDetail,
  patchLivingActivity,
  type LivingActivityItem,
} from "@/lib/api/group";

type LivingActivityEditSheetProps = {
  momentId: string;
  eventId: string;
  onClose: () => void;
  onSuccess: () => void;
  getDetail?: (momentId: string, eventId: string) => Promise<LivingActivityItem>;
  patchActivity?: (
    momentId: string,
    eventId: string,
    body: { title?: string; subtitle?: string; occurred_at?: string },
  ) => Promise<LivingActivityItem>;
  deleteActivity?: (momentId: string, eventId: string) => Promise<{ status: string }>;
};

export function LivingActivityEditSheet({
  momentId,
  eventId,
  onClose,
  onSuccess,
  getDetail = getLivingActivityDetail,
  patchActivity = patchLivingActivity,
  deleteActivity = deleteLivingActivity,
}: LivingActivityEditSheetProps) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [title, setTitle] = useState("");
  const [subtitle, setSubtitle] = useState("");
  const [occurredAt, setOccurredAt] = useState("");
  const [canDelete, setCanDelete] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    void getDetail(momentId, eventId)
      .then((detail) => {
        if (cancelled) return;
        setTitle(detail.title ?? "");
        setSubtitle(detail.subtitle ?? "");
        setOccurredAt((detail.occurred_at || "").slice(0, 16));
        setCanDelete(detail.can_delete !== false);
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
  }, [momentId, eventId, getDetail]);

  async function handleSave() {
    setSaving(true);
    setError(null);
    try {
      await patchActivity(momentId, eventId, {
        title: title.trim(),
        subtitle: subtitle.trim(),
        ...(occurredAt ? { occurred_at: new Date(occurredAt).toISOString() } : {}),
      });
      onSuccess();
      onClose();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Save failed");
    } finally {
      setSaving(false);
    }
  }

  async function handleDelete() {
    if (!canDelete) return;
    if (!window.confirm("Delete this activity?")) return;
    setSaving(true);
    setError(null);
    try {
      await deleteActivity(momentId, eventId);
      onSuccess();
      onClose();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Delete failed");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="fixed inset-0 z-[60] flex items-end justify-center bg-black/50" onClick={onClose}>
      <div
        className="w-full max-w-lg rounded-t-3xl px-5 pb-8 pt-4"
        style={{ background: colors.surfaceContainerHighest ?? colors.surface, color: colors.textPrimary }}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="mx-auto mb-4 h-1 w-10 rounded-full bg-white/20" />
        <h2 className="mb-1 text-lg font-semibold">Edit activity</h2>
        <p className="mb-4 text-xs opacity-60">Update title, note, or remove this entry</p>

        {loading ? (
          <p className="text-sm opacity-60">Loading…</p>
        ) : (
          <div className="space-y-3">
            <label className="block text-xs opacity-60">
              Title
              <input
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                className="mt-1 w-full rounded-xl border-0 px-3 py-2 text-sm outline-none"
                style={{ background: colors.surfaceContainerLow ?? colors.surfaceContainer, color: colors.textPrimary }}
              />
            </label>
            <label className="block text-xs opacity-60">
              Subtitle
              <input
                value={subtitle}
                onChange={(e) => setSubtitle(e.target.value)}
                className="mt-1 w-full rounded-xl border-0 px-3 py-2 text-sm outline-none"
                style={{ background: colors.surfaceContainerLow ?? colors.surfaceContainer, color: colors.textPrimary }}
              />
            </label>
            <label className="block text-xs opacity-60">
              When
              <input
                type="datetime-local"
                value={occurredAt}
                onChange={(e) => setOccurredAt(e.target.value)}
                className="mt-1 w-full rounded-xl border-0 px-3 py-2 text-sm outline-none"
                style={{ background: colors.surfaceContainerLow ?? colors.surfaceContainer, color: colors.textPrimary }}
              />
            </label>
          </div>
        )}

        {error ? (
          <p className="mt-3 text-sm" style={{ color: colors.error }}>
            {error}
          </p>
        ) : null}

        <div className="mt-5 flex gap-2">
          <button
            type="button"
            disabled={saving || loading || !title.trim()}
            onClick={() => void handleSave()}
            className="flex-1 rounded-xl py-3 text-sm font-semibold disabled:opacity-50"
            style={{ background: colors.brandPrimary, color: colors.brandOnPrimary ?? "#fff" }}
          >
            {saving ? "Saving…" : "Save"}
          </button>
          <button
            type="button"
            disabled={saving || loading}
            onClick={onClose}
            className="rounded-xl px-4 py-3 text-sm font-semibold"
            style={{ background: colors.surfaceContainerLow ?? colors.surfaceContainer }}
          >
            Cancel
          </button>
        </div>
        {canDelete ? (
          <button
            type="button"
            disabled={saving || loading}
            onClick={() => void handleDelete()}
            className="mt-3 w-full rounded-xl py-3 text-sm font-semibold"
            style={{ color: colors.error }}
          >
            Delete activity
          </button>
        ) : null}
      </div>
    </div>
  );
}
