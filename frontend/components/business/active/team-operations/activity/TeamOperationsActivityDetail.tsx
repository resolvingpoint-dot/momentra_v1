"use client";

import type { BusinessActivityListItem } from "@/lib/api/businessActive";
import { formatOccurredAt, TEAM_OPS } from "../shared/teamOpsTheme";
import { TeamOpsSectionCard } from "../shared/shared";

type Props = {
  item: BusinessActivityListItem;
  loading?: boolean;
  error?: string | null;
  onBack: () => void;
  onEdit?: () => void;
  onDelete?: () => void;
  onClose?: () => void;
};

export function TeamOperationsActivityDetail({
  item,
  loading,
  error,
  onBack,
  onEdit,
  onDelete,
  onClose,
}: Props) {
  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center justify-between">
        <button
          type="button"
          className="text-sm font-semibold focus-visible:outline focus-visible:outline-2"
          style={{ color: TEAM_OPS.primary, minHeight: 44 }}
          onClick={onBack}
        >
          ← Back
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
      {loading ? (
        <p className="text-sm" style={{ color: TEAM_OPS.onVariant }}>
          Loading detail…
        </p>
      ) : null}
      {error ? (
        <p className="text-sm" role="alert" style={{ color: TEAM_OPS.error }}>
          {error}
        </p>
      ) : null}
      <TeamOpsSectionCard>
        <p className="text-xs uppercase tracking-wide" style={{ color: TEAM_OPS.onVariant }}>
          {item.action_type}
        </p>
        <h2
          className="mt-2 text-xl font-bold"
          style={{ color: TEAM_OPS.onSurface, fontFamily: TEAM_OPS.fontDisplay }}
        >
          {item.title || item.action_type}
        </h2>
        {item.subtitle ? (
          <p className="mt-1 text-sm" style={{ color: TEAM_OPS.onVariant }}>
            {item.subtitle}
          </p>
        ) : null}
        <p className="mt-3 text-xs" style={{ color: TEAM_OPS.onVariant }}>
          {formatOccurredAt(String(item.occurred_at || item.created_at || ""))}
          {item.source ? ` · source ${item.source}` : ""}
          {item.created_by ? ` · by ${item.created_by}` : ""}
        </p>
        <p className="mt-2 text-xs" style={{ color: TEAM_OPS.onVariant }}>
          {item.is_editable ? "Editable" : "Not editable"} ·{" "}
          {item.is_deletable ? "Deletable" : "Not deletable"}
        </p>
        <div className="mt-4 flex flex-wrap gap-2">
          {item.is_editable && onEdit ? (
            <button
              type="button"
              className="rounded-xl px-4 py-2 text-sm font-semibold focus-visible:outline focus-visible:outline-2"
              style={{ background: TEAM_OPS.primaryContainer, color: "#0d0096", minHeight: 44 }}
              onClick={onEdit}
            >
              Edit
            </button>
          ) : null}
          {item.is_deletable && onDelete ? (
            <button
              type="button"
              className="rounded-xl px-4 py-2 text-sm font-semibold focus-visible:outline focus-visible:outline-2"
              style={{ background: TEAM_OPS.surfaceHigh, color: TEAM_OPS.error, minHeight: 44 }}
              onClick={onDelete}
            >
              Delete
            </button>
          ) : null}
        </div>
      </TeamOpsSectionCard>
    </div>
  );
}
