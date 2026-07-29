"use client";

import { useEffect, useState } from "react";
import type { BusinessActivityListItem } from "@/lib/api/businessActive";
import { formatOccurredAt, TEAM_OPS } from "./teamOpsTheme";
import {
  TeamOpsEmptyLine,
  TeamOpsScrollShell,
  TeamOpsSectionCard,
  TeamOpsSectionTitle,
  TeamOpsStatusBanner,
} from "./shared";

type Props = {
  items: BusinessActivityListItem[];
  loading: boolean;
  refreshing?: boolean;
  error: string | null;
  initialEventId?: string | null;
  bottomPadding?: number;
  onRetry: () => void;
  onClose?: () => void;
  onSaveTitle?: (eventId: string, title: string) => Promise<void>;
  onDelete?: (eventId: string) => Promise<void>;
};

export function TeamOperationsActivity({
  items,
  loading,
  refreshing,
  error,
  initialEventId = null,
  bottomPadding = 0,
  onRetry,
  onClose,
  onSaveTitle,
  onDelete,
}: Props) {
  const [selectedId, setSelectedId] = useState<string | null>(initialEventId);
  const [titleDraft, setTitleDraft] = useState("");
  const [busy, setBusy] = useState(false);
  const [localError, setLocalError] = useState<string | null>(null);

  useEffect(() => {
    setSelectedId(initialEventId);
  }, [initialEventId]);

  const selected = items.find((i) => i.event_id === selectedId) ?? null;

  async function saveTitle() {
    if (!selected?.event_id || !titleDraft.trim() || !onSaveTitle) return;
    setBusy(true);
    setLocalError(null);
    try {
      await onSaveTitle(selected.event_id, titleDraft.trim());
      setSelectedId(null);
    } catch (e) {
      setLocalError(e instanceof Error ? e.message : "Update failed");
    } finally {
      setBusy(false);
    }
  }

  async function remove() {
    if (!selected?.event_id || !onDelete) return;
    setBusy(true);
    setLocalError(null);
    try {
      await onDelete(selected.event_id);
      setSelectedId(null);
    } catch (e) {
      setLocalError(e instanceof Error ? e.message : "Delete failed");
    } finally {
      setBusy(false);
    }
  }

  if (loading && items.length === 0) {
    return (
      <TeamOpsScrollShell bottomPadding={bottomPadding}>
        <TeamOpsStatusBanner loading refreshing={false} error={null} onRetry={onRetry} />
      </TeamOpsScrollShell>
    );
  }
  if (error && items.length === 0) {
    return (
      <TeamOpsScrollShell bottomPadding={bottomPadding}>
        <TeamOpsStatusBanner loading={false} error={error} onRetry={onRetry} />
      </TeamOpsScrollShell>
    );
  }

  if (selected) {
    return (
      <TeamOpsScrollShell bottomPadding={bottomPadding}>
        <div className="mb-2 flex items-center justify-between">
          <button
            type="button"
            className="text-sm font-semibold"
            style={{ color: TEAM_OPS.primary }}
            onClick={() => setSelectedId(null)}
          >
            ← Back
          </button>
          {onClose ? (
            <button type="button" className="text-sm" style={{ color: TEAM_OPS.onVariant }} onClick={onClose}>
              Close
            </button>
          ) : null}
        </div>
        <TeamOpsSectionCard>
          <p className="text-xs uppercase tracking-wide" style={{ color: TEAM_OPS.onVariant }}>
            {selected.action_type}
          </p>
          <label className="mt-3 block text-xs" style={{ color: TEAM_OPS.onVariant }}>
            Title
          </label>
          <input
            className="mt-1 w-full rounded-xl px-3 py-2 text-sm outline-none"
            style={{
              background: TEAM_OPS.surface,
              color: TEAM_OPS.onSurface,
              border: `1px solid ${TEAM_OPS.outline}55`,
            }}
            value={titleDraft || selected.title}
            onChange={(e) => setTitleDraft(e.target.value)}
            onFocus={() => {
              if (!titleDraft) setTitleDraft(selected.title || "");
            }}
          />
          <p className="mt-2 text-xs" style={{ color: TEAM_OPS.onVariant }}>
            {formatOccurredAt(String(selected.occurred_at || selected.created_at || ""))}
          </p>
          {localError ? (
            <p className="mt-2 text-sm" style={{ color: TEAM_OPS.error }}>
              {localError}
            </p>
          ) : null}
          <div className="mt-4 flex flex-wrap gap-2">
            <button
              type="button"
              disabled={busy || !onSaveTitle}
              className="rounded-xl px-4 py-2 text-sm font-semibold disabled:opacity-50"
              style={{ background: TEAM_OPS.primaryContainer, color: "#0d0096" }}
              onClick={() => void saveTitle()}
            >
              Save
            </button>
            <button
              type="button"
              disabled={busy || !onDelete}
              className="rounded-xl px-4 py-2 text-sm font-semibold disabled:opacity-50"
              style={{ background: TEAM_OPS.surfaceHigh, color: TEAM_OPS.error }}
              onClick={() => void remove()}
            >
              Delete
            </button>
          </div>
        </TeamOpsSectionCard>
      </TeamOpsScrollShell>
    );
  }

  return (
    <TeamOpsScrollShell bottomPadding={bottomPadding}>
      <div className="mb-1 flex items-center justify-between gap-2">
        <h2
          className="text-xl font-bold"
          style={{ color: TEAM_OPS.onSurface, fontFamily: TEAM_OPS.fontDisplay }}
        >
          Team Activity
        </h2>
        {onClose ? (
          <button type="button" className="text-sm" style={{ color: TEAM_OPS.onVariant }} onClick={onClose}>
            Close
          </button>
        ) : null}
      </div>
      {refreshing ? (
        <TeamOpsStatusBanner loading={false} refreshing error={null} onRetry={onRetry} />
      ) : null}
      <TeamOpsSectionTitle>Activities ({items.length})</TeamOpsSectionTitle>
      {items.length === 0 ? (
        <TeamOpsEmptyLine label="No activities yet." />
      ) : (
        <ul className="space-y-2">
          {items.map((item) => (
            <li key={item.event_id}>
              <button
                type="button"
                className="w-full rounded-xl px-3 py-3 text-left"
                style={{ background: TEAM_OPS.surfaceLow, border: `1px solid ${TEAM_OPS.outline}22` }}
                onClick={() => {
                  setTitleDraft(item.title || "");
                  setSelectedId(item.event_id);
                }}
              >
                <p className="text-sm font-medium" style={{ color: TEAM_OPS.onSurface }}>
                  {item.title || item.action_type}
                </p>
                <p className="mt-0.5 text-xs" style={{ color: TEAM_OPS.onVariant }}>
                  {item.action_type}
                  {item.occurred_at || item.created_at
                    ? ` · ${formatOccurredAt(String(item.occurred_at || item.created_at))}`
                    : ""}
                </p>
              </button>
            </li>
          ))}
        </ul>
      )}
    </TeamOpsScrollShell>
  );
}

/** @deprecated */
export const TeamOpsActivity = TeamOperationsActivity;
