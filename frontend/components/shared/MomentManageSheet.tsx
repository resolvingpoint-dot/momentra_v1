"use client";

import { useState } from "react";
import {
  Archive,
  CheckCircle2,
  Pause,
  Pencil,
  Play,
  Settings2,
  SlidersHorizontal,
} from "lucide-react";
import { useThemeTokens } from "@/components/theme/AppContextProvider";

export type MomentManageContext = {
  momentId: string;
  typeCode: string;
  momentName: string;
  status: string;
};

type MomentManageSheetProps = {
  open: boolean;
  context: MomentManageContext | null;
  onClose: () => void;
  onEditSetup: () => void;
  onEditName: (name: string) => Promise<void>;
  onPause: () => Promise<void>;
  onResume: () => Promise<void>;
  onArchive: () => Promise<void>;
  onComplete?: () => Promise<void>;
};

type ManageAction = {
  id: string;
  title: string;
  subtitle: string;
  icon: React.ReactNode;
  destructive?: boolean;
  onClick: () => void;
};

export function MomentManageSheet({
  open,
  context,
  onClose,
  onEditSetup,
  onEditName,
  onPause,
  onResume,
  onArchive,
  onComplete,
}: MomentManageSheetProps) {
  const tokens = useThemeTokens();
  const { colors } = tokens;
  const [showNameDialog, setShowNameDialog] = useState(false);
  const [nameDraft, setNameDraft] = useState("");
  const [showArchiveConfirm, setShowArchiveConfirm] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!open || !context) return null;

  async function run(task: () => Promise<void>) {
    setBusy(true);
    setError(null);
    try {
      await task();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong");
    } finally {
      setBusy(false);
    }
  }

  const actions: ManageAction[] = [];

  if (["ACTIVE", "PAUSED", "DRAFT"].includes(context.status)) {
    actions.push({
      id: "edit-setup",
      title: "Edit setup",
      subtitle: "Revisit priorities and configuration",
      icon: <SlidersHorizontal className="size-5" />,
      onClick: () => {
        onClose();
        onEditSetup();
      },
    });
  }

  if (context.status !== "ARCHIVED") {
    actions.push({
      id: "edit-name",
      title: "Edit moment name",
      subtitle: "Rename how this moment appears",
      icon: <Pencil className="size-5" />,
      onClick: () => {
        setNameDraft(context.momentName);
        setShowNameDialog(true);
      },
    });
  }

  if (context.status === "ACTIVE") {
    actions.push({
      id: "pause",
      title: "Pause rhythm",
      subtitle: "Pause tracking without losing your data",
      icon: <Pause className="size-5" />,
      onClick: () =>
        void run(async () => {
          await onPause();
          onClose();
        }),
    });
    if (onComplete) {
      actions.push({
        id: "complete",
        title: "Complete moment",
        subtitle: "Mark this chapter as complete",
        icon: <CheckCircle2 className="size-5" />,
        onClick: () =>
          void run(async () => {
            await onComplete();
            onClose();
          }),
      });
    }
  }

  if (context.status === "PAUSED") {
    actions.push({
      id: "resume",
      title: "Resume rhythm",
      subtitle: "Bring this moment back to active tracking",
      icon: <Play className="size-5" />,
      onClick: () =>
        void run(async () => {
          await onResume();
          onClose();
        }),
    });
  }

  if (["ACTIVE", "PAUSED", "COMPLETED", "DRAFT"].includes(context.status)) {
    actions.push({
      id: "archive",
      title: "Archive chapter",
      subtitle: "Hide this moment from your active rhythm",
      icon: <Archive className="size-5" />,
      destructive: true,
      onClick: () => setShowArchiveConfirm(true),
    });
  }

  return (
    <>
      <div className="fixed inset-0 z-50 bg-black/50" onClick={busy ? undefined : onClose} aria-hidden />
      <div
        className="fixed inset-x-0 bottom-0 z-50 mx-auto max-w-lg rounded-t-3xl border px-5 pb-8 pt-4 shadow-2xl"
        style={{ background: colors.surface, borderColor: `color-mix(in srgb, ${colors.border} 30%, transparent)` }}
        role="dialog"
        aria-labelledby="manage-moment-title"
      >
        <div className="mx-auto mb-4 h-1 w-10 rounded-full bg-white/20" />
        <div className="mb-5 flex items-start gap-3">
          <div
            className="flex size-10 shrink-0 items-center justify-center rounded-xl"
            style={{ background: colors.surfaceContainer }}
          >
            <Settings2 className="size-5" style={{ color: colors.brandPrimary }} />
          </div>
          <div>
            <h2 id="manage-moment-title" className="text-lg font-bold" style={{ color: colors.textPrimary }}>
              Manage moment
            </h2>
            <p className="text-sm" style={{ color: colors.textSecondary }}>
              {context.momentName}
            </p>
          </div>
        </div>
        <div className="space-y-2">
          {actions.map((action) => (
            <button
              key={action.id}
              type="button"
              disabled={busy}
              onClick={action.onClick}
              className="flex w-full items-center gap-3 rounded-2xl border px-4 py-3 text-left disabled:opacity-60"
              style={{
                borderColor: `color-mix(in srgb, ${colors.border} 25%, transparent)`,
                background: `color-mix(in srgb, ${colors.surfaceContainer} 50%, transparent)`,
              }}
            >
              <span style={{ color: action.destructive ? colors.error : colors.brandPrimary }}>
                {action.icon}
              </span>
              <span className="min-w-0 flex-1">
                <span
                  className="block text-sm font-semibold"
                  style={{ color: action.destructive ? colors.error : colors.textPrimary }}
                >
                  {action.title}
                </span>
                <span className="block text-xs" style={{ color: colors.textSecondary }}>
                  {action.subtitle}
                </span>
              </span>
            </button>
          ))}
        </div>
        {error ? (
          <p className="mt-3 text-sm" style={{ color: colors.error }}>
            {error}
          </p>
        ) : null}
        <button
          type="button"
          disabled={busy}
          onClick={onClose}
          className="mt-4 w-full rounded-xl py-3 text-sm font-medium"
          style={{ background: colors.surfaceContainer, color: colors.textSecondary }}
        >
          Cancel
        </button>
      </div>

      {showNameDialog ? (
        <>
          <div className="fixed inset-0 z-[60] bg-black/60" onClick={() => !busy && setShowNameDialog(false)} />
          <div
            className="fixed inset-x-4 top-1/2 z-[60] mx-auto max-w-sm -translate-y-1/2 rounded-2xl border p-5 shadow-xl"
            style={{ background: colors.surface, borderColor: colors.border }}
          >
            <h3 className="mb-3 text-base font-bold" style={{ color: colors.textPrimary }}>
              Edit moment name
            </h3>
            <input
              value={nameDraft}
              onChange={(e) => setNameDraft(e.target.value)}
              className="mb-4 w-full rounded-xl border px-3 py-2 text-sm outline-none"
              style={{
                background: colors.surfaceContainer,
                borderColor: colors.border,
                color: colors.textPrimary,
              }}
            />
            <div className="flex gap-2">
              <button
                type="button"
                disabled={busy}
                onClick={() => setShowNameDialog(false)}
                className="flex-1 rounded-xl py-2 text-sm font-medium"
                style={{ background: colors.surfaceContainer, color: colors.textSecondary }}
              >
                Cancel
              </button>
              <button
                type="button"
                disabled={busy || !nameDraft.trim()}
                onClick={() =>
                  void run(async () => {
                    await onEditName(nameDraft.trim());
                    setShowNameDialog(false);
                    onClose();
                  })
                }
                className="flex-1 rounded-xl py-2 text-sm font-semibold"
                style={{ background: colors.brandPrimary, color: colors.brandOnPrimary }}
              >
                Save
              </button>
            </div>
          </div>
        </>
      ) : null}

      {showArchiveConfirm ? (
        <>
          <div className="fixed inset-0 z-[60] bg-black/60" onClick={() => !busy && setShowArchiveConfirm(false)} />
          <div
            className="fixed inset-x-4 top-1/2 z-[60] mx-auto max-w-sm -translate-y-1/2 rounded-2xl border p-5 shadow-xl"
            style={{ background: colors.surface, borderColor: colors.border }}
          >
            <h3 className="mb-2 text-base font-bold" style={{ color: colors.textPrimary }}>
              Archive chapter?
            </h3>
            <p className="mb-4 text-sm" style={{ color: colors.textSecondary }}>
              This hides &quot;{context.momentName}&quot; from your active rhythm. Your history is kept, but you will need to set up again to reactivate this type.
            </p>
            <div className="flex gap-2">
              <button
                type="button"
                disabled={busy}
                onClick={() => setShowArchiveConfirm(false)}
                className="flex-1 rounded-xl py-2 text-sm font-medium"
                style={{ background: colors.surfaceContainer, color: colors.textSecondary }}
              >
                Cancel
              </button>
              <button
                type="button"
                disabled={busy}
                onClick={() =>
                  void run(async () => {
                    await onArchive();
                    setShowArchiveConfirm(false);
                    onClose();
                  })
                }
                className="flex-1 rounded-xl py-2 text-sm font-semibold"
                style={{ background: colors.error, color: "#fff" }}
              >
                Archive
              </button>
            </div>
          </div>
        </>
      ) : null}
    </>
  );
}
