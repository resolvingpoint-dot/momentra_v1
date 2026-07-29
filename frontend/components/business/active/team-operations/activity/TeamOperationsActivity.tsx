"use client";

import { useEffect, useMemo, useState } from "react";
import type { BusinessActivityListItem } from "@/lib/api/businessActive";
import type { BusinessActivityFilters } from "@/lib/business/activityFilters";
import { DEFAULT_ACTIVITY_PAGE_SIZE } from "@/lib/business/activityFilters";
import {
  TeamOpsEmptyLine,
  TeamOpsScrollShell,
  TeamOpsSectionTitle,
  TeamOpsStatusBanner,
} from "../shared/shared";
import { TEAM_OPS } from "../shared/teamOpsTheme";
import { TeamOperationsActivityFilters } from "./TeamOperationsActivityFilters";
import { TeamOperationsActivityRow } from "./TeamOperationsActivityRow";
import { TeamOperationsActivityDetail } from "./TeamOperationsActivityDetail";
import { TeamOperationsActivityEditSheet } from "./TeamOperationsActivityEditSheet";
import { TeamOperationsActivityDeleteDialog } from "./TeamOperationsActivityDeleteDialog";

type Props = {
  items: BusinessActivityListItem[];
  total: number;
  page: number;
  pageSize?: number;
  loading: boolean;
  refreshing?: boolean;
  error: string | null;
  filters: BusinessActivityFilters;
  detail: BusinessActivityListItem | null;
  detailLoading?: boolean;
  detailError?: string | null;
  initialEventId?: string | null;
  bottomPadding?: number;
  memberOptions?: Array<{ id: string; label: string }>;
  actionTypes?: readonly string[];
  actionMeta?: Record<string, { label: string }>;
  onFiltersChange: (next: BusinessActivityFilters) => void;
  onPageChange: (page: number) => void;
  onSelectEvent: (eventId: string | null) => void;
  onRetry: () => void;
  onClose?: () => void;
  onSaveTitle?: (eventId: string, title: string) => Promise<void>;
  onDelete?: (eventId: string) => Promise<void>;
};

export function TeamOperationsActivity({
  items,
  total,
  page,
  pageSize = DEFAULT_ACTIVITY_PAGE_SIZE,
  loading,
  refreshing,
  error,
  filters,
  detail,
  detailLoading,
  detailError,
  initialEventId = null,
  bottomPadding = 0,
  memberOptions,
  actionTypes,
  actionMeta,
  onFiltersChange,
  onPageChange,
  onSelectEvent,
  onRetry,
  onClose,
  onSaveTitle,
  onDelete,
}: Props) {
  const [showFilters, setShowFilters] = useState(false);
  const [editOpen, setEditOpen] = useState(false);
  const [deleteOpen, setDeleteOpen] = useState(false);
  const [busy, setBusy] = useState(false);
  const [localError, setLocalError] = useState<string | null>(null);

  useEffect(() => {
    if (initialEventId) onSelectEvent(initialEventId);
  }, [initialEventId, onSelectEvent]);

  const totalPages = Math.max(1, Math.ceil(total / pageSize));
  const selected = detail;

  const members = useMemo(() => {
    if (memberOptions?.length) return memberOptions;
    const map = new Map<string, string>();
    for (const i of items) {
      if (i.created_by) map.set(i.created_by, i.created_by);
    }
    return [...map.entries()].map(([id, label]) => ({ id, label }));
  }, [items, memberOptions]);

  if (loading && items.length === 0 && !selected) {
    return (
      <TeamOpsScrollShell bottomPadding={bottomPadding}>
        <TeamOpsStatusBanner loading refreshing={false} error={null} onRetry={onRetry} />
      </TeamOpsScrollShell>
    );
  }
  if (error && items.length === 0 && !selected) {
    return (
      <TeamOpsScrollShell bottomPadding={bottomPadding}>
        <TeamOpsStatusBanner loading={false} error={error} onRetry={onRetry} />
      </TeamOpsScrollShell>
    );
  }

  if (selected) {
    return (
      <TeamOpsScrollShell bottomPadding={bottomPadding}>
        <TeamOperationsActivityDetail
          item={selected}
          loading={detailLoading}
          error={detailError || localError}
          onBack={() => {
            setEditOpen(false);
            setDeleteOpen(false);
            onSelectEvent(null);
          }}
          onClose={onClose}
          onEdit={selected.is_editable ? () => setEditOpen(true) : undefined}
          onDelete={selected.is_deletable ? () => setDeleteOpen(true) : undefined}
        />
        <TeamOperationsActivityEditSheet
          open={editOpen}
          initialTitle={selected.title || ""}
          busy={busy}
          error={localError}
          onClose={() => setEditOpen(false)}
          onSave={async (title) => {
            if (!onSaveTitle) return;
            setBusy(true);
            setLocalError(null);
            try {
              await onSaveTitle(selected.event_id, title);
              setEditOpen(false);
            } catch (e) {
              setLocalError(e instanceof Error ? e.message : "Update failed");
            } finally {
              setBusy(false);
            }
          }}
        />
        <TeamOperationsActivityDeleteDialog
          open={deleteOpen}
          title={selected.title || selected.action_type}
          busy={busy}
          error={localError}
          onClose={() => setDeleteOpen(false)}
          onConfirm={async () => {
            if (!onDelete) return;
            setBusy(true);
            setLocalError(null);
            try {
              await onDelete(selected.event_id);
              setDeleteOpen(false);
              onSelectEvent(null);
            } catch (e) {
              setLocalError(e instanceof Error ? e.message : "Delete failed");
            } finally {
              setBusy(false);
            }
          }}
        />
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
        <div className="flex items-center gap-3">
          <button
            type="button"
            className="text-sm font-semibold focus-visible:outline focus-visible:outline-2"
            style={{ color: TEAM_OPS.primary, minHeight: 44 }}
            onClick={() => setShowFilters((v) => !v)}
            aria-expanded={showFilters}
          >
            Filters
          </button>
          {onClose ? (
            <button
              type="button"
              className="text-sm focus-visible:outline focus-visible:outline-2"
              style={{ color: TEAM_OPS.onVariant, minHeight: 44 }}
              onClick={onClose}
            >
              Close
            </button>
          ) : null}
        </div>
      </div>
      {showFilters ? (
        <div className="mb-4">
          <TeamOperationsActivityFilters
            filters={filters}
            onChange={(next) => {
              onFiltersChange(next);
              onPageChange(1);
            }}
            memberOptions={members}
            actionTypes={actionTypes}
            actionMeta={actionMeta}
          />
        </div>
      ) : null}
      {refreshing ? (
        <TeamOpsStatusBanner loading={false} refreshing error={null} onRetry={onRetry} />
      ) : null}
      <TeamOpsSectionTitle>
        Activities ({total})
      </TeamOpsSectionTitle>
      {items.length === 0 ? (
        <TeamOpsEmptyLine label="No activities match these filters." />
      ) : (
        <ul className="space-y-2">
          {items.map((item) => (
            <TeamOperationsActivityRow
              key={item.event_id}
              item={item}
              actionMeta={actionMeta}
              onSelect={(row) => onSelectEvent(row.event_id)}
            />
          ))}
        </ul>
      )}
      {totalPages > 1 ? (
        <div className="mt-4 flex items-center justify-between gap-2">
          <button
            type="button"
            disabled={page <= 1}
            className="rounded-xl px-3 py-2 text-sm font-semibold disabled:opacity-40"
            style={{ background: TEAM_OPS.surfaceHigh, color: TEAM_OPS.onSurface, minHeight: 44 }}
            onClick={() => onPageChange(page - 1)}
          >
            Previous
          </button>
          <span className="text-xs" style={{ color: TEAM_OPS.onVariant }}>
            Page {page} / {totalPages}
          </span>
          <button
            type="button"
            disabled={page >= totalPages}
            className="rounded-xl px-3 py-2 text-sm font-semibold disabled:opacity-40"
            style={{ background: TEAM_OPS.surfaceHigh, color: TEAM_OPS.onSurface, minHeight: 44 }}
            onClick={() => onPageChange(page + 1)}
          >
            Next
          </button>
        </div>
      ) : null}
    </TeamOpsScrollShell>
  );
}
